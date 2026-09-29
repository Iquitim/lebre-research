#!/usr/bin/env python3
"""
run_v02_integration_experiments.py: Comprehensive Execution Engine for
LEBRE-V0.2-INTEGRATION-DESIGN-01.

Implements:
- CausalStandardScaler & FP16HistoryRingBuffer
- Topologies:
  - T1: Ordered Residual Cascade (Base -> Lag -> Recurrent)
  - T1R: Reversed Residual Cascade (Base -> Recurrent -> Lag) [Order-Bias Control]
  - T2: Symmetric Shadow Competition (Parallel shadow evaluation)
  - T3: Resource-Aware Conditional Arbitration (Symmetric shadow + conditional gains + Pareto dominance)
  - O_ALL: Always-On Oracle (Diagnostic ceiling)
  - E_EXP: Online Expert Weighting (Diagnostic benchmark)
- Full 4-Channel Disaggregated Resource Accounting (Live vs. Shadow)
- Strict Prequential Evaluation (zero future or label leakage)
"""

import os
import sys
import time
import argparse
import csv
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream

OUT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Hardware Resource Counter & Ledger
# -----------------------------------------------------------------------------
class ResourceVector:
    def __init__(self):
        self.fp_flops = 0.0
        self.int_ops = 0.0
        self.bytes_read = 0.0
        self.bytes_written = 0.0
        self.persistent_bytes = 0.0
        
    def reset_step(self):
        self.fp_flops = 0.0
        self.int_ops = 0.0
        self.bytes_read = 0.0
        self.bytes_written = 0.0

# -----------------------------------------------------------------------------
# 2. Causal Online Standard Scaler
# -----------------------------------------------------------------------------
class CausalStandardScaler:
    def __init__(self, d: int = 5, eps: float = 1e-4):
        self.d = d
        self.eps = eps
        self.mean = np.zeros(d, dtype=np.float64)
        self.var = np.ones(d, dtype=np.float64)
        self.count = 0
        
    def transform(self, x: np.ndarray, res: Optional[ResourceVector] = None) -> np.ndarray:
        if res:
            res.fp_flops += 2 * self.d # sub mean, div std
            res.bytes_read += self.d * 8 * 2
        std = np.sqrt(self.var + self.eps)
        return (x - self.mean) / std
        
    def update(self, x: np.ndarray, res: Optional[ResourceVector] = None):
        self.count += 1
        alpha = min(0.05, 1.0 / self.count)
        diff = x - self.mean
        self.mean += alpha * diff
        self.var = (1.0 - alpha) * self.var + alpha * (diff ** 2)
        if res:
            res.fp_flops += 4 * self.d
            res.bytes_written += self.d * 8 * 2

# -----------------------------------------------------------------------------
# 3. FP16 Exact Addressable Circular Ring Buffer
# -----------------------------------------------------------------------------
class FP16HistoryRingBuffer:
    def __init__(self, d_features: int = 5, l_max: int = 32):
        self.D = d_features
        self.L_max = l_max
        self.buffer = np.zeros((d_features, l_max + 1), dtype=np.float16)
        self.head = 0
        
    def write(self, x: np.ndarray, res: Optional[ResourceVector] = None):
        self.buffer[:, self.head] = x.astype(np.float16)
        self.head = (self.head + 1) % (self.L_max + 1)
        if res:
            res.int_ops += self.D + 2 # 5 casts + 1 mod + 1 add
            res.bytes_written += self.D * 2 # 10 bytes for 5 FP16 words
            
    def query(self, i: int, k: int, res: Optional[ResourceVector] = None) -> float:
        idx = (self.head - 1 - k) % (self.L_max + 1)
        val = float(self.buffer[i, idx])
        if res:
            res.int_ops += 4 # 2 sub, 1 mod, 1 cast to float32
            res.bytes_read += 2 # 2 bytes loaded
        return val
        
    def get_memory_bytes(self) -> int:
        return self.D * (self.L_max + 1) * 2 + 2 # 330 bytes buffer + 2 bytes head

