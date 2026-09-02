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
    EXACT_SECTION_BOOST = 0.20
    SUBSTANTIVE_LAW_BOOST = 0.18

    # Core statutory provisions that establish rights/bars (vs procedural filing sections)
    SUBSTANTIVE_PROVISIONS = {
        "3(p)": ["traditional", "ayurvedic", "herbal", "formulation", "knowledge", "herb"],
        "3(e)": ["formulation", "combining", "mixture", "admixture", "synergy", "aggregation"],
        "3(d)": ["derivative", "extract", "form", "efficacy", "nano", "enhancement"],
        "3(i)": ["method", "treatment", "cure", "administer", "disease", "patient"],
        "3(c)": ["naturally", "occurring", "plant", "isolate", "substance"],
        "10(4)": ["disclose", "source", "origin", "geographical", "collected"],
        "2(1)(j)": ["inventive", "process", "extraction", "novel", "patentable"],
        "2(1)(ja)": ["inventive step", "technical advance", "economic significance"],
        "section 3": ["foreign", "nri", "non-citizen", "overseas", "approval", "nba"],
        "section 6": ["ipr", "patent", "outside india", "nba approval"],
        "section 7": ["indian", "domestic", "vaidya", "local", "practitioner", "intimation", "sbb"],
        "regulation 3": ["synthetic", "vitamins", "minerals", "prohibited", "aahara"],
        "regulation 2(1)(a)": ["ayurveda aahara", "recipe", "authoritative", "definition"]
    }

    @classmethod
    def rerank(cls, query: str, candidates: List[Dict[str, Any]], top_k: int = 8) -> List[Dict[str, Any]]:
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

            # 3. Exact section boost (if explicitly cited in query)
            exact_boost = 0.0
            for term in ["3(p)", "3(e)", "3(a)", "3(d)", "3(i)", "158b", "section 3", "section 7", "section 6", "section 10(4)"]:
                if term in q_lower and term in sec_num:
                    exact_boost = cls.EXACT_SECTION_BOOST
                    break

            # 4. Substantive Regulatory Intent Alignment Boost
            substantive_boost = 0.0
            for sec_key, triggers in cls.SUBSTANTIVE_PROVISIONS.items():
                if sec_key in sec_num:
                    matching_triggers = sum(1 for trig in triggers if trig in q_lower)
                    if matching_triggers >= 1:
                        substantive_boost = cls.SUBSTANTIVE_LAW_BOOST * min(1.0, matching_triggers / 2.0)
                        break

            # Procedural de-prioritization: demote pre/post-grant opposition unless query specifically asks about opposition
            procedural_penalty = 0.0
            if ("section 25" in sec_num or "rule 24" in sec_num) and "opposition" not in q_lower:
                procedural_penalty = 0.12

            final_score = max(0.0, min(1.0, base_score + authority_bonus + term_score + exact_boost + substantive_boost - procedural_penalty))

            scored = dict(cand)
            scored["calibrated_score"] = round(final_score, 4)
            scored_candidates.append(scored)

        scored_candidates.sort(key=lambda x: x["calibrated_score"], reverse=True)
        return scored_candidates[:top_k]
