"""
Investigation Agent Node for INDUSAI-X.
Cross-correlates multi-source evidence (e.g. Maintenance Reports, Inspection Logs, Operating Logs).
"""

from typing import Dict, Any, List
from indusai.agents.state import AgentState

class InvestigationAgent:
    """Aggregates findings from across multiple document types and equipment logs."""

    def run(self, state: AgentState) -> Dict[str, Any]:
        evidence = state.get("evidence", [])
        
        sources = set()
        findings_summary = []

        for ev in evidence:
            src = ev.get("source", "Unknown")
            page = ev.get("page", 1)
            text = ev.get("text", "")
            sources.add(f"{src} (Page {page})")
            
            # Extract key observations
            for line in text.splitlines():
                line_s = line.strip()
                if any(w in line_s.lower() for w in ["temperature", "lubricat", "contaminat", "vibrat", "pressure", "leak", "failure", "observed", "exceeded"]):
                    findings_summary.append(f"{line_s} [{src}, p.{page}]")

        agent_outputs = dict(state.get("agent_outputs", {}))
        agent_outputs["investigation_agent"] = {
            "sources_analyzed": list(sources),
            "multi_source_count": len(sources),
            "key_observations": findings_summary[:5]
        }

        audit_entry = {
            "event": "investigation_analysis_completed",
            "sources_cross_correlated": list(sources),
            "observations_count": len(findings_summary)
        }
        audit_log = list(state.get("audit_log", []))
        audit_log.append(audit_entry)

        return {
            "agent_outputs": agent_outputs,
            "audit_log": audit_log
        }
