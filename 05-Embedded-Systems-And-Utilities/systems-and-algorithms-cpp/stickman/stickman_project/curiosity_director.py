"""
curiosity_director.py
=====================
Autonomous AI Director for English "Did You Know?" / Science Curiosity Shorts.
- Prompts DeepSeek to act as the Head Science Video Director.
- Generates:
  1. Catchy English "Did you know?" Hook
  2. 4-Scene Progressive Scientific Breakdown in English
  3. Image Search Keywords & Direct Image URLs for diagrams/photos
  4. Dynamic Python PIL Animation Code for Stickman interacting with the concept
  5. Cinematic SFX cues (whoosh, revelation bell, sub-boom, pop)
"""

import json
import re
import os
import socket
import urllib.request
import urllib.parse
import direct_deepseek
from PIL import Image

# Global socket timeout: prevents any network call from hanging indefinitely
socket.setdefaulttimeout(4)

CACHE_IMAGE_DIR = "downloaded_assets"
os.makedirs(CACHE_IMAGE_DIR, exist_ok=True)


def fetch_educational_image(query, filename, fallback_topic=None, exclude_urls=None):
    """
    Downloads high-res educational photo/diagram from:
    1. Wikimedia Commons File Search API
    2. Wikipedia PageImages API
    With strict 3-second network timeouts so it NEVER hangs!
    """
    dest_path = os.path.join(CACHE_IMAGE_DIR, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 4000:
        return dest_path

    if exclude_urls is None:
        exclude_urls = set()

    BLOCKED_TERMS = {"shooting", "massacre", "gun", "war", "attack", "homicide", "casualty", "crime", "bomb", "kill", "victim"}
    VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".svg")

    clean_base = re.sub(r'[^\w\s]', '', query).strip()
    words = clean_base.split()
    search_variants = [clean_base]
    if len(words) > 2:
        search_variants.append(" ".join(words[:2]))
    search_variants = search_variants[:2]  # Max 2 fast candidates

    # 1. Search Wikimedia Commons File API (fast timeout: 3s)
    for q_term in search_variants:
        if not q_term:
            continue
        try:
            url = (
                f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
                f"&gsrsearch={urllib.parse.quote(q_term)}&gsrnamespace=6&prop=imageinfo"
                f"&iiprop=url&iiurlwidth=1280&format=json"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (CuriosityDirector/4.0)"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                pages = data.get("query", {}).get("pages", {})
                for pid, p in pages.items():
                    title = p.get("title", "").lower()
                    if any(bad in title for bad in BLOCKED_TERMS):
                        continue
                    if not any(title.endswith(ext) for ext in VALID_EXTS):
                        continue
                    info = p.get("imageinfo", [{}])[0]
                    img_url = info.get("thumburl") or info.get("url")
                    if img_url and img_url not in exclude_urls:
                        img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(img_req, timeout=4) as r_img, open(dest_path, "wb") as f_out:
                            f_out.write(r_img.read())
                        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 4000:
                            exclude_urls.add(img_url)
                            return dest_path
        except Exception:
            pass

    # 2. Search Wikipedia PageImages API (fast timeout: 3s)
    for q_term in search_variants:
        if not q_term:
            continue
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(q_term)}&gsrlimit=4&prop=pageimages&pithumbsize=1280"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (CuriosityDirector/4.0)"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                pages = data.get("query", {}).get("pages", {})
                for pid, p in pages.items():
                    title = p.get("title", "").lower()
                    if any(bad in title for bad in BLOCKED_TERMS):
                        continue
                    img_url = p.get("thumbnail", {}).get("source")
                    if img_url and img_url not in exclude_urls:
                        img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(img_req, timeout=4) as r_img, open(dest_path, "wb") as f_out:
                            f_out.write(r_img.read())
                        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 4000:
                            exclude_urls.add(img_url)
                            return dest_path
        except Exception:
            pass

    return None


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
        pre = raw_text[:hook_idx].rstrip()
        if pre.endswith('{'):
            candidate = raw_text[len(pre)-1:]
        else:
            candidate = "{\n" + raw_text[hook_idx:]
        
        last_b = candidate.rfind('}')
        if last_b != -1:
            candidate = candidate[:last_b+1]
        else:
            candidate = candidate + "\n}"
        
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None


