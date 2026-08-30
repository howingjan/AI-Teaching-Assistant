"""
Document loader and indexer.

Handles file validation, parsing, chunking, and index persistence.
Single entry point for ingesting course materials into the system.
"""

import logging
import json
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from src.core.models import Document, Chunk, Page, IndexMetadata, DocumentType, ParseQuality
from src.core.config import Config
from src.document.pdf_parser import PDFParser
from src.document.text_chunker import TextChunker

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Loads and indexes course materials.
    """
    
    def __init__(
        self,
        index_name: str = "default",
        chunker: Optional[TextChunker] = None,
        pdf_parser: Optional[PDFParser] = None,
    ):
        """
        Initialize document loader.
        
        Args:
            index_name: Name for this index (used for file storage)
            chunker: Text chunker instance (uses defaults if None)
            pdf_parser: PDF parser instance (uses defaults if None)
        """
        self.index_name = index_name
        self.chunker = chunker or TextChunker(
            max_tokens=Config.document.chunk_max_tokens,
            overlap_sentences=Config.document.chunk_overlap_sentences,
        )
        self.pdf_parser = pdf_parser or PDFParser(
            max_chars_per_page=Config.document.max_chars_per_page
        )
        
        # In-memory storage
        self.documents: dict[str, Document] = {}  # document_id -> Document
        self.chunks: List[Chunk] = []
        self.metadata = IndexMetadata()
        
        # Load existing index if it exists
        self._load_index_from_disk()
    
    def load_document(self, file_path: str, file_name: Optional[str] = None) -> Tuple[Document, List[Chunk]]:
        """
        Load a single document and generate chunks.
        
        Args:
            file_path: Path to document file
            file_name: Original filename (if different from file_path)
            
        Returns:
            Tuple of (Document, List of Chunks)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_name is None:
            file_name = file_path.name
        
        # Check file type
        suffix = file_path.suffix.lower()
        if suffix not in Config.document.supported_formats:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: {Config.document.supported_formats}")
        
        # Parse based on type
        if suffix == '.pdf':
            document, pages = self.pdf_parser.parse_pdf(str(file_path), file_name)
        elif suffix in ('.txt', '.md'):
            document, pages = self._parse_text_file(str(file_path), file_name, suffix)
        else:
            raise NotImplementedError(f"Format {suffix} not yet implemented")
        
        # Check if document already indexed
        if document.document_id in self.documents:
            logger.warning(f"Document already indexed: {document.document_id}")
            return self.documents[document.document_id], []
        
        # Chunk pages
        chunks = self.chunker.chunk_pages(pages, chunk_id_prefix=document.document_id)
        
        # Store in memory
        self.documents[document.document_id] = document
        self.chunks.extend(chunks)
        
        # Update metadata
        self.metadata.total_documents = len(self.documents)
        self.metadata.total_chunks = len(self.chunks)
        self.metadata.document_ids = list(self.documents.keys())
        self.metadata.last_updated = datetime.now()
        
        logger.info(f"Loaded: {file_name} -> {document.document_id} ({len(chunks)} chunks)")
        
        return document, chunks
    
    def _parse_text_file(
        self,
        file_path,
        file_name: str,
        suffix: str,
    ) -> Tuple[Document, List[Page]]:
        """Parse a plain-text / Markdown file into a single-page document."""
        from src.document.pdf_parser import PDFParser

        file_path = Path(file_path)
        document_id = PDFParser.generate_document_id(str(file_path), file_name)
        text = file_path.read_text(encoding="utf-8", errors="replace")

        document_type = (
            DocumentType.MARKDOWN if suffix == ".md" else DocumentType.TEXT
        )
        quality = ParseQuality.GOOD if text.strip() else ParseQuality.EMPTY

        metadata = {
            "file_size_kb": round(file_path.stat().st_size / 1024, 2),
            "original_path": str(file_path),
            "chars": len(text),
        }

        page = Page(
            document_id=document_id,
            page_number=0,
            text=text[: Config.document.max_chars_per_page * 20],
            quality=quality,
            sections=[self._infer_section(text)] if self._infer_section(text) else [],
            has_code="```" in text or "def " in text or "class " in text,
        )

        document = Document(
            document_id=document_id,
            file_name=file_name,
            file_path=str(file_path),
            document_type=document_type,
            total_pages=1,
            metadata=metadata,
            parse_quality=quality,
            created_at=datetime.now(),
        )
        return document, [page]

    @staticmethod
    def _infer_section(text: str) -> str:
        """Best-effort first Markdown heading as the page's section name."""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()[:60]
        return ""

    def get_document_structure(self, document_id: str) -> dict:
        """
        Describe a document's internal structure: pages, sections, chunk count,
        quality summary. Used by the UI's 资料库 page and as the
        `get_document_structure` capability from the product plan.
        """
        if document_id not in self.documents:
            return {}

        doc = self.documents[document_id]
        doc_chunks = [c for c in self.chunks if c.document_id == document_id]
        pages_by_quality: dict = {}
        section_set: set = set()
        for c in doc_chunks:
            if c.section:
                section_set.add(c.section)

        # Reconstruct per-page quality from the index is not stored; approximate
        # from chunk text length where possible.
        return {
            "document_id": document_id,
            "file_name": doc.file_name,
            "total_pages": doc.total_pages,
            "document_type": doc.document_type.value,
            "parse_quality": doc.parse_quality.value,
            "total_chunks": len(doc_chunks),
            "sections": sorted(section_set)[:20],
            "pages_by_quality": pages_by_quality,
            "metadata": doc.metadata,
        }

    def load_documents_from_directory(self, directory: str) -> Tuple[List[Document], List[Chunk]]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory: Path to directory containing documents
            
        Returns:
            Tuple of (List of Documents, List of all Chunks)
        """
        dir_path = Path(directory)
        
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        documents = []
        all_chunks = []
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in Config.document.supported_formats:
                try:
                    doc, chunks = self.load_document(str(file_path))
                    documents.append(doc)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
                    continue
        
        return documents, all_chunks
    
    def get_document_info(self, document_id: str) -> dict:
        """
        Get information about a loaded document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary with document info
        """
        if document_id not in self.documents:
            return {}
        
        doc = self.documents[document_id]
        doc_chunks = [c for c in self.chunks if c.document_id == document_id]
        
        return {
            'document_id': document_id,
            'file_name': doc.file_name,
            'document_type': doc.document_type.value,
            'total_pages': doc.total_pages,
            'parse_quality': doc.parse_quality.value,
            'total_chunks': len(doc_chunks),
            'metadata': doc.metadata,
            'created_at': doc.created_at.isoformat(),
        }
    
    def get_index_stats(self) -> dict:
        """Get overall index statistics."""
        return {
            'total_documents': self.metadata.total_documents,
            'total_chunks': self.metadata.total_chunks,
            'documents': self.metadata.document_ids,
            'created_at': self.metadata.created_at.isoformat(),
            'last_updated': self.metadata.last_updated.isoformat(),
            'index_version': self.metadata.index_version,
        }
    
    def save_index(self, index_path: Optional[str] = None) -> str:
        """
        Save index to disk (JSON format).
        
        Args:
            index_path: Path to save index (uses default if None)
            
        Returns:
            Path where index was saved
        """
        if index_path is None:
            index_path = str(Config.get_index_path(self.index_name))
        
        index_path = Path(index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for serialization
        index_data = {
            'metadata': {
                'index_version': self.metadata.index_version,
                'created_at': self.metadata.created_at.isoformat(),
                'last_updated': self.metadata.last_updated.isoformat(),
                'total_documents': self.metadata.total_documents,
                'total_chunks': self.metadata.total_chunks,
                'document_ids': self.metadata.document_ids,
            },
            'documents': {
                doc_id: {
                    'document_id': doc.document_id,
                    'file_name': doc.file_name,
                    'file_path': doc.file_path,
                    'document_type': doc.document_type.value,
                    'total_pages': doc.total_pages,
                    'parse_quality': doc.parse_quality.value,
                    'metadata': doc.metadata,
                    'created_at': doc.created_at.isoformat(),
                }
                for doc_id, doc in self.documents.items()
            },
            'chunks': [
                {
                    'chunk_id': c.chunk_id,
                    'document_id': c.document_id,
                    'page_number': c.page_number,
                    'text': c.text,
                    'char_start': c.char_start,
                    'char_end': c.char_end,
                    'section': c.section,
                    'estimated_tokens': c.estimated_tokens,
                    'order_in_doc': c.order_in_doc,
                }
                for c in self.chunks
            ]
        }
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Index saved to {index_path}")
        return str(index_path)
    
    def _load_index_from_disk(self) -> bool:
        """
        Load index from disk if it exists.
        
        Returns:
            True if index was loaded, False otherwise
        """
        index_path = Config.get_index_path(self.index_name)
        
        if not index_path.exists():
            logger.info(f"No existing index at {index_path}")
            return False
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Load metadata
            meta = index_data.get('metadata', {})
            self.metadata = IndexMetadata(
                index_version=meta.get('index_version', '1.0'),
                created_at=datetime.fromisoformat(meta.get('created_at', datetime.now().isoformat())),
                last_updated=datetime.fromisoformat(meta.get('last_updated', datetime.now().isoformat())),
                total_documents=meta.get('total_documents', 0),
                total_chunks=meta.get('total_chunks', 0),
                document_ids=meta.get('document_ids', []),
            )
            
            # Load documents
            for doc_id, doc_data in index_data.get('documents', {}).items():
                doc = Document(
                    document_id=doc_data['document_id'],
                    file_name=doc_data['file_name'],
                    file_path=doc_data['file_path'],
                    document_type=DocumentType(doc_data['document_type']),
                    total_pages=doc_data.get('total_pages'),
                    metadata=doc_data.get('metadata', {}),
                    parse_quality=ParseQuality(doc_data.get('parse_quality', 'good')),
                    created_at=datetime.fromisoformat(doc_data.get('created_at', datetime.now().isoformat())),
                )
                self.documents[doc_id] = doc
            
            # Load chunks
            for chunk_data in index_data.get('chunks', []):
                chunk = Chunk(
                    chunk_id=chunk_data['chunk_id'],
                    document_id=chunk_data['document_id'],
                    page_number=chunk_data['page_number'],
                    text=chunk_data['text'],
                    char_start=chunk_data.get('char_start', 0),
                    char_end=chunk_data.get('char_end', 0),
                    section=chunk_data.get('section'),
                    estimated_tokens=chunk_data.get('estimated_tokens', 0),
                    order_in_doc=chunk_data.get('order_in_doc', 0),
                )
                self.chunks.append(chunk)
            
            logger.info(f"Loaded index: {self.metadata.total_documents} documents, {self.metadata.total_chunks} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
