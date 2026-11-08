"""CLI for running retrieval / generation evaluation.

Usage:
    # Quick demo on a built-in corpus (offline, no model download):
    python -m src.eval.run_eval --demo

    # Evaluate retrieval against a real course corpus:
    python -m src.eval.run_eval --course COMP5310

    # Only BM25 (no embedding model download):
    python -m src.eval.run_eval --course COMP5310 --retrievers bm25

    # Include LLM-as-judge generation scores (requires API key):
    python -m src.eval.run_eval --demo --judge
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from src.core.config import Config
from src.core.models import Chunk, Document, DocumentType
from src.core.runtime import build_knowledge_base, resolve_course
from src.eval.golden import load_golden_questions, resolve_relevant_chunk_ids
from src.eval.metrics import aggregate_metrics, compute_query_metrics
from src.retrieval.retriever import RetrieverFactory

# 演示语料（双语：英文正文 + 中文关键词），覆盖 golden_questions.json 中的关键短语，
# 离线即可复现完整流程，并直观展示「纯关键词召回 vs 跨语言语义召回」的差异。
_DEMO_CHUNKS = [
    "Gradient descent（梯度下降）iteratively updates model parameters to minimize the loss function.",
    "Overfitting（过拟合）occurs when a model memorizes training data and fails to generalize.",
    "Cross-validation（交叉验证）splits data into folds to estimate generalization performance.",
    "Supervised learning（监督学习）requires labeled examples for training.",
    "Classification（分类）assigns inputs to discrete categories, while regression（回归）predicts continuous values.",
    "The course covers probability, linear algebra and calculus prerequisites.",
]


def build_demo_corpus():
    """Build a tiny in-memory ML corpus for the --demo run."""
    document = Document(
        document_id="demo_ml",
        file_name="ML_Basics.pdf",
        file_path="/tmp/ML_Basics.pdf",
        document_type=DocumentType.PDF,
        total_pages=6,
    )
    chunks = [
        Chunk(chunk_id=f"c{index}", document_id="demo_ml", page_number=index, text=text)
        for index, text in enumerate(_DEMO_CHUNKS)
    ]
    return {document.document_id: document}, chunks


def _evaluate_retriever(
    retriever_type: str,
    chunks: List[Chunk],
    documents: dict,
    golden: List[dict],
    top_k: int,
) -> dict:
    try:
        retriever = RetrieverFactory.create(
            retriever_type,
            chunks,
            documents,
            model_name=Config.retriever.embedding_model,
        )
    except Exception as exc:  # pragma: no cover - model download / OOM etc.
        return {"retriever": retriever_type, "skipped": str(exc)}

    per_query = []
    details = []
    for item in golden:
        relevant = resolve_relevant_chunk_ids(item, chunks)
        try:
            results = retriever.search(item["query"], top_k=top_k)
        except Exception as exc:  # pragma: no cover - network / missing model
            return {"retriever": retriever_type, "skipped": str(exc)}
        predicted = [result.chunk.chunk_id for result in results]
        metrics = compute_query_metrics(predicted, sorted(relevant), k=top_k)
        per_query.append(metrics)
        details.append(
            {
                "id": item["id"],
                "query": item["query"],
                "predicted": predicted,
                "relevant": sorted(relevant),
                **metrics,
            }
        )
    return {
        "retriever": retriever_type,
        "aggregate": aggregate_metrics(per_query),
        "details": details,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate retrieval / generation quality.")
    parser.add_argument("--course", default=None, help="Course directory under data/.")
    parser.add_argument("--golden", default=None, help="Path to golden questions JSON.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--retrievers",
        nargs="+",
        choices=["bm25", "embedding", "hybrid"],
        default=None,
        help="Retrievers to evaluate (default: all that can be built).",
    )
    parser.add_argument("--demo", action="store_true", help="Use the built-in demo corpus.")
    parser.add_argument("--judge", action="store_true", help="Also run LLM-as-judge (needs key).")
    parser.add_argument("--out", default=None, help="Write JSON report to this path.")
    args = parser.parse_args(argv)

    golden = load_golden_questions(args.golden)

    if args.demo:
        documents, chunks = build_demo_corpus()
        course_label = "demo"
    else:
        course = resolve_course(args.course)
        loader, _ = build_knowledge_base(course)
        documents, chunks = loader.documents, loader.chunks
        course_label = course
        if not chunks:
            print(f"⚠️  课程 {course} 没有可评估的片段，请先上传课件到 data/{course}。")
            print("    或使用 `--demo` 在内置语料上体验评估流程。")
            return 1

    retrievers = args.retrievers or ["bm25", "embedding", "hybrid"]
    report = {
        "course": course_label,
        "top_k": args.top_k,
        "num_queries": len(golden),
        "retrievers": [],
    }

    print(f"评测课程: {course_label} | 查询数: {len(golden)} | top_k: {args.top_k}\n")
    for retriever_type in retrievers:
        result = _evaluate_retriever(retriever_type, chunks, documents, golden, args.top_k)
        if "skipped" in result:
            print(f"[{retriever_type}] 跳过：{result['skipped']}\n")
            continue
        agg = result["aggregate"]
        print(
            f"[{retriever_type}]  queries={agg['num_queries']}  "
            f"Hit@{args.top_k}={agg['hit_at_k']:.2f}  "
            f"Recall@{args.top_k}={agg['recall_at_k']:.2f}  "
            f"MRR={agg['mrr']:.3f}  Precision@{args.top_k}={agg['precision_at_k']:.2f}"
        )
        report["retrievers"].append(result)

    if args.judge:
        from src.eval.judge import LLMJudge

        try:
            judge = LLMJudge()
        except RuntimeError as exc:
            print(f"\nLLM-as-judge 跳过：{exc}")
        else:
            # 以 demo/第一段语料作为样例生成与忠实度评估的最小闭环。
            sample = chunks[0].text if chunks else ""
            judged = {
                "faithfulness": judge.evaluate_faithfulness(
                    "Gradient descent updates parameters to minimize loss.", sample
                ),
                "relevance": judge.evaluate_answer_relevance(
                    "什么是梯度下降？", "梯度下降通过迭代更新参数来最小化损失函数。"
                ),
            }
            report["judge"] = judged
            print(f"\nLLM-as-judge: {json.dumps(judged, ensure_ascii=False)}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n报告已写入: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
