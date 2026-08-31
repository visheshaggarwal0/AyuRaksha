"""
Comprehensive pytest suite for AyuRaksha Regulatory Decision Engines
- backend/app/engines/classifier.py (ProductClassifier)
- backend/app/engines/abs_tree.py (ABSDecisionTree)
- backend/app/engines/safety.py (SafetyGuardrailEngine sanity)

Statutory coverage:
- Drugs & Cosmetics Act, 1940 Sec 3(a) vs Sec 3(h)/Rule158B
- Patents Act, 1970 Sec 3(p)/3(e)/3(i)/10(4)
- Biological Diversity Act, 2002 Sec 3 / Sec 6 / Sec 7 + 2023 Amendments
- FSSAI (Ayurveda Aahara) Regulations, 2022
- Cosmetics Rules, 2020
Run:  pytest backend/tests/test_engines.py -v
"""
import sys
import os
import pytest

# Ensure backend root on path for `app` imports
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.engines.classifier import ProductClassifier
from app.engines.abs_tree import ABSDecisionTree
from app.engines.safety import SafetyGuardrailEngine
from app.models.schemas import ProductClassificationRequest, ABSAssessmentRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_class_req(**overrides) -> ProductClassificationRequest:
    defaults = dict(
        name="Test Formulation",
        in_classical_text=True,
        is_formulation_modified=False,
        has_novel_excipients=False,
        intended_use="therapeutic",
        disease_treatment_claims=True,
        has_biological_resources=True,
        target_market="IN",
    )
    defaults.update(overrides)
    return ProductClassificationRequest(**defaults)


def make_abs_req(**overrides) -> ABSAssessmentRequest:
    defaults = dict(
        biological_resource="Ashwagandha",
        origin_country="India",
        sourced_from_state="Kerala",
        is_commercial_utilization=True,
        is_traditional_knowledge_associated=True,
        is_indian_entity=True,
        is_export_intended=False,
    )
    defaults.update(overrides)
    return ABSAssessmentRequest(**defaults)


# ---------------------------------------------------------------------------
# ProductClassifier Tests
# ---------------------------------------------------------------------------

class TestClassifierClassicalASU:
    """Rule 1 — Classical ASU Medicine (Shastriya) : Sec 3(a) + Sec 3(p) bar"""

    def test_classical_exact_shastriya_classification(self):
        req = make_class_req(
            name="Trikatu Churna Classical",
            in_classical_text=True,
            is_formulation_modified=False,
            has_novel_excipients=False,
            intended_use="therapeutic",
            disease_treatment_claims=True,
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)"
        assert "First Schedule" in res.governing_act
        assert res.patentability == "BARRED_UNDER_SECTION_3P"
        assert res.abs_required is True
        assert res.regulatory_authority == "State Licensing Authority (AYUSH)"
        assert res.confidence == 1.0
        # citations include Sec 3(p) and Sec 3(a)
        sections = [c.section for c in res.citations]
        assert "Section 3(p)" in sections
        assert "Section 3(a)" in sections
        assert len(res.next_actions) == 4
        assert any("Manufacturing License" in a for a in res.next_actions)

    def test_classical_with_novel_excipients_not_classical(self):
        """Having novel excipients should NOT trigger Rule 1 – falls to Proprietary or other branch"""
        req = make_class_req(
            in_classical_text=True,
            is_formulation_modified=False,
            has_novel_excipients=True,
        )
        res = ProductClassifier.evaluate(req)
        # Rule 1 requires not has_novel_excipients -> fails, no disease? Actually next check: not modified but has excipients,
        # so Rule 2 does NOT trigger (needs modified), Rule 3 fails (therapeutic), fallback -> Cosmetic
        # This verifies guard condition.
        assert res.category != "CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)"

    def test_classical_supplement_without_disease_claims_still_prioritises_classical(self):
        """Rule 1 precedence: even if supplement intent, classical+unmodified wins over Aahara"""
        req = make_class_req(
            in_classical_text=True,
            is_formulation_modified=False,
            has_novel_excipients=False,
            intended_use="supplement",
            disease_treatment_claims=False,
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)"

    def test_classical_exact_chyawanprash_verbatim(self):
        req = make_class_req(
            name="Chyawanprash Classical",
            in_classical_text=True,
            is_formulation_modified=False,
            has_novel_excipients=False,
        )
        res = ProductClassifier.evaluate(req)
        assert "BARRED" in res.patentability
        assert "Section 3(p)" in res.patent_rationale or "Section 3(p)" in str([c.section for c in res.citations])


