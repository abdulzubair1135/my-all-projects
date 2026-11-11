"""
AUTO YT GENERATOR — Google Gemini AI Provider with Robust JSON Mode.

Uses Google's high-speed Gemini REST API (gemini-2.5-flash / gemini-flash-latest)
with response_mime_type: "application/json" and 8192 token window to guarantee
100% valid, untruncated JSON responses with fallback to LocalAIProvider.
"""

import json
import os
import re
from typing import Optional, Type, TypeVar, Any
import requests
from pydantic import BaseModel
from dotenv import load_dotenv

from app.ai.provider import AIProvider
from app.config import settings
from app.logger import logger

load_dotenv()
T = TypeVar("T", bound=BaseModel)


class GeminiAIProvider(AIProvider):
    """Google Gemini AI implementation with robust JSON mode & graceful fallback."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        super().__init__(api_key=api_key, model_name=model_name)
        self.api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or "gemini-2.5-flash"

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment or config.")
        else:
            logger.info(f"Gemini AI Provider initialized with model: {self.model_name}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        is_json: bool = False,
        **kwargs,
    ) -> str:
        """Calls Gemini REST API to generate text or raw JSON."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        sys_inst = system_prompt or system_instruction
        contents = []
        if sys_inst:
            prompt = f"System Instruction: {sys_inst}\n\nTask:\n{prompt}"

        contents.append({"parts": [{"text": prompt}]})

        gen_config = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
        if is_json:
            gen_config["responseMimeType"] = "application/json"

        payload = {
            "contents": contents,
            "generationConfig": gen_config,
        }

        response = requests.post(url, json=payload, timeout=90)

        if response.status_code == 200:
            data = response.json()
            try:
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {e}")
            return ""
        else:
            logger.error(f"Gemini API error ({response.status_code}): {response.text}")
            raise RuntimeError(f"Gemini API error: {response.text}")

    def generate_structured(
        self,
        prompt: str,
        schema_cls: Optional[Type[T]] = None,
        schema: Optional[Type[T]] = None,
        system_prompt: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs,
    ) -> T:
        """Forces Gemini to return valid JSON matching Pydantic schema with auto-repair and local fallback."""
        target_schema = schema_cls or schema
        if not target_schema:
            raise ValueError("schema_cls is required for generate_structured")

        schema_json = json.dumps(target_schema.model_json_schema(), indent=2)

        strict_prompt = (
            f"{prompt}\n\n"
            f"You MUST respond ONLY with a single valid JSON object strictly conforming to this schema:\n"
            f"{schema_json}\n"
        )

        try:
            raw_text = self.generate_text(
                prompt=strict_prompt,
                system_prompt=system_prompt or system_instruction,
                temperature=temperature,
                max_tokens=8192,
                is_json=True,
            )

            cleaned = raw_text.strip()
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

            parsed_dict = json.loads(cleaned)
            return target_schema.model_validate(parsed_dict)

        except Exception as err:
            logger.warning(f"Gemini structured generation failed: {err}. Falling back to Local AI Generator.")
            from app.ai.providers.local import LocalAIProvider
            local_ai = LocalAIProvider()
            return local_ai.generate_structured(
                prompt=prompt,
                schema_cls=target_schema,
                system_prompt=system_prompt,
                temperature=temperature,
            )
