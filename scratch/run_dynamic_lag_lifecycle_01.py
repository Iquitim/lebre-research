#!/usr/bin/env python3
"""
run_dynamic_lag_lifecycle_01.py: Simulation Engine for DYNAMIC-LAG-LIFECYCLE-01.
Evaluates 11 variants across 12 hidden-support benchmark tasks (D1-D12)
under DEV (seeds 701..710) and EVAL (seeds 801..830) phases.
"""

import os
import sys
from pathlib import Path
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.bench01.streams import CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper
from scratch.bench_dynamic_lags import generate_dynamic_lag_stream, ALL_TASKS_D

EXP_DIR = ROOT / "experiments" / "DYNAMIC-LAG-LIFECYCLE-01"
FIG_DIR = EXP_DIR / "figures"
EXP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

DEV_SEEDS = list(range(701, 711))   # N=10
EVAL_SEEDS = list(range(801, 831))  # N=30

VARIANTS = [
    "O0_ORACLE_SPARSE",
    "O1_FULL_DENSE_FIR",
    "O2_ORACLE_SUPPORT_LIFECYCLE",
    "B0_LEBRE_FROZEN",
    "B1_LEBRE_NO_REC_BIRTH",
    "B3_FIXED_DENSE_FIR",
    "B4_VARIABLE_CONTIGUOUS_TAP_LENGTH",
    "B5_SPARSITY_REGULARIZED_FULL_DICTIONARY",
    "B6_PROPORTIONATE_SPARSE_ADAPTIVE_FILTER",
    "B7_PROPOSED_DYNAMIC_LAG_LIFECYCLE",
    "B7_E0_MAGNITUDE_EVICTION"
]

L_MAX = 32
K_MAX = 4

# -------------------------------------------------------------
# Dynamic Lag Lifecycle Model Implementation (B7)
# -------------------------------------------------------------

