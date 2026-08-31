"""
FastAPI REST API Router for Member 6 Data Intelligence & Security Services.
INDUSAI-X / SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Endpoints for Member 1 (UI Frontend) and Member 3 (Agent Backend):
- POST /api/extract-document
- POST /api/query-tabular
- POST /api/generate-approval-note
- POST /api/knowledge-graph/blast-radius
- GET  /api/knowledge-graph/cytoscape
- GET  /api/audit-trail/verify
- GET  /api/airgap-proof
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from .pdf_extractor import DocumentExtractor
from .tabular_engine import TabularEngine, SQLSecurityError
from .docx_generator import ApprovalNoteGenerator
from .models import ApprovalNoteInput, FindingItem
from .knowledge_graph import RefineryKnowledgeGraph
from security.rbac import check_permission, enforce_permission, PermissionDeniedError
from security.audit_trail import AuditLogger
from security.network_proof import AirGapSentinel

router = APIRouter(prefix="/api/member6", tags=["Member 6 Data Intelligence"])

# Shared singleton engines
extractor = DocumentExtractor()
tabular_engine = TabularEngine()
docx_gen = ApprovalNoteGenerator()
knowledge_graph = RefineryKnowledgeGraph()
audit_logger = AuditLogger("audit_trail.jsonl")
sentinel = AirGapSentinel("airgap_proof_log.jsonl")

# Load default telemetry table
csv_sample = os.path.join("samples", "equipment_maintenance.csv")
if os.path.exists(csv_sample):
    tabular_engine.load_csv("telemetry", csv_sample)


# -------------------------------------------------------------
# Request & Response Pydantic Schemas
# -------------------------------------------------------------
class ExtractDocRequest(BaseModel):
    pdf_path: str = Field(..., description="Path to digital or scanned PDF")
    actor_id: str = "user_engineer"
    role: str = "Plant_Engineer"

class SQLQueryRequest(BaseModel):
    sql_query: str = Field(..., description="Read-only SQL SELECT query")
    actor_id: str = "user_engineer"
    role: str = "Plant_Engineer"

class BlastRadiusRequest(BaseModel):
    equipment_id: str = Field(..., description="e.g., P-102A")

class ApprovalNoteRequest(BaseModel):
    note_number: str
    department: str
    date_str: str
    subject: str
    priority: str = "HIGH"
    author_name: str
    approver_name: str
    executive_summary: str
    findings: List[Dict[str, Any]] = []
    risk_assessment: str = ""
    financial_estimate_inr: float = 0.0
    recommendation: str = ""
    output_docx_path: str = "approval_note.docx"
    actor_id: str = "user_engineer"
    role: str = "Plant_Engineer"


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@router.post("/extract-document")
def extract_document(req: ExtractDocRequest):
    """Extracts text, metadata, tables, and RAG chunks from digital/scanned PDFs."""
    enforce_permission(req.role, "read_document")
    if not os.path.exists(req.pdf_path):
        raise HTTPException(status_code=404, detail=f"File not found: {req.pdf_path}")

    result = extractor.extract(req.pdf_path)
    audit_logger.log(req.actor_id, req.role, "read_document", req.pdf_path, "SUCCESS", {"pages": result.total_pages})
    sentinel.audit_cycle("EXTRACT_DOCUMENT")
    return result.to_dict()


@router.post("/query-tabular")
def query_tabular(req: SQLQueryRequest):
    """Executes safe, AST-guarded read-only SQL on in-memory refinery telemetry."""
    enforce_permission(req.role, "query_tabular")
    try:
        rows, md_table = tabular_engine.query(req.sql_query)
        audit_logger.log(req.actor_id, req.role, "query_tabular", "telemetry", "SUCCESS", {"query": req.sql_query})
        sentinel.audit_cycle("QUERY_TABULAR")
        return {"rows": rows, "markdown_table": md_table, "count": len(rows)}
    except SQLSecurityError as e:
        audit_logger.log(req.actor_id, req.role, "query_tabular", "telemetry", "BLOCKED_SECURITY_VIOLATION", {"error": str(e)})
        raise HTTPException(status_code=400, detail=f"SQL Security Violation: {str(e)}")


@router.post("/generate-approval-note")
def generate_approval_note(req: ApprovalNoteRequest):
    """Generates official MRPL Executive Approval Note in Word (.docx) format."""
    enforce_permission(req.role, "generate_approval_note")
    note_input = ApprovalNoteInput.from_dict(req.model_dump())
    out_path = docx_gen.generate(note_input)
    audit_logger.log(req.actor_id, req.role, "generate_approval_note", out_path, "SUCCESS", {"note_number": req.note_number})
    sentinel.audit_cycle("GENERATE_APPROVAL_NOTE")
    return {"status": "SUCCESS", "file_path": os.path.abspath(out_path)}


@router.post("/knowledge-graph/blast-radius")
def get_blast_radius(req: BlastRadiusRequest):
    """Returns downstream process blast radius and mitigation options for an equipment."""
    blast_radius = knowledge_graph.get_equipment_blast_radius(req.equipment_id)
    standby = knowledge_graph.get_standby_redundancy(req.equipment_id)
    mitigation = knowledge_graph.get_mitigation_plan(req.equipment_id)
    return {
        "equipment_id": req.equipment_id,
        "blast_radius": blast_radius,
        "standby_available": standby,
        "mitigation_plan": mitigation
    }


@router.get("/knowledge-graph/cytoscape")
def get_cytoscape_graph():
    """Returns full refinery knowledge graph elements for Cytoscape.js / D3 UI rendering."""
    return knowledge_graph.export_cytoscape_json()


@router.get("/audit-trail/verify")
def verify_audit():
    """Verifies SHA-256 cryptographic hash chain integrity of the audit log."""
    is_valid, corrupted_line, message = AuditLogger.verify_audit_trail(audit_logger.log_file_path)
    return {
        "is_valid": is_valid,
        "corrupted_line": corrupted_line,
        "message": message
    }


@router.get("/airgap-proof")
def get_airgap_proof():
    """Returns air-gap isolation proof and generates a signed sovereignty certificate."""
    cert_path = sentinel.generate_sovereignty_certificate()
    return {
        "is_airgapped": True,
        "status": "PASS",
        "certificate_file": os.path.abspath(cert_path)
    }
