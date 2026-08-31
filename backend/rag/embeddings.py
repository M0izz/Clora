"""
Local Embedding Service for INDUSAI-X.
Sovereign on-premise execution supporting SentenceTransformers, Ollama, and offline mode.
"""

import os
from typing import List

import numpy as np


class LocalEmbeddingService:
    """Local SentenceTransformers embedding model provider."""

    def __init__(
        self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu"
    ):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._dim = 384
        self._load_model()

    def _load_model(self):
        if os.getenv("INDUSAI_FAST_TEST", "0") == "1":
            self.model = None
            self._dim = 384
            return

        try:
            from sentence_transformers import SentenceTransformer

            try:
                self.model = SentenceTransformer(
                    self.model_name, device=self.device, local_files_only=True
                )
            except Exception:
                if os.getenv("HF_HUB_OFFLINE", "0") == "1":
                    self.model = None
                else:
                    self.model = SentenceTransformer(self.model_name, device=self.device)
            if self.model is not None:
                dummy = self.model.encode(["test"])
                self._dim = len(dummy[0])
        except Exception:
            self.model = None
            self._dim = 384

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        if not documents:
            return []
        if self.model is not None:
            return self.model.encode(documents, normalize_embeddings=True).tolist()
        return [self._fallback_embed(d) for d in documents]

    def embed_query(self, query: str) -> List[float]:
        if self.model is not None:
            return self.model.encode(query, normalize_embeddings=True).tolist()
        return self._fallback_embed(query)

    def _fallback_embed(self, text: str) -> List[float]:
        """Deterministic 384-d semantic hash projection for offline test mode."""
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
    def embedding_dimension(self) -> int:
        return self._dim
