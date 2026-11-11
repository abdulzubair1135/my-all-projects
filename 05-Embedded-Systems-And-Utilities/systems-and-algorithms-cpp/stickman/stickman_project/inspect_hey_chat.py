import asyncio
import json
import urllib.request
import websockets

def get_deepseek_ws():
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5) as r:
        tabs = json.loads(r.read())
    for t in tabs:
        if "chat.deepseek.com" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    return None

async def check():
    ws_url = get_deepseek_ws()
    async with websockets.connect(ws_url) as ws:
        js = """
        (() => {
            const msgs = Array.from(document.querySelectorAll('.ds-markdown, .markdown, [class*="markdown"]'));
            return msgs.map(m => ({
                className: m.className,
                text: m.innerText.slice(0, 200)
            }));
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        val = res.get("result", {}).get("result", {}).get("value")
        print(json.dumps(val, indent=2))

asyncio.run(check())
