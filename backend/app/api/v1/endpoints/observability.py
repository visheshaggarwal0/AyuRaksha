from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional

from app.telemetry.models import (
    SystemHealthResponse,
    AggregatedMetricsResponse,
    RequestTelemetryRecord,
    ProviderHealthRecord
)
from app.telemetry.health import get_system_health
from app.telemetry.store import telemetry_store
from app.modules.generation import generation_module

router = APIRouter(prefix="/observability", tags=["Observability & System Health"])


@router.get("/health", response_model=SystemHealthResponse)
async def get_health():
    """
    Live dependency health endpoint.
    Actively probes API, PostgreSQL, Vector Search, Knowledge Graph, LLM Provider, and Fallback Engine with timeouts.
    """
    return await get_system_health()


@router.get("/metrics", response_model=AggregatedMetricsResponse)
async def get_metrics():
    """
    Real-time aggregated performance, quality, and retrieval metrics derived from actual application traffic.
    Returns null/0/N/A when there is insufficient data; never fabricates numbers.
    """
    return telemetry_store.get_aggregated_metrics()


@router.get("/requests", response_model=List[RequestTelemetryRecord])
async def get_recent_requests(
    limit: int = Query(default=20, ge=1, le=100, description="Number of recent request records to return")
):
    """
    Recent operational request metadata for monitoring and debugging.
    Privacy-protected: does NOT contain user queries, prompts, answers, retrieved document text, or secrets.
    """
    return telemetry_store.get_recent_requests(limit=limit)


@router.get("/providers", response_model=List[ProviderHealthRecord])
async def get_providers():
    """
    Real-time LLM provider health, circuit breaker statuses, operational counts, and fallback statistics.
    """
    return generation_module.get_providers_status()
