"""
Tests for Phase 4: cost/latency monitoring, failure library, standard case set,
txt/md document loading, HTML export, and evaluator usage metrics.

All tests run offline (mock LLM mode, no API key required).
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from src.core.models import Document, DocumentType, Chunk
from src.document.document_loader import DocumentLoader
from src.eval.case_sets import build_standard_cases
from src.eval.failure_library import FailureLibrary
from src.eval.monitor import UsageMonitor
from src.eval.evaluator import TaskEvaluator
from src.rag.llm_client import LLMClient
from src.rag.pipeline import RAGPipeline
from src.retrieval.retriever import TFIDFRetriever


def make_corpus():
    """Small mock corpus of documents and chunks (shared across tests)."""
    doc = Document(
        document_id="ml_basics_abc123",
        file_name="ML_Basics.pdf",
        file_path="/tmp/ML.pdf",
        document_type=DocumentType.PDF,
        total_pages=4,
    )
    chunks = [
        Chunk("c1", doc.document_id, 0, "Supervised learning requires labeled examples for training."),
        Chunk("c2", doc.document_id, 1, "Classification assigns inputs to discrete categories."),
        Chunk("c3", doc.document_id, 2, "Regression predicts continuous numerical values."),
        Chunk("c4", doc.document_id, 3, "Overfitting occurs when a model memorizes training data."),
    ]
    return {doc.document_id: doc}, chunks


class TestUsageMonitor(unittest.TestCase):
    def test_record_and_aggregate(self):
        monitor = UsageMonitor(persist_path=None)
        monitor.record(
            task="lesson", model="deepseek-chat", mode="real",
            latency_s=1.5, prompt_text="x" * 300, completion_text="y" * 150,
        )
        monitor.record(
            task="review", model="deepseek-chat", mode="mock",
            latency_s=0.5, prompt_text="a" * 300, completion_text="b" * 150,
        )
        summary = monitor.aggregate()
        self.assertEqual(summary.calls, 2)
        self.assertEqual(summary.real_calls, 1)
        self.assertEqual(summary.mock_calls, 1)
        self.assertAlmostEqual(summary.total_latency_s, 2.0, places=2)
        self.assertGreater(summary.total_tokens, 0)
        self.assertGreater(summary.total_cost_usd, 0)
        # last_record points at the most recent call
        self.assertEqual(monitor.last_record.task, "review")

    def test_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.jsonl"
            monitor = UsageMonitor(persist_path=path)
            monitor.record(task="lesson", model="m", mode="real",
                           latency_s=0.1, prompt_text="hi", completion_text="yo")
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            data = json.loads(lines[0])
            self.assertEqual(data["task"], "lesson")
            self.assertNotIn("api_key", str(data).lower())

    def test_markdown_table(self):
        monitor = UsageMonitor(persist_path=None)
        monitor.record(task="lesson", model="m", mode="mock",
                       latency_s=0.1, prompt_text="hi", completion_text="yo")
        md = monitor.to_markdown()
        self.assertIn("lesson", md)
        self.assertIn("成本", md)


class TestFailureLibrary(unittest.TestCase):
    def test_add_dedupe_and_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = FailureLibrary(json_path=Path(tmp) / "f.json", md_path=Path(tmp) / "f.md")
            lib.add("citation_error", "重复记录", description="v1", course="C", task="lesson")
            lib.add("citation_error", "重复记录", description="v2", course="C", task="lesson")
            self.assertEqual(len(lib.records), 1)
            self.assertEqual(lib.records[0].description, "v2")

            paths = lib.save()
            loaded = FailureLibrary(json_path=paths["json"], md_path=paths["markdown"])
            self.assertEqual(len(loaded.records), 1)
            self.assertEqual(loaded.records[0].title, "重复记录")
            # round-trip survives to_dict()'s derived type_label key
            self.assertIn("重复记录", loaded.to_markdown())

    def test_invalid_type_raises(self):
        lib = FailureLibrary()
        with self.assertRaises(ValueError):
            lib.add("not_a_real_type", "x")

    def test_empty_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = FailureLibrary(json_path=Path(tmp) / "f.json", md_path=Path(tmp) / "f.md")
            self.assertIn("暂无记录", lib.to_markdown())


class TestStandardCaseSet(unittest.TestCase):
    def test_build_standard_cases(self):
        cases = build_standard_cases()
        self.assertEqual(len(cases), 7)
        task_types = {c.task_type.value for c in cases}
        self.assertIn("lesson", task_types)
        self.assertIn("problem_solving", task_types)
        self.assertIn("review", task_types)
        self.assertIn("cheatsheet", task_types)
        self.assertIn("exam_mapping", task_types)
        self.assertTrue(any(c.out_of_scope for c in cases))


class TestTxtMarkdownLoading(unittest.TestCase):
    def test_load_md_and_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            md_path = Path(tmp) / "notes.md"
            md_path.write_text("# Chapter 1\nMarkdown note about data cleaning.\n", encoding="utf-8")
            txt_path = Path(tmp) / "syllabus.txt"
            txt_path.write_text("Syllabus: statistics for data science.\n", encoding="utf-8")

            loader = DocumentLoader(index_name="tmp_txt_md_test")
            doc_md, chunks_md = loader.load_document(str(md_path))
            self.assertEqual(doc_md.document_type, DocumentType.MARKDOWN)
            self.assertGreaterEqual(len(chunks_md), 1)
            self.assertEqual(loader.get_document_structure(doc_md.document_id)["sections"], ["Chapter 1"])

            doc_txt, chunks_txt = loader.load_document(str(txt_path))
            self.assertEqual(doc_txt.document_type, DocumentType.TEXT)
            self.assertGreaterEqual(len(chunks_txt), 1)


class TestPipelineMonitoringAndEval(unittest.TestCase):
    def setUp(self):
        self.docs, self.chunks = make_corpus()
        self.retriever = TFIDFRetriever(self.chunks, self.docs)
        self.monitor = UsageMonitor(persist_path=None)
        self.llm = LLMClient(api_key="")  # force mock mode
        self.pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=self.llm,
            monitor=self.monitor,
        )

    def test_pipeline_records_usage(self):
        lesson = self.pipeline.generate_lesson(topic="Classification")
        self.assertIsNotNone(self.monitor.last_record)
        self.assertEqual(self.monitor.last_record.task, "lesson")
        self.assertEqual(self.monitor.last_record.mode, "mock")
        self.assertGreater(self.monitor.last_record.total_tokens, 0)

    def test_html_export(self):
        lesson = self.pipeline.generate_lesson(topic="Supervised Learning")
        html = self.pipeline.export_html(lesson)
        self.assertIn("<html", html)
        self.assertIn("备课包", html)

    def test_evaluator_usage_metrics(self):
        cases = build_standard_cases()
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        report = evaluator.evaluate(self.pipeline, cases)
        # Every case should carry usage now
        self.assertTrue(any(c.latency_s is not None for c in report.cases))
        self.assertIn("total_cost_usd", report.overall)
        self.assertIn("avg_latency_s", report.overall)
        self.assertIn("真实", report.to_markdown())  # report renders mode label

    def test_evaluator_independent_citation(self):
        """Citation accuracy must be recomputed from raw output (not filtered)."""
        cases = build_standard_cases()
        evaluator = TaskEvaluator(documents=self.docs, chunks=self.chunks)
        report = evaluator.evaluate(self.pipeline, cases)
        for c in report.cases:
            if c.citation_count:
                self.assertIsNotNone(c.citation_accuracy)
                self.assertLessEqual(c.valid_citation_count, c.citation_count)


if __name__ == "__main__":
    unittest.main()