class DynamicLagLifecycleModel:
    def __init__(
        self,
        d_features: int,
        l_max: int = 32,
        k_max: int = 4,
        probe_rate: int = 2,
        mu_base: float = 0.10,
        mu_lag: float = 0.08,
        theta_promote: float = 0.15,
        theta_evict: float = 0.05,
        eviction_mode: str = "E2_TWO_TIMESCALE_OBSOLESCENCE",
        include_recurrence: bool = True
    ):
        self.D = d_features
        self.L_max = l_max
        self.K_max = k_max
        self.M = probe_rate
        self.mu_base = mu_base
        self.mu_lag = mu_lag
        self.theta_promote = theta_promote
        self.theta_evict = theta_evict
        self.eviction_mode = eviction_mode # E0 or E2
        self.include_recurrence = include_recurrence
        
        # Base Linear Model
        self.w_base = np.zeros(d_features, dtype=np.float64)
        
        # Scalar Recurrent State
        self.s = 0.0
        self.w_rec = 0.0
        self.lam = 0.90
        self.w_out = 0.0
        self.p_trace = 0.0
        
        # Active Taps: list of dicts: {'i': int, 'k': int, 'w': float, 'R': float, 'age': int, 'buffer': deque/list}
        self.active_taps = []
        
        # Provisional Candidates: list of dicts: {'i': int, 'k': int, 'w_shadow': float, 'evidence': float, 'age': int}
        self.provisional_cands = []
        
        # Rotating Probe State (M candidate pairs scanned per step)
        self.grid_pairs = [(i, k) for i in range(d_features) for k in range(1, l_max + 1)]
        self.probe_idx = 0
        self.corr_grid = np.zeros((d_features, l_max + 1), dtype=np.float64)
        
        # History Ring Buffer (HIST2: channel-specific buffers)
        # Stores past L_max values for each input dimension
        self.history = np.zeros((d_features, l_max + 1), dtype=np.float32)
        self.hist_ptr = 0
        
        # Metrics and Event Tracking
        self.events = []
        self.total_flops = 0

    def step(self, x_t: np.ndarray, y_t: float, t: int) -> Tuple[float, float, int]:
        flops = 0
        
        # 1. Update history ring buffer
        self.history[:, self.hist_ptr] = x_t.astype(np.float32)
        flops += self.D
        
        # Helper to retrieve delayed feature x_{i, t-k}
        def get_delayed(i_feat: int, lag_k: int) -> float:
            idx = (self.hist_ptr - lag_k) % (self.L_max + 1)
            return float(self.history[i_feat, idx])
            
        # 2. Live Forward Pass
        y_base = float(np.dot(self.w_base, x_t))
        flops += 2 * self.D
        
        y_lag = 0.0
        active_vals = []
        for tap in self.active_taps:
            val = get_delayed(tap['i'], tap['k'])
            active_vals.append(val)
            y_lag += tap['w'] * val
            flops += 2
            
        y_rec = 0.0
        if self.include_recurrence:
            # step state
            self.s = self.lam * self.s + float(np.dot(x_t[:2], [0.1, -0.1])) if self.D >= 2 else self.lam * self.s + 0.1 * x_t[0]
            self.s = float(np.tanh(self.s))
            y_rec = self.w_out * self.s
            flops += 8
            
        y_hat = y_base + y_lag + y_rec
        e_live = y_t - y_hat
        
        # 3. Counterfactual Candidate Scoring (Before update!)
        for cand in self.provisional_cands:
            cand_val = get_delayed(cand['i'], cand['k'])
            y_cand = y_hat + cand['w_shadow'] * cand_val
            e_cand = y_t - y_cand
            cand_gain = (e_live ** 2) - (e_cand ** 2)
            cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * cand_gain
            cand['age'] += 1
            # Update shadow weight via simple gradient step
            cand['w_shadow'] += 0.05 * e_cand * cand_val
            flops += 8
            
        # 4. Candidate Promotion Gate
        promoted = []
        for cand in self.provisional_cands:
            if cand['evidence'] >= self.theta_promote and cand['age'] >= 30:
                # Check if already active
                if not any(t['i'] == cand['i'] and t['k'] == cand['k'] for t in self.active_taps):
                    if len(self.active_taps) < self.K_max:
                        # Direct Promotion
                        new_tap = {
                            'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                            'R': cand['evidence'], 'age': 0, 'zero_count': 0
                        }
                        self.active_taps.append(new_tap)
                        promoted.append(cand)
                        self.events.append({
                            'step': t, 'event_type': 'PROVISIONAL_TO_ACTIVE',
                            'i': cand['i'], 'k': cand['k'], 'evidence': cand['evidence']
                        })
                    else:
                        # Capacity Full: Evaluate Replacement Regret
                        weakest_idx = int(np.argmin([t['R'] for t in self.active_taps]))
                        weakest_tap = self.active_taps[weakest_idx]
                        if cand['evidence'] > weakest_tap['R'] + 0.05:
                            # Replace
                            self.events.append({
                                'step': t, 'event_type': 'REPLACEMENT_EVICTION',
                                'i': weakest_tap['i'], 'k': weakest_tap['k'], 'evidence': weakest_tap['R']
                            })
                            self.active_taps[weakest_idx] = {
                                'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                                'R': cand['evidence'], 'age': 0, 'zero_count': 0
                            }
                            promoted.append(cand)
                            self.events.append({
                                'step': t, 'event_type': 'PROVISIONAL_TO_ACTIVE',
                                'i': cand['i'], 'k': cand['k'], 'evidence': cand['evidence']
                            })
                            
        # Remove promoted or expired candidates
        self.provisional_cands = [
            c for c in self.provisional_cands 
            if c not in promoted and not (c['age'] > 150 and c['evidence'] < 0.02)
        ]
        
        # 5. Live Model Weight Adaptation
        # Base weights update
        denom_base = float(np.dot(x_t, x_t)) + 1e-4
        self.w_base += (self.mu_base / denom_base) * e_live * x_t
        flops += 3 * self.D
        
        # Active tap weights update & relevance tracking
        for j, tap in enumerate(self.active_taps):
            val = get_delayed(tap['i'], tap['k'])
            tap['w'] += self.mu_lag * e_live * val
            tap['age'] += 1
            
            # Marginal conditional gain
            y_without_j = y_hat - tap['w'] * val
            e_without_j = y_t - y_without_j
            marginal_gain = (e_without_j ** 2) - (e_live ** 2)
            if abs(val) > 0.1:
                # Active signal: update relevance towards observed marginal gain
                tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
            # Else (quiescent channel): relevance remains frozen
            flops += 8
            
            # Eviction check
            if self.eviction_mode == "E0_MAGNITUDE":
                if abs(tap['w']) < 0.05:
                    tap['zero_count'] += 1
                else:
                    tap['zero_count'] = 0
                if tap['zero_count'] > 50 and tap['age'] > 100:
                    self.events.append({
                        'step': t, 'event_type': 'ACTIVE_TO_EVICTED',
                        'i': tap['i'], 'k': tap['k'], 'evidence': tap['R']
                    })
                    tap['evict'] = True
            else: # E2 Two-Timescale Relevance + Obsolescence Gate
                if tap['R'] < self.theta_evict and tap['age'] > 300:
                    # Check signal presence (obsolescence vs quiescence)
                    if abs(val) > 0.1: # non-quiescent, truly obsolete
                        self.events.append({
                            'step': t, 'event_type': 'ACTIVE_TO_EVICTED',
                            'i': tap['i'], 'k': tap['k'], 'evidence': tap['R']
                        })
                        tap['evict'] = True
                        
        self.active_taps = [t for t in self.active_taps if not t.get('evict', False)]
        
        # Recurrent unit update
        if self.include_recurrence:
            self.w_out += 0.05 * e_live * self.s
            flops += 4
            
        # 6. Bounded Candidate Probing (Rotating Schedule: M candidates)
        for _ in range(self.M):
            cand_pair = self.grid_pairs[self.probe_idx]
            self.probe_idx = (self.probe_idx + 1) % len(self.grid_pairs)
            
            # If not already active or provisional, test initial correlation
            i_p, k_p = cand_pair
            if not any(t['i'] == i_p and t['k'] == k_p for t in self.active_taps) and \
               not any(c['i'] == i_p and c['k'] == k_p for c in self.provisional_cands):
                past_val = get_delayed(i_p, k_p)
                self.corr_grid[i_p, k_p] = 0.95 * self.corr_grid[i_p, k_p] + 0.05 * (e_live * past_val)
                flops += 4
                if abs(self.corr_grid[i_p, k_p]) > 0.22 and len(self.provisional_cands) < 3:
                    self.provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w_shadow': float(self.corr_grid[i_p, k_p]),
                        'evidence': 0.05, 'age': 0
                    })
                    self.events.append({
                        'step': t, 'event_type': 'DORMANT_TO_PROVISIONAL',
                        'i': i_p, 'k': k_p, 'evidence': float(abs(self.corr_grid[i_p, k_p]))
                    })
                    
        # Advance ring buffer pointer
        self.hist_ptr = (self.hist_ptr + 1) % (self.L_max + 1)
        self.total_flops += flops
        return y_hat, e_live, flops

    def get_active_support(self) -> List[Tuple[int, int]]:
        return [(t['i'], t['k']) for t in self.active_taps]

    def get_memory_bytes(self) -> int:
        # Base: D*8*3 + 16 = 24D + 16
        base_bytes = 24 * self.D + 16
        # Rec: 40
        rec_bytes = 40 if self.include_recurrence else 0
        # Active taps: 20 bytes per tap + delay buffers (float32)
        active_bytes = len(self.active_taps) * 20 + sum(t['k'] * 4 for t in self.active_taps)
        # Provisional: 32 bytes per candidate
        cand_bytes = len(self.provisional_cands) * 32
        # History buffer: D * (L_max + 1) * 4 bytes
        hist_bytes = self.D * (self.L_max + 1) * 4
        return int(base_bytes + rec_bytes + active_bytes + cand_bytes + hist_bytes)

