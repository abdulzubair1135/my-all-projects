"""
Robust JSON output parser and cleaner for AI responses.
Handles markdown fences, trailing commas, and partial JSON recovery.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

from app.core.logging_manager import get_logger

logger = get_logger("output_parser")

T = TypeVar("T", bound=BaseModel)


def extract_json_str(raw_text: str) -> Optional[str]:
    """Find and isolate JSON content from markdown wrappers or noisy text."""
    if not raw_text:
        return None

    # 1. Check for markdown code blocks ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        if candidate.startswith("{") or candidate.startswith("["):
            return candidate

    # 2. Find outermost brackets
    start_brace = raw_text.find("{")
    end_brace = raw_text.rfind("}")
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        return raw_text[start_brace : end_brace + 1].strip()

    start_bracket = raw_text.find("[")
    end_bracket = raw_text.rfind("]")
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        return raw_text[start_bracket : end_bracket + 1].strip()

    return None


def clean_and_repair_json(json_str: str) -> str:
    """Fix common LLM JSON syntax issues like trailing commas."""
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*([\]}])", r"\1", json_str)
    return cleaned


def parse_and_validate(raw_text: str, model_cls: Type[T]) -> T:
    """Extract, parse, and validate JSON text into a Pydantic model instance."""
    json_candidate = extract_json_str(raw_text)
    if not json_candidate:
        raise ValueError(f"No JSON block found in response: {raw_text[:200]}...")

    repaired = clean_and_repair_json(json_candidate)
    try:
        data = json.loads(repaired)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}\nCandidate:\n{repaired[:300]}")
        raise ValueError(f"Invalid JSON syntax in AI output: {e}")

    return model_cls.model_validate(data)
