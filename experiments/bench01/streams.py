"""
Stream Generators and Data Loaders for BENCH-01:
Block A: Mechanistic Diagnostic Tasks (A1-A8)
Mechanistic Holdouts: (H1-H2)
Block B: Public Real-World Continuous Streams (B1-B5)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List, Generator
from pathlib import Path

class CausalStandardScaler:
    """
    Online recursive Welford / exponential running standardizer.
    Normalization statistics are computed strictly from step 0 to t-1.
    Statistics update strictly AFTER prediction.
    """
    def __init__(self, d: int, alpha: float = 1e-4, eps: float = 1e-6):
        self.d = d
        self.alpha = float(alpha)
        self.eps = float(eps)
        self.mean = np.zeros(d, dtype=np.float64)
        self.var = np.ones(d, dtype=np.float64)
        self.t = 0

    def transform(self, x: np.ndarray) -> np.ndarray:
        # Use strictly past statistics
        std = np.sqrt(self.var + self.eps)
        return (x - self.mean) / std

    def update(self, x: np.ndarray) -> None:
        self.t += 1
        # Exponential moving average of mean and variance
        delta = x - self.mean
        self.mean += self.alpha * delta
        self.var = (1.0 - self.alpha) * self.var + self.alpha * (x - self.mean) * delta
        self.var = np.maximum(self.var, 1e-4)


# =========================================================================
# BLOCK A GENERATORS (A1-A8, H1-H2)
# =========================================================================

def generate_A1_sparse_shift(seed: int = 101, total_steps: int = 10000,
                             d_features: int = 50, k: int = 3, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A1: Sparse Support Shift (Shift at t=5000)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    
    # Regime 1 (t < 5000): features 0, 1, 2
    w1 = np.array([1.0, -1.2, 0.8])
    # Regime 2 (t >= 5000): features 10, 20, 30
    w2 = np.array([-1.5, 1.0, 1.2])
    
    noise = rng.randn(total_steps) * noise_std
    y[:5000] = np.dot(X[:5000, :3], w1) + noise[:5000]
    y[5000:] = np.dot(X[5000:, [10, 20, 30]], w2) + noise[5000:]
    return X, y


def generate_A2_single_delay(seed: int = 101, total_steps: int = 10000,
                             d_features: int = 20, delay: int = 4, coeff: float = 0.8,
                             noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A2: Single Delayed Dependency (y_t = coeff * x_{1, t-delay} + eps)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    for t in range(delay, total_steps):
        y[t] = coeff * X[t - delay, 0] + noise[t]
    return X, y


def generate_A3_multiple_delays(seed: int = 101, total_steps: int = 10000,
                                d_features: int = 20, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A3: Multiple Dispersed Delays (y_t = 0.5 * x_{1, t-2} + 0.5 * x_{2, t-8} + eps)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    for t in range(8, total_steps):
        y[t] = 0.5 * X[t - 2, 0] + 0.5 * X[t - 8, 1] + noise[t]
    return X, y


def generate_A4_long_delay(seed: int = 101, total_steps: int = 10000,
                           d_features: int = 20, delay: int = 30, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A4: Long-Delay Scaling (delay = 30 default)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    for t in range(delay, total_steps):
        y[t] = 0.8 * X[t - delay, 0] + noise[t]
    return X, y


def generate_A5_set_reset(seed: int = 101, total_steps: int = 10000,
                          d_features: int = 10, p_event: float = 0.01,
                          noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A5: SET/RESET Quiescent Memory (Poisson pulses toggle bistable memory latch)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features) * 0.1
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    state = 0.0
    for t in range(total_steps):
        # Set pulse on channel 0, Reset pulse on channel 1
        if rng.rand() < p_event:
            if rng.rand() < 0.5:
                X[t, 0] = 2.0
                state = 1.0
            else:
                X[t, 1] = 2.0
                state = -1.0
        y[t] = state + noise[t]
    return X, y


def generate_A6_context_routing(seed: int = 101, total_steps: int = 10000,
                                d_features: int = 10, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A6: Context Routing (Feature 0 switches static feedforward vs AR path)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    ar_state = 0.0
    for t in range(1, total_steps):
        ar_state = 0.85 * ar_state + 0.1 * X[t - 1, 1]
        context = 1.0 if X[t, 0] > 0 else 0.0
        if context == 1.0:
            y[t] = 1.2 * X[t, 2] + noise[t]
        else:
            y[t] = ar_state + noise[t]
    return X, y


def generate_A7_quiescent_retention(seed: int = 101, total_steps: int = 10000,
                                    d_features: int = 10, lambda_gap: int = 150,
                                    noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A7: Extended Poisson Quiescence (Cues separated by Poisson(150) idle intervals)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features) * 0.1
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    stored_val = 0.0
    t = 0
    while t < total_steps:
        gap = max(10, rng.poisson(lambda_gap))
        val = rng.randn()
        X[t, 0] = val # Cue
        stored_val = val
        
        end_t = min(t + gap, total_steps)
        for step in range(t, end_t):
            y[step] = stored_val + noise[step]
        t = end_t
    return X, y


def generate_A8_tri_regime(seed: int = 101, total_steps: int = 10000,
                           d_features: int = 10, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """A8: Abrupt Tri-Regime Transition: Linear (0..3333) -> Lag (3333..6666) -> Recurrent (6666..10000)"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    # Regime 1: Linear
    y[:3333] = 1.0 * X[:3333, 0] - 0.8 * X[:3333, 1] + noise[:3333]
    
    # Regime 2: Lag
    for t in range(3333, 6666):
        y[t] = 0.8 * X[t - 5, 2] + noise[t]
        
    # Regime 3: Recurrent
    s = 0.0
    for t in range(6666, total_steps):
        s = 0.9 * s + 0.2 * X[t - 1, 3]
        y[t] = s + noise[t]
    return X, y


