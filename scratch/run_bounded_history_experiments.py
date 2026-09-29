#!/usr/bin/env python3
"""
run_bounded_history_experiments.py: Simulation Engine for BOUNDED-HISTORY-LAG-INTEGRATION-01.

Evaluates 8 History Providers:
  H0: Exact FP32 Ring
  H1: FP16 Exact Ring
  H2: INT16 Quantized Ring
  H3: INT8 Quantized Ring
  H4: Age-Aware Mixed Precision
  H5_NAIVE: Multirate Ring (Naive Decimation)
  H5_AA: Multirate Ring (Anti-Alias Filtered)
  H7_HIPPO: HiPPO Polynomial Projection (Order 6)

Across 12 Benchmark Tasks:
  Regime A (High-Entropy IID): BH1, BH2, BH3, BH4, BH8, BH9, BH10
  Regime B (Compressible):     BH5, BH6, BH7, BH11, BH12

Across Two Seed Partitions:
  DEV Seeds:   [951..960]  (N=10)
  FINAL Seeds: [1101..1130] (N=30)
"""

import os
import sys
import time
import math
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scratch.bounded_history_providers import (
    HistoryProvider,
    ExactFP32RingProvider,
    FP16RingProvider,
    QuantizedInt16RingProvider,
    QuantizedInt8RingProvider,
    AgeAwareMixedPrecisionProvider,
    MultirateRingProvider,
    PolynomialHistoryProvider
)
from scratch.bench_bounded_history import generate_stream

EXP_DIR = ROOT / "experiments" / "BOUNDED-HISTORY-LAG-INTEGRATION-01"
FIG_DIR = EXP_DIR / "figures"
EXP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

DEV_SEEDS = list(range(951, 961))     # N=10
FINAL_SEEDS = list(range(1101, 1131)) # N=30

PROVIDERS = [
    "H0_EXACT_FP32",
    "H1_FP16",
    "H2_INT16",
    "H3_INT8",
    "H4_MIXED",
    "H5_NAIVE",
    "H5_AA",
    "H7_HIPPO"
]

ALL_TASKS = [
    "BH1", "BH2", "BH3", "BH4", "BH5", "BH6",
    "BH7", "BH8", "BH9", "BH10", "BH11", "BH12"
]

def create_provider(provider_id: str, d_features: int = 5, l_max: int = 32) -> HistoryProvider:
    if provider_id == "H0_EXACT_FP32":
        return ExactFP32RingProvider(d_features=d_features, l_max=l_max)
    elif provider_id == "H1_FP16":
        return FP16RingProvider(d_features=d_features, l_max=l_max)
    elif provider_id == "H2_INT16":
        return QuantizedInt16RingProvider(d_features=d_features, l_max=l_max)
    elif provider_id == "H3_INT8":
        return QuantizedInt8RingProvider(d_features=d_features, l_max=l_max)
    elif provider_id == "H4_MIXED":
        return AgeAwareMixedPrecisionProvider(d_features=d_features, l_max=l_max, split_lag=8)
    elif provider_id == "H5_NAIVE":
        return MultirateRingProvider(d_features=d_features, l_max=l_max, use_anti_alias=False)
    elif provider_id == "H5_AA":
        return MultirateRingProvider(d_features=d_features, l_max=l_max, use_anti_alias=True)
    elif provider_id == "H7_HIPPO":
        return PolynomialHistoryProvider(d_features=d_features, l_max=l_max, n_poly=6)
    else:
        raise ValueError(f"Unknown provider_id: {provider_id}")


