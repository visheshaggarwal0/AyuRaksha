"""
Test suite for TKDL Taxonomy Corpus Ingestion, Chunking, and Hybrid RAG Search
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.corpus.chunker import LegalDocumentChunker
from app.corpus.taxonomy import TKDLTaxonomyEngine
from app.engines.search import HybridLegalSearchEngine


class TestTaxonomyChunking:
    def test_extract_chunks_from_csvs_returns_records(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.extract_chunks_from_csvs()
        assert len(chunks) > 0

        source_ids = {c["source_id"] for c in chunks}
        assert "TKDL_MEDICINAL_PLANTS" in source_ids
        assert "TKDL_AYURVEDA_BOOKS" in source_ids
        assert "TKDL_AYURVEDIC_GLOSSARY" in source_ids

    def test_plant_chunks_contain_bda_and_patent_context(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.extract_chunks_from_csvs()
        plant_chunks = [c for c in chunks if c["source_id"] == "TKDL_MEDICINAL_PLANTS"]
        assert len(plant_chunks) >= 300

        first = plant_chunks[0]
        assert "Biological Diversity Act" in first["text"]
        assert "Section 3(p)" in first["text"]
        assert first["authority_level"] == 3
        assert first["domain"] == "BOTANICAL_TAXONOMY"

    def test_classical_books_chunks_reference_first_schedule(self):
        chunker = LegalDocumentChunker()
        chunks = chunker.extract_chunks_from_csvs()
        book_chunks = [c for c in chunks if c["source_id"] == "TKDL_AYURVEDA_BOOKS"]
        assert len(book_chunks) >= 100

        charaka_matches = [b for b in book_chunks if "Charaka" in b["heading"] or "Caraka" in b["heading"]]
        assert len(charaka_matches) > 0
        assert "First Schedule" in charaka_matches[0]["text"]
        assert charaka_matches[0]["authority_level"] == 4


class TestTaxonomyEngineLookups:
    def test_taxonomy_engine_loads_records(self):
        engine = TKDLTaxonomyEngine()
        stats = engine.get_corpus_statistics()
        assert stats["plants_count"] >= 300
        assert stats["classical_books_count"] >= 100
        assert stats["glossary_terms_count"] >= 400

    def test_resolve_botanicals_in_text(self):
        engine = TKDLTaxonomyEngine()
        resolved = engine.resolve_botanicals_in_text("I want to patent a polyherbal extract containing Ashwagandha and Neem.")
        matched_terms = [r["matched_term"] for r in resolved]
        assert any("ashwagandha" in t for t in matched_terms)

    def test_is_classical_text(self):
        engine = TKDLTaxonomyEngine()
        assert engine.is_classical_text("Charaka Samhita") is True
        assert engine.is_classical_text("Ashtanga Hridaya") is True
        assert engine.is_classical_text("Modern Medicine Handbook") is False


class TestTaxonomyRAGSearch:
    @pytest.mark.asyncio
    async def test_search_retrieves_botanical_and_statutory_context(self):
        search_engine = HybridLegalSearchEngine()
        results = await search_engine.search(query="Ashwagandha patent traditional knowledge", limit=5)
        assert len(results) > 0

        # Verify results contain either Patents Act or botanical records
        source_titles = [r.get("source_title", "") for r in results]
        assert any("Patent" in t or "TKDL" in t or "First Schedule" in t for t in source_titles)

    @pytest.mark.asyncio
    async def test_statute_outranks_taxonomy_when_searching_law(self):
        search_engine = HybridLegalSearchEngine()
        results = await search_engine.search(query="Section 3(p) traditional knowledge bar", limit=5)
        assert len(results) > 0
        top_result = results[0]
        # Top result should be the primary statute (Patents Act) with authority level 5
        assert top_result.get("authority_level", 1) >= 4
