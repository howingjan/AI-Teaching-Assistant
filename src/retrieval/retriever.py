"""
Document retrievers combining dense embeddings and lexical BM25 retrieval.
"""

import logging
import math
import os
import re
from collections import Counter
from typing import List, Optional

from src.core.models import Chunk, SearchResult, Document
from src.core.config import Config

logger = logging.getLogger(__name__)


class EmbeddingRetriever:
    """
    Dense retrieval using sentence-transformers embeddings.
    
    Uses a     multilingual model (e.g. intfloat/multilingual-e5-small) so that
    a query in one language (e.g. Chinese) can match documents in another
    (e.g. English), complementing the exact-term matches from BM25.
    
    Embeddings are cached to disk to avoid re-encoding the corpus on every run.
    Heavy dependencies (sentence-transformers, numpy) are imported lazily.
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


class HybridRetriever:
    """Combine multilingual dense retrieval with local BM25 keyword retrieval."""

    _RRF_K = 60
    _TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]+")

    def __init__(
        self,
        chunks: List[Chunk],
        documents: dict[str, Document],
        model_name: str = "intfloat/multilingual-e5-small",
        cache_path: Optional[str] = None,
    ):
        self.chunks = chunks
        self.documents = documents
        self.dense_retriever = EmbeddingRetriever(
            chunks,
            documents,
            model_name=model_name,
            cache_path=cache_path,
        )
        self._tokenized_chunks = [self._tokenize(chunk.text) for chunk in chunks]
        self._chunk_frequencies = [Counter(tokens) for tokens in self._tokenized_chunks]
        self._document_frequencies = Counter(
            term
            for frequencies in self._chunk_frequencies
            for term in frequencies
        )
        self._average_length = (
            sum(map(len, self._tokenized_chunks)) / len(self._tokenized_chunks)
            if self._tokenized_chunks
            else 0.0
        )

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        """Tokenize Latin terms and overlapping Chinese character n-grams."""
        tokens = []
        for part in cls._TOKEN_PATTERN.findall(text.lower()):
            if re.fullmatch(r"[\u4e00-\u9fff]+", part):
                tokens.extend(part)
                tokens.extend(part[i:i + 2] for i in range(len(part) - 1))
            else:
                tokens.append(part)
        return tokens

    def _keyword_search(
        self,
        query: str,
        candidate_k: int,
        document_ids: Optional[List[str]],
    ) -> List[int]:
        query_terms = set(self._tokenize(query))
        if not query_terms or not self.chunks:
            return []

        allowed_documents = set(document_ids) if document_ids is not None else None
        document_count = len(self.chunks)
        average_length = self._average_length or 1.0
        ranked = []

        for index, (chunk, frequencies, tokens) in enumerate(
            zip(self.chunks, self._chunk_frequencies, self._tokenized_chunks)
        ):
            if allowed_documents is not None and chunk.document_id not in allowed_documents:
                continue

            length = len(tokens)
            score = 0.0
            for term in query_terms:
                term_frequency = frequencies.get(term, 0)
                if not term_frequency:
                    continue
                document_frequency = self._document_frequencies[term]
                inverse_document_frequency = math.log1p(
                    (document_count - document_frequency + 0.5)
                    / (document_frequency + 0.5)
                )
                denominator = term_frequency + 1.5 * (
                    1 - 0.75 + 0.75 * length / average_length
                )
                score += inverse_document_frequency * (
                    term_frequency * (1.5 + 1) / denominator
                )
            if score > 0:
                ranked.append((index, score))

        ranked.sort(key=lambda item: item[1], reverse=True)
        return [index for index, _ in ranked[:candidate_k]]

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        document_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Retrieve dense and keyword candidates, then merge them with RRF."""
        if not query or not query.strip() or top_k <= 0:
            return []
        if not self.chunks:
            return []

        candidate_k = max(top_k * 5, 20)
        dense_results = self.dense_retriever.search(
            query,
            top_k=candidate_k,
            document_ids=document_ids,
        )
        keyword_indices = self._keyword_search(query, candidate_k, document_ids)

        dense_ranks = {
            (result.chunk.document_id, result.chunk.chunk_id): rank
            for rank, result in enumerate(dense_results, start=1)
        }
        keyword_ranks = {
            (self.chunks[index].document_id, self.chunks[index].chunk_id): rank
            for rank, index in enumerate(keyword_indices, start=1)
        }
        chunk_by_key = {
            (chunk.document_id, chunk.chunk_id): chunk for chunk in self.chunks
        }

        fused_scores = {}
        for key in dense_ranks.keys() | keyword_ranks.keys():
            score = 0.0
            if key in dense_ranks:
                score += 1 / (self._RRF_K + dense_ranks[key])
            if key in keyword_ranks:
                score += 1 / (self._RRF_K + keyword_ranks[key])
            fused_scores[key] = score

        max_score = max(fused_scores.values(), default=0.0)
        ranked = sorted(fused_scores, key=fused_scores.get, reverse=True)
        results = []
        for key in ranked:
            score = fused_scores[key] / max_score
            if score < score_threshold:
                continue
            dense_rank = dense_ranks.get(key)
            keyword_rank = keyword_ranks.get(key)
            results.append(SearchResult(
                chunk=chunk_by_key[key],
                score=score,
                rank=len(results),
                reasoning=(
                    f"Hybrid RRF (dense rank: {dense_rank or '-'}, "
                    f"keyword rank: {keyword_rank or '-'})"
                ),
            ))
            if len(results) >= top_k:
                break
        return results


class RetrieverFactory:
    """
    Factory for creating document retrievers.
    """

    @staticmethod
    def create(
        retriever_type: str = "hybrid",
        chunks: List[Chunk] = None,
        documents: dict[str, Document] = None,
        **kwargs,
    ):
        """
        Create a dense or hybrid retriever.

        Args:
            retriever_type: "embedding" for dense-only or "hybrid" for dense + BM25.
            chunks: Chunks to index
            documents: Documents
            **kwargs: Extra options, e.g. model_name / cache_path.

        Returns:
            The selected retriever instance.
        """
        retriever_class = {
            "embedding": EmbeddingRetriever,
            "hybrid": HybridRetriever,
        }.get(retriever_type)
        if retriever_class is None:
            raise ValueError(
                f"Unsupported retriever type: {retriever_type} "
                "(expected 'embedding' or 'hybrid')"
            )
        return retriever_class(
            chunks,
            documents,
            model_name=kwargs.get("model_name", "intfloat/multilingual-e5-small"),
            cache_path=kwargs.get("cache_path", None),
        )
