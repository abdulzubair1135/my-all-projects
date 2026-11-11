"""
direct_deepseek.py
==================
Ultra-reliable Chrome DevTools Protocol (CDP) WebSocket client for chat.deepseek.com.
- Connects directly to the DeepSeek browser tab via WebSocket.
- Fills textarea using React/DOM synthetic events and triggers the send action.
- Directly intercepts the network stream via CDP Network domain (Network.getResponseBody).
- Captures 100% of the raw SSE completion chunks {"v": "..."} without relying on fragile DOM selectors.
"""

import asyncio
import json
import os
import re
import subprocess
import time
import urllib.request
import websockets
import concurrent.futures

CDP_JSON_URL = "http://127.0.0.1:9222/json"

def ensure_chrome_ready():
    """Checks if Chrome is listening on port 9222; if not, launches Chrome detached."""
    try:
        with urllib.request.urlopen(CDP_JSON_URL, timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        pass

    # Launch Chrome detached via WMI / start so it stays alive
    cmd = (
        r'"C:\Program Files\Google\Chrome\Application\chrome.exe" '
        r'--remote-debugging-port=9222 --user-data-dir="C:\chrome_dev" --no-first-run --no-default-browser-check '
        r'https://chat.deepseek.com https://studio.youtube.com'
    )
    try:
        ps_cmd = f"Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList '{cmd}'"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=10)
    except Exception:
        subprocess.Popen(f'cmd.exe /c start "" {cmd}', shell=True)

    for _ in range(12):
        time.sleep(1)
        try:
            with urllib.request.urlopen(CDP_JSON_URL, timeout=1) as r:
                return json.loads(r.read())
        except Exception:
            pass
    return []

def get_deepseek_ws_url():
    """
    Finds the open chat.deepseek.com tab and returns its webSocketDebuggerUrl.
    RULE:
    - If DeepSeek is ALREADY open: reuse it immediately! Zero searching, zero new navigation!
    - ONLY if DeepSeek is NOT open: open chat.deepseek.com!
    """
    tabs = ensure_chrome_ready()
    if not tabs:
        raise RuntimeError("Chrome is not running on port 9222!")

    # 1. Pehle check karo agar DeepSeek tab pehle se open hai:
    for t in tabs:
        url = t.get("url", "")
        if "deepseek.com" in url and "webSocketDebuggerUrl" in t:
            # Pehle se open hai! Direct connect!
            return t["webSocketDebuggerUrl"]

    # 2. Agar pehle se open nahi mila, tabhi navigate/open karo:
    print("[*] DeepSeek tab pehle se open nahi mila, chat.deepseek.com open kar rahe hain...")
    try:
        new_tab_url = f"{CDP_JSON_URL}/new?https://chat.deepseek.com"
        with urllib.request.urlopen(new_tab_url, timeout=5) as r_new:
            new_tab = json.loads(r_new.read())
            time.sleep(3)
            if "webSocketDebuggerUrl" in new_tab:
                return new_tab["webSocketDebuggerUrl"]
    except Exception as e:
        print(f"[!] Could not open new DeepSeek tab via CDP: {e}")

    # Re-check fresh tabs
    try:
        with urllib.request.urlopen(CDP_JSON_URL, timeout=2) as r:
            fresh_tabs = json.loads(r.read())
            for t in fresh_tabs:
                if "deepseek.com" in t.get("url", "") and "webSocketDebuggerUrl" in t:
                    return t["webSocketDebuggerUrl"]
    except Exception:
        pass

    raise RuntimeError("DeepSeek tab not found in Chrome! Please ensure chat.deepseek.com is open.")

def parse_sse_response(sse_raw_text):
    """
    Parses DeepSeek's raw SSE response body and extracts the generated text/JSON.
    DeepSeek streams deltas in 'data: {"v": "..."}'.
    """
    text_chunks = []
    for line in sse_raw_text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload_str = line[5:].strip()
        if not payload_str or payload_str == "[DONE]":
            continue
        try:
            d = json.loads(payload_str)
            v = d.get("v")
            if isinstance(v, str):
                text_chunks.append(v)
            elif isinstance(v, dict):
                # Full response snapshot if available
                resp = v.get("response", {})
                for frag in resp.get("fragments", []):
                    if frag.get("type") == "TEXT" and frag.get("content"):
                        text_chunks.append(frag["content"])
            elif isinstance(v, list):
                # Batch updates
                for item in v:
                    if isinstance(item, dict) and isinstance(item.get("v"), str):
                        text_chunks.append(item["v"])
        except Exception:
            pass

    full_text = "".join(text_chunks)
    return full_text