# -----------------------------------------------------------------------------
# 4. Instantaneous Linear Baseline Learner
# -----------------------------------------------------------------------------
class LinearBasePredictor:
    def __init__(self, d_features: int = 5, lr: float = 0.10):
        self.d = d_features
        self.lr = lr
        self.w = np.zeros(d_features, dtype=np.float64)
        
    def predict(self, x: np.ndarray, res: Optional[ResourceVector] = None) -> float:
        pred = float(np.dot(self.w, x))
        if res:
            res.fp_flops += 2 * self.d # 5 mul + 5 add
            res.bytes_read += self.d * 8 * 2
        return pred
        
    def update(self, x: np.ndarray, err: float, res: Optional[ResourceVector] = None):
        norm = float(np.dot(x, x)) + 1e-4
        step = (self.lr / norm) * err
        self.w += step * x
        if res:
            res.fp_flops += 3 * self.d + 3
            res.bytes_written += self.d * 8
            
    def get_memory_bytes(self) -> int:
        return self.d * 8 # 40 bytes

# -----------------------------------------------------------------------------
# 5. Continuous Recurrent Latent Unit (N=1)
# -----------------------------------------------------------------------------
class RecurrentScalarUnit:
    def __init__(self, lr: float = 0.05):
        self.lr = lr
        self.alpha = 0.8
        self.b = 0.5
        self.c = 0.5
        self.s = 0.0
        self.p_alpha = 0.0
        self.p_b = 0.0
        
    def forward(self, x_scalar: float, res: Optional[ResourceVector] = None) -> Tuple[float, float]:
        a = float(np.tanh(self.alpha))
        dtanh = 1.0 - a ** 2
        self.p_alpha = a * self.p_alpha + dtanh * self.s
        self.p_b = a * self.p_b + x_scalar
        self.s = a * self.s + self.b * x_scalar
        pred = self.c * self.s
        if res:
            res.fp_flops += 18.0
            res.bytes_read += 24.0
        return self.s, pred
        
    def update(self, err: float, x_scalar: float, res: Optional[ResourceVector] = None):
        grad_alpha = - err * self.c * self.p_alpha
        grad_b = - err * self.c * self.p_b
        grad_c = - err * self.s
        norm_sq = (self.c * self.p_alpha) ** 2 + (self.c * self.p_b) ** 2 + (self.s ** 2) + 1e-4
        step = self.lr / (norm_sq + 1.0)
        self.alpha = float(np.clip(self.alpha - step * grad_alpha, -4.0, 4.0))
        self.b = float(np.clip(self.b - step * grad_b, -4.0, 4.0))
        self.c = float(np.clip(self.c - step * grad_c, -4.0, 4.0))
        if res:
            res.fp_flops += 16.0
            res.bytes_written += 24.0
            
    def get_memory_bytes(self) -> int:
        return 48 # s, alpha, b, c, p_alpha, p_b (6 * 8 = 48 bytes)