class HistoryBoundedAdaptiveFilter:
    """
    Two-timescale sparse dynamic lag discovery filter decoupled from physical history representation.
    Queries past signal states strictly through the HistoryProvider interface.
    """
    def __init__(
        self,
        provider: HistoryProvider,
        d_features: int,
        l_max: int = 32,
        k_max: int = 4,
        probe_rate: int = 2,
        mu_base: float = 0.10,
        mu_lag: float = 0.08,
        theta_promote: float = 0.15,
        theta_evict: float = 0.05,
        include_recurrence: bool = True
    ):
        self.provider = provider
        self.D = d_features
        self.L_max = l_max
        self.K_max = k_max
        self.M = probe_rate
        self.mu_base = mu_base
        self.mu_lag = mu_lag
        self.theta_promote = theta_promote
        self.theta_evict = theta_evict
        self.include_recurrence = include_recurrence

        # Base linear weights
        self.w_base = np.zeros(d_features, dtype=np.float32)

        # Recurrent state unit
        self.s = 0.0
        self.lam = 0.90
        self.w_out = 0.0

        # Active taps: list of dicts: {'i': int, 'k': int, 'w': float, 'R': float, 'age': int, 'zero_count': int}
        self.active_taps: List[Dict[str, Any]] = []

        # Provisional candidates: list of dicts: {'i': int, 'k': int, 'w_shadow': float, 'evidence': float, 'age': int}
        self.provisional_cands: List[Dict[str, Any]] = []

        # Rotating probe grid
        self.grid_pairs = [(i, k) for i in range(d_features) for k in range(1, l_max + 1)]
        self.probe_idx = 0
        self.corr_grid = np.zeros((d_features, l_max + 1), dtype=np.float32)

        self.total_flops = 0

    def step(self, x_t: np.ndarray, y_t: float, t: int) -> Tuple[float, float, int]:
        flops = 0

        # 1. Write current input to history provider
        w_flops = self.provider.write(x_t)
        flops += w_flops

        # 2. Live Forward Pass
        y_base = float(np.dot(self.w_base, x_t))
        flops += 2 * self.D

        y_lag = 0.0
        for tap in self.active_taps:
            val, ok, _, _, q_flops = self.provider.query(tap['i'], tap['k'])
            y_lag += tap['w'] * val
            flops += 2 + q_flops

        y_rec = 0.0
        if self.include_recurrence:
            in_drive = 0.1 * x_t[0] - 0.1 * x_t[1] if self.D >= 2 else 0.1 * x_t[0]
            self.s = math.tanh(self.lam * self.s + in_drive)
            y_rec = self.w_out * self.s
            flops += 8

        y_hat = y_base + y_lag + y_rec
        e_live = y_t - y_hat

        # 3. Counterfactual Candidate Scoring
        for cand in self.provisional_cands:
            c_val, ok, _, _, q_flops = self.provider.query(cand['i'], cand['k'])
            y_cand = y_hat + cand['w_shadow'] * c_val
            e_cand = y_t - y_cand
            cand_gain = (e_live ** 2) - (e_cand ** 2)
            cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * cand_gain
            cand['age'] += 1
            cand['w_shadow'] += (0.05 / (c_val ** 2 + 1.0)) * e_cand * c_val
            cand['w_shadow'] = float(np.clip(cand['w_shadow'], -5.0, 5.0))
            flops += 8 + q_flops

        # 4. Candidate Promotion Gate
        promoted = []
        for cand in self.provisional_cands:
            if cand['evidence'] >= self.theta_promote and cand['age'] >= 30:
                if not any(t_['i'] == cand['i'] and t_['k'] == cand['k'] for t_ in self.active_taps):
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({
                            'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                            'R': cand['evidence'], 'age': 0, 'zero_count': 0
                        })
                        promoted.append(cand)
                    else:
                        # Capacity full: evaluate replacement
                        weakest_idx = int(np.argmin([t_['R'] for t_ in self.active_taps]))
                        weakest_tap = self.active_taps[weakest_idx]
                        if cand['evidence'] > weakest_tap['R'] + 0.05:
                            self.active_taps[weakest_idx] = {
                                'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                                'R': cand['evidence'], 'age': 0, 'zero_count': 0
                            }
                            promoted.append(cand)

        self.provisional_cands = [
            c for c in self.provisional_cands
            if c not in promoted and not (c['age'] > 150 and c['evidence'] < 0.02)
        ]

        # 5. Live Model Weight Adaptation
        denom_base = float(np.dot(x_t, x_t)) + 1e-4
        self.w_base += (self.mu_base / denom_base) * e_live * x_t
        flops += 3 * self.D

        for tap in self.active_taps:
            val, ok, _, _, q_flops = self.provider.query(tap['i'], tap['k'])
            denom_tap = (val ** 2) + 1.0
            tap['w'] += (self.mu_lag / denom_tap) * e_live * val
            tap['w'] = float(np.clip(tap['w'], -5.0, 5.0))
            tap['age'] += 1

            # Two-timescale obsolescence gate
            y_without = y_hat - tap['w'] * val
            e_without = y_t - y_without
            marginal_gain = (e_without ** 2) - (e_live ** 2)
            if abs(val) > 0.1:
                tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
            flops += 8 + q_flops

            # Eviction check with quiescence protection
            if tap['R'] < self.theta_evict and tap['age'] > 300:
                if abs(val) > 0.1:
                    tap['evict'] = True

        self.active_taps = [t_ for t_ in self.active_taps if not t_.get('evict', False)]

        if self.include_recurrence:
            self.w_out += 0.05 * e_live * self.s
            flops += 4

        # 6. Bounded Candidate Probing (M candidates per step)
        for _ in range(self.M):
            cand_pair = self.grid_pairs[self.probe_idx]
            self.probe_idx = (self.probe_idx + 1) % len(self.grid_pairs)
            i_p, k_p = cand_pair
            if not any(t_['i'] == i_p and t_['k'] == k_p for t_ in self.active_taps) and \
               not any(c_['i'] == i_p and c_['k'] == k_p for c_ in self.provisional_cands):
                past_val, ok, _, _, q_flops = self.provider.query(i_p, k_p)
                self.corr_grid[i_p, k_p] = 0.95 * self.corr_grid[i_p, k_p] + 0.05 * (e_live * past_val)
                flops += 4 + q_flops
                if abs(self.corr_grid[i_p, k_p]) > 0.08 and len(self.provisional_cands) < 8:
                    self.provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w_shadow': 0.0,
                        'evidence': abs(self.corr_grid[i_p, k_p]) * 0.5, 'age': 0
                    })

        self.total_flops += flops
        return y_hat, e_live, flops


