"""
AyuRaksha Evaluation Module
Implements IEvaluationModule for sentence-level claim verification,
grounding rate calculation, and multi-dimensional calibrated confidence scoring.
"""
import re
from typing import List, Dict, Any
from app.modules.interfaces import IEvaluationModule
from app.models.domain import Evidence, RetrievalResult, Confidence, ConfidenceLevel


class ModularEvaluationEngine(IEvaluationModule):
    """Decomposes legal responses into claims and evaluates factual grounding."""

    LEGAL_STOPWORDS = {
        "shall", "which", "under", "where", "there", "their", "these", "those",
        "section", "rule", "rules", "order", "proviso", "provided", "herein",
        "therein", "thereof", "act", "acts", "schedule", "first"
    }

    def verify_claims(
        self,
        answer: str,
        evidence: List[Evidence]
    ) -> Dict[str, Any]:
        if not answer or not evidence:
            return {
                "grounding_rate": 0.0,
                "verified_claims": [],
                "unsupported_claims": [],
                "status": "UNVERIFIED"
            }

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if len(s.strip()) > 15]
        verified_claims = []
        unsupported_claims = []

        evidence_lookup = {idx + 1: ev for idx, ev in enumerate(evidence)}

        for sent in sentences:
            markers = [int(m) for m in re.findall(r"\[(\d+)\]", sent)]
            sent_clean = re.sub(r"\[\d+\]", "", sent).strip()
            terms = {
                w for w in re.findall(r"\b[a-zA-Z]{4,}\b", sent_clean.lower())
                if w not in self.LEGAL_STOPWORDS
            }

            if not terms:
                continue

            max_support = 0.0
            if markers:
                for m in markers:
                    ev = evidence_lookup.get(m)
                    if ev:
                        source_text = f"{ev.source_title} {ev.section_number} {ev.verbatim_text}".lower()
                        matches = sum(1 for t in terms if t in source_text)
                        score = matches / len(terms)
                        if score > max_support:
                            max_support = score
            else:
                # Scan across all evidence if markers were omitted
                for ev in evidence[:3]:
                    source_text = f"{ev.source_title} {ev.section_number} {ev.verbatim_text}".lower()
                    matches = sum(1 for t in terms if t in source_text)
                    score = matches / len(terms)
                    if score > max_support:
                        max_support = score

            if max_support >= 0.20:
                verified_claims.append({"claim": sent_clean, "support_score": round(max_support, 3)})
            else:
                unsupported_claims.append({"claim": sent_clean, "support_score": round(max_support, 3)})

        total = len(verified_claims) + len(unsupported_claims)
        grounding_rate = (len(verified_claims) / total) if total > 0 else 1.0

        return {
            "grounding_rate": round(grounding_rate, 3),
            "verified_claims": verified_claims,
            "unsupported_claims": unsupported_claims,
            "status": "PASS" if grounding_rate >= 0.70 else "FLAGGED"
        }

    def compute_confidence(
        self,
        retrieval_result: RetrievalResult,
        claim_verification: Dict[str, Any]
    ) -> Confidence:
        grounding = claim_verification.get("grounding_rate", 0.8)
        candidate_count = len(retrieval_result.candidates)

        caveats = []
        if candidate_count < 2:
            caveats.append("Limited statutory provisions found for specific combination.")
        if grounding < 0.75:
            caveats.append("Portions of synthesis rely on general regulatory principles.")

        score = round(min(1.0, (grounding * 0.7) + (min(1.0, candidate_count / 3.0) * 0.3)), 3)

        if score >= 0.80:
            level = ConfidenceLevel.HIGH
        elif score >= 0.55:
            level = ConfidenceLevel.MODERATE
        else:
            level = ConfidenceLevel.LOW

        return Confidence(
            level=level,
            score=score,
            grounding_rate=grounding,
            caveats=caveats
        )


evaluation_module = ModularEvaluationEngine()
