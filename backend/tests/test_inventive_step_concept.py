"""
Tests for Systematic Resolution of Inventive Step (Section 2(1)(ja))
Verifies that Section 2(1)(ja) is resolved via the Legal Concept Layer
across multiple semantic variants of non-obviousness and technical advance,
without relying on brittle keyword hacks.
"""
import pytest
from app.modules.concepts import concept_engine
from app.agents.orchestrator import AyuRakshaOrchestrator


class TestInventiveStepConceptResolution:
    """Validates concept resolution for inventive step variants."""

    def test_semantic_variant_technological_advance(self):
        query = "Does a technological advance over prior art suffice to patent an herbal extraction technique?"
        concepts = concept_engine.resolve_concepts(query)
        concept_ids = [c.concept_id for c in concepts]
        assert "INVENTIVE_STEP" in concept_ids
        inv_step = next(c for c in concepts if c.concept_id == "INVENTIVE_STEP")
        assert "PATENTS_ACT_1970_SEC_2_1_JA" in inv_step.statutory_provisions

    def test_semantic_variant_non_obviousness(self):
        query = "How does the patent office evaluate non-obviousness in improved herbal delivery systems?"
        concepts = concept_engine.resolve_concepts(query)
        concept_ids = [c.concept_id for c in concepts]
        assert "INVENTIVE_STEP" in concept_ids
        inv_step = next(c for c in concepts if c.concept_id == "INVENTIVE_STEP")
        assert "non-obvious" in inv_step.matched_triggers or "delivery system" in inv_step.matched_triggers

    def test_semantic_variant_economic_significance(self):
        query = "We have established economic significance and superior stability for a plant isolate; what section applies?"
        concepts = concept_engine.resolve_concepts(query)
        concept_ids = [c.concept_id for c in concepts]
        assert "INVENTIVE_STEP" in concept_ids
        inv_step = next(c for c in concepts if c.concept_id == "INVENTIVE_STEP")
        assert "economic significance" in inv_step.matched_triggers

    def test_semantic_variant_inventive_step_objection(self):
        query = "Overcoming an inventive step objection from the patent examiner for botanical formulations."
        concepts = concept_engine.resolve_concepts(query)
        concept_ids = [c.concept_id for c in concepts]
        assert "INVENTIVE_STEP" in concept_ids
        expanded_query = concept_engine.expand_retrieval_query(query, concepts)
        assert "2(1)(ja)" in expanded_query

    def test_semantic_variant_nano_emulsion_extraction(self):
        query = "Is a novel nano-emulsion extraction process of Withaferin-A patentable in India?"
        concepts = concept_engine.resolve_concepts(query)
        concept_ids = [c.concept_id for c in concepts]
        assert "INVENTIVE_STEP" in concept_ids
        assert "THERAPEUTIC_EFFICACY_DERIVATIVE" in concept_ids
        expanded_query = concept_engine.expand_retrieval_query(query, concepts)
        assert "2(1)(ja)" in expanded_query
        assert "3(d)" in expanded_query


@pytest.mark.asyncio
class TestInventiveStepEndToEndRetrieval:
    """Verifies end-to-end retrieval of Section 2(1)(ja) in orchestrated answers."""

    async def test_end_to_end_nano_emulsion_includes_2_1_ja(self):
        orchestrator = AyuRakshaOrchestrator()
        query = "Is a novel nano-emulsion extraction process of Withaferin-A from Withania somnifera patentable in India?"
        ans = await orchestrator.process_query(query)
        sections = [f"{c.section.lower()} {c.source_title.lower()}" for c in ans.citations]
        
        # Must retrieve Section 2(1)(ja), Section 3(d), Section 2(1)(j), and Section 3(p)
        has_2_1_ja = any("2(1)(ja)" in s for s in sections)
        has_3_d = any("3(d)" in s for s in sections)
        assert has_2_1_ja, f"Section 2(1)(ja) must be retrieved in citations: {sections}"
        assert has_3_d, f"Section 3(d) must be retrieved in citations: {sections}"
        assert "INVENTIVE_STEP" in ans.resolved_concepts
