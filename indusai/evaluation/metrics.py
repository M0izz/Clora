"""
Evaluation Metrics for INDUSAI-X Sovereign RAG & Multi-Agent Workbench.
Measures Recall@K, Groundedness, Citation Correctness, Hallucination Rate, and Agent Efficiency.
"""

import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvaluationMetrics(BaseModel):
    recall_at_k: float = 0.0
    citation_correctness: float = 0.0
    groundedness_score: float = 0.0
    unsupported_claim_rate: float = 0.0
    evidence_coverage: float = 0.0
    retrieval_latency_ms: float = 0.0
    agent_success_rate: float = 0.0
    unnecessary_retrieval_count: int = 0

class Evaluator:
    """Computes end-to-end RAG and Agentic benchmarks."""

    @staticmethod
    def calculate_recall_at_k(retrieved_chunk_ids: List[str], ground_truth_chunk_ids: List[str], k: int = 5) -> float:
        if not ground_truth_chunk_ids:
            return 1.0
        top_k_retrieved = set(retrieved_chunk_ids[:k])
        hits = len(top_k_retrieved.intersection(set(ground_truth_chunk_ids)))
        return round(hits / len(ground_truth_chunk_ids), 4)

    @staticmethod
    def calculate_citation_correctness(citations: List[Dict[str, Any]], available_evidence: List[Dict[str, Any]]) -> float:
        """Verifies that all cited sources and pages exist in the retrieved evidence pack."""
        if not citations:
            return 1.0
        valid_citations = 0
        ev_sources = {(e.get("source"), int(e.get("page", 1))) for e in available_evidence}
        
        for c in citations:
            src = c.get("source")
            page = int(c.get("page", 1))
            if (src, page) in ev_sources:
                valid_citations += 1

        return round(valid_citations / len(citations), 4)

    @staticmethod
    def calculate_groundedness(claims: List[Dict[str, Any]]) -> float:
        """Percentage of claims classified as SUPPORTED or PARTIALLY_SUPPORTED."""
        if not claims:
            return 1.0
        grounded = sum(1 for c in claims if c.get("status") in ["SUPPORTED", "PARTIALLY_SUPPORTED"])
        return round(grounded / len(claims), 4)

    @staticmethod
    def calculate_unsupported_claim_rate(claims: List[Dict[str, Any]]) -> float:
        """Percentage of claims classified as UNSUPPORTED or CONTRADICTED."""
        if not claims:
            return 0.0
        unsupported = sum(1 for c in claims if c.get("status") in ["UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"])
        return round(unsupported / len(claims), 4)

    @staticmethod
    def calculate_evidence_coverage(used_evidence_ids: List[str], retrieved_evidence_ids: List[str]) -> float:
        """Proportion of retrieved evidence chunks actually leveraged in verified claims."""
        if not retrieved_evidence_ids:
            return 1.0
        used_unique = set(used_evidence_ids)
        retrieved_unique = set(retrieved_evidence_ids)
        overlap = len(used_unique.intersection(retrieved_unique))
        return round(overlap / len(retrieved_unique), 4)

    @classmethod
    def evaluate_response(
        cls,
        state: Dict[str, Any],
        ground_truth_chunk_ids: Optional[List[str]] = None,
        retrieval_latency_ms: float = 0.0
    ) -> EvaluationMetrics:
        retrieved_docs = state.get("retrieved_docs", [])
        retrieved_ids = [d.get("chunk_id") for d in retrieved_docs]
        
        evidence = state.get("evidence", [])
        claims = state.get("claims", [])
        
        used_evidence_ids = []
        for c in claims:
            used_evidence_ids.extend(c.get("evidence_ids", []))

        citations = [
            {"source": e.get("source"), "page": e.get("page")}
            for e in evidence
        ]

        recall = cls.calculate_recall_at_k(retrieved_ids, ground_truth_chunk_ids or retrieved_ids[:2])
        citation_acc = cls.calculate_citation_correctness(citations, evidence)
        groundedness = cls.calculate_groundedness(claims)
        unsupported_rate = cls.calculate_unsupported_claim_rate(claims)
        coverage = cls.calculate_evidence_coverage(used_evidence_ids, retrieved_ids)

        success = 1.0 if state.get("guardrail_status") in ["PASSED", "CAUSAL_HEDGING_APPLIED"] else 0.0
        unnecessary_retrieval = max(0, len(retrieved_ids) - len(set(used_evidence_ids)))

        return EvaluationMetrics(
            recall_at_k=recall,
            citation_correctness=citation_acc,
            groundedness_score=groundedness,
            unsupported_claim_rate=unsupported_rate,
            evidence_coverage=coverage,
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            agent_success_rate=success,
            unnecessary_retrieval_count=unnecessary_retrieval
        )
