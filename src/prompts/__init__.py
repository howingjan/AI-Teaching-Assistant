"""Prompt templates module."""

from src.prompts.teaching_templates import (
    SYSTEM_PROMPT,
    LESSON_TEMPLATE,
    PROBLEM_SOLVING_TEMPLATE,
    build_lesson_messages,
    build_problem_solution_messages,
    format_context,
    get_template,
)

__all__ = [
    "SYSTEM_PROMPT",
    "LESSON_TEMPLATE",
    "PROBLEM_SOLVING_TEMPLATE",
    "build_lesson_messages",
    "build_problem_solution_messages",
    "format_context",
    "get_template",
]
