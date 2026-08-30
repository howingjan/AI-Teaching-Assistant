"""Prompt templates module (Phase 2 + Phase 3)."""

from src.prompts.teaching_templates import (
    SYSTEM_PROMPT,
    LESSON_TEMPLATE,
    PROBLEM_SOLVING_TEMPLATE,
    REVIEW_TEMPLATE,
    CHEATSHEET_TEMPLATE,
    EXAM_MAPPING_TEMPLATE,
    build_lesson_messages,
    build_problem_solution_messages,
    build_review_messages,
    build_cheatsheet_messages,
    build_exam_mapping_messages,
    format_context,
    get_template,
)

__all__ = [
    "SYSTEM_PROMPT",
    "LESSON_TEMPLATE",
    "PROBLEM_SOLVING_TEMPLATE",
    "REVIEW_TEMPLATE",
    "CHEATSHEET_TEMPLATE",
    "EXAM_MAPPING_TEMPLATE",
    "build_lesson_messages",
    "build_problem_solution_messages",
    "build_review_messages",
    "build_cheatsheet_messages",
    "build_exam_mapping_messages",
    "format_context",
    "get_template",
]
