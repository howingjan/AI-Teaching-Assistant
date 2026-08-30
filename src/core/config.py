"""
Configuration management for the AI tutoring system.

Centralized settings for document processing, retrieval, LLM and output.
Loads from environment variables and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class DocumentConfig:
    """Configuration for document processing."""
    max_chars_per_page: int = 5000  # Truncate very long pages
    chunk_max_tokens: int = 1000  # Approximate max tokens per chunk
    chunk_overlap_sentences: int = 2  # Overlap for context continuity
    supported_formats: list = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.pdf', '.txt', '.md']


@dataclass
class RetrieverConfig:
    """Configuration for document retrieval."""
    retriever_type: str = "embedding"  # "tfidf", "bm25", or "embedding"
    top_k: int = 5  # Number of results to return
    score_threshold: float = 0.0  # Minimum score threshold
    max_context_chars: int = 3000  # Max total chars in context
    embedding_model: str = "intfloat/multilingual-e5-small"  # Embedding model


@dataclass
class LLMConfig:
    """Configuration for LLM API calls."""
    provider: str = "deepseek"  # "deepseek", "openai", etc.
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048
    api_base_url: str = "https://api.deepseek.com"
    timeout_seconds: int = 60
    retry_count: int = 3


@dataclass
class OutputConfig:
    """Configuration for output formatting."""
    output_format: str = "markdown"  # "markdown", "html", "json"
    include_citations: bool = True
    include_confidence: bool = False
    max_output_tokens: int = 4096


class Config:
    """
    Main configuration class that loads settings from environment and provides defaults.
    """
    
    # Path configuration
    PROJECT_ROOT = PROJECT_ROOT
    DATA_DIR = PROJECT_ROOT / "data"
    INDEX_DIR = DATA_DIR / "index"
    OUTPUT_DIR = DATA_DIR / "output"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # Create directories if they don't exist
    for directory in [INDEX_DIR, OUTPUT_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Module configurations
    document = DocumentConfig()
    retriever = RetrieverConfig()
    llm = LLMConfig()
    output = OutputConfig()
    
    # API Key (from environment variable)
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that critical configuration is present.
        Return False if required config is missing, but don't raise exception
        to allow graceful degradation.
        """
        if not cls.DEEPSEEK_API_KEY:
            print("⚠️  Warning: DEEPSEEK_API_KEY not set. LLM features will not work.")
            return False
        return True
    
    @classmethod
    def get_index_path(cls, index_name: str = "default") -> Path:
        """Get path to a specific index file."""
        return cls.INDEX_DIR / f"{index_name}.json"
    
    @classmethod
    def get_embedding_cache_path(cls, index_name: str = "default") -> Path:
        """Get path to cached chunk embeddings for an index."""
        return cls.INDEX_DIR / f"{index_name}_embeddings.npy"
    
    @classmethod
    def get_output_path(cls, filename: str, subdir: str = "") -> Path:
        """Get path for output file."""
        output_path = cls.OUTPUT_DIR / subdir if subdir else cls.OUTPUT_DIR
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / filename
    
    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary (useful for logging)."""
        return {
            "project_root": str(cls.PROJECT_ROOT),
            "data_dir": str(cls.DATA_DIR),
            "index_dir": str(cls.INDEX_DIR),
            "output_dir": str(cls.OUTPUT_DIR),
            "document": vars(cls.document),
            "retriever": vars(cls.retriever),
            "llm": {
                "provider": cls.llm.provider,
                "model": cls.llm.model,
                "temperature": cls.llm.temperature,
                "max_tokens": cls.llm.max_tokens,
            },
            "output": vars(cls.output),
            "log_level": cls.LOG_LEVEL,
        }


# Module-level validate call (non-critical)
Config.validate()
