"""
Final Response Node for INDUSAI-X.
Prepares the complete response bundle for FastAPI consumption.
"""

from typing import Dict, Any
from indusai.agents.state import AgentState

def final_response_node(state: AgentState) -> Dict[str, Any]:
    draft_answer = state.get("draft_answer", "")
    evidence = state.get("evidence", [])
    confidence = float(state.get("confidence", 0.0))
    guardrail_status = state.get("guardrail_status", "PASSED")
    audit_log = list(state.get("audit_log", []))

    citations = [
        {
            "source": ev.get("source"),
            "page": ev.get("page"),
            "chunk_id": ev.get("chunk_id"),
            "relevance_score": ev.get("score")
        }
        for ev in evidence
    ]

    audit_log.append({
        "event": "final_response_dispatched",
        "total_citations": len(citations),
        "confidence": confidence,
        "guardrail_status": guardrail_status
    })

    return {
        "audit_log": audit_log
    }
