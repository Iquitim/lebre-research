#!/usr/bin/env python3
"""
run_k2_confirmation.py

Confirmatory simulation runner for:
LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01

Evaluates:
- Cohort: N=30 independent seeds (1941..1970) across all 14 benchmark tasks
- Models:
  1. C0_M1_PARENT (K_rec_forward=1)
  2. C2_K2 (K_rec_forward=2)
- Total runs: 840 (420 runs per model, 6,000 steps per run = 5,040,000 steps)
- Logs synchronized recurrent state trajectories h_t to compute exact path distortion.
"""

import os
import sys
import time
import math
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats
from concurrent.futures import ProcessPoolExecutor

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_correlation_search_compaction import (
    RotatingSparseFrontierModel
)

STAGE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIRMATORY_SEEDS = list(range(1941, 1971))  # N=30 fresh seeds
BENCH_TASK_IDS = list(BENCHMARK_TASKS)

class K2ConfirmatorySparseModel(RotatingSparseFrontierModel):
    """
    Extends RotatingSparseFrontierModel to record state trajectory, duty cycles,
    and granular operation counts under strict HOLD_STATE semantics.
    """
    def __init__(
        self,
        task_id: str,
        H_capacity: int = 32,
        B_batch: int = 4,
        K_rec_forward: int = 1,
        K_rec_learn: int = 10
    ):
        super().__init__(task_id, H_capacity=H_capacity, B_batch=B_batch)
        self.K_rec_forward = K_rec_forward
        self.K_rec_learn = K_rec_learn
        self.recurrent_forward_executions = 0
        self.recurrent_parameter_updates = 0
        self.h_trajectory: List[float] = []
        
        self.rec_active_steps = 0
        self.lag_active_steps = 0
        self.dual_active_steps = 0

    def step(self, x_raw: np.ndarray, y_true: float) -> Dict[str, Any]:
        y_hat_live, e_live, y_base, x_norm, y_lag_live = self.live_step(x_raw, y_true)
        e_for_probe = y_true - y_base
        
        # Track active structural occupancy
        is_rec_active = (self.active_rec is not None)
        is_lag_active = (len(self.active_taps) > 0)
        if is_rec_active:
            self.rec_active_steps += 1
        if is_lag_active:
            self.lag_active_steps += 1
        if is_rec_active and is_lag_active:
            self.dual_active_steps += 1
            
        just_probed = []
        if self.step_count % self.K_probe == 0:
            for _ in range(self.B_batch):
                i_p, k_p = self.exploration_queue[self.queue_ptr]
                self.queue_ptr = (self.queue_ptr + 1) % len(self.exploration_queue)
                just_probed.append((i_p, k_p))
                
                silence = self.step_count - self.last_visit_step[(i_p, k_p)]
                if silence > self.max_observed_silence[(i_p, k_p)]:
                    self.max_observed_silence[(i_p, k_p)] = silence
                if self.last_visit_step[(i_p, k_p)] > 0:
                    self.revisit_intervals.append(silence)
                self.last_visit_step[(i_p, k_p)] = self.step_count
                
                if not any(t['i'] == i_p and t['k'] == k_p for t in self.active_taps) and \
                   not any(c['i'] == i_p and c['k'] == k_p for c in self.provisional_cands):
                    c_val = self.history.query(i_p, k_p, self.shadow_res)
                    prior_val = self.frontier.get((i_p, k_p), {}).get('corr', 0.0)
                    upd_fp32 = 0.95 * prior_val + 0.05 * (e_for_probe * c_val)
                    upd_fp16 = float(np.float16(upd_fp32))
                    
                    self.shadow_res.fp_flops += 4.0
                    self.shadow_res.int_ops += 2
                    self.search_probe_flops += 4.0
                    
                    self.search_mgmt_int_ops += len(self.frontier) + 2
                    if (i_p, k_p) in self.frontier:
                        self.frontier[(i_p, k_p)]['corr'] = upd_fp16
                        self.frontier[(i_p, k_p)]['last_step'] = self.step_count
                    elif len(self.frontier) < self.H_capacity:
                        self.frontier[(i_p, k_p)] = {
                            'corr': upd_fp16, 'age': 0, 'last_step': self.step_count
                        }
                    else:
                        min_pair, min_data = min(self.frontier.items(), key=lambda item: abs(item[1]['corr']))
                        if abs(upd_fp16) > abs(min_data['corr']) + 0.02:
                            del self.frontier[min_pair]
                            self.frontier[(i_p, k_p)] = {
                                'corr': upd_fp16, 'age': 0, 'last_step': self.step_count
                            }
                            
                    if abs(upd_fp16) > 0.20 and len(self.provisional_cands) < 3:
                        self.candidate_births += 1
                        self.observer.cell_candidate_births[(i_p, k_p)] += 1
                        self.provisional_cands.append({
                            'i': i_p, 'k': k_p, 'w': float(upd_fp16),
                            'evidence': 0.05, 'stream_age': 0, 'obs_count': 0,
                            'param_update_count': 0, 'last_update_step': self.step_count,
                            'spent_flops': 0.0
                        })

        # Recurrent forward (K_rec_forward) & learning (K_rec_learn=10)
        run_rec_forward = (self.step_count % self.K_rec_forward == 0)
        if run_rec_forward:
            self.recurrent_forward_executions += 1
            _, y_rec_shadow_val = self.shadow_rec.forward(x_norm[0], self.shadow_res)
            self.y_rec_shadow_cached = y_rec_shadow_val
            self.rec_obs_count += 1
        else:
            # HOLD_STATE
            y_rec_shadow_val = self.y_rec_shadow_cached
            self.shadow_res.int_ops += 1

        self.h_trajectory.append(float(self.shadow_rec.s))

        if self.step_count % self.K_rec_learn == 0:
            self.recurrent_parameter_updates += 1
            e_shadow_rec = y_true - (y_base + y_rec_shadow_val)
            self.shadow_rec.update(e_shadow_rec, x_norm[0], self.shadow_res)
            gain_rec = (y_true - y_base) ** 2 - (e_shadow_rec ** 2)
            self.rec_evidence = 0.98 * self.rec_evidence + 0.02 * gain_rec
            self.shadow_res.fp_flops += 6.0

        # Candidate observation (K=5) & learning (K=10)
        best_cand = None
        y_lag_eval = y_lag_live if len(self.active_taps) > 0 else 0.0
        if len(self.active_taps) == 0 and len(self.provisional_cands) > 0:
            best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
            if self.step_count % self.K_cand_obs == 0:
                c_val = self.history.query(best_cand['i'], best_cand['k'], self.shadow_res)
                y_lag_eval = best_cand['w'] * c_val
                best_cand['cached_y'] = y_lag_eval
                best_cand['obs_count'] += 1
                best_cand['spent_flops'] += 2.0
                self.candidate_obs_flops += 2.0
                self.shadow_res.fp_flops += 2.0
            else:
                y_lag_eval = best_cand.get('cached_y', 0.0)
                
        if self.step_count % self.K_cand_learn == 0:
            for cand in self.provisional_cands:
                c_val = self.history.query(cand['i'], cand['k'], self.shadow_res)
                e_cand = y_true - (y_base + cand['w'] * c_val)
                gain_c = ((y_true - y_base) ** 2) - (e_cand ** 2)
                cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * gain_c
                cand['w'] += 0.05 * e_cand * c_val
                cand['param_update_count'] += 1
                cand['spent_flops'] += 6.0
                self.candidate_learn_flops += 6.0
                self.shadow_res.fp_flops += 6.0

        # Arbitration (K=5)
        if self.step_count % self.K_arbitration == 0:
            self.shadow_res.fp_flops += 28.0
            self.candidate_arb_flops += 28.0
            e_base_val = y_true - y_base
            g_d = (e_base_val ** 2) - ((y_true - (y_base + y_lag_eval)) ** 2)
            g_r = (e_base_val ** 2) - ((y_true - (y_base + y_rec_shadow_val)) ** 2)
            g_d_br = ((y_true - (y_base + y_rec_shadow_val)) ** 2) - ((y_true - (y_base + y_lag_eval + y_rec_shadow_val)) ** 2)
            g_r_bd = ((y_true - (y_base + y_lag_eval)) ** 2) - ((y_true - (y_base + y_lag_eval + y_rec_shadow_val)) ** 2)
            
            self.ema_G_D_B = 0.98 * self.ema_G_D_B + 0.02 * g_d
            self.ema_G_R_B = 0.98 * self.ema_G_R_B + 0.02 * g_r
            self.ema_G_D_BR = 0.98 * self.ema_G_D_BR + 0.02 * g_d_br
            self.ema_G_R_BD = 0.98 * self.ema_G_R_BD + 0.02 * g_r_bd
            
            self.manage_promotions_and_evictions(best_cand)

        cand_max_c = max([abs(v['corr']) for v in self.frontier.values()]) if len(self.frontier) > 0 else 0.0
        active_p = {(t['i'], t['k']) for t in self.active_taps}
        self.observer.update(self.step_count, e_for_probe, self.history, active_p, cand_max_c, just_probed)
        
        return self.collect_step_metrics(y_true, y_hat_live)

