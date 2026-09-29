#!/usr/bin/env python3
"""
CAPACITY-DECOMPOSITION-01: Causal Capacity Decomposition Simulation Engine.
Implements the 7-level experimental ladder:
  - Level 0: B0_LEBRE_FROZEN, B1_NO_REC_BIRTH, B2_FIXED_STRICT
  - Level 1: E0_NLMS, E1_RLS, E2_REG_RLS, E3_OLS_ORACLE, E4_RIDGE_ORACLE
  - Level 2: T0_LAG_0, T1_LAG_1, T2_LAG_2, T3_LAG_4, T4_LAG_8, T5_SPARSE_LAGS
  - Level 3: NL1_POLY2, NL2_RFF, NL3_MLP
  - Level 4: TNL1_LAG4_RFF
  - Level 5/6: REC_N1, REC_N2, REC_N4
  - Auxiliary: NORM1_FROZEN_WARMUP, NORM3_ORACLE, I1_SNAPSHOT_COMPARATOR

Workloads: A2, A3, A4 (Negative Controls), A5, A7 (Positive Controls), A8 (Transition)
Seeds: DEV 501..510 (N=10), EVAL 601..630 (N=30)
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

from experiments.bench01.streams import get_stream, CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper

EXP_DIR = ROOT / "experiments" / "CAPACITY-DECOMPOSITION-01"
FIG_DIR = EXP_DIR / "figures"
EXP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

TASKS_PRIMARY = [
    "A2_Single_Delayed_Dependency",
    "A3_Multiple_Dispersed_Delays",
    "A4_Long_Delay_Scaling"
]
TASKS_CONTROL = [
    "A5_Set_Reset_Quiescent_Memory",
    "A7_Extended_Poisson_Quiescence",
    "A8_Abrupt_Tri_Regime_Transition"
]
ALL_TASKS = TASKS_PRIMARY + TASKS_CONTROL

DEV_SEEDS = list(range(501, 511))
EVAL_SEEDS = list(range(601, 631))

# -------------------------------------------------------------
# Model Implementations
# -------------------------------------------------------------

class OnlineNLMS:
    def __init__(self, d: int, mu: float = 0.10, eps: float = 1e-4):
        self.d = d
        self.mu = mu
        self.eps = eps
        self.w = np.zeros(d, dtype=np.float64)
        
    def predict(self, x: np.ndarray) -> Tuple[float, float]:
        y_hat = float(np.dot(self.w, x))
        flops = 2 * self.d
        return y_hat, flops
        
    def update(self, x: np.ndarray, y: float, y_hat: float) -> float:
        e = y - y_hat
        norm_sq = float(np.dot(x, x))
        step = (self.mu / (self.eps + norm_sq)) * e
        self.w += step * x
        flops = 2 * self.d + 3
        return flops

class OnlineRLS:
    def __init__(self, d: int, lam: float = 0.999, delta: float = 100.0):
        self.d = d
        self.lam = lam
        self.w = np.zeros(d, dtype=np.float64)
        self.P = delta * np.eye(d, dtype=np.float64)
        
    def predict(self, x: np.ndarray) -> Tuple[float, float]:
        y_hat = float(np.dot(self.w, x))
        flops = 2 * self.d
        return y_hat, flops
        
    def update(self, x: np.ndarray, y: float, y_hat: float) -> float:
        e = y - y_hat
        Px = np.dot(self.P, x)
        denom = self.lam + float(np.dot(x, Px))
        k = Px / denom
        self.w += k * e
        self.P = (self.P - np.outer(k, Px)) / self.lam
        flops = 4 * (self.d ** 2) + 4 * self.d
        return flops

class OnlineRFF:
    def __init__(self, d_in: int, k_features: int = 50, gamma: float = 0.5, seed: int = 42):
        self.d_in = d_in
        self.k = k_features
        rng = np.random.RandomState(seed)
        self.Omega = rng.normal(0.0, np.sqrt(2 * gamma), size=(k_features, d_in))
        self.bias = rng.uniform(0.0, 2 * np.pi, size=k_features)
        self.nlms = OnlineNLMS(d=k_features, mu=0.10)
        
    def transform(self, x: np.ndarray) -> np.ndarray:
        proj = np.dot(self.Omega, x) + self.bias
        return np.sqrt(2.0 / self.k) * np.cos(proj)
        
    def predict(self, x: np.ndarray) -> Tuple[float, float]:
        phi = self.transform(x)
        y_hat, f_nlms = self.nlms.predict(phi)
        flops = 2 * self.d_in * self.k + 2 * self.k + f_nlms
        return y_hat, flops
        
    def update(self, x: np.ndarray, y: float, y_hat: float) -> float:
        phi = self.transform(x)
        flops = self.nlms.update(phi, y, y_hat)
        return flops

class OnlineRecurrentState:
    def __init__(self, d_in: int, n_states: int = 1, lr_w: float = 0.05, lr_lambda: float = 0.01):
        self.d_in = d_in
        self.n = n_states
        self.lr_w = lr_w
        self.lr_lam = lr_lambda
        
        self.s = np.zeros(n_states, dtype=np.float64)
        self.Lambda = 0.8 * np.eye(n_states, dtype=np.float64)
        self.U = np.zeros((n_states, d_in), dtype=np.float64)
        self.w_s = np.zeros(n_states, dtype=np.float64)
        self.sens_lam = np.zeros((n_states, n_states), dtype=np.float64)
        
    def step_state(self, x: np.ndarray) -> float:
        # s_t = tanh(Lambda s_{t-1} + U x_t)
        act = np.dot(self.Lambda, self.s) + np.dot(self.U, x)
        self.s_prev = self.s.copy()
        self.s = np.tanh(act)
        # Sensitivity p_t = (1 - s_t^2) * (s_{t-1} + Lambda * p_{t-1})
        d_act = 1.0 - self.s ** 2
        for i in range(self.n):
            self.sens_lam[i, i] = d_act[i] * (self.s_prev[i] + self.Lambda[i, i] * self.sens_lam[i, i])
        flops = 2 * (self.n ** 2) + 2 * self.n * self.d_in + 4 * self.n
        return flops
        
    def predict_recurrent(self) -> Tuple[float, float]:
        pred = float(np.dot(self.w_s, self.s))
        flops = 2 * self.n
        return pred, flops
        
    def update_recurrent(self, e: float) -> float:
        # Online RTRL-style gradient step
        grad_w = e * self.s
        self.w_s = np.clip(self.w_s + self.lr_w * grad_w, -5.0, 5.0)
        for i in range(self.n):
            grad_lam = e * self.w_s[i] * self.sens_lam[i, i]
            self.Lambda[i, i] = np.clip(self.Lambda[i, i] + self.lr_lam * grad_lam, -0.95, 0.95)
        flops = 6 * self.n
        return flops

# -------------------------------------------------------------
# Single Stream Runner
# -------------------------------------------------------------

def run_capacity_single_stream(
    task_id: str,
    seed: int,
    variant: str,
    phase: str = "EVAL",
    test_split: float = 0.30
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    X, y = get_stream(task_id, seed=seed)
    T = len(X)
    D = X.shape[1]
    test_start = int(test_split * T)
    test_var = float(np.var(y[test_start:])) + 1e-6
    
    # ---------------------------------------------------------
    # Execution for Level 0 References (Wrapper based)
    # ---------------------------------------------------------
    if variant in ["B0_LEBRE_FROZEN", "B1_NO_REC_BIRTH", "B2_FIXED_STRICT"]:
        wrapper = TrackBFrozenWrapper(d_features=D)
        learner = wrapper.learner
        scaler = CausalStandardScaler(d=D)
        
        if variant == "B1_NO_REC_BIRTH":
            learner._trigger_birth = lambda *args, **kwargs: None
        elif variant == "B2_FIXED_STRICT":
            learner.promote_threshold = 0.15
            
        losses = []
        flops_list = []
        residuals = []
        
        for t in range(T):
            x_raw = X[t]
            y_true = float(y[t])
            x_norm = scaler.transform(x_raw)
            pred, flops = wrapper.step(x_norm, y_true)
            scaler.update(x_raw)
            
            res = y_true - float(pred)
            if t >= test_start:
                losses.append(res ** 2)
                flops_list.append(flops)
                residuals.append(res)
                
        mse = float(np.mean(losses))
        nmse = mse / test_var
        
        summary = {
            "task_id": task_id, "seed": seed, "variant": variant, "phase": phase,
            "status": "SUCCESS", "mse": mse, "nmse": nmse,
            "mean_flops": float(np.mean(flops_list)), "peak_flops": float(np.max(flops_list)),
            "memory_bytes": wrapper.get_memory_bytes(),
            "param_count": wrapper.get_active_params(),
            "births_count": len(learner.birth_events),
            "promotions_count": len([e for e in learner.birth_events if e.get("promoted", False)])
        }
        res_diag = compute_residual_diagnostics(residuals, X[test_start:], task_id, seed, variant, phase)
        return summary, res_diag

    # ---------------------------------------------------------
    # Offline Ceilings (E3, E4)
    # ---------------------------------------------------------
    if variant in ["E3_OLS_ORACLE", "E4_RIDGE_ORACLE"]:
        scaler = CausalStandardScaler(d=D)
        X_norm = np.zeros_like(X)
        for t in range(T):
            X_norm[t] = scaler.transform(X[t])
            scaler.update(X[t])
        X_test = X_norm[test_start:]
        y_test = y[test_start:]
        
        if variant == "E3_OLS_ORACLE":
            w = np.linalg.pinv(X_test.T @ X_test + 1e-6 * np.eye(D)) @ (X_test.T @ y_test)
        else: # E4 Ridge
            w = np.linalg.pinv(X_test.T @ X_test + 1.0 * np.eye(D)) @ (X_test.T @ y_test)
            
        preds = X_test @ w
        residuals = (y_test - preds).tolist()
        mse = float(np.mean(np.array(residuals) ** 2))
        nmse = mse / test_var
        
        summary = {
            "task_id": task_id, "seed": seed, "variant": variant, "phase": phase,
            "status": "SUCCESS", "mse": mse, "nmse": nmse,
            "mean_flops": 2 * D, "peak_flops": 2 * D,
            "memory_bytes": D * 8, "param_count": D,
            "births_count": 0, "promotions_count": 0
        }
        res_diag = compute_residual_diagnostics(residuals, X[test_start:], task_id, seed, variant, phase)
        return summary, res_diag

    # ---------------------------------------------------------
    # Online Streaming Estimator, Lag, Nonlinear, and Recurrent Variants
    # ---------------------------------------------------------
    scaler = CausalStandardScaler(d=D)
    
    # Setup model and lag buffers
    lag_depth = 0
    sparse_lags = False
    if variant == "T1_LAG_1": lag_depth = 1
    elif variant == "T2_LAG_2": lag_depth = 2
    elif variant in ["T3_LAG_4", "TNL1_LAG4_RFF"]: lag_depth = 4
    elif variant == "T4_LAG_8": lag_depth = 8
    elif variant == "T5_SPARSE_LAGS": sparse_lags = True
    
    # Lag buffer: stores up to 35 steps of normalized x
    x_history = []
    
    # Instantiations
    if variant in ["E0_NLMS", "T0_LAG_0", "T1_LAG_1", "T2_LAG_2", "T3_LAG_4", "T4_LAG_8", "T5_SPARSE_LAGS"]:
        dim_in = D * (lag_depth + 1) if not sparse_lags else D + 3
        model = OnlineNLMS(d=dim_in)
    elif variant == "E1_RLS":
        model = OnlineRLS(d=D, lam=0.999, delta=100.0)
    elif variant == "E2_REG_RLS":
        model = OnlineRLS(d=D, lam=0.999, delta=1.0)
    elif variant == "NL1_POLY2":
        # Degree 2 polynomial on top 5 features (5 linear + 15 quadratic = 20)
        model = OnlineNLMS(d=20)
    elif variant == "NL2_RFF":
        model = OnlineRFF(d_in=D, k_features=50, seed=seed)
    elif variant == "NL3_MLP":
        # Shallow online MLP D -> 16 -> 1
        W1 = np.random.normal(0, 0.1, size=(16, D))
        b1 = np.zeros(16)
        W2 = np.random.normal(0, 0.1, size=16)
        lr_mlp = 0.02
    elif variant == "TNL1_LAG4_RFF":
        model = OnlineRFF(d_in=D * 5, k_features=50, seed=seed)
    elif variant in ["REC_N1", "REC_N2", "REC_N4"]:
        n_st = 1 if variant == "REC_N1" else (2 if variant == "REC_N2" else 4)
        base_linear = OnlineNLMS(d=D)
        rec_model = OnlineRecurrentState(d_in=D, n_states=n_st)
    elif variant in ["NORM1_FROZEN_WARMUP", "NORM3_ORACLE", "I1_SNAPSHOT_COMPARATOR"]:
        model = OnlineNLMS(d=D)
        
    # Oracle normalizer if NORM3
    if variant == "NORM3_ORACLE":
        oracle_mean = np.mean(X, axis=0)
        oracle_std = np.std(X, axis=0) + 1e-4

    losses = []
    flops_list = []
    residuals = []
    
    for t in range(T):
        x_raw = X[t]
        y_true = float(y[t])
        
        # Normalization
        if variant == "NORM3_ORACLE":
            x_norm = (x_raw - oracle_mean) / oracle_std
        elif variant == "NORM1_FROZEN_WARMUP":
            if t < 500:
                x_norm = scaler.transform(x_raw)
                scaler.update(x_raw)
            else:
                x_norm = scaler.transform(x_raw)
        else:
            x_norm = scaler.transform(x_raw)
            scaler.update(x_raw)
            
        x_history.append(x_norm)
        
        # Construct feature vector based on variant
        if lag_depth > 0:
            feat_list = [x_norm]
            for l in range(1, lag_depth + 1):
                idx = max(0, t - l)
                feat_list.append(x_history[idx])
            z_t = np.concatenate(feat_list)
        elif sparse_lags:
            z_t = np.concatenate([
                x_norm,
                np.array([
                    x_history[max(0, t - 4)][0],
                    x_history[max(0, t - 8)][1] if D > 1 else 0.0,
                    x_history[max(0, t - 30)][0]
                ])
            ])
        elif variant == "NL1_POLY2":
            top5 = x_norm[:5]
            quads = [top5[i] * top5[j] for i in range(5) for j in range(i, 5)]
            z_t = np.concatenate([top5, np.array(quads)])
        else:
            z_t = x_norm
            
        # Prediction and Update
        if variant in ["REC_N1", "REC_N2", "REC_N4"]:
            f_st = rec_model.step_state(x_norm)
            yh_base, f_b = base_linear.predict(x_norm)
            yh_rec, f_r = rec_model.predict_recurrent()
            y_hat = yh_base + yh_rec
            flops = f_st + f_b + f_r
            
            res = y_true - y_hat
            f_ub = base_linear.update(x_norm, y_true, yh_base)
            f_ur = rec_model.update_recurrent(res)
            flops += f_ub + f_ur
        elif variant == "NL3_MLP":
            # Forward pass
            h_act = np.dot(W1, z_t) + b1
            h = np.maximum(0.0, h_act)
            y_hat = float(np.dot(W2, h))
            res = y_true - y_hat
            # Backward pass
            e = res
            dW2 = e * h
            dh = e * W2 * (h_act > 0)
            dW1 = np.outer(dh, z_t)
            W2 += lr_mlp * dW2
            W1 += lr_mlp * dW1
            b1 += lr_mlp * dh
            flops = 2 * D * 16 + 2 * 16 + 4 * D * 16
        else:
            y_hat, f_pred = model.predict(z_t)
            res = y_true - y_hat
            f_up = model.update(z_t, y_true, y_hat)
            flops = f_pred + f_up

        if t >= test_start:
            losses.append(res ** 2)
            flops_list.append(flops)
            residuals.append(res)

    mse = float(np.mean(losses))
    nmse = mse / test_var
    
    # Compute resource accounting
    if variant == "E1_RLS" or variant == "E2_REG_RLS":
        mem = 8 * (D ** 2 + D) + 64
        params = D
    elif lag_depth > 0:
        dim_in = D * (lag_depth + 1)
        mem = 8 * dim_in + 32 * lag_depth
        params = dim_in
    elif sparse_lags:
        mem = 8 * (D + 3) + 35 * 8 * D
        params = D + 3
    elif variant == "NL2_RFF":
        mem = 8 * 50 + 50 * D * 4
        params = 50
    elif variant == "NL3_MLP":
        mem = 353 * 8
        params = 353
    elif variant in ["REC_N1", "REC_N2", "REC_N4"]:
        n_st = 1 if variant == "REC_N1" else (2 if variant == "REC_N2" else 4)
        params = D + 2 * n_st + (n_st ** 2) + n_st * D
        mem = params * 8 + 128
    else:
        mem = D * 8 + 32
        params = D

    summary = {
        "task_id": task_id, "seed": seed, "variant": variant, "phase": phase,
        "status": "SUCCESS", "mse": mse, "nmse": nmse,
        "mean_flops": float(np.mean(flops_list)), "peak_flops": float(np.max(flops_list)),
        "memory_bytes": mem, "param_count": params,
        "births_count": 0, "promotions_count": 0
    }
    res_diag = compute_residual_diagnostics(residuals, X[test_start:], task_id, seed, variant, phase)
    return summary, res_diag

def compute_residual_diagnostics(residuals, X_test, task_id, seed, variant, phase) -> Dict[str, Any]:
    res = np.array(residuals)
    mean_res = float(np.mean(res))
    var_res = float(np.var(res))
    
    # Autocorrelation Function (ACF) at lags 1, 2, 4, 8, 30
    def get_acf(k):
        if len(res) <= k: return 0.0
        c0 = np.var(res)
        if c0 < 1e-8: return 0.0
        ck = np.mean((res[:-k] - mean_res) * (res[k:] - mean_res))
        return float(ck / c0)
        
    acf_1 = get_acf(1)
    acf_2 = get_acf(2)
    acf_4 = get_acf(4)
    acf_8 = get_acf(8)
    acf_30 = get_acf(30)
    
    # Correlation with inputs
    D = X_test.shape[1]
    corr_x0 = float(np.corrcoef(res, X_test[:, 0])[0, 1]) if np.std(X_test[:, 0]) > 1e-4 else 0.0
    corr_x1_lag4 = float(np.corrcoef(res[4:], X_test[:-4, 0])[0, 1]) if len(res) > 4 and np.std(X_test[:-4, 0]) > 1e-4 else 0.0
    corr_x2_lag8 = float(np.corrcoef(res[8:], X_test[:-8, 1])[0, 1]) if len(res) > 8 and D > 1 and np.std(X_test[:-8, 1]) > 1e-4 else 0.0
    corr_x1_lag30 = float(np.corrcoef(res[30:], X_test[:-30, 0])[0, 1]) if len(res) > 30 and np.std(X_test[:-30, 0]) > 1e-4 else 0.0
    
    return {
        "task_id": task_id, "seed": seed, "variant": variant, "phase": phase,
        "mean_residual": mean_res, "var_residual": var_res,
        "acf_1": acf_1, "acf_2": acf_2, "acf_4": acf_4, "acf_8": acf_8, "acf_30": acf_30,
        "corr_x0": corr_x0, "corr_x1_lag4": corr_x1_lag4, "corr_x2_lag8": corr_x2_lag8, "corr_x1_lag30": corr_x1_lag30
    }

def main():
    print("Starting CAPACITY-DECOMPOSITION-01 Execution Engine...")
    
    variants_all = [
        "B0_LEBRE_FROZEN", "B1_NO_REC_BIRTH", "B2_FIXED_STRICT",
        "E0_NLMS", "E1_RLS", "E2_REG_RLS", "E3_OLS_ORACLE", "E4_RIDGE_ORACLE",
        "T0_LAG_0", "T1_LAG_1", "T2_LAG_2", "T3_LAG_4", "T4_LAG_8", "T5_SPARSE_LAGS",
        "NL1_POLY2", "NL2_RFF", "NL3_MLP", "TNL1_LAG4_RFF",
        "REC_N1", "REC_N2", "REC_N4",
        "NORM1_FROZEN_WARMUP", "NORM3_ORACLE"
    ]
    
    # Phase 1: DEV runs (seeds 501..510)
    print(f"--- Phase 1: Development Verification (Seeds {DEV_SEEDS[0]}..{DEV_SEEDS[-1]}) ---")
    dev_args = [
        (task_id, seed, var, "DEV")
        for task_id in ALL_TASKS
        for seed in DEV_SEEDS
        for var in variants_all
    ]
    print(f"Total DEV runs: {len(dev_args)}")
    
    dev_summaries = []
    dev_residuals = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_capacity_single_stream, *arg): arg for arg in dev_args}
        done = 0
        for f in as_completed(futures):
            done += 1
            s, r = f.result()
            dev_summaries.append(s)
            dev_residuals.append(r)
            if done % 200 == 0 or done == len(dev_args):
                print(f"DEV progress: {done}/{len(dev_args)} completed")

    # Phase 2: EVAL runs (seeds 601..630)
    print(f"\n--- Phase 2: Confirmatory Evaluation (Seeds {EVAL_SEEDS[0]}..{EVAL_SEEDS[-1]}) ---")
    eval_args = [
        (task_id, seed, var, "EVAL")
        for task_id in ALL_TASKS
        for seed in EVAL_SEEDS
        for var in variants_all
    ]
    print(f"Total EVAL runs: {len(eval_args)}")
    
    eval_summaries = []
    eval_residuals = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_capacity_single_stream, *arg): arg for arg in eval_args}
        done = 0
        for f in as_completed(futures):
            done += 1
            s, r = f.result()
            eval_summaries.append(s)
            eval_residuals.append(r)
            if done % 500 == 0 or done == len(eval_args):
                print(f"EVAL progress: {done}/{len(eval_args)} completed")

    all_summaries = dev_summaries + eval_summaries
    all_residuals = dev_residuals + eval_residuals
    
    # Save CSVs
    pd.DataFrame(all_summaries)[[
        "task_id", "seed", "variant", "phase", "status"
    ]].to_csv(EXP_DIR / "CAPACITY_DECOMPOSITION_01_RUN_MANIFEST.csv", index=False)
    print(f"Wrote {EXP_DIR / 'CAPACITY_DECOMPOSITION_01_RUN_MANIFEST.csv'}")

    pd.DataFrame(all_summaries).to_csv(EXP_DIR / "CAPACITY_DECOMPOSITION_01_SEED_RESULTS.csv", index=False)
    print(f"Wrote {EXP_DIR / 'CAPACITY_DECOMPOSITION_01_SEED_RESULTS.csv'}")

    pd.DataFrame(all_residuals).to_csv(EXP_DIR / "CAPACITY_DECOMPOSITION_01_RESIDUAL_DIAGNOSTICS.csv", index=False)
    print(f"Wrote {EXP_DIR / 'CAPACITY_DECOMPOSITION_01_RESIDUAL_DIAGNOSTICS.csv'}")

if __name__ == "__main__":
    main()
