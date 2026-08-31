import time
from app.core.config import settings
from app.db.models import Query, Workspace
from app.services.agent_service import recover_zombie_queries


def test_async_query_and_polling(client):
    """Test async query dispatch (202 Accepted) and polling to completion."""
    # 1. Create Workspace
    ws_resp = client.post("/api/workspaces", json={"name": "Query Test Workspace"})
    ws_id = ws_resp.json()["id"]

    # 2. Dispatch Query
    q_payload = {
        "workspace_id": ws_id,
        "question": "What is the maximum allowable bearing temperature for Pump P-101?",
    }
    dispatch_resp = client.post("/api/query", json=q_payload)
    assert dispatch_resp.status_code == 202
    q_data = dispatch_resp.json()
    assert "query_id" in q_data
    assert q_data["poll_url"] == f"/api/query/{q_data['query_id']}"
    query_id = q_data["query_id"]

    # 3. Poll until completed
    max_retries = 20
    completed = False
    final_poll = None
    for _ in range(max_retries):
        poll_resp = client.get(f"/api/query/{query_id}")
        assert poll_resp.status_code == 200
        poll_data = poll_resp.json()
        if poll_data["status"] == "completed":
            completed = True
            final_poll = poll_data
            break
        time.sleep(0.1)

    assert completed is True
    assert final_poll["response"] is not None
    assert len(final_poll["sources"]) > 0
    assert len(final_poll["agent_tasks"]) >= 4

    # 4. Verify Workspace Query History
    history_resp = client.get(f"/api/workspaces/{ws_id}/queries")
    assert history_resp.status_code == 200
    assert history_resp.json()["total"] == 1


def test_sync_query_mode_in_debug(client):
    """Test synchronous query mode (?sync=true) when DEBUG=True."""
    ws_resp = client.post("/api/workspaces", json={"name": "Sync Query Workspace"})
    ws_id = ws_resp.json()["id"]

    settings.DEBUG = True
    q_payload = {
        "workspace_id": ws_id,
        "question": "Explain P&ID valve configurations for Pump P-101.",
    }
    resp = client.post("/api/query?sync=true", json=q_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["response"] is not None


def test_sync_query_rejected_when_not_debug(client):
    """Test sync query mode returns 400 when DEBUG=False."""
    ws_resp = client.post("/api/workspaces", json={"name": "Production Mode Workspace"})
    ws_id = ws_resp.json()["id"]

    settings.DEBUG = False
    try:
        q_payload = {
            "workspace_id": ws_id,
            "question": "Production test question",
        }
        resp = client.post("/api/query?sync=true", json=q_payload)
        assert resp.status_code == 400
        assert "restricted to debug" in resp.json()["detail"].lower()
    finally:
        settings.DEBUG = True


def test_startup_zombie_query_recovery(db_session):
    """Test recover_zombie_queries transitions stuck processing queries into failed."""
    ws = Workspace(name="Zombie Test Workspace")
    db_session.add(ws)
    db_session.commit()

    zombie_query = Query(
        workspace_id=ws.id,
        question="Unfinished zombie query before server crash",
        status="processing",
    )
    db_session.add(zombie_query)
    db_session.commit()
    db_session.refresh(zombie_query)

    # Execute recovery sweep
    recovered_count = recover_zombie_queries(db_session)
    assert recovered_count >= 1

    # Verify query status transitioned to failed
    db_session.refresh(zombie_query)
    assert zombie_query.status == "failed"
    assert "Server restarted" in zombie_query.error_message