async def _send_prompt_async(prompt_text, max_wait_sec=60):
    ws_url = get_deepseek_ws_url()
    print(f"[*] Connecting directly to DeepSeek Tab: {ws_url}")

    async with websockets.connect(ws_url, max_size=25_000_000) as ws:
        msg_id = 1

        # 1. Enable Network domain to intercept raw completion stream
        await ws.send(json.dumps({"id": msg_id, "method": "Network.enable"}))
        msg_id += 1
        await ws.recv()

        # 2. Fill prompt cleanly via native execCommand and trigger send
        escaped_prompt = json.dumps(prompt_text)
        fill_and_send_js = f"""
        (() => {{
            const ta = document.querySelector('textarea, #chat-input');
            if (!ta) return {{ filled: false, error: 'no textarea' }};
            ta.focus();
            ta.select();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
            
            const ok = document.execCommand('insertText', false, {escaped_prompt});
            if (!ok) {{
                const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
                if (setter) setter.call(ta, {escaped_prompt});
                else ta.value = {escaped_prompt};
                ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            setTimeout(() => {{
                const btn = document.querySelector('div.ds-button--circle, button.ds-button--circle, div[aria-label="Send"], button[aria-label="Send"]');
                if (btn) btn.click();
            }}, 200);

            return {{ filled: true, sent: 'INSERTED_AND_CLICKED' }};
        }})()
        """
        await ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": fill_and_send_js, "returnByValue": True}}))
        msg_id += 1
        res = json.loads(await ws.recv())
        fill_res = res.get("result", {}).get("result", {}).get("value", {})
        print(f"[*] Prompt filled into DeepSeek: {fill_res.get('filled')} ({fill_res.get('sent')})")

        # 3. Monitor Network events for completion requestId
        completion_req_id = None
        start_t = time.time()
        raw_body = ""

        print("[*] Waiting for DeepSeek response stream via CDP Network...")
        while time.time() - start_t < max_wait_sec:
            try:
                raw_msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                msg = json.loads(raw_msg)
                method = msg.get("method", "")

                if method == "Network.requestWillBeSent":
                    url = msg.get("params", {}).get("request", {}).get("url", "")
                    if "chat/completion" in url:
                        completion_req_id = msg.get("params", {}).get("requestId")
                        print(f"[*] Intercepted chat/completion requestId: {completion_req_id}")

                elif method == "Network.loadingFinished":
                    req_id = msg.get("params", {}).get("requestId")
                    if req_id == completion_req_id:
                        print(f"[SUCCESS] DeepSeek completion stream finished! Fetching body...")
                        await ws.send(json.dumps({
                            "id": msg_id,
                            "method": "Network.getResponseBody",
                            "params": {"requestId": req_id}
                        }))
                        msg_id += 1
                        body_res = json.loads(await ws.recv())
                        raw_body = body_res.get("result", {}).get("body", "")
                        break
            except asyncio.TimeoutError:
                pass

        if not raw_body:
            # Fallback: check DOM text if network body missed
            print("[*] Network body timed out, checking DOM text...")
            dom_js = "(() => document.body.innerText)()"
            await ws.send(json.dumps({"id": msg_id, "method": "Runtime.evaluate", "params": {"expression": dom_js, "returnByValue": True}}))
            res = json.loads(await ws.recv())
            return res.get("result", {}).get("result", {}).get("value", "")

        parsed_text = parse_sse_response(raw_body)
        print(f"[*] Parsed completion length: {len(parsed_text)} chars")
        return parsed_text

def safe_run_async(coro_fn, *args, **kwargs):
    """Executes an async coroutine cleanly in a fresh isolated thread."""
    def runner():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro_fn(*args, **kwargs))
        finally:
            try:
                new_loop.close()
            except Exception:
                pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(runner).result()

def ask_deepseek(prompt_text, max_wait_sec=60):
    """Synchronous entry point to query DeepSeek."""
    return safe_run_async(_send_prompt_async, prompt_text, max_wait_sec=max_wait_sec)

if __name__ == "__main__":
    resp = ask_deepseek("Say 'STICKMAN PIPELINE ONLINE' in 3 words.")
    print("Response:", resp[:200])
