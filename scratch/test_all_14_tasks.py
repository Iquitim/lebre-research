#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scratch.run_v02_integration_experiments import run_single_simulation
from scratch.bench_v02_integration import BENCHMARK_TASKS

print(f"Testing all {len(BENCHMARK_TASKS)} tasks on T3 (Seed 1301):")
print("-" * 95)
for t_id in BENCHMARK_TASKS:
    res = run_single_simulation(t_id, seed=1301, topology="T3", total_steps=6000)
    exp = res["expected_class"]
    mod = res["modal_state"]
    nmse = res["nmse"]
    lags = res["mean_active_lags"]
    rec = res["mean_rec_active"]
    flops = res["live_flops_mean"]
    print(f"{t_id:40s} | Exp: {exp:10s} | Mod: {mod:10s} | NMSE: {nmse:.4f} | Lags: {lags:.2f} | Rec: {rec:.2f} | Live FLOPs: {flops:.1f}")
