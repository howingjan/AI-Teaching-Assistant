"""Shared runtime helpers: knowledge-base loading and pipeline construction.

Extracted from app.py so the Streamlit workbench, the FastAPI service and the
evaluation CLI all build the corpus + RAG pipeline the same way.
"""

from typing import Optional, Tuple

from src.core.config import Config
from src.document.document_loader import DocumentLoader
from src.eval.monitor import UsageMonitor
from src.rag.llm_client import LLMClient
from src.rag.pipeline import RAGPipeline
from src.retrieval.retriever import RetrieverFactory

# 系统目录，不作为可选课程
_SYSTEM_DIRS = {Config.INDEX_DIR.name, Config.OUTPUT_DIR.name}


def list_courses() -> list[str]:
    """List course directories under data/ (excluding system directories)."""
    if not Config.DATA_DIR.exists():
        return []
    return [
        d.name
        for d in Config.DATA_DIR.iterdir()
        if d.is_dir() and d.name not in _SYSTEM_DIRS
    ]


def resolve_course(course: Optional[str] = None) -> str:
    """Resolve a course name, falling back to the first available course."""
    if course and course.strip():
        return course.strip()
    courses = list_courses()
    return courses[0] if courses else "COMP5310"


def build_knowledge_base(course: str) -> Tuple[DocumentLoader, object]:
    """Load (or build) the course index and create the configured retriever."""
    loader = DocumentLoader(index_name=course)
    course_path = Config.DATA_DIR / course
    if not loader.chunks:
        if course_path.exists():
            loader.load_documents_from_directory(str(course_path))
            loader.save_index()
    else:
        # 索引已存在：把磁盘上新增的课件（含 uploads/）合并进索引。
        sync = getattr(loader, "sync_directory", None)
        if callable(sync) and course_path.exists():
            added_docs, _ = sync(str(course_path))
            if added_docs:
                loader.save_index()

    retriever = RetrieverFactory.create(
        Config.retriever.retriever_type,
        loader.chunks,
        loader.documents,
        model_name=Config.retriever.embedding_model,
        cache_path=str(Config.get_embedding_cache_path(course)),
    )
    return loader, retriever


def build_pipeline(
    loader: DocumentLoader,
    retriever,
    monitor: Optional[UsageMonitor] = None,
) -> RAGPipeline:
    """Construct the RAG pipeline bound to a loaded corpus + retriever."""
    return RAGPipeline(
        retriever=retriever,
        documents=loader.documents,
        llm_client=LLMClient(),
        monitor=monitor,
    )
