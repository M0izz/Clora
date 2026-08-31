"""
AgentState definition for INDUSAI-X LangGraph workflow.
"""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_query: str
    user_id: str
    user_role: str

    intent: str
    plan: list

    retrieved_docs: list
    evidence: list
    retrieved_evidence: list

    agent_outputs: dict

    draft_answer: str
    claims: list
    verification_results: list
    verification_status: str

    confidence: float
    guardrail_status: str

    final_answer: str
    audit_log: list
