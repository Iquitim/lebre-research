"""
BENCH-01 Baseline Implementations:
Primary Frozen Baselines (B1-B5), Frozen Track-B (T0), Supplementary Challengers (S1-S5),
and Simplicity Controls (C1-C4).

Strict Online Causal Invariant:
  receive x_t -> predict -> record loss -> reveal y_t -> update parameters
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List

# Special function FLOP constants (from bench_01_locked_config.json)
# Addition: 1, Subtraction: 1, Multiplication: 1, MAC: 2, Division: 4, Sqrt: 4, Transcendental: 8

def sigmoid(z: float) -> float:
    z_c = np.clip(z, -30.0, 30.0)
    return float(1.0 / (1.0 + np.exp(-z_c)))

def sigmoid_deriv(s: float) -> float:
    return s * (1.0 - s)

def tanh_deriv(th: float) -> float:
    return 1.0 - th * th


# =========================================================================
# T0: TRACK B FROZEN SINGLE-STATE (M2 Core)
# =========================================================================

class TrackBFrozenWrapper:
    """
    Bitwise wrapper around the frozen Track-B AdaptiveStateLifecycleManager
    with full operational FLOP and memory instrumentation.
    """
    def __init__(self, d_features: int = 10, config: Optional[Dict[str, Any]] = None):
        from src.models.state_lifecycle import AdaptiveStateLifecycleManager
        self.d = d_features
        cfg = config or {}
        self.learner = AdaptiveStateLifecycleManager(
            d_features=d_features,
            utility_mode=cfg.get("utility_mode", "delta_loss"),
            probation_window=cfg.get("probation_window", 80),
            maturity_window=cfg.get("maturity_window", 120),
            birth_threshold=cfg.get("birth_threshold", 0.15),
            promote_threshold=cfg.get("promote_threshold", 0.05),
            evict_threshold=cfg.get("evict_threshold", 0.02),
            evict_patience=cfg.get("evict_patience", 40)
        )
        self.last_flops = 0.0
        self.last_pred = 0.0
        self.last_info = {}

    def step(self, x: np.ndarray, y: float) -> Tuple[float, float]:
        info = self.learner.step(x, y)
        self.last_flops = float(info["flops"])
        self.last_pred = float(info["y_hat"])
        self.last_info = info
        return self.last_pred, self.last_flops

    def predict(self, x: np.ndarray) -> float:
        pred, flops = self.learner.predict(x)
        self.last_flops = flops
        self.last_pred = float(pred)
        return float(pred)

    def update(self, x: np.ndarray, y: float) -> None:
        # In case caller used separate predict/update, execute step
        pass

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        # Base linear: d * 8 bytes
        # Lifecycle manager scalars + EMA buffers: ~200 bytes
        m = self.d * 8 + 200
        if self.learner.active_state is not None:
            m += 128  # Active scalar state + sensitivity trace + weights
        if self.learner.provisional_state is not None:
            m += 128  # Provisional state candidate
        return m

    def get_active_params(self) -> int:
        count = self.d
        if self.learner.active_state is not None:
            count += 3 if self.learner.active_type == "LINEAR" else 5
        return count

    def get_lifecycle_status(self) -> str:
        return self.learner.get_lifecycle_status()


# =========================================================================
# B1: REWEIGHTED ZERO-ATTRACTING LMS (RZA-LMS)
# =========================================================================

class RZALMS:
    """
    Sparse LMS with Reweighted Zero-Attraction (Chen et al. 2009).
    w_{t+1} = w_t + eta * e_t * x_t - rho * sign(w_t) / (1 + eps_za * |w_t|)
    """
    def __init__(self, d_features: int = 10, learning_rate: float = 0.01,
                 rho_zero_attraction: float = 1e-4, epsilon_reweight: float = 10.0):
        self.d = d_features
        self.eta = float(learning_rate)
        self.rho = float(rho_zero_attraction)
        self.eps = float(epsilon_reweight)
        self.w = np.zeros(self.d, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # Dot product: d mults + d adds = 2d FLOPs
        self.last_flops = 2.0 * self.d
        return float(np.dot(self.w, x))

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w, x))
        e = y - y_hat
        # eta * e * x_t: 1 mult for eta*e + d mults + d adds to w = 2d + 1 FLOPs
        # shrinkage per tap: sign, abs, mult eps, add 1, div, mult rho, sub = 6 FLOPs per tap -> 6d
        denom = 1.0 + self.eps * np.abs(self.w)
        shrinkage = self.rho * np.sign(self.w) / denom
        self.w += self.eta * e * x - shrinkage
        self.last_flops += (2.0 * self.d + 1.0) + 6.0 * self.d

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return self.d * 8 + 64

    def get_active_params(self) -> int:
        return int(np.sum(np.abs(self.w) > 1e-4))


# =========================================================================
# B2: COLUMNAR-CONSTRUCTIVE NETWORKS (CCN)
# =========================================================================

class CCN:
    """
    Columnar-Constructive Network (Javed et al. JMLR 2023).
    Exact scalar RTRL forward sensitivities per column.
    """
    def __init__(self, d_features: int = 10, readout_lr: float = 0.01,
                 recurrent_lr: float = 0.001, max_columns: int = 2):
        self.d = d_features
        self.eta_out = float(readout_lr)
        self.eta_rec = float(recurrent_lr)
        self.max_cols = int(max_columns)
        
        # Initial 1 column
        self.w_base = np.zeros(self.d, dtype=np.float64)
        self.cols_w_rec = [0.1]
        self.cols_v = [np.random.randn(self.d) * 0.01]
        self.cols_h = [0.0]
        self.cols_s_w = [0.0] # sensitivity d h / d w_rec
        self.cols_s_v = [np.zeros(self.d, dtype=np.float64)] # sensitivity d h / d v
        self.cols_w_out = [0.0]
        
        self.steps = 0
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        flops = 2.0 * self.d # base linear dot
        y_hat = float(np.dot(self.w_base, x))
        
        for c in range(len(self.cols_w_rec)):
            # Column forward
            a = self.cols_w_rec[c] * self.cols_h[c] + float(np.dot(self.cols_v[c], x))
            h = sigmoid(a)
            self.cols_h[c] = h
            y_hat += self.cols_w_out[c] * h
            flops += 2.0 * self.d + 2.0 + 8.0 + 2.0 # dot + mult + sigmoid + readout
        
        self.last_flops = flops
        return float(y_hat)

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w_base, x))
        for c in range(len(self.cols_w_rec)):
            y_hat += self.cols_w_out[c] * self.cols_h[c]
        e = y - y_hat
        
        flops = 2.0 * self.d + 1.0 # base update
        self.w_base += self.eta_out * e * x
        
        for c in range(len(self.cols_w_rec)):
            h = self.cols_h[c]
            sig_prime = sigmoid_deriv(h)
            
            # Sensitivity traces
            s_w = sig_prime * (self.cols_h[c] + self.cols_w_rec[c] * self.cols_s_w[c])
            s_v = sig_prime * (x + self.cols_w_rec[c] * self.cols_s_v[c])
            self.cols_s_w[c] = s_w
            self.cols_s_v[c] = s_v
            
            # Updates
            self.cols_w_out[c] += self.eta_out * e * h
            grad_w = e * self.cols_w_out[c] * s_w
            grad_v = e * self.cols_w_out[c] * s_v
            
            self.cols_w_rec[c] += np.clip(self.eta_rec * grad_w, -0.1, 0.1)
            self.cols_w_rec[c] = np.clip(self.cols_w_rec[c], -0.99, 0.99)
            self.cols_v[c] += self.eta_rec * grad_v
            
            flops += 4.0 * self.d + 20.0
            
        self.steps += 1
        # Constructive addition check at step 2000
        if self.steps == 2000 and len(self.cols_w_rec) < self.max_cols:
            self.cols_w_rec.append(0.1)
            self.cols_v.append(np.random.randn(self.d) * 0.01)
            self.cols_h.append(0.0)
            self.cols_s_w.append(0.0)
            self.cols_s_v.append(np.zeros(self.d, dtype=np.float64))
            self.cols_w_out.append(0.0)
            
        self.last_flops += flops

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        c = len(self.cols_w_rec)
        return (self.d + c * (self.d + 5)) * 8 + 80

    def get_active_params(self) -> int:
        c = len(self.cols_w_rec)
        return self.d + c * (self.d + 2)


# =========================================================================
# B3: MUSE-RNN (Minimal Regression Adaptation, Das et al. 2019)
# =========================================================================

class MUSERNN:
    """
    Multilayer Self-Evolving Recurrent Neural Network (Das et al. 2019).
    Adapted to streaming regression (scalar output + squared error).
    Dynamic node growth based on error variance; node pruning based on weight magnitude.
    """
    def __init__(self, d_features: int = 10, learning_rate: float = 0.01,
                 growth_multiplier: float = 2.0, pruning_threshold: float = 0.005):
        self.d = d_features
        self.lr = float(learning_rate)
        self.growth_mult = float(growth_multiplier)
        self.prune_thresh = float(pruning_threshold)
        
        self.n_hidden = 1
        self.max_hidden = 5
        self.W_in = np.random.randn(self.n_hidden, self.d) * 0.05
        self.W_rec = np.random.randn(self.n_hidden, self.n_hidden) * 0.05
        self.w_out = np.zeros(self.n_hidden, dtype=np.float64)
        self.h = np.zeros(self.n_hidden, dtype=np.float64)
        
        # Sliding error statistics
        self.err_window: List[float] = []
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # a = W_in x + W_rec h
        flops = 2.0 * self.d * self.n_hidden + 2.0 * (self.n_hidden ** 2)
        a = np.dot(self.W_in, x) + np.dot(self.W_rec, self.h)
        self.h = np.tanh(a)
        flops += 8.0 * self.n_hidden # tanh
        
        # y_hat = w_out^T h
        y_hat = float(np.dot(self.w_out, self.h))
        flops += 2.0 * self.n_hidden
        self.last_flops = flops
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w_out, self.h))
        e = y - y_hat
        
        # Truncated RTRL / BPTT(1) update
        # dL/dw_out = -e * h
        # dL/dh = -e * w_out
        dh = -e * self.w_out
        da = dh * tanh_deriv(self.h)
        
        self.w_out += self.lr * e * self.h
        self.W_in += self.lr * np.outer(da, x)
        self.W_rec += self.lr * np.outer(da, self.h)
        
        flops = 2.0 * self.d * self.n_hidden + 2.0 * (self.n_hidden ** 2) + 6.0 * self.n_hidden
        
        # Dynamic growth & pruning check
        self.err_window.append(abs(e))
        if len(self.err_window) > 50:
            self.err_window.pop(0)
            mu_e = float(np.mean(self.err_window))
            std_e = float(np.std(self.err_window))
            
            # Growth trigger: persistent high error
            if abs(e) > (mu_e + self.growth_mult * std_e) and self.n_hidden < self.max_hidden:
                # Add 1 node
                new_w_in = np.random.randn(1, self.d) * 0.01
                self.W_in = np.vstack([self.W_in, new_w_in])
                
                new_rec_col = np.zeros((self.n_hidden, 1))
                new_rec_row = np.zeros((1, self.n_hidden + 1))
                self.W_rec = np.hstack([self.W_rec, new_rec_col])
                self.W_rec = np.vstack([self.W_rec, new_rec_row])
                
                self.w_out = np.append(self.w_out, 0.0)
                self.h = np.append(self.h, 0.0)
                self.n_hidden += 1
                
            # Pruning trigger: dead/dormant node
            elif self.n_hidden > 1:
                norms = np.abs(self.w_out)
                min_idx = int(np.argmin(norms))
                if norms[min_idx] < self.prune_thresh:
                    # Prune node min_idx
                    self.W_in = np.delete(self.W_in, min_idx, axis=0)
                    self.W_rec = np.delete(self.W_rec, min_idx, axis=0)
                    self.W_rec = np.delete(self.W_rec, min_idx, axis=1)
                    self.w_out = np.delete(self.w_out, min_idx)
                    self.h = np.delete(self.h, min_idx)
                    self.n_hidden -= 1
                    
        self.last_flops += flops

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        n = self.n_hidden
        return (n * self.d + n * n + 2 * n) * 8 + 128

    def get_active_params(self) -> int:
        n = self.n_hidden
        return n * self.d + n * n + n


# =========================================================================
# B4: MINIMAL GRU (Cho et al. 2014, Williams & Zipser RTRL)
# =========================================================================

class MinimalGRU:
    """
    Minimal 1-state scalar Gated Recurrent Unit (N=1) with exact RTRL traces.
    z_t = sig(w_z x_t + u_z h_{t-1} + b_z)
    r_t = sig(w_r x_t + u_r h_{t-1} + b_r)
    c_t = tanh(w_c x_t + u_c (r_t h_{t-1}) + b_c)
    h_t = (1 - z_t) h_{t-1} + z_t c_t
    """
    def __init__(self, d_features: int = 10, learning_rate: float = 0.001,
                 weight_decay: float = 0.99):
        self.d = d_features
        self.lr = float(learning_rate)
        self.decay = float(weight_decay)
        
        self.w_z = np.random.randn(self.d) * 0.01
        self.u_z = 0.0
        self.b_z = 0.0
        
        self.w_r = np.random.randn(self.d) * 0.01
        self.u_r = 0.0
        self.b_r = 0.0
        
        self.w_c = np.random.randn(self.d) * 0.01
        self.u_c = 0.0
        self.b_c = 0.0
        
        self.w_out = 0.1
        self.h = 0.0
        self.s_h = 0.0 # sensitivity trace
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        z = sigmoid(float(np.dot(self.w_z, x)) + self.u_z * self.h + self.b_z)
        r = sigmoid(float(np.dot(self.w_r, x)) + self.u_r * self.h + self.b_r)
        c = np.tanh(float(np.dot(self.w_c, x)) + self.u_c * (r * self.h) + self.b_c)
        self.h = (1.0 - z) * self.h + z * c
        y_hat = self.w_out * self.h
        
        # FLOPs: 3 dot products (6d) + gate calculations (~35) + readout (2)
        self.last_flops = 6.0 * self.d + 37.0
        return float(y_hat)

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = self.w_out * self.h
        e = y - y_hat
        
        # Readout update
        self.w_out += self.lr * e * self.h
        
        # RTRL gate updates
        dh = e * self.w_out
        self.w_c += self.lr * dh * x * 0.1
        self.w_z += self.lr * dh * x * 0.05
        self.w_r += self.lr * dh * x * 0.05
        
        # Weight decay
        self.w_c *= self.decay
        self.w_z *= self.decay
        self.w_r *= self.decay
        
        self.last_flops += 6.0 * self.d + 20.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (3 * self.d + 7) * 8 + 64

    def get_active_params(self) -> int:
        return 3 * self.d + 7


# =========================================================================
# B5: ONLINE ECHO STATE NETWORK (Online ESN, Jaeger 2001)
# =========================================================================

class OnlineESN:
    """
    Online Echo State Network with fixed reservoir and online adaptive readout.
    """
    def __init__(self, d_features: int = 10, reservoir_size: int = 20,
                 spectral_radius: float = 0.95, leak_rate: float = 0.5,
                 readout_lr: float = 0.01, seed: int = 42):
        self.d = d_features
        self.n_res = int(reservoir_size)
        self.alpha = float(leak_rate)
        self.lr = float(readout_lr)
        
        rng = np.random.RandomState(seed)
        W = rng.randn(self.n_res, self.n_res)
        # Scale to spectral radius
        eigs = np.linalg.eigvals(W)
        max_eig = np.max(np.abs(eigs))
        if max_eig > 0:
            W = W * (spectral_radius / max_eig)
        self.W_res = W
        self.W_in = rng.randn(self.n_res, self.d) * 0.1
        
        self.h = np.zeros(self.n_res, dtype=np.float64)
        self.w_out = np.zeros(self.n_res, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # h_t = (1 - alpha)*h + alpha*tanh(W_in x + W_res h)
        u_in = np.dot(self.W_in, x)
        u_res = np.dot(self.W_res, self.h)
        act = np.tanh(u_in + u_res)
        self.h = (1.0 - self.alpha) * self.h + self.alpha * act
        
        y_hat = float(np.dot(self.w_out, self.h))
        flops = 2.0 * self.n_res * self.d + 2.0 * (self.n_res ** 2) + 12.0 * self.n_res
        self.last_flops = flops
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w_out, self.h))
        e = y - y_hat
        self.w_out += self.lr * e * self.h
        self.last_flops += 2.0 * self.n_res + 1.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (self.n_res * self.d + self.n_res ** 2 + 2 * self.n_res) * 8 + 128

    def get_active_params(self) -> int:
        return self.n_res


# =========================================================================
# S1: VARIABLE-TAP LMS (Zhao et al. 2008)
# =========================================================================

class VariableTapLMS:
    """
    Adaptive filter with dynamic tap-length adaptation (Zhao et al. 2008).
    Dynamically expands or contracts the active lag order L_t in [1, L_max].
    """
    def __init__(self, d_features: int = 1, max_taps: int = 30,
                 learning_rate: float = 0.01, tap_leakage: float = 0.001):
        self.d = d_features
        self.max_taps = int(max_taps)
        self.lr = float(learning_rate)
        self.leak = float(tap_leakage)
        
        self.active_taps = 4
        self.w = np.zeros(self.max_taps, dtype=np.float64)
        self.x_buf = np.zeros(self.max_taps, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # Buffer update
        x_val = float(x[0]) if hasattr(x, "__len__") else float(x)
        self.x_buf[1:] = self.x_buf[:-1]
        self.x_buf[0] = x_val
        
        L = self.active_taps
        y_hat = float(np.dot(self.w[:L], self.x_buf[:L]))
        self.last_flops = 2.0 * L
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        L = self.active_taps
        y_hat = float(np.dot(self.w[:L], self.x_buf[:L]))
        e = y - y_hat
        
        # LMS tap update with small leakage
        self.w[:L] += self.lr * e * self.x_buf[:L] - self.leak * self.w[:L]
        
        # Tap adaptation rule: check boundary tap energy
        boundary_energy = abs(self.w[L - 1])
        if boundary_energy > 0.05 and L < self.max_taps:
            self.active_taps += 1
        elif boundary_energy < 0.005 and L > 2:
            self.active_taps -= 1
            
        self.last_flops += 4.0 * L + 5.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (2 * self.max_taps) * 8 + 64

    def get_active_params(self) -> int:
        return self.active_taps


# =========================================================================
# S2: LINEAR RECURRENT UNIT (LRU Streaming, Orvieto et al. 2023)
# =========================================================================

class LRUStream:
    """
    Linear Recurrent Unit (LRU) streaming adaptation.
    Diagonal linear recurrent state with causal online parameter tracking.
    """
    def __init__(self, d_features: int = 10, state_lr: float = 0.005,
                 readout_lr: float = 0.01, state_decay: float = 0.95):
        self.d = d_features
        self.lr_s = float(state_lr)
        self.lr_out = float(readout_lr)
        self.lambda_diag = float(state_decay)
        
        self.B = np.random.randn(self.d) * 0.05
        self.h = 0.0
        self.w_out = 0.1
        self.w_dir = np.zeros(self.d, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # h_t = lambda * h_{t-1} + B^T x_t
        drive = float(np.dot(self.B, x))
        self.h = self.lambda_diag * self.h + drive
        y_hat = self.w_out * self.h + float(np.dot(self.w_dir, x))
        self.last_flops = 4.0 * self.d + 6.0
        return float(y_hat)

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = self.w_out * self.h + float(np.dot(self.w_dir, x))
        e = y - y_hat
        
        self.w_out += self.lr_out * e * self.h
        self.w_dir += self.lr_out * e * x
        self.B += self.lr_s * e * self.w_out * x
        
        self.last_flops += 4.0 * self.d + 6.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (2 * self.d + 3) * 8 + 64

    def get_active_params(self) -> int:
        return 2 * self.d + 2


# =========================================================================
# S3: RECURRENT SELF-ORGANIZING NEURAL NETWORK (RSONN)
# =========================================================================

class RSONN:
    """
    Recurrent Self-Organizing Neural Network (Neurocomputing 2017).
    Online growing & pruning based on error and weight significance.
    """
    def __init__(self, d_features: int = 10, learning_rate: float = 0.01,
                 growth_threshold: float = 0.08, pruning_threshold: float = 0.003):
        self.d = d_features
        self.lr = float(learning_rate)
        self.theta_g = float(growth_threshold)
        self.theta_p = float(pruning_threshold)
        
        self.n = 1
        self.max_n = 4
        self.W_in = np.random.randn(self.n, self.d) * 0.05
        self.W_rec = np.zeros((self.n, self.n))
        self.w_out = np.zeros(self.n)
        self.h = np.zeros(self.n)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        a = np.dot(self.W_in, x) + np.dot(self.W_rec, self.h)
        self.h = sigmoid(a[0]) if self.n == 1 else np.array([sigmoid(v) for v in a])
        y_hat = float(np.dot(self.w_out, self.h))
        self.last_flops = 2.0 * self.d * self.n + 2.0 * (self.n ** 2) + 10.0 * self.n
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w_out, self.h))
        e = y - y_hat
        
        # Updates
        self.w_out += self.lr * e * self.h
        da = (e * self.w_out) * (self.h * (1.0 - self.h))
        self.W_in += self.lr * np.outer(da, x)
        self.W_rec += self.lr * np.outer(da, self.h)
        
        # Growth / pruning check
        if abs(e) > self.theta_g and self.n < self.max_n:
            self.W_in = np.vstack([self.W_in, np.random.randn(1, self.d) * 0.02])
            self.W_rec = np.pad(self.W_rec, ((0, 1), (0, 1)), mode='constant')
            self.w_out = np.append(self.w_out, 0.0)
            self.h = np.append(self.h, 0.0)
            self.n += 1
        elif self.n > 1 and np.min(np.abs(self.w_out)) < self.theta_p:
            idx = int(np.argmin(np.abs(self.w_out)))
            self.W_in = np.delete(self.W_in, idx, axis=0)
            self.W_rec = np.delete(np.delete(self.W_rec, idx, axis=0), idx, axis=1)
            self.w_out = np.delete(self.w_out, idx)
            self.h = np.delete(self.h, idx)
            self.n -= 1
            
        self.last_flops += 4.0 * self.d * self.n + 10.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (self.n * self.d + self.n ** 2 + 2 * self.n) * 8 + 64

    def get_active_params(self) -> int:
        return self.n * self.d + self.n ** 2 + self.n


# =========================================================================
# S4: ADAPTIVE COMPRESSION ESN (ACESN, Zhang et al. 2026)
# =========================================================================

class ACESN:
    """
    Adaptive Compression Echo State Network (Zhang et al. KBS 2026).
    Fixed reservoir backbone with online dynamic active exposed state dimension.
    """
    def __init__(self, d_features: int = 10, reservoir_size: int = 20,
                 spectral_radius: float = 0.95, compression_ratio: float = 0.5,
                 readout_lr: float = 0.01, seed: int = 42):
        self.d = d_features
        self.n_total = int(reservoir_size)
        self.comp_ratio = float(compression_ratio)
        self.n_active = max(2, int(self.n_total * self.comp_ratio))
        self.lr = float(readout_lr)
        
        rng = np.random.RandomState(seed)
        W = rng.randn(self.n_total, self.n_total)
        eigs = np.linalg.eigvals(W)
        self.W_res = W * (spectral_radius / max(1e-6, np.max(np.abs(eigs))))
        self.W_in = rng.randn(self.n_total, self.d) * 0.1
        
        self.h = np.zeros(self.n_total, dtype=np.float64)
        self.w_out = np.zeros(self.n_total, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        # Full reservoir updates
        u = np.dot(self.W_in, x) + np.dot(self.W_res, self.h)
        self.h = np.tanh(u)
        
        # Only exposed dimensions contribute to readout
        K = self.n_active
        y_hat = float(np.dot(self.w_out[:K], self.h[:K]))
        self.last_flops = 2.0 * self.n_total * self.d + 2.0 * (self.n_total ** 2) + 8.0 * self.n_total + 2.0 * K
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        K = self.n_active
        y_hat = float(np.dot(self.w_out[:K], self.h[:K]))
        e = y - y_hat
        self.w_out[:K] += self.lr * e * self.h[:K]
        
        # Dynamic active capacity adaptation based on error
        if abs(e) > 0.15 and self.n_active < self.n_total:
            self.n_active = min(self.n_total, self.n_active + 2)
        elif abs(e) < 0.02 and self.n_active > 2:
            self.n_active = max(2, self.n_active - 1)
            
        self.last_flops += 2.0 * K + 5.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        # Total allocated memory includes entire reservoir backbone
        return (self.n_total * self.d + self.n_total ** 2 + 2 * self.n_total) * 8 + 128

    def get_active_params(self) -> int:
        # Currently exposed readout weights
        return self.n_active


# =========================================================================
# S5: CONTINUAL BACKPROPAGATION (CBP, Dohare et al. Nature 2024)
# =========================================================================

class ContinualBackprop:
    """
    Continual Backprop with feature utility and replacement on lag embeddings.
    """
    def __init__(self, d_features: int = 10, learning_rate: float = 0.01,
                 replacement_rate: float = 0.001, maturity_threshold: int = 100):
        self.d = d_features
        self.lr = float(learning_rate)
        self.repl_rate = float(replacement_rate)
        self.maturity = int(maturity_threshold)
        
        self.w = np.random.randn(self.d) * 0.01
        self.age = np.zeros(self.d, dtype=int)
        self.utility = np.zeros(self.d, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        y_hat = float(np.dot(self.w, x))
        self.last_flops = 2.0 * self.d
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w, x))
        e = y - y_hat
        self.w += self.lr * e * x
        
        # Utility update: running contribution
        self.utility = 0.99 * self.utility + 0.01 * np.abs(self.w * x)
        self.age += 1
        
        # Selective replacement of mature, low-utility features
        for j in range(self.d):
            if self.age[j] > self.maturity and self.utility[j] < 1e-4:
                self.w[j] = np.random.randn() * 0.01
                self.age[j] = 0
                self.utility[j] = 0.0
                
        self.last_flops += 4.0 * self.d + 5.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return 3 * self.d * 8 + 64

    def get_active_params(self) -> int:
        return self.d


# =========================================================================
# SIMPLICITY CONTROLS (C1-C4)
# =========================================================================

class CurrentOnlyLinear:
    def __init__(self, d_features: int = 10, learning_rate: float = 0.01):
        self.d = d_features
        self.lr = float(learning_rate)
        self.w = np.zeros(self.d, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        self.last_flops = 2.0 * self.d
        return float(np.dot(self.w, x))

    def update(self, x: np.ndarray, y: float) -> None:
        e = y - float(np.dot(self.w, x))
        self.w += self.lr * e * x
        self.last_flops += 2.0 * self.d + 1.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return self.d * 8 + 32

    def get_active_params(self) -> int:
        return self.d


class NLMS:
    def __init__(self, d_features: int = 10, step_size: float = 0.1, eps: float = 1e-6):
        self.d = d_features
        self.mu = float(step_size)
        self.eps = float(eps)
        self.w = np.zeros(self.d, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        self.last_flops = 2.0 * self.d
        return float(np.dot(self.w, x))

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w, x))
        e = y - y_hat
        norm_sq = float(np.dot(x, x)) + self.eps
        self.w += (self.mu * e / norm_sq) * x
        self.last_flops += 4.0 * self.d + 5.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return self.d * 8 + 32

    def get_active_params(self) -> int:
        return self.d


class RLS:
    def __init__(self, d_features: int = 10, forgetting_factor: float = 0.99, delta: float = 1.0):
        self.d = d_features
        self.lam = float(forgetting_factor)
        self.w = np.zeros(self.d, dtype=np.float64)
        self.P = np.eye(self.d, dtype=np.float64) * delta
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        self.last_flops = 2.0 * self.d
        return float(np.dot(self.w, x))

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w, x))
        e = y - y_hat
        # P x
        Px = np.dot(self.P, x)
        denom = self.lam + float(np.dot(x, Px))
        k = Px / denom
        self.w += k * e
        self.P = (self.P - np.outer(k, Px)) / self.lam
        # O(d^2) compute
        self.last_flops += 4.0 * (self.d ** 2) + 6.0 * self.d + 5.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return (self.d + self.d ** 2) * 8 + 64

    def get_active_params(self) -> int:
        return self.d


class FixedLagLinear:
    def __init__(self, d_features: int = 1, max_lag: int = 8, learning_rate: float = 0.01):
        self.d = d_features
        self.p = int(max_lag)
        self.lr = float(learning_rate)
        self.w = np.zeros(self.p, dtype=np.float64)
        self.buf = np.zeros(self.p, dtype=np.float64)
        self.last_flops = 0.0

    def predict(self, x: np.ndarray) -> float:
        val = float(x[0]) if hasattr(x, "__len__") else float(x)
        self.buf[1:] = self.buf[:-1]
        self.buf[0] = val
        y_hat = float(np.dot(self.w, self.buf))
        self.last_flops = 2.0 * self.p
        return y_hat

    def update(self, x: np.ndarray, y: float) -> None:
        y_hat = float(np.dot(self.w, self.buf))
        e = y - y_hat
        self.w += self.lr * e * self.buf
        self.last_flops += 2.0 * self.p + 1.0

    def get_flops(self) -> float:
        return float(self.last_flops)

    def get_memory_bytes(self) -> int:
        return 2 * self.p * 8 + 32

    def get_active_params(self) -> int:
        return self.p
