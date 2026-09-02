import re
from typing import List, Dict, Any

class LegalAuthorityReranker:
    """
    Reranks statutory retrieval candidates using:
    1. Base retrieval support score (Dense similarity / BM25)
    2. Statutory Authority Hierarchy Bonus (Level 5 Act > Level 4 Rule > Level 3 Taxonomy)
    3. Lexical query-overlap boost
    4. Exact section match boost
    """

    AUTHORITY_WEIGHT = 0.20
    EXACT_SECTION_BOOST = 0.15

    @classmethod
    def rerank(cls, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        q_lower = query.lower()
        query_terms = [t for t in re.findall(r"\w+", q_lower) if len(t) >= 3]

        scored_candidates = []
        for cand in candidates:
            base_score = float(cand.get("support_score", cand.get("score", 0.5)))

            # 1. Authority Tier Weight
            auth_level = int(cand.get("authority_level", 3))
            authority_bonus = (auth_level / 5.0) * cls.AUTHORITY_WEIGHT

            # 2. Term overlap in text/heading
            text = cand.get("text", "").lower()
            heading = cand.get("heading", "").lower()
            sec_num = cand.get("section_number", "").lower()

            matches = sum(1 for term in query_terms if term in text or term in heading)
            term_score = (matches / len(query_terms) * 0.20) if query_terms else 0.0

            # 3. Exact section boost (e.g. user asked about "section 3(p)" and candidate is "section 3(p)")
            exact_boost = 0.0
            for term in ["3(p)", "3(e)", "3(a)", "3(h)", "158b", "section 3", "section 7"]:
                if term in q_lower and term in sec_num:
                    exact_boost = cls.EXACT_SECTION_BOOST
                    break

            final_score = min(1.0, base_score + authority_bonus + term_score + exact_boost)

            scored = dict(cand)
            scored["calibrated_score"] = round(final_score, 4)
            scored_candidates.append(scored)

        scored_candidates.sort(key=lambda x: x["calibrated_score"], reverse=True)
        return scored_candidates[:top_k]
