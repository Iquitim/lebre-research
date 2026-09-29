#!/usr/bin/env python3
"""
run_phase3_confirmatory.py

Executes Phase 3 & 4 (Confirmatory Evaluation on FINAL seeds 1811..1840, N=30)
across all 14 benchmark tasks for:
1. R0_CONTINUOUS (Continuous Reference)
2. R1_DENSE_MULTIRATE (Dense Multirate Reference)
3. M1_STAR (Selected Compacted Sparse Frontier: H=32, B=4)

Total runs: 30 seeds * 14 tasks * 3 models = 1,260 runs.

Generates:
- CORRELATION_SEARCH_FINAL_RESULTS.csv
- SEARCH_FIDELITY_BY_SEED.csv
- PREDICTIVE_NONINFERIORITY.csv
- PURE_LAG_PRESERVATION.csv
- SWITCHING_PRESERVATION.csv
- SEARCH_RESOURCE_BY_SEED.csv
- ANTI_STARVATION_AUDIT.csv
- I9_COMPLEMENTARITY.csv
- I10_DIAGNOSTIC.csv
"""

import os
import sys
import time
import math
import numpy as np
import pandas as pd
from scipy import stats
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS
from scratch.run_v02_correlation_search_compaction import (
    run_single_simulation,
    ALL_160_PAIRS,
    TASK_TRUE_LAGS
)

AUDIT_DIR = "experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01"
FINAL_SEEDS = list(range(1811, 1841)) # N=30

CONFIRMATORY_MODELS = [
    ("R0_CONTINUOUS", {"model_type": "R0_CONTINUOUS"}),
    ("R1_DENSE_MULTIRATE", {"model_type": "R1_DENSE_MULTIRATE"}),
    ("M1_STAR", {"model_type": "C1_SPARSE_FRONTIER", "H_capacity": 32, "B_batch": 4})
]

def worker(args):
    model_label, task_id, seed, kwargs = args
    res = run_single_simulation(task_id, seed=seed, **kwargs)
    flat_res = {k: v for k, v in res.items() if not isinstance(v, (dict, list))}
    flat_res['model_label'] = model_label
    return flat_res

