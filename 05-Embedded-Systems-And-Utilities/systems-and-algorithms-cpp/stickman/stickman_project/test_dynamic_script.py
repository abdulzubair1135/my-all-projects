import direct_deepseek
import json
import re

def get_script_for_topic(topic):
    prompt = f'''
Write a 4-scene hilarious, relatable Hinglish comedy script between two 19-20 year old Indian college hostel boys for a 2D stickman YouTube Short (under 30s) on this topic:
Topic: '{topic}'

Strictly output raw JSON only with format:
{{
  "hook": "POV: ... 😭",
  "title": "POV: ... 😂 #shorts",
  "description": "...",
  "theme": "kitchen_fridge",
  "scenes": [
    {{"scene": 1, "speaker": "boy", "spoken_hindi": "...", "dialogue": "...", "sfx": ["whoosh"]}},
    {{"scene": 2, "speaker": "dost", "spoken_hindi": "...", "dialogue": "...", "sfx": ["pop"]}},
    {{"scene": 3, "speaker": "boy", "spoken_hindi": "...", "dialogue": "...", "sfx": ["record_scratch", "gasp"]}},
    {{"scene": 4, "speaker": "dost", "spoken_hindi": "...", "dialogue": "...", "sfx": ["boom", "laugh"]}}
  ]
}}
'''
    print(f"[*] Asking DeepSeek for custom script on: '{topic}'...")
    raw = direct_deepseek.ask_deepseek(prompt, max_wait_sec=40)
    match = re.search(r'\{[\s\S]*"hook"[\s\S]*"scenes"[\s\S]*\}', raw)
    if match:
        data = json.loads(match.group(0))
        return data
    return None

if __name__ == "__main__":
    t = "Late night hunger raids and blaming each other for the empty fridge"
    script = get_script_for_topic(t)
    print("Parsed Script:", json.dumps(script, indent=2, ensure_ascii=False) if script else "Failed")
