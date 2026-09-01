"""
Prompt injection guard for INDUSAI-X.
Owns: sanitizing user inputs before they reach the LLM.
Coordinate with Member 6 (Data/Security) to update rules.

Usage:
    from app.ai.guard import sanitize, scan_prompt, PromptThreatLevel

    clean = sanitize(user_input)               # strips dangerous patterns
    result = scan_prompt(user_input)            # detailed threat analysis
    if result.level == PromptThreatLevel.HIGH:
        reject(result.reason)
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("indusai.guard")


class PromptThreatLevel(Enum):
    SAFE = "safe"
    LOW = "low"           # suspicious but probably fine
    MEDIUM = "medium"     # likely injection attempt
    HIGH = "high"         # definite injection — block it


@dataclass
class ScanResult:
    level: PromptThreatLevel
    original: str
    sanitized: str
    flags: list[str] = field(default_factory=list)
    reason: str = ""


# ---------------------------------------------------------------------------
# Injection patterns (add more as Member 6 identifies new attack vectors)
# ---------------------------------------------------------------------------

# Each tuple: (compiled_regex, flag_label, threat_level)
_PATTERNS: list[tuple[re.Pattern, str, PromptThreatLevel]] = [
    # Direct override attempts
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|context)",
                re.IGNORECASE),
     "override_instructions", PromptThreatLevel.HIGH),

    (re.compile(r"(disregard|forget|override|bypass)\s+(your|the|all|any)\s+(instructions?|rules?|guidelines?|system\s+prompt)",
                re.IGNORECASE),
     "override_instructions", PromptThreatLevel.HIGH),

    # Role-play hijacking
    (re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.IGNORECASE),
     "role_hijack", PromptThreatLevel.HIGH),

    (re.compile(r"(act|pretend|behave)\s+(as|like)\s+(a|an|if)\s+", re.IGNORECASE),
     "role_hijack", PromptThreatLevel.MEDIUM),

    # System prompt extraction
    (re.compile(r"(show|print|display|reveal|output|repeat)\s+(your|the)\s+(system\s+)?(prompt|instructions?|rules?|configuration)",
                re.IGNORECASE),
     "prompt_extraction", PromptThreatLevel.HIGH),

    (re.compile(r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions?|rules?)",
                re.IGNORECASE),
     "prompt_extraction", PromptThreatLevel.MEDIUM),

    # Delimiter injection (trying to break out of the user message)
    (re.compile(r"```\s*(system|assistant)\s*\n", re.IGNORECASE),
     "delimiter_injection", PromptThreatLevel.HIGH),

    (re.compile(r"<\s*/?\s*(system|instruction|rule)s?\s*>", re.IGNORECASE),
     "delimiter_injection", PromptThreatLevel.HIGH),

    # Encoding / obfuscation tricks
    (re.compile(r"(base64|rot13|hex)\s*(decode|encode|convert)", re.IGNORECASE),
     "encoding_trick", PromptThreatLevel.MEDIUM),

    # Data exfiltration via prompt
    (re.compile(r"(send|post|fetch|curl|wget|http[s]?://)", re.IGNORECASE),
     "exfiltration_attempt", PromptThreatLevel.LOW),

    # Excessive repetition (token-stuffing attacks)
    (re.compile(r"(.{2,}?)\1{10,}"),
     "repetition_attack", PromptThreatLevel.MEDIUM),
]

# Strings that are always stripped (replacement is empty string)
_STRIP_PATTERNS: list[re.Pattern] = [
    re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE),
    re.compile(r"\[INST\].*?\[/INST\]", re.IGNORECASE | re.DOTALL),
    re.compile(r"<<\s*SYS\s*>>.*?<<\s*/SYS\s*>>", re.IGNORECASE | re.DOTALL),
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|context)[\.\,\;]?", re.IGNORECASE),
    re.compile(r"(disregard|forget|override|bypass)\s+(your|the|all|any)\s+(instructions?|rules?|guidelines?|system\s+prompt)[\.\,\;]?", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_prompt(text: str) -> ScanResult:
    """
    Analyze a user prompt for injection attempts.
    Returns a ScanResult with threat level, flags, and sanitized text.
    """
    flags: list[str] = []
    worst_level = PromptThreatLevel.SAFE

    for pattern, label, level in _PATTERNS:
        if pattern.search(text):
            flags.append(label)
            if _LEVEL_ORDER.get(level, 0) > _LEVEL_ORDER.get(worst_level, 0):
                worst_level = level

    sanitized = _strip_dangerous(text)


    reason = ""
    if flags:
        reason = f"Detected: {', '.join(flags)}"
        logger.warning("Prompt flagged [%s]: %s — input preview: %s",
                       worst_level.value, reason, text[:100])

    return ScanResult(
        level=worst_level,
        original=text,
        sanitized=sanitized,
        flags=flags,
        reason=reason,
    )


def sanitize(text: str) -> str:
    """Quick sanitize — strip known dangerous patterns, return clean text."""
    return _strip_dangerous(text)


def is_safe(text: str) -> bool:
    """Return True if the prompt has no medium or high threat flags."""
    result = scan_prompt(text)
    return result.level in (PromptThreatLevel.SAFE, PromptThreatLevel.LOW)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_dangerous(text: str) -> str:
    """Remove known dangerous delimiters and injection markers."""
    result = text
    for pattern in _STRIP_PATTERNS:
        result = pattern.sub("", result)
    # Collapse excessive whitespace left by stripping
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


# ---------------------------------------------------------------------------
# Comparison helpers for PromptThreatLevel enum ordering
# ---------------------------------------------------------------------------

_LEVEL_ORDER = {
    PromptThreatLevel.SAFE: 0,
    PromptThreatLevel.LOW: 1,
    PromptThreatLevel.MEDIUM: 2,
    PromptThreatLevel.HIGH: 3,
}
