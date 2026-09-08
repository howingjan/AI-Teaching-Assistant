"""
Embedding-based document retriever (dense retrieval via sentence-transformers).
"""

import logging
import os
from typing import List, Optional

from src.core.models import Chunk, SearchResult, Document
from src.core.config import Config

logger = logging.getLogger(__name__)


class EmbeddingRetriever:
    """
    Dense retrieval using sentence-transformers embeddings.
    
    Uses a multilingual model (e.g. intfloat/multilingual-e5-small) so that
    a query in one language (e.g. Chinese) can match documents in another
    (e.g. English). This is the key advantage over TF-IDF's exact-term match,
    which cannot bridge "hotel" and "accommodation" or cross-language terms.
    
    Embeddings are cached to disk to avoid re-encoding the corpus on every run.
    Heavy dependencies (sentence-transformers, numpy) are imported lazily so
    that TF-IDF users do not pay the import cost.
    """
    
    def __init__(
        self,
        chunks: List[Chunk],
        documents: dict[str, Document],
        model_name: str = "intfloat/multilingual-e5-small",
        cache_path: Optional[str] = None,
    ):
        """
        Args:
            chunks: Chunks to index
            documents: Dictionary of Document objects
            model_name: Sentence-transformers model to use
            cache_path: Path to cache encoded chunk embeddings (.npy)
        """
        self.chunks = chunks
        self.documents = documents
        self.model_name = model_name
        self.cache_path = cache_path
        
        # Lazy-loaded state
        self._model = None
        self._embeddings = None
    
    def _load_model(self):
        """Load the sentence-transformers model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def _embed(self, texts: List[str], is_query: bool = False):
        """Encode texts into normalized embedding vectors."""
        import numpy as np
        model = self._load_model()
        # E5-family models require "query: " / "passage: " prefixes to work well
        prefix = "query: " if is_query else "passage: "
        prefixed = [prefix + t for t in texts]
        return model.encode(
            prefixed,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
    
    def _get_chunk_embeddings(self):
        """Return chunk embeddings, loading from cache if available."""
        if self._embeddings is None:
            if self.cache_path and os.path.exists(self.cache_path):
                import numpy as np
                logger.info(f"Loading cached embeddings from {self.cache_path}")
                self._embeddings = np.load(self.cache_path)
            else:
                texts = [c.text for c in self.chunks]
                logger.info(f"Encoding {len(texts)} chunks (first run, may take a while)...")
                self._embeddings = self._embed(texts, is_query=False)
                if self.cache_path:
                    import numpy as np
                    np.save(self.cache_path, self._embeddings)
                    logger.info(f"Cached embeddings to {self.cache_path}")
        return self._embeddings
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        document_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Search for relevant chunks by cosine similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum cosine similarity (0-1)
            document_ids: Filter to specific documents (None = all)
            
        Returns:
            List of SearchResult objects, sorted by similarity
        """
        import numpy as np
        
        if not query or not query.strip():
            return []
        
        chunk_embeddings = self._get_chunk_embeddings()
        query_embedding = self._embed([query], is_query=True)[0]
        
        # Cosine similarity (vectors are normalized, so dot product == cosine)
        similarities = chunk_embeddings @ query_embedding
        
        # Rank chunks by similarity, applying document filter and threshold
        ranked = sorted(
            enumerate(similarities),
            key=lambda x: x[1],
            reverse=True,
        )
        
        results = []
        for chunk_id, sim in ranked:
            chunk = self.chunks[chunk_id]
            
            if document_ids and chunk.document_id not in document_ids:
                continue
            
            sim = float(sim)
            if sim < score_threshold:
                break  # sorted descending, so remaining are all below threshold
            
            results.append(SearchResult(
                chunk=chunk,
                score=sim,
                rank=len(results),
                reasoning=f"Embedding cosine similarity: {sim:.4f}",
            ))
            
            if len(results) >= top_k:
                break
        
        return results


class RetrieverFactory:
    """
    Factory for creating the embedding retriever.
    """

    @staticmethod
    def create(
        retriever_type: str = "embedding",
        chunks: List[Chunk] = None,
        documents: dict[str, Document] = None,
        **kwargs,
    ):
        """
        Create an EmbeddingRetriever.

        Args:
            retriever_type: Must be "embedding" (kept for API compatibility).
            chunks: Chunks to index
            documents: Documents
            **kwargs: Extra options, e.g. model_name / cache_path.

        Returns:
            EmbeddingRetriever instance
        """
        if retriever_type != "embedding":
            raise ValueError(
                f"Unsupported retriever type: {retriever_type} (only 'embedding')"
            )
        return EmbeddingRetriever(
            chunks,
            documents,
            model_name=kwargs.get("model_name", "intfloat/multilingual-e5-small"),
            cache_path=kwargs.get("cache_path", None),
        )
