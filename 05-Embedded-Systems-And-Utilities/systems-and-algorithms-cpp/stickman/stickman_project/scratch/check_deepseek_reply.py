import os
import sys
sys.path.insert(0, os.getcwd())
import asyncio
import json
import websockets
import direct_deepseek

async def check():
    ws_url = direct_deepseek.get_deepseek_ws_url()
    async with websockets.connect(ws_url) as ws:
        js = """
        (() => {
            const msgs = Array.from(document.querySelectorAll('div.ds-markdown, div[class*="markdown"]'));
            return msgs.map(m => m.innerText.trim()).filter(Boolean).slice(-2);
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print("Latest DeepSeek Replies:", res.get('result', {}).get('result', {}).get('value'))

asyncio.run(check())
