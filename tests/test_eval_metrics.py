"""Offline tests for the evaluation framework (metrics, golden set, demo corpus)."""

import unittest

from src.core.models import Chunk
from src.eval import run_eval
from src.eval.golden import load_golden_questions, resolve_relevant_chunk_ids
from src.eval.metrics import aggregate_metrics, compute_query_metrics


class TestRetrievalMetrics(unittest.TestCase):
    def test_perfect_prediction(self):
        metrics = compute_query_metrics(["c1", "c2", "c3"], ["c1", "c2"], k=5)
        self.assertEqual(metrics["hit_at_k"], 1.0)
        self.assertEqual(metrics["recall_at_k"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertEqual(metrics["precision_at_k"], 2 / 3)

    def test_miss(self):
        metrics = compute_query_metrics(["x1", "x2"], ["c1"], k=5)
        self.assertEqual(metrics["hit_at_k"], 0.0)
        self.assertEqual(metrics["recall_at_k"], 0.0)
        self.assertEqual(metrics["mrr"], 0.0)

    def test_mrr_uses_first_relevant_rank(self):
        metrics = compute_query_metrics(["x1", "c1", "c2"], ["c1", "c2"], k=5)
        self.assertEqual(metrics["mrr"], 0.5)

    def test_top_k_cutoff(self):
        metrics = compute_query_metrics(["x1", "x2", "c1"], ["c1"], k=2)
        self.assertEqual(metrics["hit_at_k"], 0.0)

    def test_empty_relevant_guard(self):
        metrics = compute_query_metrics(["c1"], [], k=5)
        self.assertEqual(metrics["recall_at_k"], 0.0)

    def test_aggregate_averages(self):
        summary = aggregate_metrics(
            [
                {"hit_at_k": 1.0, "recall_at_k": 1.0, "mrr": 1.0, "precision_at_k": 0.5},
                {"hit_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0, "precision_at_k": 0.0},
            ]
        )
        self.assertEqual(summary["num_queries"], 2)
        self.assertAlmostEqual(summary["hit_at_k"], 0.5)


class TestGoldenLoader(unittest.TestCase):
    def test_ships_a_valid_golden_set(self):
        items = load_golden_questions()
        self.assertGreaterEqual(len(items), 3)
        for item in items:
            self.assertTrue(item["id"])
            self.assertTrue(item["query"])

    def test_resolve_by_snippet(self):
        chunks = [
            Chunk("c1", "doc_a", 0, "Gradient descent optimizes the loss function."),
            Chunk("c2", "doc_a", 1, "This page is about linear algebra."),
        ]
        relevant = resolve_relevant_chunk_ids(
            {"relevant_snippets": ["gradient descent"], "relevant_document_ids": []},
            chunks,
        )
        self.assertEqual(relevant, {"c1"})

    def test_resolve_by_exact_chunk_id(self):
        chunks = [Chunk("c1", "doc_a", 0, "some text")]
        relevant = resolve_relevant_chunk_ids(
            {"relevant_chunk_ids": ["c1", "ghost"]},
            chunks,
        )
        self.assertEqual(relevant, {"c1"})

    def test_document_filter_applies(self):
        chunks = [
            Chunk("c1", "doc_a", 0, "Gradient descent is important."),
            Chunk("c2", "doc_b", 0, "Gradient descent appears here too."),
        ]
        relevant = resolve_relevant_chunk_ids(
            {
                "relevant_snippets": ["gradient descent"],
                "relevant_document_ids": ["doc_b"],
            },
            chunks,
        )
        self.assertEqual(relevant, {"c2"})


class TestDemoRun(unittest.TestCase):
    def test_demo_bm25_eval_offline(self):
        """The --demo BM25 run should exit 0 with no model download."""
        exit_code = run_eval.main(["--demo", "--retrievers", "bm25", "--top-k", "3"])
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
