#!/usr/bin/env python3
"""
audit_pareto_recomputation.py:
Forensic recomputation of Pareto dominance relations under Live-Path Vector
and Full-Online Vector, both aggregated and per-task.
"""

import csv
from pathlib import Path
import numpy as np
import pandas as pd

PARENT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01")
AUDIT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01")

seed_csv = PARENT_DIR / "LEBRE_V0_2_SEED_RESULTS.csv"
df = pd.read_csv(seed_csv)

# Aggregate across all 14 tasks and 30 seeds
topos = ["T1", "T1R", "T2", "T3", "O_ALL"]

# Compute aggregates per topology
agg_data = {}
for topo in topos:
    sub = df[df["topology"] == topo]
    nmse = float(sub["nmse"].mean())
    live_fp = float(sub["live_flops_mean"].mean())
    shadow_fp = float(sub["shadow_flops_mean"].mean())
    total_fp = live_fp + shadow_fp
    int_ops = float(sub["int_ops_mean"].mean())
    traffic = float(sub["bytes_moved_mean"].mean())
    ram = float(sub["persistent_bytes"].mean())
    agg_data[topo] = {
        "NMSE": nmse,
        "LIVE_FP": live_fp,
        "SHADOW_FP": shadow_fp,
        "TOTAL_FP": total_fp,
        "INT_OPS": int_ops,
        "TRAFFIC": traffic,
        "RAM": ram
    }

print("--- AGGREGATE RESOURCE VECTORS (30 SEEDS, 14 TASKS) ---")
for t, v in agg_data.items():
    print(f"{t:6s} | NMSE: {v['NMSE']:.4f} | Live FP: {v['LIVE_FP']:.1f} | Shadow FP: {v['SHADOW_FP']:.1f} | Total FP: {v['TOTAL_FP']:.1f} | Int Ops: {v['INT_OPS']:.1f} | Traffic: {v['TRAFFIC']:.1f} | RAM: {v['RAM']:.0f}B")

# Helper function to test Pareto dominance for minimization
def check_pareto_dominance(A: dict, B: dict, objectives: list):
    # A dominates B iff for all m: A[m] <= B[m] and exists m: A[m] < B[m]
    better_count = 0
    worse_count = 0
    for obj in objectives:
        if A[obj] < B[obj] - 1e-6:
            better_count += 1
        elif A[obj] > B[obj] + 1e-6:
            worse_count += 1
            
    if better_count > 0 and worse_count == 0:
        return "A_DOMINATES_B"
    elif worse_count > 0 and better_count == 0:
        return "B_DOMINATES_A"
    else:
        return "NON_DOMINATED_TRADEOFF"

live_objs = ["NMSE", "LIVE_FP", "RAM"]
full_objs = ["NMSE", "TOTAL_FP", "INT_OPS", "TRAFFIC", "RAM"]

pareto_rows = []

# Aggregate pairwise comparisons of T3 against all others
for comp in ["T1", "T1R", "T2", "O_ALL"]:
    rel_live = check_pareto_dominance(agg_data["T3"], agg_data[comp], live_objs)
    rel_full = check_pareto_dominance(agg_data["T3"], agg_data[comp], full_objs)
    
    pareto_rows.append({
        "LEVEL": "AGGREGATE_ALL_TASKS",
        "PAIR": f"T3_vs_{comp}",
        "T3_NMSE": f"{agg_data['T3']['NMSE']:.4f}",
        "COMP_NMSE": f"{agg_data[comp]['NMSE']:.4f}",
        "T3_LIVE_FP": f"{agg_data['T3']['LIVE_FP']:.1f}",
        "COMP_LIVE_FP": f"{agg_data[comp]['LIVE_FP']:.1f}",
        "T3_TOTAL_FP": f"{agg_data['T3']['TOTAL_FP']:.1f}",
        "COMP_TOTAL_FP": f"{agg_data[comp]['TOTAL_FP']:.1f}",
        "T3_RAM": f"{agg_data['T3']['RAM']:.0f}",
        "COMP_RAM": f"{agg_data[comp]['RAM']:.0f}",
        "LIVE_VECTOR_RELATION": rel_live,
        "FULL_ONLINE_VECTOR_RELATION": rel_full
    })

# Per-task pairwise comparisons
tasks = sorted(df["task_id"].unique())
for task_id in tasks:
    sub_task = df[df["task_id"] == task_id]
    t3_sub = sub_task[sub_task["topology"] == "T3"]
    t3_dict = {
        "NMSE": float(t3_sub["nmse"].mean()),
        "LIVE_FP": float(t3_sub["live_flops_mean"].mean()),
        "TOTAL_FP": float(t3_sub["live_flops_mean"].mean() + t3_sub["shadow_flops_mean"].mean()),
        "INT_OPS": float(t3_sub["int_ops_mean"].mean()),
        "TRAFFIC": float(t3_sub["bytes_moved_mean"].mean()),
        "RAM": float(t3_sub["persistent_bytes"].mean())
    }
    
    for comp in ["T1", "T1R", "T2", "O_ALL"]:
        comp_sub = sub_task[sub_task["topology"] == comp]
        comp_dict = {
            "NMSE": float(comp_sub["nmse"].mean()),
            "LIVE_FP": float(comp_sub["live_flops_mean"].mean()),
            "TOTAL_FP": float(comp_sub["live_flops_mean"].mean() + comp_sub["shadow_flops_mean"].mean()),
            "INT_OPS": float(comp_sub["int_ops_mean"].mean()),
            "TRAFFIC": float(comp_sub["bytes_moved_mean"].mean()),
            "RAM": float(comp_sub["persistent_bytes"].mean())
        }
        
        rel_l = check_pareto_dominance(t3_dict, comp_dict, live_objs)
        rel_f = check_pareto_dominance(t3_dict, comp_dict, full_objs)
        
        pareto_rows.append({
            "LEVEL": task_id,
            "PAIR": f"T3_vs_{comp}",
            "T3_NMSE": f"{t3_dict['NMSE']:.4f}",
            "COMP_NMSE": f"{comp_dict['NMSE']:.4f}",
            "T3_LIVE_FP": f"{t3_dict['LIVE_FP']:.1f}",
            "COMP_LIVE_FP": f"{comp_dict['LIVE_FP']:.1f}",
            "T3_TOTAL_FP": f"{t3_dict['TOTAL_FP']:.1f}",
            "COMP_TOTAL_FP": f"{comp_dict['TOTAL_FP']:.1f}",
            "T3_RAM": f"{t3_dict['RAM']:.0f}",
            "COMP_RAM": f"{comp_dict['RAM']:.0f}",
            "LIVE_VECTOR_RELATION": rel_l,
            "FULL_ONLINE_VECTOR_RELATION": rel_f
        })

df_pareto = pd.DataFrame(pareto_rows)
out_csv = AUDIT_DIR / "PARETO_RECOMPUTATION.csv"
df_pareto.to_csv(out_csv, index=False)
print(f"\nWrote {out_csv}")

# Print Aggregate Summary
print("\n--- AGGREGATE PARETO RELATIONS ---")
for r in pareto_rows[:4]:
    print(f"{r['PAIR']:12s} | Live Vector: {r['LIVE_VECTOR_RELATION']:18s} | Full Online Vector: {r['FULL_ONLINE_VECTOR_RELATION']}")
