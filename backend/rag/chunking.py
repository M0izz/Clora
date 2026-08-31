"""
Intelligent Section-Aware and Table-Aware Chunking.
Preserves exact SIH26117 chunk metadata schema.
"""

import re
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.rag.ingestion import IngestedDocument

EQUIPMENT_ID_REGEX = re.compile(
    r"\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b", re.IGNORECASE
)


class ChunkMetadata(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chunk_{uuid.uuid4().hex[:8]}")
    document_id: str
    document_name: str
    page: int = 1
    section: str = "General"
    equipment_id: Optional[str] = None
    document_type: str = "maintenance_report"
    department: str = "maintenance"
    classification: str = "internal"
    allowed_roles: List[str] = Field(default_factory=lambda: ["maintenance_engineer", "supervisor"])
    timestamp: str = "2026-08-31"

    def to_chroma_metadata(self) -> Dict[str, Any]:
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
            "allowed_roles": ",".join(self.allowed_roles),
            "timestamp": str(self.timestamp),
        }

    @classmethod
    def from_chroma_metadata(cls, meta: Dict[str, Any]) -> "ChunkMetadata":
        roles = meta.get("allowed_roles", "")
        allowed = (
            [r.strip() for r in roles.split(",") if r.strip()]
            if isinstance(roles, str)
            else (roles or [])
        )
        return cls(
            chunk_id=meta.get("chunk_id", ""),
            document_id=meta.get("document_id", ""),
            document_name=meta.get("document_name", ""),
            page=int(meta.get("page", 1)),
            section=meta.get("section", "General"),
            equipment_id=meta.get("equipment_id") if meta.get("equipment_id") else None,
            document_type=meta.get("document_type", "maintenance_report"),
            department=meta.get("department", "maintenance"),
            classification=meta.get("classification", "internal"),
            allowed_roles=allowed,
            timestamp=meta.get("timestamp", "2026-08-31"),
        )


class Chunk(BaseModel):
    text: str
    metadata: ChunkMetadata


class IntelligentChunker:
    """Creates section-aware and table-preserving chunks."""

    def __init__(self, target_chunk_size: int = 500):
        self.target_chunk_size = target_chunk_size

    def chunk_document(self, document: IngestedDocument) -> List[Chunk]:
        chunks: List[Chunk] = []
        for sec in document.sections:
            # 1. Tables as discrete chunks
            for table_str in sec.tables:
                eqs = list(set(EQUIPMENT_ID_REGEX.findall(table_str)))
                meta = ChunkMetadata(
                    document_id=document.document_id,
                    document_name=document.document_name,
                    page=sec.page,
                    section=f"{sec.title} [Table]",
                    equipment_id=eqs[0]
                    if eqs
                    else (sec.equipment_ids[0] if sec.equipment_ids else None),
                    document_type=document.document_type,
                    department=document.department,
                    classification=document.classification,
                    allowed_roles=document.allowed_roles,
                    timestamp=document.timestamp,
                )
                chunks.append(Chunk(text=f"[{sec.title} Table]\n{table_str}", metadata=meta))

            # 2. Text content
            content = sec.content.strip()
            if not content:
                continue

            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            for p in paragraphs:
                eqs = list(set(EQUIPMENT_ID_REGEX.findall(p)))
                meta = ChunkMetadata(
                    document_id=document.document_id,
                    document_name=document.document_name,
                    page=sec.page,
                    section=sec.title,
                    equipment_id=eqs[0]
                    if eqs
                    else (sec.equipment_ids[0] if sec.equipment_ids else None),
                    document_type=document.document_type,
                    department=document.department,
                    classification=document.classification,
                    allowed_roles=document.allowed_roles,
                    timestamp=document.timestamp,
                )
                chunks.append(Chunk(text=p, metadata=meta))

        return chunks
