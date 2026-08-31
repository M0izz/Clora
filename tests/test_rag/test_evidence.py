"""
Unit tests for Evidence data models.
"""

from backend.rag.evidence import Evidence, EvidencePack


def test_evidence_has_required_fields():
    evidence = Evidence(
        evidence_id="ev_001",
        content="Bearing temperature exceeded normal range.",
        source_document="maintenance_report.pdf",
        page_number=14,
        chunk_id="chunk_001",
        relevance_score=0.95,
    )

    assert evidence.evidence_id == "ev_001"
    assert evidence.page_number == 14
    assert evidence.source_document == "maintenance_report.pdf"

    pack = EvidencePack(evidence=[evidence])
    d = pack.to_dict()
    assert len(d["evidence"]) == 1
    assert d["evidence"][0]["chunk_id"] == "chunk_001"
