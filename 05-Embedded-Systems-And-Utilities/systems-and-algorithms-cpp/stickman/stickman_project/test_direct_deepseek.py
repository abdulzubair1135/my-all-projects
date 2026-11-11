import asyncio
import json
import re
import urllib.request
import websockets

def get_deepseek_ws_url():
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
        tabs = json.loads(r.read())
    for t in tabs:
        if "chat.deepseek.com" in t.get("url", ""):
            return t["webSocketDebuggerUrl"]
    return None

async def generate_script_direct_cdp(topic):
    ws_url = get_deepseek_ws_url()
    if not ws_url:
        print("[!] No DeepSeek tab open on port 9222!")
        return None

    print(f"[*] Connected to DeepSeek CDP via direct WebSocket!")
    
    prompt = f"""You are the Master Director of viral 2D Stickman POV Shorts.
Topic: '{topic}'

Analyze the topic and choose the best matching characters, theme, props, emotions, and visual gags!
Available Director Options:
1. duo_type: "boy_and_boy2" | "mummy_and_boy" | "boss_and_employee" | "boy_and_girl" | "dad_and_boy"
2. theme: "home_mummy" | "bedroom_morning" | "office_desk" | "street_food" | "exam_hall"
3. speaker per scene: "boy", "boy2", "girl", "mummy", "boss", "dad"
4. shot_type per scene: "boy_close", "girl_close", "mummy_close", "boss_close", "dad_close", "two_shot"
5. prop per scene: "phone", "chai_cup", "samosa", "newspaper", "pillow", "laptop", "none"
6. action per scene: "walk_in", "chappal_impact", "whistle_shock", "none"
7. pose per scene: "talk_gesture", "hands_on_hips", "shock", "pleading", "shrug"
8. emotion per scene: "none", "shock", "sweat", "angry"

Write a hilarious, fast-paced 4-scene dialogue banter tailored specifically to this topic.
Format your reply strictly as a single JSON object with this exact structure:
{{
  "title": "Viral Clicky Hindi Title with 1 emoji #shorts #viral",
  "hook": "POV: Relatable Hook in Hinglish",
  "duo_type": "boy_and_boy2",
  "theme": "bedroom_morning",
  "description": "Short funny description with tags #shorts #comedy #doodle #animation",
  "tags": ["shorts", "comedy", "funny", "relatable", "stickman", "doodle"],
  "scenes": [
    {{
      "scene": 1,
      "speaker": "boy",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी देवनागरी में जो आवाज़ बोलेगी (Natural, punchy spoken Hindi)",
      "dialogue": "Exact dialogue in clean Hinglish for subtitles",
      "pose": "talk_gesture",
      "prop": "phone",
      "action": "walk_in",
      "emotion": "none",
      "is_punchline": false
    }},
    {{
      "scene": 2,
      "speaker": "boy2",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी में दूसरा कैरेक्टर बोलेगा",
      "dialogue": "Exact dialogue in clean Hinglish",
      "pose": "hands_on_hips",
      "prop": "phone",
      "action": "none",
      "emotion": "none",
      "is_punchline": false
    }},
    {{
      "scene": 3,
      "speaker": "boy",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी में रिएक्शन/शॉक",
      "dialogue": "Reaction in Hinglish",
      "pose": "shock",
      "prop": "none",
      "action": "whistle_shock",
      "emotion": "shock",
      "is_punchline": false
    }},
    {{
      "scene": 4,
      "speaker": "boy2",
      "shot_type": "two_shot",
      "spoken_hindi": "शुद्ध हिंदी में फाइनल फनी पंचलाइन",
      "dialogue": "Punchline dialogue in Hinglish",
      "pose": "pleading",
      "prop": "none",
      "action": "none",
      "emotion": "none",
      "is_punchline": true
    }}
  ]
}}
Strictly return valid JSON only."""

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
        print("[*] Prompt sent to DeepSeek! Waiting for response...")
        
        last_body = ""
        stable_count = 0
        for i in range(45):
            await asyncio.sleep(1.5)
            await ws.send(json.dumps({"id": 10 + i, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerText", "returnByValue": True}}))
            res = json.loads(await ws.recv())
            body_text = res.get("result", {}).get("result", {}).get("value", "")
            
            if "{" in body_text and "scenes" in body_text:
                if len(body_text) == len(last_body):
                    stable_count += 1
                    if stable_count >= 2:
                        print(f"[*] Response finished in {i * 1.5:.1f}s!")
                        break
                else:
                    stable_count = 0
            last_body = body_text

        # Extract JSON block
        match = re.search(r'\{[\s\S]*"title"[\s\S]*"scenes"[\s\S]*\}', last_body)
        if match:
            raw_json = match.group(0)
            # Find matching balanced braces
            brace_count = 0
            end_idx = -1
            for idx, ch in enumerate(raw_json):
                if ch == '{':
                    brace_count += 1
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = idx + 1
                        break
            if end_idx != -1:
                clean_json_str = raw_json[:end_idx]
                try:
                    data = json.loads(clean_json_str)
                    print(f"[SUCCESS] Parsed script: '{data.get('title')}'")
                    return data
                except Exception as je:
                    print("[!] JSON load error:", je)
                    
    return None

if __name__ == "__main__":
    t = "College attendance: I will go tomorrow every single day"
    res = asyncio.run(generate_script_direct_cdp(t))
    if res:
        print("TITLE:", res.get("title"))
        print("SCENES:", len(res.get("scenes", [])))
        with open("live_deepseek_script.json", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
