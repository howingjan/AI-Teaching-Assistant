"""
Document retriever with TF-IDF based search.

Implements a local, interpretable retriever as Phase 1 baseline.
Can be extended with embedding-based retrieval in future phases.
"""

import logging
import math
import os
from typing import List, Optional
from collections import Counter
import re

from src.core.models import Chunk, SearchResult, Document
from src.core.config import Config

logger = logging.getLogger(__name__)


class TFIDFRetriever:
    """
    Simple TF-IDF based retriever for local document search.
    
    Advantages:
    - Fully interpretable (no black box embeddings)
    - No external dependencies
    - Fast for small to medium document sizes
    - Easy to debug and evaluate
    - Supports keyword-based filtering
    """
    
    def __init__(self, chunks: List[Chunk], documents: dict[str, Document]):
        """
        Initialize retriever with a corpus of chunks.
        
        Args:
            chunks: List of chunks to index
            documents: Dictionary of Document objects
        """
        self.chunks = chunks
        self.documents = documents
        self.vocab = set()
        self.doc_freqs = {}  # IDF cache
        self.chunk_term_freqs = {}  # TF cache
        
        self._build_index()
    
    def _build_index(self):
        """Build TF-IDF index from chunks."""
        # Build vocabulary and document frequencies
        all_terms = Counter()
        
        for chunk_id, chunk in enumerate(self.chunks):
            terms = self._tokenize(chunk.text)
            doc_terms = set(terms)
            
            # Store term frequencies for this chunk
            self.chunk_term_freqs[chunk_id] = Counter(terms)
            
            # Track document frequency
            for term in doc_terms:
                all_terms[term] += 1
        
        # Store vocab and compute IDF
        self.vocab = set(all_terms.keys())
        self.doc_freqs = {
            term: math.log(len(self.chunks) / count) if count > 0 else 0
            for term, count in all_terms.items()
        }
        
        logger.info(f"Built TF-IDF index: {len(self.chunks)} chunks, {len(self.vocab)} unique terms")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        document_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum relevance score (0-1)
            document_ids: Filter to specific documents (None = all)
            
        Returns:
            List of SearchResult objects, sorted by relevance
        """
        if not query or not query.strip():
            return []
        
        # Tokenize and compute query TF-IDF
        query_terms = self._tokenize(query)
        query_tf = Counter(query_terms)
        
        if not query_tf:
            return []
        
        # Score each chunk (only keep chunks with at least one matching term)
        scores = []
        
        for chunk_id, chunk in enumerate(self.chunks):
            # Apply document filter if provided
            if document_ids and chunk.document_id not in document_ids:
                continue
            
            # Compute TF-IDF score
            score = self._compute_similarity(query_tf, chunk_id)
            
            # Skip chunks with zero score (no matching terms)
            if score > 0:
                scores.append((chunk_id, score))
        
        # No matching chunks -> return empty (caller should surface "not found")
        if not scores:
            return []
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize scores to 0-1 range (relative to the top match)
        # Note: raw TF-IDF scores are small (e.g. 0.01~0.2), so we scale
        # them relative to the highest score rather than dividing by a
        # fixed constant, which would collapse everything to 0.00.
        max_score = scores[0][1]
        
        # Create results
        results = []
        for rank, (chunk_id, score) in enumerate(scores[:top_k]):
            normalized = score / max_score
            
            # Apply threshold on the normalized score
            if normalized < score_threshold:
                break
            
            result = SearchResult(
                chunk=self.chunks[chunk_id],
                score=normalized,
                rank=rank,
                reasoning=f"TF-IDF match on terms: {', '.join(query_terms[:5])}",
            )
            results.append(result)
        
        return results
    
    def search_by_keyword(
        self,
        keywords: List[str],
        top_k: int = 5,
        require_all: bool = False,
    ) -> List[SearchResult]:
        """
        Search for chunks containing specific keywords.
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of results to return
            require_all: If True, chunk must contain all keywords
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        for chunk_id, chunk in enumerate(self.chunks):
            chunk_text_lower = chunk.text.lower()
            matching_keywords = [kw for kw in keywords if kw.lower() in chunk_text_lower]
            
            if require_all:
                if len(matching_keywords) != len(keywords):
                    continue
            elif not matching_keywords:
                continue
            
            # Score based on keyword density
            keyword_count = sum(chunk_text_lower.count(kw.lower()) for kw in keywords)
            score = keyword_count / len(chunk.text.split())
            
            result = SearchResult(
                chunk=chunk,
                score=min(score, 1.0),
                rank=len(results),
                reasoning=f"Keyword match: {', '.join(matching_keywords)}",
            )
            results.append(result)
        
        # Sort by score and return top k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def get_chunk_context(
        self,
        chunk: Chunk,
        context_chunks: int = 2,
    ) -> str:
        """
        Get surrounding context around a chunk.
        
        Useful for expanding context window when passing to LLM.
        
        Args:
            chunk: The focal chunk
            context_chunks: Number of adjacent chunks to include
            
        Returns:
            Concatenated text with context
        """
        # Find chunk index
        chunk_idx = None
        for i, c in enumerate(self.chunks):
            if c.chunk_id == chunk.chunk_id:
                chunk_idx = i
                break
        
        if chunk_idx is None:
            return chunk.text
        
        # Gather context
        start_idx = max(0, chunk_idx - context_chunks)
        end_idx = min(len(self.chunks), chunk_idx + context_chunks + 1)
        
        context_parts = []
        for i in range(start_idx, end_idx):
            c = self.chunks[i]
            marker = ">>> FOCAL <<<" if i == chunk_idx else ""
            context_parts.append(f"{marker}\n{c.text}")
        
        return "\n".join(context_parts)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for indexing.
        
        Simple implementation: lowercase, split on whitespace and punctuation,
        remove stop words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\w+', text)
        
        # Filter stop words (basic English + Chinese common words)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            '的', '和', '是', '了', '有', '在', '中', '与', '这', '那',
        }
        
        tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
        
        return tokens
    
    def _compute_similarity(self, query_tf: Counter, chunk_id: int) -> float:
        """
        Compute TF-IDF similarity between query and chunk.
        
        Args:
            query_tf: Query term frequencies
            chunk_id: Chunk to score
            
        Returns:
            Similarity score (0-100)
        """
        chunk_tf = self.chunk_term_freqs.get(chunk_id, Counter())
        
        score = 0
        for term, freq in query_tf.items():
            if term in chunk_tf:
                # TF-IDF = TF * IDF
                tf = chunk_tf[term] / max(len(chunk_tf), 1)
                idf = self.doc_freqs.get(term, 0)
                score += tf * idf * freq
        
        return score


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
    Factory for creating different retriever types.
    
    Allows easy switching between retrieval strategies.
    """
    
    @staticmethod
    def create(
        retriever_type: str,
        chunks: List[Chunk],
        documents: dict[str, Document],
        **kwargs,
    ):
        """
        Create a retriever instance.
        
        Args:
            retriever_type: Type of retriever ("tfidf", "bm25", "embedding")
            chunks: Chunks to index
            documents: Documents
            **kwargs: Extra options for specific retrievers, e.g.
                model_name, cache_path for "embedding".
            
        Returns:
            Retriever instance
        """
        if retriever_type == "tfidf":
            return TFIDFRetriever(chunks, documents)
        elif retriever_type == "bm25":
            # TODO: Implement BM25Retriever
            raise NotImplementedError("BM25 retriever not yet implemented")
        elif retriever_type == "embedding":
            return EmbeddingRetriever(
                chunks,
                documents,
                model_name=kwargs.get("model_name", "intfloat/multilingual-e5-small"),
                cache_path=kwargs.get("cache_path", None),
            )
        else:
            raise ValueError(f"Unknown retriever type: {retriever_type}")
