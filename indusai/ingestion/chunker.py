"""
INDUSAI-X Intelligent Chunker
Section-aware, table-aware, and metadata-preserving chunking for sovereign industrial RAG.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from indusai.ingestion.schema import Chunk, ChunkMetadata, IngestedDocument, ParsedSection

EQUIPMENT_ID_REGEX = re.compile(r'\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b', re.IGNORECASE)

class IntelligentChunker:
    """Creates context-preserving, section-bounded chunks with rich industrial metadata."""

    def __init__(self, target_chunk_size: int = 600, min_chunk_size: int = 80, chunk_overlap: int = 100):
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: IngestedDocument) -> List[Chunk]:
        chunks: List[Chunk] = []

        for sec in document.sections:
            sec_chunks = self._chunk_section(sec, document)
            chunks.extend(sec_chunks)

        return chunks

    def _chunk_section(self, section: ParsedSection, document: IngestedDocument) -> List[Chunk]:
        chunks: List[Chunk] = []
        
        # 1. First process tables as isolated, table-aware chunks
        if section.tables:
            for table_str in section.tables:
                eq_ids = list(set(EQUIPMENT_ID_REGEX.findall(table_str)))
                primary_eq = eq_ids[0] if eq_ids else (section.equipment_ids[0] if section.equipment_ids else None)
                
                meta = ChunkMetadata(
                    chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
                    document_id=document.document_id,
                    document_name=document.document_name,
                    page=section.page,
                    section=f"{section.title} [Table]",
                    equipment_id=primary_eq,
                    document_type=document.document_type,
                    department=document.department,
                    classification=document.classification,
                    allowed_roles=document.allowed_roles,
                    timestamp=document.timestamp
                )
                
                table_chunk_text = f"[{section.title} Table]\n{table_str}"
                chunks.append(Chunk(text=table_chunk_text, metadata=meta))

        # 2. Process text content preserving sentences & paragraphs
        content = section.content.strip()
        if not content:
            return chunks

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [content]

        current_text = ""
        for p in paragraphs:
            if len(current_text) + len(p) + 1 <= self.target_chunk_size:
                current_text = f"{current_text}\n\n{p}".strip() if current_text else p
            else:
                if current_text:
                    chunks.append(self._create_chunk(current_text, section, document))
                
                # If paragraph itself is larger than target chunk size, split by sentences
                if len(p) > self.target_chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    sub_text = ""
                    for s in sentences:
                        if len(sub_text) + len(s) + 1 <= self.target_chunk_size:
                            sub_text = f"{sub_text} {s}".strip() if sub_text else s
                        else:
                            if sub_text:
                                chunks.append(self._create_chunk(sub_text, section, document))
                            sub_text = s
                    if sub_text:
                        current_text = sub_text
                else:
                    current_text = p

        if current_text:
            chunks.append(self._create_chunk(current_text, section, document))

        return chunks

    def _create_chunk(self, text: str, section: ParsedSection, document: IngestedDocument) -> Chunk:
        eq_ids = list(set(EQUIPMENT_ID_REGEX.findall(text)))
        primary_eq = eq_ids[0] if eq_ids else (section.equipment_ids[0] if section.equipment_ids else None)

        meta = ChunkMetadata(
            chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
            document_id=document.document_id,
            document_name=document.document_name,
            page=section.page,
            section=section.title,
            equipment_id=primary_eq,
            document_type=document.document_type,
            department=document.department,
            classification=document.classification,
            allowed_roles=document.allowed_roles,
            timestamp=document.timestamp
        )
        return Chunk(text=text, metadata=meta)
