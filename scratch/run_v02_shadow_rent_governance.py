import sys
import os
import time
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
from concurrent.futures import ProcessPoolExecutor

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_corrective_confirmation import (
    ResourceVector,
    CausalStandardScaler,
    FP16HistoryRingBuffer,
    LinearBasePredictor,
    RecurrentScalarUnit
)

class GovernedLEBREModel:
    """
    T3 Architecture with Governed Counterfactual Shadow Scheduling.
    Implements S0 (Continuous), S1 (Shadow Off), S2 (Periodic), and S3 (Event-Triggered + Heartbeat).
    Strictly preserves the Single-Difference Invariant.
    """
    def __init__(
        self,
        schedule_mode: str = "S0_CONTINUOUS",
        periodic_K: int = 5,
        ph_delta: float = 0.10,
        ph_lambda: float = 8.0,
        heartbeat_H: int = 250,
        burst_W: int = 50,
        corr_grid_dtype: np.dtype = np.float16
    ):
        self.schedule_mode = schedule_mode
        self.periodic_K = periodic_K
        self.ph_delta = ph_delta
        self.ph_lambda = ph_lambda
        self.heartbeat_H = heartbeat_H
        self.burst_W = burst_W
        self.corr_grid_dtype = corr_grid_dtype
        
        # Resource tracking
        self.live_res = ResourceVector()
        self.shadow_res = ResourceVector()
        self.scheduler_res = ResourceVector()
        
        # Core components
        self.d = 5
        self.scaler = CausalStandardScaler(self.d)
        self.history = FP16HistoryRingBuffer(self.d, 33)
        self.base = LinearBasePredictor(self.d)
        
        # Discrete Lag Structure
        self.active_taps: List[Dict[str, Any]] = []
        self.provisional_cands: List[Dict[str, Any]] = []
        self.corr_grid = np.zeros((5, 33), dtype=corr_grid_dtype)
        self.grid_pairs = [(i, k) for i in range(5) for k in range(1, 33)]
        self.probe_ptr = 0
        
        # Recurrent Structure
        self.active_rec: Optional[RecurrentScalarUnit] = None
        self.shadow_rec = RecurrentScalarUnit()
        self.rec_evidence = 0.0
        self.rec_age = 0
        
        # Arbitrator (T3)
        self.ema_G_D_B = 0.0
        self.ema_G_R_B = 0.0
        self.ema_G_R_BD = 0.0
        self.ema_G_D_BR = 0.0
        self.theta_tol = 0.015
        
        # Timesteps and metrics
        self.step_count = 0
        self.dual_active_steps = 0
        self.redundant_dual_steps = 0
        self.cast_ops = 0
        self.evictions_lag = 0
        self.evictions_rec = 0
        
        # Scheduler State (S2 and S3)
        self.ref_loss = 0.20
        self.cum_dev = 0.0
        self.heartbeat_counter = 0
        self.burst_counter = 0
        self.is_shadow_awake = True
        self.wake_reason = "initial"
        self.wake_episodes = 0
        self.alarm_count = 0
        self.heartbeat_wake_count = 0
        self.shadow_active_steps = 0

    def step(self, x_raw: np.ndarray, y_true: float) -> Dict[str, Any]:
        self.step_count += 1
        self.live_res.reset_step()
        self.shadow_res.reset_step()
        self.scheduler_res.reset_step()
        
        # Step 1 & 2: Normalize and write history (LIVE & SHARED)
        x_norm = self.scaler.transform(x_raw, self.live_res)
        self.history.write(x_norm, self.live_res)
        
        def query_delayed(i_feat: int, k_lag: int, is_shadow: bool = False) -> float:
            target_res = self.shadow_res if is_shadow else self.live_res
            return self.history.query(i_feat, k_lag, target_res)
            
        # Step 3: Base prediction (LIVE)
        y_base = self.base.predict(x_norm, self.live_res)
        
        # Step 4: Discrete Lag active prediction (LIVE)
        y_lag_live = 0.0
        for tap in self.active_taps:
            val = query_delayed(tap['i'], tap['k'], is_shadow=False)
            y_lag_live += tap['w'] * val
            self.live_res.fp_flops += 2.0
            
        # Step 5: Recurrent active prediction (LIVE)
        y_rec_live = 0.0
        if self.active_rec is not None:
            _, y_rec_live = self.active_rec.forward(x_norm[0], self.live_res)
            
        # Step 6: Form Aggregate Live Prediction (LIVE)
        y_hat_live = y_base + y_lag_live + y_rec_live
        
        # Step 7: Reveal y_true and evaluate prequential losses (LIVE)
        e_live = y_true - y_hat_live
        ell_live = e_live ** 2
        
        # Step 8: Base Linear Predictor update (LIVE)
        self.base.update(x_norm, y_true - y_base, self.live_res)
        
        # Step 9: Active lag taps updates and retention evaluation (LIVE & LIFECYCLE)
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
        
        # Step 10: Active recurrent unit update (LIVE)
        if self.active_rec is not None:
            self.active_rec.update(e_live, x_norm[0], self.live_res)
            
        # Step 11: Causal Scaler update (LIVE)
        self.scaler.update(x_raw, self.live_res)
        
        # =====================================================================
        # SCHEDULER STATE EVALUATION: Determine is_shadow_awake for current step
        # =====================================================================
        is_awake = False
        current_reason = "sleep"
        
        if self.schedule_mode == "S0_CONTINUOUS":
            is_awake = True
            current_reason = "continuous"
        elif self.schedule_mode == "S1_SHADOW_OFF":
            is_awake = False
            current_reason = "disabled"
        elif self.schedule_mode == "S2_PERIODIC":
            self.scheduler_res.int_ops += 1 # integer modulo
            if self.step_count % self.periodic_K == 0:
                is_awake = True
                current_reason = "periodic"
            else:
                is_awake = False
                current_reason = "sleep"
        elif self.schedule_mode == "S3_EVENT_TRIGGERED":
            # Sentinel evaluation: Page-Hinkley cumulative deviation on ell_live
            self.scheduler_res.fp_flops += 4.0 # EMA: 2 FP, diff: 1 FP, add: 1 FP
            self.scheduler_res.int_ops += 2   # U > 0 and U > lambda
            self.ref_loss = 0.99 * self.ref_loss + 0.01 * ell_live
            diff = ell_live - self.ref_loss - self.ph_delta
            self.cum_dev = max(0.0, self.cum_dev + diff)
            
            if self.burst_counter > 0:
                is_awake = True
                self.burst_counter -= 1
                current_reason = "burst_active"
            elif self.cum_dev > self.ph_lambda:
                is_awake = True
                self.burst_counter = self.burst_W - 1 # current step + (W-1) steps
                self.cum_dev = 0.0                    # reset cumulative sum
                self.heartbeat_counter = 0            # reset heartbeat
                self.alarm_count += 1
                self.wake_episodes += 1
                current_reason = "alarm"
            elif self.heartbeat_counter >= self.heartbeat_H:
                is_awake = True
                self.burst_counter = 0                # 1-step heartbeat exploration
                self.heartbeat_counter = 0
                self.heartbeat_wake_count += 1
                self.wake_episodes += 1
                current_reason = "heartbeat"
            else:
                is_awake = False
                self.heartbeat_counter += 1
                current_reason = "sleep"
                
        self.is_shadow_awake = is_awake
        self.wake_reason = current_reason
        if is_awake:
            self.shadow_active_steps += 1
            
        # =====================================================================
        # REMOVABLE SHADOW BLOCK: Execute only if is_shadow_awake is True
        # =====================================================================
        if is_awake:
            # Form Shadow Predictions for counterfactuals
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
            
            ell_B = (y_true - P_BASE) ** 2
            ell_BD = (y_true - P_BASE_D) ** 2
            ell_BR = (y_true - P_BASE_R) ** 2
            ell_BDR = (y_true - P_BASE_D_R) ** 2
            
            # Compute conditional gains
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
                            'evidence': 0.05, 'age': 0
                        })
                    
            # Arbitration & Promotion Logic (T3)
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
                if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                    best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                    if best_cand['evidence'] > 0.02 and best_cand['age'] >= 15:
                        self.active_taps.append({
                            'i': best_cand['i'], 'k': best_cand['k'], 'w': best_cand['w'],
                            'R': best_cand['evidence'], 'age': 0
                        })
                        self.provisional_cands.remove(best_cand)
            elif not d_helps and r_helps:
                decision = "REC_ONLY"
                if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                    self.evictions_lag += len(self.active_taps)
                    self.active_taps = []
                if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_age >= 15:
                    self.active_rec = self.shadow_rec
                    self.shadow_rec = RecurrentScalarUnit()
                    self.rec_evidence = 0.0
                    self.rec_age = 0
            else:
                # Both help independently
                if d_cond and r_cond:
                    decision = "BOTH_COMPLEMENTARY"
                    if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                        best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                        if best_cand['evidence'] > 0.02 and best_cand['age'] >= 15:
                            self.active_taps.append({
                                'i': best_cand['i'], 'k': best_cand['k'], 'w': best_cand['w'],
                                'R': best_cand['evidence'], 'age': 0
                            })
                            self.provisional_cands.remove(best_cand)
                    if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_age >= 15:
                        self.active_rec = self.shadow_rec
                        self.shadow_rec = RecurrentScalarUnit()
                        self.rec_evidence = 0.0
                        self.rec_age = 0
                elif d_cond and not r_cond:
                    decision = "PREFER_LAG"
                    if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                        self.active_rec = None
                        self.evictions_rec += 1
                    if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                        best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                        if best_cand['evidence'] > 0.02 and best_cand['age'] >= 15:
                            self.active_taps.append({
                                'i': best_cand['i'], 'k': best_cand['k'], 'w': best_cand['w'],
                                'R': best_cand['evidence'], 'age': 0
                            })
                            self.provisional_cands.remove(best_cand)
                elif not d_cond and r_cond:
                    decision = "PREFER_REC"
                    if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                        self.evictions_lag += len(self.active_taps)
                        self.active_taps = []
                    if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_age >= 15:
                        self.active_rec = self.shadow_rec
                        self.shadow_rec = RecurrentScalarUnit()
                        self.rec_evidence = 0.0
                        self.rec_age = 0
                else:
                    decision = "REDUNDANT_EQUAL"
                    if self.ema_G_D_B >= self.ema_G_R_B:
                        if self.active_rec is not None and self.ema_G_R_BD < 0.008:
                            self.active_rec = None
                            self.evictions_rec += 1
                        if len(self.active_taps) < 4 and len(self.provisional_cands) > 0:
                            best_cand = max(self.provisional_cands, key=lambda c: c['evidence'])
                            if best_cand['evidence'] > 0.02 and best_cand['age'] >= 15:
                                self.active_taps.append({
                                    'i': best_cand['i'], 'k': best_cand['k'], 'w': best_cand['w'],
                                    'R': best_cand['evidence'], 'age': 0
                                })
                                self.provisional_cands.remove(best_cand)
                    else:
                        if len(self.active_taps) > 0 and self.ema_G_D_BR < 0.005:
                            self.evictions_lag += len(self.active_taps)
                            self.active_taps = []
                        if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_age >= 15:
                            self.active_rec = self.shadow_rec
                            self.shadow_rec = RecurrentScalarUnit()
                            self.rec_evidence = 0.0
                            self.rec_age = 0
            
            # Prune stale provisional candidates
            self.provisional_cands = [
                c for c in self.provisional_cands if not (c['age'] > 150 and c['evidence'] < 0.02)
            ]

        # Tracking structural occupancy
        has_lag = len(self.active_taps) > 0
        has_rec = self.active_rec is not None
        if has_lag and has_rec:
            self.dual_active_steps += 1
            if self.ema_G_D_BR <= self.theta_tol or self.ema_G_R_BD <= self.theta_tol:
                self.redundant_dual_steps += 1
                
        # Total per-step resources
        tot_fp = self.live_res.fp_flops + self.shadow_res.fp_flops + self.scheduler_res.fp_flops
        tot_int = self.live_res.int_ops + self.shadow_res.int_ops + self.scheduler_res.int_ops
        tot_bytes = (self.live_res.bytes_read + self.live_res.bytes_written +
                     self.shadow_res.bytes_read + self.shadow_res.bytes_written +
                     self.scheduler_res.bytes_read + self.scheduler_res.bytes_written)
                     
        # Measured memory
        sched_bytes = 16 if self.schedule_mode == "S3_EVENT_TRIGGERED" else (4 if self.schedule_mode == "S2_PERIODIC" else 0)
        curr_mem = (self.scaler.d * 16 + self.history.get_memory_bytes() + self.base.get_memory_bytes() +
                    len(self.active_taps) * 16 + len(self.provisional_cands) * 16 +
                    (self.active_rec.get_memory_bytes() if self.active_rec is not None else 0) +
                    self.shadow_rec.get_memory_bytes() + 64 + self.corr_grid.nbytes + sched_bytes)
                     
        return {
            'y_hat': y_hat_live,
            'e_live': e_live,
            'ell_live': ell_live,
            'live_fp_flops': self.live_res.fp_flops,
            'shadow_fp_flops': self.shadow_res.fp_flops,
            'scheduler_fp_flops': self.scheduler_res.fp_flops,
            'total_fp_flops': tot_fp,
            'int_ops': tot_int,
            'bytes_moved': tot_bytes,
            'is_shadow_awake': is_awake,
            'wake_reason': current_reason,
            'n_active_taps': len(self.active_taps),
            'has_active_rec': has_rec,
            'structural_state': "BOTH" if (has_lag and has_rec) else ("LAG" if has_lag else ("RECURRENT" if has_rec else "NONE")),
            'occupied_bytes': curr_mem,
            'ema_G_D_B': self.ema_G_D_B,
            'ema_G_R_B': self.ema_G_R_B,
            'ema_G_D_BR': self.ema_G_D_BR,
            'ema_G_R_BD': self.ema_G_R_BD
        }

