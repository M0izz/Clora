"""
Evidence Verifier and Hallucination Firewall for INDUSAI-X.
"""

import re
from typing import List, Tuple

from pydantic import BaseModel, Field

from backend.rag.evidence import Evidence, EvidencePack
from backend.verification.claim_extractor import Claim

CAUSAL_CONNECTIVES = [
    r"\bcaused\b",
    r"\bcausing\b",
    r"\bbecause\b",
    r"\bdue to\b",
    r"\bled to\b",
    r"\bleading to\b",
    r"\bresulted in\b",
    r"\bresulting in\b",
    r"\btriggered\b",
    r"\bbrought about\b",
    r"\bconsequently\b",
    r"\bas a direct result of\b",
]
CAUSAL_REGEX = re.compile("|".join(CAUSAL_CONNECTIVES), re.IGNORECASE)

STOPWORDS = {
    "the",
    "a",
    "an",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "over",
    "under",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "and",
    "or",
    "but",
}


class VerificationResult(BaseModel):
    claims: List[Claim] = Field(default_factory=list)
    overall_confidence: float = 0.0
    overall_status: str = "VERIFIED"
    verified_count: int = 0
    hedged_count: int = 0
    unsupported_count: int = 0
    blocked_count: int = 0


class EvidenceVerifier:
    """Verifies claims against evidence and downgrades unsupported causal leaps."""

    def __init__(
        self, supported_threshold: float = 0.85, partially_supported_threshold: float = 0.60
    ):
        self.supported_threshold = supported_threshold
        self.partially_supported_threshold = partially_supported_threshold

    def calculate_evidence_support(
        self, claim_text: str, evidence: List[Evidence]
    ) -> Tuple[float, List[str], bool]:
        if not evidence:
            return 0.0, [], False

        claim_clean = claim_text.lower().rstrip(".").strip()
        all_claim_words = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", claim_clean)
        claim_content_words = set(w for w in all_claim_words if w not in STOPWORDS)
        has_causal_phrase = bool(CAUSAL_REGEX.search(claim_clean))

        best_score = 0.0
        matching_ids = []
        causal_confirmed_in_text = False

        for ev in evidence:
            ev_text = ev.content.lower()
            ev_words = set(re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", ev_text))
            if not claim_content_words:
                continue

            overlap = len(claim_content_words.intersection(ev_words)) / len(claim_content_words)
            words_list = [w for w in all_claim_words if w not in STOPWORDS]
            if len(words_list) >= 2:
                for i in range(len(words_list) - 1):
                    bigram = f"{words_list[i]} {words_list[i + 1]}"
                    if bigram in ev_text:
                        overlap += 0.15

            overlap = min(1.0, overlap)
            if overlap > best_score:
                best_score = overlap
            if overlap >= 0.40:
                matching_ids.append(ev.chunk_id)

            if has_causal_phrase and any(re.search(c, ev_text) for c in CAUSAL_CONNECTIVES):
                if overlap > 0.70:
                    causal_confirmed_in_text = True

        is_unsupported_causal_leap = has_causal_phrase and not causal_confirmed_in_text
        return round(best_score, 4), matching_ids, is_unsupported_causal_leap

    def contradicts_evidence(self, claim_text: str, evidence: List[Evidence]) -> Tuple[bool, str]:
        claim_lower = claim_text.lower()
        for ev in evidence:
            ev_lower = ev.content.lower()
            claim_says_normal = (
                "within normal" in claim_lower
                or "was normal" in claim_lower
                or "remained normal" in claim_lower
            ) and not ("exceeded" in claim_lower or "abnormal" in claim_lower)
            if claim_says_normal and (
                "exceeded normal" in ev_lower or "abnormal" in ev_lower or "high" in ev_lower
            ):
                if any(
                    k in claim_lower and k in ev_lower
                    for k in ["temperature", "pressure", "vibration"]
                ):
                    return (
                        True,
                        f"Claim asserts normal conditions while {ev.source_document} reports abnormal limits.",
                    )

            if (
                "no contamination" in claim_lower or "zero contamination" in claim_lower
            ) and "contamination" in ev_lower:
                return (
                    True,
                    f"Claim asserts no contamination while {ev.source_document} reports contamination.",
                )
        return False, ""

    def verify_claim(self, claim: Claim, evidence_pack: EvidencePack) -> Claim:
        evidence_list = evidence_pack.evidence
        if not evidence_list:
            claim.status = "INSUFFICIENT_EVIDENCE"
            claim.confidence = 0.0
            claim.reasoning = "No evidence found in repository."
            return claim

        is_contradicted, contra_desc = self.contradicts_evidence(claim.text, evidence_list)
        if is_contradicted:
            claim.status = "CONTRADICTED"
            claim.confidence = 0.1
            claim.reasoning = contra_desc
            return claim

        support_score, matched_ids, has_causal_leap = self.calculate_evidence_support(
            claim.text, evidence_list
        )
        claim.evidence_ids = matched_ids
        claim.has_causal_leap = has_causal_leap

        if has_causal_leap:
            claim.status = "PARTIALLY_SUPPORTED"
            claim.confidence = min(0.65, support_score)
            claim.reasoning = "Correlation observed in documents, but direct causation is not explicitly confirmed."
            claim.hedged_text = self._generate_hedged_text(claim.text, evidence_list)
        elif support_score >= self.supported_threshold:
            claim.status = "SUPPORTED"
            claim.confidence = support_score
            claim.reasoning = "Strictly corroborated by authorized document evidence."
        elif support_score >= self.partially_supported_threshold:
            claim.status = "PARTIALLY_SUPPORTED"
            claim.confidence = support_score
            claim.reasoning = "Partially supported by available context."
            claim.hedged_text = self._generate_hedged_text(claim.text, evidence_list)
        else:
            claim.status = "INSUFFICIENT_EVIDENCE"
            claim.confidence = support_score
            claim.reasoning = "Cannot be verified from available evidence."

        return claim

    def verify_all(self, claims: List[Claim], evidence_pack: EvidencePack) -> VerificationResult:
        verified_claims = [self.verify_claim(c, evidence_pack) for c in claims]
        supported = sum(1 for c in verified_claims if c.status == "SUPPORTED")
        hedged = sum(1 for c in verified_claims if c.status == "PARTIALLY_SUPPORTED")
        unsupported = sum(
            1 for c in verified_claims if c.status in ["UNSUPPORTED", "INSUFFICIENT_EVIDENCE"]
        )
        blocked = sum(1 for c in verified_claims if c.status == "CONTRADICTED")

        avg_conf = sum(c.confidence for c in verified_claims) / max(1, len(verified_claims))
        overall_status = "VERIFIED"
        if blocked > 0:
            overall_status = "CONTRADICTED_CONTENT_DETECTED"
        elif unsupported > 0 and supported == 0:
            overall_status = "UNVERIFIED"
        elif hedged > 0:
            overall_status = "PARTIALLY_VERIFIED"

        return VerificationResult(
            claims=verified_claims,
            overall_confidence=round(avg_conf, 4),
            overall_status=overall_status,
            verified_count=supported,
            hedged_count=hedged,
            unsupported_count=unsupported,
            blocked_count=blocked,
        )

    def _generate_hedged_text(self, claim_text: str, evidence: List[Evidence]) -> str:
        facts = []
        for ev in evidence:
            ev_lower = ev.content.lower()
            if (
                "bearing temperature" in ev_lower
                or "overheating" in ev_lower
                or "temperature exceeded" in ev_lower
            ):
                facts.append("abnormal bearing temperature")
            if "lubrication" in ev_lower or "contamination" in ev_lower:
                facts.append("lubrication contamination")
            if "vibration" in ev_lower:
                facts.append("elevated vibration levels")

        facts = list(dict.fromkeys(facts))
        if len(facts) >= 2:
            return f"Available records indicate {' and '.join(facts)}. These factors may be related; however, the documents do not conclusively establish direct causation."
        elif facts:
            return f"Available records note {facts[0]}; however, definitive root causation cannot be confirmed from available evidence alone."
        return "Available records provide partial correlation; however, the documents do not conclusively establish direct causation."
