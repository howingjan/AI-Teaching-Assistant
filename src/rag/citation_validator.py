"""
Citation validation (Phase 2).

Verifies that citations produced by the model reference documents and pages
that actually exist in the local corpus, guarding against hallucinated
document IDs and page numbers.
"""

import logging
from typing import List, Dict

from src.core.models import Chunk, Document, Citation, CitationValidation

logger = logging.getLogger(__name__)


class CitationValidator:
    """
    Validates model-generated citations against the known document corpus.

    A citation is valid when:
      - its document_id exists in the corpus
      - its page number is within the document's page range (0-indexed)
    """

    def __init__(self, chunks: List[Chunk], documents: Dict[str, Document]):
        self.chunks = chunks
        self.documents = documents
        # Cache document_id -> set of page numbers actually present in chunks
        self._pages_by_doc: Dict[str, set] = {}
        for chunk in chunks:
            self._pages_by_doc.setdefault(chunk.document_id, set()).add(chunk.page_number)

    def validate(self, citations: List[Citation]) -> CitationValidation:
        """
        Validate a list of citations.

        A citation is valid when:
          - its document_id exists in the corpus
          - if a chunk_id is provided, that chunk exists and belongs to the doc
          - its page number is within the document's page range (0-indexed)

        Args:
            citations: Citations to validate

        Returns:
            CitationValidation with missing/out-of-range/invalid-chunk info
        """
        missing_documents: List[str] = []
        out_of_range_pages: List[tuple] = []
        invalid_chunks: List[str] = []

        for citation in citations:
            doc_id = citation.document_id

            # 1. Document exists?
            if doc_id not in self.documents:
                if doc_id not in missing_documents:
                    missing_documents.append(doc_id)
                continue

            # 1.5 chunk_id (if provided) must exist in this document
            if citation.chunk_id and not self._chunk_exists(doc_id, citation.chunk_id):
                if citation.chunk_id not in invalid_chunks:
                    invalid_chunks.append(citation.chunk_id)
                continue

            # 2. Page exists in the document?
            document = self.documents[doc_id]
            known_pages = self._pages_by_doc.get(doc_id, set())
            if citation.page not in known_pages:
                # Also allow pages within total_pages even if no chunk (e.g. empty page)
                in_range = (
                    document.total_pages is not None
                    and 0 <= citation.page < document.total_pages
                )
                if not in_range:
                    out_of_range_pages.append((doc_id, citation.page))

        return CitationValidation(
            citations=citations,
            missing_documents=missing_documents,
            out_of_range_pages=out_of_range_pages,
            invalid_chunks=invalid_chunks,
        )

    def _chunk_exists(self, doc_id: str, chunk_id: str) -> bool:
        """Return True if a chunk with chunk_id exists under doc_id."""
        return any(
            c.document_id == doc_id and c.chunk_id == chunk_id for c in self.chunks
        )

    def resolve_citations(self, citations: List[Citation]) -> List[Citation]:
        """Enrich citations with chunk_id and snippet.

        Prefers the model-provided chunk_id; falls back to document_id + page
        matching when no chunk_id is given (keeps backward compatibility).
        """
        enriched = []
        for citation in citations:
            # Try to find a matching chunk by chunk_id first
            match = None
            if citation.chunk_id:
                for chunk in self.chunks:
                    if chunk.document_id == citation.document_id and chunk.chunk_id == citation.chunk_id:
                        match = chunk
                        break
            # Fall back to document_id + page matching
            if match is None:
                for chunk in self.chunks:
                    if chunk.document_id == citation.document_id and chunk.page_number == citation.page:
                        match = chunk
                        break

            if match is not None:
                citation.chunk_id = match.chunk_id
                citation.snippet = match.text[:200]
            enriched.append(citation)
        return enriched
