"""
INDUSAI-X Chunk and Document Metadata Schema
Strictly adheres to SIH26117 MRPL specifications.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

class ChunkMetadata(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chunk_{uuid.uuid4().hex[:8]}")
    document_id: str
    document_name: str
    page: int = 1
    section: str = "General"
    equipment_id: Optional[str] = None
    document_type: str = "general_document"  # e.g., maintenance_report, sop, inspection_log, p_and_id, incident_report
    department: str = "general"               # e.g., maintenance, operations, safety, engineering
    classification: str = "internal"          # public, internal, confidential, restricted
    allowed_roles: List[str] = Field(default_factory=lambda: ["maintenance_engineer", "supervisor", "operator"])
    timestamp: str = "2026-08-31"

    def to_chroma_metadata(self) -> Dict[str, Any]:
        """Convert metadata to flat dictionary format required by ChromaDB."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "page": int(self.page),
            "section": str(self.section),
            "equipment_id": str(self.equipment_id or ""),
            "document_type": str(self.document_type),
            "department": str(self.department),
            "classification": str(self.classification),
            # ChromaDB supports string lists or comma-separated strings for filtering
            "allowed_roles": ",".join(self.allowed_roles),
            "timestamp": str(self.timestamp)
        }

    @classmethod
    def from_chroma_metadata(cls, meta: Dict[str, Any]) -> "ChunkMetadata":
        roles = meta.get("allowed_roles", "")
        if isinstance(roles, str):
            allowed_roles = [r.strip() for r in roles.split(",") if r.strip()]
        elif isinstance(roles, list):
            allowed_roles = roles
        else:
            allowed_roles = []
            
        return cls(
            chunk_id=meta.get("chunk_id", ""),
            document_id=meta.get("document_id", ""),
            document_name=meta.get("document_name", ""),
            page=int(meta.get("page", 1)),
            section=meta.get("section", "General"),
            equipment_id=meta.get("equipment_id") if meta.get("equipment_id") else None,
            document_type=meta.get("document_type", "general_document"),
            department=meta.get("department", "general"),
            classification=meta.get("classification", "internal"),
            allowed_roles=allowed_roles,
            timestamp=meta.get("timestamp", "2026-08-31")
        )

class Chunk(BaseModel):
    text: str
    metadata: ChunkMetadata

class ParsedSection(BaseModel):
    title: str
    page: int
    content: str
    tables: List[str] = Field(default_factory=list)
    equipment_ids: List[str] = Field(default_factory=list)

class IngestedDocument(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    department: str
    classification: str
    allowed_roles: List[str]
    timestamp: str
    sections: List[ParsedSection] = Field(default_factory=list)
