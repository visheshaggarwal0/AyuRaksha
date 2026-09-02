from typing import Dict, Any, List

class ConfidenceCalibrator:
    """
    Calibrates overall regulatory certainty score and synthesizes statutory caveats.
    """

    @classmethod
    def calibrate(
        cls,
        route: Dict[str, Any],
        retrieval_candidates: List[Dict[str, Any]],
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        grounding_rate = verification_result.get("grounding_rate", 0.8)
        top_retrieval_score = max([c.get("calibrated_score", 0.5) for c in retrieval_candidates]) if retrieval_candidates else 0.0

        # Weighted calculation
        composite_score = (top_retrieval_score * 0.50) + (grounding_rate * 0.50)
        composite_score = min(1.0, max(0.0, composite_score))

        if composite_score >= 0.75:
            level = "HIGH"
        elif composite_score >= 0.50:
            level = "MODERATE"
        else:
            level = "LOW"

        caveats = []
        jurisdiction = route.get("jurisdiction", "IN")
        if jurisdiction == "CROSS_BORDER":
            caveats.append("Cross-border compliance requires independent dual approvals: Indian NBA Biological Resource clearance and foreign import authorization (e.g. US FDA / EU THMPD).")

        intent = route.get("intent")
        if intent == "PATENTABILITY_ASSESSMENT":
            caveats.append("Patentability of modified herbal combinations strictly requires comparative clinical data demonstrating non-obvious synergistic efficacy under Section 3(e).")
        elif intent == "ABS_ASSESSMENT":
            caveats.append("Exemption under Section 40 applies only to raw commodities traded solely for culinary/conventional trade, not for proprietary extract manufacturing.")

        return {
            "confidence_score": round(composite_score, 3),
            "confidence_level": level,
            "caveats": caveats
        }
