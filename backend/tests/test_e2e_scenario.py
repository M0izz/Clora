import io
import time

from app.core.config import settings


def test_pump_p101_industrial_demo_scenario(
    client, sample_pdf_bytes, sample_png_bytes, sample_csv_bytes
):
    """
    End-to-End Industrial Hackathon Demo Scenario:
    1. Create Workspace 'Refinery Unit 4'
    2. Upload Maintenance Manual (PDF), P&ID Schematic (PNG), Vibration Telemetry (CSV)
    3. Update file indexing status via internal worker M2M callback
    4. Dispatch Root-Cause Analysis Query: 'What caused pump P-101 bearing failure?'
    5. Poll until Completed
    6. Verify multi-modal citations (PDF page, P&ID grid, CSV telemetry) & sub-agent execution traces
    7. Verify forensic audit log trail
    """
    # ---------------------------------------------------------
    # Step 1: Create Workspace
    # ---------------------------------------------------------
    ws_resp = client.post(
        "/api/workspaces",
        json={
            "name": "Refinery Unit 4",
            "description": "Crude Distillation Unit & P-101 Pumping Circuit",
        },
        headers={"X-User-Id": "lead_engineer_01"},
    )
    assert ws_resp.status_code == 201
    ws = ws_resp.json()
    ws_id = ws["id"]
    assert ws["name"] == "Refinery Unit 4"

    # ---------------------------------------------------------
    # Step 2: Ingest Multi-Modal Assets
    # ---------------------------------------------------------
    # 2a. Maintenance Manual PDF
    pdf_upload = client.post(
        f"/api/workspaces/{ws_id}/files",
        files={"file": ("Pump_P101_Maintenance_Manual.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        headers={"X-User-Id": "lead_engineer_01"},
    )
    assert pdf_upload.status_code == 201
    pdf_id = pdf_upload.json()["id"]

    # 2b. P&ID Schematic PNG
    png_upload = client.post(
        f"/api/workspaces/{ws_id}/files",
        files={"file": ("PID_Cooling_Water_Circuit_P101.png", io.BytesIO(sample_png_bytes), "image/png")},
        headers={"X-User-Id": "lead_engineer_01"},
    )
    assert png_upload.status_code == 201
    png_id = png_upload.json()["id"]

    # 2c. Vibration Telemetry CSV
    csv_upload = client.post(
        f"/api/workspaces/{ws_id}/files",
        files={"file": ("Pump_P101_Vibration_Telemetry.csv", io.BytesIO(sample_csv_bytes), "text/csv")},
        headers={"X-User-Id": "lead_engineer_01"},
    )
    assert csv_upload.status_code == 201
    csv_id = csv_upload.json()["id"]

    # Verify all 3 files listed in workspace
    files_resp = client.get(f"/api/workspaces/{ws_id}/files")
    assert files_resp.status_code == 200
    assert files_resp.json()["total"] == 3

    # ---------------------------------------------------------
    # Step 3: M2M Worker Status Callback (Transition to 'indexed')
    # ---------------------------------------------------------
    for fid in [pdf_id, png_id, csv_id]:
        patch_resp = client.patch(
            f"/api/files/{fid}/status",
            json={"status": "indexed"},
            headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "indexed"

    # ---------------------------------------------------------
    # Step 4: Dispatch Industrial Investigation Query
    # ---------------------------------------------------------
    query_resp = client.post(
        "/api/query",
        json={
            "workspace_id": ws_id,
            "question": "What caused pump P-101 bearing failure?",
        },
        headers={"X-User-Id": "lead_engineer_01"},
    )
    assert query_resp.status_code == 202
    q_data = query_resp.json()
    query_id = q_data["query_id"]
    assert q_data["status"] == "processing"
    assert q_data["poll_url"] == f"/api/query/{query_id}"

    # ---------------------------------------------------------
    # Step 5: Poll Live Status until Completion
    # ---------------------------------------------------------
    completed = False
    final_result = None
    for _ in range(30):
        poll = client.get(f"/api/query/{query_id}")
        assert poll.status_code == 200
        data = poll.json()
        if data["status"] == "completed":
            completed = True
            final_result = data
            break
        time.sleep(0.1)

    assert completed is True, "Query orchestration should complete within timeout"

    # ---------------------------------------------------------
    # Step 6: Verify Multi-Modal Citations & Sub-Agent Traces
    # ---------------------------------------------------------
    response_text = final_result["response"]
    assert "Pump P-101" in response_text
    assert "104.2°C" in response_text or "bearing" in response_text.lower()
    assert "CV-104B" in response_text or "vibration" in response_text.lower()

    # Verify Citations
    sources = final_result["sources"]
    assert len(sources) >= 3

    # Check for PDF Manual citation
    pdf_citation = next((s for s in sources if s["file_type"] == "pdf"), None)
    assert pdf_citation is not None
    assert pdf_citation["page"] == 42
    assert pdf_citation["file_available"] is True
    assert "Section 4.3" in pdf_citation["snippet_or_data"]

    # Check for CSV Telemetry citation
    csv_citation = next((s for s in sources if s["file_type"] == "csv"), None)
    assert csv_citation is not None
    assert csv_citation["file_available"] is True
    assert csv_citation["snippet_or_data"]["peak_value"] == 104.2

    # Check for Vision P&ID citation
    vision_citation = next((s for s in sources if s["file_type"] == "image"), None)
    assert vision_citation is not None
    assert "CV-104B" in vision_citation["snippet_or_data"]
    assert vision_citation["file_available"] is True

    # Verify Agent Task Execution Traces
    tasks = final_result["agent_tasks"]
    task_names = [t["agent_name"] for t in tasks]
    assert "triage_agent" in task_names
    assert "document_agent" in task_names
    assert "tabular_agent" in task_names
    assert "vision_agent" in task_names
    assert "synthesis_agent" in task_names

    for t in tasks:
        assert t["status"] == "completed"
        assert t["completed_at"] is not None

    # ---------------------------------------------------------
    # Step 7: Verify Forensic Audit Trail
    # ---------------------------------------------------------
    audit_resp = client.get(f"/api/audit?workspace_id={ws_id}")
    assert audit_resp.status_code == 200
    audit_items = audit_resp.json()["items"]
    assert len(audit_items) >= 5

    actions_recorded = [a["action"] for a in audit_items]
    assert "CREATE_WORKSPACE" in actions_recorded
    assert "UPLOAD_FILE" in actions_recorded
    assert "UPDATE_FILE_STATUS" in actions_recorded
    assert "DISPATCH_QUERY" in actions_recorded
    assert "COMPLETE_QUERY" in actions_recorded

    for item in audit_items:
        assert item["workspace_label"] == "Refinery Unit 4"
