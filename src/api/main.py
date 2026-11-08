"""FastAPI application for the AI Teaching Assistant.

Run with:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000

Endpoints:
    GET  /health                    liveness probe
    GET  /api/status                LLM provider / availability
    POST /api/generate/lesson       备课 / 期末复习
    POST /api/generate/problem-solving  作业 / 真题讲题
    POST /api/course/compare        新旧课件比对（multipart 上传）
"""

from __future__ import annotations

import logging
import shutil
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from src.api.schemas import LessonRequest, ProblemSolvingRequest
from src.core.config import Config
from src.core.runtime import build_knowledge_base, build_pipeline, resolve_course
from src.course_update.graph import build_course_update_graph
from src.rag.llm_client import LLMClient

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Teaching Assistant API",
    version="1.0.0",
    description="基于 RAG / LangGraph 的教学内容生成服务。",
)


def _pipeline(course: str | None):
    """Build the RAG pipeline for a course, or fail with 503 if no LLM key."""
    if not LLMClient().available:
        raise HTTPException(
            status_code=503,
            detail="未配置 LLM API key（DEEPSEEK_API_KEY / OPENAI_API_KEY / "
            "AZURE_OPENAI_API_KEY）。请先配置后再调用生成接口。",
        )
    loader, retriever = build_knowledge_base(resolve_course(course))
    return build_pipeline(loader, retriever), loader


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/status")
def status() -> dict:
    client = LLMClient()
    return {
        "llm_available": client.available,
        "provider": client.provider,
        "model": client.model,
    }


@app.post("/api/generate/lesson")
def generate_lesson(request: LessonRequest) -> dict:
    pipeline, _ = _pipeline(request.course)
    lesson = pipeline.generate_lesson(
        topic=request.topic,
        student_level=request.student_level,
        duration=request.duration,
        document_ids=request.document_ids,
        cover_all=request.cover_all,
        scope_names=request.scope_names,
        extra=request.extra,
    )
    return lesson.to_dict()


@app.post("/api/generate/problem-solving")
def generate_problem_solution(request: ProblemSolvingRequest) -> dict:
    pipeline, _ = _pipeline(request.course)
    result = pipeline.generate_problem_solution(
        problem_text=request.problem_text,
        goal=request.goal,
        top_k=request.top_k,
        document_ids=request.document_ids,
        extra=request.extra,
    )
    return result.to_dict()


@app.post("/api/course/compare")
async def course_compare(
    school_pdf: UploadFile = File(..., description="最新学校课件（PDF）"),
    tutoring_file: UploadFile = File(..., description="往期补习课件（PDF 或 DOCX）"),
    course: str = Form("default"),
) -> dict:
    """Run the LangGraph course-update analysis on two uploaded files."""
    if not LLMClient().available:
        raise HTTPException(
            status_code=503,
            detail="未配置 LLM API key，无法运行课件比对。",
        )

    task_id = uuid.uuid4().hex
    staging = Config.DATA_DIR / "course_updates" / task_id / "staging"
    staging.mkdir(parents=True, exist_ok=True)

    school_path = staging / (school_pdf.filename or "school.pdf")
    tutoring_path = staging / (tutoring_file.filename or "tutoring.docx")
    try:
        with school_path.open("wb") as out:
            shutil.copyfileobj(school_pdf.file, out)
        with tutoring_path.open("wb") as out:
            shutil.copyfileobj(tutoring_file.file, out)
    finally:
        await school_pdf.close()
        await tutoring_file.close()

    initial_state = {
        "task_id": task_id,
        "course_id": course,
        "school_pdf_path": str(school_path),
        "tutoring_file_path": str(tutoring_path),
        "school_file_name": school_pdf.filename or "school.pdf",
        "tutoring_file_name": tutoring_file.filename or "tutoring.docx",
    }

    try:
        graph = build_course_update_graph(LLMClient())
        result = graph.invoke(initial_state)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "task_id": task_id,
        "coverage_report": result.get("coverage_report", []),
        "report_json_path": result.get("report_json_path"),
        "report_markdown_path": result.get("report_markdown_path"),
        "status": result.get("status"),
    }
