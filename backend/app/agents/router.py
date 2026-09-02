import re
from typing import Dict, Any

class QueryRouterAgent:
    """
    Intelligent routing agent that decomposes queries:
    1. Language detection (English, Hindi, Hinglish)
    2. Intent classification (Patent, ABS, Classification, Export, Trademark, General)
    3. Jurisdiction determination (IN, INT, CROSS_BORDER)
    4. Botanical term resolution
    """

    BOTANICAL_MAP = {
        "ashwagandha": "Withania somnifera",
        "haldi": "Curcuma longa",
        "turmeric": "Curcuma longa",
        "haridra": "Curcuma longa",
        "neem": "Azadirachta indica",
        "nimba": "Azadirachta indica",
        "kutki": "Picrorhiza kurroa",
        "katuka": "Picrorhiza kurroa",
        "giloy": "Tinospora cordifolia",
        "guduchi": "Tinospora cordifolia",
        "shatavari": "Asparagus racemosus",
        "tulsi": "Ocimum sanctum",
        "triphala": "Terminalia chebula, Terminalia bellirica, Phyllanthus emblica"
    }

    def route_query(self, query: str, user_selected_jurisdiction: str = "IN") -> Dict[str, Any]:
        q_lower = query.lower()

        # 1. Language detection
        is_hindi = bool(re.search(r"[\u0900-\u097F]", query) or re.search(r"\b(kya|main|mera|kaise|karein|chahiye|lep|dawa)\b", q_lower))
        detected_language = "hi" if is_hindi else "en"

        # 2. Jurisdiction enforcement
        jurisdiction = user_selected_jurisdiction
        if re.search(r"\b(germany|europe|usa|fda|thmpd|export|abroad|international|wipo)\b", q_lower):
            if re.search(r"\b(india|indian|sbb|nba)\b", q_lower):
                jurisdiction = "CROSS_BORDER"
            else:
                jurisdiction = "INT"

        # 3. Intent classification
        intent = "GENERAL_RESEARCH"
        if re.search(r"\b(patents?|patentable|section\s*3\(?[a-z]\)?|inventive step|prior art)", q_lower):
            intent = "PATENTABILITY_ASSESSMENT"
        elif re.search(r"\b(abs|biodiversity|nba|sbb|benefit sharing|biological resource|prior intimation)\b", q_lower):
            intent = "ABS_ASSESSMENT"
        elif re.search(r"\b(classical|proprietary|fssai|ayurveda aahara|cosmetic|license|rule 158b)\b", q_lower):
            intent = "PRODUCT_CLASSIFICATION"
        elif re.search(r"\b(trademark|brand|class 5|gi|geographical indication)\b", q_lower):
            intent = "IP_TRADEMARK_GI"
        elif re.search(r"\b(export|germany|us fda|directive 2004/24/ec)\b", q_lower):
            intent = "EXPORT_ASSESSMENT"

        # 4. Resolved botanicals via TKDL taxonomy
        detected_botanicals = []
        try:
            from app.corpus.taxonomy import taxonomy_engine
            resolved = taxonomy_engine.resolve_botanicals_in_text(query)
            for r in resolved:
                detected_botanicals.append({
                    "local_name": r.get("sanskrit_name") or r.get("matched_term"),
                    "botanical_name": r.get("botanical_name")
                })
        except Exception:
            pass

        # Fallback to hardcoded map if no taxonomy match
        if not detected_botanicals:
            for local_name, botanical_name in self.BOTANICAL_MAP.items():
                if local_name in q_lower:
                    detected_botanicals.append({"local_name": local_name, "botanical_name": botanical_name})

        return {
            "query": query,
            "detected_language": detected_language,
            "jurisdiction": jurisdiction,
            "intent": intent,
            "detected_botanicals": detected_botanicals
        }
