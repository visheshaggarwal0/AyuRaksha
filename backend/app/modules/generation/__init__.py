"""
AyuRaksha Generation Module
Implements IGenerationModule with prioritized pluggable LLM provider switching.
"""
import time
from typing import List, Tuple, Optional, Dict, Any
import logging

from app.modules.interfaces import IGenerationModule, ILLMProvider
from app.models.domain import Evidence
from app.modules.generation.providers import (
    GeminiProvider,
    OpenRouterProvider,
    GroqProvider,
    LocalOllamaProvider,
    DeterministicStatutoryProvider
)
from app.telemetry.collector import telemetry_collector
from app.telemetry.models import ProviderHealthRecord

logger = logging.getLogger("AyuRaksha.Generation")


class PluggableGenerationModule(IGenerationModule):
    """Coordinates generation across pluggable model providers."""

    def __init__(self):
        self._providers: List[Tuple[int, ILLMProvider]] = []
        self._active_provider_name: str = "Uninitialized"
        self._last_token_usage = None
        self._setup_default_providers()

    def _setup_default_providers(self):
        # Priority order: Gemini (1) -> OpenRouter (2) -> Groq (3) -> Local Ollama (4) -> Deterministic Fallback (99)
        self.register_provider(GeminiProvider(), priority=1)
        self.register_provider(OpenRouterProvider(), priority=2)
        self.register_provider(GroqProvider(), priority=3)
        self.register_provider(LocalOllamaProvider(), priority=4)
        self.register_provider(DeterministicStatutoryProvider(), priority=99)

    def register_provider(self, provider: ILLMProvider, priority: int = 10) -> None:
        self._providers.append((priority, provider))
        self._providers.sort(key=lambda x: x[0])

    def set_primary_provider(self, provider: ILLMProvider) -> None:
        """Explicitly inject or swap the top-priority provider."""
        self._providers = [(0, provider)] + [p for p in self._providers if p[1].provider_name != provider.provider_name]
        self._providers.sort(key=lambda x: x[0])

    @property
    def active_provider_name(self) -> str:
        return self._active_provider_name

    @property
    def last_token_usage(self):
        return self._last_token_usage

    def get_providers_status(self) -> List[ProviderHealthRecord]:
        """Returns live status and circuit-breaker telemetry across all registered providers."""
        from app.telemetry.store import telemetry_store
        recorded_map = {r.provider_name: r for r in telemetry_store.get_provider_records()}

        status_records: List[ProviderHealthRecord] = []
        for _, provider in self._providers:
            name = provider.provider_name
            model = getattr(provider, "model_name", "unknown")
            circuit_status = getattr(provider, "circuit_status", "healthy" if provider.is_available() else "unavailable")
            breaker_status = "open" if circuit_status == "circuit_open" else ("closed" if circuit_status in ("healthy", "ready") else "unavailable")
            
            existing = recorded_map.get(name)
            req_cnt = existing.request_count if existing else 0
            succ_cnt = existing.success_count if existing else 0
            fail_cnt = existing.failure_count if existing else 0
            avg_lat = existing.avg_latency_ms if existing else None
            fb_cnt = existing.fallback_count if existing else 0

            status_records.append(
                ProviderHealthRecord(
                    provider_name=name,
                    model=model,
                    status=circuit_status,
                    circuit_breaker_status=breaker_status,
                    request_count=req_cnt,
                    success_count=succ_cnt,
                    failure_count=fail_cnt,
                    avg_latency_ms=avg_lat,
                    fallback_count=fb_cnt
                )
            )
        return status_records

    async def generate_legal_answer(
        self,
        query: str,
        evidence: List[Evidence],
        jurisdiction: str = "IN"
    ) -> str:
        # Assemble context blocks with bracket markers [1], [2]
        context_blocks = []
        for idx, ev in enumerate(evidence):
            marker = f"[{idx + 1}]"
            context_blocks.append(
                f"{marker} Source: {ev.source_title} ({ev.section_number})\nStatutory Text: {ev.verbatim_text}"
            )
        full_context = "\n\n".join(context_blocks)

        system_prompt = (
            "You are AyuRaksha (IP-SAKTI Sahayak), an authoritative statutory information and regulatory navigation engine for Ayurvedic innovation. "
            "Your role is to provide rigorous, objective statutory analysis based on verified legal provisions from the Drugs & Cosmetics Act 1940, "
            "Patents Act 1970, Biological Diversity Act 2002, and FSSAI regulations. "
            "Do NOT output generic disclaimers refusing to answer (such as 'I cannot provide legal advice'); directly deliver the objective statutory classification, "
            "Deliver direct, objective statutory classification, comparative legal criteria, and actionable licensing pathways. "
            "Keep the response structured, clear, and concise (under 250 words). "
            "At the end of each factual statement, add citation markers like [1], [2] corresponding strictly to the provided sources."
        )
        user_prompt = f"User Question: {query}\n\nVerified Context:\n{full_context}\n\nRegulatory Guidance:"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Iterate through providers by priority
        for _, provider in self._providers:
            if provider.is_available():
                t_prov_start = time.perf_counter()
                model_name = getattr(provider, "model_name", "unknown")
                try:
                    result = await provider.complete(messages, temperature=0.1, max_tokens=600)
                    prov_ms = round((time.perf_counter() - t_prov_start) * 1000, 2)
                    if result and len(result.strip()) > 20:
                        self._active_provider_name = provider.provider_name
                        self._last_token_usage = getattr(provider, "last_token_usage", None)
                        telemetry_collector.record_provider_call(
                            provider_name=provider.provider_name,
                            model=model_name,
                            latency_ms=prov_ms,
                            success=True,
                            is_fallback=False
                        )
                        return result.strip()
                    else:
                        telemetry_collector.record_provider_call(
                            provider_name=provider.provider_name,
                            model=model_name,
                            latency_ms=prov_ms,
                            success=False,
                            is_fallback=False,
                            failure_reason="Empty or insufficient response"
                        )
                except Exception as e:
                    prov_ms = round((time.perf_counter() - t_prov_start) * 1000, 2)
                    logger.warning("Provider %s failed: %s", provider.provider_name, e)
                    telemetry_collector.record_provider_call(
                        provider_name=provider.provider_name,
                        model=model_name,
                        latency_ms=prov_ms,
                        success=False,
                        is_fallback=False,
                        failure_reason=str(e)
                    )

        # Fallback to deterministic provider
        fallback = DeterministicStatutoryProvider()
        t_fb_start = time.perf_counter()
        fb_result = await fallback.complete(messages) or "Statutory analysis complete."
        fb_ms = round((time.perf_counter() - t_fb_start) * 1000, 2)
        self._active_provider_name = fallback.provider_name
        self._last_token_usage = None
        telemetry_collector.record_provider_call(
            provider_name=fallback.provider_name,
            model=fallback.model_name,
            latency_ms=fb_ms,
            success=True,
            is_fallback=True
        )
        return fb_result


generation_module = PluggableGenerationModule()

__all__ = [
    "PluggableGenerationModule",
    "generation_module",
    "GeminiProvider",
    "OpenRouterProvider",
    "GroqProvider",
    "LocalOllamaProvider",
    "DeterministicStatutoryProvider",
]
