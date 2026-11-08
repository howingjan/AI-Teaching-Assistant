"""
Unit tests for core data models.
"""

import unittest
from src.core.models import (
    Document, DocumentType, Page, Chunk, ParseQuality,
    SearchResult, IndexMetadata
)


class TestDocument(unittest.TestCase):
    """Test Document model."""
    
    def test_document_creation(self):
        """Test creating a valid document."""
        doc = Document(
            document_id="test_123",
            file_name="test.pdf",
            file_path="/path/to/test.pdf",
            document_type=DocumentType.PDF,
            total_pages=10,
        )
        
        self.assertEqual(doc.document_id, "test_123")
        self.assertEqual(doc.file_name, "test.pdf")
        self.assertEqual(doc.document_type, DocumentType.PDF)
        self.assertEqual(doc.total_pages, 10)
        self.assertEqual(doc.parse_quality, ParseQuality.GOOD)
    
    def test_document_requires_id_and_name(self):
        """Test that document requires ID and name."""
        with self.assertRaises(ValueError):
            Document(
                document_id="",
                file_name="test.pdf",
                file_path="/path/to/test.pdf",
                document_type=DocumentType.PDF,
            )


class TestPage(unittest.TestCase):
    """Test Page model."""
    
    def test_empty_page_quality(self):
        """Test that empty pages are marked correctly."""
        page = Page(
            document_id="doc_123",
            page_number=0,
            text="",
        )
        
        self.assertEqual(page.quality, ParseQuality.EMPTY)
    
    def test_page_with_text(self):
        """Test page with content."""
        page = Page(
            document_id="doc_123",
            page_number=0,
            text="This is some test content about machine learning.",
        )
        
        self.assertEqual(page.quality, ParseQuality.GOOD)
        self.assertFalse(page.has_tables)
        self.assertFalse(page.has_code)


class TestChunk(unittest.TestCase):
    """Test Chunk model."""
    
    def test_chunk_creation(self):
        """Test creating a valid chunk."""
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_123",
            page_number=0,
            text="Important concept: supervised learning involves labeled data.",
            char_start=0,
            char_end=57,
            estimated_tokens=10,
        )
        
        self.assertEqual(chunk.document_id, "doc_123")
        self.assertEqual(chunk.page_number, 0)
        self.assertIn("doc_id: doc_123", chunk.get_citation())
        self.assertIn("page: 0", chunk.get_citation())
    
    def test_chunk_cannot_be_empty(self):
        """Test that chunks cannot have empty text."""
        with self.assertRaises(ValueError):
            Chunk(
                chunk_id="chunk_001",
                document_id="doc_123",
                page_number=0,
                text="",
            )
    
    def test_chunk_char_end_auto_set(self):
        """Test that char_end defaults to text length."""
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_123",
            page_number=0,
            text="Test text",
        )
        
        self.assertEqual(chunk.char_end, len("Test text"))


class TestSearchResult(unittest.TestCase):
    """Test SearchResult model."""
    
    def test_search_result_score_validation(self):
        """Test that search result validates score range."""
        chunk = Chunk(
            chunk_id="chunk_001",
            document_id="doc_123",
            page_number=0,
            text="Test content",
        )
        
        # Valid score
        result = SearchResult(chunk=chunk, score=0.75, rank=1)
        self.assertEqual(result.score, 0.75)
        
        # Invalid score
        with self.assertRaises(ValueError):
            SearchResult(chunk=chunk, score=1.5, rank=1)


class TestIndexMetadata(unittest.TestCase):
    """Test IndexMetadata model."""
    
    def test_metadata_creation(self):
        """Test creating metadata."""
        meta = IndexMetadata(
            total_documents=5,
            total_chunks=100,
            document_ids=["doc_1", "doc_2", "doc_3"],
        )
        
        self.assertEqual(meta.total_documents, 5)
        self.assertEqual(meta.total_chunks, 100)
        self.assertEqual(len(meta.document_ids), 3)
        self.assertIsNotNone(meta.created_at)


if __name__ == '__main__':
    unittest.main()
