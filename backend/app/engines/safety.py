import re
from typing import Dict, Any, Tuple

class SafetyGuardrailEngine:
    """
    Evaluates queries for:
    1. Illegal Biopiracy bypasses or smuggling of endangered biological resources.
    2. Deceptive/Illegal disease cure claims under Drugs & Magic Remedies Act.
    3. Safe Abstention triggers when authoritative sources are missing.
    4. Human Facilitator Case Brief generation.
    """

    ADVERSARIAL_BIOPIRACY_PATTERNS = [
        r"smuggle.*biological",
        r"bypass.*nba",
        r"bypass.*national biodiversity authority",
        r"without.*nba.*knowledge",
        r"hide.*foreign.*entity",
        r"secretly.*export.*endangered",
        r"avoid.*benefit.*sharing",
        r"bypass.*benefit[- ]*sharing",
        r"loophole",
        r"evade.*fees"
    ]

    DECEPTIVE_CURE_PATTERNS = [
        r"guaranteed.*cure.*cancer",
        r"100%.*cure.*diabetes",
        r"cure.*aids.*hiv",
        r"instant.*height.*increase"
    ]

    def evaluate_query_safety(self, query: str) -> Tuple[bool, str, str]:
        """
        Returns (is_safe, category, reason)
        """
        q_lower = query.lower()

        for pattern in self.ADVERSARIAL_BIOPIRACY_PATTERNS:
            if re.search(pattern, q_lower):
                return (
                    False,
                    "BIOPIRACY_VIOLATION",
                    "AyuRaksha strictly abstains from assisting in unauthorized extraction, concealment, or circumvention of the Biological Diversity Act, 2002."
                )

        for pattern in self.DECEPTIVE_CURE_PATTERNS:
            if re.search(pattern, q_lower):
                return (
                    False,
                    "MAGIC_REMEDIES_VIOLATION",
                    "Under the Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954, advertising cures for scheduled diseases is strictly prohibited."
                )

        return (True, "SAFE", "")

    def generate_facilitator_case_brief(
        self,
        user_query: str,
        jurisdiction: str,
        unresolved_issues: list,
        retrieved_sources: list
    ) -> Dict[str, Any]:
        """
        Generates structured 1-click case dossier for registered AYUSH IP facilitators.
        """
        return {
            "case_type": "HUMAN_FACILITATOR_ESCALATION",
            "jurisdiction": jurisdiction,
            "user_query": user_query,
            "status": "PENDING_FACILITATOR_REVIEW",
            "flagged_statutory_issues": unresolved_issues,
            "reviewed_authorities": [s.get("source_title", "") for s in retrieved_sources],
            "recommended_action": "Schedule case review with authorized AYUSH Patent/ABS Attorney."
        }