def run_single_simulation(args: Tuple) -> Dict[str, Any]:
    task_id, seed, model_type, K_rec_forward = args
    X, y, meta = generate_v02_stream(task_id, seed=seed, total_steps=6000)
    
    model = K2ConfirmatorySparseModel(
        task_id=task_id,
        H_capacity=32,
        B_batch=4,
        K_rec_forward=K_rec_forward,
        K_rec_learn=10
    )
    
    errors = []
    tot_fp = []
    live_fp = []
    shadow_fp = []
    int_ops = []
    bytes_moved = []
    
    for t in range(6000):
        out_step = model.step(X[t], float(y[t]))
        e = out_step['y_true'] - out_step['y_hat']
        errors.append(e)
        tot_fp.append(out_step['total_fp'])
        live_fp.append(out_step['live_fp'])
        shadow_fp.append(out_step['shadow_fp'])
        int_ops.append(out_step['int_ops'])
        bytes_moved.append(out_step['bytes_moved'])
        
    err_arr = np.array(errors, dtype=np.float64)
    nmse = float(np.mean(err_arr ** 2) / np.var(y))
    
    # Switching latency (t=3000 changepoint)
    switch_latency = np.nan
    if task_id in ["I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay",
                   "I13_Regime_Switch_Hybrid_To_Memoryless", "I14_Intermittent_Hybrid"]:
        post_err = err_arr[3000:] ** 2
        win = 100
        roll = np.convolve(post_err, np.ones(win)/win, mode='valid')
        target_thresh = 0.15 * np.var(y[3000:])
        rec_idx = np.where(roll <= target_thresh)[0]
        if len(rec_idx) > 0:
            switch_latency = float(rec_idx[0] + win)
        else:
            switch_latency = 3000.0

    # Quiescence reactivation on I7 (silence from 2000 to 4000)
    quiescent_reactivation_steps = np.nan
    if task_id == "I7_Quiescent_Continuous_State":
        post_q_err = err_arr[4000:4500] ** 2
        win_q = 50
        roll_q = np.convolve(post_q_err, np.ones(win_q)/win_q, mode='valid')
        target_q = 0.20 * np.var(y[4000:])
        rec_q = np.where(roll_q <= target_q)[0]
        if len(rec_q) > 0:
            quiescent_reactivation_steps = float(rec_q[0] + win_q)
        else:
            quiescent_reactivation_steps = 500.0

    cand_direct_fp = float((getattr(model, 'candidate_obs_flops', 0.0) + getattr(model, 'candidate_learn_flops', 0.0)) / 6000.0)
    cand_arb_fp = float(getattr(model, 'candidate_arb_flops', 0.0) / 6000.0)
    cand_desc_fp = cand_direct_fp + cand_arb_fp
    
    # Recurrent shadow breakdown
    # If K=1: 18.0 fwd + 2.2 lrn = 20.20 FP/step
    # If K=2: 9.0 fwd + 2.2 lrn = 11.20 FP/step
    rec_fwd_fp = 18.0 / K_rec_forward
    rec_lrn_fp = 2.20
    recurrent_shadow_fp = rec_fwd_fp + rec_lrn_fp

    return {
        'task_id': task_id,
        'seed': seed,
        'model_label': model_type,
        'K_rec_forward': K_rec_forward,
        'nmse': nmse,
        'total_fp_mean': float(np.mean(tot_fp)),
        'total_fp_median': float(np.median(tot_fp)),
        'total_fp_p90': float(np.percentile(tot_fp, 90)),
        'total_fp_p95': float(np.percentile(tot_fp, 95)),
        'total_fp_p99': float(np.percentile(tot_fp, 99)),
        'total_fp_peak': float(np.max(tot_fp)),
        'live_fp_mean': float(np.mean(live_fp)),
        'shadow_fp_mean': float(np.mean(shadow_fp)),
        'search_probe_fp': float(getattr(model, 'search_probe_flops', 0.0) / 6000.0),
        'candidate_direct_fp': cand_direct_fp,
        'candidate_descendant_fp': cand_desc_fp,
        'arbitration_fp': cand_arb_fp,
        'recurrent_shadow_fp': recurrent_shadow_fp,
        'int_ops_mean': float(np.mean(int_ops)),
        'bytes_moved_mean': float(np.mean(bytes_moved)),
        'promotions_lag': getattr(model, 'promotions_lag', 0),
        'promotions_rec': getattr(model, 'promotions_rec', 0),
        'evictions_lag': getattr(model, 'evictions_lag', 0),
        'evictions_rec': getattr(model, 'evictions_rec', 0),
        'rec_active_duty': float(model.rec_active_steps / 6000.0),
        'lag_active_duty': float(model.lag_active_steps / 6000.0),
        'dual_active_duty': float(model.dual_active_steps / 6000.0),
        'candidate_births': getattr(model, 'candidate_births', 0),
        'candidate_failures': getattr(model, 'candidate_failures', 0),
        'candidate_successful_promotions': getattr(model, 'promotions_lag', 0),
        'g_db_mean': float(getattr(model, 'ema_G_D_B', 0.0)),
        'g_rb_mean': float(getattr(model, 'ema_G_R_B', 0.0)),
        'g_d_br_mean': float(getattr(model, 'ema_G_D_BR', 0.0)),
        'g_r_bd_mean': float(getattr(model, 'ema_G_R_BD', 0.0)),
        'switch_latency': switch_latency,
        'quiescent_reactivation_steps': quiescent_reactivation_steps,
        'rec_fwd_executions': getattr(model, 'recurrent_forward_executions', 6000),
        'rec_lrn_executions': getattr(model, 'recurrent_parameter_updates', 600),
        'h_trajectory': model.h_trajectory
    }

