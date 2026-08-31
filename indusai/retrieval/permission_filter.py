"""
Permission filter module for INDUSAI-X.
Ensures zero unauthorized data leaks to the LLM or agent nodes.
"""

from typing import List, Dict, Any
from indusai.ingestion.schema import ChunkMetadata

class PermissionFilter:
    """Enforces strict RBAC at retrieval time before evidence reaches LLM prompts."""

    @staticmethod
    def is_authorized(user_role: str, allowed_roles: List[str]) -> bool:
        if not user_role or not allowed_roles:
            return False
        if "plant_manager" in user_role.lower() or "admin" in user_role.lower():
            return True
        return user_role.lower().strip() in [r.lower().strip() for r in allowed_roles]

    @classmethod
    def filter_retrieved_docs(cls, docs: List[Dict[str, Any]], user_role: str) -> List[Dict[str, Any]]:
        authorized = []
        for doc in docs:
            meta = doc.get("metadata")
            allowed = []
            if isinstance(meta, ChunkMetadata):
                allowed = meta.allowed_roles
            elif isinstance(meta, dict):
                r_val = meta.get("allowed_roles", "")
                allowed = [r.strip() for r in r_val.split(",") if r.strip()] if isinstance(r_val, str) else r_val

            if cls.is_authorized(user_role, allowed):
                authorized.append(doc)
        return authorized
