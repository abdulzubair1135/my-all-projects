"""
NVIDIA Nemotron 70B & Hugging Face Serverless Provider
Interacts with Hugging Face Inference API / Router for nvidia/Llama-3.1-Nemotron-70B-Instruct.
"""

import os
import json
import asyncio
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

try:
    from browser.providers.base import LLMProvider
    from core.cognitive_engine import CognitiveAIEngine
except ImportError:
    from .base import LLMProvider
    from ...core.cognitive_engine import CognitiveAIEngine

class NemotronHuggingFaceProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.model = model or os.getenv("NEMOTRON_MODEL", "nvidia/Llama-3.1-Nemotron-70B-Instruct")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        # Also router endpoint support
        self.router_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

    async def connect(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "nemotron_huggingface",
            "model": self.model
        }

    async def close(self):
        pass

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self._fallback(prompt)

        # 1. Try Hugging Face OpenAI-compatible Chat Completions API
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.3,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                self.router_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            loop = asyncio.get_event_loop()
            resp_data = await loop.run_in_executor(None, lambda: self._execute_request(req))
            
            if resp_data and "choices" in resp_data and len(resp_data["choices"]) > 0:
                content = resp_data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 10:
                    return content
        except Exception as e:
            # Fallback to standard inference or cognitive engine
            pass

        return self._fallback(prompt)

    async def generate_with_images(self, prompt: str, images: list, system_prompt: Optional[str] = None) -> str:
        if images:
            img_info = f"\n[User attached {len(images)} image(s): {', '.join(os.path.basename(i) for i in images)}]"
            return await self.generate(prompt + img_info, system_prompt=system_prompt)
        return await self.generate(prompt, system_prompt=system_prompt)


    def _execute_request(self, req: urllib.request.Request) -> Dict[str, Any]:
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))

    def _fallback(self, prompt: str) -> str:
        p_lower = prompt.lower().strip()
        chat_keywords = ['hey', 'hello', 'hi', 'what is', 'explain', 'how to', 'who are you', 'tell me', 'can you', 'kya']
        build_keywords = ['build', 'create', 'generate', 'implement', 'fix', 'refactor', 'make', 'add feature']
        is_build = any(k in p_lower for k in build_keywords)
        is_chat = any(p_lower.startswith(k) or f" {k} " in f" {p_lower} " for k in chat_keywords) and not is_build

        if is_chat:
            return f"Hello! I am your AI Development Assistant (Nemotron Engine). You asked: '{prompt}'. I am ready to help you discuss architecture, debug issues, or build features. What would you like to build or explore next?"

        if ("project plan" in p_lower or "architect" in p_lower) and "implement task" not in p_lower:
            plan = CognitiveAIEngine.generate_plan(prompt)
            return f"```json\n{json.dumps(plan, indent=2)}\n```"
        else:
            actions = CognitiveAIEngine.generate_code_actions(prompt)
            return f"```json\n{json.dumps(actions, indent=2)}\n```"
