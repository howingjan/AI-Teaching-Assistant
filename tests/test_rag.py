"""
Tests for Phase 2 RAG generation pipeline (offline, no API key required).
"""

import json
import unittest

from src.core.models import Document, DocumentType, Chunk, Citation
from src.retrieval.retriever import TFIDFRetriever
from src.rag.llm_client import LLMClient, parse_json_response
from src.rag.citation_validator import CitationValidator
from src.rag.pipeline import RAGPipeline
from src.prompts.teaching_templates import build_lesson_messages, format_context


class FakeLLMClient:
    """Deterministic LLM client for offline tests."""

    def __init__(self, response: dict):
        self.response = response

    def generate(self, messages, json_mode=False, **kwargs):
        return json.dumps(self.response, ensure_ascii=False)


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
        Chunk("c1", doc.document_id, 0, "Supervised learning requires labeled examples for training."),
        Chunk("c2", doc.document_id, 1, "Classification assigns inputs to discrete categories."),
        Chunk("c3", doc.document_id, 2, "Regression predicts continuous numerical values."),
        Chunk("c4", doc.document_id, 3, "Overfitting occurs when a model memorizes training data."),
    ]
    return {doc.document_id: doc}, chunks


class TestParseJSONResponse(unittest.TestCase):
    def test_plain_json(self):
        self.assertEqual(parse_json_response('{"a": 1}'), {"a": 1})

    def test_fenced_json(self):
        raw = '```json\n{"a": 1}\n```'
        self.assertEqual(parse_json_response(raw), {"a": 1})

    def test_prose_wrapped_json(self):
        raw = 'Here is the result: {"a": 1} thanks'
        self.assertEqual(parse_json_response(raw), {"a": 1})

    def test_empty(self):
        self.assertEqual(parse_json_response(""), {})

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            parse_json_response("not json at all")


class TestLLCMock(unittest.TestCase):
    def test_mock_generate_returns_valid_json(self):
        # Empty string (not None) bypasses the config fallback and forces mock mode
        client = LLMClient(api_key="")
        self.assertFalse(client.available)
        raw = client.generate([{"role": "user", "content": "【本周主题】递归"}])
        data = json.loads(raw)
        self.assertIn("topic", data)
        self.assertEqual(data["topic"], "递归")


class TestCitationValidator(unittest.TestCase):
    def test_valid_citations(self):
        docs, chunks = make_corpus()
        validator = CitationValidator(chunks, docs)
        citations = [Citation(document_id="ml_basics_abc123", page=1)]
        result = validator.validate(citations)
        self.assertTrue(result.valid)
        self.assertEqual(result.invalid_count, 0)

    def test_missing_document(self):
        docs, chunks = make_corpus()
        validator = CitationValidator(chunks, docs)
        citations = [Citation(document_id="does_not_exist", page=0)]
        result = validator.validate(citations)
        self.assertFalse(result.valid)
        self.assertIn("does_not_exist", result.missing_documents)

    def test_out_of_range_page(self):
        docs, chunks = make_corpus()
        validator = CitationValidator(chunks, docs)
        citations = [Citation(document_id="ml_basics_abc123", page=99)]
        result = validator.validate(citations)
        self.assertFalse(result.valid)
        self.assertIn(("ml_basics_abc123", 99), result.out_of_range_pages)

    def test_resolve_citations_adds_snippet(self):
        docs, chunks = make_corpus()
        validator = CitationValidator(chunks, docs)
        citations = [Citation(document_id="ml_basics_abc123", page=1)]
        enriched = validator.resolve_citations(citations)
        self.assertIsNotNone(enriched[0].chunk_id)
        self.assertIsNotNone(enriched[0].snippet)


class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.docs, self.chunks = make_corpus()
        self.retriever = TFIDFRetriever(self.chunks, self.docs)

    def test_generate_lesson_structure(self):
        response = {
            "topic": "Supervised Learning",
            "learning_objectives": ["理解监督学习"],
            "prerequisites": ["概率基础"],
            "core_explanation": "监督学习使用带标签的数据训练模型。",
            "terminology": [{"term": "supervised learning", "explanation": "监督学习"}],
            "examples": [{"title": "例子", "content": "分类器"}],
            "misconceptions": ["误区"],
            "discussion_questions": ["问题"],
            "exercises": [{"question": "q", "hint": "h", "reference_answer": "a"}],
            "citations": [{"document_id": "ml_basics_abc123", "page": 1}],
            "needs_review": [],
        }
        pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=FakeLLMClient(response),
        )
        lesson = pipeline.generate_lesson("supervised learning")

        self.assertEqual(lesson.topic, "Supervised Learning")
        self.assertEqual(len(lesson.citations), 1)
        self.assertTrue(lesson.completeness()["complete"])
        # Citation should be resolved to a real chunk
        self.assertIsNotNone(lesson.citations[0].chunk_id)

    def test_generate_lesson_invalid_citation_flagged(self):
        response = {
            "topic": "T",
            "learning_objectives": ["x"],
            "prerequisites": ["y"],
            "core_explanation": "z",
            "terminology": [],
            "examples": [],
            "misconceptions": [],
            "discussion_questions": [],
            "exercises": [],
            "citations": [{"document_id": "fake_doc", "page": 0}],
            "needs_review": [],
        }
        pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=FakeLLMClient(response),
        )
        lesson = pipeline.generate_lesson("anything")
        # Invalid citation should surface in needs_review
        self.assertTrue(any("fake_doc" in r for r in lesson.needs_review))

    def test_export_markdown_and_json(self):
        response = {
            "topic": "Supervised Learning",
            "learning_objectives": ["a"],
            "prerequisites": ["b"],
            "core_explanation": "c",
            "terminology": [{"term": "t", "explanation": "e"}],
            "examples": [{"title": "ex", "content": "content"}],
            "misconceptions": ["m"],
            "discussion_questions": ["q"],
            "exercises": [{"question": "q", "hint": "h", "reference_answer": "a"}],
            "citations": [{"document_id": "ml_basics_abc123", "page": 0}],
            "needs_review": [],
        }
        pipeline = RAGPipeline(
            retriever=self.retriever,
            documents=self.docs,
            llm_client=FakeLLMClient(response),
        )
        lesson = pipeline.generate_lesson("supervised learning")

        md = pipeline.export_markdown(lesson)
        self.assertIn("# 本周备课包", md)
        self.assertIn("学习目标", md)

        js = pipeline.export_json(lesson)
        data = json.loads(js)
        self.assertEqual(data["topic"], "Supervised Learning")


class TestPromptHelpers(unittest.TestCase):
    def test_build_lesson_messages(self):
        docs, chunks = make_corpus()
        context = format_context(chunks, docs, max_chars=500)
        messages = build_lesson_messages("recursion", context)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("recursion", messages[1]["content"])
        self.assertIn("ml_basics_abc123", messages[1]["content"])

    def test_format_context_truncates(self):
        docs, chunks = make_corpus()
        full = format_context(chunks, docs, max_chars=10000)
        self.assertIn("ml_basics_abc123", full)
        # A small limit should truncate the context (while still including the
        # first chunk) and therefore be shorter than the untruncated version.
        truncated = format_context(chunks, docs, max_chars=100)
        self.assertLess(len(truncated), len(full))
        self.assertIn("ml_basics_abc123", truncated)


if __name__ == "__main__":
    unittest.main()
