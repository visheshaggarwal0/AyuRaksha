import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ai.gateway.base import BaseLLMProvider

logger = logging.getLogger("AyuRaksha.OllamaProvider")

class OllamaProvider(BaseLLMProvider):
    """Local Ollama instance integration."""

    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        super().__init__(model_name)
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/chat"

    def is_available(self) -> bool:
        return True

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1200,
        json_mode: bool = False
    ) -> Optional[str]:
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if json_mode:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(self.endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("message", {}).get("content", "")
                    if content and len(content.strip()) > 5:
                        return content.strip()
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        except Exception as e:
            logger.warning(f"Ollama call error: {e}")

        return None
