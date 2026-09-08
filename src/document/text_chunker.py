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
        max_tokens: int = 400,
        overlap_sentences: int = 2,
        char_per_token: float = 1.5  # Rough estimate for Chinese
    ):
        """
        Initialize chunker.

        Args:
            max_tokens: Approximate maximum tokens per chunk (default 400 to stay
                within the e5-small 512-token embedding limit).
            overlap_sentences: Number of sentences to overlap between chunks
            char_per_token: Estimated characters per token (for Chinese ~1.5)
        """
        self.max_tokens = max_tokens
        self.overlap_sentences = overlap_sentences
        self.char_per_token = char_per_token
        self.max_chars = int(max_tokens * char_per_token)
        # 避免碎片化：段落边界只在块已累积到该比例时才断开
        self.min_block_chars = int(self.max_chars * 0.4)

    def chunk_page(self, page: Page, chunk_id_prefix: str = "") -> List[Chunk]:
        """
        Chunk a single page into semantic pieces with structural awareness.

        Strategy:
          1. Split the page text into paragraph blocks on blank lines
             (_split_blocks) so section / bullet boundaries act as preferred
             break points.
          2. Within each block, greedily merge sentences up to max_chars.
          3. Flush a chunk when the length limit is exceeded, or when a
             paragraph boundary is reached and the block already carries
             enough content (avoids fragmenting tiny headings).

        Args:
            page: Page object containing text and metadata
            chunk_id_prefix: Prefix for chunk IDs

        Returns:
            List of Chunk objects with source information
        """
        if not page.text or not page.text.strip():
            return []

        blocks = self._split_blocks(page.text)

        chunks = []
        current_chunk_sentences: List[str] = []
        current_length = 0
        chunk_counter = 0
        char_position = 0

        def flush() -> None:
            """Persist the pending sentences as a Chunk (keeping overlap)."""
            nonlocal current_chunk_sentences, current_length, chunk_counter
            if not current_chunk_sentences:
                return
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

            # Keep overlap for context continuity
            if self.overlap_sentences > 0 and current_chunk_sentences:
                overlap = current_chunk_sentences[-self.overlap_sentences:]
                current_chunk_sentences = overlap
                current_length = sum(len(s) for s in overlap)
            else:
                current_chunk_sentences = []
                current_length = 0

        for block in blocks:
            sentences = self._split_sentences(block)
            for sentence in sentences:
                sentence_length = len(sentence)
                # Length limit reached → break at sentence boundary
                if current_length + sentence_length > self.max_chars and current_chunk_sentences:
                    flush()
                current_chunk_sentences.append(sentence)
                current_length += sentence_length
                char_position += sentence_length
            # Paragraph boundary: flush if the block already has enough content
            if current_chunk_sentences and current_length >= self.min_block_chars:
                flush()

        # Handle remaining trailing sentences
        if current_chunk_sentences:
            flush()

        return chunks

    def _split_blocks(self, text: str) -> List[str]:
        """
        Split text into paragraph blocks on blank lines (structural awareness).

        Blank lines commonly separate sections / bullet groups in lecture
        slides, so treating them as preferred break points keeps chunks
        aligned with the document's own structure.
        """
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text)]
        return [b for b in blocks if b]
    
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
