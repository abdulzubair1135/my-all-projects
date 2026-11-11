import asyncio
import websockets
import json
import urllib.request

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
ds_tabs = [t for t in tabs if 'chat.deepseek.com' in t.get('url', '')]
print('DeepSeek tabs found:', len(ds_tabs))
if not ds_tabs:
    exit(1)

ws_url = ds_tabs[0]['webSocketDebuggerUrl']

async def test():
    async with websockets.connect(ws_url) as ws:
        js = "document.title + ' | ' + document.location.href"
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print('Page Title & URL:', res.get('result', {}).get('result', {}).get('value'))

        # Check body text
        js_body = "document.body.innerText.slice(0, 300)"
        await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': js_body, 'returnByValue': True}}))
        res2 = json.loads(await ws.recv())
        print('Body snippet:\n', res2.get('result', {}).get('result', {}).get('value'))

asyncio.run(test())