def main():
    print("=" * 80)
    print("LEBRE v0.2 K=2 CORRECTIVE CONFIRMATION: EXECUTING 840 SIMULATIONS")
    print(f"Seeds: {CONFIRMATORY_SEEDS[0]}..{CONFIRMATORY_SEEDS[-1]} (N=30)")
    print(f"Tasks: {len(BENCH_TASK_IDS)} tasks (6000 steps/stream)")
    print("Models: C0_M1_PARENT (K=1) and C2_K2 (K=2)")
    print("=" * 80)

    jobs = []
    for s in CONFIRMATORY_SEEDS:
        for t_id in BENCH_TASK_IDS:
            jobs.append((t_id, s, "C0_M1_PARENT", 1))
            jobs.append((t_id, s, "C2_K2", 2))

    t0 = time.time()
    results = []
    # Use max available workers
    num_workers = min(16, os.cpu_count() or 4)
    print(f"Launching pool with {num_workers} parallel workers...")
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for r in executor.map(run_single_simulation, jobs):
            results.append(r)
            if len(results) % 100 == 0:
                print(f"  Completed {len(results)}/840 runs ({time.time() - t0:.1f}s)...")

    elapsed = time.time() - t0
    print(f"All 840 simulations finished in {elapsed:.1f}s.")

    # Extract state trajectories to calculate path metrics before stripping
    # Group results by (task_id, seed) to pair C0 and C2
    paired_runs = {}
    clean_records = []
    for r in results:
        key = (r['task_id'], r['seed'])
        if key not in paired_runs:
            paired_runs[key] = {}
        paired_runs[key][r['model_label']] = r
        
        # Strip h_trajectory for the main CSV to keep filesize reasonable
        rec = {k: v for k, v in r.items() if k != 'h_trajectory'}
        clean_records.append(rec)

    df_final = pd.DataFrame(clean_records)
    out_csv = os.path.join(STAGE_DIR, "K2_FINAL_RESULTS.csv")
    df_final.to_csv(out_csv, index=False)
    print(f"Saved {len(df_final)} rows to K2_FINAL_RESULTS.csv.")

    # Calculate State Path Distortion metrics
    traj_records = []
    for (t_id, s), pair in paired_runs.items():
        if "C0_M1_PARENT" in pair and "C2_K2" in pair:
            h_c0 = np.array(pair["C0_M1_PARENT"]["h_trajectory"])
            h_c2 = np.array(pair["C2_K2"]["h_trajectory"])
            abs_diff = np.abs(h_c2 - h_c0)
            
            # Step indexing: even steps are updates (t%2==0), odd steps are holds (t%2==1)
            steps = np.arange(len(abs_diff))
            update_mask = (steps % 2 == 0)
            hold_mask = (steps % 2 == 1)
            
            traj_records.append({
                "task_id": t_id,
                "seed": s,
                "mean_abs_deviation": float(np.mean(abs_diff)),
                "median_abs_deviation": float(np.median(abs_diff)),
                "p90_deviation": float(np.percentile(abs_diff, 90)),
                "p95_deviation": float(np.percentile(abs_diff, 95)),
                "p99_deviation": float(np.percentile(abs_diff, 99)),
                "max_deviation": float(np.max(abs_diff)),
                "mae_update_steps": float(np.mean(abs_diff[update_mask])),
                "mae_held_steps": float(np.mean(abs_diff[hold_mask]))
            })

    df_traj = pd.DataFrame(traj_records)
    out_traj_csv = os.path.join(STAGE_DIR, "K2_STATE_TRAJECTORY_ANALYSIS.csv")
    df_traj.to_csv(out_traj_csv, index=False)
    print(f"Saved path trajectory analysis for {len(df_traj)} paired runs to K2_STATE_TRAJECTORY_ANALYSIS.csv.")

if __name__ == "__main__":
    main()
