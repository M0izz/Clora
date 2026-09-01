from fastapi import APIRouter

router = APIRouter(tags=["Agent Integration Contracts"])


@router.get(
    "/agents",
    summary="List Registered Multi-Agent Specialized Roles & Integration Contracts",
)
def list_registered_agents():
    """
    Exposes modular agent definitions for Member 2 Frontend:
    Triage Agent, Document RAG Agent, Tabular Telemetry Agent, Vision P&ID Agent, and Synthesis Agent.
    """
    return {
        "orchestration_framework": "LangGraph StateGraph",
        "agents": [
            {
                "id": "triage_agent",
                "name": "Triage & Query Planner Agent",
                "role": "Classifies industrial inquiries and routes sub-tasks to specialized data workers.",
                "tools": ["route_query", "scan_prompt_injection", "extract_equipment_tag"],
                "status": "ready",
            },
            {
                "id": "document_agent",
                "name": "Permission-Aware RAG Agent",
                "role": "Retrieves grounded text chunks from manuals, SOPs, and incident reports via ChromaDB.",
                "tools": ["vector_search", "role_filter", "domain_reranker"],
                "status": "ready",
            },
            {
                "id": "tabular_agent",
                "name": "Tabular & Telemetry Agent",
                "role": "Executes AST-safe DuckDB SQL queries over vibration/temperature sensor time-series.",
                "tools": ["duckdb_sql_query", "excursion_detector", "trend_analyzer"],
                "status": "ready",
            },
            {
                "id": "vision_agent",
                "name": "Vision & P&ID Diagram Agent",
                "role": "Performs optical inspection and symbol verification across engineering drawings.",
                "tools": ["pid_tag_matcher", "valve_state_analyzer"],
                "status": "ready",
            },
            {
                "id": "synthesis_agent",
                "name": "Industrial Synthesizer & Verification Guardrail",
                "role": "Cross-correlates multi-source evidence and runs claims through Hallucination Firewall.",
                "tools": ["claim_extractor", "nli_verifier", "causal_leap_downgrader", "docx_generator"],
                "status": "ready",
            },
        ],
    }
