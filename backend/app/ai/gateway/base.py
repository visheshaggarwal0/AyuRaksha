import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for all AyuRaksha LLM providers.
    Providers must handle rate limits, formatting, timeouts, and circuit-breaker states gracefully.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._circuit_tripped_until: float = 0.0
        self._circuit_cooldown_seconds: float = 300.0

    def is_circuit_open(self) -> bool:
        """Returns True if circuit breaker is currently open (provider temporarily disabled)."""
        return time.time() < self._circuit_tripped_until

    def trip_circuit(self, cooldown_seconds: Optional[float] = None, reason: str = "") -> None:
        """Trips the circuit breaker due to authentication, quota, or connection failure."""
        cooldown = cooldown_seconds or self._circuit_cooldown_seconds
        self._circuit_tripped_until = time.time() + cooldown

    def reset_circuit(self) -> None:
        """Resets the circuit breaker."""
        self._circuit_tripped_until = 0.0

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
        """Returns True if provider has valid credentials / endpoint configured and circuit is closed."""
        pass