# -----------------------------------------------------------------------------
# 6. Integrated Model Container Supporting All 5 Topologies
# -----------------------------------------------------------------------------
class IntegratedLEBREModel:
    def __init__(
        self,
        topology: str,
        d_features: int = 5,
        l_max: int = 32,
        k_max: int = 4,
        theta_tol: float = 0.015
    ):
        self.topology = topology # "T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"
        self.D = d_features
        self.L_max = l_max
        self.K_max = k_max
        self.theta_tol = theta_tol
        
        self.scaler = CausalStandardScaler(d=d_features)
        self.history = FP16HistoryRingBuffer(d_features=d_features, l_max=l_max)
        self.base = LinearBasePredictor(d_features=d_features)
        
        # Discrete Lags state
        self.active_taps: List[Dict[str, Any]] = [] # [{'i': int, 'k': int, 'w': float, 'R': float, 'age': int}]
        self.provisional_cands: List[Dict[str, Any]] = [] # [{'i': int, 'k': int, 'w': float, 'evidence': float, 'age': int}]
        self.corr_grid = np.zeros((d_features, l_max + 1), dtype=np.float32)
        self.grid_pairs = [(i, k) for i in range(d_features) for k in range(1, l_max + 1)]
        self.probe_ptr = 0
        
        # Recurrent unit state
        self.active_rec: Optional[RecurrentScalarUnit] = None
        self.shadow_rec = RecurrentScalarUnit()
        self.rec_evidence = 0.0
        self.rec_age = 0
        self.rec_status = "NONE" # "NONE", "PROBATION", "ACTIVE"
        
        # Expert advice state for E_EXP
        if self.topology == "E_EXP":
            self.expert_weights = np.ones(4) / 4.0 # E0: Base, E1: Base+Lag, E2: Base+Rec, E3: Base+Lag+Rec
            self.eta = 0.5
            self.alpha_share = 0.01
            
        # Filtered conditional gains for T3
        self.ema_G_D_B = 0.0
        self.ema_G_R_B = 0.0
        self.ema_G_D_BR = 0.0
        self.ema_G_R_BD = 0.0
        self.arbitration_decision = "NONE"
        
        # Resource accounting
        self.live_res = ResourceVector()
        self.shadow_res = ResourceVector()
        
        # Counters for stats
        self.step_count = 0
        self.promotions_lag = 0
        self.promotions_rec = 0
        self.evictions_lag = 0
        self.evictions_rec = 0
        self.dual_active_steps = 0
        self.redundant_dual_steps = 0
        
    def get_persistent_bytes(self) -> int:
        mem = self.scaler.d * 16 # scaler mean, var
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
        
        # Helper for delayed query
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
        # Shadow lag evaluation: use active taps if present, else best provisional candidate
        if len(self.active_taps) > 0:
            y_lag_eval = y_lag_live
        elif len(self.provisional_cands) > 0:
            best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
            c_val = query_delayed(best_cand['i'], best_cand['k'], is_shadow=True)
            y_lag_eval = best_cand['w'] * c_val
            self.shadow_res.fp_flops += 2.0
        else:
            y_lag_eval = 0.0
            
        # Shadow recurrent evaluation: use active if present, else shadow if evidence is non-negative
        _, y_rec_shadow_val = self.shadow_rec.forward(x_norm[0], self.shadow_res)
        if self.active_rec is not None:
            y_rec_eval = y_rec_live
        elif self.rec_evidence > 0.02 and self.rec_age >= 15:
            y_rec_eval = y_rec_shadow_val
        else:
            y_rec_eval = 0.0
        
        # Counterfactual loss grid (computed before revealing y_true)
        P_BASE = y_base
        P_BASE_D = y_base + y_lag_eval
        P_BASE_R = y_base + y_rec_eval
        P_BASE_D_R = y_base + y_lag_eval + y_rec_eval
        
        # Step 7: Live Prediction based on topology
        if self.topology in ("T1", "T1R", "T2", "T3"):
            y_hat_live = y_base + y_lag_live + y_rec_live
        elif self.topology == "O_ALL":
            y_hat_live = P_BASE_D_R
        elif self.topology == "E_EXP":
            preds = np.array([P_BASE, P_BASE_D, P_BASE_R, P_BASE_D_R])
            y_hat_live = float(np.dot(self.expert_weights, preds))
            self.live_res.fp_flops += 8.0
        else:
            y_hat_live = y_base
            
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
        # Update linear base
        if self.topology == "T1":
            # Lag-first cascade: base updates on live error
            self.base.update(x_norm, e_live, self.live_res)
        elif self.topology == "T1R":
            self.base.update(x_norm, e_live, self.live_res)
        else:
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
        e_for_probe = (y_true - (y_base + y_lag_live)) if self.topology == "T1" else (y_true - y_base)
        for _ in range(2):
            i_p, k_p = self.grid_pairs[self.probe_ptr]
            self.probe_ptr = (self.probe_ptr + 1) % len(self.grid_pairs)
            if not any(t['i'] == i_p and t['k'] == k_p for t in self.active_taps) and \
               not any(c['i'] == i_p and c['k'] == k_p for c in self.provisional_cands):
                c_val = query_delayed(i_p, k_p, is_shadow=True)
                self.corr_grid[i_p, k_p] = 0.95 * self.corr_grid[i_p, k_p] + 0.05 * (e_for_probe * c_val)
                if abs(self.corr_grid[i_p, k_p]) > 0.20 and len(self.provisional_cands) < 3:
                    self.provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w': float(self.corr_grid[i_p, k_p]),
                        'evidence': 0.05, 'age': 0
                    })
                self.shadow_res.fp_flops += 4.0
                
        # Step 11: Arbitration & Promotion Logic
        decision = "NONE"
        if self.topology == "T1": # Lag-first cascade
            # Lag candidate promotion
            for cand in list(self.provisional_cands):
                if cand['evidence'] >= 0.12 and cand['age'] >= 25:
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                        self.provisional_cands.remove(cand)
                        self.promotions_lag += 1
            # Recurrent promotion only if remaining residual is significant
            if self.rec_evidence >= 0.14 and self.rec_age >= 60 and self.active_rec is None:
                self.active_rec = RecurrentScalarUnit()
                self.active_rec.alpha = self.shadow_rec.alpha
                self.active_rec.b = self.shadow_rec.b
                self.active_rec.c = self.shadow_rec.c
                self.promotions_rec += 1
                
        elif self.topology == "T1R": # Recurrent-first cascade
            if self.rec_evidence >= 0.12 and self.rec_age >= 40 and self.active_rec is None:
                self.active_rec = RecurrentScalarUnit()
                self.active_rec.alpha = self.shadow_rec.alpha
                self.active_rec.b = self.shadow_rec.b
                self.active_rec.c = self.shadow_rec.c
                self.promotions_rec += 1
            for cand in list(self.provisional_cands):
                if cand['evidence'] >= 0.14 and cand['age'] >= 30:
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                        self.provisional_cands.remove(cand)
                        self.promotions_lag += 1
                        
        elif self.topology == "T2": # Symmetric shadow competition (independent promotions)
            for cand in list(self.provisional_cands):
                if cand['evidence'] >= 0.12 and cand['age'] >= 25:
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': cand['evidence'], 'age': 0})
                        self.provisional_cands.remove(cand)
                        self.promotions_lag += 1
            if self.rec_evidence >= 0.12 and self.rec_age >= 40 and self.active_rec is None:
                self.active_rec = RecurrentScalarUnit()
                self.active_rec.alpha = self.shadow_rec.alpha
                self.active_rec.b = self.shadow_rec.b
                self.active_rec.c = self.shadow_rec.c
                self.promotions_rec += 1
                
        elif self.topology == "T3": # Resource-Aware Conditional Arbitration
            # Evaluate conditional gains against threshold theta_tol
            d_helps = self.ema_G_D_B > self.theta_tol
            r_helps = self.ema_G_R_B > self.theta_tol
            d_cond = self.ema_G_D_BR > self.theta_tol
            r_cond = self.ema_G_R_BD > self.theta_tol
            
            if not d_helps and not r_helps:
                decision = "NONE"
                # Evict active if gains decayed
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
            else: # Both have standalone gain!
                if d_cond and r_cond:
                    decision = "BOTH" # True hybrid complementarity!
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
                    decision = "REDUNDANT" # One explains the other; do NOT pay twice!
                    # Prefer Pareto dominant: Discrete lag has lower memory traffic and lower FP FLOPs
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
            
        elif self.topology == "O_ALL":
            decision = "BOTH"
            if self.active_rec is None:
                self.active_rec = RecurrentScalarUnit()
            if len(self.active_taps) < self.K_max:
                for cand in list(self.provisional_cands):
                    self.active_taps.append({'i': cand['i'], 'k': cand['k'], 'w': cand['w'], 'R': 1.0, 'age': 0})
                    self.provisional_cands.remove(cand)
                    
        elif self.topology == "E_EXP":
            # Update online expert weights
            losses = np.array([ell_B, ell_BD, ell_BR, ell_BDR])
            unnorm_w = self.expert_weights * np.exp(- self.eta * (losses - np.min(losses)))
            unnorm_w = unnorm_w / np.sum(unnorm_w)
            self.expert_weights = (1.0 - self.alpha_share) * unnorm_w + self.alpha_share / 4.0
            best_idx = int(np.argmax(self.expert_weights))
            decision = ["NONE", "LAG_ONLY", "RECURRENT_ONLY", "BOTH"][best_idx]
            self.arbitration_decision = decision

        # Prune stale candidates
        self.provisional_cands = [c for c in self.provisional_cands if not (c['age'] > 150 and c['evidence'] < 0.02)]
        
        # Track dual active occupancy
        has_lag = len(self.active_taps) > 0
        has_rec = self.active_rec is not None
        if has_lag and has_rec:
            self.dual_active_steps += 1
            if decision == "REDUNDANT" or (self.ema_G_D_BR <= self.theta_tol and self.ema_G_R_BD <= self.theta_tol):
                self.redundant_dual_steps += 1
                
        # Scaler update
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
            "decision": decision,
            "allocated_state": curr_state,
            "active_lags": len(self.active_taps),
            "rec_active": 1 if has_rec else 0,
            "live_fp_flops": self.live_res.fp_flops,
            "shadow_fp_flops": self.shadow_res.fp_flops,
            "int_ops": self.live_res.int_ops + self.shadow_res.int_ops,
            "bytes_moved": self.live_res.bytes_read + self.live_res.bytes_written + self.shadow_res.bytes_read + self.shadow_res.bytes_written,
            "persistent_bytes": self.get_persistent_bytes()
        }

