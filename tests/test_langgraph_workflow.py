"""
Unit tests for LangGraph multi-agent workflow execution and auditability.
"""

import shutil
import tempfile

from indusai.agents.graph import IndusAIGraph
from indusai.ingestion.schema import Chunk, ChunkMetadata
from indusai.storage.vector_store import ChromaVectorStore


def test_full_langgraph_workflow_execution():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaVectorStore(persist_directory=temp_dir, collection_name="test_graph")

        chunk1 = Chunk(
            text="During Unit 2 inspection, Pump P-101 bearing temperature exceeded normal range at 95°C.",
            metadata=ChunkMetadata(
                chunk_id="chunk_8f29",
                document_id="maintenance_report_102",
                document_name="Pump_P-101_Maintenance.pdf",
                page=14,
                section="Root Cause Analysis",
                equipment_id="P-101",
                document_type="maintenance_report",
                department="maintenance",
                classification="confidential",
                allowed_roles=["maintenance_engineer", "supervisor"],
                timestamp="2026-08-20",
            ),
        )
        chunk2 = Chunk(
            text="Inspection notes: Lubrication contamination observed in reservoir.",
            metadata=ChunkMetadata(
                chunk_id="chunk_4a12",
                document_id="inspection_report_301",
                document_name="Pump_P-101_Inspection.pdf",
                page=3,
                section="Visual Inspection",
                equipment_id="P-101",
                document_type="inspection_log",
                department="maintenance",
                classification="internal",
                allowed_roles=["maintenance_engineer", "supervisor", "operator"],
                timestamp="2026-08-21",
            ),
        )
        store.add_chunks([chunk1, chunk2])

        graph = IndusAIGraph(vector_store=store)
        state = graph.run(
            user_query="Why did Pump P-101 fail?",
            user_id="engineer_09",
            user_role="maintenance_engineer",
        )

        assert state["intent"] == "root_cause_investigation"
        assert len(state["plan"]) > 0
        assert len(state["retrieved_docs"]) > 0
        assert len(state["evidence"]) > 0
        assert "ANSWER" in state["draft_answer"]
        assert "Verified Findings" in state["draft_answer"]
        assert "Confidence" in state["draft_answer"]
        assert len(state["audit_log"]) >= 6

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