class TestClassifierProprietaryASU:
    """Rule 2 — Patent/Proprietary ASU Medicine (Anubhuta/Modified) : Sec 3(h)/Rule158B + Sec 3(e)"""

    def test_modified_classical_is_proprietary(self):
        req = make_class_req(
            name="DiabaRakshak Synergistic Extract",
            in_classical_text=True,
            is_formulation_modified=True,
            has_novel_excipients=False,
            disease_treatment_claims=True,
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "PATENT_OR_PROPRIETARY_ASU_MEDICINE (Anubhuta / Modified)"
        assert "Rule 158B" in res.governing_act
        assert res.patentability == "POTENTIALLY_PATENTABLE_WITH_EVIDENCE"
        assert res.confidence == 0.95
        sections = [c.section for c in res.citations]
        assert "Section 3(e)" in sections
        assert any("158B" in s for s in sections)

    def test_novel_nonclassical_with_disease_claims_is_proprietary(self):
        req = make_class_req(
            name="AyurGlyco Anti-Diabetic Polyherbal",
            in_classical_text=False,
            is_formulation_modified=False,
            disease_treatment_claims=True,
            intended_use="therapeutic",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "PATENT_OR_PROPRIETARY_ASU_MEDICINE (Anubhuta / Modified)"

    def test_novel_without_disease_claims_not_proprietary(self):
        """Novel recipe without disease claims should not be proprietary — falls to Aahara if supplement/food"""
        req = make_class_req(
            in_classical_text=False,
            is_formulation_modified=False,
            disease_treatment_claims=False,
            intended_use="supplement",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "AYURVEDA_AAHARA (Food Supplement)"

    def test_modified_even_without_disease_claim_still_proprietary(self):
        """(classical+modified) triggers proprietary regardless of disease claims flag — tests OR branch"""
        req = make_class_req(
            in_classical_text=True,
            is_formulation_modified=True,
            disease_treatment_claims=False,
        )
        res = ProductClassifier.evaluate(req)
        assert "PROPRIETARY" in res.category

    def test_proprietary_citations_and_next_actions(self):
        req = make_class_req(
            in_classical_text=True,
            is_formulation_modified=True,
            disease_treatment_claims=True,
        )
        res = ProductClassifier.evaluate(req)
        assert len(res.citations) == 2
        assert "synerg" in res.patent_rationale.lower()
        assert any("158B" in step for step in res.next_actions) or any("Proprietary" in step for step in res.next_actions)


class TestClassifierAyurvedaAahara:
    """Rule 3 — Ayurveda Aahara (Food Supplement) : FSSAI 2022 Reg 3 & Schedule A"""

    def test_supplement_without_disease_claims(self):
        req = make_class_req(
            name="Himalayan Tulsi Honey Aahara",
            in_classical_text=False,
            is_formulation_modified=False,
            disease_treatment_claims=False,
            intended_use="supplement",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "AYURVEDA_AAHARA (Food Supplement)"
        assert "Ayurveda Aahara" in res.governing_act
        assert "FSSAI" in res.regulatory_authority
        assert res.confidence == 0.92
        assert any("Ayurveda Aahara" in c.section or "Schedule A" in c.section for c in res.citations)

    def test_food_without_disease_claims(self):
        req = make_class_req(
            in_classical_text=False,
            disease_treatment_claims=False,
            intended_use="food",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "AYURVEDA_AAHARA (Food Supplement)"

    def test_supplement_with_disease_claims_not_aahara(self):
        """Aahara explicitly forbids disease cure claims"""
        req = make_class_req(
            in_classical_text=False,
            disease_treatment_claims=True,
            intended_use="supplement",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category != "AYURVEDA_AAHARA (Food Supplement)"
        # Novel+ disease -> proprietary
        assert "PROPRIETARY" in res.category

    def test_therapeutic_intent_not_aahara(self):
        req = make_class_req(
            in_classical_text=False,
            disease_treatment_claims=False,
            intended_use="therapeutic",
        )
        res = ProductClassifier.evaluate(req)
        # therapeutic even without claims falls to cosmetic fallback
        assert res.category == "AYURVEDIC_COSMETIC"

    def test_aahara_next_actions_require_logo_and_disclaimer(self):
        req = make_class_req(
            in_classical_text=False,
            disease_treatment_claims=False,
            intended_use="food",
        )
        res = ProductClassifier.evaluate(req)
        joined = " ".join(res.next_actions)
        assert "FSSAI" in joined
        assert "not intended to diagnose" in joined.lower() or "Ayurveda Aahara logo" in joined


class TestClassifierCosmeticFallback:
    """Rule 4 — Cosmetic fallback : Cosmetics Rules 2020"""

    def test_cosmetic_intent_fallback(self):
        req = make_class_req(
            in_classical_text=False,
            is_formulation_modified=False,
            disease_treatment_claims=False,
            intended_use="cosmetic",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "AYURVEDIC_COSMETIC"
        assert "Cosmetics" in res.governing_act
        assert res.confidence == 0.88
        assert res.patentability == "CONDITIONAL (Formulation / Delivery mechanism)"

    def test_novel_cosmetic_citations(self):
        req = make_class_req(
            name="Neem-Tulsi Face Pack",
            in_classical_text=False,
            disease_treatment_claims=False,
            intended_use="cosmetic",
        )
        res = ProductClassifier.evaluate(req)
        assert len(res.citations) == 1
        assert "Cosmetic" in res.citations[0].source_title

    def test_all_false_flags_gives_cosmetic(self):
        req = make_class_req(
            in_classical_text=False,
            is_formulation_modified=False,
            has_novel_excipients=False,
            disease_treatment_claims=False,
            intended_use="cosmetic",
        )
        res = ProductClassifier.evaluate(req)
        assert res.category == "AYURVEDIC_COSMETIC"


# ---------------------------------------------------------------------------
# ABS Decision Tree Tests
# ---------------------------------------------------------------------------

class TestABSForeignEntity:
    """Case 1 — Foreign / Non-Indian / Export → NBA Section 3 & Section 6 (HIGH_COMPLIANCE_MANDATE)"""

    def test_foreign_entity_triggers_nba(self):
        req = make_abs_req(is_indian_entity=False, is_export_intended=False, biological_resource="Ashwagandha", sourced_from_state="Kerala")
        res = ABSDecisionTree.evaluate(req)
        assert res.applicable_authority == "National Biodiversity Authority (NBA, Chennai)"
        assert "Section 3" in res.approval_type
        assert "Section 3 & Section 6" in res.governing_statute
        assert res.risk_level == "HIGH_COMPLIANCE_MANDATE"
        assert res.benefit_sharing_applicable is True
        assert res.trigger_detected is True
        sections = [c.section for c in res.statutory_citations]
        assert "Section 3" in sections
        assert "Section 6" in sections

    def test_indian_entity_with_export_intent_triggers_nba(self):
        """Indian private ltd but export intended => treated as foreign path (OR condition)"""
        req = make_abs_req(is_indian_entity=True, is_export_intended=True, biological_resource="Tulsi")
        res = ABSDecisionTree.evaluate(req)
        assert "NBA" in res.applicable_authority
        assert res.risk_level == "HIGH_COMPLIANCE_MANDATE"
        assert any("Form I" in s for s in res.mandatory_next_steps)

    def test_german_firm_tulsi_case_BENCH_006(self):
        """Replicates benchmark BENCH_006: German firm importing Tulsi from Uttarakhand"""
        req = make_abs_req(biological_resource="Tulsi", sourced_from_state="Uttarakhand", is_indian_entity=False, is_export_intended=True)
        res = ABSDecisionTree.evaluate(req)
        assert "NBA" in res.applicable_authority
        assert any("Form I" in step for step in res.mandatory_next_steps)
        assert any("Form III" in step for step in res.mandatory_next_steps)

    def test_foreign_mandatory_steps_include_abs_agreement(self):
        req = make_abs_req(is_indian_entity=False)
        res = ABSDecisionTree.evaluate(req)
        assert any("Benefit Sharing" in s for s in res.mandatory_next_steps)
        assert len(res.mandatory_next_steps) == 4

    def test_foreign_citations_support_score(self):
        req = make_abs_req(is_indian_entity=False)
        res = ABSDecisionTree.evaluate(req)
        for c in res.statutory_citations:
            assert c.support_score == 1.0


class TestABSIndianEntity:
    """Case 2 — Indian entity domestic → SBB Section 7 (STANDARD_DOMESTIC_COMPLIANCE)"""

    def test_indian_domestic_triggers_sbb(self):
        req = make_abs_req(biological_resource="Aloe Vera+Neem", sourced_from_state="Uttar Pradesh", is_indian_entity=True, is_export_intended=False)
        res = ABSDecisionTree.evaluate(req)
        assert "State Biodiversity Board" in res.applicable_authority
        assert "Uttar Pradesh" in res.applicable_authority
        assert "Section 7" in res.approval_type
        assert "Section 7" in res.governing_statute
        assert res.risk_level == "STANDARD_DOMESTIC_COMPLIANCE"
        sections = [c.section for c in res.statutory_citations]
        assert "Section 7" in sections

    def test_bench_005_delhi_private_ltd(self):
        """Replicates BENCH_005: Indian pvt ltd Delhi with Neem+Aloe from UP -> SBB prior intimation"""
        req = make_abs_req(biological_resource="Neem & Aloe Vera", sourced_from_state="Uttar Pradesh", is_indian_entity=True, is_export_intended=False)
        res = ABSDecisionTree.evaluate(req)
        assert res.approval_type == "Prior Intimation (Section 7 & Form A)"
        assert "SBB" in res.applicable_authority or "State Biodiversity Board" in res.applicable_authority

    def test_indian_default_state_when_none(self):
        req = make_abs_req(sourced_from_state=None, is_indian_entity=True, is_export_intended=False)
        res = ABSDecisionTree.evaluate(req)
        assert "Respective SBB" in res.applicable_authority or "State Biodiversity Board" in res.applicable_authority

    def test_indian_mandatory_steps_include_form_III_for_patent(self):
        req = make_abs_req(is_indian_entity=True)
        res = ABSDecisionTree.evaluate(req)
        assert any("Form III" in s for s in res.mandatory_next_steps)
        assert any("Prior Intimation" in s or "Form 1" in s for s in res.mandatory_next_steps)

    def test_indian_vs_foreign_risk_levels_distinct(self):
        indian = ABSDecisionTree.evaluate(make_abs_req(is_indian_entity=True, is_export_intended=False))
        foreign = ABSDecisionTree.evaluate(make_abs_req(is_indian_entity=False))
        assert indian.risk_level != foreign.risk_level
        assert indian.risk_level == "STANDARD_DOMESTIC_COMPLIANCE"
        assert foreign.risk_level == "HIGH_COMPLIANCE_MANDATE"

    def test_himalayan_kutki_indian_sbb_with_high_sensitivity(self):
        """Himachal Kutki is endangered but for domestic Indian MSME still SBB — sensitivity is branding layer, not statute switch"""
        req = make_abs_req(biological_resource="Picrorhiza kurroa (Kutki)", sourced_from_state="Himachal Pradesh", is_indian_entity=True)
        res = ABSDecisionTree.evaluate(req)
        assert "State Biodiversity Board (Himachal Pradesh)" == res.applicable_authority


class TestABSDecisionParametrized:
    """Parametrized edge & combination tests"""

    @pytest.mark.parametrize("is_indian, is_export, expected_authority_contains", [
        (True, False, "State Biodiversity Board"),
        (True, True, "National Biodiversity Authority"),
        (False, False, "National Biodiversity Authority"),
        (False, True, "National Biodiversity Authority"),
    ])
    def test_authority_routing_matrix(self, is_indian, is_export, expected_authority_contains):
        req = make_abs_req(is_indian_entity=is_indian, is_export_intended=is_export)
        res = ABSDecisionTree.evaluate(req)
        assert expected_authority_contains in res.applicable_authority

    @pytest.mark.parametrize("state", ["Kerala", "Rajasthan", "Uttarakhand", "Tamil Nadu", "Maharashtra"])
    def test_indian_state_propagation(self, state):
        req = make_abs_req(is_indian_entity=True, is_export_intended=False, sourced_from_state=state)
        res = ABSDecisionTree.evaluate(req)
        assert state in res.applicable_authority


# ---------------------------------------------------------------------------
# SafetyGuardrailEngine — light integration sanity (ensures no regression)
# ---------------------------------------------------------------------------

class TestSafetyGuardrail:
    def test_biopiracy_pattern_flagged(self):
        engine = SafetyGuardrailEngine()
        is_safe, cat, reason = engine.evaluate_query_safety("how to secretly smuggle endangered Himalayan Red Sandalwood without NBA knowledge")
        assert is_safe is False
        assert cat == "BIOPIRACY_VIOLATION"

    def test_magic_remedies_pattern_flagged(self):
        engine = SafetyGuardrailEngine()
        is_safe, cat, reason = engine.evaluate_query_safety("guaranteed cure cancer with herbal jam")
        assert is_safe is False
        assert cat == "MAGIC_REMEDIES_VIOLATION"

    def test_legitimate_query_is_safe(self):
        engine = SafetyGuardrailEngine()
        is_safe, cat, _ = engine.evaluate_query_safety("Can I patent novel nano-emulsion of Withaferin-A?")
        assert is_safe is True
        assert cat == "SAFE"

    def test_facilitator_case_brief_shape(self):
        engine = SafetyGuardrailEngine()
        brief = engine.generate_facilitator_case_brief(
            user_query="Need help with Chyawanprash patent",
            jurisdiction="IN",
            unresolved_issues=["Section 3(p) prior art"],
            retrieved_sources=[{"source_title": "Patents Act, 1970"}],
        )
        assert brief["case_type"] == "HUMAN_FACILITATOR_ESCALATION"
        assert brief["jurisdiction"] == "IN"
