"""
Unit tests for the Hallucination Firewall and Causal Leap Downgrader.
Tests the exact worked example required by SIH26117 Section 6.
"""

from indusai.agents.nodes.guardrail import HallucinationFirewallNode
from indusai.agents.state import AgentState
from indusai.retrieval.evidence_pack import EvidenceItem, EvidencePack
from indusai.verification.schemas import Claim, VerificationStatus
from indusai.verification.verifier import EvidenceVerifier


def test_pump_p101_causal_leap_downgrade():
    """
    WORKED EXAMPLE TEST:
    - Query: "Why did Pump P-101 fail?"
    - Evidence 1 (Maintenance Report, p.14): bearing temperature exceeded normal range
    - Evidence 2 (Inspection Report, p.3): lubrication contamination observed
    - Claim asserts direct causation ("contamination caused overheating which caused failure")
    - Verifier must downgrade to PARTIALLY_SUPPORTED and generate hedged output.
    """
    ev1 = EvidenceItem(
        text="During the scheduled inspection of Pump P-101, bearing temperature exceeded normal range reaching 95°C.",
        source="Pump_P-101_Maintenance.pdf",
        page=14,
        chunk_id="chunk_maint_14",
        score=0.92,
        equipment_id="P-101",
        section="Root Cause Analysis",
    )
    ev2 = EvidenceItem(
        text="Field inspection of Pump P-101 lube reservoir: lubrication contamination observed with particulate presence.",
        source="Pump_P-101_Inspection.pdf",
        page=3,
        chunk_id="chunk_insp_03",
        score=0.89,
        equipment_id="P-101",
        section="Visual Inspection",
    )
    pack = EvidencePack(evidence=[ev1, ev2])

    verifier = EvidenceVerifier()

    # 1. Fact 1 alone (Supported)
    claim_fact1 = Claim(text="Bearing temperature on Pump P-101 exceeded normal operating range.")
    res_fact1 = verifier.verify_claim(claim_fact1, pack)
    assert res_fact1.status == VerificationStatus.SUPPORTED.value

    # 2. Fact 2 alone (Supported)
    claim_fact2 = Claim(text="Lubrication contamination was observed in the reservoir.")
    res_fact2 = verifier.verify_claim(claim_fact2, pack)
    assert res_fact2.status == VerificationStatus.SUPPORTED.value

    # 3. Unverified Causal Chain Assertion ("Lubrication contamination caused overheating which led to pump failure")
    causal_claim = Claim(
        text="Lubrication contamination caused bearing overheating which led to Pump P-101 failure."
    )
    res_causal = verifier.verify_claim(causal_claim, pack)

    # Must be downgraded to PARTIALLY_SUPPORTED
    assert res_causal.status == VerificationStatus.PARTIALLY_SUPPORTED.value
    assert res_causal.has_causal_leap is True
    assert "Available records indicate" in res_causal.hedged_text
    assert (
        "however, the documents do not conclusively establish direct causation"
        in res_causal.hedged_text
    )


def test_guardrail_output_formatting_and_hedging():
    ev1 = EvidenceItem(
        text="Bearing temperature exceeded normal range.",
        source="Report.pdf",
        page=14,
        chunk_id="chunk_8f29",
        score=0.91,
    )
    ev2 = EvidenceItem(
        text="Lubrication contamination observed.",
        source="Inspection.pdf",
        page=3,
        chunk_id="chunk_4a12",
        score=0.88,
    )

    verifier = EvidenceVerifier()
    pack = EvidencePack(evidence=[ev1, ev2])

    causal_claim = Claim(
        text="Lubrication contamination caused bearing overheating which led to failure."
    )
    verified_causal = verifier.verify_claim(causal_claim, pack)

    state: AgentState = {
        "user_query": "Why did Pump P-101 fail?",
        "user_id": "eng_01",
        "user_role": "maintenance_engineer",
        "intent": "root_cause_investigation",
        "plan": [],
        "retrieved_docs": [],
        "evidence": [ev1.to_dict(), ev2.to_dict()],
        "agent_outputs": {},
        "draft_answer": "Draft containing unhedged causation.",
        "claims": [verified_causal.model_dump()],
        "verification_results": [],
        "confidence": 0.70,
        "guardrail_status": "PENDING",
        "audit_log": [],
    }

    guardrail_node = HallucinationFirewallNode()
    result = guardrail_node.run(state)

    final_text = result["draft_answer"]
    assert "ANSWER" in final_text
    assert "Verified Findings" in final_text
    assert "Analysis" in final_text
    assert "Uncertainty" in final_text
    assert "Confidence: MEDIUM" in final_text
    assert "Evidence" in final_text
    assert "[1] Report.pdf — Page 14" in final_text
    assert "[2] Inspection.pdf — Page 3" in final_text
    assert "Available records indicate" in final_text
    assert "conclusively establish direct causation" in final_text
