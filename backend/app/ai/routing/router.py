import re
from typing import Dict, Any, Optional

class JurisdictionIntentRouter:
    """
    Jurisdiction-aware Intent Classifier.
    Enforces strict statutory jurisdiction boundaries:
    - IN: Indian domestic regime (Patents Act, BDA, DCA, FSSAI)
    - INT: International treaties & foreign jurisdictions (Nagoya Protocol, WIPO, US FDA, EMA)
    - CROSS_BORDER: Export compliance bridging Indian biological resources with foreign markets
    """

    INTENT_PATTERNS = [
        ("PATENTABILITY_ASSESSMENT", r"\b(patent|patentable|section 3p|section 3e|inventive step|prior art|novelty|tkdl check)\b"),
        ("ABS_ASSESSMENT", r"\b(abs|access and benefit sharing|biodiversity|nba|sbb|biological resource|prior intimation|form i|form iii|form 1|section 3|section 7)\b"),
        ("PRODUCT_CLASSIFICATION", r"\b(classical|proprietary|shastriya|anubhuta|fssai|ayurveda aahara|cosmetic|license|rule 158b|first schedule)\b"),
        ("EXPORT_ASSESSMENT", r"\b(export|cross-border|international|us fda|fda|thmpd|directive 2004/24/ec|germany|europe|tga)\b"),
        ("IP_TRADEMARK_GI", r"\b(trademark|trade mark|brand name|class 5|gi|geographical indication)\b"),
        ("GENERAL_RESEARCH", r".*")
    ]

    @classmethod
    def route(cls, query: str, requested_jurisdiction: Optional[str] = "IN") -> Dict[str, Any]:
        q_lower = query.lower()

        # 1. Determine Jurisdiction
        has_intl = bool(re.search(r"\b(us fda|fda|directive 2004/24/ec|thmpd|european union|europe|germany|wipo|pct|export|cross-border)\b", q_lower))
        has_india = bool(re.search(r"\b(india|indian|nba|sbb|ayush|fssai|patents act|bda|drugs and cosmetics|rule 158b|first schedule)\b", q_lower))

        if has_intl and has_india:
            jurisdiction = "CROSS_BORDER"
        elif has_intl:
            # International terms present. Honor an explicit CROSS_BORDER request; an
            # Indian-entity request (IN) implies an Indian-origin export scenario;
            # otherwise treat the query as an international-regime inquiry.
            if requested_jurisdiction == "CROSS_BORDER":
                jurisdiction = "CROSS_BORDER"
            elif requested_jurisdiction == "IN":
                jurisdiction = "CROSS_BORDER"
            else:
                jurisdiction = "INT"
        elif requested_jurisdiction in ["IN", "INT", "CROSS_BORDER"]:
            jurisdiction = requested_jurisdiction
        else:
            jurisdiction = "IN"

        # 2. Determine Intent
        intent = "GENERAL_RESEARCH"
        for candidate_intent, pattern in cls.INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                intent = candidate_intent
                break

        # 3. Detect Language
        detected_language = "sa" if bool(re.search(r"\b(samhita|dosha|rasayana|dravya|vitiation|ama|guna)\b", q_lower)) else "en"

        return {
            "jurisdiction": jurisdiction,
            "intent": intent,
            "detected_language": detected_language,
            "is_cross_border": jurisdiction == "CROSS_BORDER"
        }
