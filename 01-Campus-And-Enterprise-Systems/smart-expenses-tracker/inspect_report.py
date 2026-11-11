import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('generate_perfect_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

parts = text.split('<div class="page-break"></div>')
print(f"Total parts split by page-break: {len(parts)}")
for i, p in enumerate(parts):
    clean = re.sub(r'<[^>]+>', ' ', p)
    words = len(clean.split())
    titles = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', p)
    has_mermaid = 'class="mermaid"' in p
    print(f"Part {i+1}: {words} words | Mermaid: {has_mermaid} | Titles: {titles[:2]}")
