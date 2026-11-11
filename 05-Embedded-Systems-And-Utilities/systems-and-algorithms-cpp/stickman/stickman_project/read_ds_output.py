import asyncio
import json
import urllib.request
import websockets
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

async def read_msg():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        tabs = json.loads(r.read())
    ws_url = [t['webSocketDebuggerUrl'] for t in tabs if 'chat.deepseek.com' in t.get('url', '')][0]
    async with websockets.connect(ws_url) as ws:
        js = """(() => {
            const msgs = document.querySelectorAll('.ds-assistant-message-main-content');
            const last = msgs.length > 0 ? msgs[msgs.length - 1].innerText : '';
            const stop = !!document.querySelector('.ds-button--stop, button[aria-label="Stop"]');
            return { len: last.length, text: last, is_streaming: stop };
        })()"""
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print(f"Streaming: {val.get('is_streaming')} | Length: {val.get('len')} chars")
        with open('scratch/deepseek_money_code.py', 'w', encoding='utf-8') as f:
            f.write(val.get('text', ''))
        print("Saved to scratch/deepseek_money_code.py!")

asyncio.run(read_msg())
