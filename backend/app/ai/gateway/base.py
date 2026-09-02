from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for all AyuRaksha LLM providers.
    Providers must handle rate limits, formatting, and timeouts gracefully.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1200,
        json_mode: bool = False
    ) -> Optional[str]:
        """
        Generate completion from LLM provider.
        Returns text string or None if request fails.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider has valid credentials / endpoint configured."""
        pass
