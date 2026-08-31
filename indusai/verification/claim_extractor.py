"""
Claim Extraction Engine for INDUSAI-X.
Deconstructs draft LLM syntheses into verifiable atomic factual statements.
"""

import re
from typing import List, Tuple
from indusai.verification.schemas import Claim, VerificationStatus

CITATION_REGEX = re.compile(r'\[(?:Source:\s*([^,\]]+)(?:,\s*Page\s*(\d+))?|chunk_[a-zA-Z0-9]+|\d+)\]', re.IGNORECASE)
CHUNK_ID_REGEX = re.compile(r'chunk_[a-zA-Z0-9_]+', re.IGNORECASE)

class ClaimExtractor:
    """Extracts atomic factual claims and inline citation tags from raw LLM responses."""

    def extract_claims(self, text: str) -> List[Claim]:
        if not text or not text.strip():
            return []

        claims: List[Claim] = []
        lines = text.splitlines()

        skip_keywords = {
            "answer", "verified findings", "analysis", "uncertainty",
            "evidence", "confidence:", "none", "n/a", "findings", "observations"
        }

        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("─") or line_str.startswith("="):
                continue

            cleaned = re.sub(r'^[•\-\*\d+\.]\s*', '', line_str).strip()
            cleaned_lower = cleaned.lower().rstrip(":")

            if cleaned_lower in skip_keywords or cleaned_lower.startswith("confidence:"):
                continue

            # Skip lines that are purely citation references like "[1] Document.pdf — Page 14"
            if re.match(r'^\[\d+\]\s+.*—\s*Page\s*\d+', cleaned, re.IGNORECASE):
                continue

            # Strip citation tags from within the claim text
            clean_fact = re.sub(r'\[(?:Source:\s*[^,\]]+(?:,\s*Page\s*\d+)?|\d+|chunk_[a-zA-Z0-9_]+)\]', '', cleaned).strip()
            if not clean_fact or len(clean_fact) < 12:
                continue

            evidence_ids = list(set(CHUNK_ID_REGEX.findall(line_str)))

            # Sentence split if line contains multiple sentences
            sentences = re.split(r'(?<=[.!?])\s+', clean_fact)
            for s in sentences:
                s_clean = s.strip().rstrip(".")
                if len(s_clean) > 10:
                    s_lower = s_clean.lower()
                    if s_lower in skip_keywords or s_lower.startswith("confidence"):
                        continue
                    claims.append(Claim(
                        text=s_clean,
                        evidence_ids=evidence_ids,
                        status=VerificationStatus.INSUFFICIENT_EVIDENCE.value,
                        confidence=0.0
                    ))

        return claims
