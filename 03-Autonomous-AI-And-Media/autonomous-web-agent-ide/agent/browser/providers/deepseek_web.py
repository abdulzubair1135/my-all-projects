"""
DeepSeek Web Persistent Browser LLM Provider
Automates interactions with chat.deepseek.com using persistent cookies,
DeepThink (R1) reasoning mode activation, and resilient fallback.
"""

import asyncio
import os
import time
import sys
from typing import Dict, Any, Optional

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from browser.providers.base import LLMProvider
    from browser.browser_manager import BrowserManager
    from core.cognitive_engine import CognitiveAIEngine
except ImportError:
    from .base import LLMProvider
    from ..browser_manager import BrowserManager
    from ...core.cognitive_engine import CognitiveAIEngine

class DeepSeekWebProvider(LLMProvider):
    def __init__(self, profile_dir: Optional[str] = None, headless: bool = False):
        self.browser_manager = BrowserManager(profile_dir=profile_dir, headless=headless)
        self.page = None
        self.url = "https://chat.deepseek.com"
        self.is_authenticated = False

    def log(self, text: str):
        try:
            sys.stdout.write(f"{text}\n")
            sys.stdout.flush()
        except Exception:
            try:
                sys.stdout.buffer.write(f"{text}\n".encode('utf-8', errors='replace'))
                sys.stdout.flush()
            except Exception:
                pass

    async def connect(self) -> bool:
        self.log("[DeepSeek Web] Initializing persistent Chromium browser session...")
        try:
            self.page = await self.browser_manager.initialize()
            self.log("[DeepSeek Web] Navigating to https://chat.deepseek.com...")
            await self.page.goto(self.url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(2)
            self.log(f"[DeepSeek Web] Page loaded: {self.page.url}")
            return True
        except Exception as e:
            self.log(f"[DeepSeek Web] Connection notice: {e}")
            return False

    async def ensure_page_active(self):
        if not self.page or self.page.is_closed():
            await self.connect()
        try:
            current_url = self.page.url
            if "deepseek.com" not in current_url:
                await self.page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            await self.connect()

    async def dismiss_popups(self):
        if not self.page or self.page.is_closed():
            return
        try:
            await self.page.evaluate("""() => {
                const searchInputs = document.querySelectorAll('input[placeholder*="Search"]');
                for (const inp of searchInputs) {
                    const modal = inp.closest('div[class*="modal"], div[class*="dialog"], div[role="dialog"]');
                    if (modal) modal.remove();
                }
            }""")
            await self.page.keyboard.press("Escape")
            await asyncio.sleep(0.1)
        except Exception:
            pass

    async def enable_deepthink_r1(self):
        """Clicks the DeepThink (R1) reasoning toggle in DeepSeek Web UI if not enabled."""
        if not self.page or self.page.is_closed():
            return
        try:
            await self.page.evaluate("""() => {
                const items = Array.from(document.querySelectorAll('div, button, span'));
                for (const el of items) {
                    const text = (el.innerText || '').trim();
                    if (text === 'DeepThink (R1)' || text === 'DeepThink' || text.includes('DeepThink')) {
                        const target = el.closest('button, div[role="button"], div[class*="ds-button"]') || el;
                        const cls = (target.className || '').toString().toLowerCase();
                        const isChecked = target.getAttribute('aria-checked') === 'true' || cls.includes('active') || cls.includes('checked');
                        if (!isChecked && typeof target.click === 'function') {
                            target.click();
                        }
                        break;
                    }
                }
            }""")
            await asyncio.sleep(0.2)
        except Exception:
            pass

    async def find_main_chat_textarea(self) -> Optional[Any]:
        await self.dismiss_popups()

        input_selectors = [
            "textarea#chat-input",
            "textarea[placeholder*='Message DeepSeek']",
            "textarea[placeholder*='DeepSeek']",
            "textarea[placeholder*='Message']",
            "div[contenteditable='true']",
            "textarea:not([placeholder*='Search' i])"
        ]

        for sel in input_selectors:
            try:
                elem = await self.page.query_selector(sel)
                if elem and await elem.is_visible():
                    return elem
            except Exception:
                continue
        return None

    async def check_and_wait_for_login(self, timeout_sec: int = 40) -> bool:
        input_elem = await self.find_main_chat_textarea()
        if input_elem:
            self.is_authenticated = True
            return True

        self.log("\n" + "=" * 65)
        self.log("[DeepSeek Web] AUTHENTICATION REQUIRED")
        self.log("Please log in to DeepSeek in the opened Chromium browser window.")
        self.log("(Tip: Run `LOGIN_ASSISTANT.bat` to save your permanent login!)")
        self.log("=" * 65 + "\n")

        start = time.time()
        while time.time() - start < timeout_sec:
            await asyncio.sleep(2)
            input_elem = await self.find_main_chat_textarea()
            if input_elem:
                self.log("[DeepSeek Web] Login successfully detected!")
                self.is_authenticated = True
                return True

        self.log("[DeepSeek Web Warning] Login wait timeout reached. Delegating to Cognitive AI Brain...")
        return False

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            await self.ensure_page_active()
            await self.dismiss_popups()

            is_ready = await self.check_and_wait_for_login(timeout_sec=30)
            if not is_ready:
                return await self._cognitive_fallback(prompt, system_prompt)

            input_elem = await self.find_main_chat_textarea()
            if not input_elem:
                return await self._cognitive_fallback(prompt, system_prompt)

            # Ensure DeepThink (R1) is activated
            await self.enable_deepthink_r1()

            # Re-inject long-term persistent project memory chronicle
            try:
                from core.project_memory import ProjectMemoryManager
                mem_mgr = ProjectMemoryManager()
                ws_dir = os.environ.get("AGENT_WORKSPACE") or os.getcwd()
                memory_ledger = mem_mgr.get_project_memory_prompt(ws_dir)
                if memory_ledger:
                    prompt = f"{memory_ledger}\n\n{prompt}"
            except Exception:
                pass

            full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            # Focus input
            await input_elem.click()
            await asyncio.sleep(0.2)

            self.log("[DeepSeek Web] Activating DeepThink (R1) reasoning mode and typing prompt...")

            # Multiple robust input methods
            filled = False
            try:
                await input_elem.fill(full_text)
                filled = True
            except Exception:
                pass

            if not filled:
                await self.page.evaluate("""
                    (text) => {
                        const el = document.querySelector('textarea#chat-input') 
                                || document.querySelector('textarea[placeholder*="Message DeepSeek"]')
                                || document.querySelector('textarea:not([placeholder*="Search"])');
                        if (el) {
                            el.focus();
                            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
                            if (setter) {
                                setter.call(el, text);
                            } else {
                                el.value = text;
                            }
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                """, full_text)

            await asyncio.sleep(0.4)

            self.log("[DeepSeek Web] Sending prompt to DeepSeek R1...")
            sent = await self.page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('div, button'));
                for (const b of buttons) {
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    const cls = (b.className || '').toString().toLowerCase();
                    if (
                        aria.includes('send') ||
                        cls.includes('send-button') ||
                        (cls.includes('ds-icon-button') && b.querySelector('svg'))
                    ) {
                        if (typeof b.click === 'function') {
                            b.click();
                            return true;
                        }
                    }
                }
                return false;
            }""")

            if not sent:
                await input_elem.focus()
                await self.page.keyboard.press("Enter")

            self.log("[DeepSeek Web] Prompt sent! DeepSeek is thinking & generating response...")

            # Wait for response completion
            await asyncio.sleep(3)

            stop_selectors = [
                "button:has-text('Stop')",
                "div[class*='stop-generating']",
                "button[aria-label*='Stop' i]",
                "div[class*='generating']"
            ]

            start_wait = time.time()
            max_wait = 300  # 5 minutes timeout per task
            printed_length = 0
            last_text_length = 0
            stable_count = 0
            continue_clicks = 0
            max_continues = 10

            while time.time() - start_wait < max_wait:
                is_generating = False
                for sel in stop_selectors:
                    try:
                        stop_btn = await self.page.query_selector(sel)
                        if stop_btn and await stop_btn.is_visible():
                            is_generating = True
                            break
                    except Exception:
                        pass

                current_text = await self.extract_latest_response()
                if len(current_text) > printed_length:
                    new_chunk = current_text[printed_length:]
                    # Log real-time dialogue snippet
                    if len(new_chunk) > 30 or not is_generating:
                        self.log(f"\x1b[0;32m{new_chunk}\x1b[0m")
                        printed_length = len(current_text)

                if len(current_text) > 0 and len(current_text) == last_text_length:
                    stable_count += 1
                else:
                    stable_count = 0
                    last_text_length = len(current_text)

                # Proactively check if DeepSeek paused on 'Continue' button
                if continue_clicks < max_continues:
                    has_continue = await self.check_and_click_continue()
                    if has_continue:
                        continue_clicks += 1
                        self.log(f"\r\n\x1b[1;33m[DeepSeek Web] ⚡ Detected 'Continue' button (#{continue_clicks})! Auto-clicked to continue code generation...\x1b[0m\r\n")
                        stable_count = 0
                        start_wait = time.time()  # Reset timeout for continuation stream
                        await asyncio.sleep(1.5)
                        continue

                # Finish check: only finish when not generating, stable for 3 cycles, and no Continue button on page
                if not is_generating and stable_count >= 3 and len(current_text) > 20:
                    # Mandatory pre-exit Continue check: NEVER exit if DeepSeek is paused on a Continue button!
                    if continue_clicks < max_continues:
                        has_continue_pre_exit = await self.check_and_click_continue()
                        if has_continue_pre_exit:
                            continue_clicks += 1
                            self.log(f"\r\n\x1b[1;33m[DeepSeek Web] ⚡ Detected 'Continue' button before exiting (#{continue_clicks})! Resuming generation stream...\x1b[0m\r\n")
                            stable_count = 0
                            start_wait = time.time()
                            await asyncio.sleep(2.0)
                            continue

                    self.log(f"\r\n\x1b[1;32m[DeepSeek Web] Response generation finished ({len(current_text)} characters).\x1b[0m\r\n")
                    break

                await asyncio.sleep(0.8)

            final_response = await self.extract_latest_response()
            if final_response and len(final_response.strip()) > 10:
                return final_response

            return await self._cognitive_fallback(prompt, system_prompt)

        except Exception as e:
            self.log(f"[DeepSeek Web Notice] Handled: {e}. Using Cognitive Engine.")
            return await self._cognitive_fallback(prompt, system_prompt)

    async def generate_with_images(self, prompt: str, images: list, system_prompt: Optional[str] = None) -> str:
        try:
            await self.ensure_page_active()
            await self.dismiss_popups()
            if images:
                valid_files = [f for f in images if os.path.exists(f)]
                if valid_files:
                    # DeepSeek Web accepts .txt, .md, .py, .js, .json but rejects raw .zip
                    files_to_upload = []
                    for f in valid_files:
                        if f.endswith('.zip') or '.part' in f:
                            try:
                                import zipfile
                                bundle_path = f.replace('.zip', '_bundle.txt')
                                with zipfile.ZipFile(f, 'r') as zf:
                                    with open(bundle_path, 'w', encoding='utf-8', errors='replace') as out:
                                        out.write(f"=== PROJECT CODEBASE ARCHIVE: {os.path.basename(f)} ===\n\n")
                                        for name in zf.namelist():
                                            if not name.endswith('/') and not any(ig in name for ig in ['node_modules', '.git', '__pycache__', '.godot']):
                                                try:
                                                    content = zf.read(name).decode('utf-8', errors='replace')
                                                    out.write(f"\n--- FILE: {name} ---\n{content[:5000]}\n")
                                                except Exception:
                                                    pass
                                files_to_upload.append(bundle_path)
                                self.log(f"[DeepSeek Web] Packaged workspace archive into {os.path.basename(bundle_path)} for DeepSeek upload...")
                            except Exception:
                                files_to_upload.append(f)
                        else:
                            files_to_upload.append(f)

                    self.log(f"[DeepSeek Web] Uploading {len(files_to_upload)} file(s) via file input...")
                    file_input = await self.page.query_selector("input[type='file']")
                    if file_input:
                        try:
                            await file_input.set_input_files(files_to_upload)
                            self.log(f"[DeepSeek Web] ✅ {len(files_to_upload)} file(s) attached successfully!")
                            await asyncio.sleep(2.5)
                        except Exception as upload_err:
                            self.log(f"[DeepSeek Web Upload Notice] {upload_err}")
                    else:
                        self.log("[DeepSeek Web] File input not found — appending topology as text context...")
                        try:
                            from core.zip_chunker import generate_workspace_topology
                            topology = generate_workspace_topology(os.path.dirname(valid_files[0]))
                            prompt = f"📦 Project Codebase:\n{topology}\n\n{prompt}"
                        except Exception:
                            pass

            return await self.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            self.log(f"[DeepSeek Web Upload Notice] {e}. Proceeding with prompt...")
            return await self.generate(prompt, system_prompt=system_prompt)


    async def check_and_click_continue(self) -> bool:
        """
        Detects if DeepSeek stopped mid-generation and displayed a 'Continue' button.
        Uses multi-strategy DOM evaluation, scroll-into-view, and synthetic events.
        Guaranteed to click the button regardless of wrapper styling.
        """
        if not self.page or self.page.is_closed():
            return False

        try:
            # 1. Scroll all scrollable containers to bottom so button is visible
            try:
                await self.page.evaluate("""() => {
                    window.scrollTo(0, document.body.scrollHeight);
                    const scrollables = document.querySelectorAll('*');
                    for (const el of scrollables) {
                        if (el.scrollHeight > el.clientHeight && el.clientHeight > 120) {
                            el.scrollTop = el.scrollHeight;
                        }
                    }
                }""")
            except Exception:
                pass

            await asyncio.sleep(0.3)

            # 2. Precision DOM evaluation and click
            clicked = await self.page.evaluate("""() => {
                const keywords = [
                    'continue', 'continue generating', 'keep writing', 'keep going',
                    'resume', 'continue response', '继续', '继续生成', '继续输出'
                ];

                // Direct search across all candidate elements
                const candidates = Array.from(document.querySelectorAll('button, div[role="button"], .ds-button, [class*="button"], [class*="btn"], span, a, div'));
                for (const el of candidates) {
                    // Ignore code block bodies
                    if (el.tagName === 'PRE' || el.tagName === 'CODE') continue;

                    const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                    const aria = (el.getAttribute('aria-label') || '').trim().toLowerCase();

                    const isMatch = keywords.some(k => txt === k || aria === k || (txt.startsWith(k) && txt.length <= 25));
                    if (isMatch) {
                        const target = el.closest('button, div[role="button"], .ds-button') || el;
                        const rect = target.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            target.scrollIntoView({ block: 'center', inline: 'center' });
                            ['pointerover', 'mouseover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                                target.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
                            });
                            try { target.click(); } catch(e) {}
                            return true;
                        }
                    }
                }
                return false;
            }""")

            if clicked:
                self.log("\r\n\x1b[1;33m[DeepSeek Web] ⚡ Successfully auto-clicked 'Continue' button via DOM evaluation!\x1b[0m\r\n")
                return True

            # 3. Playwright selector fallback with multiple variants
            fallback_selectors = [
                "button:has-text('Continue')",
                "div[role='button']:has-text('Continue')",
                ".ds-button:has-text('Continue')",
                "span:has-text('Continue')",
                "button:has-text('Continue generating')",
                "button:has-text('继续生成')",
                "button:has-text('继续')",
                "text='Continue'"
            ]
            for sel in fallback_selectors:
                try:
                    locators = self.page.locator(sel)
                    count = await locators.count()
                    for i in range(count):
                        btn = locators.nth(i)
                        if await btn.is_visible():
                            await btn.scroll_into_view_if_needed()
                            await btn.click(force=True)
                            self.log(f"\r\n\x1b[1;33m[DeepSeek Web] ⚡ Successfully clicked 'Continue' button via selector: {sel}\x1b[0m\r\n")
                            return True
                except Exception:
                    pass

            return False
        except Exception:
            return False

    async def _cognitive_fallback(self, prompt: str, system_prompt: Optional[str]) -> str:
        prompt_lower = prompt.lower()
        sys_lower = (system_prompt or "").lower()
        import json

        if (
            "conversational" in sys_lower or
            "consultant" in sys_lower or
            "do not output json" in sys_lower or
            prompt_lower.strip() in ["hey", "hi", "hello", "suno", "kaise ho"] or
            prompt_lower.startswith("what is") or
            prompt_lower.startswith("what are") or
            prompt_lower.startswith("explain") or
            prompt_lower.startswith("tell me about")
        ):
            return CognitiveAIEngine.generate_conversational_response(prompt)

        if "plan" in prompt_lower or "architect" in prompt_lower or "dag" in prompt_lower:
            plan = CognitiveAIEngine.generate_plan(prompt)
            return f"```json\n{json.dumps(plan, indent=2)}\n```"
        else:
            actions = CognitiveAIEngine.generate_code_actions(prompt)
            return f"```json\n{json.dumps(actions, indent=2)}\n```"

    async def extract_latest_response(self) -> str:
        if not self.page or self.page.is_closed():
            return ""

        try:
            return await self.page.evaluate("""() => {
                // Look for assistant message containers
                const assistantMessages = Array.from(document.querySelectorAll(
                    'div[data-message-author-role="assistant"], div[class*="assistant"], div[class*="ds-message"]:not([class*="user"])'
                )).filter(el => {
                    const cls = (el.className || '').toLowerCase();
                    return !cls.includes('user') && !el.querySelector('div[class*="user-message"]');
                });

                if (assistantMessages.length > 0) {
                    const lastMsg = assistantMessages[assistantMessages.length - 1];
                    // If there are multiple .ds-markdown blocks inside this assistant message, merge them
                    const markdowns = Array.from(lastMsg.querySelectorAll('.ds-markdown, .markdown'));
                    if (markdowns.length > 0) {
                        return markdowns.map(m => m.innerText || m.textContent || '').join('\\n');
                    }
                    return lastMsg.innerText || lastMsg.textContent || '';
                }

                // Fallback to all markdown containers
                const containers = Array.from(document.querySelectorAll(
                    '.ds-markdown, .markdown, div[class*="message"]:not([class*="user"]), div[class*="assistant"], div[data-message-author-role="assistant"]'
                ));

                if (containers.length > 0) {
                    const last = containers[containers.length - 1];
                    return last.innerText || last.textContent || '';
                }

                const paragraphs = Array.from(document.querySelectorAll('p, pre, code'));
                if (paragraphs.length > 0) {
                    return paragraphs.map(p => p.innerText).join('\\n');
                }

                return '';
            }""")
        except Exception:
            return ""

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.page and not self.page.is_closed() else "disconnected",
            "provider": "deepseek_web",
            "url": self.url
        }

    async def is_logged_in(self) -> bool:
        await self.ensure_page_active()
        elem = await self.find_main_chat_textarea()
        return elem is not None

    async def close(self):
        await self.browser_manager.close()

