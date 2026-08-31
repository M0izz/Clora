"""
Tests for Air-Gap Network Sentinel and Sovereignty Certificate Generator.
"""

import os
import unittest

from security.network_proof import AirGapSentinel


class TestNetworkProof(unittest.TestCase):

    def setUp(self):
        self.test_log = "tests/test_airgap_proof.jsonl"
        self.test_cert = "tests/test_airgap_cert.txt"
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_cert):
            os.remove(self.test_cert)
        self.sentinel = AirGapSentinel(self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_cert):
            os.remove(self.test_cert)

    def test_audit_cycle_execution(self):
        entry = self.sentinel.audit_cycle("TEST_CYCLE_1")
        self.assertEqual(entry["seq"], 0)
        self.assertTrue(entry["is_airgapped"])
        self.assertEqual(entry["external_sockets_count"], 0)
        self.assertTrue(os.path.exists(self.test_log))

    def test_generate_sovereignty_certificate(self):
        self.sentinel.audit_cycle("EXTRACT")
        self.sentinel.audit_cycle("QUERY_DUCKDB")
        self.sentinel.audit_cycle("GENERATE_DOCX")

        cert_path = self.sentinel.generate_sovereignty_certificate(self.test_cert)
        self.assertTrue(os.path.exists(cert_path))
        with open(cert_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("INDUSAI-X: SOVEREIGN ON-PREMISE AI WORKBENCH", content)
        self.assertIn("VERIFIED AIR-GAPPED", content)
        self.assertIn("External Sockets Found: 0", content)


if __name__ == "__main__":
    unittest.main()
