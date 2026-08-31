"""
Evidence Verifier Node for INDUSAI-X.
Runs atomic claim extraction and verification against retrieved evidence.
"""

from typing import Dict, Any, List
from indusai.agents.state import AgentState
from indusai.verification.claim_extractor import ClaimExtractor
from indusai.verification.verifier import EvidenceVerifier
from indusai.retrieval.evidence_pack import EvidenceItem, EvidencePack

class EvidenceVerifierNode:
    """Orchestrates claim extraction and evidence verification."""

    def __init__(self):
        self.extractor = ClaimExtractor()
        self.verifier = EvidenceVerifier()

    def run(self, state: AgentState) -> Dict[str, Any]:
        draft = state.get("draft_answer", "")
        evidence_dicts = state.get("evidence", [])

        # Convert evidence dicts back to EvidencePack
        evidence_items = [
            EvidenceItem(
                text=ev.get("text", ""),
                source=ev.get("source", "Unknown"),
                page=int(ev.get("page", 1)),
                chunk_id=ev.get("chunk_id", "c"),
                score=float(ev.get("score", 0.9)),
                equipment_id=ev.get("equipment_id", ""),
                section=ev.get("section", "")
            )
            for ev in evidence_dicts
        ]
        pack = EvidencePack(evidence=evidence_items)

        # Extract and verify claims
        claims = self.extractor.extract_claims(draft)
        result = self.verifier.verify_all(claims, pack)

        audit_entry = {
            "event": "evidence_verification_completed",
            "total_claims": len(claims),
            "verified_count": result.verified_count,
            "hedged_count": result.hedged_count,
            "unsupported_count": result.unsupported_count,
            "blocked_count": result.blocked_count,
            "overall_confidence": result.overall_confidence
        }
        audit_log = list(state.get("audit_log", []))
        audit_log.append(audit_entry)

        return {
            "claims": [c.model_dump() for c in result.claims],
            "verification_results": [result.model_dump()],
            "confidence": result.overall_confidence,
            "audit_log": audit_log
        }
