import time
import asyncio
import logging
from typing import Dict, Any, Optional
from sqlalchemy import text

from app.core.config import settings
from app.telemetry.models import DependencyHealth, SystemHealthResponse

logger = logging.getLogger("AyuRaksha.TelemetryHealth")


async def check_api_health() -> DependencyHealth:
    """Checks API gateway process liveness."""
    t0 = time.perf_counter()
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    return DependencyHealth(
        status="healthy",
        latency_ms=latency_ms,
        message=f"AyuRaksha API v1.0.0 ({settings.APP_ENV}) operational"
    )


async def check_database_health() -> DependencyHealth:
    """Checks PostgreSQL (Neon) connectivity with strict 1.5s timeout."""
    t0 = time.perf_counter()
    try:
        from app.db.session import AsyncSessionLocal
        if AsyncSessionLocal is None:
            return DependencyHealth(
                status="unavailable",
                latency_ms=None,
                message="PostgreSQL engine offline or DATABASE_URL not configured"
            )

        async def _query():
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))

        await asyncio.wait_for(_query(), timeout=1.5)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="healthy",
            latency_ms=latency_ms,
            message="Neon PostgreSQL connected and responsive"
        )
    except asyncio.TimeoutError:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="unavailable",
            latency_ms=latency_ms,
            message="Database connection timed out (>1.5s)"
        )
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="degraded",
            latency_ms=latency_ms,
            message=f"Database check failed: {str(e)[:120]}"
        )


async def check_vector_search_health() -> DependencyHealth:
    """Checks Vector Search engine & embedding model readiness."""
    t0 = time.perf_counter()
    try:
        from app.modules.embeddings import embedding_module
        model = embedding_module._get_model()
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        if model is not None:
            return DependencyHealth(
                status="healthy",
                latency_ms=latency_ms,
                message="SentenceTransformer all-MiniLM-L6-v2 (384-dim) active",
                details={"dimension": 384, "model": "all-MiniLM-L6-v2"}
            )
        else:
            return DependencyHealth(
                status="healthy",
                latency_ms=latency_ms,
                message="Deterministic 384-dim fallback vector index active",
                details={"dimension": 384, "model": "deterministic-fallback"}
            )
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="degraded",
            latency_ms=latency_ms,
            message=f"Vector model check warning: {str(e)[:100]}"
        )


async def check_knowledge_graph_health() -> DependencyHealth:
    """Checks statutory knowledge graph retriever and relation tables."""
    t0 = time.perf_counter()
    try:
        from app.modules.retrieval.graph import IndependentGraphRetriever
        relations_count = sum(len(v) for v in IndependentGraphRetriever.STATUTORY_GRAPH.values())
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="healthy",
            latency_ms=latency_ms,
            message=f"Statutory Knowledge Graph online ({relations_count} verified relations)",
            details={"static_relations_count": relations_count}
        )
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="degraded",
            latency_ms=latency_ms,
            message=f"Knowledge graph check error: {str(e)[:100]}"
        )


async def check_llm_provider_health() -> DependencyHealth:
    """Inspects primary LLM provider status and circuit breaker conditions."""
    t0 = time.perf_counter()
    try:
        from app.modules.generation import generation_module
        active_name = generation_module.active_provider_name
        providers = generation_module._providers

        # Inspect providers
        available_providers = []
        circuit_open_providers = []
        for _, prov in providers:
            is_circuit_broken = getattr(prov, "_circuit_broken", False)
            if is_circuit_broken:
                circuit_open_providers.append(prov.provider_name)
            elif prov.is_available():
                available_providers.append(prov.provider_name)

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        if available_providers:
            status = "healthy"
            msg = f"Available: {', '.join(available_providers[:2])}"
            if circuit_open_providers:
                msg += f" (Circuit open: {', '.join(circuit_open_providers)})"
        elif circuit_open_providers:
            status = "degraded"
            msg = f"Circuit open for: {', '.join(circuit_open_providers)}"
        else:
            status = "ready"
            msg = "Fallback engine ready; no cloud API key provided"

        return DependencyHealth(
            status=status,
            latency_ms=latency_ms,
            message=msg,
            details={
                "active_provider": active_name,
                "available": available_providers,
                "circuit_open": circuit_open_providers
            }
        )
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="degraded",
            latency_ms=latency_ms,
            message=f"Provider check warning: {str(e)[:100]}"
        )


async def check_fallback_engine_health() -> DependencyHealth:
    """Checks the zero-crash Deterministic Statutory Synthesizer."""
    t0 = time.perf_counter()
    try:
        from app.modules.generation.providers import DeterministicStatutoryProvider
        provider = DeterministicStatutoryProvider()
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="ready",
            latency_ms=latency_ms,
            message="Deterministic Statutory Synthesizer standby & ready"
        )
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return DependencyHealth(
            status="degraded",
            latency_ms=latency_ms,
            message=f"Fallback engine error: {str(e)[:100]}"
        )


async def get_system_health() -> SystemHealthResponse:
    """Gathers concurrent health checks across all dependencies with safety timeouts."""
    api_task = check_api_health()
    db_task = check_database_health()
    vector_task = check_vector_search_health()
    graph_task = check_knowledge_graph_health()
    llm_task = check_llm_provider_health()
    fallback_task = check_fallback_engine_health()

    results = await asyncio.gather(
        api_task, db_task, vector_task, graph_task, llm_task, fallback_task,
        return_exceptions=True
    )

    def _safe_res(res, fallback_name) -> DependencyHealth:
        if isinstance(res, Exception):
            return DependencyHealth(status="degraded", message=f"{fallback_name} check failed: {str(res)}")
        return res

    return SystemHealthResponse(
        api=_safe_res(results[0], "API"),
        postgresql=_safe_res(results[1], "PostgreSQL"),
        vector_search=_safe_res(results[2], "Vector Search"),
        knowledge_graph=_safe_res(results[3], "Knowledge Graph"),
        llm_provider=_safe_res(results[4], "LLM Provider"),
        fallback_engine=_safe_res(results[5], "Fallback Engine")
    )
