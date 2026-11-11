from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers (Browser-based, API-based, or Mock).
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Initializes connection or launches browser context."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Sends prompt to the LLM and waits for full text generation."""
        pass

    async def generate_with_images(self, prompt: str, images: list, system_prompt: Optional[str] = None) -> str:
        """
        Sends prompt along with 1 or more local image file paths to the LLM.
        Defaults to text generate() if the provider doesn't override image upload.
        """
        return await self.generate(prompt, system_prompt=system_prompt)

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Returns provider health status dictionary."""
        pass

    @abstractmethod
    async def close(self):
        """Closes browser context and releases resources."""
        pass

