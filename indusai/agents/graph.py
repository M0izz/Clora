"""
LangGraph Multi-Agent Workflow for INDUSAI-X.
Orchestrates sovereign industrial agents, verification, and human review escalation.
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from indusai.agents.state import AgentState
from indusai.agents.nodes.query_router import query_router_node
from indusai.agents.nodes.planner import planner_node
from indusai.agents.nodes.rag_agent import RAGAgent
from indusai.agents.nodes.investigation_agent import InvestigationAgent
from indusai.agents.nodes.synthesizer import IndustrialSynthesizer
from indusai.agents.nodes.evidence_verifier import EvidenceVerifierNode
from indusai.agents.nodes.guardrail import HallucinationFirewallNode
from indusai.agents.nodes.human_review import human_review_node
from indusai.agents.nodes.final_response import final_response_node
from indusai.storage.vector_store import ChromaVectorStore
from indusai.retrieval.reranker import IndustrialReranker

class IndusAIGraph:
    """Manages compilation and invocation of the INDUSAI-X LangGraph workflow."""

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        reranker: Optional[IndustrialReranker] = None
    ):
        self.vector_store = vector_store or ChromaVectorStore()
        self.reranker = reranker or IndustrialReranker()

        self.rag_agent_instance = RAGAgent(self.vector_store, self.reranker)
        self.investigation_agent_instance = InvestigationAgent()
        self.synthesizer_instance = IndustrialSynthesizer()
        self.verifier_instance = EvidenceVerifierNode()
        self.guardrail_instance = HallucinationFirewallNode()

        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Register nodes
        workflow.add_node("query_router", query_router_node)
        workflow.add_node("planner", planner_node)
        workflow.add_node("rag_agent", self.rag_agent_instance.run)
        workflow.add_node("investigation_agent", self.investigation_agent_instance.run)
        workflow.add_node("synthesizer", self.synthesizer_instance.synthesize)
        workflow.add_node("evidence_verifier", self.verifier_instance.run)
        workflow.add_node("guardrail", self.guardrail_instance.run)
        workflow.add_node("human_review", human_review_node)
        workflow.add_node("final_response", final_response_node)

        # Set entry point
        workflow.set_entry_point("query_router")

        # Standard linear flow with conditional branching at guardrail
        workflow.add_edge("query_router", "planner")
        workflow.add_edge("planner", "rag_agent")
        workflow.add_edge("rag_agent", "investigation_agent")
        workflow.add_edge("investigation_agent", "synthesizer")
        workflow.add_edge("synthesizer", "evidence_verifier")
        workflow.add_edge("evidence_verifier", "guardrail")

        # Conditional routing after guardrail
        def route_after_guardrail(state: AgentState) -> str:
            status = state.get("guardrail_status", "PASSED")
            if "FLAGGED" in status:
                return "human_review"
            return "final_response"

        workflow.add_conditional_edges(
            "guardrail",
            route_after_guardrail,
            {
                "human_review": "human_review",
                "final_response": "final_response"
            }
        )

        workflow.add_edge("human_review", "final_response")
        workflow.add_edge("final_response", END)

        return workflow.compile()

    def run(self, user_query: str, user_id: str = "eng_01", user_role: str = "maintenance_engineer") -> AgentState:
        initial_state: AgentState = {
            "user_query": user_query,
            "user_id": user_id,
            "user_role": user_role,
            "intent": "",
            "plan": [],
            "retrieved_docs": [],
            "evidence": [],
            "agent_outputs": {},
            "draft_answer": "",
            "claims": [],
            "verification_results": [],
            "confidence": 0.0,
            "guardrail_status": "PENDING",
            "audit_log": [{
                "event": "session_started",
                "user_id": user_id,
                "user_role": user_role,
                "query": user_query
            }]
        }
        final_state = self.graph.invoke(initial_state)
        return final_state
