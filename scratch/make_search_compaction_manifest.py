#!/usr/bin/env python3
"""
make_search_compaction_manifest.py

Generates CORRELATION_SEARCH_MANIFEST.json for
experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01
"""

import os
import json
import hashlib
from datetime import datetime

EXP_DIR = "experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    manifest = {
        "study_id": "LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01",
        "title": "Dense-to-Sparse Lag-Hypothesis Search Space Compaction",
        "author": "Independent Skeptical Senior Researcher and Scientific Software Auditor",
        "date": "2026-09-22",
        "status": "CONDITIONALLY_SEALED",
        "primary_outcome": "COMPACTED_SPARSE_FRONTIER_SUPERIOR_TO_DENSE_MULTIRATE",
        "artifacts": {}
    }
    
    # Scan EXP_DIR
    for root, dirs, files in os.walk(EXP_DIR):
        for f in sorted(files):
            if f == "CORRELATION_SEARCH_MANIFEST.json":
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, EXP_DIR).replace("\\", "/")
            
            size = os.path.getsize(full_path)
            h = sha256_file(full_path)
            
            if rel_path.endswith(".md"):
                cat = "DOCUMENTATION"
            elif rel_path.endswith(".csv"):
                cat = "DATASET"
            elif rel_path.endswith(".png"):
                cat = "FIGURE"
            elif rel_path.endswith(".py"):
                cat = "SCRIPT"
            elif rel_path.endswith(".txt"):
                cat = "CHECKSUM"
            else:
                cat = "OTHER"
                
            manifest["artifacts"][rel_path] = {
                "sha256": h,
                "size_bytes": size,
                "category": cat
            }
            
    out_path = os.path.join(EXP_DIR, "CORRELATION_SEARCH_MANIFEST.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Wrote {out_path} with {len(manifest['artifacts'])} tracked artifacts.")

if __name__ == '__main__':
    main()
