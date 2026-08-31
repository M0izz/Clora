"""
RAG Agent with permission filtering and self-healing query expansion.
"""

import re
from typing import Any, Dict, List, Optional

from backend.rag.chroma_store import ChromaEvidenceStore
from backend.rag.embeddings import LocalEmbeddingService
from backend.rag.evidence import Evidence
from backend.rag.retrieval import IndustrialQueryExpander, IndustrialReranker, PermissionFilter

EQUIPMENT_ID_REGEX = re.compile(
    r"\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b", re.IGNORECASE
)


class RAGAgent:
    """Retrieves industrial evidence with strict role filtering and self-healing re-retrieval."""

    def __init__(
        self,
        store: Optional[ChromaEvidenceStore] = None,
        embedder: Optional[LocalEmbeddingService] = None,
        reranker: Optional[IndustrialReranker] = None,
    ):
        self.store = store or ChromaEvidenceStore()
        self.embedder = embedder or LocalEmbeddingService()
        self.reranker = reranker or IndustrialReranker()

    def retrieve(
        self, query: str, user_role: str = "maintenance_engineer", top_k: int = 5
    ) -> List[Evidence]:
        eq_tags = EQUIPMENT_ID_REGEX.findall(query)
        equipment_id = eq_tags[0].upper() if eq_tags else None

        # 1. Initial vector retrieval
        q_vec = self.embedder.embed_query(query)
        where_filter = {"equipment_id": equipment_id} if equipment_id else None

        raw = self.store.query(query_embedding=q_vec, n_results=top_k * 4, where=where_filter)
        candidates = self._process_raw_results(raw, user_role)

        # 2. Self-healing re-retrieval loop if 0 results
        if not candidates:
            expanded_query, _ = IndustrialQueryExpander.expand_query(query)
            q_vec_exp = self.embedder.embed_query(expanded_query)
            raw_retry = self.store.query(query_embedding=q_vec_exp, n_results=top_k * 4)
            candidates = self._process_raw_results(raw_retry, user_role)

        # 3. Rerank
        reranked = self.reranker.rerank(query, candidates)

        # 4. Convert to Evidence models
        evidence_list: List[Evidence] = []
        for idx, item in enumerate(reranked, 1):
            meta = item.get("metadata", {})
            evidence_list.append(
                Evidence(
                    evidence_id=f"ev_{idx:03d}",
                    content=item.get("text", ""),
                    source_document=meta.get("document_name", "Document.pdf"),
                    page_number=int(meta.get("page", 1)),
                    chunk_id=item.get("chunk_id", f"c_{idx}"),
                    relevance_score=float(item.get("rerank_score", item.get("score", 0.9))),
                    equipment_id=meta.get("equipment_id"),
                    section=meta.get("section"),
                    metadata=meta,
                )
            )

        return evidence_list

    def _process_raw_results(self, raw: Dict[str, Any], user_role: str) -> List[Dict[str, Any]]:
        if not raw or not raw["documents"] or not raw["documents"][0]:
            return []

        docs = raw["documents"][0]
        metas = raw["metadatas"][0] if "metadatas" in raw and raw["metadatas"] else [{}] * len(docs)
        dists = (
            raw["distances"][0] if "distances" in raw and raw["distances"] else [0.0] * len(docs)
        )
        ids = raw["ids"][0] if "ids" in raw and raw["ids"] else [f"c_{i}" for i in range(len(docs))]

        results = []
        for doc_text, meta, dist, cid in zip(docs, metas, dists, ids):
            # Enforce RBAC
            allowed_roles_str = meta.get("allowed_roles", "")
            roles_list = (
                [r.strip() for r in allowed_roles_str.split(",") if r.strip()]
                if isinstance(allowed_roles_str, str)
                else allowed_roles_str
            )

            if not PermissionFilter.is_authorized(user_role, roles_list):
                continue

            score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
            results.append(
                {"chunk_id": cid, "text": doc_text, "score": round(score, 4), "metadata": meta}
            )
        return results
