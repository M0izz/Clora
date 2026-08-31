"""
Evidence Pack generator for INDUSAI-X.
Converts retrieved & reranked chunks into the structured Evidence Pack consumed by LLMs and Verifiers.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    text: str
    source: str
    page: int
    chunk_id: str
    score: float
    equipment_id: str = ""
    section: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "chunk_id": self.chunk_id,
            "score": round(self.score, 4)
        }

class EvidencePack(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence": [item.to_dict() for item in self.evidence]
        }

    def format_as_prompt_context(self) -> str:
        """Formats the evidence pack into an unambiguous prompt context block."""
        if not self.evidence:
            return "NO EVIDENCE AVAILABLE IN RETRIEVAL REPOSITORY."
        
        blocks = []
        for idx, item in enumerate(self.evidence, 1):
            blocks.append(
                f"[Evidence {idx}] (ID: {item.chunk_id})\n"
                f"Source Document: {item.source} (Page {item.page})\n"
                f"Section: {item.section or 'N/A'}\n"
                f"Relevance Score: {item.score}\n"
                f"Content: \"\"\"\n{item.text}\n\"\"\""
            )
        return "\n\n".join(blocks)

class EvidencePackBuilder:
    """Builds standardized EvidencePack from raw retrieved chunk dictionaries."""

    @staticmethod
    def build(chunks: List[Dict[str, Any]]) -> EvidencePack:
        items: List[EvidenceItem] = []
        for c in chunks:
            text = c.get("text", "")
            meta = c.get("metadata")
            score = float(c.get("rerank_score", c.get("score", 0.85)))
            
            source = "Unknown"
            page = 1
            chunk_id = c.get("chunk_id", "unknown_chunk")
            equipment_id = ""
            section = ""

            if hasattr(meta, "document_name"):
                source = meta.document_name
                page = int(meta.page)
                chunk_id = meta.chunk_id or chunk_id
                equipment_id = meta.equipment_id or ""
                section = meta.section or ""
            elif isinstance(meta, dict):
                source = meta.get("document_name", "Unknown")
                page = int(meta.get("page", 1))
                chunk_id = meta.get("chunk_id", chunk_id)
                equipment_id = meta.get("equipment_id", "")
                section = meta.get("section", "")

            items.append(EvidenceItem(
                text=text,
                source=source,
                page=page,
                chunk_id=chunk_id,
                score=score,
                equipment_id=equipment_id,
                section=section
            ))

        return EvidencePack(evidence=items)
