import re, json

with open('scratch/last_raw_ds.txt', encoding='utf-8') as f:
    text = f.read()

# Remove FINISHED suffix
text = re.sub(r'FINISHED.*$', '', text).strip()

# Look for JSON starting from {"hook"
m = re.search(r'\{\s*"hook"[\s\S]*\}', text)
if not m:
    # Look for last { ... } containing "scenes"
    all_braces = [i for i, c in enumerate(text) if c == '{']
    for b_idx in reversed(all_braces):
        candidate = text[b_idx:]
        last_b = candidate.rfind('}')
        if last_b != -1:
            candidate = candidate[:last_b+1]
            try:
                parsed = json.loads(candidate)
                if "scenes" in parsed:
                    m = candidate
                    break
            except Exception:
                pass

if isinstance(m, str):
    parsed = json.loads(m)
elif m:
    parsed = json.loads(m.group(0))
else:
    parsed = None

if parsed:
    print("PARSED SUCCESSFULLY!")
    print("Hook:", parsed.get("hook"))
    print("Title:", parsed.get("title"))
    print("Images:", parsed.get("image_queries"))
    print("Scenes:", len(parsed.get("scenes", [])))
    for s in parsed["scenes"]:
        print(f" Scene {s['scene']}: {s['heading']} -> {s['narration']}")
else:
    print("FAILED TO PARSE")
