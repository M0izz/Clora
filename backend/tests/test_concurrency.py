import concurrent.futures
import time


def test_concurrent_queries_and_audit_writes(client):
    """
    Stress test verifying SQLite WAL mode and busy timeout handles
    simultaneous query dispatches and audit log reads/writes without lock contention.
    """
    # 1. Create workspace
    ws_resp = client.post("/api/workspaces", json={"name": "Concurrency Stress Unit"})
    assert ws_resp.status_code == 201
    ws_id = ws_resp.json()["id"]

    num_concurrent_queries = 8

    def submit_and_poll(idx: int):
        # Dispatch query
        resp = client.post(
            "/api/query",
            json={
                "workspace_id": ws_id,
                "question": f"Concurrent stress test inquiry #{idx}: evaluate cooling parameters",
            },
        )
        assert resp.status_code == 202
        query_id = resp.json()["query_id"]

        # Poll until complete
        for _ in range(30):
            poll_resp = client.get(f"/api/query/{query_id}")
            if poll_resp.status_code == 200 and poll_resp.json()["status"] == "completed":
                return True
            time.sleep(0.05)
        return False

    def query_audit_logs():
        # Read audit logs concurrently
        resp = client.get("/api/audit")
        return resp.status_code == 200

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        query_futures = [
            executor.submit(submit_and_poll, i) for i in range(num_concurrent_queries)
        ]
        audit_futures = [
            executor.submit(query_audit_logs) for _ in range(5)
        ]

        query_results = [f.result() for f in concurrent.futures.as_completed(query_futures)]
        audit_results = [f.result() for f in concurrent.futures.as_completed(audit_futures)]

    assert all(query_results), "All concurrent queries should complete successfully without SQLite lock errors"
    assert all(audit_results), "All concurrent audit queries should succeed"
