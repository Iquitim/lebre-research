#!/usr/bin/env python3
"""
generate_audit_manifest.py:
Computes cryptographic hashes for all audit artifacts and produces AUDIT_SEAL_MANIFEST.json.
"""

import hashlib
import json
import platform
import sys
from pathlib import Path
import pandas as pd

AUDIT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01")
MANIFEST_PATH = AUDIT_DIR / "AUDIT_SEAL_MANIFEST.json"

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

artifact_files = sorted([p for p in AUDIT_DIR.rglob("*") if p.is_file() and p.name != "AUDIT_SEAL_MANIFEST.json"])

file_hashes = {}
for p in artifact_files:
    rel_path = p.relative_to(AUDIT_DIR).as_posix()
    file_hashes[rel_path] = {
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size
    }

manifest_data = {
    "audit_metadata": {
        "audit_id": "LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01",
        "parent_study": "LEBRE-V0.2-INTEGRATION-DESIGN-01",
        "target_architecture": "T3_RESOURCE_AWARE_CONDITIONAL_ARBITRATION",
        "canonical_version": "0.1",
        "lebre_v0_1_status": "FROZEN_WITH_SCOPE_LIMITS",
        "m3_status": "UNOPENED",
        "novelty_claim_ready": "NO",
        "canonical_src_mutated": "NO",
        "canonical_tests_mutated": "NO",
        "primary_audit_outcome": "MULTIPLE_CORRECTABLE_ISSUES",
        "candidate_status": "EXPERIMENTAL_NON_CANONICAL",
        "safe_for_integrated_v0_2_validation": "NO",
        "next_recommended_stage": "LEBRE-V0.2-RESOURCE-COMPACTION-01"
    },
    "environment": {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy_version": pd.np.__version__ if hasattr(pd, "np") else "numpy",
        "pandas_version": pd.__version__
    },
    "verification_accounting": {
        "raw_runs_expected": 2100,
        "raw_runs_verified": 2100,
        "seeds_verified": "1311..1340 (N=30)",
        "tasks_verified": "I1..I14 (N=14)",
        "topologies_verified": "T1, T1R, T2, T3, O_ALL (N=5)",
        "report_cells_audited": 100,
        "report_cells_mismatched": 98,
        "unexplained_mismatches": 0,
        "root_cause_mismatches": "Pasting DEV seed 1301 single-run into report table instead of 30-seed confirmatory mean"
    },
    "artifact_inventory": file_hashes
}

with open(MANIFEST_PATH, "w") as f:
    json.dump(manifest_data, f, indent=2)

print(f"Generated {MANIFEST_PATH} with {len(file_hashes)} artifacts hashed.")
