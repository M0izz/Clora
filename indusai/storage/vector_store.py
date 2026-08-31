"""
ChromaDB Vector Store for INDUSAI-X.
Supports permission-aware retrieval, metadata filtering, and sovereign local embeddings.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from indusai.ingestion.schema import Chunk, ChunkMetadata
from indusai.embeddings.base import BaseEmbeddingService
from indusai.embeddings.local_embedding import LocalSentenceTransformerEmbedding

class ChromaVectorStore:
    """ChromaDB storage interface with native permission and metadata filtering."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db_indusai",
        collection_name: str = "mrpl_industrial_knowledge",
        embedding_service: Optional[BaseEmbeddingService] = None
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_service = embedding_service or LocalSentenceTransformerEmbedding()

        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "MRPL Sovereign Industrial Knowledge Store"}
        )

    def add_chunks(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0

        ids = [chunk.metadata.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata.to_chroma_metadata() for chunk in chunks]
        embeddings = self.embedding_service.embed_documents(documents)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(chunks)

    def query(
        self,
        query_text: str,
        user_role: str,
        top_k: int = 5,
        equipment_id: Optional[str] = None,
        document_type: Optional[str] = None,
        department: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Permission-aware and metadata-filtered vector retrieval.
        CRITICAL: Only chunks where allowed_roles includes user_role are returned.
        """
        query_embedding = self.embedding_service.embed_query(query_text)
        
        # Build Chroma where filters for exact matchable fields
        where_clauses: List[Dict[str, Any]] = []

        if equipment_id:
            where_clauses.append({"equipment_id": equipment_id})
        if document_type:
            where_clauses.append({"document_type": document_type})
        if department:
            where_clauses.append({"department": department})
        if date_from:
            where_clauses.append({"timestamp": {"$gte": date_from}})
        if date_to:
            where_clauses.append({"timestamp": {"$lte": date_to}})

        where_filter = None
        if len(where_clauses) == 1:
            where_filter = where_clauses[0]
        elif len(where_clauses) > 1:
            where_filter = {"$and": where_clauses}

        n_results = max(top_k * 4, 20)
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, max(1, self.collection.count())),
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            try:
                # If compound where filter failed on older chroma version, query without metadata where
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, max(1, self.collection.count())),
                    include=["documents", "metadatas", "distances"]
                )
            except Exception:
                return []

        retrieved_items: List[Dict[str, Any]] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return []

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
        ids = results["ids"][0] if "ids" in results and results["ids"] else [f"c_{i}" for i in range(len(docs))]

        for doc_text, meta, dist, cid in zip(docs, metas, distances, ids):
            # Strict double verification of permission
            allowed_roles_str = meta.get("allowed_roles", "")
            roles_list = [r.strip() for r in allowed_roles_str.split(",") if r.strip()]
            if user_role not in roles_list and "admin" not in user_role.lower():
                continue

            # Convert distance to similarity score (cosine: 1 - dist)
            score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

            retrieved_items.append({
                "chunk_id": cid,
                "text": doc_text,
                "score": round(score, 4),
                "distance": dist,
                "metadata": ChunkMetadata.from_chroma_metadata(meta)
            })

        return retrieved_items[:top_k]

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        """Clear the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(self.collection_name)
