"""
Unit tests for intelligent chunking and ChunkMetadata schema.
"""

from backend.rag.chunking import ChunkMetadata, IntelligentChunker
from backend.rag.ingestion import IngestedDocument, ParsedSection


def test_chunk_metadata_schema():
    meta = ChunkMetadata(
        chunk_id="chunk_8f29",
        document_id="maintenance_report_102",
        document_name="Pump_P-101_Maintenance.pdf",
        page=14,
        section="Root Cause Analysis",
        equipment_id="P-101",
        document_type="maintenance_report",
        department="maintenance",
        classification="confidential",
        allowed_roles=["maintenance_engineer", "supervisor"],
        timestamp="2026-08-20",
    )

    chroma_dict = meta.to_chroma_metadata()
    assert chroma_dict["chunk_id"] == "chunk_8f29"
    assert chroma_dict["equipment_id"] == "P-101"
    assert "maintenance_engineer" in chroma_dict["allowed_roles"]

    restored = ChunkMetadata.from_chroma_metadata(chroma_dict)
    assert restored.chunk_id == meta.chunk_id
    assert restored.equipment_id == meta.equipment_id


def test_intelligent_chunker_section_and_tables():
    doc = IngestedDocument(
        document_id="doc_p101",
        document_name="Pump_P101.pdf",
        sections=[
            ParsedSection(
                title="Root Cause Analysis",
                page=14,
                content="Bearing temperature exceeded normal limits.\nVibration was elevated.",
                tables=["| Metric | Value |\n| Temp | 95C |"],
                equipment_ids=["P-101"],
            )
        ],
    )
    chunker = IntelligentChunker(target_chunk_size=300)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    assert any("[Table]" in c.metadata.section for c in chunks)
