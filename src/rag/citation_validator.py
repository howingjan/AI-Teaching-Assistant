"""
Citation validation (Phase 2).

Verifies that citations produced by the model reference documents and pages
that actually exist in the local corpus, guarding against hallucinated
document IDs and page numbers.
"""

import logging
from typing import List, Dict, Optional

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

        Args:
            citations: Citations to validate

        Returns:
            CitationValidation with missing/out-of-range info
        """
        missing_documents: List[str] = []
        out_of_range_pages: List[tuple] = []

        for citation in citations:
            doc_id = citation.document_id

            # 1. Document exists?
            if doc_id not in self.documents:
                if doc_id not in missing_documents:
                    missing_documents.append(doc_id)
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
        )

    def resolve_citations(self, citations: List[Citation]) -> List[Citation]:
        """
        Enrich citations with chunk_id and snippet by matching document_id + page.

        Useful for attaching exact source chunks to citations for display/export.
        """
        enriched = []
        for citation in citations:
            # Try to find a matching chunk
            match = None
            for chunk in self.chunks:
                if chunk.document_id == citation.document_id and chunk.page_number == citation.page:
                    match = chunk
                    break

            if match is not None:
                citation.chunk_id = match.chunk_id
                citation.snippet = match.text[:200]
            enriched.append(citation)
        return enriched
