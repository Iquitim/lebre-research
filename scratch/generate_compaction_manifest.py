#!/usr/bin/env python3
"""
generate_compaction_manifest.py

Computes cryptographic hashes for all artifacts in
experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/
and produces RESOURCE_COMPACTION_MANIFEST.json.
"""

import hashlib
import json
import platform
import sys
from pathlib import Path
import pandas as pd

STUDY_DIR = Path("experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01")
MANIFEST_PATH = STUDY_DIR / "RESOURCE_COMPACTION_MANIFEST.json"

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    artifact_files = sorted([p for p in STUDY_DIR.rglob("*") if p.is_file() and p.name != "RESOURCE_COMPACTION_MANIFEST.json"])
    
    file_inventory = {}
    for p in artifact_files:
        rel_path = p.relative_to(STUDY_DIR).as_posix()
        file_inventory[rel_path] = {
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size
        }
        
    manifest = {
        "study_metadata": {
            "study_id": "LEBRE-V0.2-RESOURCE-COMPACTION-01",
            "parent_study": "LEBRE-V0.2-INTEGRATION-DESIGN-01",
            "parent_seal": "LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01",
            "primary_intervention": "FP16_PERSISTENT_CORR_GRID_FP32_UPDATE",
            "canonical_version": "0.1",
            "lebre_v0_1_status": "FROZEN_WITH_SCOPE_LIMITS",
            "m3_status": "UNOPENED",
            "novelty_claim_ready": "NO",
            "canonical_src_mutated": "NO",
            "canonical_tests_mutated": "NO",
            "primary_outcome": "FP16_COMPACTION_VALIDATED",
            "resource_compaction_supported": "YES",
            "safe_for_shadow_rent_governance_stage": "YES",
            "safe_for_integrated_validation": "NO",
            "next_recommended_stage": "LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01"
        },
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "pandas_version": pd.__version__
        },
        "cohort_accounting": {
            "dev_seeds": "1401..1410 (N=10)",
            "final_seeds": "1411..1440 (N=30)",
            "total_paired_runs": 560,
            "tasks_evaluated": 14,
            "total_streaming_steps": 3360000
        },
        "resource_accounting": {
            "c0_persistent_bytes": 1306,
            "c1_persistent_bytes": 976,
            "persistent_byte_savings": 330,
            "percent_savings": "25.27%",
            "c1_peak_working_bytes": 984,
            "legacy_r2_ceiling_bytes": 1024,
            "legacy_r2_memory_compliance": "PASS"
        },
        "statistical_accounting": {
            "aggregate_nmse_c0": 0.3282,
            "aggregate_nmse_c1": 0.3282,
            "paired_delta_nmse": "+0.000009",
            "tost_bound": "+/- 0.0100",
            "tost_p_value": "< 1e-15",
            "predictive_equivalence": "SUPPORTED",
            "candidate_top1_agreement_rate": 0.9973,
            "structural_state_agreement_rate": 0.9995
        },
        "artifact_inventory": file_inventory
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Wrote manifest with {len(file_inventory)} artifacts to {MANIFEST_PATH}")

if __name__ == "__main__":
    generate_manifest()
