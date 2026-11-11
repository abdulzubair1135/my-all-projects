"""
AUTO YT GENERATOR — OpenAI Compatible AI Provider Adapter.

Supports OpenAI, Groq, DeepSeek, Local Ollama, and any OpenAI API-compatible endpoint.
"""

import json
import re
from typing import Optional, Type
from pydantic import BaseModel
from app.ai.provider import AIProvider
from app.logger import logger


class OpenAIProvider(AIProvider):
    """OpenAI / Groq API provider adapter."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = "gpt-4o-mini", base_url: Optional[str] = None):
        super().__init__(api_key=api_key, model_name=model_name or "gpt-4o-mini")
        self.base_url = base_url
        self._client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info(f"OpenAI Provider initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to configure OpenAI client: {e}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if not self._client:
            raise RuntimeError("OpenAI API key is not configured or client failed to initialize.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> BaseModel:
        if not self._client:
            raise RuntimeError("OpenAI API key is not configured or client failed to initialize.")

        json_schema_str = json.dumps(schema_cls.model_json_schema(), indent=2)
        sys_msg = (
            f"{system_prompt or ''}\n\n"
            f"You MUST output ONLY valid JSON matching this schema:\n"
            f"{json_schema_str}\n\n"
            f"Do not include Markdown backticks or commentary."
        )

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ]

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or "{}"
        data = json.loads(raw_text)
        return schema_cls(**data)
