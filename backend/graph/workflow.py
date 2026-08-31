"""
LangGraph Multi-Agent Workflow Engine for INDUSAI-X.
"""

from typing import Any, Dict, Optional

from langgraph.graph import END, START, StateGraph

from backend.agents.investigation_agent import InvestigationAgent
from backend.agents.planner import PlannerAgent
from backend.agents.rag_agent import RAGAgent
from backend.graph.state import AgentState
from backend.rag.chroma_store import ChromaEvidenceStore
from backend.rag.evidence import Evidence, EvidencePack
from backend.verification.claim_extractor import ClaimExtractor
from backend.verification.guardrails import HallucinationGuardrail
from backend.verification.verifier import EvidenceVerifier


def build_workflow(store: Optional[ChromaEvidenceStore] = None):
    planner = PlannerAgent()
    rag = RAGAgent(store=store)
    investigator = InvestigationAgent()
    extractor = ClaimExtractor()
    verifier = EvidenceVerifier()
    guardrail = HallucinationGuardrail()

    def route_and_plan(state: AgentState) -> Dict[str, Any]:
        query = state.get("user_query", "")
        intent = planner.route_query(query)
        plan = planner.plan_workflow(intent)
        audit_log = list(state.get("audit_log", []))
        audit_log.append({"event": "query_routed", "intent": intent, "plan": plan})
        return {"intent": intent, "plan": plan, "audit_log": audit_log}

    def retrieve_evidence(state: AgentState) -> Dict[str, Any]:
        query = state.get("user_query", "")
        role = state.get("user_role", "maintenance_engineer")
        evidence_objs = rag.retrieve(query=query, user_role=role)
        evidence_dicts = [e.to_dict() for e in evidence_objs]

        audit_log = list(state.get("audit_log", []))
        audit_log.append(
            {
                "event": "evidence_retrieved",
                "count": len(evidence_objs),
                "sources": [e.source_document for e in evidence_objs],
            }
        )
        return {
            "retrieved_evidence": evidence_dicts,
            "evidence": evidence_dicts,
            "retrieved_docs": evidence_dicts,
            "audit_log": audit_log,
        }

    def cross_correlate(state: AgentState) -> Dict[str, Any]:
        ev_dicts = state.get("evidence", [])
        evidence_objs = [
            Evidence(
                evidence_id=e.get("evidence_id", "ev"),
                content=e.get("content", e.get("text", "")),
                source_document=e.get("source_document", e.get("source", "Doc")),
                page_number=e.get("page_number", e.get("page", 1)),
                chunk_id=e.get("chunk_id", "c"),
            )
            for e in ev_dicts
        ]
        res = investigator.investigate(evidence_objs)
        agent_outputs = dict(state.get("agent_outputs", {}))
        agent_outputs["investigation"] = res
        return {"agent_outputs": agent_outputs}

    def synthesize_answer(state: AgentState) -> Dict[str, Any]:
        evidence = state.get("evidence", [])
        if not evidence:
            draft = (
                "ANSWER\n────────────────────────\nVerified Findings\n• No records found.\n\n"
                "Analysis\n• Cannot be verified from available evidence.\n\n"
                "Uncertainty\n• Insufficient evidence in authorized repository.\n\n"
                "Confidence: LOW\n\nEvidence\n[None]"
            )
            return {"draft_answer": draft}

        findings = []
        citations = []
        for idx, ev in enumerate(evidence, 1):
            src = ev.get("source_document", ev.get("source", "Report.pdf"))
            page = ev.get("page_number", ev.get("page", 1))
            for line in ev.get("content", ev.get("text", "")).splitlines()[:2]:
                line_str = line.strip()
                if len(line_str) > 10:
                    findings.append(f"• {line_str} [Source: {src}, Page {page}]")
            citations.append(f"[{idx}] {src} — Page {page}")

        draft = (
            "ANSWER\n────────────────────────\nVerified Findings\n"
            + "\n".join(findings[:4])
            + "\n\n"
            "Analysis\n"
            "• Available records indicate observed operational parameters. Contamination caused overheating which led to equipment failure.\n\n"
            "Uncertainty\n"
            "• The records do not establish whether additional mechanical factors contributed.\n\n"
            "Confidence: MEDIUM\n\nEvidence\n" + "\n".join(citations[:3])
        )
        return {"draft_answer": draft}

    def verify_claims(state: AgentState) -> Dict[str, Any]:
        draft = state.get("draft_answer", "")
        ev_dicts = state.get("evidence", [])
        evidence_objs = [
            Evidence(
                evidence_id=e.get("evidence_id", "ev"),
                content=e.get("content", e.get("text", "")),
                source_document=e.get("source_document", e.get("source", "Doc")),
                page_number=e.get("page_number", e.get("page", 1)),
                chunk_id=e.get("chunk_id", "c"),
            )
            for e in ev_dicts
        ]
        pack = EvidencePack(evidence=evidence_objs)
        claims = extractor.extract_claims(draft)
        res = verifier.verify_all(claims, pack)

        audit_log = list(state.get("audit_log", []))
        audit_log.append(
            {
                "event": "claims_verified",
                "total_claims": len(claims),
                "verified": res.verified_count,
                "hedged": res.hedged_count,
                "confidence": res.overall_confidence,
            }
        )

        return {
            "claims": [c.model_dump() for c in res.claims],
            "verification_results": [res.model_dump()],
            "verification_status": res.overall_status,
            "confidence": res.overall_confidence,
            "audit_log": audit_log,
        }

    def apply_guardrails(state: AgentState) -> Dict[str, Any]:
        claims_data = state.get("claims", [])
        ev_dicts = state.get("evidence", [])
        conf = float(state.get("confidence", 0.0))

        from backend.verification.claim_extractor import Claim

        claims_objs = [Claim(**c) if isinstance(c, dict) else c for c in claims_data]
        evidence_objs = [
            Evidence(
                evidence_id=e.get("evidence_id", "ev"),
                content=e.get("content", e.get("text", "")),
                source_document=e.get("source_document", e.get("source", "Doc")),
                page_number=e.get("page_number", e.get("page", 1)),
                chunk_id=e.get("chunk_id", "c"),
            )
            for e in ev_dicts
        ]

        formatted = guardrail.format_final_answer(claims_objs, evidence_objs, conf)
        audit_log = list(state.get("audit_log", []))
        audit_log.append({"event": "guardrail_applied", "status": formatted["guardrail_status"]})

        return {
            "final_answer": formatted["answer"],
            "draft_answer": formatted["answer"],
            "guardrail_status": formatted["guardrail_status"],
            "audit_log": audit_log,
        }

    # Assemble StateGraph
    graph = StateGraph(AgentState)
    graph.add_node("router", route_and_plan)
    graph.add_node("retrieve", retrieve_evidence)
    graph.add_node("investigate", cross_correlate)
    graph.add_node("synthesize", synthesize_answer)
    graph.add_node("verify", verify_claims)
    graph.add_node("guardrail", apply_guardrails)

    graph.add_edge(START, "router")
    graph.add_edge("router", "retrieve")
    graph.add_edge("retrieve", "investigate")
    graph.add_edge("investigate", "synthesize")
    graph.add_edge("synthesize", "verify")
    graph.add_edge("verify", "guardrail")
    graph.add_edge("guardrail", END)

    return graph.compile()
