import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document as WordDocument

from src.core.models import Chunk, SearchResult
from src.course_update.graph import _parse_docx, build_course_update_graph
from src.document.text_chunker import TextChunker


class FakeLLMClient:
    def __init__(self):
        self.revision_calls = 0

    def generate(self, messages, **kwargs):
        system = messages[0]["content"]
        if "课程知识点抽取器" in system:
            return json.dumps({
                "topics": [{
                    "topic": "梯度下降",
                    "description": "理解梯度下降的更新过程",
                    "school_chunk_ids": ["school_c1"],
                }],
            }, ensure_ascii=False)
        if "覆盖度审核助手" in system:
            return json.dumps({
                "assessments": [{
                    "topic_id": "T001",
                    "coverage": "partial",
                    "tutoring_evidence_chunk_ids": ["tutor_c1"],
                    "gap": "还需要补充演示例题。",
                    "recommendation": "补充一个参数更新的数值示例。",
                    "confidence": 0.9,
                }],
            }, ensure_ascii=False)
        if "教学资料编辑助手" in system:
            self.revision_calls += 1
            return json.dumps({
                "sections": [{
                    "topic_id": "T001",
                    "heading": "梯度下降补充",
                    "content": "每次迭代沿损失函数负梯度方向更新参数。",
                }],
            }, ensure_ascii=False)
        raise AssertionError("Unexpected LLM prompt")


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def search(self, query, top_k=5):
        return [SearchResult(self.chunks[0], 0.8, 0)]


class TestCourseUpdateGraph(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.task_id = "a" * 32
        self.staging_dir = self.data_dir / "course_updates" / self.task_id / "staging"
        self.staging_dir.mkdir(parents=True)
        self.school_path = self.staging_dir / "school.pdf"
        self.school_path.write_bytes(b"%PDF-test-fixture")
        self.tutoring_path = self.staging_dir / "tutoring.docx"
        source_doc = WordDocument()
        caption_style = source_doc.styles["Caption"]
        source_doc.styles.element.remove(caption_style.element)
        source_doc.add_heading("旧讲义", level=1)
        source_doc.add_paragraph("旧课件正文")
        source_doc.save(self.tutoring_path)

        self.school_chunk = Chunk(
            "school_c1",
            "school_doc",
            0,
            "梯度下降通过梯度更新模型参数。",
        )
        self.tutoring_chunk = Chunk(
            "tutor_c1",
            "tutoring_doc",
            0,
            "梯度下降沿损失函数负梯度方向更新参数。",
            section="优化算法",
        )
        self.fake_llm = FakeLLMClient()

    def test_docx_parser_keeps_heading_and_table_sections(self):
        source = WordDocument()
        source.add_heading("优化算法", level=1)
        source.add_paragraph("梯度下降通过梯度更新模型参数。")
        table = source.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "算法"
        table.cell(0, 1).text = "用途"
        source.save(self.tutoring_path)

        chunks = _parse_docx(
            self.tutoring_path,
            "previous.docx",
            TextChunker(max_tokens=400, overlap_sentences=0),
        )

        self.assertTrue(any(chunk.section == "优化算法" for chunk in chunks))
        self.assertTrue(any(chunk.section == "表格 1" for chunk in chunks))
        self.assertTrue(any("算法 | 用途" in chunk.text for chunk in chunks))

    def test_graph_reports_evidence_and_preserves_original_on_revision(self):
        initial_hash = hashlib.sha256(self.tutoring_path.read_bytes()).hexdigest()
        retriever = FakeRetriever([self.tutoring_chunk])

        def fake_factory(*args, **kwargs):
            return retriever

        with (
            patch("src.course_update.graph.Config.DATA_DIR", self.data_dir),
            patch("src.course_update.graph._parse_pdf", return_value=[self.school_chunk]),
            patch("src.course_update.graph._parse_docx", return_value=[self.tutoring_chunk]),
        ):
            graph = build_course_update_graph(self.fake_llm, fake_factory)
            state = graph.invoke({
                "task_id": self.task_id,
                "course_id": "demo",
                "school_pdf_path": str(self.school_path),
                "school_file_name": "latest.pdf",
                "tutoring_file_path": str(self.tutoring_path),
                "tutoring_file_name": "previous.docx",
                "selected_recommendation_ids": [],
            })
            self.assertEqual(state["status"], "awaiting_teacher_review")
            self.assertEqual(state["coverage_report"][0]["coverage"], "partial")
            self.assertEqual(
                state["coverage_report"][0]["tutoring_sources"][0]["chunk_id"],
                "tutor_c1",
            )
            self.assertTrue(Path(state["report_json_path"]).is_file())

            revised = graph.invoke({
                **state,
                "action": "revise",
                "selected_recommendation_ids": ["T001"],
            })

        self.assertTrue(Path(revised["revision_docx_path"]).is_file())
        self.assertEqual(
            hashlib.sha256(self.tutoring_path.read_bytes()).hexdigest(),
            initial_hash,
        )
        output_doc = WordDocument(revised["revision_docx_path"])
        self.assertTrue(any(
            "梯度下降补充" in paragraph.text
            for paragraph in output_doc.paragraphs
        ))
        self.assertTrue(any(
            paragraph.text.startswith("审核依据：梯度下降")
            for paragraph in output_doc.paragraphs
        ))

    def test_unsupported_evidence_cannot_be_marked_covered(self):
        class HallucinatingLLM(FakeLLMClient):
            def generate(self, messages, **kwargs):
                if "覆盖度审核助手" in messages[0]["content"]:
                    return json.dumps({
                        "assessments": [{
                            "topic_id": "T001",
                            "coverage": "partial",
                            "tutoring_evidence_chunk_ids": ["not-a-real-chunk"],
                            "gap": "",
                            "recommendation": "",
                            "confidence": 1,
                        }],
                    })
                return super().generate(messages, **kwargs)

        def fake_factory(*args, **kwargs):
            return FakeRetriever([self.tutoring_chunk])
        with (
            patch("src.course_update.graph.Config.DATA_DIR", self.data_dir),
            patch("src.course_update.graph._parse_pdf", return_value=[self.school_chunk]),
            patch("src.course_update.graph._parse_docx", return_value=[self.tutoring_chunk]),
        ):
            state = build_course_update_graph(
                HallucinatingLLM(),
                fake_factory,
            ).invoke({
                "task_id": self.task_id,
                "course_id": "demo",
                "school_pdf_path": str(self.school_path),
                "school_file_name": "latest.pdf",
                "tutoring_file_path": str(self.tutoring_path),
                "tutoring_file_name": "previous.docx",
                "selected_recommendation_ids": [],
            })

        self.assertEqual(state["coverage_report"][0]["coverage"], "uncertain")
        self.assertEqual(state["coverage_report"][0]["tutoring_sources"], [])

    def test_upload_validation_rejects_outside_task_staging_directory(self):
        outside = Path(self.temp_dir.name) / "outside.pdf"
        outside.write_bytes(b"%PDF-test-fixture")
        with patch("src.course_update.graph.Config.DATA_DIR", self.data_dir):
            with self.assertRaisesRegex(ValueError, "暂存目录"):
                build_course_update_graph(self.fake_llm).invoke({
                    "task_id": self.task_id,
                    "school_pdf_path": str(outside),
                    "school_file_name": "latest.pdf",
                    "tutoring_file_path": str(self.tutoring_path),
                    "tutoring_file_name": "previous.docx",
                })


if __name__ == "__main__":
    unittest.main()
