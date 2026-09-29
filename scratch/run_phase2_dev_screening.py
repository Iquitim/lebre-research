#!/usr/bin/env python3
"""
run_phase2_dev_screening.py

Executes Phase 2 (Candidate Screening on DEV seeds 1801..1810) across all 14 benchmark tasks:
- R0_CONTINUOUS (Continuous Reference)
- C1_SPARSE_FRONTIER (H=16, B=2)
- C1_SPARSE_FRONTIER (H=16, B=4)
- C1_SPARSE_FRONTIER (H=32, B=2)
- C1_SPARSE_FRONTIER (H=32, B=4)
- C2_HIERARCHICAL (Negative Control)

Outputs:
- SPARSE_FRONTIER_DEV_RESULTS.csv
- HIERARCHICAL_SEARCH_DEV_RESULTS.csv
- SEARCH_POLICY_DEV_COMPARISON.csv
"""

import os
import sys
import time
import math
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS
from scratch.run_v02_correlation_search_compaction import (
    run_single_simulation,
    ALL_160_PAIRS,
    TASK_TRUE_LAGS
)

AUDIT_DIR = "experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01"
DEV_SEEDS = list(range(1801, 1811)) # N=10

CONFIGS = [
    ("R0_CONTINUOUS", {"model_type": "R0_CONTINUOUS"}),
    ("C1_H16_B2", {"model_type": "C1_SPARSE_FRONTIER", "H_capacity": 16, "B_batch": 2}),
    ("C1_H16_B4", {"model_type": "C1_SPARSE_FRONTIER", "H_capacity": 16, "B_batch": 4}),
    ("C1_H32_B2", {"model_type": "C1_SPARSE_FRONTIER", "H_capacity": 32, "B_batch": 2}),
    ("C1_H32_B4", {"model_type": "C1_SPARSE_FRONTIER", "H_capacity": 32, "B_batch": 4}),
    ("C2_HIERARCHICAL", {"model_type": "C2_HIERARCHICAL"}),
]

def worker(args):
    cfg_name, task_id, seed, kwargs = args
    res = run_single_simulation(task_id, seed=seed, **kwargs)
    # Strip heavy dicts
    flat_res = {k: v for k, v in res.items() if not isinstance(v, (dict, list))}
    flat_res['candidate_id'] = cfg_name
    return flat_res

