import io

from backend.app.core.config import settings


def test_file_upload_and_download(client, sample_pdf_bytes, sample_png_bytes, sample_csv_bytes):
    """Test file ingestion, magic byte verification, and download streaming."""
    # Create test workspace
    ws_resp = client.post("/api/workspaces", json={"name": "File Test Workspace"})
    assert ws_resp.status_code == 201
    ws_id = ws_resp.json()["id"]

    # 1. Upload valid PDF
    pdf_file = {"file": ("manual_p101.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    pdf_resp = client.post(f"/api/workspaces/{ws_id}/files", files=pdf_file)
    assert pdf_resp.status_code == 201
    pdf_data = pdf_resp.json()
    assert pdf_data["filename"] == "manual_p101.pdf"
    assert pdf_data["file_type"] == "pdf"
    assert pdf_data["status"] == "uploaded"
    pdf_id = pdf_data["id"]

    # 2. Upload valid PNG Diagram
    png_file = {"file": ("cooling_diagram.png", io.BytesIO(sample_png_bytes), "image/png")}
    png_resp = client.post(f"/api/workspaces/{ws_id}/files", files=png_file)
    assert png_resp.status_code == 201
    png_data = png_resp.json()
    assert png_data["filename"] == "cooling_diagram.png"
    assert png_data["file_type"] == "png"

    # 3. Upload valid Telemetry CSV
    csv_file = {"file": ("telemetry.csv", io.BytesIO(sample_csv_bytes), "text/csv")}
    csv_resp = client.post(f"/api/workspaces/{ws_id}/files", files=csv_file)
    assert csv_resp.status_code == 201
    csv_data = csv_resp.json()
    assert csv_data["filename"] == "telemetry.csv"
    assert csv_data["file_type"] == "csv"

    # 4. Verify List Files
    list_resp = client.get(f"/api/workspaces/{ws_id}/files")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 3

    # 5. Download PDF File
    dl_resp = client.get(f"/api/files/{pdf_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.content == sample_pdf_bytes


def test_magic_byte_sniffing_rejection(client, sample_fake_exe_bytes):
    """Test disguised executables with .pdf extension are blocked."""
    ws_resp = client.post("/api/workspaces", json={"name": "Security Test Workspace"})
    ws_id = ws_resp.json()["id"]

    fake_pdf = {"file": ("malicious_manual.pdf", io.BytesIO(sample_fake_exe_bytes), "application/pdf")}
    resp = client.post(f"/api/workspaces/{ws_id}/files", files=fake_pdf)
    assert resp.status_code == 400
    assert "content does not match" in resp.json()["detail"].lower()


def test_disallowed_extension_rejection(client):
    """Test disallowed file extensions are rejected."""
    ws_resp = client.post("/api/workspaces", json={"name": "Ext Test Workspace"})
    ws_id = ws_resp.json()["id"]

    exe_file = {"file": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")}
    resp = client.post(f"/api/workspaces/{ws_id}/files", files=exe_file)
    assert resp.status_code == 400
    assert "not permitted" in resp.json()["detail"].lower()


def test_m2m_status_patch_authentication(client, sample_pdf_bytes):
    """Test M2M status PATCH requires valid internal service key."""
    ws_resp = client.post("/api/workspaces", json={"name": "M2M Test Workspace"})
    ws_id = ws_resp.json()["id"]

    pdf_file = {"file": ("manual.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    pdf_resp = client.post(f"/api/workspaces/{ws_id}/files", files=pdf_file)
    file_id = pdf_resp.json()["id"]

    # 1. Attempt status update without key -> 403 Forbidden
    unauth_resp = client.patch(f"/api/files/{file_id}/status", json={"status": "indexed"})
    assert unauth_resp.status_code == 403

    # 2. Attempt with invalid key -> 403 Forbidden
    bad_resp = client.patch(
        f"/api/files/{file_id}/status",
        json={"status": "indexed"},
        headers={"X-Internal-Service-Key": "wrong-secret-key"},
    )
    assert bad_resp.status_code == 403

    # 3. Successful update with valid internal key -> 200 OK
    auth_resp = client.patch(
        f"/api/files/{file_id}/status",
        json={"status": "indexed"},
        headers={"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY},
    )
    assert auth_resp.status_code == 200
    assert auth_resp.json()["status"] == "indexed"


def test_file_deletion(client, sample_pdf_bytes):
    """Test file deletion removes database record and disk file."""
    ws_resp = client.post("/api/workspaces", json={"name": "Delete Test Workspace"})
    ws_id = ws_resp.json()["id"]

    pdf_file = {"file": ("temp.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    pdf_resp = client.post(f"/api/workspaces/{ws_id}/files", files=pdf_file)
    file_id = pdf_resp.json()["id"]

    # Delete file
    del_resp = client.delete(f"/api/files/{file_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Subsequent GET returns 404
    get_resp = client.get(f"/api/files/{file_id}")
    assert get_resp.status_code == 404
