"""
Planner and Query Router agent.
"""

from typing import List


class PlannerAgent:
    """Classifies user intent and plans execution workflow."""

    def route_query(self, query: str) -> str:
        q_lower = query.lower()
        if any(
            w in q_lower
            for w in [
                "why",
                "fail",
                "failure",
                "cause",
                "root cause",
                "overheat",
                "breakdown",
                "investigate",
            ]
        ):
            return "root_cause_investigation"
        elif any(
            w in q_lower for w in ["how to", "procedure", "sop", "steps", "start-up", "shutdown"]
        ):
            return "sop_lookup"
        elif any(w in q_lower for w in ["find", "search", "document", "report", "manual"]):
            return "document_search"
        return "knowledge_query"

    def plan_workflow(self, intent: str) -> List[str]:
        if intent == "root_cause_investigation":
            return [
                "rag_agent:retrieve_maintenance_records",
                "investigation_agent:cross_correlate_sources",
                "synthesizer:draft_findings",
                "verifier:verify_claims_and_causality",
                "guardrail:firewall_and_hedge",
            ]
        return [
            "rag_agent:retrieve_documents",
            "synthesizer:draft_findings",
            "verifier:verify_claims",
            "guardrail:firewall",
        ]
