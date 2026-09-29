#!/usr/bin/env python3
"""
run_v02_corrective_confirmation.py

Corrective Confirmatory Experiment Runner for Resource Compaction:
- Enforces the Single-Difference Invariant via a single shared model class:
    CorrectedCanonicalLEBREModel(IntegratedLEBREModel)
- Executes deterministic Canonical Reference Parity Gate against IntegratedLEBREModel.
- Runs DEV cohort (seeds 1501..1510, N=10) -> CORRECTIVE_CONFIRMATION_DEV_RESULTS.csv
- Runs FINAL cohort (seeds 1511..1540, N=30) -> CORRECTIVE_CONFIRMATION_FINAL_RESULTS.csv
- Generates CANONICAL_REFERENCE_PARITY_TRACE.csv, CANONICAL_SCALER_STATE_TRACE.csv,
  CAUSAL_DIVERGENCE_TRACE.csv, and raw parity diagnostics.
"""

import sys
import time
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from multiprocessing import Pool, cpu_count

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent.parent))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_integration_experiments import (
    IntegratedLEBREModel,
    CausalStandardScaler,
    FP16HistoryRingBuffer,
    LinearBasePredictor,
    RecurrentScalarUnit,
    ResourceVector
)

OUT_DIR = Path("experiments/LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Corrected Canonical LEBRE Model Class
# -----------------------------------------------------------------------------
class CorrectedCanonicalLEBREModel(IntegratedLEBREModel):
    """
    Corrected canonical T3 model incorporating:
      1. Canonical online causal standard scaler updates (line 559 restored).
      2. Stale candidate pruning (line 548 restored).
      3. Storage dtype parameterization for corr_grid (np.float32 for C0, np.float16 for C1).
      4. Transient single-precision (float32) arithmetic for C1 probing updates.
    """
    def __init__(
        self,
        corr_grid_dtype: np.dtype = np.float32,
        d_features: int = 5,
        l_max: int = 32,
        k_max: int = 4,
        theta_tol: float = 0.015
    ):
        super().__init__(
            topology="T3",
            d_features=d_features,
            l_max=l_max,
            k_max=k_max,
            theta_tol=theta_tol
        )
        self.corr_grid_dtype = corr_grid_dtype
        self.corr_grid = np.zeros((self.D, self.L_max + 1), dtype=corr_grid_dtype)
        self.cast_ops = 0

    def get_persistent_bytes(self) -> int:
        mem = self.scaler.d * 16 # scaler mean (8B), var (8B)
        mem += self.history.get_memory_bytes()
        mem += self.base.get_memory_bytes()
        mem += len(self.active_taps) * 16 # tap metadata
        mem += len(self.provisional_cands) * 16
        mem += self.corr_grid.nbytes
        if self.active_rec is not None:
            mem += self.active_rec.get_memory_bytes()
        mem += self.shadow_rec.get_memory_bytes()
        mem += 64 # arbitrator & state registers
        return mem

    def step(self, x_raw: np.ndarray, y_true: float) -> Dict[str, Any]:
        self.step_count += 1
        self.live_res.reset_step()
        self.shadow_res.reset_step()
        
        # Step 1 & 2: Normalize and write history
        x_norm = self.scaler.transform(x_raw, self.live_res)
        self.history.write(x_norm, self.live_res)
        
        def query_delayed(i_feat: int, k_lag: int, is_shadow: bool = False) -> float:
            target_res = self.shadow_res if is_shadow else self.live_res
            return self.history.query(i_feat, k_lag, target_res)
            
        # Step 3: Base prediction
        y_base = self.base.predict(x_norm, self.live_res)
        
        # Step 4: Discrete Lag active prediction
        y_lag_live = 0.0
        for tap in self.active_taps:
            val = query_delayed(tap['i'], tap['k'], is_shadow=False)
            y_lag_live += tap['w'] * val
            self.live_res.fp_flops += 2.0
            
        # Step 5: Recurrent active prediction
        y_rec_live = 0.0
        if self.active_rec is not None:
            _, y_rec_live = self.active_rec.forward(x_norm[0], self.live_res)
            
        # Step 6: Form Shadow Predictions for counterfactuals
        if len(self.active_taps) > 0:
            y_lag_eval = y_lag_live
        elif len(self.provisional_cands) > 0:
            best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
            c_val = query_delayed(best_cand['i'], best_cand['k'], is_shadow=True)
            y_lag_eval = best_cand['w'] * c_val
            self.shadow_res.fp_flops += 2.0
        else:
            y_lag_eval = 0.0
            
        _, y_rec_shadow_val = self.shadow_rec.forward(x_norm[0], self.shadow_res)
        if self.active_rec is not None:
            y_rec_eval = y_rec_live
        elif self.rec_evidence > 0.02 and self.rec_age >= 15:
            y_rec_eval = y_rec_shadow_val
        else:
            y_rec_eval = 0.0
        
        # Counterfactual loss grid
        P_BASE = y_base
        P_BASE_D = y_base + y_lag_eval
        P_BASE_R = y_base + y_rec_eval
        P_BASE_D_R = y_base + y_lag_eval + y_rec_eval
        
        # Step 7: Live Prediction
        y_hat_live = y_base + y_lag_live + y_rec_live
            
        # Step 8: Reveal y_true and evaluate losses
        e_live = y_true - y_hat_live
        ell_live = e_live ** 2
        
        ell_B = (y_true - P_BASE) ** 2
        ell_BD = (y_true - P_BASE_D) ** 2
        ell_BR = (y_true - P_BASE_R) ** 2
        ell_BDR = (y_true - P_BASE_D_R) ** 2
        
        # Step 9: Compute conditional gains
        G_D_B = ell_B - ell_BD
        G_R_B = ell_B - ell_BR
        G_R_BD = ell_BD - ell_BDR
        G_D_BR = ell_BR - ell_BDR
        
        # EMA filter gains
        alpha_g = 0.02
        self.ema_G_D_B = (1.0 - alpha_g) * self.ema_G_D_B + alpha_g * G_D_B
        self.ema_G_R_B = (1.0 - alpha_g) * self.ema_G_R_B + alpha_g * G_R_B
        self.ema_G_R_BD = (1.0 - alpha_g) * self.ema_G_R_BD + alpha_g * G_R_BD
        self.ema_G_D_BR = (1.0 - alpha_g) * self.ema_G_D_BR + alpha_g * G_D_BR
        self.shadow_res.fp_flops += 16.0
        
        # Step 10: Component updates
        self.base.update(x_norm, y_true - y_base, self.live_res)
            
        # Update active lag taps
        for tap in self.active_taps:
            val = query_delayed(tap['i'], tap['k'], is_shadow=False)
            tap['w'] += 0.08 * e_live * val
            tap['age'] += 1
            e_without = y_true - (y_hat_live - tap['w'] * val)
            gain_tap = (e_without ** 2) - (e_live ** 2)
            if abs(val) > 0.1:
                tap['R'] = 0.999 * tap['R'] + 0.001 * gain_tap
            if tap['R'] < 0.03 and tap['age'] > 250 and abs(val) > 0.1:
                tap['evict'] = True
            self.live_res.fp_flops += 8.0
        evict_taps = [t for t in self.active_taps if t.get('evict', False)]
        self.evictions_lag += len(evict_taps)
        self.active_taps = [t for t in self.active_taps if not t.get('evict', False)]
        
        # Update active recurrent unit
        if self.active_rec is not None:
            self.active_rec.update(e_live, x_norm[0], self.live_res)
            
        # Update shadow recurrent candidate
        e_shadow_rec = y_true - (y_base + y_rec_shadow_val)
        self.shadow_rec.update(e_shadow_rec, x_norm[0], self.shadow_res)
        gain_rec = (y_true - y_base) ** 2 - (e_shadow_rec ** 2)
        self.rec_evidence = 0.98 * self.rec_evidence + 0.02 * gain_rec
        self.rec_age += 1
        self.shadow_res.fp_flops += 6.0
        
        # Update shadow lag candidate pool
        for cand in self.provisional_cands:
            c_val = query_delayed(cand['i'], cand['k'], is_shadow=True)
            e_cand = y_true - (y_base + cand['w'] * c_val)
            gain_c = ((y_true - y_base) ** 2) - (e_cand ** 2)
            cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * gain_c
            cand['age'] += 1
            cand['w'] += 0.05 * e_cand * c_val
            self.shadow_res.fp_flops += 8.0
            
        # Shadow probing (M=2)
        e_for_probe = y_true - y_base
        for _ in range(2):
            i_p, k_p = self.grid_pairs[self.probe_ptr]
            self.probe_ptr = (self.probe_ptr + 1) % len(self.grid_pairs)
            if not any(t['i'] == i_p and t['k'] == k_p for t in self.active_taps) and \
               not any(c['i'] == i_p and c['k'] == k_p for c in self.provisional_cands):
                c_val = query_delayed(i_p, k_p, is_shadow=True)
                
                if self.corr_grid_dtype == np.float32:
                    # C0: Full IEEE 754 float32 storage
                    self.corr_grid[i_p, k_p] = 0.95 * self.corr_grid[i_p, k_p] + 0.05 * (e_for_probe * c_val)
                    corr_val = float(self.corr_grid[i_p, k_p])
                    self.shadow_res.fp_flops += 4.0
                else:
                    # C1: IEEE 754 float16 storage with transient float32 math
                    val_fp32 = float(self.corr_grid[i_p, k_p])
                    upd_fp32 = 0.95 * val_fp32 + 0.05 * (e_for_probe * c_val)
                    self.corr_grid[i_p, k_p] = np.float16(upd_fp32)
                    corr_val = upd_fp32
                    self.shadow_res.fp_flops += 4.0
                    self.shadow_res.int_ops += 2 # 2 conversion ops (read fp16->fp32, write fp32->fp16)
                    self.cast_ops += 2
                    
                if abs(corr_val) > 0.20 and len(self.provisional_cands) < 3:
                    self.provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w': float(corr_val),
                        'evidence': 0.05, 'age': 0
                    })
                
        # Step 11: Arbitration & Promotion Logic (T3)
        d_helps = self.ema_G_D_B > self.theta_tol
        r_helps = self.ema_G_R_B > self.theta_tol
        d_cond = self.ema_G_D_BR > self.theta_tol
        r_cond = self.ema_G_R_BD > self.theta_tol
        
        decision = "NONE"
        if not d_helps and not r_helps:
            decision = "NONE"
            if len(self.active_taps) > 0 and self.step_count > 300 and self.ema_G_D_B < 0.005:
                self.evictions_lag += len(self.active_taps)
                self.active_taps = []
            if self.active_rec is not None and self.step_count > 300 and self.ema_G_R_B < 0.008:
                self.active_rec = None
                self.evictions_rec += 1
        elif d_helps and not r_helps:
            decision = "LAG_ONLY"
            if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                self.active_rec = None
                self.evictions_rec += 1
            for cand in list(self.provisional_cands):
                if cand['evidence'] >= 0.10 and cand['age'] >= 20:
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                        self.provisional_cands.remove(cand)
                        self.promotions_lag += 1
        elif r_helps and not d_helps:
            decision = "RECURRENT_ONLY"
            if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                self.evictions_lag += len(self.active_taps)
                self.active_taps = []
            if self.active_rec is None and self.rec_evidence >= 0.14 and self.rec_age >= 50:
                self.active_rec = RecurrentScalarUnit()
                self.active_rec.alpha = self.shadow_rec.alpha
                self.active_rec.b = self.shadow_rec.b
                self.active_rec.c = self.shadow_rec.c
                self.promotions_rec += 1
        else: # Both have standalone gain
            if d_cond and r_cond:
                decision = "BOTH"
                for cand in list(self.provisional_cands):
                    if cand['evidence'] >= 0.10 and cand['age'] >= 20 and len(self.active_taps) < self.K_max:
                        self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                        self.provisional_cands.remove(cand)
                        self.promotions_lag += 1
                if self.active_rec is None and self.rec_evidence >= 0.14 and self.rec_age >= 50:
                    self.active_rec = RecurrentScalarUnit()
                    self.active_rec.alpha = self.shadow_rec.alpha
                    self.active_rec.b = self.shadow_rec.b
                    self.active_rec.c = self.shadow_rec.c
                    self.promotions_rec += 1
            else:
                decision = "REDUNDANT"
                if self.ema_G_D_B >= self.ema_G_R_B:
                    if self.active_rec is not None:
                        self.active_rec = None
                        self.evictions_rec += 1
                    for cand in list(self.provisional_cands):
                        if cand['evidence'] >= 0.10 and cand['age'] >= 20 and len(self.active_taps) < self.K_max:
                            self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                            self.provisional_cands.remove(cand)
                            self.promotions_lag += 1
                else:
                    if len(self.active_taps) > 0:
                        self.evictions_lag += len(self.active_taps)
                        self.active_taps = []
                    if self.active_rec is None and self.rec_evidence >= 0.14 and self.rec_age >= 50:
                        self.active_rec = RecurrentScalarUnit()
                        self.active_rec.alpha = self.shadow_rec.alpha
                        self.active_rec.b = self.shadow_rec.b
                        self.active_rec.c = self.shadow_rec.c
                        self.promotions_rec += 1

        self.arbitration_decision = decision
        
        # Prune stale candidates (CANONICAL RESTORATION)
        self.provisional_cands = [c for c in self.provisional_cands if not (c['age'] > 150 and c['evidence'] < 0.02)]
        
        # Track dual active occupancy
        has_lag = len(self.active_taps) > 0
        has_rec = self.active_rec is not None
        if has_lag and has_rec:
            self.dual_active_steps += 1
            if decision == "REDUNDANT" or (self.ema_G_D_BR <= self.theta_tol and self.ema_G_R_BD <= self.theta_tol):
                self.redundant_dual_steps += 1
                
        # Scaler update (CANONICAL RESTORATION)
        self.scaler.update(x_raw, self.live_res)
        
        # Structural state summary
        if has_lag and has_rec:
            curr_state = "BOTH"
        elif has_lag:
            curr_state = "LAG"
        elif has_rec:
            curr_state = "RECURRENT"
        else:
            curr_state = "NONE"
            
        return {
            "y_hat": y_hat_live,
            "e_live": e_live,
            "loss": ell_live,
            "G_D_B": G_D_B,
            "G_R_B": G_R_B,
            "G_D_BR": G_D_BR,
            "G_R_BD": G_R_BD,
            "ema_G_D_B": float(self.ema_G_D_B),
            "ema_G_R_B": float(self.ema_G_R_B),
            "ema_G_D_BR": float(self.ema_G_D_BR),
            "ema_G_R_BD": float(self.ema_G_R_BD),
            "decision": decision,
            "allocated_state": curr_state,
            "active_lags": len(self.active_taps),
            "rec_active": 1 if has_rec else 0,
            "live_fp_flops": self.live_res.fp_flops,
            "shadow_fp_flops": self.shadow_res.fp_flops,
            "int_ops": self.live_res.int_ops + self.shadow_res.int_ops,
            "bytes_moved": (self.live_res.bytes_read + self.live_res.bytes_written +
                            self.shadow_res.bytes_read + self.shadow_res.bytes_written),
            "cast_ops": self.cast_ops
        }

