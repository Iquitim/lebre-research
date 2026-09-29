#!/usr/bin/env python3
"""
bench_dynamic_lags.py: Hidden-Support Benchmark Generator (D1-D12)
for DYNAMIC-LAG-LIFECYCLE-01.

Generates reproducible synthetic streaming tasks where ground-truth temporal delays
are hidden from the learner. Also outputs the hidden support manifest for auditing.
"""

import numpy as np
from typing import Dict, Any, List, Tuple

def generate_dynamic_lag_stream(
    task_id: str,
    seed: int,
    total_steps: int = 10000,
    d_features: int = 5
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Returns:
      X: (total_steps, d_features) float64 array
      y: (total_steps,) float64 array
      meta: dictionary describing ground-truth support and regime transitions
    """
    rng = np.random.RandomState(seed)
    
    # Base inputs: standard Gaussian white noise
    X = rng.normal(0.0, 1.0, size=(total_steps, d_features))
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.normal(0.0, 0.6, size=total_steps) # sigma = 0.6 => noise var = 0.36
    
    meta = {
        "task_id": task_id,
        "seed": seed,
        "total_steps": total_steps,
        "d_features": d_features,
        "support_regimes": []
    }
    
    # -------------------------------------------------------------
    # D1: Single Static Delay
    # -------------------------------------------------------------
    if task_id == "D1_Single_Static_Delay":
        k1 = int((seed % 12) + 3) # delay in [3, 14]
        i1 = int(seed % min(d_features, 3))
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(i1, k1)], "coeffs": [0.8]
        })
        for t in range(k1, total_steps):
            y[t] = 0.8 * X[t - k1, i1] + noise[t]

    # -------------------------------------------------------------
    # D2: Multi-Tap Sparse Delay
    # -------------------------------------------------------------
    elif task_id == "D2_Multi_Tap_Sparse_Delay":
        k1 = int((seed % 4) + 3) # [3, 6]
        k2 = int(k1 + 7)         # [10, 13]
        i1 = 0
        i2 = 1 if d_features > 1 else 0
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(i1, k1), (i2, k2)], "coeffs": [0.5, 0.5]
        })
        for t in range(k2, total_steps):
            y[t] = 0.5 * X[t - k1, i1] + 0.5 * X[t - k2, i2] + noise[t]

    # -------------------------------------------------------------
    # D3: Widely Separated Support
    # -------------------------------------------------------------
    elif task_id == "D3_Widely_Separated_Support":
        k1 = 2
        k2 = 28
        i1 = 0
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(i1, k1), (i1, k2)], "coeffs": [0.6, 0.6]
        })
        for t in range(k2, total_steps):
            y[t] = 0.6 * X[t - k1, i1] + 0.6 * X[t - k2, i1] + noise[t]

    # -------------------------------------------------------------
    # D4: Abrupt Support Relocation
    # -------------------------------------------------------------
    elif task_id == "D4_Abrupt_Support_Relocation":
        # 3 Regimes: 0..3300, 3300..6600, 6600..10000
        meta["support_regimes"] = [
            {"start": 0, "end": 3300, "support": [(0, 4)], "coeffs": [0.8]},
            {"start": 3300, "end": 6600, "support": [(1, 10)], "coeffs": [0.8]},
            {"start": 6600, "end": total_steps, "support": [(0, 16)], "coeffs": [0.8]}
        ]
        for t in range(total_steps):
            if t < 3300:
                y[t] = (0.8 * X[t - 4, 0] if t >= 4 else 0.0) + noise[t]
            elif t < 6600:
                y[t] = (0.8 * X[t - 10, 1] if t >= 10 else 0.0) + noise[t]
            else:
                y[t] = (0.8 * X[t - 16, 0] if t >= 16 else 0.0) + noise[t]

    # -------------------------------------------------------------
    # D5: Tap Birth
    # -------------------------------------------------------------
    elif task_id == "D5_Tap_Birth":
        meta["support_regimes"] = [
            {"start": 0, "end": 5000, "support": [], "coeffs": []},
            {"start": 5000, "end": total_steps, "support": [(1, 8)], "coeffs": [0.8]}
        ]
        for t in range(total_steps):
            y_lin = 0.6 * X[t, 0]
            if t >= 5000:
                y[t] = y_lin + (0.8 * X[t - 8, 1] if t >= 8 else 0.0) + noise[t]
            else:
                y[t] = y_lin + noise[t]

    # -------------------------------------------------------------
    # D6: Tap Death
    # -------------------------------------------------------------
    elif task_id == "D6_Tap_Death":
        meta["support_regimes"] = [
            {"start": 0, "end": 5000, "support": [(0, 8)], "coeffs": [0.8]},
            {"start": 5000, "end": total_steps, "support": [], "coeffs": []}
        ]
        for t in range(total_steps):
            if t < 5000:
                y[t] = (0.8 * X[t - 8, 0] if t >= 8 else 0.0) + noise[t]
            else:
                y[t] = noise[t]

    # -------------------------------------------------------------
    # D7: Quiescent Tap
    # -------------------------------------------------------------
    elif task_id == "D7_Quiescent_Tap":
        # Feature 0 becomes zero between 3000 and 7000
        X[3000:7000, 0] = 0.0
        meta["support_regimes"] = [
            {"start": 0, "end": 3000, "support": [(0, 6)], "coeffs": [0.8], "active": True},
            {"start": 3000, "end": 7000, "support": [(0, 6)], "coeffs": [0.8], "active": False},
            {"start": 7000, "end": total_steps, "support": [(0, 6)], "coeffs": [0.8], "active": True}
        ]
        for t in range(6, total_steps):
            y[t] = 0.8 * X[t - 6, 0] + noise[t]

    # -------------------------------------------------------------
    # D8: Amplitude Drift
    # -------------------------------------------------------------
    elif task_id == "D8_Amplitude_Drift":
        k1 = 5
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(0, k1)], "coeffs": ["drifting"]
        })
        for t in range(k1, total_steps):
            w_t = 0.8 + 0.4 * np.sin(2.0 * np.pi * t / 4000.0)
            y[t] = w_t * X[t - k1, 0] + noise[t]

    # -------------------------------------------------------------
    # D9: Memoryless Negative Control
    # -------------------------------------------------------------
    elif task_id == "D9_Memoryless_Negative_Control":
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [], "coeffs": []
        })
        for t in range(total_steps):
            y[t] = 0.6 * X[t, 0] + 0.5 * X[t, 1] + noise[t]

    # -------------------------------------------------------------
    # D10: Dense FIR Control
    # -------------------------------------------------------------
    elif task_id == "D10_Dense_FIR_Control":
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(0, k) for k in range(1, 7)], "coeffs": [0.6**k for k in range(1, 7)]
        })
        for t in range(6, total_steps):
            val = sum((0.6**k) * X[t - k, 0] for k in range(1, 7))
            y[t] = val + noise[t]

    # -------------------------------------------------------------
    # D11: Continuous-State Control (Bistable Latch)
    # -------------------------------------------------------------
    elif task_id == "D11_Continuous_State_Control":
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [], "coeffs": [], "recurrent_state": True
        })
        s = 0.0
        for t in range(total_steps):
            # Input 0: Set pulse, Input 1: Reset pulse
            pulse_s = 1.0 if X[t, 0] > 1.8 else 0.0
            pulse_r = 1.0 if X[t, 1] > 1.8 else 0.0
            if pulse_s: s = 1.0
            elif pulse_r: s = -1.0
            y[t] = s + noise[t]

    # -------------------------------------------------------------
    # D12: Hybrid Memory (Delay + Continuous State)
    # -------------------------------------------------------------
    elif task_id == "D12_Hybrid_Memory":
        meta["support_regimes"].append({
            "start": 0, "end": total_steps, "support": [(0, 8)], "coeffs": [0.6], "recurrent_state": True
        })
        s = 0.0
        for t in range(8, total_steps):
            pulse_s = 1.0 if X[t, 1] > 1.8 else 0.0
            pulse_r = 1.0 if X[t, 2] > 1.8 else 0.0
            if pulse_s: s = 1.0
            elif pulse_r: s = -1.0
            y[t] = 0.6 * X[t - 8, 0] + 0.6 * s + noise[t]

    return X, y, meta

ALL_TASKS_D = [
    "D1_Single_Static_Delay",
    "D2_Multi_Tap_Sparse_Delay",
    "D3_Widely_Separated_Support",
    "D4_Abrupt_Support_Relocation",
    "D5_Tap_Birth",
    "D6_Tap_Death",
    "D7_Quiescent_Tap",
    "D8_Amplitude_Drift",
    "D9_Memoryless_Negative_Control",
    "D10_Dense_FIR_Control",
    "D11_Continuous_State_Control",
    "D12_Hybrid_Memory"
]