def run_single_simulation(args: Tuple[str, str, int, str]) -> Dict[str, Any]:
    """
    Executes a single (task_id, provider_id, seed, seed_type) simulation.
    """
    task_id, provider_id, seed, seed_type = args
    t_start = time.time()

    # Generate stream
    T = 20000
    D = 5
    L_max = 32
    sigma_v = 0.1
    X, y, meta = generate_stream(task_id, seed=seed, T=T, D=D, L_max=L_max, sigma_v=sigma_v)

    # Initialize provider & model
    provider = create_provider(provider_id, d_features=D, l_max=L_max)
    model = HistoryBoundedAdaptiveFilter(provider, d_features=D, l_max=L_max)

    # Simulation loop
    sq_errors = np.zeros(T, dtype=np.float32)
    step_flops = np.zeros(T, dtype=np.int32)
    trajectory_snapshots = []

    # Ground truth history ring for reconstruction fidelity monitoring
    exact_history = np.zeros((D, L_max + 1), dtype=np.float32)
    recon_rmses = []

    for t in range(T):
        # Update exact history ring for ground-truth comparison
        exact_history[:, t % (L_max + 1)] = X[t]

        # Step adaptive filter
        y_hat, e_live, fl = model.step(X[t], y[t], t)
        sq_errors[t] = e_live ** 2
        step_flops[t] = fl

        # Record trajectory snapshots every 1000 steps
        if (t + 1) % 1000 == 0:
            current_active = [(t_['i'], t_['k']) for t_ in model.active_taps]
            win_now = 1 if set(current_active) == set([(t_[0], t_[1]) for t_ in meta.get("active_taps", [])]) else 0
            trajectory_snapshots.append({
                "step": t + 1,
                "window_mse": float(np.mean(sq_errors[max(0, t - 999):t + 1])),
                "active_taps": ";".join([f"({a[0]},{a[1]})" for a in current_active]),
                "num_active": len(current_active),
                "win": win_now
            })

    # Reconstruction RMSE at final state across full grid (D x L_max)
    recon_diff_sq = 0.0
    for d in range(D):
        for k in range(1, L_max + 1):
            true_val = float(exact_history[d, (T - 1 - k) % (L_max + 1)])
            q_val, ok, _, _, _ = provider.query(d, k)
            recon_diff_sq += (true_val - q_val) ** 2
    final_recon_rmse = math.sqrt(recon_diff_sq / (D * L_max))

    # Evaluate tracking error post-warmup (steps 5000..20000)
    warmup = 5000
    if task_id == "BH4": # switching task: evaluate post-switch (15000..20000)
        eval_slice = sq_errors[15000:]
    elif task_id == "BH10": # quiescence task: evaluate post-silence (15000..20000)
        eval_slice = sq_errors[15000:]
    else:
        eval_slice = sq_errors[warmup:]

    mse_eval = float(np.mean(eval_slice))
    emse_eval = max(0.0, mse_eval - meta["noise_var"])

    # Tap support recovery at t=T
    final_active_set = set((t_['i'], t_['k']) for t_ in model.active_taps)
    gt_taps = meta.get("active_taps", [])
    gt_active_set = set((t_[0], t_[1]) for t_ in gt_taps)

    if len(gt_active_set) == 0: # Memoryless / Continuous
        precision = 1.0 if len(final_active_set) == 0 else 0.0
        recall = 1.0 if len(final_active_set) == 0 else 0.0
        f1 = 1.0 if len(final_active_set) == 0 else 0.0
        win = 1 if len(final_active_set) == 0 else 0
    else:
        tp = len(final_active_set.intersection(gt_active_set))
        precision = tp / len(final_active_set) if len(final_active_set) > 0 else 0.0
        recall = tp / len(gt_active_set) if len(gt_active_set) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        win = 1 if final_active_set == gt_active_set else 0

    # Memory breakdown
    mem = provider.get_memory_breakdown()
    total_mem = mem['persistent_bytes'] + mem['transient_bytes']
    mean_flops_per_step = float(np.mean(step_flops))
    elapsed_time = time.time() - t_start

    result = {
        "task_id": task_id,
        "provider_id": provider_id,
        "seed": seed,
        "seed_type": seed_type,
        "regime": meta["regime"],
        "mse": mse_eval,
        "emse": emse_eval,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "win": win,
        "active_taps": ";".join([f"({a[0]},{a[1]})" for a in sorted(list(final_active_set))]),
        "gt_taps": ";".join([f"({g[0]},{g[1]})" for g in sorted(list(gt_active_set))]),
        "recon_rmse": final_recon_rmse,
        "total_memory_bytes": total_mem,
        "history_bytes": mem['history_bytes'],
        "metadata_bytes": mem['metadata_bytes'],
        "flops_per_step": mean_flops_per_step,
        "elapsed_s": elapsed_time,
        "trajectory_snapshots": trajectory_snapshots
    }
    return result


