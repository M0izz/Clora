"""
Reranker module for industrial RAG.
Combines semantic relevance with domain-specific industrial entity boosting.
"""

import re
from typing import List, Dict, Any, Optional

EQUIPMENT_ID_REGEX = re.compile(r'\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b', re.IGNORECASE)

class IndustrialReranker:
    """Reranks retrieved candidate chunks using domain-aware scoring and entity alignment."""

    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    def rerank(self, query: str, candidate_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not candidate_chunks:
            return []

        query_eqs = [eq.upper() for eq in EQUIPMENT_ID_REGEX.findall(query)]
        query_terms = set(re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', query.lower()))

        scored_chunks = []
        for item in candidate_chunks:
            base_score = float(item.get("score", 0.5))
            text = item.get("text", "").lower()
            meta = item.get("metadata")
            
            boost = 0.0

            # 1. Equipment ID alignment boost (+0.25)
            if query_eqs:
                chunk_eq = ""
                if hasattr(meta, "equipment_id") and meta.equipment_id:
                    chunk_eq = str(meta.equipment_id).upper()
                elif isinstance(meta, dict) and meta.get("equipment_id"):
                    chunk_eq = str(meta["equipment_id"]).upper()

                if any(eq in chunk_eq or eq.lower() in text for eq in query_eqs):
                    boost += 0.25

            # 2. Section priority boost for root cause / findings / inspection (+0.15)
            sec_title = ""
            if hasattr(meta, "section"):
                sec_title = str(meta.section).lower()
            elif isinstance(meta, dict):
                sec_title = str(meta.get("section", "")).lower()

            if any(k in sec_title for k in ["root cause", "finding", "inspection", "maintenance", "failure", "action"]):
                boost += 0.15

            # 3. Term overlap ratio
            chunk_terms = set(re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', text))
            if query_terms:
                overlap = len(query_terms.intersection(chunk_terms)) / len(query_terms)
                boost += overlap * 0.15

            final_score = min(1.0, max(0.0, base_score + boost))
            
            item_copy = dict(item)
            item_copy["rerank_score"] = round(final_score, 4)
            scored_chunks.append((final_score, item_copy))

        # Sort descending by rerank_score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_chunks[:self.top_k]]
