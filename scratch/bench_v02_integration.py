#!/usr/bin/env python3
"""
bench_v02_integration.py: Causal Benchmark Stream Generators (I1-I14)
for LEBRE-V0.2-INTEGRATION-DESIGN-01.

Every benchmark provides exact mathematical ground truth for evaluation diagnostics,
with zero target leakage or metadata cues available to the learning algorithms.
"""

import numpy as np
from typing import Dict, Any, Tuple, List

BENCHMARK_TASKS = [
    "I1_Memoryless_Linear",
    "I2_Static_Nonlinear_Negative_Control",
    "I3_Single_Exact_Delay",
    "I4_Multi_Sparse_Delay",
    "I5_Moving_Delay_Support",
    "I6_Continuous_Latent_State",
    "I7_Quiescent_Continuous_State",
    "I8_Quiescent_Discrete_Delay",
    "I9_Hybrid_Delay_Plus_Latent_State",
    "I10_Redundant_Temporal_Structure",
    "I11_Regime_Switch_Delay_To_Latent",
    "I12_Regime_Switch_Latent_To_Delay",
    "I13_Regime_Switch_Hybrid_To_Memoryless",
    "I14_Intermittent_Hybrid"
]

def generate_v02_stream(
    task_id: str,
    seed: int,
    total_steps: int = 6000,
    d_features: int = 5
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Generates prequential input-target streaming pair and ground truth metadata.
    
    Returns:
      X: (total_steps, d_features) float64 array
      y: (total_steps,) float64 array
      meta: dictionary describing true structural class and regime timeline
    """
    rng = np.random.RandomState(seed)
    
    # Base input signal: Gaussian white innovations
    X = rng.normal(0.0, 1.0, size=(total_steps, d_features))
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.normal(0.0, 0.4, size=total_steps) # sigma = 0.4 (var = 0.16)
    
    # Common instantaneous linear weights
    w_base = np.array([0.8, -0.6, 0.4, -0.3, 0.2][:d_features], dtype=np.float64)
    if len(w_base) < d_features:
        w_base = np.pad(w_base, (0, d_features - len(w_base)), constant_values=0.1)
        
    meta = {
        "task_id": task_id,
        "seed": seed,
        "total_steps": total_steps,
        "d_features": d_features,
        "expected_class": "NONE",
        "regimes": []
    }
    
    # -------------------------------------------------------------------------
    # I1: Memoryless Linear (Negative Temporal Control)
    # -------------------------------------------------------------------------
    if task_id == "I1_Memoryless_Linear":
        meta["expected_class"] = "NONE"
        meta["regimes"].append({"start": 0, "end": total_steps, "class": "NONE"})
        for t in range(total_steps):
            y[t] = np.dot(w_base, X[t]) + noise[t]

    # -------------------------------------------------------------------------
    # I2: Static Nonlinear Negative Control (Mandatory Safety Check)
    # -------------------------------------------------------------------------
    elif task_id == "I2_Static_Nonlinear_Negative_Control":
        meta["expected_class"] = "NONE"
        meta["regimes"].append({"start": 0, "end": total_steps, "class": "NONE"})
        for t in range(total_steps):
            u_t = float(np.dot(w_base, X[t]))
            # Pure instantaneous nonlinearity: cubic polynomial
            y[t] = u_t + 0.35 * (u_t ** 2) - 0.15 * (u_t ** 3) + noise[t]

    # -------------------------------------------------------------------------
    # I3: Single Exact Delay (Discrete Transport Baseline)
    # -------------------------------------------------------------------------
    elif task_id == "I3_Single_Exact_Delay":
        meta["expected_class"] = "LAG"
        k_lag = 6
        i_feat = 1 % d_features
        meta["regimes"].append({
            "start": 0, "end": total_steps, "class": "LAG", "lags": [(i_feat, k_lag)]
        })
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            y_del = 0.85 * X[t - k_lag, i_feat] if t >= k_lag else 0.0
            y[t] = y_lin + y_del + noise[t]

    # -------------------------------------------------------------------------
    # I4: Multi Sparse Delay (Non-Contiguous Transport)
    # -------------------------------------------------------------------------
    elif task_id == "I4_Multi_Sparse_Delay":
        meta["expected_class"] = "LAG"
        taps = [(0 % d_features, 3, 0.75), (2 % d_features, 14, -0.60), (4 % d_features, 27, 0.80)]
        meta["regimes"].append({
            "start": 0, "end": total_steps, "class": "LAG", "lags": [(i, k) for i, k, _ in taps]
        })
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            y_del = sum(w * X[t - k, i] for i, k, w in taps if t >= k)
            y[t] = y_lin + y_del + noise[t]

    # -------------------------------------------------------------------------
    # I5: Moving Delay Support (Abrupt Support Relocation)
    # -------------------------------------------------------------------------
    elif task_id == "I5_Moving_Delay_Support":
        meta["expected_class"] = "LAG"
        split_t = total_steps // 2 # 3000
        meta["regimes"].append({"start": 0, "end": split_t, "class": "LAG", "lags": [(1 % d_features, 4)]})
        meta["regimes"].append({"start": split_t, "end": total_steps, "class": "LAG", "lags": [(3 % d_features, 18)]})
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            if t < split_t:
                y_del = 0.85 * X[t - 4, 1 % d_features] if t >= 4 else 0.0
            else:
                y_del = 0.85 * X[t - 18, 3 % d_features] if t >= 18 else 0.0
            y[t] = y_lin + y_del + noise[t]

    # -------------------------------------------------------------------------
    # I6: Continuous Latent State (Linear State-Space)
    # -------------------------------------------------------------------------
    elif task_id == "I6_Continuous_Latent_State":
        meta["expected_class"] = "RECURRENT"
        meta["regimes"].append({"start": 0, "end": total_steps, "class": "RECURRENT"})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            z_t = 0.88 * z_t + 0.40 * X[t, 0] + nu[t]
            y[t] = np.dot(w_base, X[t]) + 0.90 * z_t + noise[t]

    # -------------------------------------------------------------------------
    # I7: Quiescent Continuous State (Recurrent Silence Test)
    # -------------------------------------------------------------------------
    elif task_id == "I7_Quiescent_Continuous_State":
        meta["expected_class"] = "RECURRENT"
        q_start, q_end = 2000, 4000
        meta["regimes"].append({"start": 0, "end": q_start, "class": "RECURRENT"})
        meta["regimes"].append({"start": q_start, "end": q_end, "class": "QUIESCENT"})
        meta["regimes"].append({"start": q_end, "end": total_steps, "class": "RECURRENT"})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            if q_start <= t < q_end:
                X[t] = 0.0 # silence
            z_t = 0.88 * z_t + 0.40 * X[t, 0] + (0.0 if q_start <= t < q_end else nu[t])
            y[t] = np.dot(w_base, X[t]) + 0.90 * z_t + (noise[t] * 0.1 if q_start <= t < q_end else noise[t])

    # -------------------------------------------------------------------------
    # I8: Quiescent Discrete Delay (Lag Silence Test)
    # -------------------------------------------------------------------------
    elif task_id == "I8_Quiescent_Discrete_Delay":
        meta["expected_class"] = "LAG"
        k_lag = 6
        i_feat = 1 % d_features
        q_start, q_end = 2000, 4000
        meta["regimes"].append({"start": 0, "end": q_start, "class": "LAG", "lags": [(i_feat, k_lag)]})
        meta["regimes"].append({"start": q_start, "end": q_end, "class": "QUIESCENT"})
        meta["regimes"].append({"start": q_end, "end": total_steps, "class": "LAG", "lags": [(i_feat, k_lag)]})
        for t in range(total_steps):
            if q_start <= t < q_end:
                X[t] = 0.0
            y_lin = np.dot(w_base, X[t])
            y_del = 0.85 * X[t - k_lag, i_feat] if t >= k_lag else 0.0
            y[t] = y_lin + y_del + (noise[t] * 0.1 if q_start <= t < q_end else noise[t])

    # -------------------------------------------------------------------------
    # I9: Hybrid Delay Plus Latent State (Mandatory Composite Complementarity)
    # -------------------------------------------------------------------------
    elif task_id == "I9_Hybrid_Delay_Plus_Latent_State":
        meta["expected_class"] = "BOTH"
        k_lag = 12
        i_feat = 3 % d_features
        meta["regimes"].append({
            "start": 0, "end": total_steps, "class": "BOTH", "lags": [(i_feat, k_lag)]
        })
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            z_t = 0.85 * z_t + 0.35 * X[t, 0] + nu[t]
            y_lin = np.dot(w_base, X[t])
            y_del = 0.70 * X[t - k_lag, i_feat] if t >= k_lag else 0.0
            y[t] = y_lin + y_del + 0.80 * z_t + noise[t]

    # -------------------------------------------------------------------------
    # I10: Redundant Temporal Structure (Arbitration Stress Test)
    # -------------------------------------------------------------------------
    elif task_id == "I10_Redundant_Temporal_Structure":
        meta["expected_class"] = "REDUNDANT" # Either LAG or RECURRENT, but strictly not BOTH
        meta["regimes"].append({"start": 0, "end": total_steps, "class": "REDUNDANT"})
        y_prev = 0.0
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            # Autoregressive past target feedback + direct lagged input
            x_prev = X[t - 1, 0] if t >= 1 else 0.0
            y_t = y_lin + 0.70 * y_prev + 0.40 * x_prev + noise[t]
            y[t] = y_t
            y_prev = y_t * 0.8 # stabilized feedback

    # -------------------------------------------------------------------------
    # I11: Regime Switch Delay to Latent
    # -------------------------------------------------------------------------
    elif task_id == "I11_Regime_Switch_Delay_To_Latent":
        meta["expected_class"] = "SWITCH_DELAY_TO_LATENT"
        split_t = total_steps // 2 # 3000
        meta["regimes"].append({"start": 0, "end": split_t, "class": "LAG", "lags": [(1 % d_features, 8)]})
        meta["regimes"].append({"start": split_t, "end": total_steps, "class": "RECURRENT"})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            if t < split_t:
                y_del = 0.80 * X[t - 8, 1 % d_features] if t >= 8 else 0.0
                y[t] = y_lin + y_del + noise[t]
            else:
                z_t = 0.85 * z_t + 0.40 * X[t, 0] + nu[t]
                y[t] = y_lin + 0.90 * z_t + noise[t]

    # -------------------------------------------------------------------------
    # I12: Regime Switch Latent to Delay
    # -------------------------------------------------------------------------
    elif task_id == "I12_Regime_Switch_Latent_To_Delay":
        meta["expected_class"] = "SWITCH_LATENT_TO_DELAY"
        split_t = total_steps // 2 # 3000
        meta["regimes"].append({"start": 0, "end": split_t, "class": "RECURRENT"})
        meta["regimes"].append({"start": split_t, "end": total_steps, "class": "LAG", "lags": [(2 % d_features, 10)]})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            if t < split_t:
                z_t = 0.85 * z_t + 0.40 * X[t, 0] + nu[t]
                y[t] = y_lin + 0.90 * z_t + noise[t]
            else:
                y_del = 0.80 * X[t - 10, 2 % d_features] if t >= 10 else 0.0
                y[t] = y_lin + y_del + noise[t]

    # -------------------------------------------------------------------------
    # I13: Regime Switch Hybrid to Memoryless
    # -------------------------------------------------------------------------
    elif task_id == "I13_Regime_Switch_Hybrid_To_Memoryless":
        meta["expected_class"] = "SWITCH_HYBRID_TO_NONE"
        split_t = total_steps // 2 # 3000
        meta["regimes"].append({"start": 0, "end": split_t, "class": "BOTH", "lags": [(3 % d_features, 12)]})
        meta["regimes"].append({"start": split_t, "end": total_steps, "class": "NONE"})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            if t < split_t:
                z_t = 0.85 * z_t + 0.35 * X[t, 0] + nu[t]
                y_del = 0.70 * X[t - 12, 3 % d_features] if t >= 12 else 0.0
                y[t] = y_lin + y_del + 0.80 * z_t + noise[t]
            else:
                y[t] = y_lin + noise[t]

    # -------------------------------------------------------------------------
    # I14: Intermittent Hybrid (4-Phase Schedule)
    # -------------------------------------------------------------------------
    elif task_id == "I14_Intermittent_Hybrid":
        meta["expected_class"] = "INTERMITTENT"
        w_len = total_steps // 4 # 1500
        meta["regimes"].append({"start": 0, "end": w_len, "class": "LAG", "lags": [(0 % d_features, 5)]})
        meta["regimes"].append({"start": w_len, "end": 2 * w_len, "class": "RECURRENT"})
        meta["regimes"].append({"start": 2 * w_len, "end": 3 * w_len, "class": "BOTH", "lags": [(0 % d_features, 5)]})
        meta["regimes"].append({"start": 3 * w_len, "end": total_steps, "class": "NONE"})
        z_t = 0.0
        nu = rng.normal(0.0, 0.1, size=total_steps)
        for t in range(total_steps):
            y_lin = np.dot(w_base, X[t])
            if t < w_len:
                y_del = 0.75 * X[t - 5, 0] if t >= 5 else 0.0
                y[t] = y_lin + y_del + noise[t]
            elif t < 2 * w_len:
                z_t = 0.85 * z_t + 0.40 * X[t, 0] + nu[t]
                y[t] = y_lin + 0.85 * z_t + noise[t]
            elif t < 3 * w_len:
                z_t = 0.85 * z_t + 0.35 * X[t, 0] + nu[t]
                y_del = 0.70 * X[t - 5, 0] if t >= 5 else 0.0
                y[t] = y_lin + y_del + 0.75 * z_t + noise[t]
            else:
                y[t] = y_lin + noise[t]
                
    else:
        raise ValueError(f"Unknown task_id: {task_id}")
        
    return X, y, meta

if __name__ == "__main__":
    print("Self-testing benchmark stream generator across all 14 tasks...")
    for t_id in BENCHMARK_TASKS:
        X, y, meta = generate_v02_stream(t_id, seed=1301, total_steps=6000)
        assert X.shape == (6000, 5), f"Shape mismatch for {t_id}"
        assert len(y) == 6000, f"Length mismatch for {t_id}"
        print(f"  [OK] {t_id:38s} | y range: [{y.min():.2f}, {y.max():.2f}] | regimes: {len(meta['regimes'])}")
    print("All 14 benchmark tasks verified successfully!")