# -----------------------------------------------------------------------------
# 7. Experiment Runner Function
# -----------------------------------------------------------------------------
def run_single_simulation(
    task_id: str,
    seed: int,
    topology: str,
    total_steps: int = 6000
) -> Dict[str, Any]:
    X, y, meta = generate_v02_stream(task_id, seed, total_steps=total_steps)
    model = IntegratedLEBREModel(topology=topology, d_features=5, l_max=32)
    
    losses = []
    live_flops = []
    shadow_flops = []
    int_ops = []
    bytes_moved = []
    allocated_states = []
    active_lags_history = []
    rec_active_history = []
    
    g_db_list = []
    g_rb_list = []
    g_d_br_list = []
    g_r_bd_list = []
    
    for t in range(total_steps):
        step_info = model.step(X[t], y[t])
        losses.append(step_info["loss"])
        live_flops.append(step_info["live_fp_flops"])
        shadow_flops.append(step_info["shadow_fp_flops"])
        int_ops.append(step_info["int_ops"])
        bytes_moved.append(step_info["bytes_moved"])
        allocated_states.append(step_info["allocated_state"])
        active_lags_history.append(step_info["active_lags"])
        rec_active_history.append(step_info["rec_active"])
        
        # Subsample gains every 5 steps to limit memory
        if t % 5 == 0:
            g_db_list.append(step_info["G_D_B"])
            g_rb_list.append(step_info["G_R_B"])
            g_d_br_list.append(step_info["G_D_BR"])
            g_r_bd_list.append(step_info["G_R_BD"])
            
    # Evaluation metrics
    var_y = np.var(y) if np.var(y) > 1e-4 else 1.0
    nmse = float(np.mean(losses[1000:]) / var_y) # Steady-state NMSE post warmup
    
    # State occupancy proportions
    total_eval = len(allocated_states[1000:])
    frac_none = float(np.mean([1 if s == "NONE" else 0 for s in allocated_states[1000:]]))
    frac_lag = float(np.mean([1 if s == "LAG" else 0 for s in allocated_states[1000:]]))
    frac_rec = float(np.mean([1 if s == "RECURRENT" else 0 for s in allocated_states[1000:]]))
    frac_both = float(np.mean([1 if s == "BOTH" else 0 for s in allocated_states[1000:]]))
    
    # Modal allocated state in steady state
    states_count = {
        "NONE": frac_none,
        "LAG": frac_lag,
        "RECURRENT": frac_rec,
        "BOTH": frac_both
    }
    modal_state = max(states_count, key=states_count.get)
    
    return {
        "task_id": task_id,
        "seed": seed,
        "topology": topology,
        "expected_class": meta["expected_class"],
        "modal_state": modal_state,
        "nmse": nmse,
        "frac_none": frac_none,
        "frac_lag": frac_lag,
        "frac_rec": frac_rec,
        "frac_both": frac_both,
        "mean_active_lags": float(np.mean(active_lags_history[1000:])),
        "mean_rec_active": float(np.mean(rec_active_history[1000:])),
        "redundant_dual_rate": float(model.redundant_dual_steps / total_steps),
        "promotions_lag": model.promotions_lag,
        "promotions_rec": model.promotions_rec,
        "evictions_lag": model.evictions_lag,
        "evictions_rec": model.evictions_rec,
        "live_flops_mean": float(np.mean(live_flops)),
        "live_flops_p95": float(np.percentile(live_flops, 95)),
        "live_flops_peak": float(np.max(live_flops)),
        "shadow_flops_mean": float(np.mean(shadow_flops)),
        "int_ops_mean": float(np.mean(int_ops)),
        "bytes_moved_mean": float(np.mean(bytes_moved)),
        "persistent_bytes": model.get_persistent_bytes(),
        "g_db_mean": float(np.mean(g_db_list)),
        "g_rb_mean": float(np.mean(g_rb_list)),
        "g_d_br_mean": float(np.mean(g_d_br_list)),
        "g_r_bd_mean": float(np.mean(g_r_bd_list))
    }

