"""Tests for the standalone BM25 retriever added for evaluation baselines."""

import unittest

from src.core.models import Chunk, Document, DocumentType
from src.retrieval.retriever import BM25Retriever, RetrieverFactory


def make_corpus():
    document = Document(
        document_id="course",
        file_name="course.pdf",
        file_path="/tmp/course.pdf",
        document_type=DocumentType.PDF,
    )
    chunks = [
        Chunk("a", "course", 0, "Gradient descent optimizes model parameters."),
        Chunk("b", "course", 1, "AdamW optimizer updates model parameters."),
        Chunk("c", "course", 2, "A completely unrelated passage."),
    ]
    return {document.document_id: document}, chunks


class TestBM25Retriever(unittest.TestCase):
    def test_retrieves_keyword_match(self):
        documents, chunks = make_corpus()
        retriever = BM25Retriever(chunks, documents)
        results = retriever.search("AdamW optimizer", top_k=5)
        self.assertEqual(results[0].chunk.chunk_id, "b")
        self.assertIn("BM25", results[0].reasoning)

    def test_scores_are_normalized_to_unit_interval(self):
        documents, chunks = make_corpus()
        retriever = BM25Retriever(chunks, documents)
        for result in retriever.search("optimizer", top_k=5):
            self.assertTrue(0.0 <= result.score <= 1.0)

    def test_document_filter(self):
        documents, chunks = make_corpus()
        retriever = BM25Retriever(chunks, documents)
        self.assertEqual(
            retriever.search("optimizer", document_ids=["other-course"]),
            [],
        )

    def test_factory_registers_bm25(self):
        documents, chunks = make_corpus()
        retriever = RetrieverFactory.create("bm25", chunks, documents)
        self.assertIsInstance(retriever, BM25Retriever)


if __name__ == "__main__":
    unittest.main()
