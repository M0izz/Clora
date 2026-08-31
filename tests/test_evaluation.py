"""
Unit tests for Evaluation Metrics and Benchmarks.
"""

import pytest

from indusai.evaluation.metrics import Evaluator
from indusai.verification.schemas import VerificationStatus


def test_evaluation_metrics_computation():
    retrieved_chunk_ids = ["c1", "c2", "c3", "c4", "c5"]
    gt_chunk_ids = ["c1", "c2", "c9"]

    recall = Evaluator.calculate_recall_at_k(retrieved_chunk_ids, gt_chunk_ids, k=5)
    assert recall == pytest.approx(0.6667, 0.01)

    citations = [{"source": "Pump_Report.pdf", "page": 14}, {"source": "SOP_P101.pdf", "page": 2}]
    available_evidence = [
        {"source": "Pump_Report.pdf", "page": 14},
        {"source": "SOP_P101.pdf", "page": 2},
        {"source": "Unused.pdf", "page": 1},
    ]
    citation_score = Evaluator.calculate_citation_correctness(citations, available_evidence)
    assert citation_score == 1.0

    claims = [
        {"status": VerificationStatus.SUPPORTED.value},
        {"status": VerificationStatus.PARTIALLY_SUPPORTED.value},
        {"status": VerificationStatus.INSUFFICIENT_EVIDENCE.value},
    ]
    groundedness = Evaluator.calculate_groundedness(claims)
    assert groundedness == pytest.approx(0.6667, 0.01)

    unsupported_rate = Evaluator.calculate_unsupported_claim_rate(claims)
    assert unsupported_rate == pytest.approx(0.3333, 0.01)

