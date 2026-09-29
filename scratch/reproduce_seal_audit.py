#!/usr/bin/env python3
"""
reproduce_seal_audit.py:
One-command end-to-end reproducibility script for LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01.
Regenerates all audit tables, figures, statistical verifications, and manifest
from sealed raw data artifacts.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01: REPRODUCIBILITY PIPELINE")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working Directory: {Path.cwd()}")
    print("-" * 60)
    
    scripts = [
        ("audit_hash_parent.py", "Cryptographic Parent Preservation"),
        ("audit_gate_provenance.py", "Gate Provenance Analysis"),
        ("audit_reproduce_and_evaluate.py", "Raw-to-Report Table Reproduction & Compliance Matrix"),
        ("audit_pareto_recomputation.py", "Pareto Multi-Objective Recomputation"),
        ("audit_statistical_claims.py", "Statistical Claim & Inferential Test Audit"),
        ("audit_support_and_tracking.py", "Lag Support & Regime Tracking Analysis"),
        ("test_t3_order_invariance.py", "T3 Internal Order Invariance Permutation Test"),
        ("plot_seal_audit_figures.py", "Render 12 Forensic Audit Figures (F1..F12)"),
        ("generate_audit_manifest.py", "Generate AUDIT_SEAL_MANIFEST.json")
    ]
    
    for script_name, desc in scripts:
        script_path = Path("scratch") / script_name
        print(f"\n[RUNNING] {script_name}: {desc}...")
        res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[ERROR] {script_name} failed with code {res.returncode}:")
            print(res.stderr)
            sys.exit(1)
        else:
            stdout_lines = res.stdout.strip().split("\n")
            summary_out = "\n".join(stdout_lines[-3:]) if len(stdout_lines) >= 3 else res.stdout.strip()
            print(f"[SUCCESS] {script_name}")
            print(summary_out)
            
    print("\n" + "=" * 60)
    print("ALL AUDIT REPRODUCIBILITY STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
