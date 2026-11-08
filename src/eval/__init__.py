"""Evaluation module — retrieval & generation quality assessment.

Provides:
  - retrieval metrics (Hit@k / Recall@k / MRR / Precision@k) in `metrics`
  - golden question-set loading in `golden`
  - optional LLM-as-judge scoring in `judge`
  - a CLI runner `python -m src.eval.run_eval` in `run_eval`
"""
