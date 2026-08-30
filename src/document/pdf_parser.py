"""
PDF document parser with structured metadata preservation.

Extracts text from PDFs while tracking page numbers, document IDs,
and parse quality indicators for reliable citation.
"""

import pdfplumber
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from src.core.models import Document, DocumentType, Page, ParseQuality

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts text from PDFs with quality tracking."""
    
    def __init__(self, max_chars_per_page: int = 5000):
        """
        Initialize PDF parser.
        
        Args:
            max_chars_per_page: Maximum characters to extract per page (prevents memory issues)
        """
        self.max_chars_per_page = max_chars_per_page
    
    @staticmethod
    def generate_document_id(file_path: str, file_name: str) -> str:
        """Generate unique document ID based on file content hash."""
        try:
            with open(file_path, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()[:8]
        except Exception:
            # Fallback if file read fails
            content_hash = hashlib.md5(file_name.encode()).hexdigest()[:8]
        
        # Clean filename for ID
        clean_name = Path(file_name).stem.lower().replace(' ', '_')[:20]
        return f"{clean_name}_{content_hash}"
    
    def parse_pdf(self, file_path: str, file_name: str) -> Tuple[Document, list[Page]]:
        """
        Parse a PDF file and extract structured content.
        
        Args:
            file_path: Path to PDF file
            file_name: Original filename
            
        Returns:
            Tuple of (Document metadata, List of Page objects)
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF is corrupted
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        document_id = self.generate_document_id(str(file_path), file_name)
        pages = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                metadata = {
                    'title': pdf.metadata.get('Title') if pdf.metadata else '',
                    'author': pdf.metadata.get('Author') if pdf.metadata else '',
                    'subject': pdf.metadata.get('Subject') if pdf.metadata else '',
                    'file_size_mb': file_path.stat().st_size / (1024 * 1024),
                    'original_path': str(file_path),
                }
                
                total_pages = len(pdf.pages)
                parse_quality = ParseQuality.GOOD
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ''
                        
                        # Determine page quality
                        if not text or len(text.strip()) == 0:
                            page_quality = ParseQuality.EMPTY
                        elif len(text) < 50:
                            # Likely a scanned page or image-only
                            page_quality = ParseQuality.SCANNED
                        else:
                            page_quality = ParseQuality.GOOD
                        
                        # Truncate if too long
                        if len(text) > self.max_chars_per_page:
                            text = text[:self.max_chars_per_page]
                            page_quality = ParseQuality.PARTIAL
                        
                        # Check for tables and images
                        has_tables = bool(page.extract_tables())
                        has_images = len(page.images) > 0 if hasattr(page, 'images') else False
                        
                        # Look for code-like patterns
                        has_code = '```' in text or 'def ' in text or 'class ' in text
                        
                        page_obj = Page(
                            document_id=document_id,
                            page_number=page_num,
                            text=text,
                            quality=page_quality,
                            sections=[],  # Could be enhanced with heading detection
                            has_tables=has_tables,
                            has_images=has_images,
                            has_code=has_code,
                        )
                        
                        pages.append(page_obj)
                        
                        if page_quality != ParseQuality.GOOD:
                            parse_quality = ParseQuality.PARTIAL
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        # Create empty page record
                        page_obj = Page(
                            document_id=document_id,
                            page_number=page_num,
                            text='',
                            quality=ParseQuality.ERROR,
                        )
                        pages.append(page_obj)
                        parse_quality = ParseQuality.PARTIAL
                
            # Create document object
            document = Document(
                document_id=document_id,
                file_name=file_name,
                file_path=str(file_path),
                document_type=DocumentType.PDF,
                total_pages=total_pages,
                metadata=metadata,
                parse_quality=parse_quality,
                created_at=datetime.now(),
            )
            
            logger.info(f"Successfully parsed PDF: {file_name} ({total_pages} pages, id: {document_id})")
            
            return document, pages
            
        except pdfplumber.PDFException as e:
            logger.error(f"PDF parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while parsing PDF: {e}")
            raise
    
    def get_page_range(self, file_path: str, start_page: int = 0, end_page: Optional[int] = None) -> str:
        """
        Extract text from a page range (useful for preview).
        
        Args:
            file_path: Path to PDF
            start_page: Starting page (0-indexed)
            end_page: Ending page (0-indexed, inclusive)
            
        Returns:
            Concatenated text from page range
        """
        with pdfplumber.open(file_path) as pdf:
            total = len(pdf.pages)
            end = min(end_page or total - 1, total - 1)
            
            text_parts = []
            for i in range(start_page, end + 1):
                if 0 <= i < total:
                    page_text = pdf.pages[i].extract_text() or ''
                    text_parts.append(f"--- Page {i} ---\n{page_text}")
            
            return "\n\n".join(text_parts)


def get_pdf_stats(file_path: str) -> dict:
    """
    Quick statistics about a PDF without full text extraction.
    
    Args:
        file_path: Path to PDF
        
    Returns:
        Dictionary with page_count, file_size, has_text, etc.
    """
    file_path = Path(file_path)
    stats = {
        'page_count': 0,
        'file_size_mb': 0,
        'has_text': False,
        'has_images': False,
        'has_tables': False,
    }
    
    try:
        stats['file_size_mb'] = round(file_path.stat().st_size / (1024 * 1024), 2)
        
        with pdfplumber.open(file_path) as pdf:
            stats['page_count'] = len(pdf.pages)
            
            # Sample first page to check for text
            if pdf.pages:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                stats['has_text'] = bool(text and len(text.strip()) > 0)
                stats['has_tables'] = bool(first_page.extract_tables())
                stats['has_images'] = len(first_page.images) > 0 if hasattr(first_page, 'images') else False
    
    except Exception as e:
        logger.error(f"Error getting PDF stats: {e}")
    
    return stats
