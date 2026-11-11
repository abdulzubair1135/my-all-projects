import sys, os
sys.path.insert(0, os.path.abspath("."))
import direct_deepseek
import curiosity_director
import json
import re

topic = "Why Can't We Tickle Ourselves?"
print("Querying DeepSeek for curiosity script...")
prompt = (
    f"You are the Head Science Director for an ultra-viral English 'Did You Know?' YouTube Shorts channel with 2D Stickman animations.\n"
    f"Topic: '{topic}'.\n"
    "Create a captivating 4-scene scientific curiosity explainer script in fluent, energetic English.\n"
    "Output ONLY a single valid raw JSON object. No intro, no markdown explanation before or after. Start immediately with { and end with }:\n"
    "{\n"
    '  "hook": "Did you know that...?",\n'
    '  "title": "Why Can\'t You Tickle Yourself? 😂 Explained! #shorts #science",\n'
    '  "description": "Why your brain cancels tickling! #shorts #science #didyouknow #stickman",\n'
    '  "tags": ["shorts", "science", "didyouknow", "animation", "curiosity"],\n'
    '  "image_queries": ["cerebellum brain", "tickling reaction", "somatosensory cortex"],\n'
    '  "scenes": [\n'
    '    {"scene": 1, "heading": "THE TICKLE TEST", "narration": "Try tickling your own ribs right now. Nothing happens, right? But if a friend touches you, you burst into laughter!", "animation_action": "vibrating_soundwaves", "stickman_pose": "cupping_ear", "sfx": ["whoosh"]},\n'
    '    {"scene": 2, "heading": "THE PREDICTIVE BRAIN", "narration": "Deep in your brain, your cerebellum tracks every muscle movement you make before it even happens!", "animation_action": "ear_cross_section", "stickman_pose": "shocked_pointing", "sfx": ["ding"]},\n'
    '    {"scene": 3, "heading": "CANCELING THE SIGNAL", "narration": "Since your brain predicted the touch, it actively blocks the sensation so you do not get sensory overload!", "animation_action": "electric_sparks", "stickman_pose": "brain_glowing", "sfx": ["record_scratch"]},\n'
    '    {"scene": 4, "heading": "THE SURPRISE FACTOR", "narration": "You can only be tickled by surprise! Hit subscribe for more mind-blowing body secrets!", "animation_action": "thumbs_up_subscribe", "stickman_pose": "celebration", "sfx": ["boom"]}\n'
    '  ]\n'
    "}"
)

raw = direct_deepseek.ask_deepseek(prompt, max_wait_sec=50)
print(f"RAW LENGTH: {len(raw)}")
print("RAW PREVIEW (first 500 chars):")
print(raw[:500])
print("\nRAW END (last 300 chars):")
print(raw[-300:])

with open("scratch/last_raw_ds.txt", "w", encoding="utf-8") as f:
    f.write(raw)

print(f"Saved raw text of length {len(raw)} to scratch/last_raw_ds.txt")
