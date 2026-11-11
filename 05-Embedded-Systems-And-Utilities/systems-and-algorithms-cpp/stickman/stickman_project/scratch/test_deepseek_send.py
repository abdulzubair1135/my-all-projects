import os
import sys
sys.path.insert(0, os.getcwd())
import asyncio
import json
import websockets
import direct_deepseek

async def test_send():
    ws_url = direct_deepseek.get_deepseek_ws_url()
    print("Connecting to:", ws_url)
    async with websockets.connect(ws_url) as ws:
        js = """
        (() => {
            const ta = document.querySelector('textarea, #chat-input');
            if (!ta) return 'no textarea';
            ta.focus();
            ta.select();
            document.execCommand('insertText', false, 'Hello DeepSeek! Reply with exactly the word OK.');
            
            setTimeout(() => {
                const btn = document.querySelector('div.ds-button--circle, div[class*="ds-button--circle"], div[aria-label="Send"]');
                if (btn) btn.click();
            }, 300);
            return 'dispatched';
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print("JS result:", res.get('result', {}).get('result', {}).get('value'))

asyncio.run(test_send())
