"""
Verification Data Models and Enums for INDUSAI-X Hallucination Firewall.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class Claim(BaseModel):
    text: str
    evidence_ids: List[str] = Field(default_factory=list)
    status: str = VerificationStatus.INSUFFICIENT_EVIDENCE.value  # SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE
    confidence: float = 0.0
    reasoning: Optional[str] = None
    has_causal_leap: bool = False
    hedged_text: Optional[str] = None

class ContradictionReport(BaseModel):
    is_contradicted: bool = False
    conflicting_sources: List[str] = Field(default_factory=list)
    description: str = ""

class VerificationResult(BaseModel):
    claims: List[Claim] = Field(default_factory=list)
    overall_confidence: float = 0.0
    overall_status: str = "VERIFIED"
    contradictions: List[ContradictionReport] = Field(default_factory=list)
    verified_count: int = 0
    hedged_count: int = 0
    unsupported_count: int = 0
    blocked_count: int = 0
