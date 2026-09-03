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

    UNGROUNDED_LEGAL_ASSERTIONS = {
        "geographical indication", "gi tag", "automatic grant", "guaranteed approval",
        "criminal arrest", "blanket immunity", "exclusive copyright", "fda approved",
        "without regulatory oversight", "unconditional patent"
    }

    POLARITY_OPPOSITES = [
        ({"not patentable", "non-patentable", "shall not", "excludes", "prohibits", "barred"},
         {"freely patentable", "guaranteed patent", "unconditional grant", "permitted without approval"}),
        ({"mandatory approval", "prior approval required", "obligatory intimation"},
         {"exempted from approval", "no approval needed", "no compliance required", "freely exportable"})
    ]

    def _check_entailment_consistency(self, claim_text: str, evidence_text: str) -> bool:
        """
        Validates directional semantic entailment between a claim and statutory evidence.
        Catches unauthorized legal grants (e.g. asserting GI protection under Section 3(p))
        and polarity reversals (asserting permission where statute prohibits).
        """
        c_low = claim_text.lower()
        e_low = evidence_text.lower()

        # 1. Catch ungrounded high-stakes assertions
        for assertion in self.UNGROUNDED_LEGAL_ASSERTIONS:
            if assertion in c_low and assertion not in e_low:
                return False

        # 2. Catch polarity reversals
        for neg_set, pos_set in self.POLARITY_OPPOSITES:
            claim_has_pos = any(p in c_low for p in pos_set)
            evidence_has_neg = any(n in e_low for n in neg_set)
            if claim_has_pos and evidence_has_neg:
                return False

        return True

    def _evidence_support(self, terms: set, claim_text: str, evidence: Evidence) -> float:
        """Computes semantic entailment and normalized term-overlap support of a claim against a single evidence."""
        source_text = (
            f"{evidence.source_title} {evidence.section_number} "
            f"{evidence.verbatim_text} {evidence.authority or ''}".lower()
        )
        if not terms:
            return 0.0

        # Enforce semantic entailment consistency
        if not self._check_entailment_consistency(claim_text, source_text):
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
                        score = self._evidence_support(terms, sent_clean, ev)
                        if score > max_support:
                            max_support = score
                        # Any cited evidence with non-trivial overlap is recorded as a supporter.
                        if score >= support_threshold:
                            supporting_markers.append(m)
            else:
                # Markers omitted: scan top candidates for proximate grounding.
                for idx, ev in enumerate(evidence[:3], start=1):
                    score = self._evidence_support(terms, sent_clean, ev)
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
