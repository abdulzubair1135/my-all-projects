"""
AURA Model Backends.
Provides Ollama HTTP REST Backend and Mock Backend implementations.
Supports auto-detection of locally pulled Ollama models.
"""

import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from config import config
from core.logger import setup_logger

logger = setup_logger("ModelBackend")

class BaseModelBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str, temperature: float = 0.7, system: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7) -> str:
        pass

class OllamaBackend(BaseModelBackend):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or config.models.ollama_base_url).rstrip("/")
        self._available_models: List[str] = []

    def get_available_models(self) -> List[str]:
        if self._available_models:
            return self._available_models
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                self._available_models = models
                return models
        except Exception as e:
            logger.debug(f"Could not list Ollama models: {e}")
            return []

    def _resolve_model(self, requested_model: str) -> str:
        available = self.get_available_models()
        if not available:
            return requested_model
        
        # Exact match
        if requested_model in available:
            return requested_model
        
        # Match base name (e.g. qwen3 -> qwen3.5:9b)
        base = requested_model.split(":")[0].lower()
        for m in available:
            if base in m.lower():
                logger.info(f"Resolved requested model '{requested_model}' -> '{m}'")
                return m

        # Default to first available model if any exists
        fallback = available[0]
        logger.info(f"Fallback model for '{requested_model}' -> '{fallback}'")
        return fallback

    def generate(self, prompt: str, model: str, temperature: float = 0.7, system: Optional[str] = None) -> str:
        target_model = self._resolve_model(model)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if system:
            payload["system"] = system

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=config.models.timeout_seconds) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            logger.error(f"Ollama connection error for model {target_model}: {e}")
            raise RuntimeError(f"Ollama API request failed: {e}")

    def chat(self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7) -> str:
        target_model = self._resolve_model(model)
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=config.models.timeout_seconds) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                message = result.get("message", {})
                return message.get("content", "")
        except urllib.error.URLError as e:
            logger.error(f"Ollama chat connection error for model {target_model}: {e}")
            raise RuntimeError(f"Ollama Chat API request failed: {e}")

class MockBackend(BaseModelBackend):
    """Mock LLM Backend for reliable unit testing and offline development."""
    def __init__(self, custom_responses: Optional[Dict[str, str]] = None):
        self.custom_responses = custom_responses or {}

    def generate(self, prompt: str, model: str, temperature: float = 0.7, system: Optional[str] = None) -> str:
        for key, resp in self.custom_responses.items():
            if key in prompt:
                return resp

        prompt_lower = prompt.lower()
        if "plan" in prompt_lower or "subtask" in prompt_lower:
            return json.dumps({
                "tasks": [
                    {"title": "Research topic concepts", "description": "Gather basic knowledge about topic", "priority": 1},
                    {"title": "Execute test script", "description": "Run basic python echo experiment", "priority": 2}
                ]
            })
        elif "critic" in prompt_lower or "evaluate" in prompt_lower:
            return json.dumps({
                "success": True,
                "confidence": 0.95,
                "feedback": "Task executed successfully with clean output."
            })
        elif "reflect" in prompt_lower or "lesson" in prompt_lower:
            return json.dumps({
                "lesson": "Execution succeeded. No errors encountered.",
                "knowledge_gaps": ["Deeper optimization"],
                "confidence": 0.9
            })

        return f"[Mock Response for model '{model}'] Execution received."

    def chat(self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7) -> str:
        last_msg = messages[-1]["content"] if messages else ""
        return self.generate(last_msg, model, temperature)
