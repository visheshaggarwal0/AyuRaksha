"""
AyuRaksha Generation Module
Implements IGenerationModule with prioritized pluggable LLM provider switching.
"""
from typing import List, Tuple, Optional
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

logger = logging.getLogger("AyuRaksha.Generation")


class PluggableGenerationModule(IGenerationModule):
    """Coordinates generation across pluggable model providers."""

    def __init__(self):
        self._providers: List[Tuple[int, ILLMProvider]] = []
        self._active_provider_name: str = "Uninitialized"
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
            "comparative legal criteria, and licensing pathways requested. "
            "Structure your answer into clear, comprehensive paragraphs with headings or bullet points where helpful. "
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
                try:
                    result = await provider.complete(messages, temperature=0.1, max_tokens=3000)
                    if result and len(result.strip()) > 20:
                        self._active_provider_name = provider.provider_name
                        return result.strip()
                except Exception as e:
                    logger.warning("Provider %s failed: %s", provider.provider_name, e)

        # Fallback to deterministic provider
        fallback = DeterministicStatutoryProvider()
        self._active_provider_name = fallback.provider_name
        return await fallback.complete(messages) or "Statutory analysis complete."


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
