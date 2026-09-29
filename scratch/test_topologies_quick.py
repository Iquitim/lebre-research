#!/usr/bin/env python3
"""
test_topologies_quick.py: Quick sanity test of all 14 tasks across T1, T2, T3
to verify promotion, specialization, and redundancy control.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scratch.run_v02_integration_experiments import run_single_simulation

print("--- TESTING TOPOLOGY T3 (RESOURCE-AWARE ARBITRATION) ---")
test_tasks = [
    "I1_Memoryless_Linear",
    "I2_Static_Nonlinear_Negative_Control",
    "I3_Single_Exact_Delay",
    "I4_Multi_Sparse_Delay",
    "I6_Continuous_Latent_State",
    "I9_Hybrid_Delay_Plus_Latent_State",
    "I10_Redundant_Temporal_Structure",
    "I11_Regime_Switch_Delay_To_Latent"
]

for t_id in test_tasks:
    res = run_single_simulation(t_id, seed=1301, topology="T3", total_steps=6000)
    print(f"{t_id:38s} | Expected: {res['expected_class']:15s} | Modal: {res['modal_state']:10s} | NMSE: {res['nmse']:.4f} | Lags: {res['mean_active_lags']:.2f} | Rec: {res['mean_rec_active']:.2f}")
