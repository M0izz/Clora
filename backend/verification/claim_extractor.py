"""
Claim extractor module for INDUSAI-X.
"""

import re
from typing import List

from pydantic import BaseModel, Field

CHUNK_ID_REGEX = re.compile(r"chunk_[a-zA-Z0-9_]+", re.IGNORECASE)


class Claim(BaseModel):
    text: str
    evidence_ids: List[str] = Field(default_factory=list)
    status: str = "INSUFFICIENT_EVIDENCE"  # SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE
    confidence: float = 0.0
    reasoning: str = ""
    has_causal_leap: bool = False
    hedged_text: str = ""


class ClaimExtractor:
    """Extracts verifiable atomic factual statements from draft synthesizer text."""

    def extract_claims(self, text: str) -> List[Claim]:
        if not text or not text.strip():
            return []

        claims: List[Claim] = []
        skip_keywords = {
            "answer",
            "verified findings",
            "analysis",
            "uncertainty",
            "evidence",
            "confidence:",
            "none",
            "n/a",
            "findings",
            "observations",
        }

        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("─") or line_str.startswith("="):
                continue

            cleaned = re.sub(r"^[•\-\*\d+\.]\s*", "", line_str).strip()
            cleaned_lower = cleaned.lower().rstrip(":")

            if cleaned_lower in skip_keywords or cleaned_lower.startswith("confidence:"):
                continue

            if re.match(r"^\[\d+\]\s+.*—\s*Page\s*\d+", cleaned, re.IGNORECASE):
                continue

            clean_fact = re.sub(
                r"\[(?:Source:\s*[^,\]]+(?:,\s*Page\s*\d+)?|\d+|chunk_[a-zA-Z0-9_]+)\]", "", cleaned
            ).strip()
            if not clean_fact or len(clean_fact) < 12:
                continue

            evidence_ids = list(set(CHUNK_ID_REGEX.findall(line_str)))
            sentences = re.split(r"(?<=[.!?])\s+", clean_fact)
            for s in sentences:
                s_clean = s.strip().rstrip(".")
                if len(s_clean) > 10:
                    s_lower = s_clean.lower()
                    if s_lower in skip_keywords or s_lower.startswith("confidence"):
                        continue
                    claims.append(
                        Claim(
                            text=s_clean,
                            evidence_ids=evidence_ids,
                            status="INSUFFICIENT_EVIDENCE",
                            confidence=0.0,
                        )
                    )

        return claims
