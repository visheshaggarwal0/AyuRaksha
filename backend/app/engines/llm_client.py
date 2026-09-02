import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings

class LocalOllamaClient:
    """
    Async client for local Ollama inference using llama3.1:8b.
    100% free and private RAG pipeline.
    """

    def __init__(self):
        self.base_url = "http://localhost:11434/api/chat"
        self.model = "llama3.1:8b"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_format: bool = False
    ) -> Optional[str]:
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if json_format:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    self.base_url,
                    json=payload
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # Ollama returns {"message": {"role": "assistant", "content": "..."}}
                    return data.get("message", {}).get("content", "")
                else:
                    import logging
                    logging.error(f"[!] Ollama API Error {resp.status_code}: {resp.text}")
                    return None
        except httpx.ConnectError:
            import logging
            logging.error("[!] Failed to connect to Ollama. Is it running on localhost:11434?")
            return None
        except Exception as e:
            import logging
            logging.error(f"[!] Ollama Request Exception: {e}")
            return None
