import pytest
from fastapi.testclient import TestClient


def test_upload_file_triggers_ingestion_job(client: TestClient, sample_pdf_bytes: bytes):
    # 1. Create workspace
    ws_resp = client.post("/api/workspaces", json={"name": "Refinery Unit 101"})
    assert ws_resp.status_code == 201
    ws_id = ws_resp.json()["id"]

    # 2. Upload file via /api/files/upload
    upload_resp = client.post(
        "/api/files/upload",
        data={"workspace_id": ws_id},
        files={"file": ("manual.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert upload_resp.status_code == 201
    data = upload_resp.json()
    assert data["filename"] == "manual.pdf"
    assert "ingestion_job_id" in data
    job_id = data["ingestion_job_id"]
    assert job_id is not None

    # 3. Poll ingestion job status
    poll_resp = client.get(f"/api/ingestion/{job_id}")
    assert poll_resp.status_code == 200
    job_data = poll_resp.json()
    assert job_data["id"] == job_id
    assert job_data["workspace_id"] == ws_id
    assert job_data["status"] in ["QUEUED", "PROCESSING", "INDEXING", "COMPLETED"]

    # 4. List workspace ingestion jobs
    list_jobs_resp = client.get(f"/api/ingestion/workspace/{ws_id}")
    assert list_jobs_resp.status_code == 200
    assert list_jobs_resp.json()["total"] >= 1


def test_models_api_endpoints(client: TestClient):
    # 1. Get models status
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["runtime"] == "ollama"
    assert "active_model" in data
    assert data["hardware_mode"] == "LOCAL_AIR_GAPPED"

    # 2. Get active model
    active_resp = client.get("/api/models/active")
    assert active_resp.status_code == 200
    assert "active_model" in active_resp.json()

    # 3. Switch active model
    switch_resp = client.post("/api/models/select", json={"model_name": "llama3.2:3b"})
    assert switch_resp.status_code == 200
    assert switch_resp.json()["active_model"] == "llama3.2:3b"

    # Verify switch
    active_after = client.get("/api/models/active")
    assert active_after.json()["active_model"] == "llama3.2:3b"


def test_sovereignty_api_endpoints(client: TestClient):
    # 1. Check air-gap status
    resp = client.get("/api/sovereignty/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sovereign_mode"] == "AIR_GAPPED_VERIFIED"
    assert data["is_air_gapped"] is True

    # 2. Check certificate
    cert_resp = client.get("/api/sovereignty/certificate")
    assert cert_resp.status_code == 200
    assert "INDUSAI-X SOVEREIGNTY & AIR-GAP COMPLIANCE CERTIFICATE" in cert_resp.text


def test_agents_api_endpoint(client: TestClient):
    resp = client.get("/api/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert len(data["agents"]) >= 4
    agent_ids = [a["id"] for a in data["agents"]]
    assert "triage_agent" in agent_ids
    assert "document_agent" in agent_ids


def test_investigation_aliases(client: TestClient):
    # 1. Create workspace
    ws_resp = client.post("/api/workspaces", json={"name": "FCCU Hydrocracker Unit"})
    ws_id = ws_resp.json()["id"]

    # 2. Dispatch investigation
    inv_resp = client.post(
        "/api/investigations",
        json={"workspace_id": ws_id, "question": "Why did pump P-101 trip?"},
    )
    assert inv_resp.status_code == 202
    data = inv_resp.json()
    inv_id = data["query_id"]

    # 3. Poll investigation
    poll_resp = client.get(f"/api/investigations/{inv_id}")
    assert poll_resp.status_code == 200
    assert poll_resp.json()["query_id"] == inv_id