def get_curiosity_script(topic, language="hi"):
    """
    Directs a 4-scene Curiosity Short using the 3-Bot Review Council:
    Bot 1 (Dr. Factum): Scientific Accuracy & Real Fact Checking
    Bot 2 (Leo Viral): Script Doctor & Longer Storytelling Expansion (~40-45s)
    Bot 3 (Inspector Pixel): High-Precision Diagram Query QA
    Defaults to HINDI (Devanagari script) for authentic Edge-TTS native speech.
    """
    clean_top = str(topic).strip()
    try:
        import script_auditor_bots
        return script_auditor_bots.ScriptAuditorCouncil.audit_and_produce_script(clean_top, language=language)
    except Exception as e:
        print(f"[!] 3-Bot Council note: {e}")

    is_hi = (language == "hi")

    if is_hi:
        prompt = (
            f"You are the Head Science Director for an ultra-viral Hindi 'क्या आपको पता है?' YouTube Shorts channel with 2D Stickman animations.\n"
            f"Topic: '{clean_top}'.\n"
            "Create a captivating 4-scene scientific curiosity explainer script in natural, fluent HINDI using pure DEVANAGARI SCRIPT (हिंदी).\n"
            "CRUCIAL: Do NOT write narration in Roman/Hinglish! Pure Devanagari Hindi is required for natural TTS pronunciation.\n"
            "Every scene MUST have a distinct ENGLISH 'image_query' (2-3 keywords) for scientific diagram searches.\n"
            "Output ONLY a single valid JSON object with this exact structure:\n"
            "{\n"
            '  "hook": "क्या आपको पता है कि...?",\n'
            f'  "title": "{clean_top} का असली सच! 🤯 #shorts #science #hindi",\n'
            f'  "description": "{clean_top} के पीछे का दिमाग हिलाने वाला विज्ञान! #shorts #science #facts #hindi",\n'
            '  "tags": ["shorts", "science", "facts", "hindi", "curiosity", "education"],\n'
            '  "scenes": [\n'
            '    {\n'
            '      "scene": 1,\n'
            '      "heading": "असली रहस्य",\n'
            '      "narration": "शुरुआती 2-3 पंक्तियाँ देवनागरी हिंदी में जो रहस्य को रोचक बनाएं।",\n'
            '      "image_query": "specific english diagram keyword 1",\n'
            '      "animation_action": "scratching_head",\n'
            '      "stickman_pose": "confused",\n'
            '      "sfx": ["whoosh"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 2,\n'
            '      "heading": "वैज्ञानिक प्रक्रिया",\n'
            '      "narration": "सूक्ष्म जैविक या भौतिक प्रक्रिया को सटीक और रोचक हिंदी में समझाएं।",\n'
            '      "image_query": "specific english diagram keyword 2",\n'
            '      "animation_action": "pointing_to_diagram",\n'
            '      "stickman_pose": "explaining",\n'
            '      "sfx": ["ding", "pop"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 3,\n'
            '      "heading": "हैरान करने वाला सच",\n'
            '      "narration": "दिमाग हिलाने वाले मुख्य वैज्ञानिक ट्विस्ट को 2-3 हिंदी वाक्यों में उजागर करें।",\n'
            '      "image_query": "specific english diagram keyword 3",\n'
            '      "animation_action": "brain_glowing",\n'
            '      "stickman_pose": "shocked",\n'
            '      "sfx": ["record_scratch", "gasp"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 4,\n'
            '      "heading": "निष्कर्ष",\n'
            '      "narration": "अंतिम 2 वाक्य जो ज्ञानवर्धक हों और चैनल को सब्सक्राइब करने का आग्रह करें।",\n'
            '      "image_query": "specific english diagram keyword 4",\n'
            '      "animation_action": "thumbs_up_celebrate",\n'
            '      "stickman_pose": "celebration",\n'
            '      "sfx": ["boom"]\n'
            '    }\n'
            '  ]\n'
            "}"
        )
    else:
        prompt = (
            f"You are the Head Science Director for an ultra-viral English 'Did You Know?' YouTube Shorts channel with 2D Stickman animations.\n"
            f"Topic: '{clean_top}'.\n"
            "Create a captivating 4-scene scientific curiosity explainer script in fluent, energetic English. Keep narration punchy, cinematic, and fast-paced.\n"
            "IMPORTANT: Every single scene MUST have a DIFFERENT, highly specific 'image_query' (1-3 concrete keywords) for Wikimedia/Wikipedia diagram searches so every scene shows a unique diagram!\n"
            "Output ONLY a single valid JSON object with this exact structure:\n"
            "{\n"
            '  "hook": "Did you know that...?",\n'
            f'  "title": "{clean_top} Explained in 30s! #shorts #science",\n'
            f'  "description": "The mind-blowing science behind {clean_top}! #shorts #science #didyouknow #stickman",\n'
            '  "tags": ["shorts", "science", "didyouknow", "animation", "curiosity", "education", "stickman"],\n'
            '  "scenes": [\n'
            '    {\n'
            '      "scene": 1,\n'
            '      "heading": "THE HOOK / MYSTERY",\n'
            '      "narration": "Energetic 1-sentence hook explaining the curiosity question.",\n'
            '      "image_query": "concrete visual keyword 1",\n'
            '      "animation_action": "scratching_head",\n'
            '      "stickman_pose": "confused",\n'
            '      "sfx": ["whoosh"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 2,\n'
            '      "heading": "THE HIDDEN MECHANISM",\n'
            '      "narration": "The scientific mechanism and physical/biological cause.",\n'
            '      "image_query": "microscopic or biological diagram keyword 2",\n'
            '      "animation_action": "pointing_to_diagram",\n'
            '      "stickman_pose": "explaining",\n'
            '      "sfx": ["ding", "pop"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 3,\n'
            '      "heading": "THE MIND-BLOWING FACT",\n'
            '      "narration": "The craziest scientific twist or insight.",\n'
            '      "image_query": "scientific principle or organ diagram keyword 3",\n'
            '      "animation_action": "brain_glowing",\n'
            '      "stickman_pose": "shocked",\n'
            '      "sfx": ["record_scratch", "gasp"]\n'
            '    },\n'
            '    {\n'
            '      "scene": 4,\n'
            '      "heading": "THE TAKEAWAY",\n'
            '      "narration": "Closing punchline and call to action to follow for more secrets.",\n'
            '      "image_query": "cosmic or physics law diagram keyword 4",\n'
            '      "animation_action": "thumbs_up_celebrate",\n'
            '      "stickman_pose": "celebration",\n'
            '      "sfx": ["boom"]\n'
            '    }\n'
            '  ]\n'
            "}"
        )

    try:
        raw = direct_deepseek.ask_deepseek(prompt, max_wait_sec=50)
        data = parse_curiosity_json(raw)
        if data and "scenes" in data and len(data["scenes"]) >= 4:
            lang_label = "Hindi" if is_hi else "English"
            print(f"[*] DeepSeek Curiosity Director loaded {lang_label} script for: '{clean_top}'")
            return data
    except Exception as e:
        print(f"[!] DeepSeek Curiosity prompt note: {e}")

    # Fallbacks tailored to language (Pure Devanagari Hindi for flawless TTS)
    if is_hi:
        return {
            "hook": f"क्या आपको पता है कि {clean_top} के पीछे का असली वैज्ञानिक सच क्या है?",
            "title": f"{clean_top} का असली सच! 🧠 #shorts #science #hindi",
            "description": f"{clean_top} कैसे काम करता है? जानिए हैरान करने वाले विज्ञान का सच!\n\n#shorts #science #curiosity #facts #hindi",
            "tags": ["shorts", "science", "hindi", "facts", "curiosity", "education"],
            "scenes": [
                {
                    "scene": 1,
                    "heading": "असली रहस्य",
                    "narration": f"क्या आपने कभी सोचा है {clean_top} के बारे में? इसका सच आपके होश उड़ा देगा!",
                    "image_query": f"{clean_top} science diagram",
                    "animation_action": "scratching_head",
                    "stickman_pose": "confused",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "heading": "वैज्ञानिक प्रक्रिया",
                    "narration": "आपके शरीर और प्रकृति के अंदर सूक्ष्म अणु तुरंत एक तीव्र रासायनिक प्रतिक्रिया शुरू करते हैं!",
                    "image_query": f"{clean_top} mechanism biology",
                    "animation_action": "pointing_to_diagram",
                    "stickman_pose": "explaining",
                    "sfx": ["ding", "pop"]
                },
                {
                    "scene": 3,
                    "heading": "हैरान करने वाला सच",
                    "narration": "भौतिकी और हमारे तंत्रिका तंत्र के नियम मिलकर प्रकाश की गति से इस पूरी प्रक्रिया को संचालित करते हैं!",
                    "image_query": f"{clean_top} scientific structure",
                    "animation_action": "brain_glowing",
                    "stickman_pose": "shocked",
                    "sfx": ["record_scratch", "gasp"]
                },
                {
                    "scene": 4,
                    "heading": "निष्कर्ष",
                    "narration": "और इसी तरह विज्ञान हर सेकंड चमत्कार करता है! ऐसे ही ज्ञानवर्धक रहस्यों के लिए अभी सब्सक्राइब करें!",
                    "image_query": f"{clean_top} physics laws",
                    "animation_action": "thumbs_up_celebrate",
                    "stickman_pose": "celebration",
                    "sfx": ["boom"]
                }
            ]
        }
    else:
        # Extract meaningful topical keywords for guaranteed distinct scene queries
        words = [w.lower() for w in re.findall(r'\b[A-Za-z]{3,}\b', clean_top) if w.lower() not in {"why", "how", "what", "does", "when", "you", "your", "are", "have", "from", "with", "the"}]
        kw1 = words[0] if words else "science"
        kw2 = words[1] if len(words) > 1 else "clock"
        kw3 = words[2] if len(words) > 2 else "brain"

        return {
            "hook": f"Did you know the secret behind {clean_top}?",
            "title": f"The Science of {clean_top} 🧠 #shorts #didyouknow",
            "description": f"How does {clean_top} actually work? Mind-blowing science facts explained!\n\n#shorts #science #curiosity #stickman",
            "tags": ["shorts", "science", "didyouknow", "curiosity", "stickman", "facts"],
            "scenes": [
                {
                    "scene": 1,
                    "heading": "THE HIDDEN MYSTERY",
                    "narration": f"Have you ever wondered about {clean_top}? The truth is way crazier than you think!",
                    "image_query": f"{kw1} {kw2}",
                    "animation_action": "scratching_head",
                    "stickman_pose": "confused",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "heading": "THE CHAIN REACTION",
                    "narration": "Inside your body and the environment, microscopic signals trigger an instant chain reaction!",
                    "image_query": f"{kw1} diagram",
                    "animation_action": "pointing_to_diagram",
                    "stickman_pose": "explaining",
                    "sfx": ["ding", "pop"]
                },
                {
                    "scene": 3,
                    "heading": "THE SCIENTIFIC SECRET",
                    "narration": "Your nervous system and physics work together in perfect harmony at light speed!",
                    "image_query": f"{kw2} biology",
                    "animation_action": "brain_glowing",
                    "stickman_pose": "shocked",
                    "sfx": ["record_scratch", "gasp"]
                },
                {
                    "scene": 4,
                    "heading": "MIND BLOWN",
                    "narration": "And that is how science makes the impossible happen every single second! Follow for more!",
                    "image_query": f"{kw1} theory",
                    "animation_action": "thumbs_up_celebrate",
                    "stickman_pose": "celebration",
                    "sfx": ["boom"]
                }
            ]
        }
