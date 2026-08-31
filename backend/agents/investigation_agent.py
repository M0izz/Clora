"""
Investigation Agent and Engineering Agent for INDUSAI-X.
"""

from typing import Any, Dict, List

from backend.rag.evidence import Evidence


class InvestigationAgent:
    """Cross-correlates multi-source evidence across maintenance reports and inspection logs."""

    def investigate(self, evidence: List[Evidence]) -> Dict[str, Any]:
        sources = set(f"{e.source_document} (p.{e.page_number})" for e in evidence)
        observations = []
        for e in evidence:
            for line in e.content.splitlines():
                line_str = line.strip()
                if any(
                    k in line_str.lower()
                    for k in [
                        "temperature",
                        "lubricat",
                        "contaminat",
                        "vibrat",
                        "pressure",
                        "leak",
                        "failure",
                        "exceeded",
                    ]
                ):
                    observations.append(f"{line_str} [{e.source_document}, p.{e.page_number}]")

        return {"sources_analyzed": list(sources), "observations": observations[:5]}


class EngineeringAgent:
    """Analyzes equipment parameters against operating limits."""

    def check_limits(self, equipment_id: str, parameter: str, value: float) -> Dict[str, Any]:
        # Domain baseline thresholds
        thresholds = {"bearing_temp_c": 90.0, "vibration_rms_mms": 4.5, "h2s_ppm": 10.0}
        limit = thresholds.get(parameter, 100.0)
        is_exceeded = value > limit
        return {
            "equipment_id": equipment_id,
            "parameter": parameter,
            "observed_value": value,
            "limit": limit,
            "status": "ALARM_EXCEEDED" if is_exceeded else "NORMAL",
        }
