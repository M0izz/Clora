"""
Human Review Routing Stub Node for INDUSAI-X.
Flags ambiguous, contradicted, or safety-critical outputs for human expert review.
"""

from typing import Dict, Any
from indusai.agents.state import AgentState

def human_review_node(state: AgentState) -> Dict[str, Any]:
    guardrail_status = state.get("guardrail_status", "PASSED")
    audit_log = list(state.get("audit_log", []))
    
    if "FLAGGED" in guardrail_status:
        audit_log.append({
            "event": "human_review_escalation_triggered",
            "reason": "Contradiction or severe uncertainty in evidence pack.",
            "status": "Awaiting SME / Reliability Engineer Sign-off"
        })
    
    return {
        "audit_log": audit_log
    }
