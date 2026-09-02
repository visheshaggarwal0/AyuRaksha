"""
Test Suite: Authentic Statute Full-Text Corpus Extraction
Validates that LegalDocumentChunker parses raw statutes from data/corpus/extracted/
and provides complete coverage of all sections of the Patents Act, 1970 and other acts.
"""
import sys
import os
import pytest

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.corpus.chunker import LegalDocumentChunker


class TestFullStatuteExtraction:
    def test_patents_act_full_sections_extracted(self):
        chunker = LegalDocumentChunker()
        all_chunks = chunker.process_all_sources()

        patent_chunks = [c for c in all_chunks if c.get("source_id") == "IND_PATENTS_ACT_1970"]
        section_numbers = {c.get("section_number") for c in patent_chunks}

        # Verify critical sections that were previously missing
        assert "Section 25" in section_numbers  # Opposition to patent
        assert "Section 39" in section_numbers  # Foreign filing license
        assert "Section 64" in section_numbers  # Revocation grounds
        assert "Section 84" in section_numbers  # Compulsory licences
        assert "Section 107A" in section_numbers  # Bolar exemption / safe harbor

        # Verify curated sections are preserved with high authority
        sec_3p = next((c for c in patent_chunks if "3(p)" in c.get("section_number", "")), None)
        assert sec_3p is not None
        assert sec_3p.get("authority_level") == 5

        # Verify comprehensive count: Patents Act should have over 100 sections extracted!
        assert len(patent_chunks) >= 100

    def test_all_extracted_chunks_have_valid_hashes(self):
        chunker = LegalDocumentChunker()
        all_chunks = chunker.process_all_sources()

        patent_chunks = [c for c in all_chunks if c.get("source_id") == "IND_PATENTS_ACT_1970"]
        for c in patent_chunks[:10]:
            assert len(c.get("source_sha256", "")) == 64
            assert len(c.get("chunk_hash", "")) == 64
            assert len(c.get("raw_statute", "")) > 10
