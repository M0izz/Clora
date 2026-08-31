"""
FastAPI Router for INDUSAI-X Intelligence Backbone.
Plugs cleanly into team backend services.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from indusai.agents.graph import IndusAIGraph
from indusai.ingestion.document_parser import DocumentParser
from indusai.ingestion.chunker import IntelligentChunker
from indusai.storage.vector_store import ChromaVectorStore
from indusai.verification.verifier import EvidenceVerifier
from indusai.verification.claim_extractor import ClaimExtractor
from indusai.verification.schemas import Claim, VerificationResult
from indusai.retrieval.evidence_pack import EvidencePack, EvidenceItem

router = APIRouter(prefix="/api/v1", tags=["INDUSAI-X Intelligence Backbone"])

# Singleton pipeline instances
vector_store = ChromaVectorStore()
parser = DocumentParser()
chunker = IntelligentChunker()
graph_runner = IndusAIGraph(vector_store=vector_store)
verifier = EvidenceVerifier()
extractor = ClaimExtractor()

# Request/Response schemas
class QueryRequest(BaseModel):
    user_query: str = Field(..., example="Why did Pump P-101 fail?")
    user_id: str = Field(default="eng_01", example="eng_01")
    user_role: str = Field(default="maintenance_engineer", example="maintenance_engineer")

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    guardrail_status: str
    intent: str
    plan: List[str]
    citations: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]

class IngestFileRequest(BaseModel):
    file_path: str
    document_id: Optional[str] = None
    document_type: str = "maintenance_report"
    department: str = "maintenance"
    classification: str = "internal"
    allowed_roles: List[str] = ["maintenance_engineer", "supervisor"]

class IngestResponse(BaseModel):
    status: str
    chunks_created: int
    document_id: str

class VerifyDirectRequest(BaseModel):
    claims: List[str]
    evidence_pack: List[Dict[str, Any]]

@router.post("/query", response_model=QueryResponse)
async def execute_agentic_query(req: QueryRequest):
    """Executes the full sovereign LangGraph multi-agent RAG and verification workflow."""
    try:
        final_state = graph_runner.run(
            user_query=req.user_query,
            user_id=req.user_id,
            user_role=req.user_role
        )
        
        evidence = final_state.get("evidence", [])
        citations = [
            {
                "source": ev.get("source"),
                "page": ev.get("page"),
                "chunk_id": ev.get("chunk_id"),
                "score": ev.get("score")
            }
            for ev in evidence
        ]

        return QueryResponse(
            answer=final_state.get("draft_answer", ""),
            confidence=final_state.get("confidence", 0.0),
            guardrail_status=final_state.get("guardrail_status", "UNKNOWN"),
            intent=final_state.get("intent", ""),
            plan=final_state.get("plan", []),
            citations=citations,
            verification_results=final_state.get("verification_results", []),
            audit_log=final_state.get("audit_log", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(req: IngestFileRequest):
    """Parses and chunks an industrial document into the permission-filtered Chroma store."""
    try:
        doc = parser.parse_file(
            file_path=req.file_path,
            document_id=req.document_id,
            document_type=req.document_type,
            department=req.department,
            classification=req.classification,
            allowed_roles=req.allowed_roles
        )
        chunks = chunker.chunk_document(doc)
        vector_store.add_chunks(chunks)
        return IngestResponse(
            status="SUCCESS",
            chunks_created=len(chunks),
            document_id=doc.document_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_claims_directly(req: VerifyDirectRequest):
    """Directly verifies claims against an evidence pack using the Hallucination Firewall."""
    evidence_items = [
        EvidenceItem(
            text=e.get("text", ""),
            source=e.get("source", "Doc"),
            page=int(e.get("page", 1)),
            chunk_id=e.get("chunk_id", "c"),
            score=float(e.get("score", 0.9))
        )
        for e in req.evidence_pack
    ]
    pack = EvidencePack(evidence=evidence_items)
    claims = [Claim(text=c) for c in req.claims]
    result = verifier.verify_all(claims, pack)
    return result.model_dump()

@router.get("/health")
async def health_check():
    """Returns local workbench health status."""
    return {
        "status": "HEALTHY",
        "sovereign_mode": "AIR_GAPPED_READY",
        "stored_chunks": vector_store.count(),
        "vector_db": "ChromaDB Persistent"
    }
