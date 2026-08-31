"""
Planner Node for INDUSAI-X.
Determines sequence of agent invocations based on intent and query complexity.
"""

from typing import Dict, Any, List
from indusai.agents.state import AgentState

def planner_node(state: AgentState) -> Dict[str, Any]:
    intent = state.get("intent", "general_query")
    query = state.get("user_query", "")
    
    plan: List[str] = []
    if intent == "root_cause_investigation":
        plan = [
            "rag_agent:retrieve_maintenance_records",
            "rag_agent:retrieve_inspection_logs",
            "investigation_agent:cross_correlate_sources",
            "synthesizer:draft_findings",
            "evidence_verifier:verify_claims_and_causality",
            "guardrail:firewall_and_hedge"
        ]
    elif intent == "sop_lookup":
        plan = [
            "rag_agent:retrieve_sops",
            "synthesizer:draft_procedure",
            "evidence_verifier:verify_steps",
            "guardrail:firewall"
        ]
    else:
        plan = [
            "rag_agent:retrieve_documents",
            "synthesizer:draft_answer",
            "evidence_verifier:verify",
            "guardrail:firewall"
        ]

    audit_entry = {
        "event": "plan_generated",
        "plan_steps": plan
    }
    audit_log = list(state.get("audit_log", []))
    audit_log.append(audit_entry)

    return {
        "plan": plan,
        "audit_log": audit_log
    }
