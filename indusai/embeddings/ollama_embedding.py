"""
Ollama Local Embedding Provider.
Interacts with on-premise Ollama embedding models (e.g., nomic-embed-text, bge-m3).
"""

from typing import List, Optional
import httpx
from indusai.embeddings.base import BaseEmbeddingService

class OllamaEmbeddingService(BaseEmbeddingService):
    """Local Ollama embeddings for air-gapped sovereign execution."""

    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self._model_name = model_name
        self.base_url = base_url.rstrip("/")
        self._dim = 768

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(self.embed_query(text))
        return results

    def embed_query(self, query: str) -> List[float]:
        try:
            with httpx.Client(timeout=httpx.Timeout(2.0, connect=0.25)) as client:
                res = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self._model_name, "prompt": query}
                )
                if res.status_code == 200:
                    data = res.json()
                    vec = data.get("embedding", [])
                    if vec:
                        self._dim = len(vec)
                        return vec
        except Exception:
            pass
        # Fallback if local Ollama daemon is currently offline
        from indusai.embeddings.local_embedding import LocalSentenceTransformerEmbedding
        return LocalSentenceTransformerEmbedding().embed_query(query)

    @property
    def model_name(self) -> str:
        return f"ollama/{self._model_name}"

    @property
    def embedding_dimension(self) -> int:
        return self._dim
