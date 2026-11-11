import requests
import json
from typing import Optional
from .base_brain import BaseBrain
import config

class ApiFallbackBrain(BaseBrain):
    """
    Direct API caller for DeepSeek and Gemini.
    Activated when API keys are available in environment or config.
    """
    def __init__(self, deepseek_key: Optional[str] = None, gemini_key: Optional[str] = None):
        self.deepseek_key = deepseek_key or config.DEEPSEEK_API_KEY
        self.gemini_key = gemini_key or config.GEMINI_API_KEY

    def is_available(self) -> bool:
        return bool(self.deepseek_key or self.gemini_key)

    def ask(self, prompt: str) -> str:
        if self.deepseek_key:
            return self._ask_deepseek_api(prompt)
        elif self.gemini_key:
            return self._ask_gemini_api(prompt)
        else:
            raise RuntimeError("No API key configured for Direct API Brain.")

    def _ask_deepseek_api(self, prompt: str) -> str:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_key}"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are OmniDev AI, an expert software developer and autonomous agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _ask_gemini_api(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
