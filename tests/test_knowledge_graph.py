"""
Tests for NetworkX Refinery Knowledge Graph Engine.
"""

import unittest
from data_intelligence.knowledge_graph import RefineryKnowledgeGraph


class TestKnowledgeGraph(unittest.TestCase):

    def setUp(self):
        self.kg = RefineryKnowledgeGraph()

    def test_default_topology_loaded(self):
        nodes = list(self.kg.graph.nodes)
        self.assertIn("P-102A", nodes)
        self.assertIn("CDU-1", nodes)
        self.assertIn("T-101", nodes)
        self.assertIn("SKF-23144", nodes)

    def test_blast_radius_downstream_calculation(self):
        # Downstream of P-102A: E-101 -> V-104 -> T-101 -> VDU
        blast_radius = self.kg.get_equipment_blast_radius("P-102A")
        self.assertGreater(len(blast_radius), 0)
        impacted_nodes = [item["node_id"] for item in blast_radius]
        self.assertIn("E-101", impacted_nodes)
        self.assertIn("T-101", impacted_nodes)

    def test_standby_equipment_discovery(self):
        standby = self.kg.get_standby_redundancy("P-102A")
        self.assertIsNotNone(standby)
        self.assertEqual(standby["standby_id"], "P-102B")

    def test_mitigation_and_spare_parts(self):
        mitigation = self.kg.get_mitigation_plan("P-102A")
        self.assertEqual(mitigation["equipment_id"], "P-102A")
        self.assertGreater(len(mitigation["failure_modes"]), 0)
        self.assertGreater(len(mitigation["required_parts"]), 0)
        part_ids = [p["part_id"] for p in mitigation["required_parts"]]
        self.assertIn("SKF-23144", part_ids)

    def test_export_triples_for_member5_rag(self):
        triples = self.kg.export_triples()
        self.assertGreater(len(triples), 0)
        # Check triple tuple format (Subject, Predicate, Object)
        self.assertEqual(len(triples[0]), 3)

    def test_export_cytoscape_json(self):
        cy_data = self.kg.export_cytoscape_json()
        self.assertIn("nodes", cy_data)
        self.assertIn("edges", cy_data)
        self.assertGreater(len(cy_data["nodes"]), 0)


if __name__ == "__main__":
    unittest.main()
