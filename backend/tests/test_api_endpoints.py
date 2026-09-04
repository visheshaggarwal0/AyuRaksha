"""
HTTP-layer happy-path tests for the FastAPI /api/v1 endpoints.

These tests exercise the full request/response cycle through the ASGI app
(TestClient), including serialization, request validation, response-model
coercion, and header propagation. The database dependency degrades to a
safe MockSession when no real database is configured, and the LLM layer
degrades to deterministic/safe-abstention fallbacks, so these tests run
hermetically without external services.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. /chat endpoints
# ============================================================================

def test_chat_query_returns_structured_answer(client):
    """POST /api/v1/chat/query returns a valid structured, citation-grounded answer."""
    payload = {
        "query": "Is a classical Ayurvedic formulation containing Ashwagandha patentable in India?",
        "jurisdiction": "IN",
        "language": "en",
    }
    resp = client.post("/api/v1/chat/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "direct_answer" in data
    assert isinstance(data["direct_answer"], str) and len(data["direct_answer"]) > 0
    assert "citations" in data
    assert isinstance(data["citations"], list)
    # Request/trace header propagation
    assert resp.headers.get("X-Request-ID", "").startswith("REQ-")


def test_chat_query_validates_min_length(client):
    """A query shorter than the minimum length is rejected with 422."""
    resp = client.post("/api/v1/chat/query", json={"query": "ok", "jurisdiction": "INDIA"})
    assert resp.status_code == 422


def test_chat_stream_returns_sse_events(client):
    """POST /api/v1/chat/stream emits a Server-Sent Events (SSE) response."""
    payload = {
        "query": "What filing is required for export of Ashwagandha extract to the EU?",
        "jurisdiction": "IN",
        "language": "en",
    }
    resp = client.post("/api/v1/chat/stream", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert "data:" in resp.text
    assert resp.text.count("event:") >= 1


# ============================================================================
# 2. /abs endpoints
# ============================================================================

def test_abs_evaluate_returns_assessment(client):
    """POST /api/v1/abs/evaluate returns an ABS compliance determination."""
    payload = {
        "biological_resource": "Ashwagandha",
        "origin_country": "India",
        "is_commercial_utilization": True,
        "is_traditional_knowledge_associated": True,
        "is_indian_entity": True,
        "is_export_intended": False,
    }
    resp = client.post("/api/v1/abs/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["resource"] == "Ashwagandha"
    assert data["governing_statute"]
    assert data["approval_type"]
    assert isinstance(data["statutory_citations"], list)
    assert len(data["statutory_citations"]) > 0


# ============================================================================
# 3. /classification endpoints
# ============================================================================

def test_classification_evaluate_returns_classification(client):
    """POST /api/v1/classification/evaluate returns a deterministic classification."""
    payload = {
        "name": "AshwaNeuro Boost Capsule",
        "in_classical_text": False,
        "is_formulation_modified": True,
        "has_novel_excipients": True,
        "is_purified_standardized_fraction": True,
        "intended_use": "therapeutic",
        "disease_treatment_claims": True,
        "has_biological_resources": True,
        "target_market": "IN",
    }
    resp = client.post("/api/v1/classification/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_name"] == "AshwaNeuro Boost Capsule"
    assert data["category"]
    assert data["governing_act"]
    assert data["patentability"]
    assert isinstance(data["citations"], list)


# ============================================================================
# 4. /corpus endpoints
# ============================================================================

def test_corpus_manifest_returns_sources(client):
    """GET /api/v1/corpus/manifest returns the statutory manifest."""
    resp = client.get("/api/v1/corpus/manifest")
    assert resp.status_code == 200
    manifest = resp.json()
    assert isinstance(manifest, list)
    assert len(manifest) > 0


def test_corpus_books_search(client):
    """GET /api/v1/corpus/books returns classical text search results."""
    resp = client.get("/api/v1/corpus/books", params={"query": "Charaka", "limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_corpus_plants_search(client):
    """GET /api/v1/corpus/plants returns botanical taxonomy results."""
    resp = client.get("/api/v1/corpus/plants", params={"query": "ashwagandha", "limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_corpus_stats_returns_counts(client):
    """GET /api/v1/corpus/stats returns corpus statistics."""
    resp = client.get("/api/v1/corpus/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "statutory_manifest_count" in data
    assert data["statutory_manifest_count"] > 0


# ============================================================================
# 5. /dossier endpoints
# ============================================================================

def test_dossier_generate_returns_dossier(client):
    """POST /api/v1/dossier/generate returns an audit-ready compliance dossier."""
    payload = {
        "product_name": "AshwaCurcumin Extract",
        "ingredients": ["Ashwagandha", "Turmeric", "Black Pepper"],
        "in_classical_text": False,
        "is_formulation_modified": True,
        "is_purified_standardized_fraction": True,
        "intended_use": "therapeutic",
        "disease_treatment_claims": True,
        "is_indian_entity": True,
        "target_market": "IN",
    }
    resp = client.post("/api/v1/dossier/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "dossier_id" in data
    assert "product_profile" in data
    assert "filing_roadmap" in data
    assert data["product_profile"]["name"] == "AshwaCurcumin Extract"
    assert len(data["verifiable_citations"]) > 0


def test_dossier_sample_returns_dossier(client):
    """GET /api/v1/dossier/sample returns an instant sample dossier."""
    resp = client.get("/api/v1/dossier/sample")
    assert resp.status_code == 200
    data = resp.json()
    assert "dossier_id" in data
    assert "product_profile" in data


def test_dossier_export_markdown(client):
    """POST /api/v1/dossier/export-markdown returns a downloadable Markdown document."""
    payload = {
        "product_name": "AshwaTest Tonic",
        "ingredients": ["Ashwagandha"],
        "in_classical_text": True,
        "is_formulation_modified": False,
        "intended_use": "supplement",
        "target_market": "IN",
    }
    resp = client.post("/api/v1/dossier/export-markdown", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    assert "Content-Disposition" in resp.headers
    assert "ashwatest" in resp.headers["Content-Disposition"]
