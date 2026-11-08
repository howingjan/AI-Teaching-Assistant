"""Retrieval quality metrics.

All functions are pure and offline-friendly: they operate on lists of chunk
identifiers, so they can be used with any retriever exposing `.search()`.
"""

from typing import Dict, List, Sequence


def compute_query_metrics(
    predicted_chunk_ids: Sequence[str],
    relevant_chunk_ids: Sequence[str],
    k: int = 5,
) -> Dict[str, float]:
    """Compute Hit@k, Recall@k, MRR and Precision@k for a single query.

    Args:
        predicted_chunk_ids: Chunk IDs returned by the retriever (in rank order).
        relevant_chunk_ids: Ground-truth relevant chunk IDs for this query.
        k: Rank cutoff (top-k).

    Returns:
        Dict with keys hit_at_k, recall_at_k, mrr, precision_at_k.
    """
    predicted = list(predicted_chunk_ids)[:k]
    relevant = set(relevant_chunk_ids)

    hit_rank = None
    for rank, chunk_id in enumerate(predicted, start=1):
        if chunk_id in relevant:
            hit_rank = rank
            break

    retrieved_relevant = sum(1 for chunk_id in predicted if chunk_id in relevant)
    precision = retrieved_relevant / len(predicted) if predicted else 0.0
    recall = retrieved_relevant / len(relevant) if relevant else 0.0

    return {
        "hit_at_k": 1.0 if hit_rank is not None else 0.0,
        "recall_at_k": min(recall, 1.0),
        "mrr": 1.0 / hit_rank if hit_rank is not None else 0.0,
        "precision_at_k": precision,
    }


def aggregate_metrics(per_query: List[Dict[str, float]]) -> Dict[str, float]:
    """Average per-query metrics into a single summary dict."""
    if not per_query:
        return {
            "num_queries": 0,
            "hit_at_k": 0.0,
            "recall_at_k": 0.0,
            "mrr": 0.0,
            "precision_at_k": 0.0,
        }
    keys = ("hit_at_k", "recall_at_k", "mrr", "precision_at_k")
    summary = {"num_queries": len(per_query)}
    for key in keys:
        summary[key] = sum(row[key] for row in per_query) / len(per_query)
    return summary
