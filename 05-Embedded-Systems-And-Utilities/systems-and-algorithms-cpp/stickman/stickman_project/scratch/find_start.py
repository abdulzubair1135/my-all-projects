with open('scratch/last_raw_ds.txt', encoding='utf-8') as f:
    t = f.read()

import re, json
m = list(re.finditer(r'\{\s*"hook"', t))
print("Matches found:", len(m))
if m:
    idx = m[-1].start()
    clean_json = t[idx:]
    # Remove FINISHED
    clean_json = re.sub(r'FINISHED.*$', '', clean_json).strip()
    last_brace = clean_json.rfind('}')
    clean_json = clean_json[:last_brace+1]
    data = json.loads(clean_json)
    print("SUCCESS!")
    print("Hook:", data.get("hook"))
    print("Title:", data.get("title"))
    print("Images:", data.get("image_queries"))
    for s in data["scenes"]:
        print(f" Scene {s['scene']}: {s['heading']} ({s['animation_action']})")
