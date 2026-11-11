import asyncio
import json
import re
import urllib.request
import websockets

def get_deepseek_ws():
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
        tabs = json.loads(r.read())
    for t in tabs:
        if "chat.deepseek.com" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    return None

async def ask_deepseek_for_code(prompt):
    ws_url = get_deepseek_ws()
    if not ws_url:
        print("[!] No DeepSeek tab!")
        return None

    async with websockets.connect(ws_url) as ws:
        escaped_prompt = json.dumps(prompt)
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
            
            setTimeout(() => {{
                const sendBtn = document.querySelector('div.ds-button--circle, button.ds-button--circle, div[aria-label="Send"], button[aria-label="Send"]');
                if (sendBtn) sendBtn.click();
            }}, 300);
            return true;
        }})()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": fill_js, "returnByValue": True}}))
        await ws.recv()
        print("[*] Prompt sent to DeepSeek. Waiting for code response...")
        
        last_body = ""
        stable_count = 0
        for i in range(40):
            await asyncio.sleep(1.5)
            await ws.send(json.dumps({"id": 10 + i, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerText", "returnByValue": True}}))
            res = json.loads(await ws.recv())
            body_text = res.get("result", {}).get("result", {}).get("value", "")
            
            if "def " in body_text:
                if len(body_text) == len(last_body):
                    stable_count += 1
                    if stable_count >= 2:
                        break
                else:
                    stable_count = 0
            last_body = body_text

        return last_body

if __name__ == "__main__":
    prompt = """Write a Python function using PIL ImageDraw to draw an expressive, funny 2D cartoon scene.
Function signature:
def draw_scene(draw, t, duration, w, h):
    # w=720, h=1280. t goes from 0.0 to duration.
    # Draw:
    # 1. Background: bedroom with window, alarm clock vibrating
    # 2. Stickman character: sleeping under blanket or waking up with funny expressions and moving limbs based on math.sin(t * 10)
    # 3. Clean ink doodle aesthetic

Output Python code block only."""
    code_resp = asyncio.run(ask_deepseek_for_code(prompt))
    print("[*] DeepSeek Code Response Received:")
    print(code_resp[-1500:])
    with open("scratch/deepseek_raw_code_resp.txt", "w", encoding="utf-8") as f:
        f.write(code_resp)
