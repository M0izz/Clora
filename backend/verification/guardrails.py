"""
Guardrails and Response Formatter for INDUSAI-X.
"""

from typing import Any, Dict, List

from backend.rag.evidence import Evidence
from backend.verification.claim_extractor import Claim


class HallucinationGuardrail:
    """Enforces evidence bounds and standard MRPL answer format."""

    def format_final_answer(
        self, claims: List[Claim], evidence: List[Evidence], confidence: float
    ) -> Dict[str, Any]:
        if not evidence:
            answer = (
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
                "answer": answer,
                "guardrail_status": "INSUFFICIENT_EVIDENCE",
                "confidence_level": "LOW",
            }

        verified_findings = []
        analysis_points = []
        uncertainty_points = []
        has_hedged = False
        has_contradiction = False

        for c in claims:
            if c.status == "SUPPORTED":
                verified_findings.append(f"• {c.text}")
            elif c.status == "PARTIALLY_SUPPORTED":
                has_hedged = True
                if c.hedged_text:
                    analysis_points.append(f"• {c.hedged_text}")
                else:
                    analysis_points.append(
                        f"• {c.text} (Partial correlation observed; direct causation unconfirmed)"
                    )
                uncertainty_points.append(
                    "• Direct causation is not explicitly established in referenced records."
                )
            elif c.status == "CONTRADICTED":
                has_contradiction = True
                uncertainty_points.append(
                    f"• Conflicting data detected across records: {c.reasoning}"
                )
            elif c.status in ["UNSUPPORTED", "INSUFFICIENT_EVIDENCE"]:
                uncertainty_points.append(
                    f'• Statement cannot be verified from available evidence: "{c.text}"'
                )

        if not verified_findings:
            for ev in evidence[:2]:
                for line in ev.content.splitlines()[:2]:
                    line_str = line.strip()
                    if len(line_str) > 10:
                        verified_findings.append(
                            f"• {line_str} [Source: {ev.source_document}, Page {ev.page_number}]"
                        )
                        break

        citations = [
            f"[{idx}] {ev.source_document} — Page {ev.page_number}"
            for idx, ev in enumerate(evidence, 1)
        ]

        conf_str = "HIGH" if confidence >= 0.85 else "MEDIUM" if confidence >= 0.60 else "LOW"

        answer = (
            "ANSWER\n"
            "────────────────────────\n"
            "Verified Findings\n"
            + (
                "\n".join(verified_findings)
                if verified_findings
                else "• No fully verified factual claims extracted."
            )
            + "\n\nAnalysis\n"
            + (
                "\n".join(analysis_points)
                if analysis_points
                else "• Based on the available evidence, operational parameters are consistent with recorded observations."
            )
            + "\n\nUncertainty\n"
            + (
                "\n".join(uncertainty_points)
                if uncertainty_points
                else "• The records do not establish additional secondary factors."
            )
            + f"\n\nConfidence: {conf_str}\n\n"
            "Evidence\n" + ("\n".join(citations[:5]) if citations else "[None]")
        )

        status = "PASSED"
        if has_contradiction:
            status = "FLAGGED_FOR_HUMAN_REVIEW"
        elif has_hedged:
            status = "CAUSAL_HEDGING_APPLIED"

        return {"answer": answer, "guardrail_status": status, "confidence_level": conf_str}
