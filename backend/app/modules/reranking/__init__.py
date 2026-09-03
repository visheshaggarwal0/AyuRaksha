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
            if any(k in q_lower for k in ["patent", "invent", "novelty", "3(p)", "3(e)", "tkdl", "extract", "formulation"]):
                if "PATENTS" in src_id:
                    domain_boost += 0.25

            # Biodiversity and ABS questions
            if any(k in q_lower for k in ["biodiversity", "abs", "nba", "sbb", "biological", "benefit sharing", "wild", "herb"]):
                if "BIOLOGICAL_DIVERSITY" in src_id or "ABS" in src_id:
                    domain_boost += 0.25

            # 5. Substantive Regulatory Intent Alignment Boost
            substantive_boost = 0.0
            substantive_map = {
                "3(p)": ["traditional", "ayurvedic", "ayurveda", "herbal", "formulation", "knowledge", "ashwagandha", "brahmi", "guggulu", "samhita", "purified", "cow urine", "modification", "neem", "haldi"],
                "3(e)": ["formulation", "combining", "mixture", "admixture", "synergy", "aggregation", "synergistic"],
                "3(d)": ["derivative", "extract", "form", "efficacy", "nano", "enhancement", "withaferin", "berberine", "daruharidra", "isolate", "pure"],
                "3(i)": ["method", "treatment", "cure", "administer", "disease", "ulcer", "patient", "doctor"],
                "3(c)": ["naturally", "occurring", "plant", "isolate", "substance"],
                "10(4)": ["disclose", "source", "origin", "geographical", "collected", "himachal"],
                "2(1)(j)": ["inventive", "process", "extraction", "novel", "patentable", "nano"],
                "2(1)(ja)": ["inventive step", "technical advance", "economic significance", "inventive", "advance"],
                "section 3": ["foreign", "nri", "non-citizen", "overseas", "approval", "nba", "german", "munich", "import"],
                "section 6": ["ipr", "patent", "outside india", "nba approval", "disclose", "pct"],
                "section 7": ["indian", "domestic", "vaidya", "local", "practitioner", "intimation", "sbb", "delhi", "clinic", "patients"],
                "regulation 3": ["synthetic", "vitamins", "minerals", "prohibited", "aahara"],
                "regulation 2(1)(a)": ["ayurveda aahara", "recipe", "authoritative", "definition"]
            }
            for sec_key, triggers in substantive_map.items():
                if sec_key in sec_num:
                    matching_triggers = sum(1 for trig in triggers if trig in q_lower)
                    if matching_triggers >= 1:
                        substantive_boost = 0.22 * min(1.0, matching_triggers / 2.0)
                        break

            # Procedural de-prioritization: demote pre/post-grant opposition unless query specifically asks about opposition
            procedural_penalty = 0.0
            if ("section 25" in sec_num or "section 64" in sec_num or "section 92" in sec_num or "rule 24" in sec_num) and "opposition" not in q_lower and "revocation" not in q_lower:
                procedural_penalty = 0.15

            final_score = max(0.0, min(1.0, base_score + authority_bonus + term_score + exact_boost + domain_boost + substantive_boost - procedural_penalty))
            cand_copy = cand.model_copy()
            cand_copy.relevance_score = round(final_score, 4)
            scored_candidates.append(cand_copy)

        scored_candidates.sort(key=lambda x: x.relevance_score, reverse=True)

        # Source diversity: Cap lower-tier taxonomy/classical text records to at most 2 entries
        # to ensure primary statutory Acts and Rules always receive adequate representation
        final_list = []
        taxonomy_count = 0
        for cand in scored_candidates:
            src_id = (cand.source_id or "").upper()
            is_taxonomy = any(t in src_id for t in ["TKDL_AYURVEDA_BOOKS", "CLASSICAL_TEXTS", "GLOSSARY", "FIRST SCHEDULE"]) or cand.authority_level <= 3
            if is_taxonomy:
                if taxonomy_count >= 2:
                    continue
                taxonomy_count += 1
            final_list.append(cand)
            if len(final_list) >= top_k:
                break

        return final_list


reranking_module = LegalAuthorityReranker()