def generate_H1_damped_resonator(seed: int = 101, total_steps: int = 10000,
                                 d_features: int = 50, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """H1: Damped Harmonic Resonator with drifting frequency and damping"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    s1, s2 = 0.0, 0.0
    for t in range(total_steps):
        # Drifting frequency and damping
        omega = 0.2618 + 0.5236 * (0.5 + 0.5 * np.sin(2.0 * np.pi * t / 2500.0))
        r = 0.85 + 0.13 * (0.5 + 0.5 * np.cos(2.0 * np.pi * t / 3500.0))
        
        u = X[t, 0]
        s1_next = 2.0 * r * np.cos(omega) * s1 - (r ** 2) * s2 + u
        s2 = s1
        s1 = s1_next
        y[t] = s1 + noise[t]
    return X, y


def generate_H2_switching_volterra(seed: int = 101, total_steps: int = 10000,
                                   d_features: int = 40, noise_std: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """H2: Switching Delayed Volterra Stream"""
    rng = np.random.RandomState(seed)
    X = rng.randn(total_steps, d_features)
    y = np.zeros(total_steps, dtype=np.float64)
    noise = rng.randn(total_steps) * noise_std
    
    s = 0.0
    for t in range(7, total_steps):
        s = 0.92 * s + X[t - 1, 3]
        switch_val = X[t, 0]
        if switch_val > 0.0:
            y[t] = 0.6 * (X[t - 3, 1] ** 2) + 0.4 * X[t - 7, 2] + noise[t]
        else:
            y[t] = 0.8 * s + 0.2 * X[t, 3] + noise[t]
    return X, y


# =========================================================================
# BLOCK B LOADERS (REAL WORLD)
# =========================================================================

def load_B1_elec(file_path: str = "data/external/elec2_nsw_continuous.csv") -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path)
    # Covariates: period, nswdemand, vicprice, vicdemand, transfer
    feature_cols = ['period', 'nswdemand', 'vicprice', 'vicdemand', 'transfer']
    target_col = 'nswprice'
    X = df[feature_cols].values.astype(np.float64)
    y = df[target_col].values.astype(np.float64)
    return X, y


def load_B2_jena(file_path: str = "data/external/jena_climate_2014_2016.csv") -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path)
    target_col = 'T (degC)'
    feature_cols = [c for c in df.columns if c not in ['Date Time', target_col]]
    X = df[feature_cols].values.astype(np.float64)
    y = df[target_col].values.astype(np.float64)
    return X, y


def load_B3_gas(file_path: str = "data/external/gas_dynamic_mixture_co.csv") -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path)
    target_col = 'CO_ppm'
    feature_cols = [c for c in df.columns if 'sensor' in c]
    X = df[feature_cols].values.astype(np.float64)
    y = df[target_col].values.astype(np.float64)
    return X, y


def load_B4_silverbox(file_path: str = "data/external/silverbox_eval_sn.csv") -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path)
    # Single input V_in, target V_out
    X = df[['V_in']].values.astype(np.float64)
    y = df['V_out'].values.astype(np.float64)
    return X, y


def load_B5_household(file_path: str = "data/external/household_power_submetering.csv") -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(file_path)
    target_col = 'Global_active_power'
    feature_cols = ['Global_reactive_power', 'Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
    X = df[feature_cols].values.astype(np.float64)
    y = df[target_col].values.astype(np.float64)
    return X, y


def get_stream(task_id: str, seed: int = 101) -> Tuple[np.ndarray, np.ndarray]:
    """Dispatch helper returning raw (X, y) for any benchmark task."""
    if task_id == "A1_Sparse_Support_Shift":
        return generate_A1_sparse_shift(seed=seed)
    elif task_id == "A2_Single_Delayed_Dependency":
        return generate_A2_single_delay(seed=seed)
    elif task_id == "A3_Multiple_Dispersed_Delays":
        return generate_A3_multiple_delays(seed=seed)
    elif task_id == "A4_Long_Delay_Scaling":
        return generate_A4_long_delay(seed=seed)
    elif task_id == "A5_Set_Reset_Quiescent_Memory":
        return generate_A5_set_reset(seed=seed)
    elif task_id == "A6_Context_Routing":
        return generate_A6_context_routing(seed=seed)
    elif task_id == "A7_Extended_Poisson_Quiescence":
        return generate_A7_quiescent_retention(seed=seed)
    elif task_id == "A8_Abrupt_Tri_Regime_Transition":
        return generate_A8_tri_regime(seed=seed)
    elif task_id == "H1_Damped_Harmonic_Resonator":
        return generate_H1_damped_resonator(seed=seed)
    elif task_id == "H2_Switching_Delayed_Volterra":
        return generate_H2_switching_volterra(seed=seed)
    elif "B1" in task_id or "Electricity" in task_id:
        return load_B1_elec()
    elif "B2" in task_id or "Jena" in task_id:
        return load_B2_jena()
    elif "B3" in task_id or "Gas" in task_id:
        return load_B3_gas()
    elif "B4" in task_id or "Silverbox" in task_id:
        return load_B4_silverbox()
    elif "B5" in task_id or "Household" in task_id:
        return load_B5_household()
    else:
        raise ValueError(f"Unknown task_id: {task_id}")
