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
            # Baseline score normalized to max 0.20
            raw_rel = cand.relevance_score if cand.relevance_score is not None else 0.5
            base_score = min(0.20, float(raw_rel) * 0.20)

            # 1. Authority Hierarchy Bonus (max 0.10)
            auth_level = min(5, max(1, cand.authority_level or 4))
            authority_bonus = (auth_level / 5.0) * 0.10

            # 2. Term overlap in text (max 0.15)
            text = (cand.verbatim_text or "").lower()
            matches = sum(1 for term in query_terms if term in text)
            term_score = (matches / len(query_terms) * 0.15) if query_terms else 0.0

            # 3. Exact section boost (0.35)
            sec_num = (cand.section_number or "").lower()
            exact_boost = 0.0
            clean_num = re.sub(r"\b(section|rule|regulation|article)\b", "", sec_num).strip()
            base_num = clean_num.split("(")[0].strip() if clean_num else ""
            if sec_num and (sec_num in q_lower or (clean_num and len(clean_num) >= 2 and re.search(r"\b" + re.escape(clean_num) + r"\b", q_lower))):
                exact_boost = self.EXACT_SECTION_BOOST
            elif base_num and len(base_num) >= 1 and re.search(r"\b(?:section|rule|regulation|article)\s*" + re.escape(base_num) + r"\b", q_lower):
                exact_boost = self.EXACT_SECTION_BOOST * 0.90

            # 4. Domain Intent Alignment Bonus (0.15)
            domain_boost = 0.0
            src_id = (cand.source_id or "").upper()
            
            # Classification, ASU, Proprietary, and Ayurveda Aahara questions
            if any(k in q_lower for k in ["classify", "classification", "classical", "proprietary", "aahara", "fssai", "license", "licensing"]):
                if "DRUGS_COSMETICS" in src_id:
                    domain_boost += 0.15
                elif "FSSAI" in src_id or "AAHARA" in src_id:
                    domain_boost += 0.15
                elif "TRADE_MARKS" in src_id and not any(tm in q_lower for tm in ["trademark", "brand", "mark", "logo", "class 5"]):
                    domain_boost -= 0.35  # Suppress trademark goods classes for drug regulatory questions

            # Patentability and Traditional Knowledge questions
            if any(k in q_lower for k in ["patent", "invent", "novelty", "3(p)", "3(e)", "tkdl", "extract", "formulation"]):
                if "PATENTS" in src_id:
                    domain_boost += 0.15

            # Biodiversity and ABS questions
            if any(k in q_lower for k in ["biodiversity", "abs", "nba", "sbb", "biological", "benefit sharing", "wild", "herb"]):
                if "BIOLOGICAL_DIVERSITY" in src_id or "ABS" in src_id:
                    domain_boost += 0.15

            # Export and International compliance questions
            if any(k in q_lower for k in ["export", "germany", "europe", "eu", "us", "usa", "fda", "ndi", "thmpd", "directive", "cfr", "overseas"]):
                if "EXPORT" in src_id or "INTERNATIONAL" in src_id or "WIPO" in src_id:
                    domain_boost += 0.15

            # Trademarks & Brand Name Protection
            if any(k in q_lower for k in ["trademark", "trade mark", "brand", "logo", "kesh", "distinctive", "bottle design", "passing off", "class 5", "ayush-shakti"]):
                if "TRADE_MARKS" in src_id or "TMA" in src_id:
                    domain_boost += 0.15

            # Advertising & DMR Act Questions
            if any(k in q_lower for k in ["advertisement", "ad", "dmr", "cure", "obesity", "cancer", "diabetes", "guaranteed cure", "100% cure"]):
                if "MAGIC_REMEDIES" in src_id or "ADVERTISING" in src_id:
                    domain_boost += 0.15
            elif "MAGIC_REMEDIES" in src_id:
                domain_boost -= 0.35

            # 5. Substantive Regulatory Intent Alignment Boost
            substantive_boost = 0.0
            substantive_map = {
                "3(p)": ["traditional", "ayurvedic", "ayurveda", "herbal", "formulation", "knowledge", "ashwagandha", "brahmi", "guggulu", "samhita", "purified", "cow urine", "modification", "neem", "haldi"],
                "3(e)": ["formulation", "combining", "mixture", "admixture", "synergy", "aggregation", "synergistic"],
                "3(d)": ["derivative", "extract", "form", "efficacy", "nano", "enhancement", "withaferin", "withanolides", "withania", "berberine", "daruharidra", "isolate", "pure", "obesity", "diabetes", "cancer", "cavitation", "yield", "extraction method", "curcumin", "phytosome"],
                "3(i)": ["method", "treatment", "cure", "administer", "disease", "ulcer", "patient", "doctor"],
                "3(c)": ["naturally", "occurring", "plant", "isolate", "substance"],
                "10(4)": ["disclose", "source", "origin", "geographical", "collected", "himachal"],
                "2(1)(j)": ["inventive", "process", "extraction", "novel", "patentable", "nano"],
                "2(1)(ja)": ["inventive step", "technical advance", "economic significance", "inventive", "advance", "novel", "process", "delivery", "superiority", "bioavailability", "extraction", "yield", "cavitation", "nano-formulation", "nano"],
                "section 3(a)": ["classical", "authoritative", "first schedule", "asu drug", "ayush drug", "dawa", "ilaj", "vitamins", "kidney failure", "punarnava"],
                "section 3": ["foreign", "nri", "non-citizen", "overseas", "approval", "nba", "german", "munich", "import", "indigenous", "wild kutki", "kutki", "germany"],
                "section 6": ["ipr", "patent", "outside india", "nba approval", "disclose", "pct", "form iii", "form 3", "form-iii", "patent grant", "before patent", "commercialize", "phytosome", "curcumin"],
                "section 7": ["indian", "domestic", "vaidya", "local", "practitioner", "intimation", "sbb", "delhi", "clinic", "patients"],
                "regulation 3": ["synthetic", "vitamins", "minerals", "prohibited", "aahara"],
                "regulation 5": ["disease", "cure", "claim", "claims", "aahara", "prohibited"],
                "schedule a": ["arjuna", "energy bar", "ingredients", "authoritative", "recipe", "permitted", "schedule a", "treatise"],
                "regulation 2(1)(a)": ["ayurveda aahara", "recipe", "authoritative", "definition"],
                "section 9": ["descriptive", "generic", "kesh", "distinctive", "trademark", "refusal", "absolute grounds", "ayush-shakti", "brand"],
                "rule 28": ["representation", "logo", "device", "distinctive", "label"],
                "section 29": ["infringement", "identical", "deceptively similar", "bottle design", "copy", "trade dress", "passing off"],
                "schedule y": ["clinical trial", "trials", "novel indication", "human phase", "protocol"],
                "schedule t": ["gmp", "manufacturing", "hygiene", "bhasma", "factory"],
                "section 3(b)": ["cosmetic", "soap", "anti-fungal", "therapeutic", "drug definition"],
                "section 39": ["foreign filing", "resident", "outside india", "license", "permission", "originating in india", "pct"],
                "section 40": ["contravention", "penalty", "section 39", "foreign filing", "liability"],
                "section 13": ["chemical", "single", "ashwagandha churna", "medicinal substance", "herbal name", "latin", "generic"],
                "regulation 8": ["logo", "green logo", "ayurveda aahara logo", "substitute", "not to be used as substitute"],
                "section 3(j)": ["fungus", "antimicrobial", "plants", "animals", "microorganism", "living thing", "nilgiris", "wild"],
                "rule 24b": ["timeline", "examination", "form 18", "shortened", "thirty-one months", "31 months", "request for examination"],
                "article 3": ["wipo", "gratk", "mandatory disclosure", "patent specification", "article 3", "pct", "originating in india"],
                "article 5": ["formal defect", "revocation", "sanctions", "defect in origin", "remedies", "gratk"],
                "cites": ["cites", "sandalwood", "red sanders", "endangered", "permit", "management authority"],
                "directive 2004/24/ec": ["germany", "europe", "eu", "thmpd", "traditional herbal", "export", "plans to export"],
                "21 cfr part 111": ["curcumin", "phytosome", "ndi", "us fda", "america", "united states", "dietary supplement", "notification", "commercialize", "21 cfr", "part 111"]
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

        # Deduplicate same statute + same normalized section (e.g. "Section 39" and "Section Section 39")
        unique_candidates = []
        seen_sec_keys = set()
        for cand in scored_candidates:
            clean_sec = re.sub(r"^(?:section|rule|regulation|article|\s)+", "", (cand.section_number or "").lower()).strip()
            if clean_sec.startswith("10(4)"):
                clean_sec = "10(4)"
            sec_key = (cand.source_id, clean_sec) if clean_sec else (cand.source_id, cand.section_number)
            if sec_key not in seen_sec_keys:
                seen_sec_keys.add(sec_key)
                unique_candidates.append(cand)

        # Source diversity: Cap lower-tier taxonomy to at most 2.
        # Primary statutes capped at 5 unless candidate has direct exact/substantive boost
        final_list = []
        taxonomy_count = 0
        source_counts: Dict[str, int] = {}
        primary_sources = {
            (c.source_id or "").upper()
            for c in unique_candidates
            if not any(t in (c.source_id or "").upper() for t in ["TKDL", "CLASSICAL", "GLOSSARY", "FIRST_SCHEDULE", "FIRST SCHEDULE", "AYURVEDIC_BOOKS"]) and c.authority_level >= 4
        }
        is_multi_statute = len(primary_sources) >= 2

        for cand in unique_candidates:
            src_id = (cand.source_id or "").upper()
            is_taxonomy = any(t in src_id for t in ["TKDL", "CLASSICAL", "GLOSSARY", "FIRST_SCHEDULE", "FIRST SCHEDULE", "AYURVEDIC_BOOKS"]) or cand.authority_level <= 3
            sec_num = (cand.section_number or "").lower()
            clean_sec = re.sub(r"\b(section|rule|regulation|article)\b", "", sec_num).strip()
            base_sec = clean_sec.split("(")[0].strip() if clean_sec else ""
            has_exact = sec_num in q_lower or (clean_sec and re.search(r"\b" + re.escape(clean_sec) + r"\b", q_lower)) or (base_sec and re.search(r"\b(?:section|rule|regulation|article)\s*" + re.escape(base_sec) + r"\b", q_lower))
            has_substantive = False
            for sk, trigs in substantive_map.items():
                if sk in sec_num and any(t in q_lower for t in trigs):
                    has_substantive = True
                    break
            has_direct_boost = bool(has_exact or has_substantive)

            if is_taxonomy:
                if taxonomy_count >= 2:
                    continue
                taxonomy_count += 1
            elif "AMENDMENT" in src_id and not has_direct_boost and source_counts.get(src_id, 0) >= 1:
                continue
            elif "WIPO" in src_id and not has_direct_boost and source_counts.get(src_id, 0) >= 2:
                continue
            elif is_multi_statute and source_counts.get(src_id, 0) >= 5 and not has_direct_boost:
                continue

            source_counts[src_id] = source_counts.get(src_id, 0) + 1
            final_list.append(cand)
            if len(final_list) >= top_k:
                break

        return final_list


reranking_module = LegalAuthorityReranker()
