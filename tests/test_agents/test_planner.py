"""
Unit tests for PlannerAgent.
"""

from backend.agents.planner import PlannerAgent


def test_planner_intent_routing():
    planner = PlannerAgent()
    assert planner.route_query("Why did Pump P-101 fail?") == "root_cause_investigation"
    assert planner.route_query("How to perform startup procedure for K-201?") == "sop_lookup"
    assert planner.route_query("Find maintenance report for tank TK-502") == "document_search"
    assert planner.route_query("General refinery info") == "knowledge_query"


def test_planner_workflow_plan():
    planner = PlannerAgent()
    plan = planner.plan_workflow("root_cause_investigation")
    assert len(plan) >= 4
    assert any("rag_agent" in step for step in plan)
