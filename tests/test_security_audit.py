"""
Tests for RBAC matrix, Thread-Safe Audit Logger, and Tamper-Evidence.
"""

import os
import json
import unittest
import threading
from security.rbac import check_permission, enforce_permission, PermissionDeniedError
from security.audit_trail import AuditLogger
from security.airgap_monitor import check_network_isolation


class TestSecurityAndAudit(unittest.TestCase):

    def setUp(self):
        self.test_log_path = "tests/test_audit_temp.jsonl"
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)
        self.logger = AuditLogger(self.test_log_path)

    def tearDown(self):
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_rbac_matrix_permissions(self):
        # Admin can do everything
        self.assertTrue(check_permission("Admin", "generate_approval_note"))
        self.assertTrue(check_permission("Admin", "view_audit_log"))

        # Plant Engineer
        self.assertTrue(check_permission("Plant_Engineer", "generate_approval_note"))
        self.assertFalse(check_permission("Plant_Engineer", "view_audit_log"))

        # Safety Officer
        self.assertTrue(check_permission("Safety_Officer", "run_ocr"))
        self.assertFalse(check_permission("Safety_Officer", "generate_approval_note"))

        # Operator (Read only)
        self.assertTrue(check_permission("Operator", "read_document"))
        self.assertFalse(check_permission("Operator", "run_ocr"))
        self.assertFalse(check_permission("Operator", "query_tabular"))

    def test_rbac_enforcement_raises_error(self):
        with self.assertRaises(PermissionDeniedError):
            enforce_permission("Operator", "generate_approval_note")

    def test_audit_logger_hash_chaining_and_monotonic_sequence(self):
        self.logger.log("user1", "Plant_Engineer", "read_document", "doc1.pdf")
        self.logger.log("user1", "Plant_Engineer", "query_tabular", "telemetry")
        self.logger.log("user2", "Admin", "generate_approval_note", "approval.docx")

        valid, line_no, msg = AuditLogger.verify_audit_trail(self.test_log_path)
        self.assertTrue(valid, msg)
        self.assertIsNone(line_no)

    def test_audit_tamper_detection(self):
        self.logger.log("user1", "Plant_Engineer", "read_document", "doc1.pdf")
        self.logger.log("user1", "Plant_Engineer", "query_tabular", "telemetry")
        self.logger.log("user2", "Admin", "generate_approval_note", "approval.docx")

        # Deliberately tamper with line 1 (second entry)
        with open(self.test_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        tampered_entry = json.loads(lines[1])
        tampered_entry["resource"] = "hacked_resource"
        lines[1] = json.dumps(tampered_entry) + "\n"

        with open(self.test_log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        valid, line_no, msg = AuditLogger.verify_audit_trail(self.test_log_path)
        self.assertFalse(valid)
        self.assertEqual(line_no, 1)
        self.assertIn("Tampering detected on line 1", msg)

    def test_thread_safe_concurrent_logging(self):
        def log_worker(worker_id):
            for i in range(10):
                self.logger.log(f"worker_{worker_id}", "Plant_Engineer", "query_tabular", f"query_{i}")

        threads = [threading.Thread(target=log_worker, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        valid, line_no, msg = AuditLogger.verify_audit_trail(self.test_log_path)
        self.assertTrue(valid, msg)

    def test_airgap_network_isolation_check(self):
        res = check_network_isolation()
        self.assertIn("is_airgapped", res)
        self.assertIn("status", res)
        self.assertTrue(res["is_airgapped"])


if __name__ == "__main__":
    unittest.main()
