"""
Unit tests for Pump P-101 failure scenario and causal leap downgrading.
"""

from backend.rag.evidence import Evidence, EvidencePack
from backend.verification.claim_extractor import Claim
from backend.verification.verifier import EvidenceVerifier


def test_pump_p101_causal_leap_downgrade():
    ev1 = Evidence(
        evidence_id="ev_001",
        content="Pump P-101 bearing temperature exceeded normal range.",
        source_document="Maintenance_Report.pdf",
        page_number=14,
        chunk_id="c1",
    )
    ev2 = Evidence(
        evidence_id="ev_002",
        content="Lubrication contamination observed in reservoir.",
        source_document="Inspection_Log.pdf",
        page_number=3,
        chunk_id="c2",
    )
    pack = EvidencePack(evidence=[ev1, ev2])
    verifier = EvidenceVerifier()

    # Supported factual claim
    fact_claim = Claim(text="Bearing temperature on Pump P-101 exceeded normal operating range.")
    res_fact = verifier.verify_claim(fact_claim, pack)
    assert res_fact.status == "SUPPORTED"

    # Unverified causal link
    causal_claim = Claim(
        text="Lubrication contamination caused bearing overheating which led to pump failure."
    )
    res_causal = verifier.verify_claim(causal_claim, pack)
    assert res_causal.status == "PARTIALLY_SUPPORTED"
    assert "conclusively establish direct causation" in res_causal.hedged_text
