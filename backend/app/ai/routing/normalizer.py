import re
import unicodedata
from typing import Dict, Any

class QueryNormalizer:
    """
    Normalizes user queries:
    - Normalizes Unicode & strips corrupted diacritics / legacy font artifacts
    - Detects script (Latin, Devanagari)
    - Replaces common informal vernacular terms with canonical forms
    """

    # Common transliteration mappings
    DIACRITIC_MAP = {
        'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'ri', 'ṝ': 'ri',
        'ḷ': 'li', 'ḹ': 'li', 'ñ': 'n', 'ṅ': 'n', 'ṇ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ś': 'sh', 'ṣ': 'sh', 'ṃ': 'm',
        'ḥ': 'h', '®': 'n', '¢': 'a', '¦': 'u', 'º': 's',
        '¨': 'ri', '¼': 'ng', '¾': 'sh'
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        if not text:
            return ""
        # 1. Unicode normalization
        normalized = unicodedata.normalize("NFKD", text)
        # 2. Map known transliteration diacritics
        for char, repl in cls.DIACRITIC_MAP.items():
            normalized = normalized.replace(char, repl)
        # 3. Collapse extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @classmethod
    def detect_script(cls, text: str) -> str:
        devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
        if devanagari_count > len(text) * 0.2:
            return "Devanagari"
        return "Latin"

    @classmethod
    def process(cls, query: str) -> Dict[str, Any]:
        cleaned = cls.normalize_text(query)
        script = cls.detect_script(query)
        return {
            "raw_query": query,
            "normalized_query": cleaned,
            "script": script,
            "is_multilingual": script == "Devanagari" or bool(re.search(r"[\u0900-\u097F]", query))
        }
