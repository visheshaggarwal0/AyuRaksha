"""
Test suite validating the 5th Regulatory Classification Tier:
Phytopharmaceutical Drug under Drugs & Cosmetics Gazette G.S.R. 918(E) & New Drugs Rules 2019.
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse, Jurisdiction
from app.engines.classifier import ProductClassifier


class TestPhytopharmaceuticalClassification:
    def test_phytopharmaceutical_tier_takes_effect(self):
        """
        Verify that a non-classical purified standardized fraction with disease claims
        is classified as PHYTOPHARMACEUTICAL_DRUG under CDSCO / GSR 918(E).
        """
        req = ProductClassificationRequest(
            name="Curcuma-Fraction-95 (Standardized Curcuminoids)",
            in_classical_text=False,
            is_formulation_modified=True,
            has_novel_excipients=True,
            is_purified_standardized_fraction=True,
            intended_use="therapeutic",
            disease_treatment_claims=True,
            has_biological_resources=True,
            target_market="IN"
        )
        resp = ProductClassifier.evaluate(req)

        assert resp.category == "PHYTOPHARMACEUTICAL_DRUG (CDSCO / GSR 918E)"
        assert "Drugs and Cosmetics Rules, 1945 (Rule 122E / GSR 918(E))" in resp.governing_act
        assert resp.regulatory_authority == "Central Drugs Standard Control Organization (CDSCO) / DCGI"
        assert resp.patentability == "PATENTABLE_SUBJECT_TO_NOVELTY_AND_EFFICACY"
        assert resp.abs_required is True

        # Check citations
        citation_sources = [c.source_id for c in resp.citations]
        assert "IND_DRUGS_COSMETICS_RULES_1945_GSR_918E" in citation_sources
        assert "IND_PATENTS_ACT_1970" in citation_sources

        # Check next actions include Form CT-18 / CT-21 and 4 marker compounds
        assert any("CT-18" in act for act in resp.next_actions)
        assert any("4 analytical/bioactive marker" in act for act in resp.next_actions)

    def test_classical_medicine_takes_precedence_over_phytopharmaceutical(self):
        """
        Even if someone marks standardized fraction, if it is in classical text unmodified,
        it is Shastriya classical medicine barred under Section 3(p).
        """
        req = ProductClassificationRequest(
            name="Classical Triphala Churna",
            in_classical_text=True,
            is_formulation_modified=False,
            has_novel_excipients=False,
            is_purified_standardized_fraction=True,
            intended_use="therapeutic",
            disease_treatment_claims=True,
            has_biological_resources=True,
            target_market="IN"
        )
        resp = ProductClassifier.evaluate(req)
        assert resp.category == "CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)"
        assert resp.patentability == "BARRED_UNDER_SECTION_3P"
