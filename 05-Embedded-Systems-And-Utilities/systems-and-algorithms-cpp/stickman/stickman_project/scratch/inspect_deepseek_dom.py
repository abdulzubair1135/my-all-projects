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
            const ta = document.querySelector('textarea, #chat-input, div[contenteditable="true"]');
            const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
            const sendBtn = btns.filter(b => {
                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                const cls = (b.className || '').toLowerCase();
                return aria.includes('send') || cls.includes('send') || cls.includes('circle');
            });
            return {
                textarea_found: !!ta,
                textarea_value_len: ta ? (ta.value || ta.innerText || '').length : 0,
                send_buttons_found: sendBtn.map(b => ({
                    tag: b.tagName,
                    cls: b.className,
                    aria: b.getAttribute('aria-label'),
                    disabled: b.disabled || b.getAttribute('aria-disabled')
                }))
            };
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        print("DOM State:", json.dumps(val, indent=2))

asyncio.run(check())
