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

    def _evidence_support(self, terms: set, evidence: Evidence) -> float:
        """Computes normalized term-overlap support of a claim's terms against a single evidence."""
        source_text = (
            f"{evidence.source_title} {evidence.section_number} "
            f"{evidence.verbatim_text} {evidence.authority or ''}".lower()
        )
        if not terms:
            return 0.0
        matches = sum(1 for t in terms if t in source_text)
        return matches / len(terms)

    def verify_claims(
        self,
        answer: str,
        evidence: List[Evidence],
        support_threshold: float = 0.20
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
            supporting_markers = []

            if markers:
                # Only check evidence that the answer explicitly cited.
                for m in markers:
                    ev = evidence_lookup.get(m)
                    if ev:
                        score = self._evidence_support(terms, ev)
                        if score > max_support:
                            max_support = score
                        # Any cited evidence with non-trivial overlap is recorded as a supporter.
                        if score >= support_threshold:
                            supporting_markers.append(m)
            else:
                # Markers omitted: scan top candidates for proximate grounding.
                for idx, ev in enumerate(evidence[:3], start=1):
                    score = self._evidence_support(terms, ev)
                    if score > max_support:
                        max_support = score
                    if score >= support_threshold:
                        supporting_markers.append(idx)

            is_supported = max_support >= support_threshold
            claim_record = {
                "claim": sent_clean,
                "support_score": round(max_support, 3),
                "cited_markers": markers,
                "supporting_markers": sorted(set(supporting_markers)),
            }

            if is_supported:
                verified_claims.append(claim_record)
            else:
                unsupported_claims.append(claim_record)

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
