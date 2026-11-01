import unittest
from unittest.mock import patch

from src.core.models import Chunk, Document, DocumentType, SearchResult
from src.retrieval.retriever import HybridRetriever, RetrieverFactory


class TestHybridRetriever(unittest.TestCase):
    def setUp(self):
        document = Document(
            document_id="course",
            file_name="course.pdf",
            file_path="/tmp/course.pdf",
            document_type=DocumentType.PDF,
        )
        self.chunks = [
            Chunk("dense", "course", 0, "Gradient descent optimizes model parameters."),
            Chunk("keyword", "course", 1, "AdamW optimizer updates model parameters."),
            Chunk("other", "course", 2, "A completely unrelated passage."),
        ]
        self.retriever = HybridRetriever(self.chunks, {"course": document})

    def test_factory_defaults_to_hybrid(self):
        retriever = RetrieverFactory.create(
            chunks=self.chunks,
            documents=self.retriever.documents,
        )
        self.assertIsInstance(retriever, HybridRetriever)

    def test_keyword_retrieval_finds_exact_term(self):
        with patch.object(self.retriever.dense_retriever, "search", return_value=[]):
            results = self.retriever.search("AdamW optimizer")

        self.assertEqual([result.chunk.chunk_id for result in results], ["keyword"])
        self.assertIn("keyword rank: 1", results[0].reasoning)

    def test_rrf_combines_dense_and_keyword_rankings(self):
        dense_results = [
            SearchResult(self.chunks[0], 0.9, 0),
            SearchResult(self.chunks[1], 0.8, 1),
        ]
        with patch.object(
            self.retriever.dense_retriever,
            "search",
            return_value=dense_results,
        ):
            results = self.retriever.search("AdamW optimizer", top_k=2)

        self.assertEqual(results[0].chunk.chunk_id, "keyword")
        self.assertIn("dense rank: 2", results[0].reasoning)
        self.assertIn("keyword rank: 1", results[0].reasoning)
        self.assertEqual(results[1].chunk.chunk_id, "dense")

    def test_document_filter_applies_to_both_retrievers(self):
        with patch.object(self.retriever.dense_retriever, "search", return_value=[]):
            results = self.retriever.search(
                "AdamW optimizer",
                document_ids=["another-course"],
            )

        self.assertEqual(results, [])

    def test_chinese_keyword_retrieval(self):
        chunk = Chunk("cn", "course", 3, "梯度下降优化模型参数。")
        retriever = HybridRetriever(
            self.chunks + [chunk],
            self.retriever.documents,
        )
        with patch.object(retriever.dense_retriever, "search", return_value=[]):
            results = retriever.search("梯度下降")

        self.assertEqual([result.chunk.chunk_id for result in results], ["cn"])


if __name__ == "__main__":
    unittest.main()