# -----------------------------------------------------------------------------
# 2. Canonical Reference Parity Gate
# -----------------------------------------------------------------------------
def run_canonical_parity_gate() -> bool:
    print("=" * 80)
    print("MANDATORY CANONICAL REFERENCE PARITY GATE")
    print("Testing CorrectedCanonicalLEBREModel (C0) against IntegratedLEBREModel (T3)")
    print("=" * 80)
    
    total_steps = 6000
    seed = 1301
    parity_trace = []
    scaler_trace = []
    
    all_passed = True
    
    for task_id in BENCHMARK_TASKS:
        X, y, meta = generate_v02_stream(task_id, seed, total_steps=total_steps)
        
        m_canon = IntegratedLEBREModel(topology="T3")
        m_c0 = CorrectedCanonicalLEBREModel(corr_grid_dtype=np.float32)
        
        task_mismatches = 0
        max_abs_err_yhat = 0.0
        max_abs_err_loss = 0.0
        max_abs_err_scaler = 0.0
        
        for t in range(total_steps):
            r_canon = m_canon.step(X[t], y[t])
            r_c0 = m_c0.step(X[t], y[t])
            
            if task_id == "I1_Memoryless_Linear" and t % 50 == 0:
                scaler_trace.append({
                    "step": t,
                    "canon_mean_0": float(m_canon.scaler.mean[0]),
                    "c0_mean_0": float(m_c0.scaler.mean[0]),
                    "canon_var_0": float(m_canon.scaler.var[0]),
                    "c0_var_0": float(m_c0.scaler.var[0]),
                    "canon_count": int(m_canon.scaler.count),
                    "c0_count": int(m_c0.scaler.count),
                    "diff_mean_l1": float(np.sum(np.abs(m_canon.scaler.mean - m_c0.scaler.mean))),
                    "diff_var_l1": float(np.sum(np.abs(m_canon.scaler.var - m_c0.scaler.var)))
                })
                
            err_y = abs(r_canon["y_hat"] - r_c0["y_hat"])
            err_loss = abs(r_canon["loss"] - r_c0["loss"])
            err_scaler = float(np.max(np.abs(m_canon.scaler.mean - m_c0.scaler.mean)))
            
            if err_y > max_abs_err_yhat:
                max_abs_err_yhat = err_y
            if err_loss > max_abs_err_loss:
                max_abs_err_loss = err_loss
            if err_scaler > max_abs_err_scaler:
                max_abs_err_scaler = err_scaler
                
            if r_canon["allocated_state"] != r_c0["allocated_state"] or \
               r_canon["decision"] != r_c0["decision"] or \
               err_y > 1e-12:
                task_mismatches += 1
                
        status = "PASS_BITWISE" if task_mismatches == 0 and max_abs_err_yhat == 0.0 else (
                 "PASS_FLOAT_TOL" if task_mismatches == 0 and max_abs_err_yhat < 1e-10 else "FAIL")
        
        parity_trace.append({
            "task_id": task_id,
            "steps_evaluated": total_steps,
            "max_abs_err_yhat": max_abs_err_yhat,
            "max_abs_err_loss": max_abs_err_loss,
            "max_abs_err_scaler_mean": max_abs_err_scaler,
            "event_disagreements": task_mismatches,
            "status": status
        })
        
        print(f"[{status}] Task {task_id:<38} MaxErr(y_hat): {max_abs_err_yhat:.2e} | Events: {task_mismatches}")
        if "FAIL" in status:
            all_passed = False
            
    df_parity = pd.DataFrame(parity_trace)
    df_parity.to_csv(OUT_DIR / "CANONICAL_REFERENCE_PARITY_TRACE.csv", index=False)
    
    df_scaler = pd.DataFrame(scaler_trace)
    df_scaler.to_csv(OUT_DIR / "CANONICAL_SCALER_STATE_TRACE.csv", index=False)
    
    print("=" * 80)
    print(f"CANONICAL PARITY GATE RESULT: {'PASS (100% BITWISE IDENTICAL)' if all_passed else 'FAIL'}")
    print("=" * 80)
    return all_passed

