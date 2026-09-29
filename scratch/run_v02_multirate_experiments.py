#!/usr/bin/env python3
"""
run_v02_multirate_experiments.py

LEBRE v0.2 Multirate Shadow Decomposition Experiment Runner
Implements:
- MultirateLEBREModel with decoupled clocks for sensing, candidate observation,
  candidate learning, recurrent propagation, recurrent learning, and arbitration.
- Disaggregated clocks (STREAM_AGE, OBSERVATION_COUNT, PARAMETER_UPDATE_COUNT).
- Skip semantics (HOLD_STATE, NO_NEW_EVIDENCE, STALE_WITH_AGE_METADATA).
- Evidence freshness tracking and synchronization.
- Component sensitivity screening on DEV (D0, D7, D8, D9F, D9L, D10).
- Component rate ladder (K in {1, 2, 5, 10}).
- Policy candidates (MR1, MR2, MR3).
- Confirmatory evaluation on FINAL cohort (M0 vs M1, seeds 1711..1740, N=30).
"""

import sys
import os
import time
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_corrective_confirmation import (
    ResourceVector,
    CausalStandardScaler,
    FP16HistoryRingBuffer,
    LinearBasePredictor,
    RecurrentScalarUnit
)

class MultirateLEBREModel:
    """
    T3 Architecture with Decoupled Multirate Shadow Subsystem.
    Preserves all canonical live invariants bit-for-bit while allowing independent
    cadence control and data-selective / temporal routing for shadow stages.
    """
    def __init__(
        self,
        K_probe: int = 1,
        K_cand_obs: int = 1,
        K_cand_learn: int = 1,
        K_rec_forward: int = 1,
        K_rec_learn: int = 1,
        K_arbitration: int = 1,
        router_type: str = "NONE", # "NONE", "DATA_SELECTIVE", "TEMPORAL_ROUTER"
        innov_gamma: float = 0.010,
        temporal_theta: float = 0.15,
        heartbeat_H: int = 100,
        tau_tol: int = 2,
        corr_grid_dtype: np.dtype = np.float16
    ):
        self.K_probe = K_probe
        self.K_cand_obs = K_cand_obs
        self.K_cand_learn = K_cand_learn
        self.K_rec_forward = K_rec_forward
        self.K_rec_learn = K_rec_learn
        self.K_arbitration = K_arbitration
        self.router_type = router_type
        self.innov_gamma = innov_gamma
        self.temporal_theta = temporal_theta
        self.heartbeat_H = heartbeat_H
        self.tau_tol = tau_tol
        self.corr_grid_dtype = corr_grid_dtype
        
        # Resource accounting
        self.live_res = ResourceVector()
        self.shadow_res = ResourceVector()
        self.router_res = ResourceVector()
        
        # Core live pipeline components
        self.d = 5
        self.scaler = CausalStandardScaler(self.d)
        self.history = FP16HistoryRingBuffer(self.d, 33)
        self.base = LinearBasePredictor(self.d)
        
        # Discrete lag structures
        self.active_taps: List[Dict[str, Any]] = []
        self.provisional_cands: List[Dict[str, Any]] = []
        self.corr_grid = np.zeros((5, 33), dtype=corr_grid_dtype)
        self.grid_pairs = [(i, k) for i in range(5) for k in range(1, 33)]
        self.probe_ptr = 0
        
        # Recurrent structure
        self.active_rec: Optional[RecurrentScalarUnit] = None
        self.shadow_rec = RecurrentScalarUnit()
        self.rec_evidence = 0.0
        self.rec_stream_age = 0
        self.rec_obs_count = 0
        self.rec_param_update_count = 0
        self.rec_last_forward_step = 0
        self.rec_last_learn_step = 0
        self.y_rec_shadow_cached = 0.0
        
        # Capacity arbitrator (T3)
        self.ema_G_D_B = 0.0
        self.ema_G_R_B = 0.0
        self.ema_G_R_BD = 0.0
        self.ema_G_D_BR = 0.0
        self.theta_tol = 0.015
        self.arb_last_step = 0
        
        # Tracking metrics and counters
        self.step_count = 0
        self.dual_active_steps = 0
        self.redundant_dual_steps = 0
        self.cast_ops = 0
        self.evictions_lag = 0
        self.evictions_rec = 0
        self.promotions_lag = 0
        self.promotions_rec = 0
        
        # Utilization counters
        self.probe_executions = 0
        self.candidate_observations = 0
        self.candidate_parameter_updates = 0
        self.recurrent_forward_executions = 0
        self.recurrent_parameter_updates = 0
        self.arbitration_updates = 0
        self.heartbeat_executions = 0
        self.event_triggered_executions = 0
        self.stale_arbitration_skips = 0
        
        # Router state
        self.router_r_e = 0.0
        self.router_var_e = 0.16 # initial variance estimate
        self.router_e_prev = 0.0
        self.router_heartbeat_counter = 0
        self.is_temporal_awake = True
        self.temporal_wake_events = 0
        self.temporal_sleep_events = 0

    def step(self, x_raw: np.ndarray, y_true: float) -> Dict[str, Any]:
        self.step_count += 1
        self.live_res.reset_step()
        self.shadow_res.reset_step()
        self.router_res.reset_step()
        
        # =====================================================================
        # 1. CANONICAL LIVE PATH (MANDATORY BIT-EXACT CONTINUOUS EXECUTION)
        # =====================================================================
        # Step 1: Causal Input Standardization (10 FP, 80 B moved)
        x_norm = self.scaler.transform(x_raw, self.live_res)
        
        # Step 2: History Buffer Write (5 int ops, 10 B moved)
        self.history.write(x_norm, self.live_res)
        
        def query_delayed(i_feat: int, k_lag: int, is_shadow: bool = False) -> float:
            target_res = self.shadow_res if is_shadow else self.live_res
            return self.history.query(i_feat, k_lag, target_res)
            
        # Step 3: Base Linear Prediction (10 FP, 40 B moved)
        y_base = self.base.predict(x_norm, self.live_res)
        
        # Step 4: Active Delay Taps Prediction (2 FP per tap)
        y_lag_live = 0.0
        for tap in self.active_taps:
            val = query_delayed(tap['i'], tap['k'], is_shadow=False)
            y_lag_live += tap['w'] * val
            self.live_res.fp_flops += 2.0
            
        # Step 5: Active Recurrent Forward Pass (18 FP if active)
        y_rec_live = 0.0
        if self.active_rec is not None:
            _, y_rec_live = self.active_rec.forward(x_norm[0], self.live_res)
            
        # Step 6: Form Aggregate Live Prediction (2 FP)
        y_hat_live = y_base + y_lag_live + y_rec_live
        
        # Step 7: Reveal True Target & Evaluate Prequential Losses (2 FP)
        e_live = y_true - y_hat_live
        ell_live = e_live ** 2
        
        # Step 8: Base Linear Predictor LMS Update (18 FP, 40 B moved)
        self.base.update(x_norm, y_true - y_base, self.live_res)
        
        # Step 9: Active Lag Taps LMS Updates & Eviction Check (8 FP per tap)
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
        
        # Step 10: Active Recurrent RTRL Update (16 FP if active)
        if self.active_rec is not None:
            self.active_rec.update(e_live, x_norm[0], self.live_res)
            
        # Step 11: Causal Scaler Online Welford Update (20 FP, 80 B moved)
        self.scaler.update(x_raw, self.live_res)
        
        # Step 12: Stream Age Advance for Shadow Objects (0 FP, bookkeeping)
        self.rec_stream_age += 1
        for c in self.provisional_cands:
            c['stream_age'] = c.get('stream_age', 0) + 1

        # =====================================================================
        # 2. MULTIRATE ROUTER & SCHEDULING LOGIC
        # =====================================================================
        # Temporal router check (MR3)
        allow_temporal_exploration = True
        if self.router_type == "TEMPORAL_ROUTER":
            # Router cost: 1 mul + 2 EMA (4 FP) + 1 ratio (1 FP) = 6 FP
            self.router_res.fp_flops += 6.0
            self.router_res.int_ops += 2
            
            # Update causal residual serial cross-product
            prod = e_live * self.router_e_prev
            self.router_r_e = 0.95 * self.router_r_e + 0.05 * prod
            self.router_var_e = 0.95 * self.router_var_e + 0.05 * ell_live
            self.router_e_prev = e_live
            
            c_temp = self.router_r_e / (self.router_var_e + 1e-4)
            
            if self.router_heartbeat_counter >= self.heartbeat_H:
                allow_temporal_exploration = True
                self.router_heartbeat_counter = 0
                self.heartbeat_executions += 1
            elif c_temp > self.temporal_theta:
                allow_temporal_exploration = True
                self.router_heartbeat_counter = 0
                self.event_triggered_executions += 1
                self.temporal_wake_events += 1
            else:
                allow_temporal_exploration = False
                self.router_heartbeat_counter += 1
                self.temporal_sleep_events += 1
        else:
            allow_temporal_exploration = True

        # =====================================================================
        # 3. STAGE 7: CORRELATION GRID PROBING (Multirate Cadence: K_probe)
        # =====================================================================
        run_probe = (self.step_count % self.K_probe == 0) and allow_temporal_exploration
        if run_probe:
            self.probe_executions += 1
            e_for_probe = y_true - y_base
            for _ in range(2): # 2 probes per execution
                i_p, k_p = self.grid_pairs[self.probe_ptr]
                self.probe_ptr = (self.probe_ptr + 1) % len(self.grid_pairs)
                if not any(t['i'] == i_p and t['k'] == k_p for t in self.active_taps) and \
                   not any(c['i'] == i_p and c['k'] == k_p for c in self.provisional_cands):
                    c_val = query_delayed(i_p, k_p, is_shadow=True)
                    val_fp32 = float(self.corr_grid[i_p, k_p])
                    upd_fp32 = 0.95 * val_fp32 + 0.05 * (e_for_probe * c_val)
                    self.corr_grid[i_p, k_p] = np.float16(upd_fp32)
                    corr_val = upd_fp32
                    self.shadow_res.fp_flops += 4.0
                    self.shadow_res.int_ops += 2
                    self.cast_ops += 2
                    
                    if abs(corr_val) > 0.20 and len(self.provisional_cands) < 3:
                        self.provisional_cands.append({
                            'i': i_p, 'k': k_p, 'w': float(corr_val),
                            'evidence': 0.05, 'stream_age': 0, 'obs_count': 0,
                            'param_update_count': 0, 'last_update_step': self.step_count
                        })

        # =====================================================================
        # 4. STAGE 9: SHADOW RECURRENT UNIT (State Prop: K_fwd, Learn: K_lrn)
        # =====================================================================
        # 9A & 9B: Recurrent State Propagation & Output Prediction
        run_rec_forward = (self.step_count % self.K_rec_forward == 0) and allow_temporal_exploration
        if run_rec_forward:
            self.recurrent_forward_executions += 1
            _, y_rec_shadow_val = self.shadow_rec.forward(x_norm[0], self.shadow_res)
            self.y_rec_shadow_cached = y_rec_shadow_val
            self.rec_last_forward_step = self.step_count
            self.rec_obs_count += 1
        else:
            # HOLD_STATE / STALE_WITH_AGE_METADATA
            y_rec_shadow_val = self.y_rec_shadow_cached

        # 9C, 9D, 9E: Recurrent Sensitivity, Parameter Update, and Evidence EMA
        run_rec_learn = (self.step_count % self.K_rec_learn == 0) and allow_temporal_exploration
        if self.router_type == "DATA_SELECTIVE" and run_rec_learn:
            # Data-selective check: innovation > gamma
            self.router_res.fp_flops += 2.0
            e_diff = abs(y_true - (y_base + y_rec_shadow_val))
            if (y_true - y_base)**2 - e_diff**2 <= self.innov_gamma:
                run_rec_learn = False

        if run_rec_learn:
            self.recurrent_parameter_updates += 1
            e_shadow_rec = y_true - (y_base + y_rec_shadow_val)
            self.shadow_rec.update(e_shadow_rec, x_norm[0], self.shadow_res)
            gain_rec = (y_true - y_base) ** 2 - (e_shadow_rec ** 2)
            self.rec_evidence = 0.98 * self.rec_evidence + 0.02 * gain_rec
            self.rec_param_update_count += 1
            self.rec_last_learn_step = self.step_count
            self.shadow_res.fp_flops += 6.0

        # =====================================================================
        # 5. STAGE 8: PROVISIONAL CANDIDATES (Observation vs Parameter Learning)
        # =====================================================================
        run_cand_obs = (self.step_count % self.K_cand_obs == 0) and allow_temporal_exploration
        run_cand_learn = (self.step_count % self.K_cand_learn == 0) and allow_temporal_exploration
        
        # Best candidate forward prediction for counterfactuals
        best_cand = None
        y_lag_eval = 0.0
        if len(self.active_taps) > 0:
            y_lag_eval = y_lag_live
        elif len(self.provisional_cands) > 0:
            best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
            if run_cand_obs:
                self.candidate_observations += 1
                c_val = query_delayed(best_cand['i'], best_cand['k'], is_shadow=True)
                y_lag_eval = best_cand['w'] * c_val
                best_cand['cached_y'] = y_lag_eval
                best_cand['obs_count'] += 1
                best_cand['last_update_step'] = self.step_count
                self.shadow_res.fp_flops += 2.0
            else:
                # STALE_WITH_AGE_METADATA
                y_lag_eval = best_cand.get('cached_y', 0.0)

        # Candidate LMS updates and evidence EMA
        if run_cand_learn:
            for cand in self.provisional_cands:
                do_update = True
                if self.router_type == "DATA_SELECTIVE":
                    self.router_res.fp_flops += 2.0
                    c_val = query_delayed(cand['i'], cand['k'], is_shadow=True)
                    e_c = y_true - (y_base + cand['w'] * c_val)
                    if ((y_true - y_base)**2 - e_c**2) <= self.innov_gamma:
                        do_update = False
                if do_update:
                    self.candidate_parameter_updates += 1
                    c_val = query_delayed(cand['i'], cand['k'], is_shadow=True)
                    e_cand = y_true - (y_base + cand['w'] * c_val)
                    gain_c = ((y_true - y_base) ** 2) - (e_cand ** 2)
                    cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * gain_c
                    cand['w'] += 0.05 * e_cand * c_val
                    cand['param_update_count'] += 1
                    self.shadow_res.fp_flops += 8.0

        # =====================================================================
        # 6. STAGE 10: COUNTERFACTUAL ARBITRATION (Freshness-Gated)
        # =====================================================================
        run_arb = (self.step_count % self.K_arbitration == 0) and allow_temporal_exploration
        
        # Check evidence freshness
        lag_age = 0 if len(self.active_taps) > 0 else (
            self.step_count - best_cand['last_update_step'] if best_cand is not None else 0
        )
        rec_age = 0 if self.active_rec is not None else (
            self.step_count - self.rec_last_forward_step
        )
        
        freshness_ok = (lag_age <= self.tau_tol) and (rec_age <= self.tau_tol)
        
        if run_arb and freshness_ok:
            self.arbitration_updates += 1
            
            # Select recurrent eval value
            if self.active_rec is not None:
                y_rec_eval = y_rec_live
            elif self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
                y_rec_eval = y_rec_shadow_val
            else:
                y_rec_eval = 0.0
                
            # 10A: Counterfactual Loss Quadruplet (8 FP)
            P_BASE = y_base
            P_BASE_D = y_base + y_lag_eval
            P_BASE_R = y_base + y_rec_eval
            P_BASE_D_R = y_base + y_lag_eval + y_rec_eval
            
            ell_B = (y_true - P_BASE) ** 2
            ell_BD = (y_true - P_BASE_D) ** 2
            ell_BR = (y_true - P_BASE_R) ** 2
            ell_BDR = (y_true - P_BASE_D_R) ** 2
            
            # 10B: Conditional Gain Evaluation (4 FP)
            G_D_B = ell_B - ell_BD
            G_R_B = ell_B - ell_BR
            G_R_BD = ell_BD - ell_BDR
            G_D_BR = ell_BR - ell_BDR
            
            # 10C: Gain EMA Filtering (16 FP)
            alpha_g = 0.02
            self.ema_G_D_B = (1.0 - alpha_g) * self.ema_G_D_B + alpha_g * G_D_B
            self.ema_G_R_B = (1.0 - alpha_g) * self.ema_G_R_B + alpha_g * G_R_B
            self.ema_G_R_BD = (1.0 - alpha_g) * self.ema_G_R_BD + alpha_g * G_R_BD
            self.ema_G_D_BR = (1.0 - alpha_g) * self.ema_G_D_BR + alpha_g * G_D_BR
            self.shadow_res.fp_flops += 28.0
            self.arb_last_step = self.step_count
            
            # 10D: Arbitration Decision & Structural Promotion/Eviction (6 int ops)
            d_helps = self.ema_G_D_B > self.theta_tol
            r_helps = self.ema_G_R_B > self.theta_tol
            d_cond = self.ema_G_D_BR > self.theta_tol
            r_cond = self.ema_G_R_BD > self.theta_tol
            
            if not d_helps and not r_helps:
                if len(self.active_taps) > 0 and self.step_count > 300 and self.ema_G_D_B < 0.005:
                    self.evictions_lag += len(self.active_taps)
                    self.active_taps = []
                if self.active_rec is not None and self.step_count > 300 and self.ema_G_R_B < 0.008:
                    self.active_rec = None
                    self.evictions_rec += 1
            elif d_helps and not r_helps:
                if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                    self.active_rec = None
                    self.evictions_rec += 1
                if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                    b_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                    if b_cand['evidence'] > 0.02 and b_cand['obs_count'] >= 15:
                        self.active_taps.append({
                            'i': b_cand['i'], 'k': b_cand['k'], 'w': b_cand['w'],
                            'R': b_cand['evidence'], 'age': 0
                        })
                        self.promotions_lag += 1
                        self.provisional_cands.remove(b_cand)
            elif not d_helps and r_helps:
                if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                    self.evictions_lag += len(self.active_taps)
                    self.active_taps = []
                if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
                    self.active_rec = self.shadow_rec
                    self.promotions_rec += 1
                    self.shadow_rec = RecurrentScalarUnit()
                    self.rec_evidence = 0.0
                    self.rec_obs_count = 0
            else:
                # Both help independently
                if d_cond and r_cond:
                    if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                        b_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                        if b_cand['evidence'] > 0.02 and b_cand['obs_count'] >= 15:
                            self.active_taps.append({
                                'i': b_cand['i'], 'k': b_cand['k'], 'w': b_cand['w'],
                                'R': b_cand['evidence'], 'age': 0
                            })
                            self.promotions_lag += 1
                            self.provisional_cands.remove(b_cand)
                    if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
                        self.active_rec = self.shadow_rec
                        self.promotions_rec += 1
                        self.shadow_rec = RecurrentScalarUnit()
                        self.rec_evidence = 0.0
                        self.rec_obs_count = 0
                elif d_cond and not r_cond:
                    if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                        self.active_rec = None
                        self.evictions_rec += 1
                    if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                        b_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                        if b_cand['evidence'] > 0.02 and b_cand['obs_count'] >= 15:
                            self.active_taps.append({
                                'i': b_cand['i'], 'k': b_cand['k'], 'w': b_cand['w'],
                                'R': b_cand['evidence'], 'age': 0
                            })
                            self.promotions_lag += 1
                            self.provisional_cands.remove(b_cand)
                elif not d_cond and r_cond:
                    if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                        self.evictions_lag += len(self.active_taps)
                        self.active_taps = []
                    if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
                        self.active_rec = self.shadow_rec
                        self.promotions_rec += 1
                        self.shadow_rec = RecurrentScalarUnit()
                        self.rec_evidence = 0.0
                        self.rec_obs_count = 0
                else:
                    # Redundant equal: arbitrate by magnitude
                    if self.ema_G_D_B >= self.ema_G_R_B:
                        if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                            self.active_rec = None
                            self.evictions_rec += 1
                        if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                            b_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                            if b_cand['evidence'] > 0.02 and b_cand['obs_count'] >= 15:
                                self.active_taps.append({
                                    'i': b_cand['i'], 'k': b_cand['k'], 'w': b_cand['w'],
                                    'R': b_cand['evidence'], 'age': 0
                                })
                                self.promotions_lag += 1
                                self.provisional_cands.remove(b_cand)
                    else:
                        if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                            self.evictions_lag += len(self.active_taps)
                            self.active_taps = []
                        if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
                            self.active_rec = self.shadow_rec
                            self.promotions_rec += 1
                            self.shadow_rec = RecurrentScalarUnit()
                            self.rec_evidence = 0.0
                            self.rec_obs_count = 0
        elif run_arb and not freshness_ok:
            # Rejection due to staleness: NO_NEW_EVIDENCE, HOLD_STATE
            self.stale_arbitration_skips += 1

        # Prune stale provisional candidates (stream age > 150 without sufficient evidence)
        self.provisional_cands = [
            c for c in self.provisional_cands if not (c['stream_age'] > 150 and c['evidence'] < 0.02)
        ]

        # =====================================================================
        # 7. METRIC & RESOURCE ACCOUNTING
        # =====================================================================
        has_lag = len(self.active_taps) > 0
        has_rec = self.active_rec is not None
        if has_lag and has_rec:
            self.dual_active_steps += 1
            if self.ema_G_D_BR <= self.theta_tol or self.ema_G_R_BD <= self.theta_tol:
                self.redundant_dual_steps += 1

        tot_fp = self.live_res.fp_flops + self.shadow_res.fp_flops + self.router_res.fp_flops
        tot_int = self.live_res.int_ops + self.shadow_res.int_ops + self.router_res.int_ops
        tot_bytes = (self.live_res.bytes_read + self.live_res.bytes_written +
                     self.shadow_res.bytes_read + self.shadow_res.bytes_written +
                     self.router_res.bytes_read + self.router_res.bytes_written)
                     
        # Dynamic memory calculation (Phase A standards)
        router_bytes = 18 if self.router_type == "TEMPORAL_ROUTER" else 0
        curr_mem = (self.scaler.d * 16 + self.history.get_memory_bytes() + self.base.get_memory_bytes() +
                    len(self.active_taps) * 16 + len(self.provisional_cands) * 16 +
                    (self.active_rec.get_memory_bytes() if self.active_rec is not None else 0) +
                    self.shadow_rec.get_memory_bytes() + 64 + self.corr_grid.nbytes + router_bytes)

        return {
            'y_hat': y_hat_live,
            'e_live': e_live,
            'ell_live': ell_live,
            'live_fp_flops': self.live_res.fp_flops,
            'shadow_fp_flops': self.shadow_res.fp_flops,
            'router_fp_flops': self.router_res.fp_flops,
            'total_fp_flops': tot_fp,
            'int_ops': tot_int,
            'bytes_moved': tot_bytes,
            'n_active_taps': len(self.active_taps),
            'has_active_rec': has_rec,
            'structural_state': "BOTH" if (has_lag and has_rec) else ("LAG" if has_lag else ("RECURRENT" if has_rec else "NONE")),
            'occupied_bytes': curr_mem,
            'ema_G_D_B': self.ema_G_D_B,
            'ema_G_R_B': self.ema_G_R_B,
            'ema_G_D_BR': self.ema_G_D_BR,
            'ema_G_R_BD': self.ema_G_R_BD,
            'is_temporal_awake': allow_temporal_exploration
        }

