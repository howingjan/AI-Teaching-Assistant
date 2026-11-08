"""Typed state and report models for course-material update tasks."""

from typing import Literal, TypedDict


CoverageStatus = Literal[
    "covered",
    "partial",
    "missing",
    "conflict",
    "uncertain",
]


class SourceEvidence(TypedDict):
    chunk_id: str
    file_name: str
    page: int | None
    section: str | None
    excerpt: str


class CoverageItem(TypedDict):
    topic_id: str
    topic: str
    description: str
    coverage: CoverageStatus
    school_sources: list[SourceEvidence]
    tutoring_sources: list[SourceEvidence]
    gap: str
    recommendation: str
    confidence: float


class CourseUpdateState(TypedDict, total=False):
    task_id: str
    course_id: str
    school_pdf_path: str
    school_file_name: str
    tutoring_file_path: str
    tutoring_file_name: str
    school_sha256: str
    tutoring_sha256: str
    school_chunks: list
    tutoring_chunks: list
    topics: list[dict]
    evidence_by_topic: dict[str, list[SourceEvidence]]
    coverage_report: list[CoverageItem]
    report_json_path: str
    report_markdown_path: str
    error: str
    status: str
