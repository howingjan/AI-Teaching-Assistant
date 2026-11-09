"""Shared runtime helpers: knowledge-base loading and pipeline construction.

Extracted from app.py so the Streamlit workbench builds the corpus + RAG
pipeline in one place.
"""

from typing import Optional, Tuple

from src.core.config import Config
from src.document.document_loader import DocumentLoader
from src.core.monitor import UsageMonitor
from src.rag.llm_client import LLMClient
from src.rag.pipeline import RAGPipeline
from src.retrieval.retriever import RetrieverFactory


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
