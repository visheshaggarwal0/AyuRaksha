"""
Test Suite: Active Compliance Dossier Generator (SIH 26045)
Validates deterministic synthesis of regulatory categories, ABS filing milestones,
timelines, fees, and cryptographic citation trails.
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.models.dossier import DossierGenerationRequest, ComplianceDossierResponse
from app.engines.dossier_generator import ComplianceDossierGenerator


class TestComplianceDossierGenerator:
    def test_classical_formulation_dossier(self):
        req = DossierGenerationRequest(
            product_name="Maha Sudarshan Churna Classical",
            ingredients=["Neem", "Giloy", "Ginger"],
            in_classical_text=True,
            is_formulation_modified=False,
            is_purified_standardized_fraction=False,
            intended_use="therapeutic",
            disease_treatment_claims=True,
            is_indian_entity=True,
            target_market="IN"
        )
        dossier = ComplianceDossierGenerator.generate_dossier(req)

        assert isinstance(dossier, ComplianceDossierResponse)
        assert dossier.dossier_id.startswith("DOSSIER-")
        assert "CLASSICAL" in dossier.regulatory_classification["category"]
        assert "BARRED" in dossier.regulatory_classification["patentability"]
        assert len(dossier.filing_roadmap) >= 2

        # Check Milestone Details
        m1 = dossier.filing_roadmap[0]
        assert "SBB" in m1.authority or "Raw Material" in m1.title
        m2 = dossier.filing_roadmap[1]
        assert "Form 24D" in m2.mandatory_form

        # Check markdown report contains key elements
        assert "# AYURAKSHA ACTIVE COMPLIANCE DOSSIER" in dossier.markdown_report
        assert "Form 24D" in dossier.markdown_report
        assert len(dossier.verifiable_citations) > 0

    def test_phytopharmaceutical_dossier_with_cross_border(self):
        req = DossierGenerationRequest(
            product_name="Curcumin Standardized Nano-Emulsion",
            ingredients=["Turmeric", "Black Pepper"],
            in_classical_text=False,
            is_formulation_modified=True,
            is_purified_standardized_fraction=True,
            intended_use="therapeutic",
            disease_treatment_claims=True,
            is_indian_entity=True,
            target_market="CROSS_BORDER"
        )
        dossier = ComplianceDossierGenerator.generate_dossier(req)

        assert "PHYTOPHARMACEUTICAL" in dossier.regulatory_classification["category"]
        assert "PATENTABLE" in dossier.regulatory_classification["patentability"]

        # Check CDSCO requirement in milestones
        cdsco_step = next((m for m in dossier.filing_roadmap if "CDSCO" in m.authority), None)
        assert cdsco_step is not None
        assert "CT-18" in cdsco_step.mandatory_form or "CT-21" in cdsco_step.mandatory_form

        # Check NBA Form III for patent grant
        nba_step = next((m for m in dossier.filing_roadmap if "Form III" in m.mandatory_form), None)
        assert nba_step is not None

        # Check cross-border posture
        assert dossier.cross_border_posture is not None
        assert "DSHEA" in dossier.cross_border_posture["destination_market_clearance"]
        assert "WIPO GRATK" in dossier.cross_border_posture["destination_market_clearance"]