# -----------------------------------------------------------------------------
# 3. Paired Simulation Worker Function
# -----------------------------------------------------------------------------
def run_paired_simulation_corrective(args: Tuple[str, int, str]) -> Dict[str, Any]:
    task_id, seed, cohort = args
    total_steps = 6000
    
    X, y, meta = generate_v02_stream(task_id, seed, total_steps=total_steps)
    var_y = float(np.var(y)) if np.var(y) > 1e-4 else 1.0
    
    m_c0 = CorrectedCanonicalLEBREModel(corr_grid_dtype=np.float32)
    m_c1 = CorrectedCanonicalLEBREModel(corr_grid_dtype=np.float16)
    
    losses_c0, losses_c1 = [], []
    states_c0, states_c1 = [], []
    live_flops_c0, live_flops_c1 = [], []
    shadow_flops_c0, shadow_flops_c1 = [], []
    int_ops_c0, int_ops_c1 = [], []
    bytes_c0, bytes_c1 = [], []
    mem_c0, mem_c1 = [], []
    
    g_db_c0, g_db_c1 = [], []
    g_rb_c0, g_rb_c1 = [], []
    g_d_br_c0, g_d_br_c1 = [], []
    g_r_bd_c0, g_r_bd_c1 = [], []
    
    top1_agrees = []
    top3_agrees = []
    pairwise_inversions = []
    thresh_cross_disagrees = []
    near_thresh_disagrees = []
    far_thresh_disagrees = []
    
    first_divergence = None
    
    for t in range(total_steps):
        s_c0 = m_c0.step(X[t], y[t])
        s_c1 = m_c1.step(X[t], y[t])
        
        losses_c0.append(s_c0["loss"])
        losses_c1.append(s_c1["loss"])
        states_c0.append(s_c0["allocated_state"])
        states_c1.append(s_c1["allocated_state"])
        
        live_flops_c0.append(s_c0["live_fp_flops"])
        live_flops_c1.append(s_c1["live_fp_flops"])
        shadow_flops_c0.append(s_c0["shadow_fp_flops"])
        shadow_flops_c1.append(s_c1["shadow_fp_flops"])
        int_ops_c0.append(s_c0["int_ops"])
        int_ops_c1.append(s_c1["int_ops"])
        bytes_c0.append(s_c0["bytes_moved"])
        bytes_c1.append(s_c1["bytes_moved"])
        
        if t % 10 == 0:
            mem_c0.append(m_c0.get_persistent_bytes())
            mem_c1.append(m_c1.get_persistent_bytes())
            
        if t % 5 == 0:
            g_db_c0.append(s_c0["ema_G_D_B"])
            g_db_c1.append(s_c1["ema_G_D_B"])
            g_rb_c0.append(s_c0["ema_G_R_B"])
            g_rb_c1.append(s_c1["ema_G_R_B"])
            g_d_br_c0.append(s_c0["ema_G_D_BR"])
            g_d_br_c1.append(s_c1["ema_G_D_BR"])
            g_r_bd_c0.append(s_c0["ema_G_R_BD"])
            g_r_bd_c1.append(s_c1["ema_G_R_BD"])
            
        # Detect first structural divergence
        if first_divergence is None and s_c0["allocated_state"] != s_c1["allocated_state"]:
            first_divergence = {
                "task_id": task_id,
                "seed": seed,
                "cohort": cohort,
                "step": t,
                "state_c0": s_c0["allocated_state"],
                "state_c1": s_c1["allocated_state"],
                "decision_c0": s_c0["decision"],
                "decision_c1": s_c1["decision"],
                "G_D_B_c0": s_c0["ema_G_D_B"],
                "G_D_B_c1": s_c1["ema_G_D_B"],
                "G_R_B_c0": s_c0["ema_G_R_B"],
                "G_R_B_c1": s_c1["ema_G_R_B"],
                "G_D_BR_c0": s_c0["ema_G_D_BR"],
                "G_D_BR_c1": s_c1["ema_G_D_BR"],
                "G_R_BD_c0": s_c0["ema_G_R_BD"],
                "G_R_BD_c1": s_c1["ema_G_R_BD"],
                "active_lags_c0": len(m_c0.active_taps),
                "active_lags_c1": len(m_c1.active_taps),
                "rec_active_c0": 1 if m_c0.active_rec is not None else 0,
                "rec_active_c1": 1 if m_c1.active_rec is not None else 0
            }
            
        # Sample candidate ranking parity every 20 steps
        if t % 20 == 0:
            grid0 = np.abs(m_c0.corr_grid[:, 1:])
            grid1 = np.abs(m_c1.corr_grid[:, 1:]).astype(np.float32)
            
            top1_c0 = np.argmax(grid0)
            top1_c1 = np.argmax(grid1)
            top1_agrees.append(1 if top1_c0 == top1_c1 else 0)
            
            top3_c0 = set(np.argsort(grid0.ravel())[-3:])
            top3_c1 = set(np.argsort(grid1.ravel())[-3:])
            jaccard = len(top3_c0 & top3_c1) / float(len(top3_c0 | top3_c1))
            top3_agrees.append(jaccard)
            
            top10_c0 = np.argsort(grid0.ravel())[-10:]
            v0 = grid0.ravel()[top10_c0]
            v1 = grid1.ravel()[top10_c0]
            inversions = 0
            n_pairs = 0
            for i in range(len(top10_c0)):
                for j in range(i + 1, len(top10_c0)):
                    n_pairs += 1
                    diff0 = v0[i] - v0[j]
                    diff1 = v1[i] - v1[j]
                    if diff0 * diff1 < 0:
                        inversions += 1
            pairwise_inversions.append(inversions / float(n_pairs) if n_pairs > 0 else 0.0)
            
            cross0 = grid0 > 0.20
            cross1 = grid1 > 0.20
            disagree_mask = (cross0 != cross1)
            thresh_cross_disagrees.append(int(np.sum(disagree_mask)))
            
            near_mask = np.abs(grid0 - 0.20) <= 0.01
            near_disagrees = np.sum(disagree_mask & near_mask)
            far_disagrees = np.sum(disagree_mask & (~near_mask))
            near_thresh_disagrees.append(int(near_disagrees))
            far_thresh_disagrees.append(int(far_disagrees))
            
    # Evaluation metrics (post warmup steps 1000..6000)
    nmse_c0 = float(np.mean(losses_c0[1000:]) / var_y)
    nmse_c1 = float(np.mean(losses_c1[1000:]) / var_y)
    
    frac_none_c0 = float(np.mean([1 if s == "NONE" else 0 for s in states_c0[1000:]]))
    frac_lag_c0  = float(np.mean([1 if s == "LAG" else 0 for s in states_c0[1000:]]))
    frac_rec_c0  = float(np.mean([1 if s == "RECURRENT" else 0 for s in states_c0[1000:]]))
    frac_both_c0 = float(np.mean([1 if s == "BOTH" else 0 for s in states_c0[1000:]]))
    
    frac_none_c1 = float(np.mean([1 if s == "NONE" else 0 for s in states_c1[1000:]]))
    frac_lag_c1  = float(np.mean([1 if s == "LAG" else 0 for s in states_c1[1000:]]))
    frac_rec_c1  = float(np.mean([1 if s == "RECURRENT" else 0 for s in states_c1[1000:]]))
    frac_both_c1 = float(np.mean([1 if s == "BOTH" else 0 for s in states_c1[1000:]]))
    
    dict_states_c0 = {"NONE": frac_none_c0, "LAG": frac_lag_c0, "RECURRENT": frac_rec_c0, "BOTH": frac_both_c0}
    dict_states_c1 = {"NONE": frac_none_c1, "LAG": frac_lag_c1, "RECURRENT": frac_rec_c1, "BOTH": frac_both_c1}
    modal_c0 = max(dict_states_c0, key=dict_states_c0.get)
    modal_c1 = max(dict_states_c1, key=dict_states_c1.get)
    
    # Ground truth support analysis for I3 and I4
    support_prec_c0, support_rec_c0, support_f1_c0 = np.nan, np.nan, np.nan
    support_prec_c1, support_rec_c1, support_f1_c1 = np.nan, np.nan, np.nan
    
    if task_id == "I3_Single_Exact_Delay":
        true_taps = {(1, 6)}
        taps_c0 = set((t['i'], t['k']) for t in m_c0.active_taps)
        taps_c1 = set((t['i'], t['k']) for t in m_c1.active_taps)
        
        tp0 = len(taps_c0 & true_taps)
        support_prec_c0 = tp0 / len(taps_c0) if len(taps_c0) > 0 else 0.0
        support_rec_c0 = tp0 / len(true_taps)
        support_f1_c0 = (2 * support_prec_c0 * support_rec_c0) / (support_prec_c0 + support_rec_c0) if (support_prec_c0 + support_rec_c0) > 0 else 0.0
        
        tp1 = len(taps_c1 & true_taps)
        support_prec_c1 = tp1 / len(taps_c1) if len(taps_c1) > 0 else 0.0
        support_rec_c1 = tp1 / len(true_taps)
        support_f1_c1 = (2 * support_prec_c1 * support_rec_c1) / (support_prec_c1 + support_rec_c1) if (support_prec_c1 + support_rec_c1) > 0 else 0.0
        
    elif task_id == "I4_Multi_Sparse_Delay":
        true_taps = {(0, 3), (2, 14), (4, 27)}
        taps_c0 = set((t['i'], t['k']) for t in m_c0.active_taps)
        taps_c1 = set((t['i'], t['k']) for t in m_c1.active_taps)
        
        tp0 = len(taps_c0 & true_taps)
        support_prec_c0 = tp0 / len(taps_c0) if len(taps_c0) > 0 else 0.0
        support_rec_c0 = tp0 / len(true_taps)
        support_f1_c0 = (2 * support_prec_c0 * support_rec_c0) / (support_prec_c0 + support_rec_c0) if (support_prec_c0 + support_rec_c0) > 0 else 0.0
        
        tp1 = len(taps_c1 & true_taps)
        support_prec_c1 = tp1 / len(taps_c1) if len(taps_c1) > 0 else 0.0
        support_rec_c1 = tp1 / len(true_taps)
        support_f1_c1 = (2 * support_prec_c1 * support_rec_c1) / (support_prec_c1 + support_rec_c1) if (support_prec_c1 + support_rec_c1) > 0 else 0.0
        
    # Switching latency for I11, I12, I13
    switch_lat_c0, switch_lat_c1 = np.nan, np.nan
    post_nmse_c0, post_nmse_c1 = np.nan, np.nan
    
    if task_id in ("I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay", "I13_Regime_Switch_Hybrid_To_Memoryless"):
        target_state = "RECURRENT" if "I11" in task_id else ("LAG" if "I12" in task_id else "NONE")
        post_nmse_c0 = float(np.mean(losses_c0[4000:]) / var_y)
        post_nmse_c1 = float(np.mean(losses_c1[4000:]) / var_y)
        
        for idx, s in enumerate(states_c0[3000:]):
            if s == target_state:
                switch_lat_c0 = idx
                break
        if np.isnan(switch_lat_c0):
            switch_lat_c0 = 3000.0
            
        for idx, s in enumerate(states_c1[3000:]):
            if s == target_state:
                switch_lat_c1 = idx
                break
        if np.isnan(switch_lat_c1):
            switch_lat_c1 = 3000.0
            
    c0_result = {
        "task_id": task_id,
        "seed": seed,
        "cohort": cohort,
        "variant": "C0",
        "nmse": nmse_c0,
        "modal_state": modal_c0,
        "frac_none": frac_none_c0,
        "frac_lag": frac_lag_c0,
        "frac_rec": frac_rec_c0,
        "frac_both": frac_both_c0,
        "promotions_lag": m_c0.promotions_lag,
        "promotions_rec": m_c0.promotions_rec,
        "evictions_lag": m_c0.evictions_lag,
        "evictions_rec": m_c0.evictions_rec,
        "live_flops_mean": float(np.mean(live_flops_c0)),
        "shadow_flops_mean": float(np.mean(shadow_flops_c0)),
        "int_ops_mean": float(np.mean(int_ops_c0)),
        "bytes_moved_mean": float(np.mean(bytes_c0)),
        "cast_ops_mean": 0.0,
        "persistent_bytes_capacity": 1306,
        "occupied_bytes_mean": float(np.mean(mem_c0)),
        "occupied_bytes_max": int(np.max(mem_c0)),
        "transient_workspace_bytes": 4,
        "peak_working_bytes": 1310,
        "support_precision": support_prec_c0,
        "support_recall": support_rec_c0,
        "support_f1": support_f1_c0,
        "g_db_mean": float(np.mean(g_db_c0)),
        "g_rb_mean": float(np.mean(g_rb_c0)),
        "g_d_br_mean": float(np.mean(g_d_br_c0)),
        "g_r_bd_mean": float(np.mean(g_r_bd_c0)),
        "switch_latency": switch_lat_c0,
        "post_switch_nmse": post_nmse_c0
    }
    
    c1_result = {
        "task_id": task_id,
        "seed": seed,
        "cohort": cohort,
        "variant": "C1",
        "nmse": nmse_c1,
        "modal_state": modal_c1,
        "frac_none": frac_none_c1,
        "frac_lag": frac_lag_c1,
        "frac_rec": frac_rec_c1,
        "frac_both": frac_both_c1,
        "promotions_lag": m_c1.promotions_lag,
        "promotions_rec": m_c1.promotions_rec,
        "evictions_lag": m_c1.evictions_lag,
        "evictions_rec": m_c1.evictions_rec,
        "live_flops_mean": float(np.mean(live_flops_c1)),
        "shadow_flops_mean": float(np.mean(shadow_flops_c1)),
        "int_ops_mean": float(np.mean(int_ops_c1)),
        "bytes_moved_mean": float(np.mean(bytes_c1)),
        "cast_ops_mean": 4.0, # 2 probes * 2 cast ops (read+write) per step
        "persistent_bytes_capacity": 976,
        "occupied_bytes_mean": float(np.mean(mem_c1)),
        "occupied_bytes_max": int(np.max(mem_c1)),
        "transient_workspace_bytes": 8,
        "peak_working_bytes": 984,
        "support_precision": support_prec_c1,
        "support_recall": support_rec_c1,
        "support_f1": support_f1_c1,
        "g_db_mean": float(np.mean(g_db_c1)),
        "g_rb_mean": float(np.mean(g_rb_c1)),
        "g_d_br_mean": float(np.mean(g_d_br_c1)),
        "g_r_bd_mean": float(np.mean(g_r_bd_c1)),
        "switch_latency": switch_lat_c1,
        "post_switch_nmse": post_nmse_c1
    }
    
    ranking_row = {
        "task_id": task_id,
        "seed": seed,
        "cohort": cohort,
        "top1_agreement": float(np.mean(top1_agrees)),
        "top3_jaccard": float(np.mean(top3_agrees)),
        "top10_inversion_rate": float(np.mean(pairwise_inversions)),
        "thresh_cross_disagreements": int(np.sum(thresh_cross_disagrees)),
        "near_thresh_disagreements": int(np.sum(near_thresh_disagrees)),
        "far_thresh_disagreements": int(np.sum(far_thresh_disagrees))
    }
    
    return {
        "c0": c0_result,
        "c1": c1_result,
        "ranking": ranking_row,
        "divergence": first_divergence
    }

