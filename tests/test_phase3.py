"""
Tests for Phase 3: problem solving, review, cheat sheet, exam mapping,
and the unified evaluation module. All offline (no API key required).
"""

import json
import unittest
from pathlib import Path

from src.core.models import (
    Document,
    DocumentType,
    Chunk,
    TeachingTask,
)
from src.retrieval.retriever import TFIDFRetriever
from src.rag.pipeline import RAGPipeline
from src.rag.llm_client import LLMClient, parse_json_response
from src.eval.evaluator import TaskEvaluator, EvaluationCase, EvaluationReport


class RoutingFakeLLMClient:
    """
    Deterministic LLM client that returns task-appropriate JSON based on which
    template marker appears in the user message.
    """

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
        elif "【复习范围】" in user:
            payload = {
                "scope": "数据探索与 ETL",
                "knowledge_map": [
                    {
                        "name": "Data Exploration",
                        "chapter": "数据探索",
                        "core_idea": "了解数据的典型值与分布",
                        "prerequisite_of": ["ETL"],
                        "depends_on": [],
                    },
                    {
                        "name": "ETL",
                        "chapter": "数据集成",
                        "core_idea": "抽取-转换-加载",
                        "prerequisite_of": [],
                        "depends_on": ["Data Exploration"],
                    },
                ],
                "core_concepts": [
                    {"chapter": "数据探索", "concepts": ["集中趋势", "离散程度", "数据类型"]}
                ],
                "confusion_points": [
                    {"a": "中位数", "b": "均值", "difference": "均值受极端值影响更大"}
                ],
                "self_test_questions": [
                    {"question": "解释 ETL 的 T 阶段", "hint": "转换", "reference_answer": "清洗与变换"}
                ],
                "exam_mapping": [
                    {"exam_topic": "测量尺度", "knowledge_points": ["数据类型"]}
                ],
                "priority_advice": ["优先复习数据类型与 ETL 流程"],
                "citations": [{"document_id": "ml_basics_abc123", "page": 0}],
                "needs_review": [],
            }
        elif "【考试范围】" in user:
            payload = {
                "title": "数据探索速查表",
                "scope": "数据探索与 ETL",
                "sections": [
                    {
                        "heading": "数据类型",
                        "items": [
                            {
                                "type": "definition",
                                "label": "Nominal",
                                "content": "只具区分性",
                                "source": {"document_id": "ml_basics_abc123", "page": 0},
                            }
                        ],
                    }
                ],
                "layout_notes": ["两栏排版，字号 9pt"],
                "compression_advice": ["删除示例只留定义"],
                "within_page_limit": True,
                "citations": [{"document_id": "ml_basics_abc123", "page": 0}],
                "needs_review": [],
            }
        elif "【真题/考点】" in user:
            payload = {
                "exam_topic": "四种测量尺度",
                "knowledge_points": [
                    {
                        "name": "Data Types",
                        "chapter": "数据探索",
                        "relevance": "真题要求区分测量尺度",
                        "evidence_chunks": [{"document_id": "ml_basics_abc123", "page": 0}],
                    }
                ],
                "coverage_gap": "",
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
    """Build a small mock corpus of documents and chunks."""
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
        self.retriever = TFIDFRetriever(self.chunks, self.docs)
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
        # Layered hints should be tiered (distinct levels)
        levels = {h.level for h in result.layered_hints}
        self.assertGreaterEqual(len(levels), 2)
        self.assertTrue(result.completeness()["layered_hints_are_tiered"])
        # Citations resolved to real chunks
        self.assertTrue(result.citations)
        self.assertIsNotNone(result.citations[0].chunk_id)
        # Tutoring mode: reference_direction present
        self.assertTrue(result.reference_direction)

    def test_export(self):
        result = self.pipeline.generate_problem_solution(
            problem_text="Explain ETL and missing values."
        )
        md = self.pipeline._render_markdown(result)
        self.assertIn("作业/真题讲题", md)
        self.assertIn("分层提示", md)
        # Save to a temp location so tests don't pollute data/output.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test_sol.json"
            path.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            js = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(js["task_type"], "problem_solving")


class TestReview(Phase3TestBase):
    def test_structure(self):
        result = self.pipeline.generate_review(scope="data exploration and ETL")
        self.assertEqual(len(result.knowledge_map), 2)
        self.assertTrue(result.completeness()["knowledge_map_has_dependencies"])
        self.assertTrue(result.confusion_points)
        self.assertTrue(result.exam_mapping)
        self.assertTrue(result.priority_advice)
        self.assertTrue(result.citations)

    def test_export_markdown(self):
        result = self.pipeline.generate_review(scope="data exploration and ETL")
        md = self.pipeline._render_markdown(result)
        self.assertIn("期末复习包", md)
        self.assertIn("课程知识点地图", md)


class TestCheatsheet(Phase3TestBase):
    def test_structure(self):
        result = self.pipeline.generate_cheatsheet(scope="data exploration")
        self.assertTrue(result.title)
        self.assertTrue(result.sections)
        self.assertTrue(result.within_page_limit)
        self.assertTrue(result.layout_notes)
        # Item source citation resolved to a real document
        item = result.sections[0].items[0]
        self.assertIsNotNone(item.source)
        self.assertEqual(item.source.document_id, "ml_basics_abc123")

    def test_export_markdown(self):
        result = self.pipeline.generate_cheatsheet(scope="data exploration")
        md = self.pipeline._render_markdown(result)
        self.assertIn("速查表", md)
        self.assertIn("排版建议", md)


class TestExamMapping(Phase3TestBase):
    def test_structure(self):
        result = self.pipeline.generate_exam_mapping(
            exam_topic="four levels of measurement"
        )
        self.assertEqual(result.task_type, TeachingTask.EXAM_MAPPING)
        self.assertEqual(len(result.knowledge_points), 1)
        self.assertTrue(result.knowledge_points[0].evidence)
        self.assertEqual(result.coverage_gap, "")

    def test_generate_task_dispatch(self):
        result = self.pipeline.generate_task(
            TeachingTask.EXAM_MAPPING, {"exam_topic": "four levels of measurement"}
        )
        self.assertEqual(result.task_type, TeachingTask.EXAM_MAPPING)


class TestEvaluator(Phase3TestBase):
    def test_report_aggregates(self):
        cases = [
            EvaluationCase(TeachingTask.PROBLEM_SOLVING, {"problem_text": "ETL question"}, name="ps"),
            EvaluationCase(TeachingTask.REVIEW, {"scope": "ETL"}, name="rev"),
            EvaluationCase(TeachingTask.CHEATSHEET, {"scope": "ETL"}, name="cs"),
            EvaluationCase(TeachingTask.EXAM_MAPPING, {"exam_topic": "measurement"}, name="em"),
        ]
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        report = evaluator.evaluate(self.pipeline, cases)
        self.assertEqual(report.total_cases, 4)
        self.assertEqual(report.overall["success_rate"], 1.0)
        self.assertGreaterEqual(report.overall["citation_accuracy"], 0.9)
        self.assertGreaterEqual(report.overall["field_complete_rate"], 0.9)
        self.assertIn("problem_solving", report.by_task)

    def test_citation_accuracy_measured_independently(self):
        # The pipeline filters bad citations; the evaluator must still detect
        # them from the raw output, so accuracy reflects model quality.
        class BadCitationClient(RoutingFakeLLMClient):
            def generate(self, messages, json_mode=False, **kwargs):
                raw = super().generate(messages, json_mode=json_mode, **kwargs)
                data = json.loads(raw)
                data["citations"] = [
                    {"document_id": "does_not_exist", "page": 0},
                    {"document_id": "ml_basics_abc123", "page": 99},
                ]
                return json.dumps(data, ensure_ascii=False)

        pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=BadCitationClient(),
        )
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        case = EvaluationCase(TeachingTask.LESSON, {"topic": "central tendency"}, name="bad-cites")
        case_result = evaluator.evaluate_case(pipeline, case)
        self.assertEqual(case_result.citation_count, 2)
        self.assertEqual(case_result.valid_citation_count, 0)
        self.assertEqual(case_result.citation_accuracy, 0.0)
        # The invalid citations must be flagged for teacher review by the pipeline
        self.assertTrue(any("不存在" in n for n in case_result.needs_review))

    def test_out_of_scope_refusal(self):
        class RefusingClient(RoutingFakeLLMClient):
            def generate(self, messages, json_mode=False, **kwargs):
                payload = {
                    "topic": "量子计算",
                    "learning_objectives": [],
                    "prerequisites": [],
                    "core_explanation": "",
                    "terminology": [],
                    "examples": [],
                    "misconceptions": [],
                    "discussion_questions": [],
                    "exercises": [],
                    "citations": [],
                    "needs_review": ["课程资料中没有关于量子计算的内容，资料不足。"],
                    "insufficient_material": True,
                }
                return json.dumps(payload, ensure_ascii=False)

        pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=RefusingClient(),
        )
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        case = EvaluationCase(
            TeachingTask.LESSON,
            {"topic": "量子计算"},
            name="out-of-scope",
            out_of_scope=True,
        )
        case_result = evaluator.evaluate_case(pipeline, case)
        self.assertTrue(case_result.refused_correctly)

    def test_report_markdown_and_json(self):
        cases = [
            EvaluationCase(TeachingTask.CHEATSHEET, {"scope": "ETL"}, name="cs"),
        ]
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        report = evaluator.evaluate(self.pipeline, cases)
        md = report.to_markdown()
        self.assertIn("评测报告", md)
        data = json.loads(report.to_json())
        self.assertEqual(data["total_cases"], 1)


class TestLLCMock(unittest.TestCase):
    def test_mock_problem_response_routes(self):
        client = LLMClient(api_key="")
        self.assertFalse(client.available)
        # Mock only fully supports lesson schema; it must still be parseable JSON.
        raw = client.generate([{"role": "user", "content": "【本周主题】递归"}])
        self.assertEqual(json.loads(raw)["topic"], "递归")


if __name__ == "__main__":
    unittest.main()
