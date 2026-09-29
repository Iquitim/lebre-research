import sys
import os
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_corrective_confirmation import (
    ResourceVector,
    CausalStandardScaler,
    FP16HistoryRingBuffer,
    LinearBasePredictor,
    RecurrentScalarUnit,
    CorrectedCanonicalLEBREModel
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
        ph_delta: float = 0.05,
        ph_lambda: float = 6.0,
        heartbeat_H: int = 200,
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
            'structural_state': "BOTH" if (has_lag and has_rec) else ("LAG" if has_lag else ("RECURRENT" if has_rec else "NONE"))
        }

def evaluate_dev_grid():
    dev_seeds = list(range(1601, 1606)) # 5 seeds for fast calibration
    print(f'Starting Page-Hinkley Grid Evaluation on DEV seeds {dev_seeds}...')
    
    # 12 Candidate configurations
    deltas = [0.05, 0.10]
    lambdas = [4.0, 6.0, 8.0]
    heartbeats = [150, 250]
    
    grid = []
    cfg_idx = 1
    for d in deltas:
        for l in lambdas:
            for h in heartbeats:
                grid.append({
                    'config_id': f'C{cfg_idx:02d}',
                    'ph_delta': d,
                    'ph_lambda': l,
                    'heartbeat_H': h,
                    'burst_W': 50
                })
                cfg_idx += 1
                
    results = []
    # Test on representative tasks: I1 (Memoryless), I3 (Pure Lag), I6 (Pure Rec), I9 (Hybrid), I11 (Switching)
    rep_tasks = [
        'I1_Memoryless_Linear',
        'I3_Single_Exact_Delay',
        'I6_Continuous_Latent_State',
        'I9_Hybrid_Delay_Plus_Latent_State',
        'I11_Regime_Switch_Delay_To_Latent'
    ]
    
    for cfg in grid:
        t0 = time.time()
        nmse_list = []
        duty_list = []
        fp_list = []
        switch_latencies = []
        
        for s in dev_seeds:
            for tid in rep_tasks:
                X, y, meta = generate_v02_stream(tid, s, 6000)
                m = GovernedLEBREModel(
                    schedule_mode="S3_EVENT_TRIGGERED",
                    ph_delta=cfg['ph_delta'],
                    ph_lambda=cfg['ph_lambda'],
                    heartbeat_H=cfg['heartbeat_H'],
                    burst_W=cfg['burst_W'],
                    corr_grid_dtype=np.float16
                )
                
                preds = []
                fps = []
                duties = []
                first_wake_post_switch = -1
                
                for t in range(6000):
                    out = m.step(X[t], y[t])
                    preds.append(out['y_hat'])
                    fps.append(out['total_fp_flops'])
                    duties.append(1.0 if out['is_shadow_awake'] else 0.0)
                    
                    if tid == 'I11_Regime_Switch_Delay_To_Latent' and t >= 3000 and first_wake_post_switch == -1:
                        if out['is_shadow_awake'] and out['wake_reason'] == 'alarm':
                            first_wake_post_switch = t - 3000
                            
                y_arr = np.array(y)
                pred_arr = np.array(preds)
                var_y = float(np.var(y_arr))
                nmse = float(np.mean((y_arr - pred_arr) ** 2)) / (var_y if var_y > 1e-6 else 1.0)
                
                nmse_list.append(nmse)
                duty_list.append(np.mean(duties))
                fp_list.append(np.mean(fps))
                if first_wake_post_switch != -1:
                    switch_latencies.append(first_wake_post_switch)
                    
        elapsed = time.time() - t0
        mean_nmse = float(np.mean(nmse_list))
        mean_duty = float(np.mean(duty_list))
        mean_fp = float(np.mean(fp_list))
        mean_sw_lat = float(np.mean(switch_latencies)) if switch_latencies else 999.0
        
        status = "PASS_BUDGET" if mean_fp <= 100.0 else "FAIL_BUDGET"
        
        res_row = {
            'config_id': cfg['config_id'],
            'ph_delta': cfg['ph_delta'],
            'ph_lambda': cfg['ph_lambda'],
            'heartbeat_H': cfg['heartbeat_H'],
            'burst_W': cfg['burst_W'],
            'mean_duty': mean_duty,
            'mean_total_fp': mean_fp,
            'mean_nmse': mean_nmse,
            'mean_switch_alarm_delay': mean_sw_lat,
            'status': status
        }
        results.append(res_row)
        print(f"[{cfg['config_id']}] delta={cfg['ph_delta']:.2f} lam={cfg['ph_lambda']:.1f} H={cfg['heartbeat_H']} | Duty={mean_duty:.3f} | Total_FP={mean_fp:.2f} | NMSE={mean_nmse:.4f} | SwDelay={mean_sw_lat:.1f} | {status} ({elapsed:.1f}s)")
        
    df = pd.DataFrame(results)
    out_csv = 'experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/EVENT_TRIGGER_GRID.csv'
    df.to_csv(out_csv, index=False)
    print(f'Wrote {len(df)} grid results to {out_csv}')

if __name__ == '__main__':
    evaluate_dev_grid()
