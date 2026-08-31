"""
Member 6 Integration Bridge
============================
Connects Member 6's Data Intelligence & Security modules to:
  - Member 3's LangGraph agent pipeline (backend/agents/ + backend/graph/)
  - Member 5's ChromaDB RAG ingestion pipeline (backend/rag/)

Usage example (Member 3 in backend/graph/workflow.py):
    from data_intelligence.integration_bridge import Member6Bridge
    bridge = Member6Bridge()
    bridge.inject_into_workflow(state)   # enriches any AgentState dict
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1.  Knowledge-Graph Enrichment for Member 3's Planner / Investigator
# ---------------------------------------------------------------------------

class KnowledgeGraphBridge:
    """
    Wraps RefineryKnowledgeGraph so Member 3's agents can call it without
    depending directly on networkx or our internal graph representation.
    """

    def __init__(self) -> None:
        from data_intelligence.knowledge_graph import RefineryKnowledgeGraph
        self._kg = RefineryKnowledgeGraph()

    def get_blast_radius(self, equipment_id: str) -> Dict[str, Any]:
        """
        Returns blast-radius dict for a given equipment tag.

        Used by Member 3's InvestigationAgent to enrich its findings
        with downstream impact analysis from the Knowledge Graph.

        Args:
            equipment_id: MRPL equipment tag, e.g. "P-102A"

        Returns:
            {
              "equipment_id": str,
              "downstream_chain": [str, ...],   # ordered list of impacted units
              "standby_unit": str | None,
              "required_parts": [str, ...],
              "procedure_sop": str | None,
            }
        """
        blast_list = self._kg.get_equipment_blast_radius(equipment_id)
        # blast_list is a list of dicts like [{"node_id": ..., "hops": ...}, ...]
        downstream_chain = [item["node_id"] for item in blast_list if "node_id" in item]

        standby_info = self._kg.get_standby_redundancy(equipment_id)
        standby_unit = standby_info.get("standby_unit") if standby_info else None

        mitigation = self._kg.get_mitigation_plan(equipment_id)
        return {
            "equipment_id": equipment_id,
            "downstream_chain": downstream_chain,
            "standby_unit": standby_unit,
            "required_parts": mitigation.get("required_parts", []),
            "procedure_sop": mitigation.get("procedure_sop"),
        }

    def export_rag_triples(self) -> List[Tuple[str, str, str]]:
        """
        Returns all (Subject, Predicate, Object) triples from the knowledge graph.
        Member 5 uses this to seed their ChromaDB / FAISS vector store
        with structured domain knowledge.
        """
        return self._kg.export_triples()

    def export_cytoscape(self) -> Dict[str, Any]:
        """
        Returns Cytoscape.js-compatible graph JSON.
        Member 1 (Frontend) uses this to render the equipment topology.
        """
        return self._kg.export_cytoscape_json()


# ---------------------------------------------------------------------------
# 2.  Document-Extraction Bridge for Member 5's RAG Ingestion Pipeline
# ---------------------------------------------------------------------------

class DocumentIngestionBridge:
    """
    Wraps DocumentExtractor so Member 5 can ingest documents into ChromaDB
    using Member 6's dual-engine (PyMuPDF + OCR) extractor without
    writing their own PDF parsing code.
    """

    def __init__(self) -> None:
        from data_intelligence.pdf_extractor import DocumentExtractor
        self._extractor = DocumentExtractor()

    def ingest_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts and returns chunked documents ready for ChromaDB upsert.

        Returns a list of dicts, each matching the ChromaDB `add()` format:
            {
              "id": str,           # unique chunk_id
              "document": str,     # raw chunk text
              "metadata": {
                "source_document": str,
                "page_number": int,
                "block_type": str,     # 'header' | 'paragraph' | 'table'
                "needs_human_review": bool,
                "allowed_roles": str,  # comma-separated RBAC roles
              }
            }
        """
        from security.rbac import DEFAULT_DOCUMENT_ROLES
        result = self._extractor.extract(pdf_path)
        chroma_docs = []
        for chunk in result.chunks:
            chroma_docs.append({
                "id": chunk.chunk_id,
                "document": chunk.text,
                "metadata": {
                    "source_document": chunk.source_document,
                    "page_number": chunk.page_number,
                    "block_type": chunk.block_type,
                    "needs_human_review": chunk.needs_human_review,
                    "allowed_roles": DEFAULT_DOCUMENT_ROLES,
                },
            })
        logger.info(
            "Ingestion bridge: extracted %d chunks from '%s'",
            len(chroma_docs), pdf_path,
        )
        return chroma_docs


