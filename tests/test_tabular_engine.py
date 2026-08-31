"""
Tests for Tabular DuckDB Engine and AST-level SQL Security Guard.
"""

import os
import unittest
from data_intelligence.tabular_engine import TabularEngine, SQLSecurityError


class TestTabularEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TabularEngine()
        self.csv_path = os.path.join("samples", "equipment_maintenance.csv")
        self.engine.load_csv("telemetry", self.csv_path)

    def tearDown(self):
        self.engine.close()

    def test_valid_select_queries(self):
        # Test simple SELECT
        rows, md = self.engine.query("SELECT equipment_id, status FROM telemetry LIMIT 5")
        self.assertEqual(len(rows), 5)
        self.assertIn("equipment_id", rows[0])
        self.assertIn("| equipment_id", md)

        # Test Aggregations & Math
        rows, md = self.engine.query(
            "SELECT equipment_id, ROUND(AVG(vibration_mms), 2) AS avg_vib, MAX(bearing_temp_c) AS max_temp "
            "FROM telemetry GROUP BY equipment_id HAVING AVG(vibration_mms) > 4.0"
        )
        self.assertGreater(len(rows), 0)
        self.assertEqual(rows[0]["equipment_id"], "P-102A")

    def test_block_multi_statement_injection(self):
        with self.assertRaises(SQLSecurityError) as ctx:
            self.engine.query("SELECT * FROM telemetry; DROP TABLE telemetry;")
        self.assertIn("Multiple SQL statements detected", str(ctx.exception))

    def test_block_dml_and_ddl_operations(self):
        dangerous_queries = [
            "DROP TABLE telemetry",
            "DELETE FROM telemetry WHERE status='CRITICAL'",
            "UPDATE telemetry SET status='NORMAL'",
            "INSERT INTO telemetry VALUES ('2026-08-31', 'P-999', 'Fake', 'CDU', 1.0, 50.0, 10.0, 100.0, 'NORMAL', '2026-01-01')",
            "CREATE TABLE hack AS SELECT 1"
        ]
        for q in dangerous_queries:
            with self.subTest(query=q):
                with self.assertRaises(SQLSecurityError):
                    self.engine.query(q)

    def test_block_filesystem_and_unauthorized_functions(self):
        with self.assertRaises(SQLSecurityError) as ctx:
            self.engine.query("SELECT read_csv('secret.csv')")
        self.assertTrue(isinstance(ctx.exception, SQLSecurityError))

    def test_block_unregistered_tables(self):
        with self.assertRaises(SQLSecurityError) as ctx:
            self.engine.query("SELECT * FROM non_existent_table")
        self.assertIn("is not in the list of registered in-memory tables", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
