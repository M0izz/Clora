"""
Unit tests for Self-Healing Query Expansion, Re-retrieval Loop, and Fallback Paths.
"""

import shutil
import tempfile

from indusai.agents.graph import IndusAIGraph
from indusai.ingestion.schema import Chunk, ChunkMetadata
from indusai.retrieval.query_expander import IndustrialQueryExpander
from indusai.storage.vector_store import ChromaVectorStore


def test_query_expander_mappings():
    # Tag expansion
    expanded, exp_list = IndustrialQueryExpander.expand_query("Status of P-101")
    assert "Booster Pump 101" in expanded
    assert len(exp_list) > 0

    # Reverse colloquial mapping
    expanded2, exp_list2 = IndustrialQueryExpander.expand_query(
        "Why is the booster pump overheating?"
    )
    assert "P-101" in expanded2
    assert "thermal excursion" in expanded2 or "temperature exceeded normal" in expanded2


def test_re_retrieval_success_flow():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaVectorStore(persist_directory=temp_dir, collection_name="test_retry_success")

        # Ingest P-101 doc
        chunk = Chunk(
            text="Operating report for Centrifugal Booster Pump P-101 in crude unit.",
            metadata=ChunkMetadata(
                chunk_id="chunk_p101",
                document_id="doc_p101",
                document_name="Pump_P101.pdf",
                equipment_id="P-101",
                allowed_roles=["maintenance_engineer", "supervisor"],
            ),
        )
        store.add_chunks([chunk])

        graph = IndusAIGraph(vector_store=store)

        # Query using descriptor instead of ID
        state = graph.run(
            user_query="Inspect booster pump operation", user_role="maintenance_engineer"
        )

        assert len(state["retrieved_docs"]) > 0
        assert state["retrieved_docs"][0]["chunk_id"] == "chunk_p101"
        assert state["guardrail_status"] in ["PASSED", "CAUSAL_HEDGING_APPLIED"]

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_re_retrieval_clean_failure_fallback_path():
    """
    CRITICAL: Validates that when a query fails initial retrieval AND retry,
    the workflow cleanly terminates with INSUFFICIENT_EVIDENCE without looping or crashing.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaVectorStore(persist_directory=temp_dir, collection_name="test_retry_fail")
        graph = IndusAIGraph(vector_store=store)

        # Query completely nonexistent topic in empty/unrelated DB
        state = graph.run(
            user_query="What is the core coolant temperature of the nuclear reactor?",
            user_role="maintenance_engineer",
        )

        assert len(state["retrieved_docs"]) == 0
        assert len(state["evidence"]) == 0
        assert state["guardrail_status"] == "INSUFFICIENT_EVIDENCE"
        assert "cannot be verified from available evidence" in state["draft_answer"].lower()

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
