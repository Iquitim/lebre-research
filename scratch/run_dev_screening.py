#!/usr/bin/env python3
"""
run_dev_screening.py

Executes DEV screening and rate ladder exploration for LEBRE v0.2 Multirate Decomposition.
Cohort: Seeds 1701..1710 (N=10) across 14 Benchmark Streams.
Generates:
- COMPONENT_SENSITIVITY_DEV_RESULTS.csv
- COMPONENT_RATE_BOUNDARIES.csv
- MULTIRATE_DEV_RESULTS.csv
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS
from scratch.run_v02_multirate_experiments import run_single_simulation

OUT_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"
DEV_SEEDS = list(range(1701, 1711))

def run_batch(configs, max_workers=6):
    tasks = []
    for model_id, params in configs.items():
        for task_id in BENCHMARK_TASKS:
            for seed in DEV_SEEDS:
                tasks.append((task_id, seed, model_id, params))
                
    print(f"Executing batch of {len(tasks)} simulation runs with {max_workers} workers...")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_single_simulation, t) for t in tasks]
        for f in as_completed(futures):
            results.append(f.result())
            if len(results) % 200 == 0:
                print(f"  Completed {len(results)}/{len(tasks)} runs ({time.time()-t0:.1f}s)...")
                
    print(f"Batch completed in {time.time()-t0:.2f}s.")
    return pd.DataFrame(results)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 1. Isolated Sensitivity Screening at K=5
    sensitivity_configs = {
        "D0": {}, # Continuous baseline
        "D7": {"K_probe": 5},
        "D8": {"K_cand_obs": 5, "K_cand_learn": 5},
        "D9F": {"K_rec_forward": 5},
        "D9L": {"K_rec_forward": 1, "K_rec_learn": 5},
        "D10": {"K_arbitration": 5}
    }
    
    df_sens = run_batch(sensitivity_configs)
    sens_csv = os.path.join(OUT_DIR, "COMPONENT_SENSITIVITY_DEV_RESULTS.csv")
    df_sens.to_csv(sens_csv, index=False)
    print(f"Wrote {sens_csv}")
    
    # 2. Component Rate Ladder Exploration
    ladder_configs = {
        # Probing ladder
        "PROBE_K1": {"K_probe": 1},
        "PROBE_K2": {"K_probe": 2},
        "PROBE_K5": {"K_probe": 5},
        "PROBE_K10": {"K_probe": 10},
        # Candidate adaptation ladder
        "CAND_K1": {"K_cand_obs": 1, "K_cand_learn": 1},
        "CAND_K2": {"K_cand_obs": 2, "K_cand_learn": 2},
        "CAND_K5": {"K_cand_obs": 5, "K_cand_learn": 5},
        "CAND_K10": {"K_cand_obs": 10, "K_cand_learn": 10},
        # Recurrent forward ladder (State propagation)
        "REC_FWD_K1": {"K_rec_forward": 1},
        "REC_FWD_K2": {"K_rec_forward": 2},
        "REC_FWD_K5": {"K_rec_forward": 5},
        "REC_FWD_K10": {"K_rec_forward": 10},
        # Recurrent learning ladder (RTRL parameters, forward stays K=1)
        "REC_LRN_K1": {"K_rec_forward": 1, "K_rec_learn": 1},
        "REC_LRN_K2": {"K_rec_forward": 1, "K_rec_learn": 2},
        "REC_LRN_K5": {"K_rec_forward": 1, "K_rec_learn": 5},
        "REC_LRN_K10": {"K_rec_forward": 1, "K_rec_learn": 10},
        # Arbitration ladder
        "ARB_K1": {"K_arbitration": 1},
        "ARB_K2": {"K_arbitration": 2},
        "ARB_K5": {"K_arbitration": 5},
        "ARB_K10": {"K_arbitration": 10}
    }
    
    df_ladder = run_batch(ladder_configs)
    ladder_csv = os.path.join(OUT_DIR, "COMPONENT_RATE_BOUNDARIES.csv")
    df_ladder.to_csv(ladder_csv, index=False)
    print(f"Wrote {ladder_csv}")
    
    # 3. Multirate Full Policy Candidates on DEV (Max 6)
    policy_configs = {
        "D0": {},
        # MR1_A: Fast sensing, moderate adaptation
        "MR1_A": {
            "K_probe": 2, "K_cand_obs": 2, "K_cand_learn": 5,
            "K_rec_forward": 1, "K_rec_learn": 5, "K_arbitration": 5
        },
        # MR1_B: Budget-optimized Multirate (targeting <= 100 FP)
        "MR1_B": {
            "K_probe": 5, "K_cand_obs": 5, "K_cand_learn": 10,
            "K_rec_forward": 1, "K_rec_learn": 10, "K_arbitration": 10
        },
        # MR1_C: Balanced Multirate
        "MR1_C": {
            "K_probe": 2, "K_cand_obs": 5, "K_cand_learn": 10,
            "K_rec_forward": 1, "K_rec_learn": 10, "K_arbitration": 5
        },
        # MR2: Data-Selective Adaptation (gated by innovation)
        "MR2": {
            "K_probe": 5, "K_cand_obs": 2, "K_cand_learn": 1,
            "K_rec_forward": 1, "K_rec_learn": 1, "K_arbitration": 5,
            "router_type": "DATA_SELECTIVE", "innov_gamma": 0.010
        },
        # MR3: Temporal Evidence Routed Multirate (residual serial correlation)
        "MR3": {
            "K_probe": 5, "K_cand_obs": 5, "K_cand_learn": 10,
            "K_rec_forward": 1, "K_rec_learn": 10, "K_arbitration": 10,
            "router_type": "TEMPORAL_ROUTER", "temporal_theta": 0.15, "heartbeat_H": 100
        }
    }
    
    df_policies = run_batch(policy_configs)
    policy_csv = os.path.join(OUT_DIR, "MULTIRATE_DEV_RESULTS.csv")
    df_policies.to_csv(policy_csv, index=False)
    print(f"Wrote {policy_csv}")
    
    print("DEV screening and candidate evaluation successfully finished.")

if __name__ == "__main__":
    main()