def run_experiment_suite():
    print("==================================================")
    print("STARTING EXPERIMENT SUITE: BOUNDED-HISTORY-01")
    print("==================================================")
    
    # 1. DEV Phase (N=10 seeds: 951..960)
    print(f"\n[PHASE 1/2] Running DEV Phase ({len(DEV_SEEDS)} seeds, {len(ALL_TASKS)} tasks, {len(PROVIDERS)} providers)...")
    dev_jobs = [
        (task, prov, seed, "DEV")
        for seed in DEV_SEEDS
        for task in ALL_TASKS
        for prov in PROVIDERS
    ]
    print(f"Total DEV configurations: {len(dev_jobs)}")

    t0_dev = time.time()
    dev_results = []
    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(run_single_simulation, job): job for job in dev_jobs}
        done_cnt = 0
        for fut in as_completed(futures):
            res = fut.result()
            dev_results.append(res)
            done_cnt += 1
            if done_cnt % 100 == 0 or done_cnt == len(dev_jobs):
                print(f"  DEV Progress: {done_cnt}/{len(dev_jobs)} completed ({100*done_cnt/len(dev_jobs):.1f}%)")
    dev_duration = time.time() - t0_dev
    print(f"[PHASE 1/2] DEV Phase Completed in {dev_duration:.2f} s.")

    # 2. FINAL Confirmation Phase (N=30 seeds: 1101..1130)
    print(f"\n[PHASE 2/2] Running FINAL Confirmation Phase ({len(FINAL_SEEDS)} seeds, {len(ALL_TASKS)} tasks, {len(PROVIDERS)} providers)...")
    final_jobs = [
        (task, prov, seed, "FINAL")
        for seed in FINAL_SEEDS
        for task in ALL_TASKS
        for prov in PROVIDERS
    ]
    print(f"Total FINAL configurations: {len(final_jobs)}")

    t0_final = time.time()
    final_results = []
    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(run_single_simulation, job): job for job in final_jobs}
        done_cnt = 0
        for fut in as_completed(futures):
            res = fut.result()
            final_results.append(res)
            done_cnt += 1
            if done_cnt % 200 == 0 or done_cnt == len(final_jobs):
                print(f"  FINAL Progress: {done_cnt}/{len(final_jobs)} completed ({100*done_cnt/len(final_jobs):.1f}%)")
    final_duration = time.time() - t0_final
    print(f"[PHASE 2/2] FINAL Phase Completed in {final_duration:.2f} s.")

    all_results = dev_results + final_results

    # 3. Export CSV Artifacts
    print("\n[ARTIFACT EXPORT] Exporting CSV artifacts...")

    # Manifest CSV
    manifest_csv = EXP_DIR / "BOUNDED_HISTORY_01_RUN_MANIFEST.csv"
    with open(manifest_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["task_id", "provider_id", "seed", "seed_type", "elapsed_s", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            writer.writerow({
                "task_id": r["task_id"],
                "provider_id": r["provider_id"],
                "seed": r["seed"],
                "seed_type": r["seed_type"],
                "elapsed_s": f"{r['elapsed_s']:.4f}",
                "status": "COMPLETED"
            })
    print(f"  -> Exported: {manifest_csv}")

    # Seed Results CSV
    seed_results_csv = EXP_DIR / "BOUNDED_HISTORY_01_SEED_RESULTS.csv"
    with open(seed_results_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "task_id", "provider_id", "seed", "seed_type", "regime",
            "mse", "emse", "precision", "recall", "f1", "win",
            "active_taps", "gt_taps", "recon_rmse",
            "total_memory_bytes", "history_bytes", "metadata_bytes",
            "flops_per_step", "elapsed_s"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row = {k: r[k] for k in fieldnames}
            writer.writerow(row)
    print(f"  -> Exported: {seed_results_csv}")

    # History Error Summary CSV
    history_error_csv = EXP_DIR / "BOUNDED_HISTORY_01_HISTORY_ERROR.csv"
    with open(history_error_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["provider_id", "task_id", "regime", "seed_type", "mean_recon_rmse", "std_recon_rmse", "max_recon_rmse"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Group by provider, task, seed_type
        from collections import defaultdict
        grouped = defaultdict(list)
        for r in all_results:
            grouped[(r["provider_id"], r["task_id"], r["regime"], r["seed_type"])].append(r["recon_rmse"])
        for (prov, task, reg, s_type), vals in sorted(grouped.items()):
            writer.writerow({
                "provider_id": prov,
                "task_id": task,
                "regime": reg,
                "seed_type": s_type,
                "mean_recon_rmse": f"{np.mean(vals):.6f}",
                "std_recon_rmse": f"{np.std(vals):.6f}",
                "max_recon_rmse": f"{np.max(vals):.6f}"
            })
    print(f"  -> Exported: {history_error_csv}")

    # Trajectories CSV (FINAL seeds only to keep file size optimal)
    trajectories_csv = EXP_DIR / "BOUNDED_HISTORY_01_SUPPORT_TRAJECTORIES.csv"
    with open(trajectories_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["task_id", "provider_id", "seed", "step", "window_mse", "active_taps", "num_active", "win"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in final_results:
            for snap in r["trajectory_snapshots"]:
                writer.writerow({
                    "task_id": r["task_id"],
                    "provider_id": r["provider_id"],
                    "seed": r["seed"],
                    "step": snap["step"],
                    "window_mse": f"{snap['window_mse']:.6f}",
                    "active_taps": snap["active_taps"],
                    "num_active": snap["num_active"],
                    "win": snap["win"]
                })
    print(f"  -> Exported: {trajectories_csv}")

    print("\nExperiment Suite Successfully Finished!")

if __name__ == "__main__":
    run_experiment_suite()