def run_single_simulation(args: Tuple) -> Dict[str, Any]:
    task_id, seed, sched_id, sched_params = args
    X, y, meta = generate_v02_stream(task_id, seed, 6000)
    
    m = GovernedLEBREModel(
        schedule_mode=sched_id,
        periodic_K=sched_params.get('periodic_K', 5),
        ph_delta=sched_params.get('ph_delta', 0.10),
        ph_lambda=sched_params.get('ph_lambda', 8.0),
        heartbeat_H=sched_params.get('heartbeat_H', 250),
        burst_W=sched_params.get('burst_W', 50),
        corr_grid_dtype=np.float16
    )
    
    preds = []
    live_fps = []
    shadow_fps = []
    sched_fps = []
    tot_fps = []
    int_ops = []
    bytes_moved = []
    duties = []
    memories = []
    states = []
    
    # Trace wake events
    wake_events = []
    
    # State conditioned accumulators
    state_compute = {
        'NONE': {'steps': 0, 'live_fp': 0.0, 'shadow_fp': 0.0, 'sched_fp': 0.0},
        'LAG': {'steps': 0, 'live_fp': 0.0, 'shadow_fp': 0.0, 'sched_fp': 0.0},
        'RECURRENT': {'steps': 0, 'live_fp': 0.0, 'shadow_fp': 0.0, 'sched_fp': 0.0},
        'BOTH': {'steps': 0, 'live_fp': 0.0, 'shadow_fp': 0.0, 'sched_fp': 0.0}
    }
    
    # Specific task diagnostics
    # Switching: switch occurs at t=3000
    first_discovery_step = -1
    retirement_step = -1
    
    # I9 complementarity
    i9_g_d_br = []
    i9_g_r_bd = []
    
    # Quiescent phases
    quiescent_sleep_steps = 0
    quiescent_total_steps = 0
    active_phase_sleep_steps = 0
    active_phase_total_steps = 0
    
    for t in range(6000):
        out = m.step(X[t], y[t])
        
        preds.append(out['y_hat'])
        live_fps.append(out['live_fp_flops'])
        shadow_fps.append(out['shadow_fp_flops'])
        sched_fps.append(out['scheduler_fp_flops'])
        tot_fps.append(out['total_fp_flops'])
        int_ops.append(out['int_ops'])
        bytes_moved.append(out['bytes_moved'])
        duties.append(1.0 if out['is_shadow_awake'] else 0.0)
        memories.append(out['occupied_bytes'])
        st = out['structural_state']
        states.append(st)
        
        sc = state_compute[st]
        sc['steps'] += 1
        sc['live_fp'] += out['live_fp_flops']
        sc['shadow_fp'] += out['shadow_fp_flops']
        sc['sched_fp'] += out['scheduler_fp_flops']
        
        if out['is_shadow_awake'] and out['wake_reason'] in ['alarm', 'heartbeat']:
            wake_events.append({
                'seed': seed,
                'task_id': task_id,
                'scheduler_id': sched_id,
                'step': t + 1,
                'wake_reason': out['wake_reason'],
                'loss_at_wake': float(out['ell_live']),
                'cum_dev_at_wake': float(m.cum_dev),
                'heartbeat_count_at_wake': int(m.heartbeat_counter),
                'active_taps_count': out['n_active_taps'],
                'active_rec_present': out['has_active_rec']
            })
            
        # Task I11 discovery and retirement
        if task_id == 'I11_Regime_Switch_Delay_To_Latent' and t >= 3000:
            if out['has_active_rec'] and first_discovery_step == -1:
                first_discovery_step = t - 3000
            if out['n_active_taps'] == 0 and retirement_step == -1:
                retirement_step = t - 3000
                
        # Task I12 discovery and retirement
        if task_id == 'I12_Regime_Switch_Latent_To_Delay' and t >= 3000:
            if out['n_active_taps'] > 0 and first_discovery_step == -1:
                first_discovery_step = t - 3000
            if not out['has_active_rec'] and retirement_step == -1:
                retirement_step = t - 3000
                
        # Task I13 discovery and retirement
        if task_id == 'I13_Regime_Switch_Hybrid_To_Memoryless' and t >= 3000:
            if out['n_active_taps'] == 0 and not out['has_active_rec'] and retirement_step == -1:
                retirement_step = t - 3000
                
        # Task I14 discovery
        if task_id == 'I14_Intermittent_Hybrid' and t >= 3000:
            if (out['n_active_taps'] > 0 or out['has_active_rec']) and first_discovery_step == -1:
                first_discovery_step = t - 3000
                
        if task_id == 'I9_Hybrid_Delay_Plus_Latent_State':
            i9_g_d_br.append(out['ema_G_D_BR'])
            i9_g_r_bd.append(out['ema_G_R_BD'])
            
        if task_id in ['I7_Quiescent_Continuous_State', 'I8_Quiescent_Discrete_Delay']:
            # t in [2000, 4000] is quiescent
            if 2000 <= t < 4000:
                quiescent_total_steps += 1
                if not out['is_shadow_awake']:
                    quiescent_sleep_steps += 1
            else:
                active_phase_total_steps += 1
                if not out['is_shadow_awake']:
                    active_phase_sleep_steps += 1

    y_arr = np.array(y)
    pred_arr = np.array(preds)
    var_y = float(np.var(y_arr))
    nmse = float(np.mean((y_arr - pred_arr) ** 2)) / (var_y if var_y > 1e-6 else 1.0)
    
    # Post-switch regret on switching streams: excess MSE in t in [3000, 3500] vs baseline [2000, 2500]
    post_switch_regret = 0.0
    if task_id in ['I11_Regime_Switch_Delay_To_Latent', 'I12_Regime_Switch_Latent_To_Delay',
                   'I13_Regime_Switch_Hybrid_To_Memoryless', 'I14_Intermittent_Hybrid']:
        errs = (y_arr - pred_arr) ** 2
        base_mse = float(np.mean(errs[2000:2500]))
        trans_mse = float(np.mean(errs[3000:3500]))
        post_switch_regret = max(0.0, trans_mse - base_mse)
        
    return {
        'seed': seed,
        'task_id': task_id,
        'scheduler_id': sched_id,
        'nmse': nmse,
        'mean_live_fp': float(np.mean(live_fps)),
        'mean_shadow_fp': float(np.mean(shadow_fps)),
        'mean_scheduler_fp': float(np.mean(sched_fps)),
        'mean_total_fp': float(np.mean(tot_fps)),
        'mean_int_ops': float(np.mean(int_ops)),
        'mean_bytes_moved': float(np.mean(bytes_moved)),
        'duty_fraction': float(np.mean(duties)),
        'alarm_count': m.alarm_count,
        'heartbeat_count': m.heartbeat_wake_count,
        'peak_working_bytes': int(max(memories)),
        'status': 'PASS_BUDGET' if np.mean(tot_fps) <= 100.0 else 'FAIL_BUDGET',
        'dual_active_steps': m.dual_active_steps,
        'redundant_dual_steps': m.redundant_dual_steps,
        'first_discovery_step': first_discovery_step,
        'retirement_step': retirement_step,
        'post_switch_regret': post_switch_regret,
        'i9_g_d_br_mean': float(np.mean(i9_g_d_br)) if i9_g_d_br else 0.0,
        'i9_g_r_bd_mean': float(np.mean(i9_g_r_bd)) if i9_g_r_bd else 0.0,
        'quiescent_sleep_frac': (quiescent_sleep_steps / quiescent_total_steps) if quiescent_total_steps > 0 else 0.0,
        'active_sleep_frac': (active_phase_sleep_steps / active_phase_total_steps) if active_phase_total_steps > 0 else 0.0,
        'state_compute': state_compute,
        'wake_events': wake_events
    }