# -------------------------------------------------------------
# Single Stream Runner for All Variants
# -------------------------------------------------------------

def run_single_stream(
    task_id: str,
    seed: int,
    variant: str,
    phase: str = "EVAL",
    test_split: float = 0.30
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    X, y, meta = generate_dynamic_lag_stream(task_id, seed=seed)
    T, D = X.shape
    test_start = int(test_split * T)
    test_var = float(np.var(y[test_start:])) + 1e-6
    
    events_log = []
    trajectories_log = []
    losses = []
    flops_list = []
    
    # Extract true support for evaluating precision/recall
    def get_true_support_at(t_step: int) -> List[Tuple[int, int]]:
        for reg in meta["support_regimes"]:
            if reg["start"] <= t_step < reg["end"]:
                return reg.get("support", [])
        return []

    # ---------------------------------------------------------
    # Variant Execution
    # ---------------------------------------------------------
    if variant == "B0_LEBRE_FROZEN":
        wrapper = TrackBFrozenWrapper(d_features=D)
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            pred, flops = wrapper.step(x_norm, float(y[t]))
            scaler.update(X[t])
            res = float(y[t]) - float(pred)
            if t >= test_start:
                losses.append(res ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = wrapper.get_memory_bytes()
        params = wrapper.get_active_params()
        mean_active_lags = 0.0

    elif variant == "B1_LEBRE_NO_REC_BIRTH":
        w = np.zeros(D)
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            pred = float(np.dot(w, x_norm))
            e = float(y[t]) - pred
            w += (0.10 / (np.dot(x_norm, x_norm) + 1e-4)) * e * x_norm
            scaler.update(X[t])
            flops = 5 * D
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = 24 * D + 16
        params = D
        mean_active_lags = 0.0

    elif variant == "O0_ORACLE_SPARSE":
        # Static oracle receiving support from first regime
        true_sup = meta["support_regimes"][0]["support"]
        k_list = [k for (_, k) in true_sup]
        dim_total = D + len(true_sup)
        w = np.zeros(dim_total)
        hist = np.zeros((D, L_MAX + 1))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            # Construct feature vector
            feats = [x_norm]
            for (i_f, k_f) in true_sup:
                feats.append([hist[i_f, (h_ptr - k_f) % (L_MAX + 1)]])
            z_t = np.concatenate(feats)
            pred = float(np.dot(w, z_t))
            e = float(y[t]) - pred
            w += (0.08 / (np.dot(z_t, z_t) + 1e-4)) * e * z_t
            h_ptr = (h_ptr + 1) % (L_MAX + 1)
            scaler.update(X[t])
            flops = 5 * dim_total + len(true_sup)
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = 24 * D + 20 * len(true_sup) + sum(k * 4 for k in k_list)
        params = dim_total
        mean_active_lags = float(len(true_sup))

    elif variant == "O1_FULL_DENSE_FIR":
        # Full D x L_MAX dictionary (e.g. 5 x 32 = 160 taps)
        dim_total = D * (L_MAX + 1)
        w = np.zeros(dim_total)
        hist = np.zeros((D, L_MAX + 1))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            # Flatten circular buffer into ordered delay vector
            z_t = np.array([hist[:, (h_ptr - k) % (L_MAX + 1)] for k in range(L_MAX + 1)]).flatten()
            pred = float(np.dot(w, z_t))
            e = float(y[t]) - pred
            w += (0.05 / (np.dot(z_t, z_t) + 1e-4)) * e * z_t
            h_ptr = (h_ptr + 1) % (L_MAX + 1)
            scaler.update(X[t])
            flops = 4 * dim_total
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = dim_total * 8 + D * (L_MAX + 1) * 4
        params = dim_total
        mean_active_lags = float(dim_total - D)

    elif variant == "O2_ORACLE_SUPPORT_LIFECYCLE":
        # Receives dynamic support switches
        w_base = np.zeros(D)
        active_weights = {} # (i, k) -> float
        hist = np.zeros((D, L_MAX + 1))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            current_true = get_true_support_at(t)
            # Synchronize active weights with current true support
            active_weights = {pair: active_weights.get(pair, 0.0) for pair in current_true}
            # Predict
            pred = float(np.dot(w_base, x_norm))
            for (i_f, k_f), w_val in active_weights.items():
                pred += w_val * hist[i_f, (h_ptr - k_f) % (L_MAX + 1)]
            e = float(y[t]) - pred
            # Update
            w_base += (0.10 / (np.dot(x_norm, x_norm) + 1e-4)) * e * x_norm
            for pair in active_weights:
                i_f, k_f = pair
                active_weights[pair] += 0.08 * e * hist[i_f, (h_ptr - k_f) % (L_MAX + 1)]
            h_ptr = (h_ptr + 1) % (L_MAX + 1)
            scaler.update(X[t])
            flops = 5 * D + 6 * len(active_weights)
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = 24 * D + 32 * max(1, len(active_weights))
        params = D + len(active_weights)
        mean_active_lags = float(len(meta["support_regimes"][0].get("support", [])))

    elif variant == "B3_FIXED_DENSE_FIR":
        # Fixed order contiguous FIR K=4
        k_order = 4
        dim_total = D * k_order
        w = np.zeros(dim_total)
        hist = np.zeros((D, k_order))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            z_t = np.array([hist[:, (h_ptr - k) % k_order] for k in range(k_order)]).flatten()
            pred = float(np.dot(w, z_t))
            e = float(y[t]) - pred
            w += (0.08 / (np.dot(z_t, z_t) + 1e-4)) * e * z_t
            h_ptr = (h_ptr + 1) % k_order
            scaler.update(X[t])
            flops = 4 * dim_total
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = dim_total * 8 + D * k_order * 4
        params = dim_total
        mean_active_lags = float(dim_total - D)

    elif variant == "B4_VARIABLE_CONTIGUOUS_TAP_LENGTH":
        # Gong & Cowan 2005 variable tap-length FIR
        L_t = 2
        l_frac = 2.0
        w = np.zeros(D * L_MAX)
        hist = np.zeros((D, L_MAX))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        active_counts = []
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            cur_dim = D * L_t
            z_t = np.concatenate([hist[:, (h_ptr - k) % L_MAX] for k in range(L_t)])
            pred = float(np.dot(w[:cur_dim], z_t))
            e = float(y[t]) - pred
            w[:cur_dim] += (0.08 / (np.dot(z_t, z_t) + 1e-4)) * e * z_t
            
            # Fractional tap length update (Gong & Cowan)
            tail_energy = np.sum(w[max(0, cur_dim - 2*D):cur_dim] ** 2)
            if tail_energy > 0.02 and L_t < L_MAX:
                l_frac += 0.01
            elif tail_energy < 0.005 and L_t > 1:
                l_frac -= 0.01
            L_t = int(np.clip(int(l_frac), 1, L_MAX))
            active_counts.append(L_t)
            
            h_ptr = (h_ptr + 1) % L_MAX
            scaler.update(X[t])
            flops = 4 * cur_dim + 12
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = D * L_MAX * 8 + D * L_MAX * 4
        params = int(np.mean(active_counts)) * D
        mean_active_lags = float(np.mean(active_counts))

    elif variant == "B5_SPARSITY_REGULARIZED_FULL_DICTIONARY":
        # Gu et al. 2009 l0-LMS
        dim_total = D * L_MAX
        w = np.zeros(dim_total)
        hist = np.zeros((D, L_MAX))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            z_t = np.concatenate([hist[:, (h_ptr - k) % L_MAX] for k in range(L_MAX)])
            pred = float(np.dot(w, z_t))
            e = float(y[t]) - pred
            # l0 zero-attraction
            za = 1e-4 * 5.0 * np.sign(w) * np.exp(-5.0 * np.abs(w))
            w += (0.05 / (np.dot(z_t, z_t) + 1e-4)) * e * z_t - za
            h_ptr = (h_ptr + 1) % L_MAX
            scaler.update(X[t])
            flops = 6 * dim_total
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = dim_total * 8 + D * L_MAX * 4
        params = int(np.sum(np.abs(w) > 0.05))
        mean_active_lags = float(params)

    elif variant == "B6_PROPORTIONATE_SPARSE_ADAPTIVE_FILTER":
        # Duttweiler 2000 PNLMS
        dim_total = D * L_MAX
        w = np.zeros(dim_total)
        hist = np.zeros((D, L_MAX))
        h_ptr = 0
        scaler = CausalStandardScaler(d=D)
        for t in range(T):
            x_norm = scaler.transform(X[t])
            hist[:, h_ptr] = x_norm
            z_t = np.concatenate([hist[:, (h_ptr - k) % L_MAX] for k in range(L_MAX)])
            pred = float(np.dot(w, z_t))
            e = float(y[t]) - pred
            # Proportionate gains
            max_w = max(1e-4, np.max(np.abs(w)))
            gamma = np.maximum(0.01 * max_w, np.abs(w))
            g = gamma / np.sum(gamma)
            denom = float(np.dot(z_t, g * z_t)) + 1e-4
            w += (0.08 / denom) * (g * z_t) * e
            h_ptr = (h_ptr + 1) % L_MAX
            scaler.update(X[t])
            flops = 8 * dim_total
            if t >= test_start:
                losses.append(e ** 2)
                flops_list.append(flops)
        mse = float(np.mean(losses))
        mem = dim_total * 12 + D * L_MAX * 4
        params = int(np.sum(np.abs(w) > 0.05))
        mean_active_lags = float(params)

    elif variant in ["B7_PROPOSED_DYNAMIC_LAG_LIFECYCLE", "B7_E0_MAGNITUDE_EVICTION"]:
        evict_mode = "E0_MAGNITUDE" if variant == "B7_E0_MAGNITUDE_EVICTION" else "E2_TWO_TIMESCALE_OBSOLESCENCE"
        model = DynamicLagLifecycleModel(
            d_features=D, l_max=L_MAX, k_max=K_MAX,
            probe_rate=2, eviction_mode=evict_mode,
            include_recurrence=True
        )
        scaler = CausalStandardScaler(d=D)
        active_counts = []
        precisions = []
        recalls = []
        
        for t in range(T):
            x_norm = scaler.transform(X[t])
            pred, res, flops = model.step(x_norm, float(y[t]), t)
            scaler.update(X[t])
            
            cur_active = model.get_active_support()
            active_counts.append(len(cur_active))
            
            if t >= test_start:
                losses.append(res ** 2)
                flops_list.append(flops)
                
            # Log trajectories every 500 steps
            if t % 500 == 0:
                true_sup = get_true_support_at(t)
                tp = sum(1 for p in cur_active if p in true_sup)
                prec = (tp / len(cur_active)) if len(cur_active) > 0 else (1.0 if len(true_sup) == 0 else 0.0)
                rec = (tp / len(true_sup)) if len(true_sup) > 0 else 1.0
                precisions.append(prec)
                recalls.append(rec)
                trajectories_log.append({
                    'task_id': task_id, 'seed': seed, 'variant': variant, 'phase': phase,
                    'step': t, 'active_taps': len(cur_active), 'precision': prec, 'recall': rec,
                    'instant_mse': float(res ** 2)
                })
                
        mse = float(np.mean(losses))
        mem = model.get_memory_bytes()
        params = D + len(model.active_taps)
        mean_active_lags = float(np.mean(active_counts))
        events_log = model.events
        # Add metadata to events
        for ev in events_log:
            ev.update({'task_id': task_id, 'seed': seed, 'variant': variant, 'phase': phase})

    nmse = mse / test_var
    
    summary = {
        "task_id": task_id, "seed": seed, "variant": variant, "phase": phase,
        "status": "SUCCESS", "mse": mse, "nmse": nmse,
        "mean_flops": float(np.mean(flops_list)) if len(flops_list) > 0 else 50.0,
        "peak_flops": float(np.max(flops_list)) if len(flops_list) > 0 else 50.0,
        "memory_bytes": int(mem),
        "param_count": int(params),
        "mean_active_lags": mean_active_lags,
        "final_precision": float(np.mean(precisions[-5:])) if "precisions" in locals() and len(precisions) > 0 else 0.0,
        "final_recall": float(np.mean(recalls[-5:])) if "recalls" in locals() and len(recalls) > 0 else 0.0,
        "total_events": len(events_log)
    }
    
    return summary, events_log, trajectories_log

# -------------------------------------------------------------
# Main Batch Execution
# -------------------------------------------------------------

def main():
    print("Starting DYNAMIC-LAG-LIFECYCLE-01 Execution Engine...")
    
    # Phase 1: DEV runs
    print(f"--- Phase 1: Development Verification (Seeds {DEV_SEEDS[0]}..{DEV_SEEDS[-1]}) ---")
    dev_args = [
        (task_id, seed, var, "DEV")
        for task_id in ALL_TASKS_D
        for seed in DEV_SEEDS
        for var in VARIANTS
    ]
    print(f"Total DEV runs: {len(dev_args)}")
    
    dev_summaries = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(run_single_stream, *arg) for arg in dev_args]
        done = 0
        for f in as_completed(futures):
            s, evs, trajs = f.result()
            dev_summaries.append(s)
            done += 1
            if done % 200 == 0 or done == len(dev_args):
                print(f"DEV progress: {done}/{len(dev_args)} completed ({time.time() - t0:.1f}s)")
                
    print("DEV phase completed successfully.")
    
    # Phase 2: EVAL runs
    print(f"--- Phase 2: Confirmatory Evaluation (Seeds {EVAL_SEEDS[0]}..{EVAL_SEEDS[-1]}) ---")
    eval_args = [
        (task_id, seed, var, "EVAL")
        for task_id in ALL_TASKS_D
        for seed in EVAL_SEEDS
        for var in VARIANTS
    ]
    print(f"Total EVAL runs: {len(eval_args)}")
    
    eval_summaries = []
    all_events = []
    all_trajectories = []
    
    t1 = time.time()
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(run_single_stream, *arg) for arg in eval_args]
        done = 0
        for f in as_completed(futures):
            s, evs, trajs = f.result()
            eval_summaries.append(s)
            all_events.extend(evs)
            all_trajectories.extend(trajs)
            done += 1
            if done % 500 == 0 or done == len(eval_args):
                print(f"EVAL progress: {done}/{len(eval_args)} completed ({time.time() - t1:.1f}s)")
                
    # Combine summaries
    all_summaries = dev_summaries + eval_summaries
    df_manifest = pd.DataFrame(all_summaries)[[
        "task_id", "seed", "variant", "phase", "status", "mean_flops", "memory_bytes", "param_count"
    ]]
    df_results = pd.DataFrame(all_summaries)
    df_events = pd.DataFrame(all_events)
    df_trajs = pd.DataFrame(all_trajectories)
    
    manifest_path = EXP_DIR / "DYNAMIC_LAG_LIFECYCLE_01_RUN_MANIFEST.csv"
    results_path = EXP_DIR / "DYNAMIC_LAG_LIFECYCLE_01_SEED_RESULTS.csv"
    events_path = EXP_DIR / "DYNAMIC_LAG_LIFECYCLE_01_TAP_EVENTS.csv"
    trajs_path = EXP_DIR / "DYNAMIC_LAG_LIFECYCLE_01_SUPPORT_TRAJECTORIES.csv"
    
    df_manifest.to_csv(manifest_path, index=False)
    df_results.to_csv(results_path, index=False)
    df_events.to_csv(events_path, index=False)
    df_trajs.to_csv(trajs_path, index=False)
    
    print(f"Wrote {manifest_path}")
    print(f"Wrote {results_path}")
    print(f"Wrote {events_path}")
    print(f"Wrote {trajs_path}")

if __name__ == "__main__":
    main()
