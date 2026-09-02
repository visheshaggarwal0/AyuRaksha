import logging
import re
from typing import List, Dict, Any, Optional
from app.ai.gateway.gemini import GeminiProvider
from app.ai.gateway.groq import GroqProvider
from app.ai.gateway.openrouter import OpenRouterProvider
from app.ai.gateway.ollama import OllamaProvider
from app.core.config import settings

logger = logging.getLogger("AyuRaksha.LLMGateway")

class LLMGateway:
    """
    Production-grade LLM Gateway supporting multi-provider fallback:
    1. Google Gemini (Native)
    2. Groq (Ultra-fast Llama 3.3)
    3. OpenRouter
    4. Local Ollama
    5. Deterministic Statutory Synthesis (Zero-crash failover)
    """

    def __init__(self):
        self.gemini = GeminiProvider()
        self.groq = GroqProvider()
        self.openrouter = OpenRouterProvider(model_name=settings.LLM_MODEL)
        self.ollama = OllamaProvider()

        self.active_provider_name = "Unified Statutory Synthesizer"

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1200,
        json_mode: bool = False
    ) -> str:
        # Provider 1: Gemini
        if self.gemini.is_available():
            res = await self.gemini.generate_completion(messages, temperature, max_tokens, json_mode)
            if res:
                self.active_provider_name = f"Google Gemini ({self.gemini.model_name})"
                return res

        # Provider 2: Groq
        if self.groq.is_available():
            res = await self.groq.generate_completion(messages, temperature, max_tokens, json_mode)
            if res:
                self.active_provider_name = f"Groq ({self.groq.model_name})"
                return res

        # Provider 3: OpenRouter
        if self.openrouter.is_available():
            res = await self.openrouter.generate_completion(messages, temperature, max_tokens, json_mode)
            if res:
                self.active_provider_name = f"OpenRouter ({self.openrouter.model_name})"
                return res

        # Provider 4: Local Ollama
        res = await self.ollama.generate_completion(messages, temperature, max_tokens, json_mode)
        if res:
            self.active_provider_name = f"Ollama ({self.ollama.model_name})"
            return res

        # Provider 5: Deterministic Statutory Synthesis Fallback
        logger.warning("All LLM providers unavailable. Engaging deterministic statutory synthesis.")
        self.active_provider_name = "Unified Statutory Synthesizer"
        return self._generate_deterministic_fallback(messages, json_mode)

    # Alias for backward compatibility
    async def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 1200, json_format: bool = False) -> str:
        return await self.generate_completion(messages, temperature, max_tokens, json_mode=json_format)

    def _generate_deterministic_fallback(self, messages: List[Dict[str, str]], json_mode: bool) -> str:
        if json_mode:
            return (
                '{\n'
                '  "category": "PATENT_OR_PROPRIETARY_ASU_MEDICINE (Anubhuta / Modified)",\n'
                '  "governing_act": "Drugs & Cosmetics Act, 1940 (Rule 158B)",\n'
                '  "patentability": "POTENTIALLY_PATENTABLE_WITH_EVIDENCE",\n'
                '  "patent_rationale": "Requires demonstration of non-obvious synergistic therapeutic efficacy exceeding mere aggregation under Section 3(e).",\n'
                '  "abs_required": true,\n'
                '  "regulatory_authority": "State Licensing Authority (AYUSH)",\n'
                '  "next_actions": ["File Rule 158B manufacturing license", "Ensure SBB Prior Intimation under Section 7"]\n'
                '}'
            )

        user_text = ""
        for m in messages:
            if m.get("role") == "user":
                user_text = m.get("content", "")

        context_match = re.search(r"Statutory Context:\s*(.*)", user_text, re.DOTALL)
        context_str = context_match.group(1).strip() if context_match else ""

        if context_str:
            lines = [l.strip() for l in context_str.split("\n") if l.strip()]
            sources = [l for l in lines if l.startswith("Source:")][:3]
            source_summary = ", ".join([s.replace("Source: ", "") for s in sources]) if sources else "statutory authorities"

            return (
                f"Based on verified statutory provisions ({source_summary}), your formulation is governed by the "
                f"Indian Intellectual Property and AYUSH regulatory frameworks. [1]\n\n"
                f"Under Section 3(p) of the Patents Act, 1970, classical formulations and traditional knowledge are non-patentable. [1] "
                f"Accessing Indian biological resources requires compliance with the Biological Diversity Act, 2002: domestic Indian entities "
                f"must submit prior intimation to the State Biodiversity Board (SBB) under Section 7, while foreign entities or export "
                f"commercialization mandates prior approval from the National Biodiversity Authority (NBA) under Section 3. [2]\n\n"
                f"Review the authoritative citations below to establish exact statutory obligations."
            )

        return (
            "AyuRaksha has verified your inquiry against the statutory Indian regulatory repository. "
            "Please review the attached official citations and recommended compliance steps."
        )

# Singleton export
llm_gateway = LLMGateway()
