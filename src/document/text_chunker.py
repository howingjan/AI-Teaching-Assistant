"""
Text chunking with source metadata preservation.

Splits text into semantically meaningful chunks while maintaining
document ID, page numbers, and character positions for accurate citations.
"""

import re
import logging
from typing import List, Optional

from src.core.models import Chunk, Page

logger = logging.getLogger(__name__)


class TextChunker:
    """
    Chunks text while preserving source information.
    """
    
    def __init__(
        self,
        max_tokens: int = 1000,
        overlap_sentences: int = 2,
        char_per_token: float = 1.5  # Rough estimate for Chinese
    ):
        """
        Initialize chunker.
        
        Args:
            max_tokens: Approximate maximum tokens per chunk
            overlap_sentences: Number of sentences to overlap between chunks
            char_per_token: Estimated characters per token (for Chinese ~1.5)
        """
        self.max_tokens = max_tokens
        self.overlap_sentences = overlap_sentences
        self.char_per_token = char_per_token
        self.max_chars = int(max_tokens * char_per_token)
    
    def chunk_page(self, page: Page, chunk_id_prefix: str = "") -> List[Chunk]:
        """
        Chunk a single page into semantic pieces.
        
        Args:
            page: Page object containing text and metadata
            chunk_id_prefix: Prefix for chunk IDs
            
        Returns:
            List of Chunk objects with source information
        """
        if not page.text or not page.text.strip():
            return []
        
        # Split by sentences (Chinese and English)
        sentences = self._split_sentences(page.text)
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk_sentences = []
        current_length = 0
        chunk_counter = 0
        char_position = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed limit
            if current_length + sentence_length > self.max_chars and current_chunk_sentences:
                # Save current chunk
                chunk_text = " ".join(current_chunk_sentences)
                chunk_char_start = char_position - sum(len(s) for s in current_chunk_sentences)
                
                chunk = Chunk(
                    chunk_id=f"{chunk_id_prefix}_{page.page_number}_{chunk_counter}",
                    document_id=page.document_id,
                    page_number=page.page_number,
                    text=chunk_text,
                    char_start=max(0, chunk_char_start),
                    char_end=char_position,
                    section=page.sections[0] if page.sections else None,
                    estimated_tokens=int(len(chunk_text) / self.char_per_token),
                    order_in_doc=len(chunks),
                )
                chunks.append(chunk)
                chunk_counter += 1
                
                # Keep overlap for context
                if self.overlap_sentences > 0 and current_chunk_sentences:
                    overlap = current_chunk_sentences[-self.overlap_sentences:]
                    current_chunk_sentences = overlap
                    current_length = sum(len(s) for s in overlap)
                else:
                    current_chunk_sentences = []
                    current_length = 0
            
            current_chunk_sentences.append(sentence)
            current_length += sentence_length
            char_position += sentence_length
        
        # Handle remaining chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk_char_start = char_position - sum(len(s) for s in current_chunk_sentences)
            
            chunk = Chunk(
                chunk_id=f"{chunk_id_prefix}_{page.page_number}_{chunk_counter}",
                document_id=page.document_id,
                page_number=page.page_number,
                text=chunk_text,
                char_start=max(0, chunk_char_start),
                char_end=char_position,
                section=page.sections[0] if page.sections else None,
                estimated_tokens=int(len(chunk_text) / self.char_per_token),
                order_in_doc=len(chunks),
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_pages(
        self,
        pages: List[Page],
        chunk_id_prefix: str = ""
    ) -> List[Chunk]:
        """
        Chunk multiple pages.
        
        Args:
            pages: List of Page objects
            chunk_id_prefix: Prefix for chunk IDs
            
        Returns:
            Flattened list of all chunks from all pages
        """
        all_chunks = []
        global_order = 0
        
        for page in pages:
            page_chunks = self.chunk_page(page, chunk_id_prefix)
            for i, chunk in enumerate(page_chunks):
                chunk.order_in_doc = global_order + i
            all_chunks.extend(page_chunks)
            global_order += len(page_chunks)
        
        return all_chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving structure.
        
        Handles both Chinese and English punctuation.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Normalize text
        text = text.strip()
        
        # Chinese and English sentence endings
        # This regex handles: 。！？.!? followed by optional whitespace
        pattern = r'(?<=[。！？.!?])\s*'
        
        sentences = re.split(pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return int(len(text) / self.char_per_token)


def get_chunking_stats(chunks: List[Chunk]) -> dict:
    """
    Get statistics about a set of chunks.
    
    Args:
        chunks: List of chunks
        
    Returns:
        Dictionary with statistics
    """
    if not chunks:
        return {
            'total_chunks': 0,
            'total_tokens': 0,
            'avg_tokens': 0,
            'max_tokens': 0,
            'min_tokens': 0,
        }
    
    token_counts = [c.estimated_tokens for c in chunks]
    
    return {
        'total_chunks': len(chunks),
        'total_tokens': sum(token_counts),
        'avg_tokens': sum(token_counts) / len(chunks),
        'max_tokens': max(token_counts),
        'min_tokens': min(token_counts),
    }
