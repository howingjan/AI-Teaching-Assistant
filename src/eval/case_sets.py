"""
Standard evaluation case set (Phase 4).

Centralizes the built-in evaluation questions so the Phase 3 demo, the Phase 4
reliability demo and the UI all use the same cases. Each case maps to a scenario
from the product plan's evaluation question set (section 7.1):

  - 课件中明确出现的概念解释        -> lesson: central tendency
  - 跨页 / 跨文档检索               -> review: data exploration & ETL
  - 作业要求和评分标准定位          -> problem_solving: Assignment 1
  - 真题对应的知识点                -> exam_mapping: four measurement scales
  - 需要生成练习和讲解              -> cheatsheet: data types & ETL
  - 课件没有覆盖的资料外问题        -> lesson: quantum computing (out_of_scope)

The review cross-chapter case exercises retrieval across multiple course PDFs.
"""

from typing import List

from src.core.models import TeachingTask
from src.eval.evaluator import EvaluationCase


def build_standard_cases() -> List[EvaluationCase]:
    """Return the standard evaluation case set used across demos and the UI."""
    return [
        EvaluationCase(
            task_type=TeachingTask.LESSON,
            inputs={"topic": "什么是集中趋势（central tendency）？"},
            name="课件内概念-集中趋势",
        ),
        EvaluationCase(
            task_type=TeachingTask.PROBLEM_SOLVING,
            inputs={
                "problem_text": (
                    "Assignment 1 asks you to explore the hotel booking dataset: "
                    "identify the data types, detect missing values, and explain "
                    "how you would clean the data before analysis. Guide the "
                    "student through the reasoning."
                )
            },
            name="作业讲题-ETL与缺失值",
        ),
        EvaluationCase(
            task_type=TeachingTask.REVIEW,
            inputs={"scope": "data exploration, ETL and data cleaning"},
            name="期末复习-数据探索与ETL",
        ),
        EvaluationCase(
            task_type=TeachingTask.CHEATSHEET,
            inputs={"scope": "data exploration, data types and ETL"},
            name="速查表-数据类型与ETL",
        ),
        EvaluationCase(
            task_type=TeachingTask.EXAM_MAPPING,
            inputs={
                "exam_topic": (
                    "What are the four levels of data measurement (nominal, "
                    "ordinal, interval, ratio) and why do they matter for "
                    "choosing statistics and charts?"
                )
            },
            name="真题映射-四种测量尺度",
        ),
        # 跨页/跨文档检索：测量尺度与集中趋势分散在多个课件中。
        EvaluationCase(
            task_type=TeachingTask.REVIEW,
            inputs={"scope": "levels of measurement and measures of central tendency"},
            name="期末复习-跨章节检索",
        ),
        # 资料外问题：课件完全没有覆盖 → 应拒答而不是编造。
        EvaluationCase(
            task_type=TeachingTask.LESSON,
            inputs={"topic": "请讲解量子计算的基本原理与容错纠错机制"},
            name="资料外-量子计算",
            out_of_scope=True,
        ),
    ]


def default_problem() -> str:
    """Default problem text (kept for CLI demos)."""
    return build_standard_cases()[1].inputs["problem_text"]
