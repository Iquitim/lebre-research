"""
Benchmark Stream Generator Suite for Bounded-History Lag Discovery Integration
Task ID: BOUNDED-HISTORY-LAG-INTEGRATION-01
Defines streams BH1 to BH12 across Regime A (High-Entropy IID) and Regime B (Compressible).
Exports BOUNDED_HISTORY_01_HIDDEN_SUPPORT_MANIFEST.csv.
"""

import os
import csv
import numpy as np
from typing import Dict, List, Tuple, Any

def generate_stream(
    task_id: str,
    seed: int,
    T: int = 20000,
    D: int = 5,
    L_max: int = 32,
    sigma_v: float = 0.1  # noise var = 0.01 -> SNR ~20dB
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Generates input matrix X (T, D) and target vector y (T) along with ground truth metadata.
    """
    rng = np.random.RandomState(seed)
    metadata: Dict[str, Any] = {
        "task_id": task_id,
        "seed": seed,
        "T": T,
        "D": D,
        "L_max": L_max,
        "sigma_v": sigma_v,
        "noise_var": sigma_v ** 2,
    }

    if task_id == "BH1":
        # Regime A: Single Discrete Lag
        metadata["regime"] = "Regime A"
        metadata["description"] = "Single discrete lag on high-entropy white noise"
        metadata["active_taps"] = [(1, 12, 0.85)]  # (channel, lag, weight)
        X = rng.randn(T, D).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(12, T):
            y[t] = 0.85 * X[t - 12, 1]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH2":
        # Regime A: Multi-Tap Dispersed
        metadata["regime"] = "Regime A"
        metadata["description"] = "Three dispersed discrete taps across channels"
        metadata["active_taps"] = [(0, 4, 0.70), (2, 11, -0.60), (3, 25, 0.50)]
        X = rng.randn(T, D).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(25, T):
            y[t] = (0.70 * X[t - 4, 0]
                    - 0.60 * X[t - 11, 2]
                    + 0.50 * X[t - 25, 3])
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH3":
        # Regime A: Widely Separated Taps
        metadata["regime"] = "Regime A"
        metadata["description"] = "Widely separated boundary taps (tau=2, tau=30)"
        metadata["active_taps"] = [(1, 2, 0.65), (4, 30, -0.65)]
        X = rng.randn(T, D).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(30, T):
            y[t] = 0.65 * X[t - 2, 1] - 0.65 * X[t - 30, 4]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH4":
        # Regime A: Relocating Dynamic Lag
        metadata["regime"] = "Regime A"
        metadata["description"] = "Dynamic lag relocation from tau=8 to tau=22 at t=10000"
        metadata["active_taps_phase1"] = [(2, 8, 0.80)]
        metadata["active_taps_phase2"] = [(2, 22, 0.80)]
        metadata["active_taps"] = [(2, 22, 0.80)]  # final support
        metadata["switch_step"] = 10000
        X = rng.randn(T, D).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(T):
            if t < 10000:
                if t >= 8:
                    y[t] = 0.80 * X[t - 8, 2]
            else:
                if t >= 22:
                    y[t] = 0.80 * X[t - 22, 2]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH5":
        # Regime B: Smooth AR(1) Low-Pass
        metadata["regime"] = "Regime B"
        metadata["description"] = "Smooth AR(1) low-pass correlated input (alpha=0.92)"
        metadata["active_taps"] = [(1, 14, 0.80)]
        alpha = 0.92
        scale = np.sqrt(1.0 - alpha ** 2)
        innov = rng.randn(T + 200, D).astype(np.float32)
        X_full = np.zeros((T + 200, D), dtype=np.float32)
        for t in range(1, T + 200):
            X_full[t] = alpha * X_full[t - 1] + scale * innov[t]
        X = X_full[200:]
        y = np.zeros(T, dtype=np.float32)
        for t in range(14, T):
            y[t] = 0.80 * X[t - 14, 1]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH6":
        # Regime B: Bandlimited Multi-Tap
        metadata["regime"] = "Regime B"
        metadata["description"] = "Bandlimited input filtered through low-pass IIR with 3 taps"
        metadata["active_taps"] = [(0, 5, 0.60), (2, 12, -0.50), (4, 19, 0.45)]
        # 2nd order Butterworth low-pass simulation (fc ~ 0.15)
        # Difference equation: x_t = b0*e_t + b1*e_{t-1} + b2*e_{t-2} - a1*x_{t-1} - a2*x_{t-2}
        b = np.array([0.067455, 0.134911, 0.067455], dtype=np.float32)
        a = np.array([1.0, -1.14298, 0.41280], dtype=np.float32)
        innov = rng.randn(T + 200, D).astype(np.float32)
        X_full = np.zeros((T + 200, D), dtype=np.float32)
        for t in range(2, T + 200):
            X_full[t] = (b[0] * innov[t] + b[1] * innov[t - 1] + b[2] * innov[t - 2]
                         - a[1] * X_full[t - 1] - a[2] * X_full[t - 2])
        # Standardize variance
        std_dev = np.std(X_full[200:], axis=0, keepdims=True)
        std_dev[std_dev < 1e-4] = 1.0
        X = (X_full[200:] / std_dev).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(19, T):
            y[t] = (0.60 * X[t - 5, 0]
                    - 0.50 * X[t - 12, 2]
                    + 0.45 * X[t - 19, 4])
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH7":
        # Regime B: Correlated Long Delay
        metadata["regime"] = "Regime B"
        metadata["description"] = "Gaussian-kernel correlated input with long delay tau=28"
        metadata["active_taps"] = [(3, 28, 0.80)]
        # FIR Gaussian filter
        k_indices = np.arange(-10, 11)
        h = np.exp(-k_indices ** 2 / 18.0)
        h = (h / np.sqrt(np.sum(h ** 2))).astype(np.float32)
        innov = rng.randn(T + 50, D).astype(np.float32)
        X_full = np.zeros((T + 50, D), dtype=np.float32)
        for d in range(D):
            X_full[:, d] = np.convolve(innov[:, d], h, mode='same')
        X = X_full[50:].astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        for t in range(28, T):
            y[t] = 0.80 * X[t - 28, 3]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH8":
        # Regime A: Dynamic Range Stress
        metadata["regime"] = "Regime A"
        metadata["description"] = "Dynamic range stress with intermittent 25x amplitude bursts"
        metadata["active_taps"] = [(1, 10, 0.75)]
        X = rng.randn(T, D).astype(np.float32)
        # Insert intermittent burst scaling
        burst_mask = rng.rand(T) < 0.005
        burst_indices = np.where(burst_mask)[0]
        for idx in burst_indices:
            end_idx = min(T, idx + 8)
            X[idx:end_idx] *= 25.0
        X = np.clip(X, -80.0, 80.0)
        y = np.zeros(T, dtype=np.float32)
        for t in range(10, T):
            y[t] = 0.75 * X[t - 10, 1]
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH9":
        # Regime A: Memoryless Control
        metadata["regime"] = "Regime A"
        metadata["description"] = "Memoryless control system (tau=0 only, ground truth history empty)"
        metadata["active_taps"] = []  # No history taps (only contemporaneous)
        metadata["contemporaneous_taps"] = [(0, 0, 0.80), (2, 0, -0.60)]
        X = rng.randn(T, D).astype(np.float32)
        y = (0.80 * X[:, 0] - 0.60 * X[:, 2] + rng.randn(T).astype(np.float32) * sigma_v)

    elif task_id == "BH10":
        # Regime A: Quiescent Delay Stability
        metadata["regime"] = "Regime A"
        metadata["description"] = "Zero-gradient silence period t in [8000, 12000], tau=15"
        metadata["active_taps"] = [(2, 15, 0.85)]
        metadata["silence_start"] = 8000
        metadata["silence_end"] = 12000
        X = rng.randn(T, D).astype(np.float32)
        X[8000:12000] = 0.0
        y = np.zeros(T, dtype=np.float32)
        for t in range(15, T):
            y[t] = 0.85 * X[t - 15, 2]
        # Noise remains during silence
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH11":
        # Regime B: Continuous-State Recurrence
        metadata["regime"] = "Regime B"
        metadata["description"] = "Continuous linear state-space system sampled at dt=0.05"
        metadata["active_taps"] = []  # Continuous distributed memory
        metadata["continuous_order"] = 4
        # Stable state-space system: h_{t+1} = A h_t + B x_t, y_t = C h_t
        A_block1 = np.array([[0.95 * np.cos(0.2), -0.95 * np.sin(0.2)],
                             [0.95 * np.sin(0.2),  0.95 * np.cos(0.2)]], dtype=np.float32)
        A_block2 = np.array([[0.90 * np.cos(0.4), -0.90 * np.sin(0.4)],
                             [0.90 * np.sin(0.4),  0.90 * np.cos(0.4)]], dtype=np.float32)
        A = np.zeros((4, 4), dtype=np.float32)
        A[0:2, 0:2] = A_block1
        A[2:4, 2:4] = A_block2
        B = np.array([[0.5, 0.0, 0.0, 0.0, 0.0],
                      [0.0, 0.5, 0.0, 0.0, 0.0],
                      [0.0, 0.0, 0.5, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.5, 0.0]], dtype=np.float32)
        C = np.array([0.4, -0.3, 0.3, -0.2], dtype=np.float32)
        X = rng.randn(T, D).astype(np.float32)
        y = np.zeros(T, dtype=np.float32)
        h = np.zeros(4, dtype=np.float32)
        for t in range(T):
            h = A @ h + B @ X[t]
            y[t] = np.dot(C, h)
        y += rng.randn(T).astype(np.float32) * sigma_v

    elif task_id == "BH12":
        # Regime B: Hybrid Discrete + Continuous
        metadata["regime"] = "Regime B"
        metadata["description"] = "Hybrid sparse discrete tap (tau=7) + continuous AR(2) tail"
        metadata["active_taps"] = [(1, 7, 0.60)]
        metadata["continuous_tail"] = "AR(2) r=0.92, theta=0.3 on channel 3"
        X = rng.randn(T, D).astype(np.float32)
        y_discrete = np.zeros(T, dtype=np.float32)
        for t in range(7, T):
            y_discrete[t] = 0.60 * X[t - 7, 1]
        # AR(2) resonant tail
        r = 0.92
        theta = 0.3
        a1 = -2.0 * r * np.cos(theta)
        a2 = r ** 2
        y_cont = np.zeros(T, dtype=np.float32)
        for t in range(2, T):
            y_cont[t] = 0.50 * X[t, 3] - a1 * y_cont[t - 1] - a2 * y_cont[t - 2]
        # Standardize continuous contribution
        y_cont = 0.40 * (y_cont / (np.std(y_cont) + 1e-6))
        y = y_discrete + y_cont + rng.randn(T).astype(np.float32) * sigma_v

    else:
        raise ValueError(f"Unknown task_id: {task_id}")

    return X, y, metadata

def export_hidden_support_manifest(output_path: str):
    """
    Exports the ground truth hidden support manifest for all tasks BH1 to BH12.
    """
    tasks = ["BH1", "BH2", "BH3", "BH4", "BH5", "BH6", "BH7", "BH8", "BH9", "BH10", "BH11", "BH12"]
    rows = []
    for task_id in tasks:
        _, _, meta = generate_stream(task_id, seed=1101, T=100)
        active_taps_str = "; ".join([f"(d={t[0]},tau={t[1]},w={t[2]:.2f})" for t in meta.get("active_taps", [])])
        if not active_taps_str:
            active_taps_str = "None (Memoryless / Continuous)"
        rows.append({
            "task_id": task_id,
            "regime": meta["regime"],
            "description": meta["description"],
            "D": meta["D"],
            "L_max": meta["L_max"],
            "active_taps": active_taps_str,
            "temporal_dynamics": "Switching" if "switch_step" in meta else ("Quiescent" if "silence_start" in meta else "Stationary"),
            "noise_variance": meta["noise_var"]
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["task_id", "regime", "description", "D", "L_max", "active_taps", "temporal_dynamics", "noise_variance"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Exported hidden support manifest to {output_path} ({len(rows)} tasks).")

if __name__ == "__main__":
    out_csv = os.path.join("experiments", "BOUNDED-HISTORY-LAG-INTEGRATION-01", "BOUNDED_HISTORY_01_HIDDEN_SUPPORT_MANIFEST.csv")
    export_hidden_support_manifest(out_csv)
