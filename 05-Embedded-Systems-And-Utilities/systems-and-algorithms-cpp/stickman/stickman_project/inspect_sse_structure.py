import json
import re

with open("raw_sse_sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, l in enumerate(lines[:30]):
    l = l.strip()
    if l.startswith("data:"):
        print(f"[{idx}] {l[:100]}")

print("...")
for idx, l in enumerate(lines[-30:], start=len(lines)-30):
    l = l.strip()
    if l.startswith("data:"):
        print(f"[{idx}] {l[:100]}")
