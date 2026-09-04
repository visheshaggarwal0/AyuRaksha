import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.telemetry.models import (
    RequestTelemetryRecord,
    TokenUsage,
    compute_query_hash
)
from app.telemetry.store import telemetry_store, ITelemetryStore

logger = logging.getLogger("AyuRaksha.TelemetryCollector")


class TelemetryCollector:
    """
    Best-effort operational telemetry collector.
    Guarantees that telemetry failures never crash or disrupt user requests.
    Enforces strict privacy: never stores raw user queries, answers, or prompts.
    """

    def __init__(self, store: Optional[ITelemetryStore] = None):
        self.store = store or telemetry_store

    def record_request(
        self,
        request_id: str,
        trace_id: str,
        jurisdiction: str = "IN",
        provider: str = "Unknown",
        model: str = "unknown",
        latency_ms: float = 0.0,
        latency_breakdown: Optional[Dict[str, float]] = None,
        retrieval_count: int = 0,
        reranked_count: int = 0,
        citation_count: int = 0,
        grounding_rate: Optional[float] = None,
        abstained: bool = False,
        failure_reason: Optional[str] = None,
        token_usage: Optional[TokenUsage] = None,
        success: bool = True,
        query: str = ""
    ) -> None:
        """Records a single operational request record safely."""
        try:
            record = RequestTelemetryRecord(
                request_id=request_id or f"REQ-{trace_id[-8:] if trace_id else '0000'}",
                trace_id=trace_id or "TRC-NONE",
                timestamp=datetime.now(timezone.utc),
                jurisdiction=jurisdiction,
                provider=provider,
                model=model,
                latency_ms=round(max(0.0, latency_ms), 2),
                latency_breakdown=latency_breakdown or {},
                retrieval_count=retrieval_count,
                reranked_count=reranked_count,
                citation_count=citation_count,
                grounding_rate=grounding_rate,
                abstained=abstained,
                failure_reason=failure_reason,
                token_usage=token_usage,
                success=success,
                query_hash=compute_query_hash(query)
            )
            self.store.record_request(record)
        except Exception as e:
            logger.warning("Failed to record request telemetry: %s", e)

    def record_orchestration_response(
        self,
        response_obj: Any,
        query: str,
        request_id: Optional[str] = None,
        token_usage: Optional[TokenUsage] = None,
        success: bool = True,
        failure_reason: Optional[str] = None
    ) -> None:
        """Extracts telemetry fields from an orchestrator RAGResponse or dict."""
        try:
            trace_id = getattr(response_obj, "trace_id", None) or "TRC-UNKNOWN"
            req_id = request_id or f"REQ-{trace_id[-8:]}"

            # Extract jurisdiction
            jur = getattr(response_obj, "jurisdiction", "IN")
            if hasattr(jur, "value"):
                jur = jur.value

            # Extract diagnostics
            diag = getattr(response_obj, "diagnostics", {}) or {}
            ret_count = diag.get("candidates_retrieved_count", 0)
            rerank_count = diag.get("candidates_reranked_count", 0)
            cit_count = diag.get("citations_extracted_count", 0) or len(getattr(response_obj, "citations", []) or [])
            provider_name = diag.get("generation_provider", "Unknown")

            # Extract confidence / grounding
            conf = getattr(response_obj, "confidence", None)
            grounding_rate = None
            if conf and hasattr(conf, "grounding_rate"):
                grounding_rate = conf.grounding_rate
            elif "grounding_rate" in diag:
                grounding_rate = diag["grounding_rate"]

            # Extract abstention
            abstained = getattr(response_obj, "safe_abstention", False)
            if not abstained and diag.get("abstained"):
                abstained = True

            # Latency
            lat_breakdown = getattr(response_obj, "latency_breakdown", {}) or {}
            total_lat = lat_breakdown.get("total_ms", 0.0)

            # Extract model from provider string if possible
            model = "unknown"
            if "(" in provider_name and ")" in provider_name:
                model = provider_name.split("(")[1].split(")")[0].strip()

            self.record_request(
                request_id=req_id,
                trace_id=trace_id,
                jurisdiction=str(jur),
                provider=provider_name,
                model=model,
                latency_ms=total_lat,
                latency_breakdown=lat_breakdown,
                retrieval_count=ret_count,
                reranked_count=rerank_count,
                citation_count=cit_count,
                grounding_rate=grounding_rate,
                abstained=abstained,
                failure_reason=failure_reason,
                token_usage=token_usage,
                success=success,
                query=query
            )
        except Exception as e:
            logger.warning("Failed to parse orchestration response for telemetry: %s", e)

    def record_provider_call(
        self,
        provider_name: str,
        model: str,
        latency_ms: float,
        success: bool,
        is_fallback: bool = False,
        failure_reason: Optional[str] = None
    ) -> None:
        """Records provider-level outcome safely."""
        try:
            self.store.record_provider_event(
                provider_name=provider_name,
                model=model,
                latency_ms=latency_ms,
                success=success,
                is_fallback=is_fallback,
                failure_reason=failure_reason
            )
        except Exception as e:
            logger.warning("Failed to record provider telemetry: %s", e)


# Default singleton instance
telemetry_collector = TelemetryCollector()
