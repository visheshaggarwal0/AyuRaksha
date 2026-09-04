"""
AyuRaksha Embeddings Module
Implements IEmbeddingModule with dense vector generation.
Supports SentenceTransformers, FastEmbed, and clean normalized unit-vector fallback.
"""
from typing import List, Optional, Any
import hashlib
import math
import logging
from app.modules.interfaces import IEmbeddingModule

logger = logging.getLogger("AyuRaksha.Embeddings")


class ModularEmbeddingEngine(IEmbeddingModule):
    """Production implementation of IEmbeddingModule."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        self._model_name = model_name
        self._dim = dimension
        self._model: Any = None
        self._initialized = False

    @property
    def dimension(self) -> int:
        return self._dim

    def _get_model(self):
        if not self._initialized:
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    # Attempt instant local cache load first (0 network calls, 0 404s)
                    self._model = SentenceTransformer(self._model_name, local_files_only=True)
                except Exception:
                    self._model = SentenceTransformer(self._model_name)
                logger.info("Initialized SentenceTransformer('%s')", self._model_name)
            except Exception as e:
                logger.warning("sentence-transformers not available (%s); using deterministic unit vectors.", e)
                self._model = None
            self._initialized = True
        return self._model

    def _fallback_vector(self, text: str) -> List[float]:
        """Generates a deterministic 384-dimensional unit vector from text tokens."""
        vector = [0.0] * self._dim
        words = text.lower().split()
        if not words:
            return [1.0 / math.sqrt(self._dim)] * self._dim

        for w in words:
            # Map word hash into dimension bins
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vector[idx] += sign

        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [float(x / norm) for x in vector]

    async def embed_query(self, text: str) -> List[float]:
        model = self._get_model()
        if model is not None:
            try:
                import asyncio
                vec = await asyncio.to_thread(model.encode, text, normalize_embeddings=True)
                return [float(v) for v in vec]
            except Exception as e:
                logger.warning("Embedding encode error (%s); falling back.", e)

        return self._fallback_vector(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model is not None:
            try:
                import asyncio
                vectors = await asyncio.to_thread(model.encode, texts, normalize_embeddings=True)
                return [[float(v) for v in vec] for vec in vectors]
            except Exception as e:
                logger.warning("Batch embedding encode error (%s); falling back.", e)

        return [self._fallback_vector(t) for t in texts]


embedding_module = ModularEmbeddingEngine()

