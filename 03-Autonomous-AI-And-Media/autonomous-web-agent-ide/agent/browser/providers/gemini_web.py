"""
Google Gemini Web Persistent Browser LLM Provider
Automates interactions with gemini.google.com with session persistence,
login detection, and seamless cognitive fallback.
"""

import asyncio
import os
import time
import sys
from typing import Dict, Any, Optional

try:
    from browser.providers.base import LLMProvider
    from browser.browser_manager import BrowserManager
    from core.cognitive_engine import CognitiveAIEngine
except ImportError:
    from .base import LLMProvider
    from ..browser_manager import BrowserManager
    from ...core.cognitive_engine import CognitiveAIEngine

class GeminiWebProvider(LLMProvider):
    def __init__(self, profile_dir: Optional[str] = None, headless: bool = False):
        self.browser_manager = BrowserManager(profile_dir=profile_dir, headless=headless)
        self.page = None
        self.url = "https://gemini.google.com/app"

    def log(self, text: str):
        sys.stdout.write(f"{text}\n")
        sys.stdout.flush()

    async def connect(self) -> bool:
        self.log("[Gemini Web] Initializing persistent browser session...")
        try:
            self.page = await self.browser_manager.initialize()
            self.log("[Gemini Web] Navigating to https://gemini.google.com/app...")
            await self.page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            self.log(f"[Gemini Web] Page loaded: {self.page.url}")
            return True
        except Exception as e:
            self.log(f"[Gemini Web] Connection notice: {e}")
            return False

    async def ensure_page_active(self):
        if not self.page or self.page.is_closed():
            await self.connect()
        try:
            current_url = self.page.url
            if "gemini.google.com" not in current_url:
                await self.page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            await self.connect()

    async def dismiss_popups(self):
        if not self.page or self.page.is_closed():
            return
        try:
            await self.page.evaluate("""() => {
                // Dismiss Google cookie / onboarding dialogs
                const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
                for (const b of buttons) {
                    const text = (b.innerText || '').toLowerCase();
                    if (text.includes('i agree') || text.includes('accept all') || text.includes('got it') || text.includes('dismiss')) {
                        b.click();
                    }
                }
            }""")
            await self.page.keyboard.press("Escape")
        except Exception:
            pass

    async def find_input(self) -> Optional[Any]:
        await self.dismiss_popups()
        selectors = [
            "div[contenteditable='true']",
            "rich-textarea textarea",
            "div.ql-editor",
            "textarea",
            "input[type='text']"
        ]
        for sel in selectors:
            try:
                elem = await self.page.query_selector(sel)
                if elem and await elem.is_visible():
                    return elem
            except Exception:
                continue
        return None

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            await self.ensure_page_active()
            await self.dismiss_popups()

            input_elem = await self.find_input()
            if not input_elem:
                self.log("\n[Gemini Web] Login or verification required on gemini.google.com.")
                self.log("[Tip] Run `LOGIN_ASSISTANT.bat` to save your permanent Google login.\n")
                for _ in range(10):
                    await asyncio.sleep(1.5)
                    input_elem = await self.find_input()
                    if input_elem:
                        break

            if not input_elem:
                self.log("[Gemini Web] Input not found. Smoothly delegating to Cognitive AI Brain...")
                return await self._cognitive_fallback(prompt, system_prompt)

            full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            # Count existing responses before sending
            initial_count = await self.get_response_count()

            await input_elem.click()
            await asyncio.sleep(0.2)
            try:
                await input_elem.fill(full_text)
            except Exception:
                await self.page.keyboard.type(full_text, delay=5)
            await asyncio.sleep(0.5)

            # Carefully find Send button (DO NOT click Stop button!)
            send_btn = await self.page.query_selector("button[aria-label*='Send message']")
            if send_btn and await send_btn.is_visible():
                await send_btn.click()
            else:
                await self.page.keyboard.press("Enter")

            self.log("[Gemini Web] Prompt sent! Waiting for response stream...")

            # 1. Wait for generation to start (Stop button appears or new response element created)
            started = False
            for _ in range(12):
                await asyncio.sleep(0.5)
                stop_btn = await self.page.query_selector("button[aria-label*='Stop response']")
                current_count = await self.get_response_count()
                if (stop_btn and await stop_btn.is_visible()) or current_count > initial_count:
                    started = True
                    break

            # 2. Wait for generation to complete (Stop button disappears)
            for _ in range(35):
                await asyncio.sleep(1)
                # Check for Continue button
                await self.check_and_click_continue()
                stop_btn = await self.page.query_selector("button[aria-label*='Stop response']")
                if not stop_btn or not (await stop_btn.is_visible()):
                    # Check one more time before finishing
                    if await self.check_and_click_continue():
                        await asyncio.sleep(1.5)
                        continue
                    await asyncio.sleep(1)
                    break

            # Extract latest response
            text = await self.extract_latest_response()
            if text and len(text.strip()) > 1 and "you stopped this response" not in text.lower():
                return text

            # If stopped or empty, smoothly use cognitive fallback
            return await self._cognitive_fallback(prompt, system_prompt)

        except Exception as e:
            self.log(f"[Gemini Web Notice] Handled: {e}. Using Cognitive Engine fallback.")
            return await self._cognitive_fallback(prompt, system_prompt)

    async def generate_with_images(self, prompt: str, images: list, system_prompt: Optional[str] = None) -> str:
        try:
            await self.ensure_page_active()
            await self.dismiss_popups()
            if images:
                valid_images = [img for img in images if os.path.exists(img)]
                if valid_images:
                    is_zip = any(f.endswith('.zip') or '.part' in f for f in valid_images)
                    label = "archive/code package(s)" if is_zip else "image/media asset(s)"
                    self.log(f"[Gemini Web] Uploading {len(valid_images)} {label}...")

                    # Step 1: Specifically click the Gemini 'Upload and tools' icon button
                    upload_btn = await self.page.query_selector(
                        "button[aria-label*='Upload and tools'], button[aria-label='Upload files'], button[aria-label*='Upload file'], button[aria-label*='Add files']"
                    )
                    if upload_btn:
                        self.log("[Gemini Web] Clicking 'Upload and tools' button...")
                        await upload_btn.click()
                        await asyncio.sleep(1.0)
                    else:
                        self.log("[Gemini Web] Direct upload button not found, searching inputs...")

                    # Step 2: Find file input and attach files
                    file_inputs = await self.page.query_selector_all("input[type='file']")
                    if file_inputs:
                        try:
                            await file_inputs[0].set_input_files(valid_images)
                            self.log(f"[Gemini Web] ✅ {len(valid_images)} file(s) attached successfully!")
                            await asyncio.sleep(2.5)
                        except Exception as upload_err:
                            self.log(f"[Gemini Web Upload Notice] {upload_err}")
                    else:
                        self.log("[Gemini Web] File input not found — appending topology as text context...")
                        try:
                            from core.zip_chunker import generate_workspace_topology
                            topology = generate_workspace_topology(os.path.dirname(valid_images[0]))
                            prompt = f"📦 Project Codebase:\n{topology}\n\n{prompt}"
                        except Exception:
                            pass

            return await self.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            self.log(f"[Gemini Web Upload Notice] {e}. Proceeding with prompt...")
            return await self.generate(prompt, system_prompt=system_prompt)


    async def get_response_count(self) -> int:
        try:
            elems = await self.page.query_selector_all("message-content, model-response, div.markdown")
            return len(elems)
        except Exception:
            return 0

    async def extract_latest_response(self) -> str:
        selectors = [
            "message-content",
            "div.markdown",
            "model-response",
            "div.response-container",
            "div.model-response-text"
        ]
        for sel in selectors:
            try:
                elements = await self.page.query_selector_all(sel)
                if elements:
                    text = await elements[-1].inner_text()
                    text = text.strip()
                    # Strip leading "Gemini said\n" prefix if present
                    if text.startswith("Gemini said"):
                        text = text[len("Gemini said"):].strip()
                    gemini_error_phrases = [
                        "you stopped this response",
                        "i seem to be encountering an error",
                        "can i try something else for you",
                        "something went wrong",
                        "an error occurred",
                        "response was blocked",
                    ]
                    if text and len(text) > 1 and not any(ge in text.lower() for ge in gemini_error_phrases):
                        return text
            except Exception:
                continue
        return ""

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

    async def check_and_click_continue(self) -> bool:
        """Detects and clicks Continue/Continue generating button if present."""
        if not self.page or self.page.is_closed():
            return False
        try:
            clicked = await self.page.evaluate("""() => {
                const keywords = ['continue', 'continue generating', 'keep writing', 'keep going', 'resume'];
                const isExcluded = (el) => !!el.closest('.markdown, pre, code, p, blockquote, .prose');

                const buttons = Array.from(document.querySelectorAll('button, [role="button"], [class*="button"], [class*="btn"]'));
                for (const el of buttons) {
                    if (isExcluded(el)) continue;
                    const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                    const aria = (el.getAttribute('aria-label') || '').trim().toLowerCase();
                    if (txt.length <= 40 && keywords.some(k => txt === k || txt.startsWith(k) || txt.includes(k) || aria.includes(k))) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            el.scrollIntoView({ block: 'center' });
                            ['pointerover', 'mouseover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                                el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
                            });
                            try { el.click(); } catch(e) {}
                            return true;
                        }
                    }
                }
                return false;
            }""")
            if clicked:
                self.log("\r\n\x1b[1;33m[Gemini Web] ⚡ Detected and clicked 'Continue' button via DOM!\x1b[0m\r\n")
                return True

            for sel in [
                "button:has-text('Continue generating')",
                "button:has-text('Continue')",
                "[role='button']:has-text('Continue')",
                "button:has-text('Keep writing')"
            ]:
                try:
                    loc = self.page.locator(sel).first
                    if await loc.is_visible(timeout=200):
                        await loc.scroll_into_view_if_needed(timeout=300)
                        await loc.click(force=True, timeout=500)
                        self.log(f"\r\n\x1b[1;33m[Gemini Web] ⚡ Clicked 'Continue' button via selector: {sel}\x1b[0m\r\n")
                        return True
                except Exception:
                    pass

            return False
        except Exception:
            return False

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.page and not self.page.is_closed() else "disconnected",
            "provider": "gemini_web",
            "url": self.url
        }

    async def close(self):
        await self.browser_manager.close()
