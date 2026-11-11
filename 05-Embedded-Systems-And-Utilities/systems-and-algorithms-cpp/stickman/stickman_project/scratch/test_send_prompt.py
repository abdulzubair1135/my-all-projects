import asyncio
import json
import re
import time
import urllib.request
import websockets

async def send_prompt_to_deepseek(prompt_text):
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
        tabs = json.loads(r.read())
        
    ds_tab = None
    for t in tabs:
        if "chat.deepseek.com" in t.get("url", ""):
            ds_tab = t
            break
            
    if not ds_tab:
        raise RuntimeError("DeepSeek tab not found in Chrome!")
        
    ws_url = ds_tab["webSocketDebuggerUrl"]
    print(f"[*] Connecting to DeepSeek WebSocket: {ws_url}")
    
    async with websockets.connect(ws_url) as ws:
        # Step 1: Input text into textarea
        escaped_prompt = json.dumps(prompt_text)
        fill_js = f"""
        (() => {{
            const ta = document.querySelector('textarea, div[contenteditable="true"]');
            if (!ta) return false;
            ta.focus();
            const proto = Object.getPrototypeOf(ta);
            const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
            setter.call(ta, {escaped_prompt});
            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }})()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": fill_js, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        filled = res.get("result", {}).get("result", {}).get("value")
        print(f"[*] Textarea filled: {filled}")
        
        await asyncio.sleep(0.5)
        
        # Step 2: Click the circular send button
        click_js = """
        (() => {
            const sendBtn = document.querySelector('div.ds-button--circle, button.ds-button--circle, div[aria-label="Send"], button[aria-label="Send"]');
            if (sendBtn) {
                sendBtn.click();
                return 'CLICKED_CIRCLE';
            }
            const ta = document.querySelector('textarea');
            if (ta) {
                ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                return 'ENTER_DISPATCHED';
            }
            return 'NOT_FOUND';
        })()
        """
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": click_js, "returnByValue": True}}))
        click_res = json.loads(await ws.recv())
        print(f"[*] Send button triggered: {click_res.get('result', {}).get('result', {}).get('value')}")
        
        # Step 3: Wait for generation to finish
        print("[*] Waiting for DeepSeek response to stream...")
        last_len = 0
        stable_count = 0
        final_text = ""
        
        for i in range(50):
            await asyncio.sleep(1.5)
            check_js = """
            (() => {
                const stopBtn = document.querySelector('div[aria-label="Stop"], button:has-text("Stop"), .ds-button--stop');
                const msgs = Array.from(document.querySelectorAll('.ds-markdown, .markdown, .ds-message-bubble'));
                const latest = msgs.length > 0 ? msgs[msgs.length - 1].innerText : '';
                return {
                    generating: !!stopBtn,
                    text: latest
                };
            })()
            """
            await ws.send(json.dumps({"id": 10 + i, "method": "Runtime.evaluate", "params": {"expression": check_js, "returnByValue": True}}))
            status_res = json.loads(await ws.recv())
            val = status_res.get("result", {}).get("result", {}).get("value", {})
            cur_text = val.get("text", "")
            is_gen = val.get("generating", False)
            
            print(f"[{i+1}s] Text length: {len(cur_text)} | Generating: {is_gen}")
            
            if len(cur_text) > 100:
                if len(cur_text) == last_len:
                    stable_count += 1
                    if stable_count >= 3:
                        final_text = cur_text
                        break
                else:
                    stable_count = 0
            last_len = len(cur_text)
            
        print("[*] Completed response snippet:")
        print(final_text[:400])
        return final_text

if __name__ == "__main__":
    test_topic = "College attendance: I will go tomorrow"
    prompt = f"Give me a 4-scene funny dialogue banter for 2D stickman animation on: '{test_topic}'. Strictly return valid JSON only."
    asyncio.run(send_prompt_to_deepseek(prompt))
