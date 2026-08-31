"""
Test LangGraph workflow compilation and execution.
"""

import shutil
import tempfile

from backend.graph.workflow import build_workflow
from backend.rag.chroma_store import ChromaEvidenceStore


def test_workflow_compiles():
    workflow = build_workflow()
    assert workflow is not None


def test_workflow_execution():
    temp_dir = tempfile.mkdtemp()
    try:
        store = ChromaEvidenceStore(collection_name="test_wf", persist_path=temp_dir)
        workflow = build_workflow(store=store)

        state = {
            "user_query": "Why did Pump P-101 fail?",
            "user_role": "maintenance_engineer",
            "user_id": "eng_01",
        }
        res = workflow.invoke(state)

        assert res["intent"] == "root_cause_investigation"
        assert "ANSWER" in res["final_answer"]
        assert "Confidence" in res["final_answer"]
        assert len(res["audit_log"]) >= 4

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
