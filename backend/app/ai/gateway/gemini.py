import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ai.gateway.base import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger("AyuRaksha.GeminiProvider")

class GeminiProvider(BaseLLMProvider):
    """Native Google Gemini REST integration."""

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        super().__init__(model_name)
        self.api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""

    def is_available(self) -> bool:
        return bool(self.api_key) and not self.is_circuit_open()

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1200,
        json_mode: bool = False
    ) -> Optional[str]:
        if not self.is_available():
            return None

        system_text = ""
        contents = []

        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_text += content + "\n"
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_text:
            payload["system_instruction"] = {
                "parts": [{"text": system_text.strip()}]
            }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        models_to_try = [self.model_name, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for mod in models_to_try:
            req_headers = {"Content-Type": "application/json"}
            if self.api_key.startswith("AQ.") or self.api_key.startswith("ya29."):
                req_headers["Authorization"] = f"Bearer {self.api_key}"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent"
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self.api_key}"

            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(url, json=payload, headers=req_headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "").strip()
                                if text:
                                    return text
                    elif resp.status_code in (401, 403):
                        logger.warning(f"Gemini credentials rejected ({resp.status_code}). Tripping circuit breaker for 300s.")
                        self.trip_circuit(300, reason=f"Gemini {resp.status_code}")
                        break
                    elif resp.status_code == 404:
                        continue
                    else:
                        logger.warning(f"Gemini ({mod}) returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.warning(f"Gemini ({mod}) error: {e}")
                self.trip_circuit(60, reason=str(e))
                break

        return None
