"""
Tests for FastAPI REST Router Endpoints.
"""

import os
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from data_intelligence.api_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestApiRouter(unittest.TestCase):

    def test_extract_document_endpoint(self):
        pdf_path = os.path.join("samples", "sample_inspection_digital.pdf")
        response = client.post("/api/member6/extract-document", json={
            "pdf_path": pdf_path,
            "actor_id": "eng_1",
            "role": "Plant_Engineer"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["primary_method"], "native_text")
        self.assertGreater(len(data["chunks"]), 0)

    def test_query_tabular_endpoint(self):
        response = client.post("/api/member6/query-tabular", json={
            "sql_query": "SELECT equipment_id, status FROM telemetry LIMIT 3",
            "actor_id": "eng_1",
            "role": "Plant_Engineer"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["rows"]), 3)

    def test_query_tabular_security_rejection(self):
        response = client.post("/api/member6/query-tabular", json={
            "sql_query": "SELECT 1; DROP TABLE telemetry;",
            "actor_id": "bad_actor",
            "role": "Plant_Engineer"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("SQL Security Violation", response.json()["detail"])

    def test_knowledge_graph_blast_radius_endpoint(self):
        response = client.post("/api/member6/knowledge-graph/blast-radius", json={
            "equipment_id": "P-102A"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["equipment_id"], "P-102A")
        self.assertEqual(data["standby_available"]["standby_id"], "P-102B")

    def test_knowledge_graph_cytoscape_endpoint(self):
        response = client.get("/api/member6/knowledge-graph/cytoscape")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    def test_audit_verify_endpoint(self):
        response = client.get("/api/member6/audit-trail/verify")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_valid", data)

    def test_airgap_proof_endpoint(self):
        response = client.get("/api/member6/airgap-proof")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_airgapped"])


if __name__ == "__main__":
    unittest.main()