# ---------------------------------------------------------------------------
# 3.  RBAC Bridge for Member 3's LangGraph nodes
# ---------------------------------------------------------------------------

class RBACBridge:
    """
    Thin wrapper around Member 6's RBAC matrix for use in Member 3's
    LangGraph nodes (e.g. guardrail, query router) without importing
    the full security module.
    """

    def __init__(self) -> None:
        from security.rbac import RBACEnforcer
        self._enforcer = RBACEnforcer()

    def can_access(self, user_role: str, action: str) -> bool:
        """
        Returns True if user_role is permitted to perform action.

        Args:
            user_role: One of Admin | Plant_Engineer | Safety_Officer |
                       Auditor | Operator (case-insensitive)
            action:   One of read_document | run_query | generate_note |
                       view_audit | manage_users

        Returns:
            bool
        """
        from security.rbac import PermissionDeniedError
        try:
            self._enforcer.require(user_role, action)
            return True
        except (PermissionError, PermissionDeniedError):
            return False

    def check_and_raise(self, user_role: str, action: str) -> None:
        """Raises PermissionError if role is not authorized."""
        self._enforcer.require(user_role, action)


# ---------------------------------------------------------------------------
# 4.  Audit-Trail Bridge for Member 3's LangGraph event logging
# ---------------------------------------------------------------------------

class AuditBridge:
    """
    Allows Member 3's LangGraph nodes to append events to the
    Member 6 tamper-evident audit trail automatically.
    """

    def __init__(self) -> None:
        from security.audit_trail import AuditLogger
        self._logger = AuditLogger()

    def log_event(
        self,
        event_type: str,
        user_role: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Appends a signed, hash-chained audit event.

        Args:
            event_type: Human-readable event label (e.g. "rag_retrieval",
                        "claim_verified", "guardrail_applied")
            user_role:  Role performing the action
            details:    Optional dict of extra metadata to include
        """
        # AuditLogger.log(actor_id, role, action, resource, status, metadata)
        self._logger.log(
            actor_id="system",
            role=user_role,
            action=event_type,
            resource="indusai-x",
            status="SUCCESS",
            metadata=details or {},
        )

    def verify_trail(self) -> Dict[str, Any]:
        """Returns integrity verification result for judge demo."""
        from security.audit_trail import AuditLogger
        import os
        log_path = os.path.join(os.getcwd(), "audit_trail.jsonl")
        is_valid, corrupted_line, message = AuditLogger.verify_audit_trail(log_path)
        return {"is_valid": is_valid, "corrupted_line": corrupted_line, "message": message}


# ---------------------------------------------------------------------------
# 5.  Unified Bridge Facade (one-stop shop for Member 3)
# ---------------------------------------------------------------------------

class Member6Bridge:
    """
    Single import point for Member 3's workflow.

    Example usage in backend/graph/workflow.py:

        from data_intelligence.integration_bridge import Member6Bridge

        bridge = Member6Bridge()

        # In the investigator node:
        blast = bridge.kg.get_blast_radius("P-102A")

        # In the guardrail node:
        if not bridge.rbac.can_access(user_role, "run_query"):
            raise PermissionError(...)

        # Auto-log every node completion:
        bridge.audit.log_event("node_complete", user_role, {"node": "guardrail"})
    """

    def __init__(self) -> None:
        self.kg = KnowledgeGraphBridge()
        self.ingestion = DocumentIngestionBridge()
        self.rbac = RBACBridge()
        self.audit = AuditBridge()

    def enrich_agent_state(
        self, state: Dict[str, Any], equipment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method: injects KG blast-radius and RBAC status
        directly into a LangGraph AgentState dict.

        Call this at the top of any LangGraph node that needs domain context.
        """
        enriched = dict(state)
        if equipment_id:
            enriched["kg_blast_radius"] = self.kg.get_blast_radius(equipment_id)
        enriched["m6_rbac_bridge"] = self.rbac
        enriched["m6_audit_bridge"] = self.audit
        return enriched
