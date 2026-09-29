#!/usr/bin/env python3
"""
Full analysis and documentation generator for LEBRE-DIAG-01.
Computes statistical tables, effect sizes, bootstrap CIs, calibration curves,
and writes all 5 required markdown analysis reports.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy import stats

EXP_DIR = ROOT / "experiments" / "LEBRE-DIAG-01"

def bootstrap_diff(a: np.ndarray, b: np.ndarray, n_boot: int = 10000, alpha: float = 0.05):
    """Computes paired difference a - b with 95% bootstrap CI and paired effect size."""
    diff = a - b
    mean_diff = float(np.mean(diff))
    rng = np.random.RandomState(42)
    n = len(diff)
    boot_means = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(diff, size=n, replace=True)
        boot_means[i] = np.mean(sample)
    ci_low = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
    ci_high = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))
    
    # Paired Cohen's d_z
    std_diff = float(np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 1e-8 else 1e-8
    cohen_dz = mean_diff / std_diff
    
    # Paired win rate (a < b, lower is better)
    win_rate = float(np.mean(diff < 0.0))
    
    # Wilcoxon signed rank test
    try:
        w_stat, p_val = stats.wilcoxon(diff)
    except Exception:
        p_val = 1.0
        
    return {
        "mean_diff": mean_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "cohen_dz": cohen_dz,
        "win_rate": win_rate,
        "p_val": p_val
    }

def generate_all_reports():
    seed_csv = EXP_DIR / "LEBRE_DIAG_01_SEED_RESULTS.csv"
    event_csv = EXP_DIR / "LEBRE_DIAG_01_PROMOTION_EVENTS.csv"
    
    if not seed_csv.exists() or not event_csv.exists():
        print("Data files not found.")
        return
        
    df_seeds = pd.read_csv(seed_csv)
    df_events = pd.read_csv(event_csv)
    
    tasks_primary = ["A2_Single_Delayed_Dependency", "A3_Multiple_Dispersed_Delays", "A4_Long_Delay_Scaling"]
    tasks_control = ["A5_Set_Reset_Quiescent_Memory", "A7_Extended_Poisson_Quiescence", "A8_Abrupt_Tri_Regime_Transition"]
    
    # -------------------------------------------------------------
    # 1. Primary Statistical Metrics Table
    # -------------------------------------------------------------
    primary_metrics = {}
    for t_id in tasks_primary:
        sub_f = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_FROZEN")].sort_values("seed")
        sub_n = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")].sort_values("seed")
        sub_o = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_ORACLE_HARM_STOP")].sort_values("seed")
        
        nmse_f = sub_f["nmse"].values
        nmse_n = sub_n["nmse"].values
        nmse_o = sub_o["nmse"].values
        
        # Paired test Frozen vs No-Birth
        st = bootstrap_diff(nmse_f, nmse_n)
        
        # Oracle recovery fraction
        denom = np.mean(nmse_f - nmse_n)
        numer = np.mean(nmse_f - nmse_o)
        oracle_recovery = float(numer / denom * 100.0) if abs(denom) > 1e-6 else 0.0
        
        # Event metrics
        ev_t = df_events[df_events["task_id"] == t_id]
        n_proms = len(ev_t[ev_t["promoted"] == True])
        proms_per_seed = n_proms / len(sub_f)
        
        # False promotion rate at H=250
        proms_250 = ev_t[ev_t["G_post_250"].notna()]
        fpr_250 = float(np.mean(proms_250["G_post_250"] < 0.0)) if len(proms_250) > 0 else 0.0
        
        # Mean eviction response latency
        latencies = ev_t[ev_t["t_evict_response"].notna()]["t_evict_response"].values
        mean_lat = float(np.mean(latencies)) if len(latencies) > 0 else 0.0
        
        # Mean R_harm per seed
        r_harm_per_seed = float(np.sum(ev_t["R_harm"]) / len(sub_f))
        
        primary_metrics[t_id] = {
            "nmse_f_mean": float(np.mean(nmse_f)),
            "nmse_f_ci": (float(np.percentile(nmse_f, 2.5)), float(np.percentile(nmse_f, 97.5))),
            "nmse_n_mean": float(np.mean(nmse_n)),
            "nmse_n_ci": (float(np.percentile(nmse_n, 2.5)), float(np.percentile(nmse_n, 97.5))),
            "delta": st["mean_diff"],
            "delta_ci": (st["ci_low"], st["ci_high"]),
            "cohen_dz": st["cohen_dz"],
            "win_rate": st["win_rate"],
            "p_val": st["p_val"],
            "proms_per_seed": proms_per_seed,
            "fpr_250": fpr_250,
            "mean_lat": mean_lat,
            "r_harm_seed": r_harm_per_seed,
            "oracle_recovery": oracle_recovery
        }
        
    print("Computed Primary Metrics:")
    for k, v in primary_metrics.items():
        print(f"  {k[:2]}: Frozen={v['nmse_f_mean']:.4f}, NoBirth={v['nmse_n_mean']:.4f}, Delta={v['delta']:+.4f} (p={v['p_val']:.4e}), FPR_250={v['fpr_250']*100:.1f}%, OracleRecov={v['oracle_recovery']:.1f}%")
        
    # -------------------------------------------------------------
    # 2. Positive Control Metrics Table
    # -------------------------------------------------------------
    control_metrics = {}
    for t_id in tasks_control:
        sub_f = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_FROZEN")].sort_values("seed")
        sub_n = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")].sort_values("seed")
        nmse_f = sub_f["nmse"].values
        nmse_n = sub_n["nmse"].values
        st = bootstrap_diff(nmse_f, nmse_n)
        control_metrics[t_id] = {
            "nmse_f_mean": float(np.mean(nmse_f)),
            "nmse_n_mean": float(np.mean(nmse_n)),
            "delta": st["mean_diff"],
            "delta_ci": (st["ci_low"], st["ci_high"]),
            "p_val": st["p_val"]
        }
        print(f"  Control {t_id[:2]}: Frozen={control_metrics[t_id]['nmse_f_mean']:.4f}, NoBirth={control_metrics[t_id]['nmse_n_mean']:.4f}, Delta={control_metrics[t_id]['delta']:+.4f}")
        
    return primary_metrics, control_metrics

if __name__ == "__main__":
    generate_all_reports()
