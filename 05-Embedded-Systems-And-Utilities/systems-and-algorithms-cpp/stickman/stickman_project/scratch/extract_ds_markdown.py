import asyncio
import json
import urllib.request
import websockets

async def check():
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
        tabs = json.loads(r.read())
    ds_tab = next(t for t in tabs if "chat.deepseek.com" in t.get("url", ""))
    async with websockets.connect(ds_tab["webSocketDebuggerUrl"]) as ws:
        js = """
        (() => {
            const mds = Array.from(document.querySelectorAll('.ds-markdown, .markdown, [class*="markdown"]'));
            return mds.map(m => m.innerText);
        })()
        """
        payload = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}
        await ws.send(json.dumps(payload))
        res = json.loads(await ws.recv())
        mds = res["result"]["result"]["value"]
        print(f"Total markdown blocks: {len(mds)}")
        for i, m in enumerate(mds):
            if "def draw_scene" in m:
                print(f"Block {i+1} matches!")
                with open("scratch/deepseek_extracted_code.py", "w", encoding="utf-8") as f:
                    f.write(m)
                print("Wrote block to scratch/deepseek_extracted_code.py!")
                break

if __name__ == "__main__":
    asyncio.run(check())
