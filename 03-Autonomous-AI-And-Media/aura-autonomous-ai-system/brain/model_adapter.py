"""
AURA Model Adapter.
Decouples AURA Cognitive Core from specific LLM runtimes (Ollama, llama.cpp, Mock, etc.).
"""

from typing import List, Dict, Any, Optional
from config import config
from brain.ollama_backend import BaseModelBackend, OllamaBackend, MockBackend
from core.logger import setup_logger

logger = setup_logger("ModelAdapter")

class ModelAdapter:
    def __init__(self, backend: Optional[BaseModelBackend] = None):
        if backend is not None:
            self.backend = backend
        elif config.models.use_mock:
            logger.info("Initializing ModelAdapter with MockBackend")
            self.backend = MockBackend()
        else:
            logger.info(f"Initializing ModelAdapter with OllamaBackend ({config.models.ollama_base_url})")
            self.backend = OllamaBackend()
        
        self.call_count = 0

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> str:
        target_model = model or config.models.normal_model
        self.call_count += 1
        logger.debug(f"Generate call #{self.call_count} using model '{target_model}'")
        
        try:
            return self.backend.generate(prompt, target_model, temperature, system)
        except Exception as e:
            logger.warning(f"Primary backend failed for model '{target_model}': {e}. Retrying with MockBackend fallback.")
            fallback = MockBackend()
            return fallback.generate(prompt, target_model, temperature, system)

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        target_model = model or config.models.normal_model
        self.call_count += 1
        logger.debug(f"Chat call #{self.call_count} using model '{target_model}'")
        
        try:
            return self.backend.chat(messages, target_model, temperature)
        except Exception as e:
            logger.warning(f"Primary backend chat failed for model '{target_model}': {e}. Retrying with MockBackend fallback.")
            fallback = MockBackend()
            return fallback.chat(messages, target_model, temperature)

# Default global adapter instance
model_adapter = ModelAdapter()
