"""Pydantic request/response schemas for the API service."""

from typing import List, Optional

from pydantic import BaseModel, Field


class LessonRequest(BaseModel):
    """备课 / 期末复习任务请求体。"""

    course: Optional[str] = None
    topic: str = ""
    student_level: str = "初学者"
    duration: str = "1 小时"
    document_ids: Optional[List[str]] = None
    cover_all: bool = True
    scope_names: Optional[List[str]] = None
    extra: str = ""


class ProblemSolvingRequest(BaseModel):
    """作业 / 真题讲题任务请求体。"""

    course: Optional[str] = None
    problem_text: str = Field(..., min_length=1, description="题目文本")
    goal: str = "讲解解题思路，不代写答案"
    document_ids: Optional[List[str]] = None
    top_k: int = Field(5, ge=1, le=20)
    extra: str = ""


class StatusResponse(BaseModel):
    llm_available: bool
    provider: str
    model: str


class ErrorResponse(BaseModel):
    detail: str
