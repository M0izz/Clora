from pathlib import Path
from app.core.config import settings


def test_workspace_crud(client):
    """Test full workspace lifecycle: create, get, list, and delete."""
    # 1. Create Workspace
    payload = {
        "name": "Refinery Unit 4",
        "description": "Distillation & Cooling Tower Infrastructure",
    }
    create_resp = client.post("/api/workspaces", json=payload)
    assert create_resp.status_code == 201
    ws = create_resp.json()
    assert ws["name"] == "Refinery Unit 4"
    assert ws["description"] == "Distillation & Cooling Tower Infrastructure"
    assert "id" in ws
    ws_id = ws["id"]

    # Verify physical workspace storage directory was created
    ws_dir = settings.STORAGE_DIR / "workspaces" / ws_id
    assert ws_dir.exists()

    # 2. Get Workspace Detail
    get_resp = client.get(f"/api/workspaces/{ws_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Refinery Unit 4"
    assert get_resp.json()["files_count"] == 0

    # 3. List Workspaces
    list_resp = client.get("/api/workspaces")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(item["id"] == ws_id for item in list_data["items"])

    # 4. Delete Workspace
    del_resp = client.delete(f"/api/workspaces/{ws_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 5. Verify 404 on Subsequent Get
    get_again = client.get(f"/api/workspaces/{ws_id}")
    assert get_again.status_code == 404


def test_workspace_not_found(client):
    """Test 404 returned for nonexistent workspace."""
    response = client.get("/api/workspaces/nonexistent-uuid-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
