"""
Query Router Node for INDUSAI-X.
Classifies industrial intent (root_cause_investigation, document_search, sop_lookup, general_query).
"""

import re
from typing import Dict, Any
from indusai.agents.state import AgentState

EQUIPMENT_ID_REGEX = re.compile(r'\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b', re.IGNORECASE)

def query_router_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("user_query", "")
    q_lower = query.lower()
    
    intent = "general_query"
    if any(w in q_lower for w in ["why", "fail", "failure", "cause", "root cause", "overheat", "breakdown", "investigate", "incident"]):
        intent = "root_cause_investigation"
    elif any(w in q_lower for w in ["how to", "procedure", "sop", "steps", "start-up", "shutdown"]):
        intent = "sop_lookup"
    elif any(w in q_lower for w in ["find", "search", "document", "report", "manual", "where"]):
        intent = "document_search"

    audit_entry = {
        "event": "query_routed",
        "user_id": state.get("user_id"),
        "user_role": state.get("user_role"),
        "intent": intent,
        "query": query
    }

    audit_log = list(state.get("audit_log", []))
    audit_log.append(audit_entry)

    return {
        "intent": intent,
        "audit_log": audit_log
    }
