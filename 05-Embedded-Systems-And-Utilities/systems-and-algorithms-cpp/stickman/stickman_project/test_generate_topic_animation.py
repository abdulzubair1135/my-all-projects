"""
test_generate_topic_animation.py
================================
Prompts DeepSeek to generate custom Python drawing functions and script
specifically for the topic: 'Friend asking for money and suddenly going invisible'.
"""

import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import direct_deepseek
import re
import json

TOPIC = "Friend asking for money and suddenly going invisible"

prompt = f"""
You are an expert Python animator and comedic scriptwriter.
Create a complete, hilarious, 4-scene 2D stickman animation script AND Python PIL drawing code for YouTube Shorts for this exact topic:
Topic: '{TOPIC}'

Scene Breakdown:
Scene 1: Street / Chai Tapri setup with tea kettle & bench. Boy 1 urgently asking friend: "Bhai bas 500 rupay UPI kar de, kal pakka wapas karunga!"
Scene 2: Dost smiling in hoodie, pretending to type on his phone: "Arre bhai tere liye jaan haazir hai, bas scan kar raha hoon..."
Scene 3: Boy 1 staring at phone screen: "Pending bata raha hai bhai... aur tu kahan gaya?" Dilated shock face.
Scene 4: Climax: Dost has vanished into a puffy comic smoke cloud ('POOF!'), only an empty silhouette/shoes left behind. Boy 1 in disbelief: "Bhai 500 ke chakkar mein insaan se hawa ban gaya!"

STRICT REQUIREMENTS:
1. Provide valid Python PIL drawing code with 4 functions:
   - draw_scene_1(draw, t, dur, w, h)
   - draw_scene_2(draw, t, dur, w, h)
   - draw_scene_3(draw, t, dur, w, h)
   - draw_scene_4(draw, t, dur, w, h)
   Use `w=720, h=1280`. Use math.sin(t) for smooth organic physics (tea steam, hand waving, blinking eyes, smoke puff expansion).
2. Provide the script metadata block with `hook`, `title`, `scenes` array (containing `scene`, `speaker`, `spoken_hindi`, `dialogue`, `sfx`).

Output the complete python code inside a single ```python ... ``` markdown block.
"""

print(f"[*] Prompting DeepSeek to write custom animation code for '{TOPIC}'...")
response = direct_deepseek.ask_deepseek(prompt, max_wait_sec=90)
print(f"[*] Response received ({len(response)} chars)!")

with open("scratch/deepseek_raw_money_topic.txt", "w", encoding="utf-8") as f:
    f.write(response)

print("[*] Saved raw DeepSeek response to scratch/deepseek_raw_money_topic.txt")
