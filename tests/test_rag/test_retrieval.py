"""
Unit tests for Retrieval, Permission Filter, and Query Expander.
"""

from backend.rag.retrieval import IndustrialQueryExpander, IndustrialReranker, PermissionFilter


def test_permission_filter_logic():
    assert (
        PermissionFilter.is_authorized(
            "maintenance_engineer", ["maintenance_engineer", "supervisor"]
        )
        is True
    )
    assert PermissionFilter.is_authorized("operator", ["supervisor", "plant_manager"]) is False
    assert PermissionFilter.is_authorized("plant_manager", ["restricted"]) is True


def test_query_expander_and_reranker():
    expanded, exp_list = IndustrialQueryExpander.expand_query("Why is the booster pump failing?")
    assert "P-101" in expanded
    assert len(exp_list) > 0

    reranker = IndustrialReranker(top_k=2)
    candidates = [
        {"chunk_id": "c1", "text": "General maintenance rules.", "score": 0.6, "metadata": {}},
        {
            "chunk_id": "c2",
            "text": "Pump P-101 Root cause analysis.",
            "score": 0.7,
            "metadata": {"equipment_id": "P-101", "section": "Root Cause"},
        },
    ]
    reranked = reranker.rerank("Why did P-101 fail?", candidates)
    assert len(reranked) == 2
    assert reranked[0]["chunk_id"] == "c2"
