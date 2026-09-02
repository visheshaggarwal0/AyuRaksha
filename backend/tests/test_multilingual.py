"""
Test suite validating the Digital India Bhashini Multilingual Engine:
- Language detection (English, Hindi, Sanskrit, Tamil)
- Statutory term preservation & transliteration
- End-to-end query processing in Hindi & Sanskrit
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.ai.multilingual.bhashini import BhashiniService
from app.ai.pipeline import ai_pipeline


class TestBhashiniMultilingualService:
    def test_language_detection(self):
        # English
        assert BhashiniService.detect_language("Can I patent Ashwagandha in India?") == "en"

        # Hindi
        assert BhashiniService.detect_language("क्या मैं अश्वगंधा को पेटेंट करा सकता हूँ?") == "hi"

        # Sanskrit
        assert BhashiniService.detect_language("किम् अहम् अश्वगन्धायाः पेटेंट-अधिकारं लभे?") == "sa"
        assert BhashiniService.detect_language("अयं योगः पारम्परिक-ज्ञान-अधिनियमः अस्ति।") == "sa"

        # Tamil
        assert BhashiniService.detect_language("அஸ்வகந்தா காப்புரிமை பெற முடியுமா?") == "ta"

    def test_statutory_lexicon_translation_hindi(self):
        sample_text = (
            "Under Section 3(p) of the Patents Act, this formulation is Not Patentable. "
            "Approval Required from National Biodiversity Authority."
        )
        hi_translated = BhashiniService.translate_statutory_text(sample_text, target_lang="hi")

        assert "धारा 3(p)" in hi_translated
        assert "पेटेंट अधिनियम, 1970" in hi_translated
        assert "राष्ट्रीय जैव विविधता प्राधिकरण (NBA)" in hi_translated
        assert "पेटेंट योग्य नहीं" in hi_translated

    def test_statutory_lexicon_translation_sanskrit(self):
        sample_text = "Under Rule 158B and Patents Act, Compliance Required from State Biodiversity Board."
        sa_translated = BhashiniService.translate_statutory_text(sample_text, target_lang="sa")

        assert "नियमः १५८B" in sa_translated
        assert "पेटेंट-अधिनियमः" in sa_translated
        assert "राज्य-जैवविविधता-मण्डलम् (SBB)" in sa_translated

    @pytest.mark.asyncio
    async def test_incoming_hindi_query_processing(self):
        hindi_query = "क्या अश्वगंधा का पेटेंट धारा 3(p) के तहत वर्जित है?"
        en_query, detected_lang = await BhashiniService.process_incoming_query(hindi_query)

        assert detected_lang == "hi"
        # Check that statutory keywords were preserved or mapped
        assert "patent" in en_query.lower()

    @pytest.mark.asyncio
    async def test_end_to_end_hindi_pipeline_execution(self):
        # Run full pipeline with language="hi"
        result = await ai_pipeline.execute(
            query="Can I patent Ashwagandha in India?",
            jurisdiction="IN",
            language="hi"
        )

        assert result["detected_language"] == "hi"
        assert result["direct_answer"] is not None
        # Verify statutory terms were translated into Hindi in the response
        assert "धारा 3(p)" in result["direct_answer"] or "पेटेंट अधिनियम" in result["direct_answer"]
