"""
Unit tests for Ingestion and Intelligent Chunking.
"""

import os
import tempfile

from indusai.ingestion.chunker import IntelligentChunker
from indusai.ingestion.document_parser import DocumentParser
from indusai.ingestion.schema import ChunkMetadata


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
    assert chroma_dict["page"] == 14

    restored = ChunkMetadata.from_chroma_metadata(chroma_dict)
    assert restored.chunk_id == meta.chunk_id
    assert restored.equipment_id == meta.equipment_id
    assert restored.allowed_roles == ["maintenance_engineer", "supervisor"]


def test_document_parser_and_chunker():
    sample_text = """# 1.0 General Description
Pump P-101 is a centrifugal booster pump operating in Unit 2.

# 2.0 Root Cause Analysis
During inspection on 2026-08-20, bearing temperature exceeded normal range significantly.
Vibration sensors indicated elevated harmonics.

| Parameter | Baseline | Observed | Unit |
| Bearing Temp | 65 | 92 | C |
| Vibration | 1.2 | 4.8 | mm/s |

# 3.0 Corrective Actions
Recommended immediate overhaul and lube oil sample analysis.
"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(sample_text)
        temp_path = f.name

    try:
        parser = DocumentParser()
        doc = parser.parse_file(
            file_path=temp_path,
            document_id="p101_report",
            document_type="maintenance_report",
            department="maintenance",
            allowed_roles=["maintenance_engineer", "supervisor"],
        )

        assert doc.document_id == "p101_report"
        assert len(doc.sections) >= 3

        chunker = IntelligentChunker(target_chunk_size=300)
        chunks = chunker.chunk_document(doc)

        assert len(chunks) >= 3
        # Check metadata on chunks
        eq_chunks = [c for c in chunks if c.metadata.equipment_id == "P-101"]
        assert len(eq_chunks) >= 1
        assert all(c.metadata.document_type == "maintenance_report" for c in chunks)
        assert all("maintenance_engineer" in c.metadata.allowed_roles for c in chunks)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
