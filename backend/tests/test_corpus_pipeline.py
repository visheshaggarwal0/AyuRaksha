import asyncio
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.corpus.normalizer import detect_provisions
from app.corpus.validation import CorpusValidationError, validate_normalized_document, validate_raw_source
from app.engines.reranker import LegalCitationReranker
from app.engines.verifier import CitationEntailmentVerifier
from app.models.schemas import Citation


def test_detect_provisions_preserves_section_boundaries():
    provisions = detect_provisions(
        "TEST_ACT",
        "Section 3 Patent exclusions\nTraditional knowledge is excluded.\n\nRule 7 Filing\nSubmit the required form.",
    )
    assert [provision["number"] for provision in provisions] == ["3", "7"]
    assert "Traditional knowledge" in provisions[0]["text"]


def test_validation_rejects_missing_provision_text():
    document = {
        "document_id": "TEST", "title": "Test", "jurisdiction": "IN", "authority": "Authority",
        "source": {"sha256": "a" * 64},
        "provisions": [{"provision_id": "ONE", "number": "1", "text": ""}],
    }
    with pytest.raises(CorpusValidationError):
        validate_normalized_document(document)


def test_raw_hash_validation_detects_tampering(tmp_path):
    raw_file = tmp_path / "source.txt"
    raw_file.write_text("authoritative source", encoding="utf-8")
    with pytest.raises(CorpusValidationError):
        validate_raw_source(raw_file, "0" * 64)


def test_reranker_prefers_exact_section_and_authority():
    candidates = [
        {"text": "Traditional knowledge is not patentable.", "section_number": "Section 3(p)", "authority_level": 5, "fused_score": 0.02},
        {"text": "Patent filing guide.", "section_number": "Section 1", "authority_level": 2, "fused_score": 0.02},
    ]
    ranked = LegalCitationReranker().rerank("What does Section 3(p) say about traditional knowledge?", candidates)
    assert ranked[0]["section_number"] == "Section 3(p)"


def test_verifier_never_marks_an_unsupported_claim_as_confident():
    citation = Citation(
        source_id="TEST", source_title="Test Act", section="Section 3", jurisdiction="IN",
        verbatim_quote="The authority may maintain a register.",
    )
    verification = CitationEntailmentVerifier.verify("Patents are automatically granted for herbs.", [citation])
    assert verification.is_supported is False
    assert verification.confidence_score == 0.0
