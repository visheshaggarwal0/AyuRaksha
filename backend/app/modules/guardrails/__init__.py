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
        r"\bsecretly\b.{0,30}\b(export|transfer|harvest|take|send|move|funnel)\b",
        r"bypass\s+(nba|sbb|national\s+biodiversity\s+authority)",
        r"bypass\s+[\w\s]{0,25}\s*(prior\s+approval|approval|benefit\s+sharing|authority)",
        r"(shell\s+company|offshore\s+entity|foreign\s+front)\b.{0,60}\b(bypass|evade|funnel|secretly|nba)\b",
        r"(loophole|loopholes|trick|tricks|hack|hacks|shortcut|workaround|evade|evading|dodge|get\s+around|way\s+around)\s+.{0,40}\b(nba|sbb|approval|regulation|law|biodiversity|authority)\b",
        r"avoid\s+(prior\s+approval|benefit\s+sharing|nba|sbb|paying)",
        r"circumvent\s+(bda|biological\s+diversity\s+act|approval|nba|sbb)",
        r"export\s+without\s+(nba|approval|permission)\s+(knowledge|notice|clearance)",
        r"(how\s+can\s+i|how\s+to|ways?\s+to)\s+.{0,40}(without|avoiding)\s+(nba|sbb)\s*(knowledge|approval|permission|clearance)",
        r"(forge|fake|counterfeit)\s+(an?\s+)?(sbb|nba|certificate|license|permit|origin)",
        r"without\s+(being\s+)?(caught|detected|noticed|forest\s+department)",
        r"without\s+forest\s+department\s+detection",
        r"illegal(ly)?\s+(harvest|supply|export|sell|poach|collect)",
        r"harvest\s+.{0,40}(endangered|national\s+park|sanctuary).{0,30}(night|secretly|without\s+detection)",
        r"pakda\s+na\s+jaoon",
    ]

    MAGIC_REMEDIES_PATTERNS = [
        r"guaranteed?\s+(\d+%\s+|100\s+percent\s+|permanent\s+)?cure\s+for\s+(cancer|diabetes|hiv|aids|epilepsy|blindness|paralysis)",
        r"100%\s+(permanent\s+)?cure\s+for\s+(cancer|diabetes|paralysis|aids|blindness)",
        r"permanent\s+cure\s+for\s+(cancer|aids|blindness|diabetes|hiv)",
        r"miracle\s+remedy\s+for",
        r"cure\s+(type-2\s+diabetes|cancer|aids)\s+in\s+\d+\s+days",
    ]

    CLINICAL_EMERGENCY_PATTERNS = [
        r"\binject\b.{0,30}\b(vein|blood|artery|intravenous|iv)\b",
        r"(severe|acute)\s+(high\s+fever|chest\s+pain|shortness\s+of\s+breath|convulsion)",
        r"\bchest\s+pain\b.{0,30}\b(inject|vein|acute)\b",
    ]

    def evaluate_safety(
        self,
        query: str,
        jurisdiction: str = "IN"
    ) -> Optional[AbstentionReason]:
        q_lower = query.lower()

        # 1. Clinical emergency / acute intervention check
        for pat in self.CLINICAL_EMERGENCY_PATTERNS:
            if re.search(pat, q_lower):
                return AbstentionReason(
                    code=AbstentionCode.OUT_OF_REGULATORY_SCOPE,
                    description="Inquiry describes an acute medical emergency or hazardous parenteral administration requiring immediate allopathic hospital care.",
                    remedial_action="Seek emergency medical treatment immediately at an accredited hospital or casualty department."
                )

        # 2. Biopiracy circumvention check
        for pat in self.BIOPIRACY_BYPASS_PATTERNS:
            if re.search(pat, q_lower):
                return AbstentionReason(
                    code=AbstentionCode.BIOPIRACY_CIRCUMVENTION_DETECTED,
                    description="Inquiry requests instructions to evade statutory Access and Benefit Sharing (ABS) mandates or poach protected biological resources.",
                    remedial_action="Apply for prior approval via NBA Form I (Commercial Utilization) or NBA Form III (IP Rights) under BDA 2002."
                )

        # 3. Magic remedies & advertisement prohibition
        for pat in self.MAGIC_REMEDIES_PATTERNS:
            if re.search(pat, q_lower):
                return AbstentionReason(
                    code=AbstentionCode.DRUGS_MAGIC_REMEDIES_VIOLATION,
                    description="Claims of guaranteed cures for scheduled diseases violate Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.",
                    remedial_action="Reformulate therapeutic indications to supportive or management claims with State Ayush SLA approval."
                )

        return None


guardrails_module = ModularGuardrailEngine()
