"""
Evidence data models for INDUSAI-X.
Standard evidence representation exchanged across all agents.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    evidence_id: str
    content: str
    source_document: str
    page_number: Optional[int] = 1
    chunk_id: str
    relevance_score: Optional[float] = 1.0
    equipment_id: Optional[str] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "content": self.content,
            "text": self.content,  # compatibility alias
            "source_document": self.source_document,
            "source": self.source_document,  # compatibility alias
            "page_number": self.page_number,
            "page": self.page_number,  # compatibility alias
            "chunk_id": self.chunk_id,
            "relevance_score": round(self.relevance_score or 1.0, 4),
            "score": round(self.relevance_score or 1.0, 4),
            "equipment_id": self.equipment_id or "",
            "section": self.section or "",
            "metadata": self.metadata,
        }


class EvidencePack(BaseModel):
    evidence: List[Evidence] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"evidence": [item.to_dict() for item in self.evidence]}
