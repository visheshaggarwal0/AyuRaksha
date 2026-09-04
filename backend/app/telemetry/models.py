import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


def compute_query_hash(query: str) -> str:
    """Produces a privacy-preserving 12-char SHA-256 one-way hash for query correlation."""
    if not query:
        return "empty"
    return hashlib.sha256(query.strip().encode("utf-8")).hexdigest()[:12]


class TokenUsage(BaseModel):
    """Actual token counts reported by the LLM provider. Null if unavailable."""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class RequestTelemetryRecord(BaseModel):
    """
    Privacy-safe operational record of an individual request.
    NEVER contains raw queries, prompts, answers, retrieved text, or credentials.
    """
    request_id: str = Field(..., description="Unique request identifier, e.g. REQ-...")
    trace_id: str = Field(..., description="Correlated trace identifier, e.g. TRC-...")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    jurisdiction: str = Field(default="IN")
    provider: str = Field(default="Unknown")
    model: str = Field(default="unknown")
    latency_ms: float = Field(default=0.0)
    latency_breakdown: Dict[str, float] = Field(default_factory=dict)
    retrieval_count: int = Field(default=0)
    reranked_count: int = Field(default=0)
    citation_count: int = Field(default=0)
    grounding_rate: Optional[float] = None
    abstained: bool = Field(default=False)
    failure_reason: Optional[str] = None
    token_usage: Optional[TokenUsage] = None
    success: bool = Field(default=True)
    query_hash: str = Field(..., description="One-way SHA-256 hash prefix for correlation")


class DependencyHealth(BaseModel):
    """Health status and diagnosis for an individual dependency."""
    status: str = Field(..., description="healthy | degraded | unavailable | ready")
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SystemHealthResponse(BaseModel):
    """Aggregate system health across all core AyuRaksha components."""
    api: DependencyHealth
    postgresql: DependencyHealth
    vector_search: DependencyHealth
    knowledge_graph: DependencyHealth
    llm_provider: DependencyHealth
    fallback_engine: DependencyHealth
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProviderHealthRecord(BaseModel):
    """Status, circuit-breaker condition, and operational metrics for an LLM provider."""
    provider_name: str
    model: str
    status: str = Field(..., description="healthy | circuit_open | unavailable | ready")
    circuit_breaker_status: str = Field(..., description="closed | open | unavailable | ready")
    circuit_cooldown_remaining_sec: float = 0.0
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: Optional[float] = None
    fallback_count: int = 0


class AggregatedMetricsResponse(BaseModel):
    """Real aggregated metrics derived from actual application activity."""
    queries_today: int = 0
    avg_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    citation_grounding: Optional[float] = None
    abstention_rate: Optional[float] = None
    jurisdiction_leakage: float = 0.0
    total_requests_recorded: int = 0
    provider_statistics: Dict[str, Any] = Field(default_factory=dict)
    retrieval_statistics: Dict[str, Any] = Field(default_factory=dict)
    failure_statistics: Dict[str, Any] = Field(default_factory=dict)