def main():
    print("=" * 70)
    print("EXECUTING PHASE 2 CANDIDATE DEV SCREENING (SEEDS 1801..1810, 14 TASKS)")
    print("=" * 70)
    
    work_items = []
    for cfg_name, kwargs in CONFIGS:
        for s in DEV_SEEDS:
            for t in BENCHMARK_TASKS:
                work_items.append((cfg_name, t, s, kwargs))
                
    print(f"Total screening simulation runs: {len(work_items)}")
    
    t0 = time.time()
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(worker, work_items))
    t1 = time.time()
    print(f"All {len(results)} runs completed in {t1 - t0:.2f}s!")
    
    df_all = pd.DataFrame(results)
    
    # Also load R1 DEV runs from Phase 0/1 if available, or run R1
    # Let's run R1 to have identical aligned structure
    print("Running R1 aligned baseline on DEV...")
    r1_items = [("R1_DENSE_MULTIRATE", t, s, {"model_type": "R1_DENSE_MULTIRATE"}) for s in DEV_SEEDS for t in BENCHMARK_TASKS]
    with ProcessPoolExecutor() as executor:
        r1_results = list(executor.map(worker, r1_items))
    df_r1 = pd.DataFrame(r1_results)
    
    df_full = pd.concat([df_all, df_r1], ignore_index=True)
    
    # 1. SPARSE_FRONTIER_DEV_RESULTS.csv
    df_sparse = df_full[df_full['candidate_id'].str.startswith("C1_")].copy()
    sparse_path = os.path.join(AUDIT_DIR, "SPARSE_FRONTIER_DEV_RESULTS.csv")
    df_sparse.to_csv(sparse_path, index=False)
    print(f"Wrote {sparse_path} ({len(df_sparse)} rows)")
    
    # 2. HIERARCHICAL_SEARCH_DEV_RESULTS.csv
    df_hier = df_full[df_full['candidate_id'] == "C2_HIERARCHICAL"].copy()
    hier_path = os.path.join(AUDIT_DIR, "HIERARCHICAL_SEARCH_DEV_RESULTS.csv")
    df_hier.to_csv(hier_path, index=False)
    print(f"Wrote {hier_path} ({len(df_hier)} rows)")
    
    # 3. SEARCH_POLICY_DEV_COMPARISON.csv
    # Compute R0 mean NMSE per (task, seed) as benchmark reference
    df_r0 = df_full[df_full['candidate_id'] == "R0_CONTINUOUS"].set_index(['task_id', 'seed'])['nmse']
    
    # Merge R0 reference into each run to get paired delta NMSE
    df_full_indexed = df_full.set_index(['task_id', 'seed'])
    df_full_indexed['nmse_r0'] = df_r0
    df_full_indexed['delta_nmse_vs_r0'] = df_full_indexed['nmse'] - df_full_indexed['nmse_r0']
    df_full_indexed = df_full_indexed.reset_index()
    
    comp_rows = []
    pure_lag_tasks = ["I3_Single_Exact_Delay", "I4_Multi_Sparse_Delay", "I5_Moving_Delay_Support", "I8_Quiescent_Discrete_Delay"]
    switching_tasks = ["I11_Continuous_Abrupt_Switch", "I12_Discrete_Abrupt_Switch", "I13_Intermittent_Regime_Switch", "I14_Orthogonal_Regime_Switch"]
    
    for cid, grp in df_full_indexed.groupby('candidate_id'):
        mean_nmse = grp['nmse'].mean()
        mean_delta_r0 = grp['delta_nmse_vs_r0'].mean()
        std_delta_r0 = grp['delta_nmse_vs_r0'].std()
        ci95_delta_r0 = 1.96 * (std_delta_r0 / math.sqrt(len(grp)))
        
        # Pure lag subset delta NMSE
        pure_grp = grp[grp['task_id'].isin(pure_lag_tasks)]
        pure_delta_r0 = pure_grp['delta_nmse_vs_r0'].mean()
        
        # Switching recovery latency
        switch_grp = grp[grp['task_id'].isin(switching_tasks)]
        mean_switch_lat = switch_grp['switch_latency'].dropna().mean()
        
        # Resource metrics
        mean_total_fp = grp['total_fp_mean'].mean()
        mean_search_fp = grp['search_probe_fp'].mean()
        mean_desc_fp = grp['candidate_descendant_fp'].mean()
        mean_failed_fp = grp['failed_probation_fp'].mean()
        mean_regret = grp['search_regret_mean'].mean()
        mean_silence = grp['mean_silence_steps'].mean()
        max_silence = grp['max_silence_steps'].max()
        ram_bytes = grp['search_persistent_bytes'].iloc[0]
        
        # Recall metrics
        visit_rec = grp['true_visit_recall'].mean()
        cand_rec = grp['true_cand_recall'].mean()
        prom_rec = grp['true_prom_recall'].mean()
        
        # Candidate status
        if cid == "R0_CONTINUOUS":
            status = "REFERENCE_CONTINUOUS"
        elif cid == "R1_DENSE_MULTIRATE":
            status = "REFERENCE_MULTIRATE"
        elif cid == "C2_HIERARCHICAL":
            status = "DISQUALIFIED_NEGATIVE_CONTROL"
        elif mean_total_fp <= 100.0 and mean_delta_r0 < 0.0100 and pure_delta_r0 <= 0.0150:
            status = "QUALIFIED_CANDIDATE"
        else:
            status = "REJECTED_UNDERPERFORMING"
            
        comp_rows.append({
            'candidate_id': cid,
            'status': status,
            'mean_nmse': mean_nmse,
            'delta_nmse_vs_r0_mean': mean_delta_r0,
            'delta_nmse_vs_r0_ci95_half': ci95_delta_r0,
            'delta_nmse_vs_r0_ci95_upper': mean_delta_r0 + ci95_delta_r0,
            'pure_lag_delta_nmse': pure_delta_r0,
            'mean_switch_latency': mean_switch_lat,
            'total_fp_mean': mean_total_fp,
            'search_probe_fp_mean': mean_search_fp,
            'descendant_probation_fp_mean': mean_desc_fp,
            'failed_probation_fp_mean': mean_failed_fp,
            'mean_search_regret': mean_regret,
            'mean_silence_steps': mean_silence,
            'max_silence_steps': max_silence,
            'search_ram_bytes': ram_bytes,
            'true_delay_visit_recall': visit_rec,
            'true_delay_cand_recall': cand_rec,
            'true_delay_prom_recall': prom_rec
        })
        
    df_comp = pd.DataFrame(comp_rows).sort_values(by='delta_nmse_vs_r0_mean')
    comp_path = os.path.join(AUDIT_DIR, "SEARCH_POLICY_DEV_COMPARISON.csv")
    df_comp.to_csv(comp_path, index=False)
    print(f"Wrote {comp_path}")
    print("\nPolicy Comparison Summary:")
    print(df_comp[['candidate_id', 'status', 'delta_nmse_vs_r0_mean', 'total_fp_mean', 'search_probe_fp_mean', 'true_delay_prom_recall', 'search_ram_bytes']])

if __name__ == '__main__':
    main()