def run_single_simulation(args: Tuple) -> Dict[str, Any]:
    task_id, seed, model_id, model_params = args
    X, y, meta = generate_v02_stream(task_id, seed, 6000)
    
    m = MultirateLEBREModel(**model_params)
    
    errors = []
    live_fp = []
    shadow_fp = []
    router_fp = []
    tot_fp = []
    int_ops = []
    bytes_moved = []
    occupied_bytes = []
    states = []
    both_steps = 0
    redundant_both_steps = 0
    awake_steps = 0
    
    # Track quiescence specifically for I7 / I8 (silence interval: t in [2000, 4000))
    quiescent_shadow_fp = []
    
    for t in range(6000):
        out = m.step(X[t], y[t])
        errors.append(out['e_live'])
        live_fp.append(out['live_fp_flops'])
        shadow_fp.append(out['shadow_fp_flops'])
        router_fp.append(out['router_fp_flops'])
        tot_fp.append(out['total_fp_flops'])
        int_ops.append(out['int_ops'])
        bytes_moved.append(out['bytes_moved'])
        occupied_bytes.append(out['occupied_bytes'])
        states.append(out['structural_state'])
        if out['structural_state'] == "BOTH":
            both_steps += 1
            if out['ema_G_D_BR'] <= m.theta_tol or out['ema_G_R_BD'] <= m.theta_tol:
                redundant_both_steps += 1
        if out['is_temporal_awake']:
            awake_steps += 1
        if 2000 <= t < 4000:
            quiescent_shadow_fp.append(out['shadow_fp_flops'])
            
    err_arr = np.array(errors, dtype=np.float64)
    nmse = float(np.mean(err_arr ** 2) / np.var(y))
    
    # Steady state frac_both on t in [1000, 6000)
    ss_states = states[1000:6000]
    frac_both_ss = float(sum(1 for s in ss_states if s == "BOTH") / len(ss_states))
    
    # State occupancy fractions over all 6000 steps
    frac_none = float(sum(1 for s in states if s == "NONE") / 6000)
    frac_lag = float(sum(1 for s in states if s == "LAG") / 6000)
    frac_rec = float(sum(1 for s in states if s == "RECURRENT") / 6000)
    frac_both = float(sum(1 for s in states if s == "BOTH") / 6000)
    
    # Modal structural state
    state_counts = {"NONE": frac_none, "LAG": frac_lag, "RECURRENT": frac_rec, "BOTH": frac_both}
    modal_state = max(state_counts, key=state_counts.get)
    
    # Switching latency (for I11, I12, I13, I14 with change-point at t=3000)
    switch_latency = np.nan
    if task_id in ["I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay",
                    "I13_Regime_Switch_Hybrid_To_Memoryless", "I14_Intermittent_Hybrid"]:
        # Find post-switch recovery step
        post_err = err_arr[3000:] ** 2
        # Rolling window of 100 steps
        win = 100
        roll = np.convolve(post_err, np.ones(win)/win, mode='valid')
        # Target threshold: 0.15 for NMSE recovery
        target_thresh = 0.15 * np.var(y[3000:])
        rec_idx = np.where(roll <= target_thresh)[0]
        if len(rec_idx) > 0:
            switch_latency = float(rec_idx[0] + win)
        else:
            switch_latency = 3000.0 # max delay
            
    # Support recovery on I3 and I4
    support_prec, support_rec, support_f1 = np.nan, np.nan, np.nan
    if task_id == "I3_Single_Exact_Delay":
        true_taps = {(0, 5)}
        active_tuples = {(t['i'], t['k']) for t in m.active_taps}
        tp = len(active_tuples.intersection(true_taps))
        support_prec = float(tp / len(active_tuples)) if len(active_tuples) > 0 else 0.0
        support_rec = float(tp / len(true_taps))
        support_f1 = (2 * support_prec * support_rec / (support_prec + support_rec)) if (support_prec + support_rec) > 0 else 0.0
    elif task_id == "I4_Multi_Sparse_Delay":
        true_taps = {(0, 3), (1, 7), (2, 12)}
        active_tuples = {(t['i'], t['k']) for t in m.active_taps}
        tp = len(active_tuples.intersection(true_taps))
        support_prec = float(tp / len(active_tuples)) if len(active_tuples) > 0 else 0.0
        support_rec = float(tp / len(true_taps))
        support_f1 = (2 * support_prec * support_rec / (support_prec + support_rec)) if (support_prec + support_rec) > 0 else 0.0

    return {
        'task_id': task_id,
        'seed': seed,
        'model_id': model_id,
        'nmse': nmse,
        'modal_state': modal_state,
        'frac_none': frac_none,
        'frac_lag': frac_lag,
        'frac_rec': frac_rec,
        'frac_both': frac_both,
        'frac_both_ss': frac_both_ss,
        'promotions_lag': m.promotions_lag,
        'promotions_rec': m.promotions_rec,
        'evictions_lag': m.evictions_lag,
        'evictions_rec': m.evictions_rec,
        'live_fp_mean': float(np.mean(live_fp)),
        'shadow_fp_mean': float(np.mean(shadow_fp)),
        'router_fp_mean': float(np.mean(router_fp)),
        'total_fp_mean': float(np.mean(tot_fp)),
        'int_ops_mean': float(np.mean(int_ops)),
        'bytes_moved_mean': float(np.mean(bytes_moved)),
        'occupied_bytes_mean': float(np.mean(occupied_bytes)),
        'occupied_bytes_peak': int(np.max(occupied_bytes)),
        'support_precision': support_prec,
        'support_recall': support_rec,
        'support_f1': support_f1,
        'switch_latency': switch_latency,
        'g_db_mean': m.ema_G_D_B,
        'g_rb_mean': m.ema_G_R_B,
        'g_d_br_mean': m.ema_G_D_BR,
        'g_r_bd_mean': m.ema_G_R_BD,
        'probe_executions': m.probe_executions,
        'candidate_observations': m.candidate_observations,
        'candidate_parameter_updates': m.candidate_parameter_updates,
        'recurrent_forward_executions': m.recurrent_forward_executions,
        'recurrent_parameter_updates': m.recurrent_parameter_updates,
        'arbitration_updates': m.arbitration_updates,
        'heartbeat_executions': m.heartbeat_executions,
        'event_triggered_executions': m.event_triggered_executions,
        'stale_arbitration_skips': m.stale_arbitration_skips,
        'awake_fraction': float(awake_steps / 6000.0),
        'quiescent_shadow_fp_mean': float(np.mean(quiescent_shadow_fp)) if len(quiescent_shadow_fp) > 0 else 0.0
    }

if __name__ == "__main__":
    print("Multirate simulation module loaded successfully.")
