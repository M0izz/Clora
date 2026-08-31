"""
Tests for the Member 6 Integration Bridge.
Verifies that KnowledgeGraphBridge, DocumentIngestionBridge,
RBACBridge, and AuditBridge all function correctly without
requiring langgraph or chromadb to be installed.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# KnowledgeGraphBridge tests
# ---------------------------------------------------------------------------

class TestKnowledgeGraphBridge:
    def setup_method(self):
        from data_intelligence.integration_bridge import KnowledgeGraphBridge
        self.bridge = KnowledgeGraphBridge()

    def test_blast_radius_returns_dict_with_required_keys(self):
        result = self.bridge.get_blast_radius("P-102A")
        assert isinstance(result, dict)
        for key in ["equipment_id", "downstream_chain", "standby_unit", "required_parts"]:
            assert key in result, f"Missing key: {key}"
        assert result["equipment_id"] == "P-102A"

    def test_blast_radius_downstream_chain_not_empty(self):
        result = self.bridge.get_blast_radius("P-102A")
        assert isinstance(result["downstream_chain"], list)
        assert len(result["downstream_chain"]) > 0

    def test_export_rag_triples_returns_list_of_tuples(self):
        triples = self.bridge.export_rag_triples()
        assert isinstance(triples, list)
        assert len(triples) > 0
        for triple in triples[:3]:
            assert isinstance(triple, tuple)
            assert len(triple) == 3

    def test_export_cytoscape_returns_nodes_and_edges(self):
        cyto = self.bridge.export_cytoscape()
        assert "nodes" in cyto
        assert "edges" in cyto
        assert len(cyto["nodes"]) > 0


# ---------------------------------------------------------------------------
# RBACBridge tests
# ---------------------------------------------------------------------------

class TestRBACBridge:
    def setup_method(self):
        from data_intelligence.integration_bridge import RBACBridge
        self.bridge = RBACBridge()

    def test_admin_can_do_everything(self):
        for action in ["read_document", "query_tabular", "generate_approval_note", "view_audit_log"]:
            assert self.bridge.can_access("Admin", action), f"Admin denied: {action}"

    def test_operator_restricted_to_read_only(self):
        assert self.bridge.can_access("Operator", "read_document") is True
        assert self.bridge.can_access("Operator", "generate_approval_note") is False
        assert self.bridge.can_access("Operator", "view_audit_log") is False

    def test_check_and_raise_on_denied_action(self):
        from security.rbac import PermissionDeniedError
        with pytest.raises((PermissionError, PermissionDeniedError)):
            self.bridge.check_and_raise("Operator", "generate_approval_note")

    def test_plant_engineer_can_run_query(self):
        assert self.bridge.can_access("Plant_Engineer", "read_document") is True
        assert self.bridge.can_access("Plant_Engineer", "query_tabular") is True


# ---------------------------------------------------------------------------
# AuditBridge tests
# ---------------------------------------------------------------------------

class TestAuditBridge:
    def test_log_event_and_verify(self):
        from data_intelligence.integration_bridge import AuditBridge
        bridge = AuditBridge()
        # Log two events
        bridge.log_event("rag_retrieval", "Plant_Engineer", {"query": "P-102A failure"})
        bridge.log_event("guardrail_applied", "Admin", {"status": "PASS"})
        # Verify the trail returns the expected dict structure
        result = bridge.verify_trail()
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "message" in result
        # Trail should be valid since we just wrote to it
        assert result["is_valid"] is True


# ---------------------------------------------------------------------------
# Member6Bridge facade tests
# ---------------------------------------------------------------------------

class TestMember6Bridge:
    def setup_method(self):
        from data_intelligence.integration_bridge import Member6Bridge
        self.bridge = Member6Bridge()

    def test_bridge_has_all_sub_bridges(self):
        assert hasattr(self.bridge, "kg")
        assert hasattr(self.bridge, "ingestion")
        assert hasattr(self.bridge, "rbac")
        assert hasattr(self.bridge, "audit")

    def test_enrich_agent_state_adds_kg_data(self):
        state = {"user_query": "Why did P-102A fail?", "user_role": "Plant_Engineer"}
        enriched = self.bridge.enrich_agent_state(state, equipment_id="P-102A")
        assert "kg_blast_radius" in enriched
        assert enriched["kg_blast_radius"]["equipment_id"] == "P-102A"

    def test_enrich_agent_state_without_equipment_id(self):
        state = {"user_query": "Show me all documents", "user_role": "Auditor"}
        enriched = self.bridge.enrich_agent_state(state)
        # Should not crash; kg_blast_radius should not be present
        assert "kg_blast_radius" not in enriched
        assert "m6_rbac_bridge" in enriched
