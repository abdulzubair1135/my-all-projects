import time
import subprocess
import os
from pathlib import Path
from typing import Optional, Any
from .base_brain import BaseBrain
import config
from config import console

class ChromeDeepSeekBrain(BaseBrain):
    """
    Automates interactions with DeepSeek Web Chat (chat.deepseek.com)
    using Playwright connected to Chrome via CDP on port 9222 with persistent profile.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_connected = False

    def ensure_chrome_running(self):
        """
        Launches Chrome with remote debugging if not already running.
        """
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", config.CHROME_DEBUG_PORT)) == 0:
                # Already running
                return

        console.print("[yellow]Starting Chrome with persistent profile & debugging port 9222...[/yellow]")
        chrome_exe = config.get_chrome_executable()
        profile_dir = str(config.CHROME_PROFILE_DIR)

        cmd = [
            chrome_exe,
            f"--remote-debugging-port={config.CHROME_DEBUG_PORT}",
            f"--user-data-dir={profile_dir}",
            config.DEEPSEEK_URL,
        ]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

    def connect(self) -> bool:
        """
        Connects Playwright to the Chrome instance via CDP.
        """
        try:
            from playwright.sync_api import sync_playwright
            self.ensure_chrome_running()

            if not self.playwright:
                self.playwright = sync_playwright().start()

            self.browser = self.playwright.chromium.connect_over_cdp(config.CHROME_CDP_URL)
            contexts = self.browser.contexts
            context = contexts[0] if contexts else self.browser.new_context()

            # Clean up any unwanted extension tabs (like adblocker or shortkeys welcome pages)
            for p in list(context.pages):
                if any(bad in p.url.lower() for bad in ["vid-adblocker", "shortkeys", "chrome-extension://"]):
                    try:
                        p.close()
                    except Exception:
                        pass

            # Look for existing DeepSeek tab
            target_page = None
            for p in context.pages:
                if "deepseek.com" in p.url:
                    target_page = p
                    break

            if not target_page:
                target_page = context.new_page()
                target_page.goto(config.DEEPSEEK_URL, wait_until="domcontentloaded", timeout=30000)

            self.page = target_page
            
            # Intercept file chooser events so Chromium NEVER opens native OS File Open dialogs
            try:
                self.page.on("filechooser", lambda fc: fc.set_files([]) if not hasattr(self, "_active_attach_file") or not self._active_attach_file else fc.set_files(self._active_attach_file))
            except Exception:
                pass

            self.page.bring_to_front()
            self._feed_or_dismiss_os_file_dialog()
            self.is_connected = True
            console.print("[green]✓ Connected to DeepSeek in Chrome successfully![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error connecting to Chrome Playwright: {e}[/red]")
            self.is_connected = False
            return False

    @staticmethod
    def _feed_or_dismiss_os_file_dialog(file_path: Optional[str] = None):
        """
        If a Windows 'Open' file dialog is present on screen:
        If file_path is provided: Pastes the exact absolute path into the 'File name' box and presses Enter.
        If no file_path: Closes the dialog via WM_CLOSE.
        """
        try:
            import ctypes
            import subprocess
            import time
            user32 = ctypes.windll.user32
            for title in ["Open", "Select a File", "Select file", "ファイルを開く", "Choose File"]:
                hwnd = user32.FindWindowW(None, title)
                if hwnd:
                    if file_path and Path(file_path).exists():
                        clean_path = str(Path(file_path).resolve())
                        user32.SetForegroundWindow(hwnd)
                        time.sleep(0.3)
                        # Set clipboard text and paste + Enter via PowerShell
                        ps_script = f'''
                        Set-Clipboard -Value "{clean_path}"
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.SendKeys]::SendWait("^v")
                        Start-Sleep -Milliseconds 250
                        [System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
                        '''
                        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], timeout=6)
                        time.sleep(1.0)
                    else:
                        user32.PostMessageW(hwnd, 0x0010, 0, 0)
        except Exception:
            pass

    _auto_dismiss_os_file_dialogs = _feed_or_dismiss_os_file_dialog

    def is_available(self) -> bool:
        if not self.is_connected or not self.page:
            return self.connect()
        return True

    def ask(self, prompt: str, new_chat: bool = False, file_to_attach: Optional[Any] = None) -> str:
        """
        Types prompt into DeepSeek chat, sends it, waits for completion,
        and extracts the response.
        """
        if not self.is_available():
            raise RuntimeError("Could not connect to Chrome DeepSeek session.")

        self._feed_or_dismiss_os_file_dialog(str(file_to_attach) if file_to_attach else None)
        self._active_attach_file = str(file_to_attach) if file_to_attach else None
        page = self.page
        page.bring_to_front()

        # Only open a fresh clean new chat when explicitly requested (e.g. brand new user task)
        if new_chat:
            try:
                if "/a/chat/s/" in page.url:
                    console.print("[cyan]Opening clean new chat on DeepSeek...[/cyan]")
                    page.goto(config.DEEPSEEK_URL, wait_until="domcontentloaded")
                    time.sleep(1.2)
                else:
                    new_chat_btn = page.query_selector("div:has-text('New chat'), button:has-text('New chat')")
                    if new_chat_btn and new_chat_btn.is_visible():
                        new_chat_btn.click()
                        time.sleep(0.8)
            except Exception:
                pass

        # Manage file attachment (.py, .zip, etc.) in the chat input box
        attachment_succeeded = False
        if file_to_attach and Path(file_to_attach).exists():
            try:
                fname = Path(file_to_attach).name
                
                # Check for existing valid / error badges
                badge_status = page.evaluate("""(name) => {
                    const textarea = document.querySelector('textarea');
                    const box = textarea ? (textarea.closest('div[class*="chat-input"]') || textarea.parentElement.parentElement.parentElement) : document.body;
                    const badges = Array.from(box.querySelectorAll('.ds-animated-size-item, div[class*="animated-size"], div[class*="badge"], div[class*="file"]'));
                    const nameBadges = badges.filter(b => (b.innerText || b.textContent || '').includes(name));
                    if (nameBadges.length === 0) return { exists: false, error: false };
                    
                    const hasError = nameBadges.some(b => {
                        const t = (b.innerText || b.textContent || '').toLowerCase();
                        return t.includes('server busy') || t.includes('failed') || t.includes('error') || t.includes('失败') || t.includes('繁忙');
                    });
                    return { exists: true, error: hasError };
                }""", fname)

                # If there's an error badge, purge it immediately
                if badge_status.get("error"):
                    console.print(f"[yellow]⚠️ Detected failed attachment / 'Server busy' on DeepSeek, purging broken badges...[/yellow]")
                    page.evaluate("""() => {
                        const textarea = document.querySelector('textarea');
                        const box = textarea ? (textarea.closest('div[class*="chat-input"]') || textarea.parentElement.parentElement.parentElement) : document.body;
                        const closeBtns = Array.from(box.querySelectorAll('div[class*="animated-size"] div[tabindex="0"], .ds-animated-size-item div[tabindex="0"], div[role="button"], button'));
                        closeBtns.forEach(btn => {
                            if (btn.querySelector('svg') || (btn.getAttribute('aria-label') || '').includes('close') || (btn.getAttribute('aria-label') || '').includes('remove')) {
                                btn.click();
                            }
                        });
                        // Force remove lingering broken badge elements
                        const badges = Array.from(box.querySelectorAll('.ds-animated-size-item, div[class*="animated-size"]'));
                        badges.forEach(b => {
                            if ((b.innerText || '').toLowerCase().includes('server busy') || (b.innerText || '').toLowerCase().includes('failed')) {
                                b.remove();
                            }
                        });
                    }""")
                    time.sleep(0.5)

                if not badge_status.get("exists") or badge_status.get("error"):
                    file_input = page.query_selector("input[type='file']")
                    if file_input:
                        console.print(f"[cyan]📎 Attaching file to DeepSeek: {fname}...[/cyan]")
                        page.set_input_files("input[type='file']", str(Path(file_to_attach).resolve()))
                        
                        # Wait for upload progress to finish (wait until 'Uploading' is gone and badge is present without errors)
                        console.print("[cyan]⏳ Verifying file upload on DeepSeek...[/cyan]")
                        for _ in range(16):
                            time.sleep(0.5)
                            upload_state = page.evaluate("""(name) => {
                                const textarea = document.querySelector('textarea');
                                const box = textarea ? (textarea.closest('div[class*="chat-input"]') || textarea.parentElement.parentElement.parentElement) : document.body;
                                const text = box ? (box.innerText || box.textContent || '') : '';
                                const isBusy = text.includes('Uploading') || text.includes('上传中');
                                const hasBadge = text.includes(name);
                                const hasError = text.toLowerCase().includes('server busy') || text.toLowerCase().includes('failed') || text.toLowerCase().includes('error') || text.includes('失败') || text.includes('繁忙');
                                return { busy: isBusy, ready: hasBadge, error: hasError };
                            }""", fname)

                            if upload_state.get("error"):
                                console.print("[yellow]⚠️ DeepSeek attachment server returned 'Server busy'. Purging broken badge and switching to inline bundle fallback...[/yellow]")
                                page.evaluate("""() => {
                                    const textarea = document.querySelector('textarea');
                                    const box = textarea ? (textarea.closest('div[class*="chat-input"]') || textarea.parentElement.parentElement.parentElement) : document.body;
                                    const badges = Array.from(box.querySelectorAll('.ds-animated-size-item, div[class*="animated-size"]'));
                                    badges.forEach(b => b.remove());
                                }""")
                                break

                            if not upload_state.get("busy") and upload_state.get("ready") and not upload_state.get("error"):
                                attachment_succeeded = True
                                break

                        if attachment_succeeded:
                            console.print("[green]✓ File upload complete and verified in input![/green]")
                            time.sleep(0.5)

                    # Check if an OS dialog was opened and feed it
                    self._feed_or_dismiss_os_file_dialog(str(file_to_attach))
                else:
                    attachment_succeeded = True
                    console.print(f"[cyan]📎 File {fname} already attached in input box, proceeding...[/cyan]")
            except Exception as fe:
                console.print(f"[yellow]Note: Attachment handled ({fe}), falling back to inline prompt context.[/yellow]")
                self._feed_or_dismiss_os_file_dialog(str(file_to_attach))

        # Fallback: If file upload was not successful or server was busy, inject file content inline into prompt
        if file_to_attach and Path(file_to_attach).exists() and not attachment_succeeded:
            try:
                bundle_text = Path(file_to_attach).read_text(encoding="utf-8", errors="ignore")
                console.print(f"[cyan]📦 Injecting bundle ({len(bundle_text)} chars) directly into prompt text...[/cyan]")
                prompt = f"PROJECT CONTEXT FILES ({Path(file_to_attach).name}):\n```text\n{bundle_text}\n```\n\n{prompt}"
            except Exception as read_err:
                console.print(f"[yellow]Could not read bundle for inline fallback: {read_err}[/yellow]")

        if not file_to_attach:
            # If no file is to be attached, remove any leftover attachment badges from previous prompt
            try:
                page.evaluate("""() => {
                    const textarea = document.querySelector('textarea');
                    const box = textarea ? textarea.parentElement.parentElement.parentElement : null;
                    if (!box) return;
                    const closeBtns = Array.from(box.querySelectorAll('div[class*="animated-size"] div[tabindex="0"], .ds-animated-size-item div[tabindex="0"]'));
                    closeBtns.forEach(btn => {
                        if (btn.querySelector('svg')) btn.click();
                    });
                }""")
            except Exception:
                pass

        # Find textarea
        input_el = None
        try:
            input_el = page.wait_for_selector("textarea", timeout=8000)
        except Exception:
            pass

        if not input_el:
            raise RuntimeError("Could not locate DeepSeek chat input box. Please ensure chat.deepseek.com is loaded.")

        console.print("[cyan]Sending prompt to DeepSeek Web...[/cyan]")
        input_el.click()
        time.sleep(0.2)
        
        # Record initial assistant message count so we only capture NEW responses
        initial_msg_count = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('.ds-markdown, .ds-message .ds-markdown')).filter(el => {
                return !el.parentElement.closest('.ds-markdown');
            });
            return els.length;
        }""")

        # Clear any leftover input
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.2)

        # Insert prompt using keyboard events so React state properly updates
        page.keyboard.insert_text(prompt)
        time.sleep(0.8)

        # Dismiss any accidental OS/browser dialogs before proceeding
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass

        # Click send button (strictly excluding file attachment/paperclip button)
        sent = False
        for attempt in range(8):
            sent = page.evaluate("""() => {
                const textarea = document.querySelector('textarea');
                const container = textarea ? (textarea.closest('div[class*="chat-input"]') || textarea.parentElement.parentElement.parentElement) : document.body;
                
                // 1. Gather candidate buttons
                const candidates = Array.from(container.querySelectorAll('div[role="button"], button, div.ds-icon-button, div[class*="button"], div[class*="send"]'));
                
                for (const btn of candidates) {
                    const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const cls = (btn.className || '').toString().toLowerCase();
                    const inner = (btn.innerText || '').toLowerCase();
                    const style = window.getComputedStyle(btn);
                    const bg = style.backgroundColor || '';
                    
                    // Exclude paperclip / attachment / DeepThink / Search
                    if (aria.includes('attach') || aria.includes('file') || aria.includes('upload') || 
                        inner.includes('deepthink') || inner.includes('search') ||
                        btn.querySelector('input[type="file"]') || btn.closest('input[type="file"]')) {
                        continue;
                    }

                    const isSendAria = aria.includes('send') || aria.includes('发送');
                    const isBluePrimary = bg.includes('77, 107, 254') || bg.includes('43, 90, 237') || bg.includes('29, 78, 216') || bg.includes('rgb(0, 122, 255)');
                    const isCirclePrimary = (cls.includes('primary') || cls.includes('circle')) && btn.querySelector('svg');
                    const isDisabled = cls.includes('disabled') || btn.getAttribute('disabled') !== null || btn.getAttribute('aria-disabled') === 'true';
                    
                    if ((isSendAria || isBluePrimary || isCirclePrimary) && !isDisabled) {
                        btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
                        btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
                        btn.click();
                        return true;
                    }
                }
                
                // 2. Specific querySelector fallback for DeepSeek send button
                const directSend = container.querySelector('div.ds-button--circle, div[role="button"].ds-button--primary, div[aria-label*="Send"]');
                if (directSend && !directSend.className.includes('disabled')) {
                    directSend.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
                    directSend.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
                    directSend.click();
                    return true;
                }
                
                return false;
            }""")
            if sent:
                break
            time.sleep(0.4)

        # Keyboard submit fallbacks if button was not clicked
        try:
            input_el.focus()
            page.keyboard.press("Enter")
            time.sleep(0.3)
            page.keyboard.press("Control+Enter")
        except Exception:
            pass

        console.print("[magenta]Waiting for DeepSeek response...[/magenta]")
        time.sleep(3)

        # Wait for generation to complete
        max_wait = 180
        start_t = time.time()
        prev_text = ""
        stable_count = 0
        continue_click_count = 0
        max_continue_clicks = 12
        retry_click_count = 0
        max_retry_clicks = 3

        while time.time() - start_t < max_wait:
            time.sleep(1.5)

            try:
                # 1. Multi-strategy AUTO-CLICK for 'Retry' / 'Regenerate' / 'Try again' / '重新生成' / '重试'
                # Strictly ignore code blocks, syntax highlight tokens, and input boxes
                clicked_retry = False
                if retry_click_count < max_retry_clicks:
                    # Method A: Playwright Role / Text Locators
                    try:
                        retry_loc = page.locator("button, div[role='button'], .ds-button").filter(has_text=re.compile(r"^\s*(Retry|Regenerate|Try again|重新生成|重试)\s*$", re.I)).last
                        if retry_loc.count() > 0 and retry_loc.is_visible():
                            is_in_code = retry_loc.evaluate("el => !!el.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')")
                            if not is_in_code:
                                retry_loc.scroll_into_view_if_needed()
                                retry_loc.click(force=True)
                                clicked_retry = True
                    except Exception:
                        pass

                    # Method B: Full DOM Candidate Dispatch
                    if not clicked_retry:
                        clicked_retry = page.evaluate("""() => {
                            function isVisible(el) {
                                if (!el) return false;
                                const rect = el.getBoundingClientRect();
                                if (rect.width === 0 || rect.height === 0) return false;
                                const style = window.getComputedStyle(el);
                                return style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity || '1') > 0;
                            }
                            const candidates = Array.from(document.querySelectorAll('button, div[role="button"], .ds-button, div[class*="button"], div[tabindex]'));
                            const btn = candidates.find(el => {
                                if (el.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')) return false;
                                const t = (el.innerText || el.textContent || '').trim().toLowerCase();
                                const aria = (el.getAttribute('aria-label') || '').trim().toLowerCase();
                                const title = (el.getAttribute('title') || '').trim().toLowerCase();
                                const matches = t === 'retry' || t === 'regenerate' || t === 'try again' ||
                                                aria === 'retry' || aria === 'regenerate' || title === 'retry' ||
                                                t === '重试' || t === '重新生成';
                                return matches && isVisible(el);
                            });
                            if (btn) {
                                btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                                ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evtName => {
                                    btn.dispatchEvent(new MouseEvent(evtName, { bubbles: true, cancelable: true, view: window }));
                                });
                                return true;
                            }
                            return false;
                        }""")

                if clicked_retry:
                    retry_click_count += 1
                    console.print("[bold yellow]⚡ Detected 'Retry' / 'Regenerate' button: Auto-clicked by OmniDev![/bold yellow]")
                    stable_count = 0
                    time.sleep(3.0)
                    continue

                # 2. Multi-strategy AUTO-CLICK for 'Continue' / 'Continue generating' / '继续生成'
                clicked_continue = False
                if continue_click_count < max_continue_clicks:
                    try:
                        # Strategy A: Playwright locator with exact text filter and bounding box click
                        for loc_pat in [r"Continue", r"继续", r"Resume"]:
                            c_locs = page.locator("button, div[role='button'], .ds-button, [class*='button'], [class*='btn']").filter(has_text=re.compile(loc_pat, re.I))
                            if c_locs.count() > 0:
                                last_loc = c_locs.last
                                if last_loc.is_visible():
                                    is_in_code = last_loc.evaluate("el => !!el.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')")
                                    if not is_in_code:
                                        last_loc.scroll_into_view_if_needed()
                                        box = last_loc.bounding_box()
                                        if box and box["width"] < 550 and box["height"] < 120:
                                            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                                            time.sleep(0.05)
                                            page.mouse.down()
                                            time.sleep(0.05)
                                            page.mouse.up()
                                            try:
                                                last_loc.click(force=True, timeout=1000)
                                            except Exception:
                                                pass
                                            clicked_continue = True
                                            break
                    except Exception:
                        pass

                    # Strategy B: Pinpoint smallest area leaf DOM button search with clientX/clientY event dispatch
                    if not clicked_continue:
                        try:
                            btn_box = page.evaluate("""() => {
                                function isVisible(el) {
                                    if (!el) return false;
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width === 0 || rect.height === 0) return false;
                                    const style = window.getComputedStyle(el);
                                    return style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity || '1') > 0;
                                }

                                const candidates = Array.from(document.querySelectorAll('button, div[role="button"], .ds-button, [class*="button"], [class*="btn"], span, div')).filter(el => {
                                    if (el.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')) return false;
                                    const t = (el.innerText || el.textContent || '').trim().toLowerCase();
                                    const aria = (el.getAttribute('aria-label') || '').trim().toLowerCase();
                                    const isMatch = (t.includes('continue') || 
                                                     t.includes('继续') || 
                                                     aria.includes('continue') ||
                                                     t.includes('resume'));
                                    if (!isMatch || !isVisible(el)) return false;
                                    const rect = el.getBoundingClientRect();
                                    return rect.width > 5 && rect.width < 550 && rect.height > 5 && rect.height < 120;
                                });

                                if (candidates.length === 0) return null;
                                
                                // Sort by smallest bounding box area to get the exact innermost pill button
                                candidates.sort((a, b) => {
                                    const ra = a.getBoundingClientRect();
                                    const rb = b.getBoundingClientRect();
                                    return (ra.width * ra.height) - (rb.width * rb.height);
                                });

                                const target = candidates[0];
                                target.scrollIntoView({ behavior: 'instant', block: 'center' });
                                const rect = target.getBoundingClientRect();
                                
                                ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                                    target.dispatchEvent(new MouseEvent(evt, {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window,
                                        clientX: rect.x + rect.width / 2,
                                        clientY: rect.y + rect.height / 2
                                    }));
                                });
                                if (typeof target.click === 'function') target.click();

                                return {
                                    x: rect.x + rect.width / 2,
                                    y: rect.y + rect.height / 2,
                                    width: rect.width,
                                    height: rect.height
                                };
                            }""")

                            if btn_box and btn_box.get("width", 0) > 0:
                                page.mouse.move(btn_box["x"], btn_box["y"])
                                time.sleep(0.05)
                                page.mouse.down()
                                time.sleep(0.05)
                                page.mouse.up()
                                clicked_continue = True
                        except Exception:
                            pass

                if clicked_continue:
                    continue_click_count += 1
                    console.print(f"[bold cyan]⚡ Long code detected: Auto-clicked 'Continue' on DeepSeek ({continue_click_count}/{max_continue_clicks})![/bold cyan]")
                    stable_count = 0
                    time.sleep(3.5)
                    continue

                # 3. Check if streaming stop button is present (exclude code blocks)
                is_streaming = page.evaluate("""() => {
                    function isVisible(el) {
                        if (!el) return false;
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return false;
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }
                    const btns = Array.from(document.querySelectorAll('div[role="button"], button'));
                    return btns.some(b => {
                        if (b.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')) return false;
                        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                        const text = (b.innerText || b.textContent || '').toLowerCase().trim();
                        return (aria.includes('stop') || text === 'stop' || text === '停止' || text === 'stop generating') && isVisible(b);
                    });
                }""")

                if is_streaming:
                    stable_count = 0
                    time.sleep(1.2)
                    continue

                # 4. Check if Continue button is still rendering or visible anywhere
                has_pending_continue = page.evaluate("""() => {
                    function isVisible(el) {
                        if (!el) return false;
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return false;
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity || '1') > 0;
                    }
                    const all = Array.from(document.querySelectorAll('button, div[role="button"], .ds-button, [class*="button"], [class*="btn"], span, div'));
                    return all.some(el => {
                        if (el.closest('pre, code, textarea, input, .code-block, .ds-markdown pre')) return false;
                        const t = (el.innerText || el.textContent || '').trim().toLowerCase();
                        const aria = (el.getAttribute('aria-label') || '').trim().toLowerCase();
                        const isMatch = (t.includes('continue') || t.includes('继续') || aria.includes('continue') || t.includes('resume'));
                        if (!isMatch || !isVisible(el)) return false;
                        const rect = el.getBoundingClientRect();
                        return rect.width > 5 && rect.width < 550 && rect.height > 5 && rect.height < 120;
                    });
                }""")

                if has_pending_continue and continue_click_count < max_continue_clicks:
                    stable_count = 0
                    time.sleep(1.0)
                    continue

                # 5. Find latest assistant markdown message
                current_text = page.evaluate("""() => {
                    const els = Array.from(document.querySelectorAll('.ds-markdown, .ds-message .ds-markdown')).filter(el => {
                        return !el.parentElement.closest('.ds-markdown');
                    });
                    if (els.length === 0) return null;
                    const lastEl = els[els.length - 1];

                    // Live pre elements for pristine innerText with newlines
                    const livePres = Array.from(lastEl.querySelectorAll('pre'));

                    const clone = lastEl.cloneNode(true);
                    
                    // Remove all copy buttons, download buttons, and noise headers
                    const noise = Array.from(clone.querySelectorAll('button, .ds-button, [class*="header"], [class*="copy"], [class*="download"]'));
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
                        
                        // Clean noise prefixes and zero-width characters
                        codeText = codeText.replace(/^(?:Copy|Download|gdscript|gdscene|python|html|json|text|bash|sh)\\s*\\n/i, "");
                        codeText = codeText.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');

                        const trimmed = codeText.trim();
                        let lang = 'gdscript';
                        if (trimmed.startsWith('<!DOCTYPE html') || trimmed.startsWith('<html') || trimmed.includes('</html>')) {
                            lang = 'html';
                        } else if (trimmed.startsWith('[gd_scene') || trimmed.startsWith('[ext_resource') || trimmed.startsWith('[sub_resource')) {
                            lang = 'gdscene';
                        } else if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
                            try { JSON.parse(trimmed); lang = 'json'; } catch(e) {}
                        } else if (trimmed.includes('import ') || trimmed.includes('def ') || trimmed.includes('class ')) {
                            lang = 'python';
                        }
                        
                        const replacement = document.createElement('div');
                        replacement.textContent = '\\n```' + lang + '\\n' + trimmed + '\\n```\\n';
                        pre.parentNode.replaceChild(replacement, pre);
                    });

                    // Ensure block elements have linebreaks
                    const blockEls = Array.from(clone.querySelectorAll('p, div, h1, h2, h3, h4, h5, h6, li, tr'));
                    blockEls.forEach(b => {
                        b.appendChild(document.createTextNode('\\n'));
                    });
                    
                    const result = clone.textContent || clone.innerText || "";
                    return result.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');
                }""")

                if current_text and current_text.strip() != prompt.strip() and len(current_text.strip()) > 20:
                    # 6. Check for Incomplete / Cut-off Code Sentinel
                    # If code blocks are unclosed or ends abruptly on a comma/parenthesis/operator, wait for Continue
                    is_code_truncated = False
                    raw_text = current_text.strip()
                    # Count code fence occurrences
                    fence_count = raw_text.count("```")
                    if fence_count % 2 != 0:
                        is_code_truncated = True
                    else:
                        last_line = raw_text.splitlines()[-1].strip() if raw_text.splitlines() else ""
                        if last_line.endswith(("(", ",", "+", "=", "->", ":", "\\", "[", "{")) or last_line.endswith("Input.set_mouse_mode"):
                            is_code_truncated = True

                    if is_code_truncated and continue_click_count < max_continue_clicks:
                        # Don't finish if code is visibly cut off; wait for DeepSeek's Continue button
                        stable_count = 0
                        time.sleep(1.5)
                        continue

                    if current_text == prev_text:
                        stable_count += 1
                        # When text is stable for 4 cycles (approx 6s) and no streaming / continue / truncation, return
                        if stable_count >= 4:
                            return current_text
                    else:
                        stable_count = 0
                        prev_text = current_text
            except Exception as loop_err:
                if any(k in str(loop_err) for k in ["destroyed", "closed", "Target page"]):
                    time.sleep(1.5)
                    continue

        return prev_text or "No response captured from DeepSeek."

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
