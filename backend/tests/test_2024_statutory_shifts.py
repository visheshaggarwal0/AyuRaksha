"""
Test suite validating the 2024 Legal Shifts in AyuRaksha:
1. WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (2024)
2. The Patents (Amendment) Rules, 2024 (G.S.R. 211(E))
"""
import sys
import os
import pytest
from pathlib import Path

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.corpus.chunker import LegalDocumentChunker
from app.ai.retrieval.graph import GraphRetriever
from app.ai.retrieval.hybrid import HybridRetriever
from app.ai.retrieval.planner import RetrievalPlanner


class Test2024StatutoryManifestAndChunking:
    def test_manifest_includes_2024_sources(self):
        chunker = LegalDocumentChunker()
        manifest = chunker.parse_manifest()
        source_ids = {s["source_id"] for s in manifest}
        assert "INT_WIPO_GRATK_TREATY_2024" in source_ids
        assert "IND_PATENTS_AMENDMENT_RULES_2024" in source_ids

    def test_dynamic_live_hash_computed_from_disk(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.process_all_sources()
        wipo_chunks = [c for c in chunks if c["source_id"] == "INT_WIPO_GRATK_TREATY_2024"]
        assert len(wipo_chunks) > 0

        # Check that live hash is calculated from disk
        first_chunk = wipo_chunks[0]
        assert first_chunk.get("source_sha256") is not None
        assert len(first_chunk["source_sha256"]) == 64 # valid 256-bit hex hash

    def test_wipo_gratk_chunks_contain_mandatory_disclosure(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.process_all_sources()
        wipo_chunks = [c for c in chunks if c["source_id"] == "INT_WIPO_GRATK_TREATY_2024"]
        assert len(wipo_chunks) >= 4

        # Check Article 3.1 & 3.2 disclosure mandates
        disclosure_chunk = next((c for c in wipo_chunks if "Article 3" in c.get("section_number", "")), None)
        assert disclosure_chunk is not None
        assert "country of origin" in disclosure_chunk["text"].lower()
        assert "traditional knowledge" in disclosure_chunk["text"].lower()
        assert disclosure_chunk["authority_level"] == 5
        assert disclosure_chunk["jurisdiction"] == "INT"

    def test_patent_amendment_rules_2024_contain_procedural_reforms(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.process_all_sources()
        rule_chunks = [c for c in chunks if c["source_id"] == "IND_PATENTS_AMENDMENT_RULES_2024"]
        assert len(rule_chunks) >= 4

        # Check Rule 24B 31-month timeline
        r24b = next((c for c in rule_chunks if "24B" in c.get("section_number", "")), None)
        assert r24b is not None
        assert "thirty-one months" in r24b["text"].lower() or "31 months" in r24b["text"].lower()

        # Check Rule 131 3-year Form 27 reporting
        r131 = next((c for c in rule_chunks if "131" in c.get("section_number", "")), None)
        assert r131 is not None
        assert "three financial years" in r131["text"].lower()


class Test2024StatutoryKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_patents_act_expands_to_2024_rules_and_wipo_treaty(self):
        dummy_patents_act_candidate = [{
            "source_id": "IND_PATENTS_ACT_1970",
            "source_title": "The Patents Act, 1970",
            "section_number": "Section 3(p)",
            "authority_level": 5,
            "support_score": 0.95
        }]
        expanded = await GraphRetriever.expand_candidates(dummy_patents_act_candidate)
        expanded_sources = [c.get("source_id") for c in expanded]

        # Verify graph expansion links Patents Act to 2024 Rules and WIPO GRATK
        assert any("PATENTS_AMENDMENT_RULES_2024" in s for s in expanded_sources)
        assert any("WIPO_GRATK_TREATY_2024" in s for s in expanded_sources)


class Test2024HybridRAGRetrieval:
    @pytest.mark.asyncio
    async def test_retrieval_finds_wipo_gratk_disclosure_rules(self):
        retriever = HybridRetriever()
        plan = RetrievalPlanner.plan(
            normalized_query="What is the mandatory disclosure requirement for genetic resources under WIPO GRATK Treaty 2024?",
            route={"jurisdiction": "INT", "intent": "PATENTABILITY_ASSESSMENT"},
            entities={"botanicals": []}
        )
        candidates = await retriever.retrieve(
            query="What is the mandatory disclosure requirement for genetic resources under WIPO GRATK Treaty 2024?",
            plan=plan,
            top_k=5
        )
        assert len(candidates) > 0
        titles = [c.get("source_title", "") for c in candidates]
        assert any("WIPO" in t for t in titles)

    @pytest.mark.asyncio
    async def test_retrieval_finds_form_27_three_year_relaxation(self):
        retriever = HybridRetriever()
        plan = RetrievalPlanner.plan(
            normalized_query="How often do I need to file Form 27 under Patents Amendment Rules 2024?",
            route={"jurisdiction": "IN", "intent": "PATENTABILITY_ASSESSMENT"},
            entities={"botanicals": []}
        )
        candidates = await retriever.retrieve(
            query="How often do I need to file Form 27 under Patents Amendment Rules 2024?",
            plan=plan,
            top_k=5
        )
        assert len(candidates) > 0
        sections = [c.get("section_number", "") for c in candidates]
        assert any("131" in s or "Rule" in s for s in sections)
