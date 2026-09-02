"""
AyuRaksha Guardrails Module
Implements IGuardrailModule for biopiracy prevention, magic remedies compliance,
and safe statutory abstention.
"""
import re
from typing import Optional
from app.modules.interfaces import IGuardrailModule
from app.models.domain import AbstentionReason, AbstentionCode


class ModularGuardrailEngine(IGuardrailModule):
    """Enforces statutory safety and proactive compliance boundaries."""

    BIOPIRACY_BYPASS_PATTERNS = [
        r"bypass\s+nba",
        r"avoid\s+(prior\s+approval|benefit\s+sharing|nba|sbb)",
        r"smuggle\s+biological\s+resources",
        r"circumvent\s+(bda|biological\s+diversity\s+act)",
        r"export\s+without\s+(nba|approval)",
    ]

    MAGIC_REMEDIES_PATTERNS = [
        r"guaranteed?\s+cure\s+for\s+(cancer|diabetes|hiv|aids|epilepsy)",
        r"100%\s+cure\s+for\s+(cancer|diabetes|paralysis)",
        r"miracle\s+remedy\s+for",
    ]

    def evaluate_safety(
        self,
        query: str,
        jurisdiction: str = "IN"
    ) -> Optional[AbstentionReason]:
        q_lower = query.lower()

        # 1. Biopiracy circumvention check
        for pat in self.BIOPIRACY_BYPASS_PATTERNS:
            if re.search(pat, q_lower):
                return AbstentionReason(
                    code=AbstentionCode.BIOPIRACY_CIRCUMVENTION_DETECTED,
                    description="Inquiry requests instructions to evade statutory Access and Benefit Sharing (ABS) mandates.",
                    remedial_action="Apply for prior approval via NBA Form I (Commercial Utilization) or NBA Form III (IP Rights) under BDA 2002."
                )

        # 2. Magic remedies & advertisement prohibition
        for pat in self.MAGIC_REMEDIES_PATTERNS:
            if re.search(pat, q_lower):
                return AbstentionReason(
                    code=AbstentionCode.DRUGS_MAGIC_REMEDIES_VIOLATION,
                    description="Claims of guaranteed cures for scheduled diseases violate Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.",
                    remedial_action="Reformulate therapeutic indications to supportive or management claims with State Ayush SLA approval."
                )

        return None


guardrails_module = ModularGuardrailEngine()
