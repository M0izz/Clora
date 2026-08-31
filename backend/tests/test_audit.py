def test_audit_logging_and_snapshot_permanence(client):
    """
    Test forensic audit trail:
    Verifies that when a workspace is deleted, historical audit logs
    retain intelligible workspace labels via snapshot resolution ('Refinery Unit 4 (deleted)').
    """
    # 1. Create Workspace
    ws_resp = client.post("/api/workspaces", json={"name": "Refinery Unit 4"})
    assert ws_resp.status_code == 201
    ws_id = ws_resp.json()["id"]

    # 2. Query Audit Logs (workspace exists)
    audit_resp = client.get(f"/api/audit?workspace_id={ws_id}")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert audit_data["total"] >= 1
    create_entry = next(e for e in audit_data["items"] if e["action"] == "CREATE_WORKSPACE")
    assert create_entry["workspace_label"] == "Refinery Unit 4"

    # 3. Delete Workspace
    del_resp = client.delete(f"/api/workspaces/{ws_id}")
    assert del_resp.status_code == 200

    # 4. Query Audit Logs Again (workspace deleted)
    audit_after = client.get(f"/api/audit?workspace_id={ws_id}")
    assert audit_after.status_code == 200
    entries_after = audit_after.json()["items"]
    assert len(entries_after) >= 2  # CREATE_WORKSPACE and DELETE_WORKSPACE

    for entry in entries_after:
        assert entry["workspace_label"] == "Refinery Unit 4 (deleted)"


def test_audit_log_filtering(client):
    """Test filtering audit logs by action and user_id."""
    ws_resp = client.post(
        "/api/workspaces",
        json={"name": "Audit Filter Test"},
        headers={"X-User-Id": "engineer_alice"},
    )
    ws_id = ws_resp.json()["id"]

    # Filter by user_id
    user_audit = client.get("/api/audit?user_id=engineer_alice")
    assert user_audit.status_code == 200
    assert user_audit.json()["total"] >= 1
    assert all(e["user_id"] == "engineer_alice" for e in user_audit.json()["items"])

    # Filter by action
    action_audit = client.get("/api/audit?action=CREATE_WORKSPACE")
    assert action_audit.status_code == 200
    assert action_audit.json()["total"] >= 1
    assert all(e["action"] == "CREATE_WORKSPACE" for e in action_audit.json()["items"])
