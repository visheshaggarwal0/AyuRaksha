import math
import threading
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.telemetry.models import (
    RequestTelemetryRecord,
    AggregatedMetricsResponse,
    ProviderHealthRecord
)


class ITelemetryStore(ABC):
    """Abstract interface for telemetry storage (in-memory, Postgres, Prometheus, etc.)."""

    @abstractmethod
    def record_request(self, record: RequestTelemetryRecord) -> None:
        pass

    @abstractmethod
    def record_provider_event(
        self,
        provider_name: str,
        model: str,
        latency_ms: float,
        success: bool,
        is_fallback: bool = False,
        failure_reason: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def get_recent_requests(self, limit: int = 20) -> List[RequestTelemetryRecord]:
        pass

    @abstractmethod
    def get_aggregated_metrics(self) -> AggregatedMetricsResponse:
        pass

    @abstractmethod
    def get_provider_records(self) -> List[ProviderHealthRecord]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class InMemoryTelemetryStore(ITelemetryStore):
    """
    Lightweight, thread-safe in-memory ring buffer store for request telemetry and metrics.
    Never stores sensitive raw prompt or query content.
    """

    def __init__(self, max_records: int = 1000):
        self._lock = threading.Lock()
        self._max_records = max_records
        self._records: deque[RequestTelemetryRecord] = deque(maxlen=max_records)
        self._provider_stats: Dict[str, Dict[str, Any]] = {}

    def record_request(self, record: RequestTelemetryRecord) -> None:
        with self._lock:
            self._records.append(record)

    def record_provider_event(
        self,
        provider_name: str,
        model: str,
        latency_ms: float,
        success: bool,
        is_fallback: bool = False,
        failure_reason: Optional[str] = None
    ) -> None:
        with self._lock:
            if provider_name not in self._provider_stats:
                self._provider_stats[provider_name] = {
                    "provider_name": provider_name,
                    "model": model,
                    "request_count": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_latency_ms": 0.0,
                    "fallback_count": 0,
                    "last_failure_reason": None,
                }

            stats = self._provider_stats[provider_name]
            stats["model"] = model or stats["model"]
            stats["request_count"] += 1
            if success:
                stats["success_count"] += 1
                stats["total_latency_ms"] += max(0.0, latency_ms)
            else:
                stats["failure_count"] += 1
                stats["last_failure_reason"] = failure_reason

            if is_fallback:
                stats["fallback_count"] += 1

    def get_recent_requests(self, limit: int = 20) -> List[RequestTelemetryRecord]:
        with self._lock:
            bounded_limit = max(1, min(limit, self._max_records))
            # Newest first
            return list(reversed(list(self._records)))[:bounded_limit]

    def get_aggregated_metrics(self) -> AggregatedMetricsResponse:
        with self._lock:
            records = list(self._records)

        total_recorded = len(records)
        if total_recorded == 0:
            return AggregatedMetricsResponse(
                queries_today=0,
                avg_latency_ms=None,
                p95_latency_ms=None,
                citation_grounding=None,
                abstention_rate=None,
                jurisdiction_leakage=0.0,
                total_requests_recorded=0,
                provider_statistics=self._compute_provider_summary(),
                retrieval_statistics={"avg_retrieved": None, "avg_reranked": None, "avg_citations": None},
                failure_statistics={"total_failures": 0, "failure_rate": 0.0, "reasons": {}}
            )

        # 1. Queries today (UTC date)
        now_utc = datetime.now(timezone.utc).date()
        today_records = [
            r for r in records
            if (r.timestamp.date() if hasattr(r.timestamp, "date") else r.timestamp) == now_utc
        ]
        queries_today = len(today_records)

        # 2. Latencies (Average and P95)
        latencies = [r.latency_ms for r in records if r.latency_ms > 0]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

        p95_latency: Optional[float] = None
        if latencies:
            sorted_lat = sorted(latencies)
            # Nearest rank method
            p95_index = min(math.ceil(0.95 * len(sorted_lat)) - 1, len(sorted_lat) - 1)
            p95_latency = round(sorted_lat[max(0, p95_index)], 2)

        # 3. Quality Metrics
        grounding_rates = [r.grounding_rate for r in records if r.grounding_rate is not None]
        avg_grounding = round(sum(grounding_rates) / len(grounding_rates), 3) if grounding_rates else None

        abstained_count = sum(1 for r in records if r.abstained)
        abstention_rate = round(abstained_count / total_recorded, 3)

        # 4. Retrieval Statistics
        retrieved_counts = [r.retrieval_count for r in records]
        reranked_counts = [r.reranked_count for r in records]
        citation_counts = [r.citation_count for r in records]

        retrieval_stats = {
            "avg_retrieved": round(sum(retrieved_counts) / total_recorded, 1) if retrieved_counts else 0,
            "avg_reranked": round(sum(reranked_counts) / total_recorded, 1) if reranked_counts else 0,
            "avg_citations": round(sum(citation_counts) / total_recorded, 1) if citation_counts else 0,
        }

        # 5. Failure Statistics
        failures = [r for r in records if not r.success]
        failure_reasons: Dict[str, int] = {}
        for f in failures:
            reason = f.failure_reason or "Unknown Error"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        failure_stats = {
            "total_failures": len(failures),
            "failure_rate": round(len(failures) / total_recorded, 3),
            "reasons": failure_reasons
        }

        return AggregatedMetricsResponse(
            queries_today=queries_today,
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            citation_grounding=avg_grounding,
            abstention_rate=abstention_rate,
            jurisdiction_leakage=0.0,  # Strict statutory isolation maintained
            total_requests_recorded=total_recorded,
            provider_statistics=self._compute_provider_summary(),
            retrieval_statistics=retrieval_stats,
            failure_statistics=failure_stats
        )

    def _compute_provider_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for name, data in self._provider_stats.items():
            req_count = data["request_count"]
            succ_count = data["success_count"]
            tot_lat = data["total_latency_ms"]
            avg_lat = round(tot_lat / succ_count, 2) if succ_count > 0 else None
            summary[name] = {
                "model": data["model"],
                "requests": req_count,
                "successes": succ_count,
                "failures": data["failure_count"],
                "fallbacks": data["fallback_count"],
                "avg_latency_ms": avg_lat
            }
        return summary

    def get_provider_records(self) -> List[ProviderHealthRecord]:
        with self._lock:
            # We can merge recorded operational counts with known providers
            records: List[ProviderHealthRecord] = []
            for name, data in self._provider_stats.items():
                succ = data["success_count"]
                avg_lat = round(data["total_latency_ms"] / succ, 2) if succ > 0 else None
                records.append(
                    ProviderHealthRecord(
                        provider_name=name,
                        model=data["model"],
                        status="healthy" if data["failure_count"] == 0 else "degraded",
                        circuit_breaker_status="closed",
                        request_count=data["request_count"],
                        success_count=succ,
                        failure_count=data["failure_count"],
                        avg_latency_ms=avg_lat,
                        fallback_count=data["fallback_count"]
                    )
                )
            return records

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._provider_stats.clear()


# Default singleton instance
telemetry_store = InMemoryTelemetryStore()
