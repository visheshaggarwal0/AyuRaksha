import re
from typing import Dict, Any, List
from app.corpus.taxonomy import taxonomy_engine

class EntityExtractor:
    """
    Extracts high-precision regulatory, botanical, and classical entities
    from normalized queries using TKDL Taxonomy & statutory regex.
    """

    STATUTORY_SECTION_PATTERNS = [
        (r"\bsection 3\(?p\)?\b", "Patents Act, 1970 - Section 3(p) [Traditional Knowledge Bar]"),
        (r"\bsection 3\(?e\)?\b", "Patents Act, 1970 - Section 3(e) [Mere Admixture Bar]"),
        (r"\bsection 3\(?a\)?\b", "Drugs & Cosmetics Act, 1940 - Section 3(a) [Classical ASU Definition]"),
        (r"\bsection 3\(?h\)?\b", "Drugs & Cosmetics Act, 1940 - Section 3(h) [Proprietary ASU Definition]"),
        (r"\brule 158-?b\b", "Drugs & Cosmetics Rules, 1945 - Rule 158B [Licensing]"),
        (r"\bsection 3\b", "Biological Diversity Act, 2002 - Section 3 [Foreign Entity Mandate]"),
        (r"\bsection 6\b", "Biological Diversity Act, 2002 - Section 6 [IPR Prior Approval]"),
        (r"\bsection 7\b", "Biological Diversity Act, 2002 - Section 7 [SBB Prior Intimation]"),
        (r"\bfirst schedule\b", "Drugs & Cosmetics Act, 1940 - First Schedule [Authoritative Texts]"),
        (r"\bform i\b", "NBA Form I [Access Approval]"),
        (r"\bform iii\b", "NBA Form III [Patent Application Approval]")
    ]

    @classmethod
    def extract_entities(cls, query: str) -> Dict[str, Any]:
        q_lower = query.lower()

        # 1. Botanical Entities
        botanicals = []
        try:
            resolved = taxonomy_engine.resolve_botanicals_in_text(query)
            for r in resolved:
                botanicals.append({
                    "matched_term": r.get("matched_term"),
                    "scientific_name": r.get("scientific_name"),
                    "sanskrit_name": r.get("sanskrit_name"),
                    "common_name": r.get("common_name"),
                    "unani_name": r.get("unani_name"),
                    "is_biological_resource": True
                })
        except Exception:
            pass

        # 2. Classical Books
        matched_books = []
        try:
            for book in taxonomy_engine.books:
                title = book.get("title", "").lower()
                if title and len(title) > 3 and title in q_lower:
                    matched_books.append({
                        "title": book.get("title"),
                        "author": book.get("author"),
                        "first_schedule_status": True
                    })
        except Exception:
            pass

        # 3. Explicit Statutory Sections
        statutory_mentions = []
        for pattern, label in cls.STATUTORY_SECTION_PATTERNS:
            if re.search(pattern, q_lower):
                statutory_mentions.append(label)

        # 4. Clinical / Disease Conditions
        matched_diseases = []
        try:
            for dis in taxonomy_engine.diseases:
                s_name = dis.get("sanskrit_name", "").lower()
                e_name = dis.get("english_name", "").lower()
                if (s_name and len(s_name) > 3 and s_name in q_lower) or (e_name and len(e_name) > 3 and e_name in q_lower):
                    matched_diseases.append({
                        "sanskrit_name": dis.get("sanskrit_name"),
                        "english_name": dis.get("english_name")
                    })
        except Exception:
            pass

        return {
            "botanicals": botanicals,
            "classical_books": matched_books,
            "statutory_provisions": statutory_mentions,
            "diseases": matched_diseases,
            "has_biological_resources": len(botanicals) > 0
        }
