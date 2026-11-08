"""Golden question-set loading and relevance resolution.

A golden question is a JSON object:

    {
      "id": "q001",
      "query": "什么是梯度下降？",
      "relevant_document_ids": ["ml_basics_abc123"],   // optional; empty = any doc
      "relevant_snippets": ["gradient descent", "梯度下降"],  // optional
      "relevant_chunk_ids": ["c1", "c2"]               // optional, exact
    }

Relevance is resolved in two ways:
  1. `relevant_chunk_ids` — exact chunk-ID matches (most precise).
  2. `relevant_snippets` — a chunk is relevant when its text contains any
     snippet (case-insensitive). `relevant_document_ids` optionally narrows
     the search to specific documents; when empty, all documents are allowed.
     This keeps the golden set portable across corpora whose chunk IDs are
     derived from file hashes.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Sequence

from src.core.models import Chunk

logger = logging.getLogger(__name__)

DEFAULT_GOLDEN_PATH = Path(__file__).with_name("golden_questions.json")

_REQUIRED_KEYS = ("id", "query")


def load_golden_questions(path: Optional[str] = None) -> List[dict]:
    """Load and validate the golden question set from a JSON file."""
    path = Path(path) if path else DEFAULT_GOLDEN_PATH
    if not path.exists():
        raise FileNotFoundError(f"Golden question file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("questions", [])
    if not isinstance(items, list):
        raise ValueError(f"Golden file must be a JSON list: {path}")

    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"Golden item must be an object: {item!r}")
        missing = [key for key in _REQUIRED_KEYS if not item.get(key)]
        if missing:
            raise ValueError(f"Golden item missing required keys {missing}: {item!r}")
        has_exact = bool(item.get("relevant_chunk_ids"))
        has_snippet = bool(item.get("relevant_snippets"))
        if not (has_exact or has_snippet):
            raise ValueError(
                f"Golden item {item.get('id')!r} needs either relevant_chunk_ids "
                "or relevant_snippets."
            )
    return items


def resolve_relevant_chunk_ids(item: dict, chunks: Sequence[Chunk]) -> set:
    """Return the set of corpus chunk IDs relevant to one golden item."""
    exact = item.get("relevant_chunk_ids") or []
    if exact:
        known = {chunk.chunk_id for chunk in chunks}
        return {chunk_id for chunk_id in exact if chunk_id in known}

    # An empty/missing relevant_document_ids means "any document".
    allowed_documents = set(item.get("relevant_document_ids") or [])
    snippets = [str(s).lower() for s in (item.get("relevant_snippets") or [])]
    relevant = set()
    for chunk in chunks:
        if allowed_documents and chunk.document_id not in allowed_documents:
            continue
        text = chunk.text.lower()
        if any(snippet in text for snippet in snippets):
            relevant.add(chunk.chunk_id)
    return relevant
