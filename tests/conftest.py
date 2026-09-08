"""
Conftest for pytest configuration and shared fixtures.
"""

import re
import sys
from pathlib import Path

from src.core.models import SearchResult

# Add project root to path (for `import src.*`)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# Add tests dir to path (for `from conftest import TestRetriever`)
sys.path.insert(0, str(Path(__file__).parent))


class TestRetriever:
    """Lightweight keyword-matching retriever for offline tests.

    Replaces the removed TF-IDF retriever: exposes the same `.search()` /
    `.chunks` surface the pipeline relies on, with zero external dependencies.
    """

    __test__ = False  # tell pytest this is not a test class

    def __init__(self, chunks, documents):
        self.chunks = list(chunks)
        self.documents = documents

    def search(self, query, top_k=5, score_threshold=0.0, document_ids=None, **kwargs):
        """Keyword-overlap search (documents test behaviour, not semantics)."""
        q = (query or "").lower()
        terms = [t for t in re.findall(r"\w+", q) if len(t) > 1]
        scored = []
        for i, chunk in enumerate(self.chunks):
            if document_ids and chunk.document_id not in document_ids:
                continue
            text = chunk.text.lower()
            hits = sum(1 for t in terms if t in text)
            if hits:
                scored.append((i, hits))
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for i, hits in scored[:top_k]:
            chunk = self.chunks[i]
            results.append(SearchResult(
                chunk=chunk,
                score=min(1.0, hits / max(len(terms), 1)),
                rank=len(results),
                reasoning=f"keyword hits: {hits}",
            ))
        return results
