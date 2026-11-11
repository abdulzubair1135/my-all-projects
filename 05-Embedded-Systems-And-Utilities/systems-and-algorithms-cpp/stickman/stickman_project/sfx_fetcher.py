"""
sfx_fetcher.py
==============
Handles authentic SFX and BGM resolution:
- Uses ONLY authentic, organic acoustic recorded sound effects (WAV).
- ZERO synthetic sine oscillators / ZERO high-pitch Hz beep tones.
- Maps comedy cues directly to clean cartoon foley:
    'alarm'        -> 'ding.wav' / 'boing.wav'
    'shock'        -> 'record_scratch.wav' / 'gasp.wav'
    'wake'         -> 'whoosh.wav'
    'punchline'    -> 'vine_boom.wav' / 'laugh.wav'
    'bgm'          -> 'sneaky_snitch.mp3'
"""

import os
import urllib.request

SFX_DIR = "sfx"
os.makedirs(SFX_DIR, exist_ok=True)

# Curated Authentic Foley Mapping
AUTHENTIC_MAPPING = {
    "alarm": "ding.wav",
    "alarm_ring": "ding.wav",
    "snore": "whoosh.wav",
    "tea_sip": "pop.wav",
    "sip": "pop.wav",
    "shock": "record_scratch.wav",
    "dramatic": "record_scratch.wav",
    "whistle": "record_scratch.wav",
    "gasp": "gasp.wav",
    "boing": "boing.wav",
    "boom": "vine_boom.wav",
    "vine_boom": "vine_boom.wav",
    "laugh": "laugh.wav",
    "pop": "pop.wav",
    "whoosh": "whoosh.wav",
}

def resolve_sfx(tag_or_url):
    """Returns path to an authentic audio file. Never synthesizes Hz beeps."""
    if not tag_or_url:
        return None

    # 1. Direct URL download if provided
    if tag_or_url.startswith("http://") or tag_or_url.startswith("https://"):
        fname = os.path.basename(tag_or_url.split("?")[0])
        if not fname.endswith((".wav", ".mp3")):
            fname += ".mp3"
        out_p = os.path.join(SFX_DIR, fname)
        if os.path.exists(out_p):
            return out_p
        try:
            req = urllib.request.Request(tag_or_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as r, open(out_p, 'wb') as f:
                f.write(r.read())
            print(f"[SFX] Auto-downloaded external audio: {out_p}")
            return out_p
        except Exception as e:
            print(f"[SFX] Download error for {tag_or_url}: {e}")
            return None

    clean = tag_or_url.lower().replace(" ", "_").strip()

    # 2. Check direct file in sfx/
    for ext in [".wav", ".mp3"]:
        direct_p = os.path.join(SFX_DIR, clean + ext)
        if os.path.exists(direct_p):
            return direct_p

    # 3. Check authentic foley mapping
    if clean in AUTHENTIC_MAPPING:
        mapped_file = AUTHENTIC_MAPPING[clean]
        p = os.path.join(SFX_DIR, mapped_file)
        if os.path.exists(p):
            return p

    # 4. Fallback to pop.wav
    fallback = os.path.join(SFX_DIR, "pop.wav")
    return fallback if os.path.exists(fallback) else None

if __name__ == "__main__":
    print("Alarm mapped to:", resolve_sfx("alarm_ring"))
    print("Shock mapped to:", resolve_sfx("shock"))
    print("BGM mapped to:", resolve_sfx("sneaky_snitch"))
