"""
Unit tests for text chunking.
"""

import unittest
from src.core.models import Page
from src.document.text_chunker import TextChunker, get_chunking_stats


class TestTextChunker(unittest.TestCase):
    """Test text chunking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chunker = TextChunker(
            max_tokens=500,  # Small for testing
            overlap_sentences=1,
        )
    
    def test_chunk_single_page(self):
        """Test chunking a single page."""
        page = Page(
            document_id="doc_123",
            page_number=0,
            text="First sentence. Second sentence. Third sentence. Fourth sentence.",
        )
        
        chunks = self.chunker.chunk_page(page, "test")
        
        # Should have at least one chunk
        self.assertGreater(len(chunks), 0)
        
        # All chunks should have correct document_id
        for chunk in chunks:
            self.assertEqual(chunk.document_id, "doc_123")
            self.assertEqual(chunk.page_number, 0)
            self.assertTrue(len(chunk.text) > 0)
    
    def test_chunk_empty_page(self):
        """Test chunking an empty page."""
        page = Page(
            document_id="doc_123",
            page_number=0,
            text="",
        )
        
        chunks = self.chunker.chunk_page(page, "test")
        
        # Should return no chunks for empty page
        self.assertEqual(len(chunks), 0)
    
    def test_chunk_preservation_of_text(self):
        """Test that all text is preserved after chunking."""
        original_text = "Machine learning is a subset of AI. Deep learning uses neural networks. " * 10
        
        page = Page(
            document_id="doc_123",
            page_number=0,
            text=original_text,
        )
        
        chunks = self.chunker.chunk_page(page, "test")
        
        # Concatenate all chunk texts
        reconstructed = " ".join(c.text for c in chunks)
        
        # Should contain original content (may have overlaps)
        self.assertIn("Machine learning", reconstructed)
        self.assertIn("neural networks", reconstructed)
    
    def test_chunk_ordering(self):
        """Test that chunks are ordered correctly."""
        page = Page(
            document_id="doc_123",
            page_number=0,
            text="First. Second. Third. Fourth. Fifth. Sixth.",
        )
        
        chunks = self.chunker.chunk_page(page, "test")
        
        # Check order_in_doc is sequential
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk.order_in_doc, i)
    
    def test_multiple_pages(self):
        """Test chunking multiple pages."""
        pages = [
            Page(
                document_id="doc_123",
                page_number=i,
                text=f"Page {i} content. Another sentence. More text. Final sentence.",
            )
            for i in range(3)
        ]
        
        chunks = self.chunker.chunk_pages(pages, "test")
        
        # Should have chunks from all pages
        pages_in_chunks = set(c.page_number for c in chunks)
        self.assertEqual(len(pages_in_chunks), 3)
        
        # All chunks should reference doc_123
        for chunk in chunks:
            self.assertEqual(chunk.document_id, "doc_123")


class TestChunkingStats(unittest.TestCase):
    """Test chunking statistics."""
    
    def test_stats_on_empty_chunks(self):
        """Test stats with no chunks."""
        stats = get_chunking_stats([])
        
        self.assertEqual(stats['total_chunks'], 0)
        self.assertEqual(stats['total_tokens'], 0)
    
    def test_stats_calculation(self):
        """Test stat calculations."""
        from src.core.models import Chunk
        
        chunks = [
            Chunk("c1", "doc", 0, "test content", estimated_tokens=10),
            Chunk("c2", "doc", 0, "more content", estimated_tokens=20),
            Chunk("c3", "doc", 0, "final content", estimated_tokens=15),
        ]
        
        stats = get_chunking_stats(chunks)
        
        self.assertEqual(stats['total_chunks'], 3)
        self.assertEqual(stats['total_tokens'], 45)
        self.assertEqual(stats['avg_tokens'], 15)
        self.assertEqual(stats['max_tokens'], 20)
        self.assertEqual(stats['min_tokens'], 10)


if __name__ == '__main__':
    unittest.main()