# -----------------------------------------------------------------------------
# 8. Batch Benchmark Execution Harness
# -----------------------------------------------------------------------------
def run_experiments(mode: str = "dev"):
    if mode == "dev":
        seeds = list(range(1301, 1311)) # N=10 dev seeds
        print(f"=== RUNNING DEVELOPMENT SCREENING (N=10 seeds: 1301..1310) ===")
    elif mode == "final":
        seeds = list(range(1311, 1341)) # N=30 final seeds
        print(f"=== RUNNING FINAL CONFIRMATORY AUDIT (N=30 seeds: 1311..1340) ===")
    else:
        raise ValueError(f"Unknown mode: {mode}")
        
    topologies = ["T1", "T1R", "T2", "T3", "O_ALL"]
    tasks = BENCHMARK_TASKS
    
    total_runs = len(seeds) * len(tasks) * len(topologies)
    print(f"Total Simulation Runs: {len(seeds)} seeds x {len(tasks)} tasks x {len(topologies)} topologies = {total_runs} runs")
    
    results = []
    start_time = time.time()
    run_idx = 0
    
    for seed in seeds:
        for task_id in tasks:
            for topo in topologies:
                run_idx += 1
                res = run_single_simulation(task_id, seed, topo, total_steps=6000)
                results.append(res)
                if run_idx % 50 == 0 or run_idx == total_runs:
                    elapsed = time.time() - start_time
                    fps = run_idx / elapsed
                    eta = (total_runs - run_idx) / fps
                    print(f"  Completed {run_idx}/{total_runs} ({run_idx*100.0/total_runs:.1f}%) | {elapsed:.1f}s elapsed | ETA {eta:.1f}s...")
                    
    # Export results CSV
    prefix = "DEV_" if mode == "dev" else "FINAL_"
    res_file = OUT_DIR / f"{prefix}LEBRE_V0_2_SEED_RESULTS.csv"
    if mode == "final":
        res_file = OUT_DIR / "LEBRE_V0_2_SEED_RESULTS.csv"
        
    fieldnames = list(results[0].keys())
    with open(res_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSuccessfully exported {len(results)} rows to {res_file}")
    
    # Export run manifest
    manifest_file = OUT_DIR / ("DEV_RUN_MANIFEST.csv" if mode == "dev" else "LEBRE_V0_2_RUN_MANIFEST.csv")
    with open(manifest_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "task_id", "seed", "topology", "status"])
        for i, r in enumerate(results):
            writer.writerow([i+1, r["task_id"], r["seed"], r["topology"], "COMPLETED"])
    print(f"Successfully exported run manifest to {manifest_file}")
    
    # Export structural events CSV
    events_file = OUT_DIR / ("DEV_STRUCTURAL_EVENTS.csv" if mode == "dev" else "LEBRE_V0_2_STRUCTURAL_EVENTS.csv")
    with open(events_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_id", "seed", "topology", "promotions_lag", "promotions_rec", "evictions_lag", "evictions_rec", "redundant_dual_rate", "modal_state"])
        for r in results:
            writer.writerow([r["task_id"], r["seed"], r["topology"], r["promotions_lag"], r["promotions_rec"], r["evictions_lag"], r["evictions_rec"], r["redundant_dual_rate"], r["modal_state"]])
    print(f"Successfully exported structural events to {events_file}")
    
    # Export conditional gains CSV
    gains_file = OUT_DIR / ("DEV_CONDITIONAL_GAINS.csv" if mode == "dev" else "LEBRE_V0_2_CONDITIONAL_GAINS.csv")
    with open(gains_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_id", "seed", "topology", "G_D_B", "G_R_B", "G_D_BR", "G_R_BD"])
        for r in results:
            writer.writerow([r["task_id"], r["seed"], r["topology"], r["g_db_mean"], r["g_rb_mean"], r["g_d_br_mean"], r["g_r_bd_mean"]])
    print(f"Successfully exported conditional gains to {gains_file}")
    
    # Export resource trace CSV
    trace_file = OUT_DIR / ("DEV_RESOURCE_TRACE.csv" if mode == "dev" else "LEBRE_V0_2_RESOURCE_TRACE.csv")
    with open(trace_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_id", "seed", "topology", "live_flops_mean", "live_flops_p95", "live_flops_peak", "shadow_flops_mean", "int_ops_mean", "bytes_moved_mean", "persistent_bytes"])
        for r in results:
            writer.writerow([r["task_id"], r["seed"], r["topology"], r["live_flops_mean"], r["live_flops_p95"], r["live_flops_peak"], r["shadow_flops_mean"], r["int_ops_mean"], r["bytes_moved_mean"], r["persistent_bytes"]])
    print(f"Successfully exported resource trace to {trace_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dev", "final", "test"], default="dev")
    args = parser.parse_args()
    
    if args.mode == "test":
        print("Executing single-run diagnostic test...")
        t_start = time.time()
        res = run_single_simulation("I9_Hybrid_Delay_Plus_Latent_State", 1301, "T3", total_steps=2000)
        print(f"  Test run finished in {time.time() - t_start:.2f}s:")
        print(f"  Modal State: {res['modal_state']} | NMSE: {res['nmse']:.4f} | Live FLOPs: {res['live_flops_mean']:.1f} | Shadow FLOPs: {res['shadow_flops_mean']:.1f}")
        print(f"  G_D_B: {res['g_db_mean']:.4f} | G_R_B: {res['g_rb_mean']:.4f} | G_D_BR: {res['g_d_br_mean']:.4f} | G_R_BD: {res['g_r_bd_mean']:.4f}")
    else:
        run_experiments(mode=args.mode)
