"""
Unit tests for Permission-Aware Retrieval.
Validates that unauthorized chunks are blocked at retrieval time before model exposure.
"""

import shutil
import tempfile

from indusai.ingestion.schema import Chunk, ChunkMetadata
from indusai.storage.vector_store import ChromaVectorStore


def test_permission_aware_retrieval():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaVectorStore(persist_directory=temp_dir, collection_name="test_rbac")

        # Chunk 1: Operator and Engineer accessible
        c1 = Chunk(
            text="Pump P-101 routine daily operating checklist and valve positions.",
            metadata=ChunkMetadata(
                chunk_id="chunk_public_01",
                document_id="doc_sop_01",
                document_name="SOP_P101.pdf",
                page=1,
                section="Daily Operations",
                equipment_id="P-101",
                allowed_roles=["operator", "maintenance_engineer", "supervisor"],
            ),
        )

        # Chunk 2: Restricted to Supervisor & Plant Manager (Confidential Incident & Root Cause)
        c2 = Chunk(
            text="Confidential incident report: Critical seal rupture on Pump P-101 due to uncalibrated over-pressure.",
            metadata=ChunkMetadata(
                chunk_id="chunk_confidential_02",
                document_id="doc_incident_99",
                document_name="Incident_Report_99.pdf",
                page=4,
                section="Investigation Findings",
                equipment_id="P-101",
                classification="confidential",
                allowed_roles=["supervisor", "plant_manager"],
            ),
        )

        store.add_chunks([c1, c2])

        # 1. Query as operator: MUST NOT see chunk_confidential_02
        operator_results = store.query(
            query_text="What happened to Pump P-101 incident?", user_role="operator", top_k=5
        )
        retrieved_ids_operator = [r["chunk_id"] for r in operator_results]
        assert "chunk_public_01" in retrieved_ids_operator
        assert "chunk_confidential_02" not in retrieved_ids_operator

        # 2. Query as supervisor: CAN see chunk_confidential_02
        supervisor_results = store.query(
            query_text="What happened to Pump P-101 incident?", user_role="supervisor", top_k=5
        )
        retrieved_ids_supervisor = [r["chunk_id"] for r in supervisor_results]
        assert "chunk_confidential_02" in retrieved_ids_supervisor

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
