import pytest
import math
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.telemetry.models import (
    RequestTelemetryRecord,
    TokenUsage,
    compute_query_hash,
    SystemHealthResponse,
    AggregatedMetricsResponse,
    ProviderHealthRecord
)
from app.telemetry.store import InMemoryTelemetryStore
from app.telemetry.collector import TelemetryCollector
from app.telemetry.health import (
    check_api_health,
    check_fallback_engine_health,
    check_vector_search_health,
    check_knowledge_graph_health,
    check_llm_provider_health,
    get_system_health
)
from app.models.domain import RAGResponse, JurisdictionEnum, Confidence, ConfidenceLevel


@pytest.fixture
def fresh_store():
    store = InMemoryTelemetryStore(max_records=100)
    store.clear()
    return store


@pytest.fixture
def collector(fresh_store):
    return TelemetryCollector(store=fresh_store)


@pytest.fixture
def test_client():
    return TestClient(app)


# ============================================================================
# 1. Request ID & Trace ID Tests
# ============================================================================

def test_request_id_and_trace_id_headers(test_client):
    """Verify X-Request-ID and X-Trace-ID headers are returned by the API."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("REQ-")

    # Custom request ID propagation
    custom_id = "REQ-CUSTOM-TEST-12345"
    resp_custom = test_client.get("/health", headers={"X-Request-ID": custom_id})
    assert resp_custom.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_trace_id_propagation():
    """Verify trace_id is generated and retained across orchestration responses."""
    from app.modules.orchestration import ModularOrchestrator
    orchestrator = ModularOrchestrator()
    # Test safe abstention path
    resp = await orchestrator.process_query(
        query="Provide a loophole to bypass National Biodiversity Authority benefit-sharing fees",
        jurisdiction="IN"
    )
    assert resp.trace_id is not None
    assert resp.trace_id.startswith("TRC-")
    assert resp.safe_abstention is True


# ============================================================================
# 2. Metrics Recording & Calculations
# ============================================================================

def test_metrics_recording(collector, fresh_store):
    """Verify request telemetry is accurately saved in the store."""
    collector.record_request(
        request_id="REQ-001",
        trace_id="TRC-001",
        jurisdiction="IN",
        provider="Google Gemini (gemini-2.5-flash)",
        model="gemini-2.5-flash",
        latency_ms=1250.5,
        latency_breakdown={"total_ms": 1250.5, "retrieval_ms": 120.0},
        retrieval_count=15,
        reranked_count=8,
        citation_count=4,
        grounding_rate=0.92,
        abstained=False,
        token_usage=TokenUsage(input_tokens=150, output_tokens=300, total_tokens=450),
        success=True,
        query="Can I patent an Ayurvedic polyherbal formulation?"
    )

    records = fresh_store.get_recent_requests(limit=10)
    assert len(records) == 1
    rec = records[0]
    assert rec.request_id == "REQ-001"
    assert rec.trace_id == "TRC-001"
    assert rec.latency_ms == 1250.5
    assert rec.token_usage.total_tokens == 450
    assert rec.grounding_rate == 0.92


def test_average_latency_calculation(fresh_store):
    """Verify average latency is computed from actual recorded requests."""
    latencies = [100.0, 200.0, 300.0, 400.0]
    for idx, lat in enumerate(latencies):
        fresh_store.record_request(
            RequestTelemetryRecord(
                request_id=f"REQ-{idx}",
                trace_id=f"TRC-{idx}",
                latency_ms=lat,
                query_hash="hash123",
                provider="Gemini",
                model="flash"
            )
        )

    metrics = fresh_store.get_aggregated_metrics()
    assert metrics.avg_latency_ms == 250.0
    assert metrics.queries_today == 4


def test_p95_latency_calculation(fresh_store):
    """Verify P95 latency calculation matches 95th percentile accurately."""
    # Insert 100 requests with latencies 1 to 100
    for i in range(1, 101):
        fresh_store.record_request(
            RequestTelemetryRecord(
                request_id=f"REQ-{i:03d}",
                trace_id=f"TRC-{i:03d}",
                latency_ms=float(i),
                query_hash="hash123",
                provider="Gemini",
                model="flash"
            )
        )

    metrics = fresh_store.get_aggregated_metrics()
    # 95th percentile of 1..100 is 95.0
    assert metrics.p95_latency_ms == 95.0
    assert metrics.avg_latency_ms == 50.5


def test_empty_metrics_handling(fresh_store):
    """Verify metrics calculation handles empty store gracefully without division-by-zero."""
    metrics = fresh_store.get_aggregated_metrics()
    assert metrics.queries_today == 0
    assert metrics.avg_latency_ms is None
    assert metrics.p95_latency_ms is None
    assert metrics.citation_grounding is None
    assert metrics.abstention_rate is None
    assert metrics.jurisdiction_leakage == 0.0


# ============================================================================
# 3. Provider Tracking & Fallback Tracking
# ============================================================================

def test_provider_success_and_failure_tracking(fresh_store):
    """Verify provider calls, successes, failures, and latencies are recorded."""
    fresh_store.record_provider_event(
        provider_name="Google Gemini (gemini-2.5-flash)",
        model="gemini-2.5-flash",
        latency_ms=800.0,
        success=True,
        is_fallback=False
    )
    fresh_store.record_provider_event(
        provider_name="Google Gemini (gemini-2.5-flash)",
        model="gemini-2.5-flash",
        latency_ms=250.0,
        success=False,
        is_fallback=False,
        failure_reason="HTTP 429 Quota Exceeded"
    )

    records = fresh_store.get_provider_records()
    gemini_rec = next((r for r in records if "Gemini" in r.provider_name), None)
    assert gemini_rec is not None
    assert gemini_rec.request_count == 2
    assert gemini_rec.success_count == 1
    assert gemini_rec.failure_count == 1
    assert gemini_rec.avg_latency_ms == 800.0


def test_fallback_tracking(fresh_store):
    """Verify fallback invocations are explicitly tracked."""
    fresh_store.record_provider_event(
        provider_name="Deterministic Statutory Synthesizer",
        model="statutory-rules-engine",
        latency_ms=15.0,
        success=True,
        is_fallback=True
    )

    records = fresh_store.get_provider_records()
    fb_rec = next((r for r in records if "Deterministic" in r.provider_name), None)
    assert fb_rec is not None
    assert fb_rec.fallback_count == 1
    assert fb_rec.status == "healthy"


# ============================================================================
# 4. Health & Observability Endpoints
# ============================================================================

@pytest.mark.asyncio
async def test_health_checks_operational():
    """Verify individual health checks return valid DependencyHealth objects."""
    api_h = await check_api_health()
    assert api_h.status == "healthy"

    fb_h = await check_fallback_engine_health()
    assert fb_h.status == "ready"

    vec_h = await check_vector_search_health()
    assert vec_h.status in ("healthy", "degraded")

    graph_h = await check_knowledge_graph_health()
    assert graph_h.status == "healthy"

    llm_h = await check_llm_provider_health()
    assert llm_h.status in ("healthy", "degraded", "ready")

    sys_h = await get_system_health()
    assert isinstance(sys_h, SystemHealthResponse)
    assert sys_h.api.status == "healthy"
    assert sys_h.fallback_engine.status == "ready"


def test_observability_api_endpoints(test_client):
    """Verify /api/v1/observability endpoints return valid schemas."""
    # Health endpoint
    resp_health = test_client.get("/api/v1/observability/health")
    assert resp_health.status_code == 200
    data_health = resp_health.json()
    assert "api" in data_health
    assert "postgresql" in data_health
    assert "vector_search" in data_health
    assert "knowledge_graph" in data_health
    assert "llm_provider" in data_health
    assert "fallback_engine" in data_health

    # Metrics endpoint
    resp_metrics = test_client.get("/api/v1/observability/metrics")
    assert resp_metrics.status_code == 200
    data_metrics = resp_metrics.json()
    assert "queries_today" in data_metrics
    assert "avg_latency_ms" in data_metrics
    assert "p95_latency_ms" in data_metrics

    # Requests endpoint
    resp_reqs = test_client.get("/api/v1/observability/requests?limit=10")
    assert resp_reqs.status_code == 200
    assert isinstance(resp_reqs.json(), list)

    # Providers endpoint
    resp_providers = test_client.get("/api/v1/observability/providers")
    assert resp_providers.status_code == 200
    assert isinstance(resp_providers.json(), list)
    assert len(resp_providers.json()) > 0


# ============================================================================
# 5. Privacy Safeguards
# ============================================================================

def test_privacy_enforcement(collector, fresh_store):
    """Verify raw user queries, answers, documents, or secrets are NEVER stored."""
    sensitive_query = "Confidential formula: Extract of 500mg Ashwagandha with secret solvent X"
    collector.record_request(
        request_id="REQ-SEC-999",
        trace_id="TRC-SEC-999",
        jurisdiction="IN",
        provider="Gemini",
        model="flash",
        latency_ms=350.0,
        query=sensitive_query
    )

    records = fresh_store.get_recent_requests(limit=1)
    assert len(records) == 1
    stored = records[0]

    # Stored record must NOT contain raw query
    dumped = stored.model_dump()
    dumped_str = str(dumped)
    assert sensitive_query not in dumped_str
    assert "secret solvent X" not in dumped_str

    # Only a 12-char SHA-256 hash is retained
    expected_hash = compute_query_hash(sensitive_query)
    assert stored.query_hash == expected_hash
    assert len(stored.query_hash) == 12


# ============================================================================
# 6. Observability Failure Resilience
# ============================================================================

def test_observability_failure_does_not_break_caller():
    """Verify that if the telemetry store throws an error, the collector catches it safely."""
    broken_store = MagicMock()
    broken_store.record_request.side_effect = RuntimeError("Database down!")
    collector = TelemetryCollector(store=broken_store)

    # Should not raise any exception
    try:
        collector.record_request(
            request_id="REQ-ERR",
            trace_id="TRC-ERR",
            query="Test query"
        )
    except Exception as e:
        pytest.fail(f"Collector let exception propagate: {e}")