def main():
    print("=" * 80)
    print("LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01: Full Experimental Pipeline")
    print("=" * 80)
    
    out_dir = 'experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01'
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'figures'), exist_ok=True)
    
    sched_params = {
        'periodic_K': 5,
        'ph_delta': 0.10,
        'ph_lambda': 8.0,
        'heartbeat_H': 250,
        'burst_W': 50
    }
    
    schedulers = ["S0_CONTINUOUS", "S1_SHADOW_OFF", "S2_PERIODIC", "S3_EVENT_TRIGGERED"]
    
    # -------------------------------------------------------------
    # 1. DEV Cohort Execution (Seeds 1601..1610, N=10)
    # -------------------------------------------------------------
    dev_seeds = list(range(1601, 1611))
    print(f"\nPhase 3: Executing DEV Cohort (Seeds {dev_seeds[0]}..{dev_seeds[-1]}, N=10)...")
    dev_args = [
        (tid, s, sch, sched_params)
        for s in dev_seeds
        for tid in BENCHMARK_TASKS
        for sch in schedulers
    ]
    print(f"Total DEV runs: {len(dev_args)}")
    t0 = time.time()
    
    dev_results = []
    # Use ProcessPoolExecutor for parallel speed
    with ProcessPoolExecutor() as executor:
        for res in executor.map(run_single_simulation, dev_args, chunksize=10):
            dev_results.append(res)
    print(f"DEV Cohort completed in {time.time() - t0:.1f} s.")
    
    dev_rows = [{k: v for k, v in r.items() if k not in ['state_compute', 'wake_events']} for r in dev_results]
    dev_df = pd.DataFrame(dev_rows)
    dev_df.to_csv(os.path.join(out_dir, 'SHADOW_RENT_DEV_RESULTS.csv'), index=False)
    print(f"Saved {len(dev_df)} rows to SHADOW_RENT_DEV_RESULTS.csv")
    
    # -------------------------------------------------------------
    # 2. Confirmatory Cohort Execution (Seeds 1611..1640, N=30)
    # -------------------------------------------------------------
    final_seeds = list(range(1611, 1641))
    print(f"\nPhase 4: Executing Confirmatory Cohort (Seeds {final_seeds[0]}..{final_seeds[-1]}, N=30)...")
    final_args = [
        (tid, s, sch, sched_params)
        for s in final_seeds
        for tid in BENCHMARK_TASKS
        for sch in schedulers
    ]
    print(f"Total Confirmatory runs: {len(final_args)}")
    t0 = time.time()
    
    final_results = []
    with ProcessPoolExecutor() as executor:
        for res in executor.map(run_single_simulation, final_args, chunksize=10):
            final_results.append(res)
    print(f"Confirmatory Cohort completed in {time.time() - t0:.1f} s.")
    
    final_rows = [{k: v for k, v in r.items() if k not in ['state_compute', 'wake_events']} for r in final_results]
    final_df = pd.DataFrame(final_rows)
    final_df.to_csv(os.path.join(out_dir, 'SHADOW_RENT_FINAL_RESULTS.csv'), index=False)
    print(f"Saved {len(final_df)} rows to SHADOW_RENT_FINAL_RESULTS.csv")
    
    # -------------------------------------------------------------
    # 3. Harvest Wake Events & Exposures
    # -------------------------------------------------------------
    all_wake_events = []
    for r in final_results:
        all_wake_events.extend(r['wake_events'])
    wake_df = pd.DataFrame(all_wake_events)
    wake_df.to_csv(os.path.join(out_dir, 'SHADOW_WAKE_EVENTS.csv'), index=False)
    print(f"Saved {len(wake_df)} wake events to SHADOW_WAKE_EVENTS.csv")
    
    # Exposures by seed
    seed_exp_rows = []
    for s in final_seeds:
        for sch in schedulers:
            sub = final_df[(final_df['seed'] == s) & (final_df['scheduler_id'] == sch)]
            mean_duty = sub['duty_fraction'].mean()
            mean_fp = sub['mean_total_fp'].mean()
            mean_nmse = sub['nmse'].mean()
            seed_exp_rows.append({
                'seed': s,
                'scheduler_id': sch,
                'stream_steps': 6000 * 14,
                'shadow_exposure_count': int(round(mean_duty * 6000 * 14)),
                'shadow_exposure_fraction': mean_duty,
                'mean_total_fp': mean_fp,
                'aggregate_nmse': mean_nmse
            })
    pd.DataFrame(seed_exp_rows).to_csv(os.path.join(out_dir, 'SHADOW_EXPOSURE_BY_SEED.csv'), index=False)
    
    # Resource Vector by Seed
    res_vec_rows = []
    for s in final_seeds:
        for sch in schedulers:
            sub = final_df[(final_df['seed'] == s) & (final_df['scheduler_id'] == sch)]
            res_vec_rows.append({
                'seed': s,
                'scheduler_id': sch,
                'aggregate_nmse': sub['nmse'].mean(),
                'live_fp': sub['mean_live_fp'].mean(),
                'shadow_fp': sub['mean_shadow_fp'].mean(),
                'scheduler_fp': sub['mean_scheduler_fp'].mean(),
                'total_fp': sub['mean_total_fp'].mean(),
                'int_ops': sub['mean_int_ops'].mean(),
                'bytes_moved': sub['mean_bytes_moved'].mean(),
                'peak_bytes': sub['peak_working_bytes'].max()
            })
    pd.DataFrame(res_vec_rows).to_csv(os.path.join(out_dir, 'RESOURCE_VECTOR_BY_SEED.csv'), index=False)
    
    # -------------------------------------------------------------
    # 4. State Conditioned Compute
    # -------------------------------------------------------------
    state_rows = []
    for tid in BENCHMARK_TASKS:
        for sch in schedulers:
            matching = [r for r in final_results if r['task_id'] == tid and r['scheduler_id'] == sch]
            for st in ['NONE', 'LAG', 'RECURRENT', 'BOTH']:
                tot_steps = sum(m['state_compute'][st]['steps'] for m in matching)
                all_steps = sum(sum(m['state_compute'][s_all]['steps'] for s_all in ['NONE', 'LAG', 'RECURRENT', 'BOTH']) for m in matching)
                freq = tot_steps / all_steps if all_steps > 0 else 0.0
                
                live_fp = (sum(m['state_compute'][st]['live_fp'] for m in matching) / tot_steps) if tot_steps > 0 else 0.0
                shadow_fp = (sum(m['state_compute'][st]['shadow_fp'] for m in matching) / tot_steps) if tot_steps > 0 else 0.0
                sched_fp = (sum(m['state_compute'][st]['sched_fp'] for m in matching) / tot_steps) if tot_steps > 0 else 0.0
                state_rows.append({
                    'task_id': tid,
                    'scheduler_id': sch,
                    'state': st,
                    'state_frequency': freq,
                    'live_fp': live_fp,
                    'shadow_fp': shadow_fp,
                    'scheduler_fp': sched_fp,
                    'total_fp': live_fp + shadow_fp + sched_fp
                })
    pd.DataFrame(state_rows).to_csv(os.path.join(out_dir, 'STATE_CONDITIONED_COMPUTE.csv'), index=False)
    
    # -------------------------------------------------------------
    # 5. Statistical Predictive Non-Inferiority
    # -------------------------------------------------------------
    print("\nCalculating Inferential Predictive Non-Inferiority...")
    # Seed level aggregate NMSE
    seed_agg = {}
    for sch in schedulers:
        seed_agg[sch] = [
            final_df[(final_df['seed'] == s) & (final_df['scheduler_id'] == sch)]['nmse'].mean()
            for s in final_seeds
        ]
        
    noninf_rows = []
    # Primary comparisons against S0: S1 vs S0, S2 vs S0, S3 vs S0
    comparisons = [
        ('S2_vs_S0', 'S2_PERIODIC', 'S0_CONTINUOUS', 0.0100),
        ('S3_vs_S0', 'S3_EVENT_TRIGGERED', 'S0_CONTINUOUS', 0.0100),
        ('S1_vs_S0', 'S1_SHADOW_OFF', 'S0_CONTINUOUS', 0.0100),
        ('S3_vs_S2', 'S3_EVENT_TRIGGERED', 'S2_PERIODIC', 0.0100)
    ]
    
    raw_p_values = []
    test_data = []
    
    for comp_name, test_sch, ref_sch, margin in comparisons:
        arr_test = np.array(seed_agg[test_sch])
        arr_ref = np.array(seed_agg[ref_sch])
        diff = arr_test - arr_ref
        mean_diff = float(np.mean(diff))
        std_diff = float(np.std(diff, ddof=1))
        se_diff = std_diff / math.sqrt(len(diff))
        
        # One-sided t-test: H0: mean_diff >= margin vs H1: mean_diff < margin
        t_stat = (mean_diff - margin) / se_diff
        df_deg = len(diff) - 1
        p_val = stats.t.cdf(t_stat, df=df_deg)
        
        ci_95_upper = mean_diff + stats.t.ppf(0.95, df=df_deg) * se_diff
        
        test_data.append({
            'comparison': comp_name,
            'mean_delta_nmse': mean_diff,
            'se_delta': se_diff,
            'ci_95_upper': ci_95_upper,
            't_stat': t_stat,
            'df': df_deg,
            'p_raw': p_val,
            'margin': margin,
            'non_inferior': bool(ci_95_upper < margin)
        })
        if comp_name in ['S2_vs_S0', 'S3_vs_S0']:
            raw_p_values.append(p_val)
            
    # Holm-Bonferroni on primary family (S2 vs S0, S3 vs S0)
    sorted_indices = np.argsort(raw_p_values)
    holm_p = np.zeros(len(raw_p_values))
    m_tests = len(raw_p_values)
    for rank, idx in enumerate(sorted_indices):
        holm_p[idx] = min(1.0, raw_p_values[idx] * (m_tests - rank))
        
    h_idx = 0
    for row in test_data:
        if row['comparison'] in ['S2_vs_S0', 'S3_vs_S0']:
            row['p_holm'] = holm_p[h_idx]
            h_idx += 1
        else:
            row['p_holm'] = row['p_raw']
            
    pd.DataFrame(test_data).to_csv(os.path.join(out_dir, 'PREDICTIVE_NONINFERIORITY.csv'), index=False)
    print("Saved PREDICTIVE_NONINFERIORITY.csv")
    
    # -------------------------------------------------------------
    # 6. Switching Latency & Regret Analysis
    # -------------------------------------------------------------
    switch_tasks = ['I11_Regime_Switch_Delay_To_Latent', 'I12_Regime_Switch_Latent_To_Delay',
                    'I13_Regime_Switch_Hybrid_To_Memoryless', 'I14_Intermittent_Hybrid']
    sw_rows = []
    for tid in switch_tasks:
        for sch in schedulers:
            sub = [r for r in final_results if r['task_id'] == tid and r['scheduler_id'] == sch]
            disc_lats = [r['first_discovery_step'] for r in sub if r['first_discovery_step'] != -1]
            ret_lats = [r['retirement_step'] for r in sub if r['retirement_step'] != -1]
            regrets = [r['post_switch_regret'] for r in sub]
            
            sw_rows.append({
                'task_id': tid,
                'scheduler_id': sch,
                'mean_discovery_latency': float(np.mean(disc_lats)) if disc_lats else 999.0,
                'median_discovery_latency': float(np.median(disc_lats)) if disc_lats else 999.0,
                'mean_retirement_latency': float(np.mean(ret_lats)) if ret_lats else 999.0,
                'median_retirement_latency': float(np.median(ret_lats)) if ret_lats else 999.0,
                'post_switch_regret': float(np.mean(regrets))
            })
    pd.DataFrame(sw_rows).to_csv(os.path.join(out_dir, 'SWITCHING_LATENCY_ANALYSIS.csv'), index=False)
    
    # -------------------------------------------------------------
    # 7. Quiescence Reactivation Analysis
    # -------------------------------------------------------------
    q_rows = []
    for tid in ['I7_Quiescent_Continuous_State', 'I8_Quiescent_Discrete_Delay']:
        for sch in schedulers:
            sub = [r for r in final_results if r['task_id'] == tid and r['scheduler_id'] == sch]
            q_sleep = float(np.mean([r['quiescent_sleep_frac'] for r in sub]))
            act_sleep = float(np.mean([r['active_sleep_frac'] for r in sub]))
            mean_fp = float(np.mean([r['mean_total_fp'] for r in sub]))
            nmse_m = float(np.mean([r['nmse'] for r in sub]))
            q_rows.append({
                'task_id': tid,
                'scheduler_id': sch,
                'quiescent_sleep_fraction': q_sleep,
                'active_sleep_fraction': act_sleep,
                'mean_total_fp': mean_fp,
                'nmse': nmse_m
            })
    pd.DataFrame(q_rows).to_csv(os.path.join(out_dir, 'QUIESCENCE_REACTIVATION_ANALYSIS.csv'), index=False)
    
    # -------------------------------------------------------------
    # 8. I9 Complementarity Analysis
    # -------------------------------------------------------------
    i9_rows = []
    for sch in schedulers:
        sub = [r for r in final_results if r['task_id'] == 'I9_Hybrid_Delay_Plus_Latent_State' and r['scheduler_id'] == sch]
        nmse_m = float(np.mean([r['nmse'] for r in sub]))
        both_frac = float(np.mean([r['dual_active_steps'] / 6000.0 for r in sub]))
        g_d_br = float(np.mean([r['i9_g_d_br_mean'] for r in sub]))
        g_r_bd = float(np.mean([r['i9_g_r_bd_mean'] for r in sub]))
        i9_rows.append({
            'scheduler_id': sch,
            'nmse': nmse_m,
            'frac_dual_active': both_frac,
            'mean_G_D_BR': g_d_br,
            'mean_G_R_BD': g_r_bd,
            'complementarity_preserved': bool(g_d_br > 0.015 and g_r_bd > 0.015)
        })
    pd.DataFrame(i9_rows).to_csv(os.path.join(out_dir, 'I9_COMPLEMENTARITY_ANALYSIS.csv'), index=False)
    
    # -------------------------------------------------------------
    # 9. I10 Redundancy Analysis
    # -------------------------------------------------------------
    i10_rows = []
    for sch in schedulers:
        sub = [r for r in final_results if r['task_id'] == 'I10_Redundant_Temporal_Structure' and r['scheduler_id'] == sch]
        nmse_m = float(np.mean([r['nmse'] for r in sub]))
        both_frac = float(np.mean([r['dual_active_steps'] / 6000.0 for r in sub]))
        redundant_frac = float(np.mean([r['redundant_dual_steps'] / 6000.0 for r in sub]))
        i10_rows.append({
            'scheduler_id': sch,
            'nmse': nmse_m,
            'frac_both': both_frac,
            'frac_redundant_dual': redundant_frac,
            'gate6_redundancy_status': 'FAIL' if both_frac > 0.10 else 'PASS'
        })
    pd.DataFrame(i10_rows).to_csv(os.path.join(out_dir, 'I10_REDUNDANCY_ANALYSIS.csv'), index=False)
    
    # -------------------------------------------------------------
    # 10. False Wake Analysis on Negative Controls
    # -------------------------------------------------------------
    neg_rows = []
    for tid in ['I1_Memoryless_Linear', 'I2_Static_Nonlinear_Negative_Control']:
        for sch in schedulers:
            sub = [r for r in final_results if r['task_id'] == tid and r['scheduler_id'] == sch]
            alarms = float(np.mean([r['alarm_count'] for r in sub]))
            heartbeats = float(np.mean([r['heartbeat_count'] for r in sub]))
            duty = float(np.mean([r['duty_fraction'] for r in sub]))
            tot_fp = float(np.mean([r['mean_total_fp'] for r in sub]))
            neg_rows.append({
                'task_id': tid,
                'scheduler_id': sch,
                'mean_alarm_count': alarms,
                'alarm_rate_per_1000': alarms / 6.0,
                'mean_heartbeat_count': heartbeats,
                'duty_fraction': duty,
                'total_fp': tot_fp
            })
    pd.DataFrame(neg_rows).to_csv(os.path.join(out_dir, 'FALSE_WAKE_ANALYSIS.csv'), index=False)
    
    # -------------------------------------------------------------
    # 11. Scheduler Multi-Objective Pareto Analysis
    # -------------------------------------------------------------
    # Aggregate objectives across all 14 tasks
    cand_metrics = {}
    for sch in schedulers:
        sub = final_df[final_df['scheduler_id'] == sch]
        cand_metrics[sch] = {
            'nmse': sub['nmse'].mean(),
            'total_fp': sub['mean_total_fp'].mean(),
            'int_ops': sub['mean_int_ops'].mean(),
            'bytes_moved': sub['mean_bytes_moved'].mean(),
            'peak_bytes': sub['peak_working_bytes'].max()
        }
        
    pareto_rows = []
    for a in schedulers:
        for b in schedulers:
            if a == b:
                continue
            ma = cand_metrics[a]
            mb = cand_metrics[b]
            
            # Check weak dominance (all <=)
            a_le_b = (ma['nmse'] <= mb['nmse'] and
                      ma['total_fp'] <= mb['total_fp'] and
                      ma['int_ops'] <= mb['int_ops'] and
                      ma['bytes_moved'] <= mb['bytes_moved'] and
                      ma['peak_bytes'] <= mb['peak_bytes'])
            a_lt_b = (ma['nmse'] < mb['nmse'] or
                      ma['total_fp'] < mb['total_fp'] or
                      ma['int_ops'] < mb['int_ops'] or
                      ma['bytes_moved'] < mb['bytes_moved'] or
                      ma['peak_bytes'] < mb['peak_bytes'])
            a_dominates_b = a_le_b and a_lt_b
            
            b_le_a = (mb['nmse'] <= ma['nmse'] and
                      mb['total_fp'] <= ma['total_fp'] and
                      mb['int_ops'] <= ma['int_ops'] and
                      mb['bytes_moved'] <= ma['bytes_moved'] and
                      mb['peak_bytes'] <= ma['peak_bytes'])
            b_lt_a = (mb['nmse'] < ma['nmse'] or
                      mb['total_fp'] < ma['total_fp'] or
                      mb['int_ops'] < ma['int_ops'] or
                      mb['bytes_moved'] < ma['bytes_moved'] or
                      mb['peak_bytes'] < ma['peak_bytes'])
            b_dominates_a = b_le_a and b_lt_a
            
            rel = "A_DOMINATES_B" if a_dominates_b else ("B_DOMINATES_A" if b_dominates_a else "NON_DOMINATED_TRADEOFF")
            
            tradeoffs = []
            if ma['nmse'] < mb['nmse']: tradeoffs.append(f"{a}_better_nmse")
            if mb['nmse'] < ma['nmse']: tradeoffs.append(f"{b}_better_nmse")
            if ma['total_fp'] < mb['total_fp']: tradeoffs.append(f"{a}_lower_fp")
            if mb['total_fp'] < ma['total_fp']: tradeoffs.append(f"{b}_lower_fp")
            
            pareto_rows.append({
                'candidate_A': a,
                'candidate_B': b,
                'A_dominates_B': a_dominates_b,
                'B_dominates_A': b_dominates_a,
                'relation': rel,
                'tradeoff_dimensions': "; ".join(tradeoffs)
            })
    pd.DataFrame(pareto_rows).to_csv(os.path.join(out_dir, 'SCHEDULER_PARETO_ANALYSIS.csv'), index=False)
    print("Saved SCHEDULER_PARETO_ANALYSIS.csv")
    print("\nAll simulations and forensic analyses generated successfully!")

if __name__ == '__main__':
    main()
