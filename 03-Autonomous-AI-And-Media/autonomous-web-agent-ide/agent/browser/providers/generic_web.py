"""
ChatGPT & Generic Web LLM Provider
Automates interactions with chatgpt.com with modal dismissal,
session persistence, and cognitive fallback.
"""

import asyncio
import os
import time
import sys
from typing import Dict, Any, Optional
from .base import LLMProvider
from ..browser_manager import BrowserManager

try:
    from core.cognitive_engine import CognitiveAIEngine
except ImportError:
    from ...core.cognitive_engine import CognitiveAIEngine

class GenericWebProvider(LLMProvider):
    def __init__(self, target_url: str = "https://chatgpt.com", profile_dir: Optional[str] = None, headless: bool = False):
        self.browser_manager = BrowserManager(profile_dir=profile_dir, headless=headless)
        self.url = target_url
        self.page = None

    def log(self, text: str):
        sys.stdout.write(f"{text}\n")
        sys.stdout.flush()

    async def connect(self) -> bool:
        self.log(f"[ChatGPT Web] Connecting to {self.url}...")
        try:
            self.page = await self.browser_manager.initialize()
            await self.page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            await self.dismiss_login_modal()
            return True
        except Exception as e:
            self.log(f"[ChatGPT Web] Connection notice: {e}")
            return False

    async def ensure_page_active(self):
        if not self.page or self.page.is_closed():
            await self.connect()
        try:
            if self.url not in self.page.url:
                await self.page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            await self.connect()

    async def dismiss_login_modal(self):
        if not self.page or self.page.is_closed():
            return
        try:
            await self.page.evaluate("""() => {
                // Dismiss ChatGPT "Log in or sign up" modal by clicking close button or pressing escape
                const closeBtns = document.querySelectorAll('button[aria-label="Close"], button:has(svg), div[role="dialog"] button');
                for (const b of closeBtns) {
                    if (b.innerText.includes('✕') || b.getAttribute('aria-label') === 'Close') {
                        b.click();
                    }
                }
            }""")
            await self.page.keyboard.press("Escape")
        except Exception:
            pass

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            if not self.page or self.page.is_closed():
                await self.connect()

            await self.dismiss_login_modal()

            # Find input box
            input_selectors = [
                "#prompt-textarea",
                "div#prompt-textarea",
                "div[contenteditable='true']",
                "textarea[placeholder*='Message']",
                "textarea"
            ]

            input_elem = None
            for sel in input_selectors:
                try:
                    elem = await self.page.query_selector(sel)
                    if elem and await elem.is_visible():
                        input_elem = elem
                        break
                except Exception:
                    continue

            if not input_elem:
                self.log("[ChatGPT Web] Login required on chatgpt.com. Delegating to Cognitive AI Brain...")
                return await self._cognitive_fallback(prompt, system_prompt)

            full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            await input_elem.click()
            await asyncio.sleep(0.2)
            await input_elem.fill(full_text)
            await asyncio.sleep(0.4)
            await input_elem.press("Enter")

            self.log("[ChatGPT Web] Prompt sent! Waiting for response...")
            await asyncio.sleep(4)

            response_selectors = [
                "[data-message-author-role='assistant']",
                ".font-claude-message",
                ".prose",
                "div[class*='markdown']"
            ]

            for _ in range(30):
                await asyncio.sleep(1)
                for sel in response_selectors:
                    try:
                        elems = await self.page.query_selector_all(sel)
                        if elems:
                            text = await elems[-1].inner_text()
                            if len(text.strip()) > 30:
                                return text
                    except Exception:
                        continue

            return await self._cognitive_fallback(prompt, system_prompt)

        except Exception as e:
            self.log(f"[ChatGPT Web Notice] Handled: {e}. Using Cognitive Brain.")
            return await self._cognitive_fallback(prompt, system_prompt)

    async def generate_with_images(self, prompt: str, images: list, system_prompt: Optional[str] = None) -> str:
        try:
            await self.ensure_page_active()
            if images:
                file_input = await self.page.query_selector("input[type='file']")
                if file_input:
                    valid_images = [img for img in images if os.path.exists(img)]
                    if valid_images:
                        self.log(f"[ChatGPT Web] Uploading {len(valid_images)} image(s)...")
                        await file_input.set_input_files(valid_images)
                        await asyncio.sleep(2.0)
            return await self.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            self.log(f"[ChatGPT Web Upload Notice] {e}. Proceeding with prompt...")
            return await self.generate(prompt, system_prompt=system_prompt)


    async def _cognitive_fallback(self, prompt: str, system_prompt: Optional[str]) -> str:
        prompt_lower = prompt.lower()
        if (system_prompt and "conversational question" in system_prompt.lower()) or "what is" in prompt_lower or prompt_lower.strip() in ["hey", "hi", "hello"]:
            return CognitiveAIEngine.generate_conversational_response(prompt)
        elif "generate project plan" in prompt_lower or "project plan with tasks" in prompt_lower or "task graph" in prompt_lower:
            plan = CognitiveAIEngine.generate_plan(prompt)
            import json
            return f"```json\n{json.dumps(plan, indent=2)}\n```"
        else:
            actions = CognitiveAIEngine.generate_code_actions(prompt)
            import json
            return f"```json\n{json.dumps(actions, indent=2)}\n```"

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.page and not self.page.is_closed() else "disconnected",
            "provider": "generic_web",
            "url": self.url
        }

    async def close(self):
        await self.browser_manager.close()
