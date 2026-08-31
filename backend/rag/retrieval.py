"""
Retrieval orchestration, permission filtering, reranking, and self-healing query expansion.
"""

import re
from typing import Any, Dict, List, Tuple

EQUIPMENT_ID_REGEX = re.compile(
    r"\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b", re.IGNORECASE
)

EQUIPMENT_DESCRIPTOR_MAP = {
    "P-101": ["booster pump 101", "booster pump", "crude feed pump", "centrifugal pump p-101"],
    "P-102": ["slurry pump", "slurry circulation pump", "heavy oil pump p-102"],
    "K-201": ["wet gas compressor", "gas compressor k-201", "compressor 201"],
    "HEX-301": ["pre-heat exchanger", "crude exchanger hex-301", "heat exchanger 301"],
    "TK-502": ["naphtha storage tank", "storage tank 502", "tank tk-502"],
    "MOV-102": ["motor operated valve", "isolation valve 102", "emergency shutoff valve"],
    "FCV-204": ["flow control valve", "reflux valve 204", "valve fcv-204"],
}

TECHNICAL_SYNONYMS = {
    "overheat": [
        "temperature exceeded normal",
        "thermal excursion",
        "high bearing temperature",
        "overheating",
    ],
    "fail": ["failure", "breakdown", "tripped", "shutdown", "rupture", "malfunction"],
    "contamination": [
        "particulate presence",
        "foreign debris",
        "degraded lube oil",
        "moisture ingress",
    ],
    "leak": ["loss of containment", "seal leakage", "gasket blow-out"],
    "vibration": ["high harmonics", "elevated vibration levels", "shaft misalignment", "unbalance"],
}


class PermissionFilter:
    """Enforces strict RBAC filtering at retrieval time."""

    @staticmethod
    def is_authorized(user_role: str, allowed_roles: List[str]) -> bool:
        if not user_role or not allowed_roles:
            return False
        if "plant_manager" in user_role.lower() or "admin" in user_role.lower():
            return True
        return user_role.lower().strip() in [r.lower().strip() for r in allowed_roles]


class IndustrialQueryExpander:
    """Expands ambiguous/colloquial queries into technical search aliases."""

    @classmethod
    def expand_query(cls, query: str) -> Tuple[str, List[str]]:
        expansions = []
        parts = [query]

        # Expand equipment tag
        tags = EQUIPMENT_ID_REGEX.findall(query)
        for t in tags:
            tu = t.upper()
            if tu in EQUIPMENT_DESCRIPTOR_MAP:
                aliases = EQUIPMENT_DESCRIPTOR_MAP[tu]
                parts.extend([a.title() for a in aliases[:2]])
                expansions.append(f"Tag {tu} -> {aliases[:2]}")

        # Reverse colloquial mapping
        ql = query.lower()
        for tag, aliases in EQUIPMENT_DESCRIPTOR_MAP.items():
            if tag.lower() not in ql:
                for a in aliases:
                    if a in ql or a.replace(" ", "") in ql.replace(" ", ""):
                        parts.append(tag)
                        expansions.append(f"Alias {a} -> {tag}")
                        break

        for term, syns in TECHNICAL_SYNONYMS.items():
            if term in ql:
                for s in syns[:2]:
                    if s not in ql:
                        parts.append(s)
                        expansions.append(f"Synonym {term} -> {s}")

        return " ".join(dict.fromkeys(parts)), expansions


class IndustrialReranker:
    """Domain-aware reranking prioritizing equipment IDs and findings sections."""

    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    def rerank(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        query_eqs = [eq.upper() for eq in EQUIPMENT_ID_REGEX.findall(query)]
        query_terms = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query.lower()))

        scored = []
        for item in candidates:
            base_score = float(item.get("score", 0.5))
            text = item.get("text", "").lower()
            meta = item.get("metadata", {})
            boost = 0.0

            chunk_eq = ""
            if hasattr(meta, "equipment_id") and meta.equipment_id:
                chunk_eq = str(meta.equipment_id).upper()
            elif isinstance(meta, dict) and meta.get("equipment_id"):
                chunk_eq = str(meta["equipment_id"]).upper()

            if query_eqs and any(eq in chunk_eq or eq.lower() in text for eq in query_eqs):
                boost += 0.25

            sec_title = ""
            if hasattr(meta, "section"):
                sec_title = str(meta.section).lower()
            elif isinstance(meta, dict):
                sec_title = str(meta.get("section", "")).lower()

            if any(
                k in sec_title
                for k in ["root cause", "finding", "inspection", "maintenance", "failure", "action"]
            ):
                boost += 0.15

            chunk_terms = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", text))
            if query_terms:
                overlap = len(query_terms.intersection(chunk_terms)) / len(query_terms)
                boost += overlap * 0.15

            final_score = min(1.0, max(0.0, base_score + boost))
            item_copy = dict(item)
            item_copy["rerank_score"] = round(final_score, 4)
            scored.append((final_score, item_copy))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[: self.top_k]]
