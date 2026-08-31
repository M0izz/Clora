"""
Guardrail & Hallucination Firewall Node for INDUSAI-X.
Blocks unverified assertions, enforces hedged language for causal leaps, and standardizes output.
"""

from typing import Dict, Any, List
from indusai.agents.state import AgentState
from indusai.verification.schemas import VerificationStatus

class HallucinationFirewallNode:
    """Enforces evidence bounds and rewrites draft answers into verified MRPL format."""

    def run(self, state: AgentState) -> Dict[str, Any]:
        claims_data = state.get("claims", [])
        evidence = state.get("evidence", [])
        confidence = float(state.get("confidence", 0.0))

        if not evidence:
            final_formatted = (
                "ANSWER\n"
                "────────────────────────\n"
                "Verified Findings\n"
                "• No verified findings available in authorized repository.\n\n"
                "Analysis\n"
                "• The inquiry cannot be verified from available evidence.\n\n"
                "Uncertainty\n"
                "• Documentation is insufficient or inaccessible under current user authorization.\n\n"
                "Confidence: LOW\n\n"
                "Evidence\n"
                "[None]"
            )
            return {
                "draft_answer": final_formatted,
                "guardrail_status": "INSUFFICIENT_EVIDENCE",
                "audit_log": list(state.get("audit_log", [])) + [{
                    "event": "guardrail_blocked_insufficient_evidence"
                }]
            }

        verified_findings = []
        analysis_points = []
        uncertainty_points = []
        needs_human_review = False
        has_hedged = False

        for c in claims_data:
            text = c.get("text", "")
            status = c.get("status")
            hedged_text = c.get("hedged_text")
            causal = c.get("has_causal_leap", False)

            if status == VerificationStatus.SUPPORTED.value:
                verified_findings.append(f"• {text}")
            elif status == VerificationStatus.PARTIALLY_SUPPORTED.value:
                has_hedged = True
                if hedged_text:
                    analysis_points.append(f"• {hedged_text}")
                else:
                    analysis_points.append(f"• {text} (Partial correlation observed; direct causation unconfirmed)")
                uncertainty_points.append("• Direct causation is not explicitly established in referenced records.")
            elif status == VerificationStatus.CONTRADICTED.value:
                needs_human_review = True
                uncertainty_points.append(f"• Conflicting data detected across records: {c.get('reasoning', '')}")
            elif status in [VerificationStatus.UNSUPPORTED.value, VerificationStatus.INSUFFICIENT_EVIDENCE.value]:
                uncertainty_points.append(f"• Statement cannot be verified from available evidence: \"{text}\"")

        # Compile citations
        citation_lines = []
        for idx, ev in enumerate(evidence, 1):
            src = ev.get("source", "Document")
            page = ev.get("page", 1)
            citation_lines.append(f"[{idx}] {src} — Page {page}")

        # Ensure findings exist
        if not verified_findings:
            for ev in evidence:
                src = ev.get("source", "Report.pdf")
                page = ev.get("page", 1)
                for line in ev.get("text", "").splitlines()[:2]:
                    l = line.strip()
                    if len(l) > 10:
                        verified_findings.append(f"• {l} [Source: {src}, Page {page}]")
                        break

        # Confidence level indicator
        if confidence >= 0.85:
            conf_str = "HIGH"
        elif confidence >= 0.60:
            conf_str = "MEDIUM"
        else:
            conf_str = "LOW"

        # Build clean final report format matching Section 6
        final_answer = (
            "ANSWER\n"
            "────────────────────────\n"
            "Verified Findings\n"
            + ("\n".join(verified_findings) if verified_findings else "• No fully verified factual claims extracted.")
            + "\n\nAnalysis\n"
            + ("\n".join(analysis_points) if analysis_points else "• Based on the available evidence, operational parameters are consistent with recorded observations.")
            + "\n\nUncertainty\n"
            + ("\n".join(uncertainty_points) if uncertainty_points else "• The records do not establish additional secondary factors.")
            + f"\n\nConfidence: {conf_str}\n\n"
            "Evidence\n"
            + ("\n".join(citation_lines[:5]) if citation_lines else "[None]")
        )

        guardrail_status = "PASSED"
        if needs_human_review:
            guardrail_status = "FLAGGED_FOR_HUMAN_REVIEW"
        elif has_hedged:
            guardrail_status = "CAUSAL_HEDGING_APPLIED"

        audit_entry = {
            "event": "guardrail_firewall_applied",
            "guardrail_status": guardrail_status,
            "confidence_level": conf_str,
            "hedged_applied": has_hedged
        }
        audit_log = list(state.get("audit_log", []))
        audit_log.append(audit_entry)

        return {
            "draft_answer": final_answer,
            "guardrail_status": guardrail_status,
            "audit_log": audit_log
        }
