import json

with open('scratch/search_hits.json', 'r', encoding='utf-8') as f:
    hits = json.load(f)

for cat in ['440_bytes', 'quatro_estados', 'quatro_fases', 'garante', 'jamais', 'strictly_bounded', '100_flops']:
    print(f"=== {cat} ===")
    for h in hits:
        if h['cat'] == cat:
            txt = h['text'].encode('ascii', errors='replace').decode('ascii')
            print(f"  {h['file']}:{h['line']} -> {txt}")
