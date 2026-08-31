"""
Benchmark Suite for INDUSAI-X.
Runs automated evaluation passes over test queries and measures accuracy & latency.
"""

import time
from typing import List, Dict, Any
from indusai.evaluation.metrics import Evaluator, EvaluationMetrics
from indusai.agents.graph import IndusAIGraph

class BenchmarkRunner:
    """Runs automated benchmarks over sample queries and aggregates statistics."""

    def __init__(self, graph: IndusAIGraph):
        self.graph = graph

    def run_benchmark(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        latencies = []

        for case in test_cases:
            query = case["query"]
            role = case.get("role", "maintenance_engineer")
            gt_ids = case.get("ground_truth_chunks", [])

            t0 = time.perf_counter()
            state = self.graph.run(user_query=query, user_role=role)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

            metrics = Evaluator.evaluate_response(state, ground_truth_chunk_ids=gt_ids, retrieval_latency_ms=elapsed_ms)
            results.append({
                "query": query,
                "role": role,
                "metrics": metrics.model_dump(),
                "guardrail_status": state.get("guardrail_status")
            })

        avg_recall = sum(r["metrics"]["recall_at_k"] for r in results) / max(1, len(results))
        avg_groundedness = sum(r["metrics"]["groundedness_score"] for r in results) / max(1, len(results))
        avg_citation = sum(r["metrics"]["citation_correctness"] for r in results) / max(1, len(results))
        avg_unsupported = sum(r["metrics"]["unsupported_claim_rate"] for r in results) / max(1, len(results))
        avg_latency = sum(latencies) / max(1, len(latencies))

        summary = {
            "total_test_cases": len(results),
            "avg_recall_at_5": round(avg_recall, 4),
            "avg_groundedness_score": round(avg_groundedness, 4),
            "avg_citation_correctness": round(avg_citation, 4),
            "avg_unsupported_claim_rate": round(avg_unsupported, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "individual_results": results
        }
        return summary
