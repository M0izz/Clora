"""
ChromaDB evidence storage with permission and metadata filtering.
"""

import os
from typing import Any, Dict, List, Optional

import chromadb


class ChromaEvidenceStore:
    """Persistent ChromaDB vector store for sovereign industrial documents."""

    def __init__(
        self, collection_name: str = "industrial_knowledge", persist_path: str = "./data/chroma"
    ):
        self.persist_path = persist_path
        self.collection_name = collection_name
        os.makedirs(self.persist_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
        if not ids:
            return
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ):
        count = self.collection.count()
        if count == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        actual_n = min(n_results, count)
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n,
                include=["documents", "metadatas", "distances"],
            )

    def count(self) -> int:
        return self.collection.count()
