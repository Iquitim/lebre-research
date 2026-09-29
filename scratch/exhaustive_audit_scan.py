import os
import re
from pathlib import Path

search_dirs = [
    Path("docs"),
    Path("experiments/ARCH-SPEC-01"),
    Path("experiments/ARCH-SPEC-01R"),
    Path("experiments/ARCH-SPEC-01R2"),
    Path("experiments/ARCH-SPEC-01R2a"),
    Path("README.md"),
]

patterns = {
    "four-state": re.compile(r"\bfour[- ]states?\b", re.IGNORECASE),
    "four-phase": re.compile(r"\bfour[- ]phases?\b", re.IGNORECASE),
    "quatro estados": re.compile(r"\bquatro[- ]estados?\b", re.IGNORECASE),
    "quatro fases": re.compile(r"\bquatro[- ]fases?\b", re.IGNORECASE),
    "garante": re.compile(r"\bgarante\b", re.IGNORECASE),
    "garantido": re.compile(r"\bgarantid[oa]s?\b", re.IGNORECASE),
    "garantia": re.compile(r"\bgarantias?\b", re.IGNORECASE),
    "jamais": re.compile(r"\bjamais\b", re.IGNORECASE),
    "nunca": re.compile(r"\bnunca\b", re.IGNORECASE),
    "sempre": re.compile(r"\bsempre\b", re.IGNORECASE),
    "strictly bounded": re.compile(r"\bstrictly bounded\b", re.IGNORECASE),
    "strict bound": re.compile(r"\bstrict bounds?\b", re.IGNORECASE),
    "hard bound": re.compile(r"\bhard bounds?\b", re.IGNORECASE),
    "flawless": re.compile(r"\bflawless\b", re.IGNORECASE),
    "perfect": re.compile(r"\bperfect\b", re.IGNORECASE),
    "guarantee": re.compile(r"\bguarantees?\b", re.IGNORECASE),
    "guaranteed": re.compile(r"\bguaranteed\b", re.IGNORECASE),
    "440 bytes": re.compile(r"440\s*bytes", re.IGNORECASE),
    "440.0 bytes": re.compile(r"440\.0\s*bytes", re.IGNORECASE),
    "100 FLOPs": re.compile(r"100\s*FLOPs?", re.IGNORECASE),
    "100 FLOPs/step": re.compile(r"100\s*FLOPs?/step", re.IGNORECASE),
    "100 FLOPs/passo": re.compile(r"100\s*FLOPs?/passo", re.IGNORECASE),
}

results = {k: [] for k in patterns}

for item in search_dirs:
    if not item.exists():
        continue
    if item.is_file():
        candidates = [item]
    else:
        candidates = [p for p in item.rglob("*") if p.is_file() and p.suffix.lower() in [".md", ".yaml", ".yml", ".html", ".txt", ".py"]]
        
    for fpath in candidates:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = content.splitlines()
        for lnum, line in enumerate(lines, 1):
            for p_name, pat in patterns.items():
                if pat.search(line):
                    results[p_name].append((str(fpath), lnum, line.strip()))

print("=== EXHAUSTIVE SCAN RESULTS ===")
for k, matches in results.items():
    print(f"\n--- Term: '{k}' -> {len(matches)} matches ---")
    for fpath, lnum, line in matches:
        safe_line = line[:120].encode('ascii', errors='replace').decode('ascii')
        print(f"  [{fpath}:{lnum}] {safe_line}")
