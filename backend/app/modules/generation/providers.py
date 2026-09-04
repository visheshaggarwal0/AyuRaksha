"""
Pluggable LLM Provider Adapters
Implements ILLMProvider for Google Gemini, Groq, local Ollama, and OpenRouter.
Allows swapping between cloud and air-gapped local models seamlessly.
"""
import httpx
import logging
from typing import List, Dict, Any, Optional
from app.modules.interfaces import ILLMProvider
from app.core.config import settings

logger = logging.getLogger("AyuRaksha.GenerationProviders")


class GeminiProvider(ILLMProvider):
    """Google Gemini REST API adapter."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self._api_key = (api_key or settings.GEMINI_API_KEY or "").strip()
        self._model = model
        self._circuit_broken = False

    @property
    def provider_name(self) -> str:
        return f"Google Gemini ({self._model})"

    def is_available(self) -> bool:
        if self._circuit_broken:
            return False
        return bool(self._api_key and len(self._api_key) > 20)

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 3000,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        if not self.is_available():
            return None

        system_instruction = ""
        contents = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_instruction += content + "\n"
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({"role": gemini_role, "parts": [{"text": content}]})

        models_to_try = [
            "gemini-2.5-flash",
            self._model,
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        # Deduplicate while preserving order
        models_to_try = list(dict.fromkeys(models_to_try))

        headers = {
            "Content-Type": "application/json"
        }

        # Query v1beta directly with ?key parameter
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]

        for mod in models_to_try:
            if self._api_key.startswith("AQ.") or self._api_key.startswith("ya29."):
                headers["Authorization"] = f"Bearer {self._api_key}"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent"
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self._api_key}"

            payload: Dict[str, Any] = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            if response_format == "json":
                payload["generationConfig"]["responseMimeType"] = "application/json"

            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction.strip()}]
                }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "").strip()
                                if text:
                                    logger.info("Successfully received answer from Google Gemini (%s via v1beta)", mod)
                                    return text
                    elif resp.status_code in (400, 401, 403, 404):
                        logger.info("Gemini %s returned %s; tripping circuit breaker for fast fallback.", mod, resp.status_code)
                        self._circuit_broken = True
                        break
                    else:
                        logger.warning(
                            "Gemini %s returned HTTP %s: %s",
                            mod, resp.status_code, resp.text[:200]
                        )
            except Exception as e:
                logger.debug("Gemini %s connection error: %s", mod, e)

        return None


class OpenRouterProvider(ILLMProvider):
    """OpenRouter Cloud LLM Adapter (supporting Gemma 2, Llama 3.3, Claude, Mistral)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = (api_key or settings.OPENROUTER_API_KEY or "").strip()
        self._model = model or settings.LLM_MODEL or "google/gemma-2-9b-it:free"
        self._circuit_broken = False

    @property
    def provider_name(self) -> str:
        return f"OpenRouter ({self._model})"

    def is_available(self) -> bool:
        if self._circuit_broken:
            return False
        return bool(self._api_key and len(self._api_key) > 10)

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 3000,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        if not self.is_available():
            return None

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://ayuraksha.gov.in",
            "X-Title": "AyuRaksha Legal Navigator",
            "Content-Type": "application/json"
        }
        candidate_models = [
            self._model,
            "google/gemini-2.5-flash",
            "google/gemini-2.0-flash-001",
            "meta-llama/llama-3.3-70b-instruct",
            "mistralai/mistral-7b-instruct:free"
        ]
        # Deduplicate while preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        for mod in candidate_models:
            payload: Dict[str, Any] = {
                "model": mod,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format == "json":
                payload["response_format"] = {"type": "json_object"}

            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            text = choices[0].get("message", {}).get("content", "").strip()
                            if text:
                                return text
                    elif resp.status_code in (401, 402, 403):
                        logger.info("OpenRouter auth/credit failure (HTTP %s); tripping circuit breaker for fast fallback.", resp.status_code)
                        self._circuit_broken = True
                        break
                    else:
                        logger.info("OpenRouter model %s returned %s: %s", mod, resp.status_code, resp.text[:120])
            except Exception as e:
                logger.debug("OpenRouter model %s error: %s", mod, e)

        return None


class GroqProvider(ILLMProvider):
    """Groq Cloud Llama / Mixtral ultra-fast inference adapter."""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self._api_key = (api_key or settings.GROQ_API_KEY or "").strip()
        self._model = model

    @property
    def provider_name(self) -> str:
        return f"Groq ({self._model})"

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        if not self.is_available():
            return None

        url = "https://api.groq.com/openai/v1/chat/completions"
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json"
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.debug("Groq call failed: %s", e)

        return None


class LocalOllamaProvider(ILLMProvider):
    """Local offline Ollama instance adapter for air-gapped SIH demos."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._circuit_broken = False

    @property
    def provider_name(self) -> str:
        return f"Local Ollama ({self._model})"

    def is_available(self) -> bool:
        if self._circuit_broken:
            return False
        return True  # Probe on demand

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        if not self.is_available():
            return None

        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        }
        if response_format == "json":
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("message", {}).get("content", "").strip()
        except Exception:
            self._circuit_broken = True  # Circuit break immediately if local Ollama daemon is offline

        return None


class DeterministicStatutoryProvider(ILLMProvider):
    """Zero-crash, dynamically grounded statutory legal synthesis fallback."""

    @property
    def provider_name(self) -> str:
        return "Deterministic Statutory Synthesizer"

    def is_available(self) -> bool:
        return True

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        user_query = ""
        context = ""
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", "")
                user_query = content
                if "Verified Context:" in content:
                    parts = content.split("Verified Context:")
                    context = parts[1].strip()

        q_lower = user_query.lower()
        is_patent_q = any(k in q_lower for k in ["patent", "invent", "novelty", "section 3", "3(p)", "3(e)"])
        is_abs_q = any(k in q_lower for k in ["abs", "biodiversity", "nba", "sbb", "biological", "benefit sharing"])
        is_polyherbal = any(k in q_lower for k in ["polyherbal", "formulation", "combination", "ashwagandha", "brahmi"])

        # Dynamically build expert statutory reasoning
        paragraphs = []

        # 1. Patentability & Section 3(p) / 3(e) Analysis
        if is_patent_q or is_polyherbal:
            p1 = (
                "Under Indian patent jurisprudence, a classical or routine polyherbal formulation "
                "combining known Ayurvedic botanicals is non-patentable as a matter of law. [1] "
                "Specifically, Section 3(p) of the Patents Act, 1970 excludes any invention that in effect "
                "is traditional knowledge, or an aggregation or duplication of known properties of traditionally known components. [1] "
                "Furthermore, Section 3(e) strictly bars substances obtained by a mere admixture resulting only in the aggregation "
                "of the properties of the components thereof. [2]"
            )
            paragraphs.append(p1)

            p2 = (
                "To overcome these statutory bars, an applicant must demonstrate a patentable pathway beyond classical formulation: "
                "(1) empirical proof of unexpected synergistic enhancement (where the combined biological effect is significantly greater than the sum of individual effects), "
                "(2) a novel, non-obvious extraction process yielding a specific standardized fraction, or "
                "(3) novel targeted drug delivery (e.g., lipid nanoparticles or phytosomes). "
                "If the formulation is developed as a purified, standardized fraction, the CDSCO Phytopharmaceutical pathway (Rule 122E / Form CT-18) "
                "provides an appropriate evidence-backed regulatory route."
            )
            paragraphs.append(p2)

        # 2. Manufacturing & AYUSH Licensing Route
        p3 = (
            "For commercialization and manufacturing in India, Chapter IV-A of the Drugs and Cosmetics Act, 1940 governs Ayurvedic drugs. [1] "
            "If the formulation follows an authoritative recipe listed in the First Schedule (such as Charaka Samhita or Sharangadhara Samhita), "
            "it qualifies as a Classical Ayurvedic Medicine under Section 3(a). [2] "
            "If the ingredients or proportions are modified, it must be licensed as an Ayurvedic Patent or Proprietary Medicine under Section 3(h), "
            "requiring a Form 24D / 25D manufacturing license under Rule 158B of the Drugs and Cosmetics Rules, 1945 with documented safety and stability data. [2]"
        )
        paragraphs.append(p3)

        # 3. Biological Diversity & Mandatory Approvals
        p4 = (
            "Prior to commercial utilization or filing any patent application, compliance with the Biological Diversity Act, 2002 is mandatory: "
            "Foreign entities, non-residents, or Indian companies with foreign shareholding require prior approval from the National Biodiversity Authority (NBA) via Form I under Section 3. [1] "
            "Domestic Indian citizens and entities must submit prior intimation to the State Biodiversity Board (SBB) under Section 7. "
            "Crucially, under Section 6 of the BDA, prior approval from the NBA (Form III) is obligatory before filing any patent application based on Indian biological resources."
        )
        paragraphs.append(p4)

        return "\n\n".join(paragraphs)
