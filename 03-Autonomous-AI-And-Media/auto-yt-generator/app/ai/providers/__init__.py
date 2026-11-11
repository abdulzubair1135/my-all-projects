"""
AUTO YT GENERATOR — AI Provider Factory.
"""

from app.config import settings
from app.ai.provider import AIProvider
from app.ai.providers.local import LocalAIProvider
from app.ai.providers.gemini import GeminiAIProvider
from app.ai.providers.openai import OpenAIProvider
from app.logger import logger


def get_ai_provider(provider_name: str = None) -> AIProvider:
    """Returns the configured AI Provider instance with automatic fallback to LocalAIProvider."""
    target_provider = provider_name or settings.providers.ai_provider

    if target_provider == "gemini":
        if settings.gemini_api_key:
            return GeminiAIProvider(api_key=settings.gemini_api_key)
        else:
            logger.info("GEMINI_API_KEY not found. Using local offline fallback provider.")
            return LocalAIProvider()

    elif target_provider == "openai":
        if settings.openai_api_key:
            return OpenAIProvider(api_key=settings.openai_api_key)
        else:
            logger.info("OPENAI_API_KEY not found. Using local offline fallback provider.")
            return LocalAIProvider()

    elif target_provider == "local":
        return LocalAIProvider()

    logger.warning(f"Unknown AI provider '{target_provider}', defaulting to LocalAIProvider.")
    return LocalAIProvider()
