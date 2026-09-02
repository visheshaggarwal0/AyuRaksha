import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ai.gateway.base import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger("AyuRaksha.OpenRouterProvider")

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter multi-model gateway integration."""

    def __init__(self, model_name: str = "google/gemma-4-31b-it:free"):
        super().__init__(model_name)
        self.api_key = settings.OPENROUTER_API_KEY.strip() if settings.OPENROUTER_API_KEY else ""
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1200,
        json_mode: bool = False
    ) -> Optional[str]:
        if not self.is_available():
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ayuraksha.gov.in",
            "X-Title": "AyuRaksha Legal Navigator",
            "Content-Type": "application/json"
        }
        candidate_models = list(dict.fromkeys([
            self.model_name,
            "google/gemini-2.5-flash",
            "google/gemini-3.5-flash",
            "meta-llama/llama-3.3-70b-instruct",
            "google/gemma-4-31b-it:free"
        ]))

        for mod in candidate_models:
            payload: Dict[str, Any] = {
                "model": mod,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    url = f"{self.base_url}/chat/completions"
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        if content and len(content.strip()) > 5:
                            return content.strip()
                    elif resp.status_code == 404:
                        continue
                    else:
                        logger.warning(f"OpenRouter ({mod}) returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.warning(f"OpenRouter ({mod}) call error: {e}")

        return None
