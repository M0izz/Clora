"""
AgentState definition for INDUSAI-X LangGraph workflow.
Strictly conforms to SIH26117 specifications.
"""

from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    user_query: str
    user_id: str
    user_role: str

    intent: str
    plan: list

    retrieved_docs: list
    evidence: list

    agent_outputs: dict

    draft_answer: str
    claims: list
    verification_results: list

    confidence: float
    guardrail_status: str

    audit_log: list
