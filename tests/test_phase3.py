"""Tests for the problem-solving (作业/真题讲题) generation. Offline."""
import json
import unittest
from pathlib import Path

from src.core.models import Document, DocumentType, Chunk
from conftest import TestRetriever
from src.rag.pipeline import RAGPipeline
from src.rag.llm_client import LLMClient


class RoutingFakeLLMClient:
    """Deterministic LLM client that returns task-appropriate JSON."""

    model = "deepseek-chat"
    available = True

    def generate(self, messages, json_mode=False, **kwargs):
        user = " ".join(
            str(m.get("content", "")) for m in messages if m.get("role") == "user"
        )
        if "【题目】" in user:
            payload = {
                "problem_summary": "ETL 与缺失值处理",
                "knowledge_points": [
                    {"name": "ETL", "explanation": "抽取-转换-加载流程"},
                    {"name": "Missing Value", "explanation": "缺失值处理"},
                ],
                "prerequisites": ["数据清洗", "描述性统计"],
                "steps": [
                    {"description": "理解题意", "hint": "找出题目关键词", "answer_progress": "列出入场数据"},
                    {"description": "识别数据类型", "hint": "四类测量尺度", "answer_progress": "分类"},
                ],
                "layered_hints": [
                    {"level": 1, "hint": "想想 ETL 的流程"},
                    {"level": 2, "hint": "缺失值会影响哪些统计量"},
                    {"level": 3, "hint": "删除还是填充取决于什么"},
                ],
                "common_errors": ["把缺失值当 0"],
                "rubric_mapping": [
                    {"criterion": "正确识别数据类型", "how_to_earn": "按四种测量尺度分类"},
                ],
                "reference_direction": "先列出 ETL 步骤，再说明缺失值处理选项，不直接代写。",
                "citations": [{"document_id": "ml_basics_abc123", "page": 1}],
                "needs_review": [],
            }
        else:
            payload = {
                "topic": "数据探索",
                "learning_objectives": ["理解集中趋势"],
                "prerequisites": ["统计基础"],
                "core_explanation": "集中趋势描述数据的典型值。",
                "terminology": [{"term": "central tendency", "explanation": "集中趋势"}],
                "examples": [{"title": "均值", "content": "所有值求和除以个数"}],
                "misconceptions": ["均值总是合适"],
                "discussion_questions": ["何时用中位数？"],
                "exercises": [{"question": "q", "hint": "h", "reference_answer": "a"}],
                "citations": [{"document_id": "ml_basics_abc123", "page": 1}],
                "needs_review": [],
            }
        return json.dumps(payload, ensure_ascii=False)


def make_corpus():
    """Build a small corpus of documents and chunks."""
    doc = Document(
        document_id="ml_basics_abc123",
        file_name="ML_Basics.pdf",
        file_path="/tmp/ML.pdf",
        document_type=DocumentType.PDF,
        total_pages=4,
    )
    chunks = [
        Chunk("c1", doc.document_id, 0, "Data types: nominal, ordinal, interval and ratio scales."),
        Chunk("c2", doc.document_id, 1, "ETL is extract, transform and load; data cleaning handles missing values."),
        Chunk("c3", doc.document_id, 2, "Regression predicts continuous numerical values."),
        Chunk("c4", doc.document_id, 3, "Overfitting occurs when a model memorizes training data."),
    ]
    return {doc.document_id: doc}, chunks


class Phase3TestBase(unittest.TestCase):
    def setUp(self):
        self.docs, self.chunks = make_corpus()
        self.retriever = TestRetriever(self.chunks, self.docs)
        self.pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=RoutingFakeLLMClient(),
        )


class TestProblemSolution(Phase3TestBase):
    def test_structure(self):
        result = self.pipeline.generate_problem_solution(
            problem_text="Explain ETL and missing values in the hotel dataset."
        )
        self.assertIn("ETL", result.problem_summary)
        self.assertEqual(len(result.knowledge_points), 2)
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(len(result.layered_hints), 3)
        levels = {h.level for h in result.layered_hints}
        self.assertGreaterEqual(len(levels), 2)
        self.assertTrue(result.completeness()["layered_hints_are_tiered"])
        self.assertTrue(result.citations)
        self.assertIsNotNone(result.citations[0].chunk_id)
        self.assertTrue(result.reference_direction)

    def test_export_markdown_and_json(self):
        result = self.pipeline.generate_problem_solution(
            problem_text="Explain ETL and missing values."
        )
        md = self.pipeline._render_markdown(result)
        self.assertIn("作业/真题讲题", md)
        self.assertIn("分层提示", md)
        path = Path("/tmp/test_sol.json")
        try:
            path.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            js = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(js["task_type"], "problem_solving")
        finally:
            path.unlink(missing_ok=True)


class TestLLCNoKey(unittest.TestCase):
    def test_generate_without_key_raises(self):
        # Mock mode was removed: without an API key generation must fail loudly.
        client = LLMClient(api_key="")
        self.assertFalse(client.available)
        with self.assertRaises(RuntimeError):
            client.generate([{"role": "user", "content": "hello"}])


if __name__ == "__main__":
    unittest.main()
