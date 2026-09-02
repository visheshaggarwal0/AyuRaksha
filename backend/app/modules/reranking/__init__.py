"""
AyuRaksha Reranking Module
Implements IRerankingModule using statutory authority hierarchy weighting and exact-section boosts.
"""
import re
from typing import List
from app.modules.interfaces import IRerankingModule
from app.models.domain import Evidence


class LegalAuthorityReranker(IRerankingModule):
    """Authority-weighted reranker for legal and regulatory provisions."""

    AUTHORITY_WEIGHT = 0.25
    EXACT_SECTION_BOOST = 0.20

    def rerank(
        self,
        query: str,
        candidates: List[Evidence],
        top_k: int = 5
    ) -> List[Evidence]:
        if not candidates:
            return []

        q_lower = query.lower()
        query_terms = [t for t in re.findall(r"\w+", q_lower) if len(t) >= 3]

        scored_candidates = []
        for cand in candidates:
            base_score = cand.relevance_score

            # 1. Authority Hierarchy Bonus (5 = Acts/Treaties, 4 = Rules, 3 = Guidelines)
            auth_level = cand.authority_level
            authority_bonus = (auth_level / 5.0) * self.AUTHORITY_WEIGHT

            # 2. Term overlap in text
            text = cand.verbatim_text.lower()
            matches = sum(1 for term in query_terms if term in text)
            term_score = (matches / len(query_terms) * 0.20) if query_terms else 0.0

            # 3. Exact section boost
            sec_num = cand.section_number.lower()
            exact_boost = 0.0
            if sec_num and sec_num in q_lower:
                exact_boost = self.EXACT_SECTION_BOOST

            # 4. Domain Intent Alignment Bonus
            domain_boost = 0.0
            src_id = (cand.source_id or "").upper()
            
            # Classification, ASU, Proprietary, and Ayurveda Aahara questions
            if any(k in q_lower for k in ["classify", "classification", "classical", "proprietary", "aahara", "fssai", "license", "licensing"]):
                if "DRUGS_COSMETICS" in src_id:
                    domain_boost += 0.25
                elif "FSSAI" in src_id or "AAHARA" in src_id:
                    domain_boost += 0.25
                elif "TRADE_MARKS" in src_id and not any(tm in q_lower for tm in ["trademark", "brand", "mark", "logo", "class 5"]):
                    domain_boost -= 0.35  # Suppress trademark goods classes for drug regulatory questions

            # Patentability and Traditional Knowledge questions
            if any(k in q_lower for k in ["patent", "invent", "novelty", "3(p)", "3(e)", "tkdl"]):
                if "PATENTS" in src_id:
                    domain_boost += 0.25

            # Biodiversity and ABS questions
            if any(k in q_lower for k in ["biodiversity", "abs", "nba", "sbb", "biological", "benefit sharing"]):
                if "BIOLOGICAL_DIVERSITY" in src_id or "ABS" in src_id:
                    domain_boost += 0.25

            final_score = max(0.0, min(1.0, base_score + authority_bonus + term_score + exact_boost + domain_boost))
            cand_copy = cand.model_copy()
            cand_copy.relevance_score = round(final_score, 4)
            scored_candidates.append(cand_copy)

        scored_candidates.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_candidates[:top_k]


reranking_module = LegalAuthorityReranker()
