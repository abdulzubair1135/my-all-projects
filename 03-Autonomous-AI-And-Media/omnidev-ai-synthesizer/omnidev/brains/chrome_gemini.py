import time
import re
from pathlib import Path
from typing import Optional, Any
from .base_brain import BaseBrain
import config
from config import console

class ChromeGeminiBrain(BaseBrain):
    """
    Automates interactions with Gemini Web Chat (gemini.google.com)
    using Playwright connected to Chrome on port 9222.
    """
    def __init__(self, cdp_browser=None):
        self.browser = cdp_browser
        self.playwright = None
        self.page = None
        self.is_connected = False

    def ensure_chrome_running(self):
        """Starts Chrome with remote debugging on port 9222 if not running."""
        import socket
        import subprocess
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', config.CHROME_DEBUG_PORT))
        sock.close()
        if result == 0:
            return  # Already running

        console.print("[yellow]Starting Chrome with persistent profile & debugging port 9222 for Gemini...[/yellow]")
        chrome_exe = config.get_chrome_executable()
        profile_dir = str(config.CHROME_PROFILE_DIR)

        cmd = [
            chrome_exe,
            f"--remote-debugging-port={config.CHROME_DEBUG_PORT}",
            f"--user-data-dir={profile_dir}",
            config.GEMINI_URL,
        ]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

    def connect(self) -> bool:
        try:
            from playwright.sync_api import sync_playwright
            self.ensure_chrome_running()

            if not self.playwright:
                self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(config.CHROME_CDP_URL)
            context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()

            # Clean up extension tabs
            for p in list(context.pages):
                if any(bad in p.url.lower() for bad in ["vid-adblocker", "shortkeys", "chrome-extension://"]):
                    try:
                        p.close()
                    except Exception:
                        pass

            # Look for existing Gemini tab
            for p in context.pages:
                if "gemini.google.com" in p.url:
                    self.page = p
                    break

            if not self.page:
                self.page = context.new_page()
                self.page.goto(config.GEMINI_URL, wait_until="domcontentloaded", timeout=30000)

            self.page.bring_to_front()
            self.is_connected = True
            console.print("[green]✓ Connected to Gemini in Chrome successfully![/green]")
            return True
        except Exception as e:
            console.print(f"[yellow]Gemini Web connection notice: {e}[/yellow]")
            return False

    def is_available(self) -> bool:
        if not self.is_connected or not self.page:
            return self.connect()
        try:
            # Check if page is alive
            self.page.evaluate("1+1")
            return True
        except Exception:
            return self.connect()

    def ask(self, prompt: str, new_chat: bool = False, file_to_attach: Optional[Any] = None, image_to_attach: Optional[Any] = None) -> str:
        """
        Sends prompt to Gemini Web (gemini.google.com), handles context & image attachments,
        and extracts pristine code and markdown response.
        """
        if not self.is_available():
            raise RuntimeError("Could not connect to Chrome Gemini session. Please ensure Chrome is running on port 9222.")

        page = self.page
        page.bring_to_front()

        # 1. New Chat handling
        if new_chat:
            try:
                console.print("[cyan]Opening clean new chat on Gemini...[/cyan]")
                new_chat_btn = page.query_selector("button[aria-label*='New chat'], a[aria-label*='New chat'], div:has-text('New chat')")
                if new_chat_btn and new_chat_btn.is_visible():
                    new_chat_btn.click()
                    time.sleep(1.0)
                else:
                    page.goto(config.GEMINI_URL, wait_until="domcontentloaded")
                    time.sleep(1.2)
            except Exception:
                pass

        # 2. Image Attachment for Gemini Vision
        if image_to_attach and Path(image_to_attach).exists():
            try:
                img_path = str(Path(image_to_attach).resolve())
                console.print(f"[cyan]📷 Attaching screenshot/image to Gemini Vision: {Path(image_to_attach).name}...[/cyan]")
                file_input = page.query_selector("input[type='file']")
                if file_input:
                    page.set_input_files("input[type='file']", img_path)
                    time.sleep(1.5)
            except Exception as ie:
                console.print(f"[yellow]Image attachment note: {ie}[/yellow]")

        # 3. File Context / Bundle injection
        if file_to_attach and Path(file_to_attach).exists():
            try:
                bundle_text = Path(file_to_attach).read_text(encoding="utf-8", errors="ignore")
                fname = Path(file_to_attach).name
                console.print(f"[cyan]📦 Injecting project bundle ({len(bundle_text)} chars) into Gemini prompt...[/cyan]")
                prompt = f"PROJECT CONTEXT FILES ({fname}):\n```text\n{bundle_text}\n```\n\n{prompt}"
            except Exception as fe:
                console.print(f"[yellow]Bundle read note: {fe}[/yellow]")

        # 4. Locate Gemini Input Element
        input_selectors = [
            "rich-textarea div[contenteditable='true']",
            "div[contenteditable='true']",
            "p[data-placeholder]",
            "textarea",
            "div[role='textbox']"
        ]

        input_el = None
        for sel in input_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                if el and el.is_visible():
                    input_el = el
                    break
            except Exception:
                continue

        # 4. Record initial response count to only capture the NEW response
        initial_response_count = page.evaluate("""() => {
            const containers = Array.from(document.querySelectorAll('message-content, .model-response-text, model-response, [class*="response-content"]'));
            return containers.length;
        }""")

        console.print("[cyan]Sending prompt to Gemini Web (Fast Engine)...[/cyan]")
        
        # 5. Clean, reliable prompt insertion with Angular state update
        page.evaluate("""(text) => {
            const input = document.querySelector("rich-textarea div[contenteditable='true'], div[contenteditable='true'], p[data-placeholder], textarea");
            if (!input) return false;
            input.focus();
            
            if (input.isContentEditable) {
                // Clear any existing text
                document.execCommand('selectAll', false, null);
                const ok = document.execCommand('insertText', false, text);
                if (!ok || input.innerText.trim().length === 0) {
                    input.innerHTML = '<p>' + text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</p>';
                }
                input.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertFromPaste' }));
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            } else {
                input.value = text;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }
        }""", prompt)

        time.sleep(0.5)

        # 6. Click Send Button (strictly ONCE)
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, div[role="button"], .send-button'));
            const sendBtn = btns.find(b => {
                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                const title = (b.getAttribute('title') || '').toLowerCase();
                const isMatch = aria.includes('send') || aria.includes('submit') || title.includes('send') || (b.className || '').includes('send');
                const isDisabled = b.getAttribute('disabled') !== null || b.getAttribute('aria-disabled') === 'true';
                return isMatch && !isDisabled;
            });
            if (sendBtn) {
                sendBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
                ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                    sendBtn.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
                });
                sendBtn.click();
            }
        }""")

        # Fallback Enter press to ensure prompt dispatches
        try:
            input_el.press("Enter")
        except Exception:
            pass

        console.print("[magenta]Waiting for Gemini response...[/magenta]")
        time.sleep(3.0)

        # 7. Wait for Generation to Complete
        max_wait = 180
        start_t = time.time()
        prev_text = ""
        stable_count = 0

        while time.time() - start_t < max_wait:
            time.sleep(1.5)

            try:
                # Check if streaming / stop button is present
                is_streaming = page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                    return btns.some(b => {
                        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                        const isStop = aria.includes('stop') || aria.includes('cancel');
                        const rect = b.getBoundingClientRect();
                        return isStop && rect.width > 0 && rect.height > 0;
                    });
                }""")

                if is_streaming:
                    stable_count = 0
                    time.sleep(1.0)
                    continue

                # Extract only the NEW assistant response
                current_text = page.evaluate("""(initCount) => {
                    const containers = Array.from(document.querySelectorAll('message-content, .model-response-text, model-response, [class*="response-content"]'));
                    if (containers.length === 0) return null;
                    if (containers.length <= initCount && initCount > 0) return null;
                    const lastEl = containers[containers.length - 1];

                    const livePres = Array.from(lastEl.querySelectorAll('pre'));
                    const clone = lastEl.cloneNode(true);

                    // Remove copy/download buttons and header noise
                    const noise = Array.from(clone.querySelectorAll('button, [class*="header"], [class*="copy"], [class*="action"]'));
                    noise.forEach(n => n.remove());

                    const clonePres = Array.from(clone.querySelectorAll('pre'));
                    clonePres.forEach((pre, idx) => {
                        const livePre = livePres[idx];
                        let codeText = "";
                        if (livePre) {
                            const liveCode = livePre.querySelector('code');
                            codeText = (liveCode ? liveCode.innerText : livePre.innerText) || livePre.textContent || "";
                        } else {
                            const codeEl = pre.querySelector('code');
                            codeText = (codeEl ? codeEl.innerText : pre.innerText) || pre.textContent || "";
                        }

                        codeText = codeText.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');
                        const trimmed = codeText.trim();
                        let lang = 'gdscript';
                        if (trimmed.startsWith('<!DOCTYPE html') || trimmed.startsWith('<html')) lang = 'html';
                        else if (trimmed.startsWith('[gd_scene') || trimmed.startsWith('[ext_resource')) lang = 'gdscene';
                        else if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
                            try { JSON.parse(trimmed); lang = 'json'; } catch(e) {}
                        } else if (trimmed.includes('import ') || trimmed.includes('def ')) lang = 'python';

                        const rep = document.createElement('div');
                        rep.textContent = '\\n```' + lang + '\\n' + trimmed + '\\n```\\n';
                        pre.parentNode.replaceChild(rep, pre);
                    });

                    const blockEls = Array.from(clone.querySelectorAll('p, div, h1, h2, h3, h4, h5, h6, li'));
                    blockEls.forEach(b => b.appendChild(document.createTextNode('\\n')));

                    const result = clone.textContent || clone.innerText || "";
                    return result.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');
                }""", initial_response_count)

                if current_text and current_text.strip() != prompt.strip() and len(current_text.strip()) > 20:
                    if current_text == prev_text:
                        stable_count += 1
                        if stable_count >= 3:
                            return current_text
                    else:
                        stable_count = 0
                        prev_text = current_text
            except Exception as err:
                if any(k in str(err) for k in ["destroyed", "closed", "Target page"]):
                    time.sleep(1.5)
                    continue

        return prev_text or "No response captured from Gemini."

    def close(self):
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

