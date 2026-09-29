#!/usr/bin/env python3
"""
resource_accounting_instrumentation.py: Precision Multi-View Hardware-Independent Resource Counter.
Implements the frozen operation taxonomy for RESOURCE-ACCOUNTING-RECONCILIATION-01:
- FLOATING_POINT_OPS
- INTEGER_OPS
- MEMORY_TRAFFIC (Bytes Read, Bytes Written, Total Bytes Moved)
- CONTROL_OPS (Branches, Modulo, Comparisons)
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple

class ResourceCounter:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Floating Point Operations (IEEE-754)
        self.fp_add = 0
        self.fp_sub = 0
        self.fp_mul = 0
        self.fp_div = 0
        self.fp_sqrt = 0
        self.fp_compare = 0
        self.mac_count = 0
        
        # Integer & Conversion Operations
        self.int_add = 0
        self.int_sub = 0
        self.int_mul = 0
        self.int_div = 0
        self.int_shift = 0
        self.int_compare = 0
        self.bitwise_op = 0
        self.round_op = 0
        self.clip_op = 0
        self.cast_fp_to_int = 0
        self.cast_int_to_fp = 0
        self.abs_op = 0
        self.min_max = 0
        self.modulo_op = 0
        
        # Memory Traffic (Bytes)
        self.bytes_read = 0
        self.bytes_written = 0
        
        # Control
        self.branches = 0
        
    @property
    def total_fp_flops_standardized(self) -> int:
        # Standardized: Pure Add(1) + Sub(1) + Mul(1) + Div(1) + Sqrt(1) + Compare(1) + 2*MAC(2)
        return (self.fp_add + self.fp_sub + self.fp_mul + self.fp_div + 
                self.fp_sqrt + self.fp_compare + 2 * self.mac_count)
                
    @property
    def total_integer_ops(self) -> int:
        return (self.int_add + self.int_sub + self.int_mul + self.int_div + 
                self.int_shift + self.int_compare + self.bitwise_op + 
                self.round_op + self.clip_op + self.cast_fp_to_int + 
                self.cast_int_to_fp + self.abs_op + self.min_max + self.modulo_op)
                
    @property
    def total_bytes_moved(self) -> int:
        return self.bytes_read + self.bytes_written

    def add(self, other: 'ResourceCounter'):
        self.fp_add += other.fp_add
        self.fp_sub += other.fp_sub
        self.fp_mul += other.fp_mul
        self.fp_div += other.fp_div
        self.fp_sqrt += other.fp_sqrt
        self.fp_compare += other.fp_compare
        self.mac_count += other.mac_count
        
        self.int_add += other.int_add
        self.int_sub += other.int_sub
        self.int_mul += other.int_mul
        self.int_div += other.int_div
        self.int_shift += other.int_shift
        self.int_compare += other.int_compare
        self.bitwise_op += other.bitwise_op
        self.round_op += other.round_op
        self.clip_op += other.clip_op
        self.cast_fp_to_int += other.cast_fp_to_int
        self.cast_int_to_fp += other.cast_int_to_fp
        self.abs_op += other.abs_op
        self.min_max += other.min_max
        self.modulo_op += other.modulo_op
        
        self.bytes_read += other.bytes_read
        self.bytes_written += other.bytes_written
        self.branches += other.branches

    def snapshot(self) -> Dict[str, int]:
        return {
            'fp_flops': self.total_fp_flops_standardized,
            'mac_count': self.mac_count,
            'int_ops': self.total_integer_ops,
            'bytes_read': self.bytes_read,
            'bytes_written': self.bytes_written,
            'bytes_moved': self.total_bytes_moved,
            'branches': self.branches
        }


class InstrumentedAdaptiveFilter:
    """
    Standardized Adaptive Filter with disaggregated operation instrumentation.
    Provides mathematically exact parity with HistoryBoundedAdaptiveFilter while
    recording every primitive into the 4-channel resource taxonomy.
    """
    def __init__(self, provider, d_features: int = 5, l_max: int = 32, k_max: int = 4):
        self.provider = provider
        self.D = d_features
        self.L_max = l_max
        self.K_max = k_max
        self.M = 2 # Rotating candidate probes
        self.mu_base = 0.10
        self.mu_lag = 0.08
        self.theta_promote = 0.15
        self.theta_evict = 0.05
        self.include_recurrence = True

        # Base Linear Model (FP32)
        self.w_base = np.zeros(d_features, dtype=np.float32)

        # Scalar Recurrent State
        self.s = 0.0
        self.lam = 0.90
        self.w_out = 0.0

        # Active Taps & Candidates
        self.active_taps: List[Dict[str, Any]] = []
        self.provisional_cands: List[Dict[str, Any]] = []

        # Rotating probe grid
        self.grid_pairs = [(i, k) for i in range(d_features) for k in range(1, l_max + 1)]
        self.probe_idx = 0
        self.corr_grid = np.zeros((d_features, l_max + 1), dtype=np.float32)

    def step(self, x_t: np.ndarray, y_t: float, t: int) -> Tuple[float, float, Dict[str, ResourceCounter]]:
        # Breakdown counters per component
        comp_counters = {
            'HISTORY_WRITE': ResourceCounter(),
            'BASE_FORWARD': ResourceCounter(),
            'ACTIVE_FORWARD': ResourceCounter(),
            'RECURRENT_FORWARD': ResourceCounter(),
            'SHADOW_SCORING': ResourceCounter(),
            'BASE_UPDATE': ResourceCounter(),
            'ACTIVE_UPDATE': ResourceCounter(),
            'RECURRENT_UPDATE': ResourceCounter(),
            'CANDIDATE_PROBING': ResourceCounter(),
            'PROMOTION_EVICTION': ResourceCounter()
        }

        # ---------------------------------------------------------------------
        # 1. History Write
        # ---------------------------------------------------------------------
        c_hw = comp_counters['HISTORY_WRITE']
        # Call provider write while accounting for operations explicitly
        if "H0" in self.provider.provider_id:
            self.provider.buffer[:, self.provider.head] = x_t.astype(np.float32)
            self.provider.head = (self.provider.head + 1) % (self.L_max + 1)
            c_hw.modulo_op += 1
            c_hw.int_add += 1
            c_hw.bytes_written += self.D * 4 # 5 * 4 = 20 B
        elif "H1" in self.provider.provider_id:
            self.provider.buffer[:, self.provider.head] = x_t.astype(np.float16)
            self.provider.head = (self.provider.head + 1) % (self.L_max + 1)
            c_hw.cast_fp_to_int += self.D # FP32 -> FP16 cast
            c_hw.modulo_op += 1
            c_hw.int_add += 1
            c_hw.bytes_written += self.D * 2 # 10 B
        elif "H2" in self.provider.provider_id:
            self.provider.total_writes += self.D
            for i in range(self.D):
                ax = abs(float(x_t[i]))
                c_hw.abs_op += 1
                c_hw.fp_compare += 1
                c_hw.branches += 1
                if ax > self.provider.scale[i]:
                    self.provider.scale[i] = max(1.0, 0.99 * self.provider.scale[i] + 0.01 * (ax * 1.2))
                    c_hw.fp_mul += 2
                    c_hw.fp_add += 1
                    c_hw.min_max += 1
                scaled = (x_t[i] / self.provider.scale[i]) * 32767.0
                c_hw.fp_div += 1
                c_hw.fp_mul += 1
                c_hw.round_op += 1
                c_hw.clip_op += 2
                c_hw.cast_fp_to_int += 1
                q = int(np.clip(np.round(scaled), -32767, 32767))
                self.provider.buffer[i, self.provider.head] = q
                c_hw.bytes_written += 2
            self.provider.head = (self.provider.head + 1) % (self.L_max + 1)
            c_hw.modulo_op += 1
            c_hw.int_add += 1
        elif "H3" in self.provider.provider_id:
            self.provider.total_writes += self.D
            for i in range(self.D):
                ax = abs(float(x_t[i]))
                c_hw.abs_op += 1
                c_hw.fp_compare += 1
                c_hw.branches += 1
                if ax > self.provider.scale[i]:
                    self.provider.scale[i] = max(1.0, 0.99 * self.provider.scale[i] + 0.01 * (ax * 1.2))
                    c_hw.fp_mul += 2
                    c_hw.fp_add += 1
                    c_hw.min_max += 1
                scaled = (x_t[i] / self.provider.scale[i]) * 127.0
                c_hw.fp_div += 1
                c_hw.fp_mul += 1
                c_hw.round_op += 1
                c_hw.clip_op += 2
                c_hw.cast_fp_to_int += 1
                q = int(np.clip(np.round(scaled), -127, 127))
                self.provider.buffer[i, self.provider.head] = q
                c_hw.bytes_written += 1
            self.provider.head = (self.provider.head + 1) % (self.L_max + 1)
            c_hw.modulo_op += 1
            c_hw.int_add += 1
        elif "H4" in self.provider.provider_id:
            _ = self.provider.write(x_t)
            c_hw.bytes_written += self.D * 2 # write recent FP16
            c_hw.bytes_written += self.D * 1 # evict to INT8
            c_hw.modulo_op += 2

        # Helper to query provider and instrument query
        def query_instrumented(channel: int, lag: int, counter: ResourceCounter) -> float:
            counter.int_sub += 2
            counter.modulo_op += 1
            if "H0" in self.provider.provider_id:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.bytes_read += 4
                return val
            elif "H1" in self.provider.provider_id:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.cast_int_to_fp += 1
                counter.bytes_read += 2
                return val
            elif "H2" in self.provider.provider_id:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.cast_int_to_fp += 1
                counter.fp_mul += 1
                counter.bytes_read += 2
                return val
            elif "H3" in self.provider.provider_id:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.cast_int_to_fp += 1
                counter.fp_mul += 1 # val = q * (scale / 127.0)
                counter.bytes_read += 1 # INT8 buffer read
                return val
            elif "H4" in self.provider.provider_id:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.cast_int_to_fp += 1
                if lag > self.provider.split:
                    counter.fp_mul += 1
                    counter.bytes_read += 1
                else:
                    counter.bytes_read += 2
                return val
            else:
                val, _, _, _, _ = self.provider.query(channel, lag)
                counter.bytes_read += 2
                return val

        # ---------------------------------------------------------------------
        # 2. Live Forward Pass
        # ---------------------------------------------------------------------
        # Base Linear
        c_bf = comp_counters['BASE_FORWARD']
        y_base = float(np.dot(self.w_base, x_t))
        c_bf.mac_count += self.D
        c_bf.bytes_read += self.D * 4 # w_base
        c_bf.bytes_read += self.D * 4 # x_t

        # Active Lags
        c_af = comp_counters['ACTIVE_FORWARD']
        y_lag = 0.0
        active_vals = []
        for tap in self.active_taps:
            val = query_instrumented(tap['i'], tap['k'], c_af)
            active_vals.append(val)
            y_lag += tap['w'] * val
            c_af.mac_count += 1
            c_af.bytes_read += 4 # tap['w']

        # Recurrent Unit Forward
        c_rf = comp_counters['RECURRENT_FORWARD']
        y_rec = 0.0
        if self.include_recurrence:
            in_drive = 0.1 * x_t[0] - 0.1 * x_t[1] if self.D >= 2 else 0.1 * x_t[0]
            c_rf.fp_mul += 2 if self.D >= 2 else 1
            c_rf.fp_sub += 1 if self.D >= 2 else 0
            # s = tanh(lam * s + in_drive)
            self.s = math.tanh(self.lam * self.s + in_drive)
            c_rf.fp_mul += 1
            c_rf.fp_add += 1
            c_rf.fp_mul += 8 # tanh priced at 8 FLOPs transcendental
            y_rec = self.w_out * self.s
            c_rf.fp_mul += 1
            c_rf.bytes_read += 8 # w_out, s

        y_hat = y_base + y_lag + y_rec
        e_live = y_t - y_hat
        c_bf.fp_add += 2 # y_base + y_lag + y_rec
        c_bf.fp_sub += 1 # y_t - y_hat

        # ---------------------------------------------------------------------
        # 3. Counterfactual Candidate Scoring
        # ---------------------------------------------------------------------
        c_cs = comp_counters['SHADOW_SCORING']
        for cand in self.provisional_cands:
            c_val = query_instrumented(cand['i'], cand['k'], c_cs)
            y_cand = y_hat + cand['w_shadow'] * c_val
            c_cs.fp_mul += 1
            c_cs.fp_add += 1
            e_cand = y_t - y_cand
            c_cs.fp_sub += 1
            cand_gain = (e_live ** 2) - (e_cand ** 2)
            c_cs.fp_mul += 2
            c_cs.fp_sub += 1
            cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * cand_gain
            c_cs.fp_mul += 2
            c_cs.fp_add += 1
            cand['age'] += 1
            c_cs.int_add += 1

            # Shadow gradient update with normalization
            denom_c = (c_val ** 2) + 1.0
            c_cs.fp_mul += 1
            c_cs.fp_add += 1
            cand['w_shadow'] += (0.05 / denom_c) * e_cand * c_val
            c_cs.fp_div += 1
            c_cs.fp_mul += 2
            c_cs.fp_add += 1
            cand['w_shadow'] = float(np.clip(cand['w_shadow'], -5.0, 5.0))
            c_cs.clip_op += 2
            c_cs.bytes_read += 12 # shadow state
            c_cs.bytes_written += 12

        # ---------------------------------------------------------------------
        # 4. Candidate Promotion Gate
        # ---------------------------------------------------------------------
        c_pe = comp_counters['PROMOTION_EVICTION']
        promoted = []
        for cand in self.provisional_cands:
            c_pe.fp_compare += 1
            c_pe.int_compare += 1
            c_pe.branches += 2
            if cand['evidence'] >= self.theta_promote and cand['age'] >= 30:
                if not any(t_['i'] == cand['i'] and t_['k'] == cand['k'] for t_ in self.active_taps):
                    if len(self.active_taps) < self.K_max:
                        self.active_taps.append({
                            'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                            'R': cand['evidence'], 'age': 0, 'zero_count': 0
                        })
                        promoted.append(cand)
                    else:
                        c_pe.int_compare += len(self.active_taps) # argmin search
                        weakest_idx = int(np.argmin([t_['R'] for t_ in self.active_taps]))
                        weakest_tap = self.active_taps[weakest_idx]
                        c_pe.fp_compare += 1
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

        # ---------------------------------------------------------------------
        # 5. Live Model Weight Adaptation
        # ---------------------------------------------------------------------
        # Base Linear Update
        c_bu = comp_counters['BASE_UPDATE']
        denom_base = float(np.dot(x_t, x_t)) + 1e-4
        c_bu.mac_count += self.D
        c_bu.fp_add += 1
        scale_step = (self.mu_base / denom_base) * e_live
        c_bu.fp_div += 1
        c_bu.fp_mul += 1
        self.w_base += scale_step * x_t
        c_bu.mac_count += self.D
        c_bu.bytes_written += self.D * 4

        # Active Taps Update
        c_au = comp_counters['ACTIVE_UPDATE']
        for j, tap in enumerate(self.active_taps):
            # Query delayed value (re-use queried value or query)
            val = active_vals[j] if j < len(active_vals) else query_instrumented(tap['i'], tap['k'], c_au)
            denom_tap = (val ** 2) + 1.0
            c_au.fp_mul += 1
            c_au.fp_add += 1
            tap['w'] += (self.mu_lag / denom_tap) * e_live * val
            c_au.fp_div += 1
            c_au.fp_mul += 2
            c_au.fp_add += 1
            tap['w'] = float(np.clip(tap['w'], -5.0, 5.0))
            c_au.clip_op += 2
            tap['age'] += 1
            c_au.int_add += 1

            # Relevance & Obsolescence
            y_without = y_hat - tap['w'] * val
            c_au.fp_mul += 1
            c_au.fp_sub += 1
            e_without = y_t - y_without
            c_au.fp_sub += 1
            marginal_gain = (e_without ** 2) - (e_live ** 2)
            c_au.fp_mul += 2
            c_au.fp_sub += 1
            
            c_au.abs_op += 1
            c_au.fp_compare += 1
            c_au.branches += 1
            if abs(val) > 0.1:
                tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
                c_au.fp_mul += 2
                c_au.fp_add += 1

            # Eviction check
            c_au.fp_compare += 1
            c_au.int_compare += 1
            c_au.branches += 2
            if tap['R'] < self.theta_evict and tap['age'] > 300:
                if abs(val) > 0.1:
                    tap['evict'] = True

            c_au.bytes_read += 8 # w, R
            c_au.bytes_written += 8

        self.active_taps = [t_ for t_ in self.active_taps if not t_.get('evict', False)]

        # Recurrent Unit Adaptation
        c_ru = comp_counters['RECURRENT_UPDATE']
        if self.include_recurrence:
            self.w_out += 0.05 * e_live * self.s
            c_ru.fp_mul += 2
            c_ru.fp_add += 1
            c_ru.bytes_written += 4

        # ---------------------------------------------------------------------
        # 6. Bounded Candidate Probing
        # ---------------------------------------------------------------------
        c_cp = comp_counters['CANDIDATE_PROBING']
        for _ in range(self.M):
            cand_pair = self.grid_pairs[self.probe_idx]
            self.probe_idx = (self.probe_idx + 1) % len(self.grid_pairs)
            c_cp.int_add += 1
            c_cp.modulo_op += 1
            i_p, k_p = cand_pair
            
            if not any(t_['i'] == i_p and t_['k'] == k_p for t_ in self.active_taps) and \
               not any(c_['i'] == i_p and c_['k'] == k_p for c_ in self.provisional_cands):
                past_val = query_instrumented(i_p, k_p, c_cp)
                self.corr_grid[i_p, k_p] = 0.95 * self.corr_grid[i_p, k_p] + 0.05 * (e_live * past_val)
                c_cp.fp_mul += 2
                c_cp.fp_add += 1
                c_cp.bytes_read += 4
                c_cp.bytes_written += 4
                
                c_cp.abs_op += 1
                c_cp.fp_compare += 1
                c_cp.branches += 1
                if abs(self.corr_grid[i_p, k_p]) > 0.08 and len(self.provisional_cands) < 8:
                    self.provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w_shadow': 0.0,
                        'evidence': abs(self.corr_grid[i_p, k_p]) * 0.5, 'age': 0
                    })
                    c_cp.fp_mul += 1
                    c_cp.bytes_written += 16

        return y_hat, e_live, comp_counters
