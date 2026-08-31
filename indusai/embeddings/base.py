"""
Base interface for local embedding services.
Sovereign on-premise execution with no cloud API reliance.
"""

from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np

class BaseEmbeddingService(ABC):
    """Abstract base class for all local embedding models."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of document chunks."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Compute embedding for a single query string."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name or identifier of the local embedding model."""
        pass

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """Dimension size of the embedding vectors."""
        pass
