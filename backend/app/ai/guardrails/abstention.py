import re
from typing import Dict, Any, List, Optional

class AbstentionGate:
    """
    Evidence Sufficiency & Statutory Safety Gate.
    Determines whether AyuRaksha must safely abstain from speculation.
    """

    SAFETY_RULES = [
        (
            r"\b(bypass nba|circumvent sbb|smuggle|avoid benefit sharing|hide biological resource|export without approval)\b",
            "ADVERSARIAL_BIOPIRACY",
            "AyuRaksha cannot provide advice on circumventing statutory compliance under the Biological Diversity Act, 2002. Any access or commercial utilization of Indian biological resources without NBA approval or SBB prior intimation constitutes an offense under Section 55."
        ),
        (
            r"\b(cure cancer|cure aids|guaranteed cure diabetes|magical cure|100% cure)\b",
            "MAGIC_REMEDIES_VIOLATION",
            "AyuRaksha cannot validate claims of guaranteed cures for scheduled diseases. Under the Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 and FSSAI 2022 Regulation 5, disease cure claims for ASU drugs or Ayurveda Aahara are strictly prohibited without approved clinical trials."
        )
    ]

    MIN_EVIDENCE_THRESHOLD = 0.22

    @classmethod
    def evaluate(
        cls,
        query: str,
        candidates: List[Dict[str, Any]],
        route: Dict[str, Any]
    ) -> Dict[str, Any]:
        q_lower = query.lower()

        # 1. Statutory Adversarial Safety Check
        for pattern, rule_code, explanation in cls.SAFETY_RULES:
            if re.search(pattern, q_lower):
                return {
                    "should_abstain": True,
                    "reason_code": rule_code,
                    "explanation": explanation,
                    "facilitator_brief": cls._build_case_brief(query, rule_code, explanation, candidates)
                }

        # 2. Evidence Sufficiency Check
        if not candidates:
            explanation = "AyuRaksha could not retrieve authoritative statutory provisions matching your inquiry in the indexed repository."
            return {
                "should_abstain": True,
                "reason_code": "INSUFFICIENT_STATUTORY_EVIDENCE",
                "explanation": explanation,
                "facilitator_brief": cls._build_case_brief(query, "INSUFFICIENT_STATUTORY_EVIDENCE", explanation, [])
            }

        top_score = max([c.get("calibrated_score", c.get("support_score", 0)) for c in candidates])
        if top_score < cls.MIN_EVIDENCE_THRESHOLD:
            explanation = f"Statutory evidence retrieved has low relevance (score {top_score:.2f} < threshold {cls.MIN_EVIDENCE_THRESHOLD:.2f}). To prevent legal hallucination, AyuRaksha abstains from definitive assertion."
            return {
                "should_abstain": True,
                "reason_code": "LOW_CONFIDENCE_EVIDENCE",
                "explanation": explanation,
                "facilitator_brief": cls._build_case_brief(query, "LOW_CONFIDENCE_EVIDENCE", explanation, candidates)
            }

        return {
            "should_abstain": False,
            "reason_code": "EVIDENCE_SUFFICIENT",
            "explanation": "Authoritative evidence retrieved exceeds statutory confidence threshold.",
            "facilitator_brief": None
        }

    @staticmethod
    def _build_case_brief(query: str, code: str, explanation: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "case_query": query,
            "abstention_code": code,
            "statutory_risk": explanation,
            "recommended_next_steps": [
                "Consult an empaneled Ayurvedic Patent Attorney or State Licensing Authority (SLA)",
                "Submit a formal query to the National Biodiversity Authority (NBA) or relevant State Biodiversity Board (SBB)",
                "Conduct exhaustive prior art search directly in the CSIR Traditional Knowledge Digital Library (TKDL)"
            ],
            "related_statutory_frameworks": [
                c.get("source_title") for c in candidates[:3] if c.get("source_title")
            ]
        }
