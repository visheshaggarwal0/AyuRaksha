"""
Test suite validating the Dual-Pane Cross-Border Jurisdiction Isolation Engine:
- Statutory posture isolation between India (BDA 2002, Patents Act Sec 39)
  and Destination Regimes (WIPO GRATK Treaty 2024, US FDA DSHEA, EU THMPD).
- Verification that postures are never conflated (SIH 26045 mandate).
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.ai.pipeline import ai_pipeline
from app.agents.orchestrator import AyuRakshaOrchestrator


class TestCrossBorderDualPaneIsolation:
    @pytest.mark.asyncio
    async def test_cross_border_query_produces_isolated_dual_postures(self):
        query = "What are the export and patent requirements to market Himalayan Kutki in the US and Europe?"
        result = await ai_pipeline.execute(
            query=query,
            jurisdiction="CROSS_BORDER",
            language="en"
        )

        assert result["jurisdiction"] == "CROSS_BORDER"
        posture = result.get("cross_border_posture")
        assert posture is not None
        assert "india_posture" in posture
        assert "international_posture" in posture

        india_text = posture["india_posture"]
        intl_text = posture["international_posture"]

        # Check India Posture covers BDA Section 3/19 and Patents Act Section 39 FFL
        assert "Biological Diversity Act, 2002" in india_text
        assert "National Biodiversity Authority" in india_text or "NBA" in india_text
        assert "Section 39" in india_text

        # Check International Posture covers WIPO GRATK Treaty 2024 and US FDA DSHEA / EU THMPD
        assert "WIPO GRATK Treaty" in intl_text
        assert "Article 3" in intl_text
        assert "DSHEA" in intl_text or "FDA" in intl_text
        assert "Directive 2004/24/EC" in intl_text or "EMA" in intl_text

    @pytest.mark.asyncio
    async def test_orchestrator_preserves_cross_border_posture(self):
        orchestrator = AyuRakshaOrchestrator()
        answer = await orchestrator.process_query(
            query="Can I export Ashwagandha extract to Germany?",
            user_jurisdiction="CROSS_BORDER",
            language="en"
        )

        assert answer.jurisdiction == "CROSS_BORDER"
        assert answer.cross_border_posture is not None
        assert "india_posture" in answer.cross_border_posture
        assert "international_posture" in answer.cross_border_posture