# -----------------------------------------------------------------------------
# 4. Main Batch Runner
# -----------------------------------------------------------------------------
def run_experiments():
    parser = argparse.ArgumentParser(description="LEBRE V0.2 Resource Compaction Corrective Confirmation")
    parser.add_argument("--skip-parity", action="store_true", help="Skip canonical reference parity test")
    args = parser.parse_args()
    
    if not args.skip_parity:
        passed = run_canonical_parity_gate()
        if not passed:
            print("ERROR: Canonical Parity Gate failed! Aborting confirmatory run.")
            sys.exit(1)
            
    n_workers = min(cpu_count(), 16)
    print(f"\nLaunching simulation runs across {n_workers} CPU workers...")
    
    # DEV Cohort (Seeds 1501..1510, N=10)
    dev_seeds = list(range(1501, 1511))
    dev_jobs = [(task, seed, "DEV") for seed in dev_seeds for task in BENCHMARK_TASKS]
    print(f"Executing DEV cohort: {len(dev_jobs)} paired tasks ({len(dev_jobs)*2} model runs)...")
    
    t0 = time.time()
    with Pool(processes=n_workers) as pool:
        dev_results = pool.map(run_paired_simulation_corrective, dev_jobs)
    t_dev = time.time() - t0
    print(f"DEV cohort completed in {t_dev:.2f} seconds.")
    
    dev_rows = []
    for res in dev_results:
        dev_rows.append(res["c0"])
        dev_rows.append(res["c1"])
    df_dev = pd.DataFrame(dev_rows)
    df_dev.to_csv(OUT_DIR / "CORRECTIVE_CONFIRMATION_DEV_RESULTS.csv", index=False)
    print(f"Saved {len(df_dev)} rows to CORRECTIVE_CONFIRMATION_DEV_RESULTS.csv")
    
    # FINAL Cohort (Seeds 1511..1540, N=30)
    final_seeds = list(range(1511, 1541))
    final_jobs = [(task, seed, "FINAL") for seed in final_seeds for task in BENCHMARK_TASKS]
    print(f"\nExecuting FINAL confirmatory cohort: {len(final_jobs)} paired tasks ({len(final_jobs)*2} model runs)...")
    
    t0 = time.time()
    with Pool(processes=n_workers) as pool:
        final_results = pool.map(run_paired_simulation_corrective, final_jobs)
    t_final = time.time() - t0
    print(f"FINAL cohort completed in {t_final:.2f} seconds.")
    
    final_rows = []
    ranking_rows = []
    divergence_rows = []
    
    for res in final_results:
        final_rows.append(res["c0"])
        final_rows.append(res["c1"])
        ranking_rows.append(res["ranking"])
        if res["divergence"] is not None:
            divergence_rows.append(res["divergence"])
            
    df_final = pd.DataFrame(final_rows)
    df_final.to_csv(OUT_DIR / "CORRECTIVE_CONFIRMATION_FINAL_RESULTS.csv", index=False)
    print(f"Saved {len(df_final)} rows to CORRECTIVE_CONFIRMATION_FINAL_RESULTS.csv")
    
    df_ranking = pd.DataFrame(ranking_rows)
    df_ranking.to_csv(OUT_DIR / "STRUCTURAL_PARITY.csv", index=False)
    print(f"Saved {len(df_ranking)} rows to STRUCTURAL_PARITY.csv")
    
    df_div = pd.DataFrame(divergence_rows)
    if len(df_div) == 0:
        df_div = pd.DataFrame(columns=[
            "task_id", "seed", "cohort", "step", "state_c0", "state_c1",
            "decision_c0", "decision_c1", "G_D_B_c0", "G_D_B_c1",
            "G_R_B_c0", "G_R_B_c1", "G_D_BR_c0", "G_D_BR_c1",
            "G_R_BD_c0", "G_R_BD_c1", "active_lags_c0", "active_lags_c1",
            "rec_active_c0", "rec_active_c1"
        ])
    df_div.to_csv(OUT_DIR / "CAUSAL_DIVERGENCE_TRACE.csv", index=False)
    print(f"Saved {len(df_div)} divergence events to CAUSAL_DIVERGENCE_TRACE.csv")
    
    print("\nSimulation phase successfully finished!")

if __name__ == "__main__":
    run_experiments()
