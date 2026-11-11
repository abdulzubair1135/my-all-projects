import asyncio
import json
import urllib.request
import websockets

async def check_send_button():
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
        tabs = json.loads(r.read())
    
    ds_tab = next(t for t in tabs if "chat.deepseek.com" in t.get("url", ""))
    ws_url = ds_tab["webSocketDebuggerUrl"]
    
    async with websockets.connect(ws_url) as ws:
        js = """
        (() => {
            const btns = Array.from(document.querySelectorAll('div[role="button"], button'));
            return btns.map(b => ({
                aria: b.getAttribute('aria-label'),
                className: String(b.className),
                text: b.innerText,
                tag: b.tagName
            }));
        })()
        """
        payload = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "returnByValue": True
            }
        }
        await ws.send(json.dumps(payload))
        res = json.loads(await ws.recv())
        buttons = res.get("result", {}).get("result", {}).get("value", [])
        for b in buttons:
            print("Button:", b)

if __name__ == "__main__":
    asyncio.run(check_send_button())
