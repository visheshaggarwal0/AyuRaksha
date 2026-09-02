"""
Digital India Bhashini (ULCA / Anuvada) Multilingual Service
Provides language detection, translation, and statutory term transliteration
across English, Hindi (hi), Sanskrit (sa), Tamil (ta), and other Indian languages.
"""
import re
import logging
from typing import Optional, Tuple, Dict, Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BhashiniService:
    """
    Multilingual Gateway interfacing with Digital India Bhashini infrastructure,
    with automatic fallbacks for LLM-based translation and offline statutory lexicons.
    """

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi (हिन्दी)",
        "sa": "Sanskrit (संस्कृतम्)",
        "ta": "Tamil (தமிழ்)",
        "mr": "Marathi (मराठी)",
        "te": "Telugu (తెలుగు)"
    }

    # Core statutory & AYUSH vocabulary preservation dictionary
    STATUTORY_LEXICON_HI = {
        "patents act": "पेटेंट अधिनियम, 1970",
        "section 3(p)": "धारा 3(p) (पारंपरिक ज्ञान अपवर्जन)",
        "section 3(e)": "धारा 3(e) (मात्र मिश्रण)",
        "section 3(d)": "धारा 3(d) (संवर्धित प्रभावकारिता)",
        "biological diversity act": "जैविक विविधता अधिनियम, 2002",
        "access and benefit sharing": "पहुंच और लाभ साझाकरण (ABS)",
        "national biodiversity authority": "राष्ट्रीय जैव विविधता प्राधिकरण (NBA)",
        "state biodiversity board": "राज्य जैव विविधता बोर्ड (SBB)",
        "drugs and cosmetics act": "औषधि एवं प्रसाधन सामग्री अधिनियम, 1940",
        "drugs and cosmetics rules": "औषधि एवं प्रसाधन सामग्री नियमावली, 1945",
        "rule 158b": "नियम 158B (पेटेंट/स्वामित्व वाली औषधियां)",
        "ayurveda aahara": "आयुर्वेद आहार (FSSAI 2022)",
        "phytopharmaceutical": "फाइटोफार्मास्युटिकल औषधि (CDSCO / GSR 918(E))",
        "wipo gratk treaty": "विपो GRATK संधि, 2024",
        "mandatory disclosure": "अनिवार्य उत्पत्ति प्रकटीकरण",
        "tkdl": "पारंपरिक ज्ञान डिजिटल लाइब्रेरी (TKDL)",
        "form 3": "प्रपत्र 3 (विदेशी आवेदन विवरण)",
        "form 27": "प्रपत्र 27 (पेटेंट का वाणिज्यिक कार्यकरण)",
        "direct answer": "प्रत्यक्ष विधिक परामर्श",
        "recommended next action": "अनुशंसित अग्रिम कार्रवाई",
        "jurisdiction": "अधिकार क्षेत्र",
        "confidence": "विश्वास स्तर",
        "safe abstention": "सुरक्षित विधिक स्थगन"
    }

    STATUTORY_LEXICON_SA = {
        "patents act": "पेटेंट-अधिनियमः १९७०",
        "section 3(p)": "धारा ३(p) (पारम्परिक-ज्ञान-प्रतिबन्धः)",
        "section 3(e)": "धारा ३(e) (संमिश्रण-निषेधः)",
        "biological diversity act": "जैव-विविधता-अधिनियमः २००२",
        "access and benefit sharing": "प्रवेश-लाभ-वितरणम् (ABS)",
        "national biodiversity authority": "राष्ट्रीय-जैवविविधता-प्राधिकरणम् (NBA)",
        "state biodiversity board": "राज्य-जैवविविधता-मण्डलम् (SBB)",
        "drugs and cosmetics act": "औषध-सौन्दर्यप्रसाधन-अधिनियमः १९४०",
        "rule 158b": "नियमः १५८B (स्वायत्त-औषधयः)",
        "ayurveda aahara": "आयुर्वेद-आहारः",
        "phytopharmaceutical": "वनस्पति-औषधम् (CDSCO)",
        "wipo gratk treaty": "विपो GRATK सन्धिः २०२४",
        "tkdl": "पारम्परिकज्ञान-डिजिटल-पुस्तकालयः (TKDL)",
        "direct answer": "साक्षात् विधिक-उत्तरम्",
        "recommended next action": "अनुशंसित-अग्रिम-कार्यम्",
        "jurisdiction": "अधिकारक्षेत्रम्"
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect language based on Unicode script ranges and keywords.
        """
        if not text:
            return "en"

        # Tamil script range: 0B80 - 0BFF
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "ta"

        # Telugu script range: 0C00 - 0C7F
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "te"

        # Devanagari script range: 0900 - 097F
        if re.search(r"[\u0900-\u097F]", text):
            # Differentiate Sanskrit by visarga (ः), avagraha (ऽ), and specific inflections
            if re.search(r"[ःऽ]", text) or any(w in text for w in ["अस्ति", "भवति", "अधिनियमः", "विधिः"]):
                return "sa"
            return "hi"

        return "en"

    @classmethod
    async def translate_via_bhashini_api(cls, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Calls live Digital India Bhashini Dhruva pipeline if credentials are configured.
        """
        if not settings.BHASHINI_API_KEY or not settings.BHASHINI_USER_ID:
            return None

        headers = {
            "Content-Type": "application/json",
            "ulcaApiKey": settings.BHASHINI_API_KEY,
            "userId": settings.BHASHINI_USER_ID
        }

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        }
                    }
                }
            ],
            "inputData": {
                "input": [{"source": text}]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(settings.BHASHINI_INFERENCE_URL, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    outputs = data.get("pipelineResponse", [{}])[0].get("output", [])
                    if outputs and "target" in outputs[0]:
                        return outputs[0]["target"]
        except Exception as e:
            logger.warning(f"Bhashini live API failed: {e}. Falling back to internal engine.")

        return None

    @classmethod
    def translate_statutory_text(cls, text: str, target_lang: str) -> str:
        """
        Translates legal and Ayush answers using domain lexicon mapping
        and structured template transformation.
        """
        if target_lang == "en" or not text:
            return text

        lexicon = cls.STATUTORY_LEXICON_HI if target_lang == "hi" else cls.STATUTORY_LEXICON_SA

        translated = text
        for en_term, Indic_term in lexicon.items():
            pattern = re.compile(re.escape(en_term), re.IGNORECASE)
            translated = pattern.sub(Indic_term, translated)

        # High-utility template translations for Direct Answers
        if target_lang == "hi":
            translated = re.sub(r"\bNot Patentable\b", "पेटेंट योग्य नहीं (वर्जित)", translated, flags=re.I)
            translated = re.sub(r"\bPatentable\b", "पेटेंट योग्य", translated, flags=re.I)
            translated = re.sub(r"\bCompliance Required\b", "विधिक अनुपालन अनिवार्य", translated, flags=re.I)
            translated = re.sub(r"\bApproval Required\b", "पूर्व अनुमति आवश्यक", translated, flags=re.I)
            translated = re.sub(r"\bFormulation is barred under\b", "यह सूत्रीकरण वर्जित है", translated, flags=re.I)
        elif target_lang == "sa":
            translated = re.sub(r"\bNot Patentable\b", "पेटेंट-अयोग्यम् (प्रतिषिद्धम्)", translated, flags=re.I)
            translated = re.sub(r"\bPatentable\b", "पेटेंट-योग्यम्", translated, flags=re.I)
            translated = re.sub(r"\bCompliance Required\b", "अनुपालनम् आवश्यकम्", translated, flags=re.I)

        return translated

    @classmethod
    async def process_incoming_query(cls, query: str, user_lang: Optional[str] = None) -> Tuple[str, str]:
        """
        Detects query language, translates non-English queries to English
        for statutory indexing, and returns (english_query, detected_lang).
        """
        detected_lang = user_lang or cls.detect_language(query)
        if detected_lang == "en":
            return query, "en"

        # Attempt Bhashini live API
        live_tr = await cls.translate_via_bhashini_api(query, source_lang=detected_lang, target_lang="en")
        if live_tr:
            return live_tr, detected_lang

        # Fallback keyword transliteration / normalizer for statutory terms in Hindi/Sanskrit
        en_query = query
        reverse_lexicon = {v.lower(): k for k, v in cls.STATUTORY_LEXICON_HI.items()}
        for indic_term, en_term in reverse_lexicon.items():
            if indic_term in query.lower():
                en_query += f" {en_term}"

        # Common Hindi question words mapping
        en_query = re.sub(r"\bक्या\b", "", en_query)
        en_query = re.sub(r"\bपेटेंट\b", "patent", en_query)
        en_query = re.sub(r"\bहो सकता है\b", "patentability eligibility", en_query)
        en_query = re.sub(r"\bअधिनियम\b", "act", en_query)
        en_query = re.sub(r"\bनियम\b", "rules", en_query)

        return en_query.strip(), detected_lang
