"""
AUTO YT GENERATOR — Abstract AI Provider Interface.

Defines the contract that any LLM provider (Gemini, OpenAI, Anthropic, Local) must implement.
Guarantees clean provider interchangeability without vendor lock-in.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel


class AIProvider(ABC):
    """Abstract interface for all AI model providers."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generates raw text response for a given prompt."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.5,
    ) -> BaseModel:
        """Generates structured JSON and validates it against a Pydantic schema model."""
        pass
