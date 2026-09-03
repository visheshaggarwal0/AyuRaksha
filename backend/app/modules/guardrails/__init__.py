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
        r"\bsmuggle\b",
        r"\bsecretly\b.{0,30}\b(export|transfer|harvest|take|send|move)\b",
        r"bypass\s+(nba|sbb|national\s+biodiversity\s+authority)",
        r"bypass\s+[\w\s]{0,12}\s*(prior\s+approval|approval|benefit\s+sharing)",
        r"(loophole|loopholes|trick|tricks|hack|hacks|shortcut|workaround|evade|evading|dodge|get\s+around|way\s+around)\s+.{0,40}\b(nba|sbb|approval|regulation|law|biodiversity|authority)\b",
        r"avoid\s+(prior\s+approval|benefit\s+sharing|nba|sbb|paying)",
        r"circumvent\s+(bda|biological\s+diversity\s+act|approval|nba|sbb)",
        r"export\s+without\s+(nba|approval|permission)\s+(knowledge|notice|clearance)",
        r"(how\s+can\s+i|how\s+to|ways?\s+to)\s+.{0,40}(without|avoiding)\s+(nba|sbb)\s*(knowledge|approval|permission|clearance)",
        r"(forge|fake|counterfeit)\s+(an?\s+)?(sbb|nba|certificate|license|permit)",
        r"without\s+(being\s+)?(caught|detected|noticed)",
        r"illegal(ly)?\s+(harvest|supply|export|sell)",
        r"pakda\s+na\s+jaoon",
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
