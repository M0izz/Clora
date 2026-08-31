"""
FastAPI route definitions for graph execution.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.graph.workflow import build_workflow

routes = APIRouter(prefix="/graph", tags=["Agent Workflow"])
workflow_runner = build_workflow()


class QueryRequest(BaseModel):
    user_query: str = Field(..., json_schema_extra={"example": "Why did Pump P-101 fail?"})
    user_id: str = "eng_01"
    user_role: str = "maintenance_engineer"


class QueryResponse(BaseModel):
    final_answer: str
    confidence: float
    guardrail_status: str
    intent: str
    plan: List[str]
    retrieved_evidence: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]


@routes.post("/execute", response_model=QueryResponse)
async def run_workflow(req: QueryRequest):
    try:
        initial_state = {
            "user_query": req.user_query,
            "user_id": req.user_id,
            "user_role": req.user_role,
            "audit_log": [{"event": "session_started", "user": req.user_id}],
        }
        res = workflow_runner.invoke(initial_state)
        return QueryResponse(
            final_answer=res.get("final_answer", res.get("draft_answer", "")),
            confidence=float(res.get("confidence", 0.0)),
            guardrail_status=res.get("guardrail_status", "UNKNOWN"),
            intent=res.get("intent", ""),
            plan=res.get("plan", []),
            retrieved_evidence=res.get("retrieved_evidence", res.get("evidence", [])),
            claims=res.get("claims", []),
            audit_log=res.get("audit_log", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
