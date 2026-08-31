"""
Industrial Query Expander for INDUSAI-X.
Handles technical equipment aliases, refinery terminology synonyms, and query relaxation.
"""

import re
from typing import List, Dict, Tuple, Optional

# Known MRPL Equipment Tag <-> Technical Descriptor mapping
EQUIPMENT_DESCRIPTOR_MAP = {
    "P-101": ["booster pump 101", "booster pump", "crude feed pump", "centrifugal pump p-101"],
    "P-102": ["slurry pump", "slurry circulation pump", "heavy oil pump p-102"],
    "K-201": ["wet gas compressor", "gas compressor k-201", "compressor 201"],
    "HEX-301": ["pre-heat exchanger", "crude exchanger hex-301", "heat exchanger 301"],
    "TK-502": ["naphtha storage tank", "storage tank 502", "tank tk-502"],
    "MOV-102": ["motor operated valve", "isolation valve 102", "emergency shutoff valve"],
    "FCV-204": ["flow control valve", "reflux valve 204", "valve fcv-204"]
}

# Refinery Technical Vocabulary Synonyms
TECHNICAL_SYNONYMS = {
    "overheat": ["temperature exceeded normal", "thermal excursion", "high bearing temperature", "overheating"],
    "fail": ["failure", "breakdown", "tripped", "shutdown", "rupture", "malfunction"],
    "contamination": ["particulate presence", "foreign debris", "degraded lube oil", "moisture ingress"],
    "leak": ["loss of containment", "seal leakage", "gasket blow-out"],
    "vibration": ["high harmonics", "elevated vibration levels", "shaft misalignment", "unbalance"]
}

EQUIPMENT_ID_REGEX = re.compile(r'\b(?:P|K|E|T|TK|V|C|R|HEX|MOV|FCV|PT|TT|LT|FT|D)-\d{2,4}[A-Z]?\b', re.IGNORECASE)

class IndustrialQueryExpander:
    """Expands ambiguous or colloquial queries into technical industrial search terms."""

    @classmethod
    def expand_query(cls, query: str) -> Tuple[str, List[str]]:
        """
        Returns (expanded_query_string, list_of_applied_expansions).
        """
        expansions_applied = []
        expanded_parts = [query]

        # 1. Expand equipment tags to full equipment names
        eq_tags = EQUIPMENT_ID_REGEX.findall(query)
        for tag in eq_tags:
            tag_upper = tag.upper()
            if tag_upper in EQUIPMENT_DESCRIPTOR_MAP:
                aliases = EQUIPMENT_DESCRIPTOR_MAP[tag_upper]
                expanded_parts.extend([a.title() for a in aliases[:2]])
                expansions_applied.append(f"Equipment tag '{tag_upper}' -> {aliases[:2]}")

        # Check reverse mapping: if query says "booster pump" but not P-101
        q_lower = query.lower()
        for tag, aliases in EQUIPMENT_DESCRIPTOR_MAP.items():
            if tag.lower() not in q_lower:
                for alias in aliases:
                    if alias in q_lower or alias.replace(" ", "") in q_lower.replace(" ", ""):
                        expanded_parts.append(tag)
                        expansions_applied.append(f"Descriptor '{alias}' -> Equipment tag '{tag}'")
                        break

        # 2. Expand technical synonyms
        for term, synonyms in TECHNICAL_SYNONYMS.items():
            if term in q_lower:
                for syn in synonyms[:2]:
                    if syn not in q_lower:
                        expanded_parts.append(syn)
                        expansions_applied.append(f"Synonym '{term}' -> '{syn}'")

        expanded_query = " ".join(dict.fromkeys(expanded_parts))
        return expanded_query, expansions_applied