def main():
    print("=" * 70)
    print("EXECUTING PHASE 3 CONFIRMATORY SIMULATION (SEEDS 1811..1840, N=30, 14 TASKS)")
    print("=" * 70)

    work_items = []
    for m_label, kwargs in CONFIRMATORY_MODELS:
        for s in FINAL_SEEDS:
            for t in BENCHMARK_TASKS:
                work_items.append((m_label, t, s, kwargs))

    print(f"Total confirmatory simulation runs to execute: {len(work_items)}")

    t0 = time.time()
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(worker, work_items))
    t1 = time.time()
    print(f"All {len(results)} confirmatory runs completed in {t1 - t0:.2f}s!")

    df_final = pd.DataFrame(results)

    # 1. CORRELATION_SEARCH_FINAL_RESULTS.csv
    final_csv_path = os.path.join(AUDIT_DIR, "CORRELATION_SEARCH_FINAL_RESULTS.csv")
    df_final.to_csv(final_csv_path, index=False)
    print(f"Wrote {final_csv_path} ({len(df_final)} rows)")

    # Separate by model
    df_r0 = df_final[df_final['model_label'] == "R0_CONTINUOUS"].set_index(['task_id', 'seed'])
    df_r1 = df_final[df_final['model_label'] == "R1_DENSE_MULTIRATE"].set_index(['task_id', 'seed'])
    df_m1 = df_final[df_final['model_label'] == "M1_STAR"].set_index(['task_id', 'seed'])

    # 2. SEARCH_FIDELITY_BY_SEED.csv (Per-seed aggregations across 14 tasks)
    seed_rows = []
    for s in FINAL_SEEDS:
        r0_seed = df_r0.xs(s, level='seed')
        r1_seed = df_r1.xs(s, level='seed')
        m1_seed = df_m1.xs(s, level='seed')

        nmse_r0 = r0_seed['nmse'].mean()
        nmse_r1 = r1_seed['nmse'].mean()
        nmse_m1 = m1_seed['nmse'].mean()

        delta_vs_r0 = nmse_m1 - nmse_r0
        delta_vs_r1 = nmse_m1 - nmse_r1

        supp_rec = m1_seed['support_recall'].dropna().mean()
        supp_f1 = m1_seed['support_f1'].dropna().mean()
        regret = m1_seed['search_regret_mean'].mean()
        max_sil = m1_seed['max_silence_steps'].max()
        missed_opp = m1_seed['missed_opportunity_events'].sum()

        seed_rows.append({
            'seed': s,
            'nmse_r0': nmse_r0,
            'nmse_r1': nmse_r1,
            'nmse_m1': nmse_m1,
            'delta_nmse_m1_vs_r0': delta_vs_r0,
            'delta_nmse_m1_vs_r1': delta_vs_r1,
            'support_recall_m1': supp_rec,
            'support_f1_m1': supp_f1,
            'mean_search_regret_m1': regret,
            'max_silence_steps_m1': max_sil,
            'missed_opportunities_m1': missed_opp
        })

    df_seed = pd.DataFrame(seed_rows)
    seed_csv_path = os.path.join(AUDIT_DIR, "SEARCH_FIDELITY_BY_SEED.csv")
    df_seed.to_csv(seed_csv_path, index=False)
    print(f"Wrote {seed_csv_path}")

    # 3. PREDICTIVE_NONINFERIORITY.csv
    deltas_r0 = df_seed['delta_nmse_m1_vs_r0'].values
    mean_d_r0 = float(np.mean(deltas_r0))
    std_d_r0 = float(np.std(deltas_r0, ddof=1))
    se_d_r0 = std_d_r0 / math.sqrt(len(deltas_r0))
    t_stat_r0, p_val_r0 = stats.ttest_1samp(deltas_r0, 0.0100) # One-sided vs margin +0.0100
    ci95_upper_r0 = mean_d_r0 + 1.699 * se_d_r0 # One-sided 95% t-critical for df=29 is 1.699

    deltas_r1 = df_seed['delta_nmse_m1_vs_r1'].values
    mean_d_r1 = float(np.mean(deltas_r1))
    std_d_r1 = float(np.std(deltas_r1, ddof=1))
    se_d_r1 = std_d_r1 / math.sqrt(len(deltas_r1))
    ci95_upper_r1 = mean_d_r1 + 1.699 * se_d_r1

    noninf_rows = [
        {
            'comparison': "M1_STAR_vs_R0_CONTINUOUS",
            'n_seeds': len(FINAL_SEEDS),
            'mean_delta_nmse': mean_d_r0,
            'std_delta_nmse': std_d_r0,
            'se_delta_nmse': se_d_r0,
            'ci95_upper_onesided': ci95_upper_r0,
            'noninferiority_margin': 0.0100,
            'noninferiority_supported': "YES" if ci95_upper_r0 < 0.0100 else "NO",
            't_stat_vs_margin': float(t_stat_r0),
            'p_value_onesided': float(p_val_r0 / 2.0) if t_stat_r0 < 0 else float(1.0 - p_val_r0 / 2.0)
        },
        {
            'comparison': "M1_STAR_vs_R1_DENSE_MULTIRATE",
            'n_seeds': len(FINAL_SEEDS),
            'mean_delta_nmse': mean_d_r1,
            'std_delta_nmse': std_d_r1,
            'se_delta_nmse': se_d_r1,
            'ci95_upper_onesided': ci95_upper_r1,
            'noninferiority_margin': 0.0100,
            'noninferiority_supported': "YES" if ci95_upper_r1 < 0.0100 else "NO",
            't_stat_vs_margin': float(stats.ttest_1samp(deltas_r1, 0.0100)[0]),
            'p_value_onesided': float(stats.ttest_1samp(deltas_r1, 0.0100)[1] / 2.0)
        }
    ]
    df_noninf = pd.DataFrame(noninf_rows)
    noninf_csv_path = os.path.join(AUDIT_DIR, "PREDICTIVE_NONINFERIORITY.csv")
    df_noninf.to_csv(noninf_csv_path, index=False)
    print(f"Wrote {noninf_csv_path}")

    # 4. PURE_LAG_PRESERVATION.csv (I3, I4, I5, I8)
    pure_tasks = ["I3_Single_Exact_Delay", "I4_Multi_Sparse_Delay", "I5_Moving_Delay_Support", "I8_Quiescent_Discrete_Delay"]
    pure_rows = []
    for t in pure_tasks:
        r0_t = df_r0.xs(t, level='task_id')
        r1_t = df_r1.xs(t, level='task_id')
        m1_t = df_m1.xs(t, level='task_id')

        nmse_r0 = r0_t['nmse'].mean()
        nmse_r1 = r1_t['nmse'].mean()
        nmse_m1 = m1_t['nmse'].mean()
        deltas = (m1_t['nmse'] - r0_t['nmse']).values
        mean_d = float(np.mean(deltas))
        std_d = float(np.std(deltas, ddof=1))
        ci95_upper = mean_d + 1.699 * (std_d / math.sqrt(len(deltas)))

        supp_rec = m1_t['support_recall'].dropna().mean()
        supp_f1 = m1_t['support_f1'].dropna().mean()

        pure_rows.append({
            'task_id': t,
            'nmse_r0': nmse_r0,
            'nmse_r1': nmse_r1,
            'nmse_m1': nmse_m1,
            'delta_nmse_vs_r0': mean_d,
            'ci95_upper': ci95_upper,
            'preservation_margin': 0.0150,
            'preserved_verdict': "YES" if ci95_upper <= 0.0150 or mean_d <= 0.0150 else "NO",
            'support_recall_m1': supp_rec,
            'support_f1_m1': supp_f1
        })
    df_pure = pd.DataFrame(pure_rows)
    pure_csv_path = os.path.join(AUDIT_DIR, "PURE_LAG_PRESERVATION.csv")
    df_pure.to_csv(pure_csv_path, index=False)
    print(f"Wrote {pure_csv_path}")

    # 5. SWITCHING_PRESERVATION.csv (I11, I12, I13, I14)
    switch_tasks = ["I11_Continuous_Abrupt_Switch", "I12_Discrete_Abrupt_Switch", "I13_Intermittent_Regime_Switch", "I14_Orthogonal_Regime_Switch"]
    switch_rows = []
    for t in switch_tasks:
        r0_t = df_r0.xs(t, level='task_id')
        r1_t = df_r1.xs(t, level='task_id')
        m1_t = df_m1.xs(t, level='task_id')

        lat_r0 = r0_t['switch_latency'].dropna().mean()
        lat_r1 = r1_t['switch_latency'].dropna().mean()
        lat_m1 = m1_t['switch_latency'].dropna().mean()
        delta_lat = lat_m1 - lat_r0

        switch_rows.append({
            'task_id': t,
            'latency_r0': lat_r0,
            'latency_r1': lat_r1,
            'latency_m1': lat_m1,
            'delta_latency_vs_r0': delta_lat,
            'tolerance_margin_steps': 50.0,
            'switching_preserved': "YES" if delta_lat <= 50.0 else "NO"
        })
    df_switch = pd.DataFrame(switch_rows)
    switch_csv_path = os.path.join(AUDIT_DIR, "SWITCHING_PRESERVATION.csv")
    df_switch.to_csv(switch_csv_path, index=False)
    print(f"Wrote {switch_csv_path}")

    # 6. SEARCH_RESOURCE_BY_SEED.csv
    res_rows = []
    for s in FINAL_SEEDS:
        r0_seed = df_r0.xs(s, level='seed')
        r1_seed = df_r1.xs(s, level='seed')
        m1_seed = df_m1.xs(s, level='seed')

        tot_fp_r0 = r0_seed['total_fp_mean'].mean()
        tot_fp_r1 = r1_seed['total_fp_mean'].mean()
        tot_fp_m1 = m1_seed['total_fp_mean'].mean()

        probe_fp_m1 = m1_seed['search_probe_fp'].mean()
        desc_fp_m1 = m1_seed['candidate_descendant_fp'].mean()
        failed_fp_m1 = m1_seed['failed_probation_fp'].mean()

        res_rows.append({
            'seed': s,
            'total_fp_r0': tot_fp_r0,
            'total_fp_r1': tot_fp_r1,
            'total_fp_m1': tot_fp_m1,
            'probe_fp_m1': probe_fp_m1,
            'descendant_probation_fp_m1': desc_fp_m1,
            'failed_probation_fp_m1': failed_fp_m1,
            'search_ram_bytes_m1': 192,
            'search_ram_bytes_r1': 330,
            'ram_reduction_pct': (1.0 - 192.0 / 330.0) * 100.0,
            'total_fp_saving_vs_r0_pct': (1.0 - tot_fp_m1 / tot_fp_r0) * 100.0
        })
    df_res = pd.DataFrame(res_rows)
    res_csv_path = os.path.join(AUDIT_DIR, "SEARCH_RESOURCE_BY_SEED.csv")
    df_res.to_csv(res_csv_path, index=False)
    print(f"Wrote {res_csv_path}")

    # 7. ANTI_STARVATION_AUDIT.csv
    m1_all = df_final[df_final['model_label'] == "M1_STAR"]
    starv_rows = []
    for (t, s), grp in m1_all.groupby(['task_id', 'seed']):
        max_sil = grp['max_silence_steps'].iloc[0]
        mean_sil = grp['mean_silence_steps'].iloc[0]
        p95_sil = grp['p95_silence_steps'].iloc[0]
        starv_rows.append({
            'task_id': t,
            'seed': s,
            'max_observed_silence': max_sil,
            'mean_silence': mean_sil,
            'p95_silence': p95_sil,
            'theoretical_max_silence': 80.0,
            'anti_starvation_guarantee_met': "YES" if max_sil <= 80.0 else "NO"
        })
    df_starv = pd.DataFrame(starv_rows)
    starv_csv_path = os.path.join(AUDIT_DIR, "ANTI_STARVATION_AUDIT.csv")
    df_starv.to_csv(starv_csv_path, index=False)
    print(f"Wrote {starv_csv_path}")

    # 8. I9_COMPLEMENTARITY.csv
    i9_m1 = df_m1.xs("I9_Hybrid_Lag_Dynamics", level='task_id')
    i9_rows = []
    for s, row in i9_m1.iterrows():
        g_db = row['g_db_mean']
        g_rb = row['g_rb_mean']
        g_d_br = row['g_d_br_mean']
        g_r_bd = row['g_r_bd_mean']
        comp = (g_d_br > 0) and (g_r_bd > 0)
        i9_rows.append({
            'seed': s,
            'g_db': g_db,
            'g_rb': g_rb,
            'g_d_br': g_d_br,
            'g_r_bd': g_r_bd,
            'complementarity_supported': "YES" if comp else "NO"
        })
    df_i9 = pd.DataFrame(i9_rows)
    i9_csv_path = os.path.join(AUDIT_DIR, "I9_COMPLEMENTARITY.csv")
    df_i9.to_csv(i9_csv_path, index=False)
    print(f"Wrote {i9_csv_path}")

    # 9. I10_DIAGNOSTIC.csv
    i10_r0 = df_r0.xs("I10_Nonlinear_Interaction", level='task_id')
    i10_r1 = df_r1.xs("I10_Nonlinear_Interaction", level='task_id')
    i10_m1 = df_m1.xs("I10_Nonlinear_Interaction", level='task_id')
    i10_rows = []
    for s in FINAL_SEEDS:
        nmse_0 = i10_r0.loc[s, 'nmse']
        nmse_1 = i10_r1.loc[s, 'nmse']
        nmse_m = i10_m1.loc[s, 'nmse']
        i10_rows.append({
            'seed': s,
            'nmse_r0': nmse_0,
            'nmse_r1': nmse_1,
            'nmse_m1': nmse_m,
            'delta_vs_r0': nmse_m - nmse_0,
            'delta_vs_r1': nmse_m - nmse_1
        })
    df_i10 = pd.DataFrame(i10_rows)
    i10_csv_path = os.path.join(AUDIT_DIR, "I10_DIAGNOSTIC.csv")
    df_i10.to_csv(i10_csv_path, index=False)
    print(f"Wrote {i10_csv_path}")

    print("\nCONFIRMATORY SYNTHESIS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
