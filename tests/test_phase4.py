"""Tests for usage/cost monitoring, pipeline monitoring, and HTML export. Offline."""
import json
import tempfile
import unittest
from pathlib import Path

from src.core.models import Document, DocumentType, Chunk
from src.eval.monitor import UsageMonitor
from src.rag.pipeline import RAGPipeline
from conftest import TestRetriever


def make_corpus():
    """Small corpus of documents and chunks (shared across tests)."""
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


class FakeLLMClient:
    """Deterministic real-mode stand-in (offline)."""

    model = "deepseek-chat"
    available = True

    def generate(self, messages, json_mode=False, **kwargs):
        return json.dumps({
            "topic": "Supervised Learning",
            "learning_objectives": ["目标"],
            "prerequisites": ["前置"],
            "core_explanation": "讲解",
            "terminology": [],
            "examples": [],
            "misconceptions": [],
            "discussion_questions": [],
            "exercises": [],
            "citations": [{"document_id": "ml_basics_abc123", "page": 0}],
            "needs_review": [],
            "insufficient_material": False,
        }, ensure_ascii=False)


class TestUsageMonitor(unittest.TestCase):
    def test_record(self):
        monitor = UsageMonitor(persist_path=None)
        monitor.record(
            task="lesson", model="deepseek-chat", latency_s=1.5,
            prompt_text="x" * 300, completion_text="y" * 150,
        )
        rec = monitor.last_record
        self.assertIsNotNone(rec)
        self.assertEqual(rec.mode, "real")
        self.assertEqual(rec.task, "lesson")
        self.assertGreater(rec.total_tokens, 0)
        self.assertGreater(rec.cost_usd, 0)
        self.assertEqual(len(monitor.records), 1)

    def test_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.jsonl"
            monitor = UsageMonitor(persist_path=path)
            monitor.record(task="lesson", model="m", latency_s=0.1,
                           prompt_text="hi", completion_text="yo")
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            data = json.loads(lines[0])
            self.assertEqual(data["task"], "lesson")
            self.assertNotIn("api_key", str(data).lower())


class TestPipelineMonitoring(unittest.TestCase):
    def setUp(self):
        self.docs, self.chunks = make_corpus()
        self.retriever = TestRetriever(self.chunks, self.docs)
        self.monitor = UsageMonitor(persist_path=None)
        self.pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=FakeLLMClient(),
            monitor=self.monitor,
        )

    def test_pipeline_records_usage(self):
        self.pipeline.generate_lesson(topic="Classification")
        rec = self.monitor.last_record
        self.assertIsNotNone(rec)
        self.assertEqual(rec.task, "lesson")
        self.assertEqual(rec.mode, "real")
        self.assertGreater(rec.total_tokens, 0)

    def test_html_export(self):
        lesson = self.pipeline.generate_lesson(topic="Supervised Learning")
        html = self.pipeline.export_html(lesson)
        self.assertIn("<html", html)
        self.assertIn("备课包", html)


if __name__ == "__main__":
    unittest.main()
