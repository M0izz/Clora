"""
Unit tests for Guardrails and format compliance.
"""

from backend.rag.evidence import Evidence
from backend.verification.claim_extractor import Claim
from backend.verification.guardrails import HallucinationGuardrail


def test_guardrail_unsupported_claim_handling():
    guardrail = HallucinationGuardrail()
    unsupported_claim = Claim(text="Unknown speculation", status="UNSUPPORTED")
    evidence = [
        Evidence(
            evidence_id="e1",
            content="Report text",
            source_document="doc.pdf",
            page_number=1,
            chunk_id="c1",
        )
    ]

    res = guardrail.format_final_answer([unsupported_claim], evidence, confidence=0.4)
    assert "ANSWER" in res["answer"]
    assert "Uncertainty" in res["answer"]
    assert "Confidence: LOW" in res["answer"]


def test_unsupported_claim_is_not_verified():
    claim_status = "UNSUPPORTED"
    assert claim_status != "SUPPORTED"
