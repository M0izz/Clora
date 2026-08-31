"""
Refinery Equipment & Process Knowledge Graph Module using NetworkX.
INDUSAI-X / SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Features:
- Constructs structured topology and failure-mode knowledge graphs for refinery assets.
- Node entity types: Unit, Equipment, Component, Sensor, FailureMode, Mitigation.
- Relationship edges: LOCATED_IN, FEEDS_INTO, STANDBY_FOR, HAS_FAILURE_MODE, REQUIRES_PART, MONITORED_BY.
- Graph analytics: Upstream/downstream blast radius, standby redundancy analysis, root-cause path search.
- Export formats: Cytoscape/D3 JSON (for Member 1 UI), Triple List (for Member 5 RAG).
"""

import json
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple, Set


class RefineryKnowledgeGraph:
    """Industrial Knowledge Graph engine for refinery asset relationship reasoning."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_default_refinery_topology()

    def add_entity(self, entity_id: str, entity_type: str, properties: Optional[Dict[str, Any]] = None):
        """Adds a typed node to the knowledge graph."""
        props = properties or {}
        self.graph.add_node(entity_id, entity_type=entity_type, **props)

    def add_relationship(self, source_id: str, target_id: str, relation: str, properties: Optional[Dict[str, Any]] = None):
        """Adds a directed typed edge between entities."""
        props = properties or {}
        self.graph.add_edge(source_id, target_id, relation=relation, **props)

    def _build_default_refinery_topology(self):
        """Initializes standard MRPL CDU-1 process and equipment relationships."""
        # 1. Units
        self.add_entity("CDU-1", "PlantUnit", {"name": "Crude Distillation Unit 1", "capacity": "150,000 BPD"})
        self.add_entity("VDU", "PlantUnit", {"name": "Vacuum Distillation Unit", "capacity": "70,000 BPD"})
        self.add_entity("FCCU", "PlantUnit", {"name": "Fluidized Catalytic Cracking Unit"})

        # 2. Equipment
        self.add_entity("P-101A", "Pump", {"name": "Crude Booster Pump A", "criticality": "MEDIUM"})
        self.add_entity("P-101B", "Pump", {"name": "Crude Booster Pump B (Standby)", "criticality": "MEDIUM"})
        self.add_entity("P-102A", "Pump", {"name": "Main Crude Charge Pump A", "criticality": "HIGH"})
        self.add_entity("P-102B", "Pump", {"name": "Main Crude Charge Pump B (Standby)", "criticality": "HIGH"})
        self.add_entity("E-101", "HeatExchanger", {"name": "Crude Pre-Heat Train Exchanger", "criticality": "MEDIUM"})
        self.add_entity("T-101", "Column", {"name": "Atmospheric Distillation Column", "criticality": "CRITICAL"})
        self.add_entity("V-104", "Valve", {"name": "Atmospheric Column Feed Control Valve"})

        # 3. Components & Spares
        self.add_entity("SKF-23144", "SparePart", {"name": "Spherical Roller Bearing SKF 23144 CC/W33", "stock": 4})
        self.add_entity("JC-5620", "SparePart", {"name": "John Crane Type 5620 Cartridge Mechanical Seal", "stock": 2})

        # 4. Failure Modes & Mitigations
        self.add_entity("FM-BRG-SPALL", "FailureMode", {"name": "Drive-End Bearing Inner Race Spalling", "severity": "CRITICAL"})
        self.add_entity("FM-SEAL-LEAK", "FailureMode", {"name": "Mechanical Seal Hydrocarbon Leakage", "severity": "CRITICAL"})
        self.add_entity("MIT-OVERHAUL-P102A", "MitigationAction", {
            "procedure": "SOP-CDU-SEC-014",
            "est_downtime_hours": 18,
            "cost_inr": 285000
        })

        # 5. Connect Entities (Edges)
        # Unit containment
        for eq in ["P-101A", "P-101B", "P-102A", "P-102B", "E-101", "T-101", "V-104"]:
            self.add_relationship(eq, "CDU-1", "LOCATED_IN")

        # Process Flow / Blast Radius
        self.add_relationship("P-101A", "P-102A", "FEEDS_INTO")
        self.add_relationship("P-101B", "P-102B", "FEEDS_INTO")
        self.add_relationship("P-102A", "E-101", "FEEDS_INTO")
        self.add_relationship("P-102B", "E-101", "FEEDS_INTO")
        self.add_relationship("E-101", "V-104", "FEEDS_INTO")
        self.add_relationship("V-104", "T-101", "FEEDS_INTO")
        self.add_relationship("T-101", "VDU", "FEEDS_INTO")

        # Standby Pairings
        self.add_relationship("P-102B", "P-102A", "STANDBY_FOR")
        self.add_relationship("P-101B", "P-101A", "STANDBY_FOR")

        # Failure Mode Associations
        self.add_relationship("P-102A", "FM-BRG-SPALL", "HAS_FAILURE_MODE")
        self.add_relationship("FM-BRG-SPALL", "FM-SEAL-LEAK", "CAN_INDUCE")
        self.add_relationship("FM-BRG-SPALL", "MIT-OVERHAUL-P102A", "RESOLVED_BY")
        self.add_relationship("MIT-OVERHAUL-P102A", "SKF-23144", "REQUIRES_PART")
        self.add_relationship("MIT-OVERHAUL-P102A", "JC-5620", "REQUIRES_PART")

    def get_equipment_blast_radius(self, equipment_id: str) -> List[Dict[str, Any]]:
        """
        Finds all downstream process equipment and units affected if equipment fails.
        """
        if equipment_id not in self.graph:
            return []

        downstream_nodes = nx.descendants(self.graph, equipment_id)
        impact_list = []
        for n in downstream_nodes:
            node_data = self.graph.nodes[n]
            # Exclude failure modes and mitigations from physical process flow
            if node_data.get("entity_type") in ("PlantUnit", "Pump", "Column", "HeatExchanger", "Valve"):
                try:
                    path = nx.shortest_path(self.graph, equipment_id, n)
                    impact_list.append({
                        "node_id": n,
                        "entity_type": node_data.get("entity_type"),
                        "name": node_data.get("name"),
                        "hops": len(path) - 1,
                        "path": path
                    })
                except nx.NetworkXNoPath:
                    pass

        impact_list.sort(key=lambda x: x["hops"])
        return impact_list

    def get_standby_redundancy(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Finds active standby replacement unit for an equipment."""
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == "STANDBY_FOR" and v == equipment_id:
                standby_data = self.graph.nodes[u]
                return {
                    "standby_id": u,
                    "name": standby_data.get("name"),
                    "criticality": standby_data.get("criticality")
                }
        return None

    def get_mitigation_plan(self, equipment_id: str) -> Dict[str, Any]:
        """Returns root-cause failure mode, required spare parts, and SOP procedure."""
        failure_modes = []
        mitigations = []
        required_parts = []

        for _, target, data in self.graph.out_edges(equipment_id, data=True):
            if data.get("relation") == "HAS_FAILURE_MODE":
                fm_data = self.graph.nodes[target]
                failure_modes.append({"id": target, "name": fm_data.get("name"), "severity": fm_data.get("severity")})

                # Find mitigations for this failure mode
                for _, mit_target, mit_data in self.graph.out_edges(target, data=True):
                    if mit_data.get("relation") == "RESOLVED_BY":
                        mit_info = self.graph.nodes[mit_target]
                        mitigations.append({
                            "id": mit_target,
                            "procedure": mit_info.get("procedure"),
                            "cost_inr": mit_info.get("cost_inr"),
                            "downtime_hours": mit_info.get("est_downtime_hours")
                        })
                        # Find required parts
                        for _, part_target, part_data in self.graph.out_edges(mit_target, data=True):
                            if part_data.get("relation") == "REQUIRES_PART":
                                p_info = self.graph.nodes[part_target]
                                required_parts.append({
                                    "part_id": part_target,
                                    "name": p_info.get("name"),
                                    "stock_available": p_info.get("stock")
                                })

        return {
            "equipment_id": equipment_id,
            "failure_modes": failure_modes,
            "mitigations": mitigations,
            "required_parts": required_parts
        }

    def export_triples(self) -> List[Tuple[str, str, str]]:
        """Exports all knowledge graph triples (Subject, Predicate, Object) for Member 5 RAG."""
        triples = []
        for u, v, data in self.graph.edges(data=True):
            triples.append((u, data.get("relation", "CONNECTED_TO"), v))
        return triples

    def export_cytoscape_json(self) -> Dict[str, Any]:
        """Exports elements formatted for Cytoscape.js / D3 graph UI rendering."""
        nodes = []
        for n, data in self.graph.nodes(data=True):
            nodes.append({
                "data": {
                    "id": n,
                    "label": data.get("name", n),
                    "type": data.get("entity_type", "Entity"),
                    **data
                }
            })
        edges = []
        for idx, (u, v, data) in enumerate(self.graph.edges(data=True)):
            edges.append({
                "data": {
                    "id": f"e{idx}",
                    "source": u,
                    "target": v,
                    "label": data.get("relation", "CONNECTED_TO"),
                    **data
                }
            })
        return {"nodes": nodes, "edges": edges}
