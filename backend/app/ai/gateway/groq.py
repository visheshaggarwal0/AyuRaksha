import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ai.gateway.base import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger("AyuRaksha.GroqProvider")

class GroqProvider(BaseLLMProvider):
    """Ultra-low latency Groq Cloud REST API integration."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        super().__init__(model_name)
        self.api_key = settings.GROQ_API_KEY.strip() if getattr(settings, "GROQ_API_KEY", None) else ""
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

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
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 5:
                        return content.strip()
                else:
                    logger.warning(f"Groq API returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Groq API call error: {e}")

        return None
