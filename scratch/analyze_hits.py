import json

with open('scratch/search_hits.json', 'r', encoding='utf-8') as f:
    hits = json.load(f)

by_cat = {}
for h in hits:
    by_cat.setdefault(h['cat'], []).append(h)

for cat, items in by_cat.items():
    print(f"=== Category: {cat} ({len(items)} hits) ===")
    for item in items:
        # print safely
        txt = item['text'][:120].encode('ascii', errors='replace').decode('ascii')
        print(f"  {item['file']}:{item['line']} -> {txt}")
