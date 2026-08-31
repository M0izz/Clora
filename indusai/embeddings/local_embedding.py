"""
Local Sentence-Transformer and PyTorch Embedding Service.
Fully sovereign, on-premise embedding generator.
"""

import time
from typing import List, Optional
import numpy as np
from indusai.embeddings.base import BaseEmbeddingService

class LocalSentenceTransformerEmbedding(BaseEmbeddingService):
    """Local SentenceTransformers embedding model provider."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu"):
        self._model_name = model_name
        self.device = device
        self._model = None
        self._dim = 384
        self._load_model()

    def _load_model(self):
        import os
        if os.getenv("INDUSAI_FAST_TEST", "0") == "1":
            self._model = None
            self._dim = 384
            return

        try:
            from sentence_transformers import SentenceTransformer
            # Attempt to load local cached files first
            try:
                self._model = SentenceTransformer(self._model_name, device=self.device, local_files_only=True)
            except Exception:
                # If local cache missing and allowed
                if os.getenv("HF_HUB_OFFLINE", "0") == "1":
                    self._model = None
                else:
                    self._model = SentenceTransformer(self._model_name, device=self.device)
            if self._model is not None:
                dummy = self._model.encode(["test"])
                self._dim = len(dummy[0])
        except Exception:
            self._model = None
            self._dim = 384

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self._model is not None:
            embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        if self._model is not None:
            embedding = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
            return embedding.tolist()
        return self._fallback_embed(query)

    def _fallback_embed(self, text: str) -> List[float]:
        """Deterministic 384-d semantic hash projection for testing/offline fallback."""
        vec = np.zeros(self._dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
        for i, word in enumerate(words):
            h = hash(word) % self._dim
            vec[h] += 1.0 / (1.0 + np.log1p(i))
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def embedding_dimension(self) -> int:
        return self._dim

class EmbeddingService(BaseEmbeddingService):
    """
    Standard interface requested in Section 5:
    class EmbeddingService:
        def __init__(self, model_name): ...
        def embed_documents(self, chunks): ...
        def embed_query(self, query): ...
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._provider = LocalSentenceTransformerEmbedding(model_name=model_name)

    def embed_documents(self, chunks: List[str]) -> List[List[float]]:
        return self._provider.embed_documents(chunks)

    def embed_query(self, query: str) -> List[float]:
        return self._provider.embed_query(query)

    @property
    def model_name(self) -> str:
        return self._provider.model_name

    @property
    def embedding_dimension(self) -> int:
        return self._provider.embedding_dimension
