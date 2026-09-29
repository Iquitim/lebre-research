import os
import json
import hashlib

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"

manifest = {
    "study_id": "LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01",
    "timestamp_iso": "2026-09-22T07:05:00-03:00",
    "author": "Independent Skeptical Senior Researcher",
    "milestone": "Milestone 2 (Experimental Stream v0.2)",
    "status": "SEALED",
    "primary_outcome": "COMPONENT_TIMESCALE_CONFLICT",
    "multirate_shadow_governance_supported": False,
    "whole_block_shadow_governance": "NOT_VALIDATED",
    "safe_for_integrated_validation": False,
    "safe_to_open_m3": False,
    "canonical_src_changed": False,
    "canonical_tests_changed": False,
    "files": {}
}

for root, dirs, files in os.walk(EXP_DIR):
    for f in sorted(files):
        if f == "SHADOW_MULTIRATE_MANIFEST.json":
            continue
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, EXP_DIR).replace("\\", "/")
        with open(full_path, 'rb') as fp:
            data = fp.read()
            h = hashlib.sha256(data).hexdigest()
            size = len(data)
        manifest["files"][rel_path] = {
            "sha256": h,
            "bytes": size
        }

manifest_path = os.path.join(EXP_DIR, "SHADOW_MULTIRATE_MANIFEST.json")
with open(manifest_path, 'w', encoding='utf-8') as fp:
    json.dump(manifest, fp, indent=2)

print(f"Wrote {manifest_path} with {len(manifest['files'])} files.")
