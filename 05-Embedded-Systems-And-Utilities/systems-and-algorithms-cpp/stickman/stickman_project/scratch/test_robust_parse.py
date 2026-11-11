import re, json

with open('scratch/last_raw_ds.txt', encoding='utf-8') as f:
    text = f.read()

def parse_curiosity_json(raw_text):
    raw_text = re.sub(r'FINISHED.*$', '', raw_text).strip()
    raw_text = re.sub(r'```(?:json)?', '', raw_text).strip()
    
    # 1. Try standard JSON match
    m = re.search(r'\{[\s\S]*"scenes"[\s\S]*\}', raw_text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # 2. Check if "hook" exists
    hook_idx = raw_text.find('"hook"')
    if hook_idx != -1:
        # Check if there is an opening brace before hook
        pre = raw_text[:hook_idx].rstrip()
        if pre.endswith('{'):
            candidate = raw_text[len(pre)-1:]
        else:
            candidate = "{\n" + raw_text[hook_idx:]
        
        # Ensure it ends with '}'
        last_b = candidate.rfind('}')
        if last_b != -1:
            candidate = candidate[:last_b+1]
        else:
            candidate = candidate + "\n}"
        
        try:
            return json.loads(candidate)
        except Exception as e:
            print("Candidate parse error:", e)

    return None

data = parse_curiosity_json(text)
if data:
    print("[SUCCESS] Parsed with robust parser!")
    print("Hook:", data.get("hook"))
    print("Title:", data.get("title"))
    print("Image queries:", data.get("image_queries"))
    for s in data.get("scenes", []):
        print(f" Scene {s.get('scene')}: {s.get('heading')} -> {s.get('narration')[:60]}...")
else:
    print("[FAILED]")
