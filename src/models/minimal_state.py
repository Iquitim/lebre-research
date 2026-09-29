import numpy as np
from typing import Dict, Any, Tuple, Optional, List

def sigmoid(x: float) -> float:
    """Numerically stable sigmoid scalar."""
    if x >= 0:
        z = np.exp(-x)
        return 1.0 / (1.0 + z)
    else:
        z = np.exp(x)
        return z / (1.0 + z)

class LinearScalarState:
    """
    R2: Learned Linear Scalar State (STATE_DIM = 1)
        s_t = a_t * s_{t-1} + b_t * x_t
        y_hat_t = c_t * s_t
    where a_t = tanh(alpha_t) in (-1, 1) guarantees stability.
    Uses exact online forward sensitivity trace for (alpha, b, c).
    """
    def __init__(self, lr: float = 0.05, init_alpha: float = 1.0, init_b: float = 1.0, init_c: float = 1.0, train_c: bool = True):
        self.lr = lr
        self.alpha = float(init_alpha) # tanh(1.0) approx 0.7616
        self.b = float(init_b)
        self.c = float(init_c)
        self.train_c = train_c
        
        self.s = 0.0 # scalar state
        
        # Forward sensitivities: p_theta = ds_t / dtheta
        self.p_alpha = 0.0
        self.p_b = 0.0
        
        self.total_steps = 0

    def forward(self, x: float) -> Tuple[float, float, float]:
        """
        Advances state by one step and computes prediction.
        Returns:
            s_t: new scalar state
            y_hat: prediction
            a_t: current recurrent weight tanh(alpha)
        """
        self.total_steps += 1
        a_t = float(np.tanh(self.alpha))
        dtanh = 1.0 - a_t ** 2
        
        # Recursive forward sensitivities
        self.p_alpha = a_t * self.p_alpha + dtanh * self.s
        self.p_b = a_t * self.p_b + x
        
        # State update
        self.s = a_t * self.s + self.b * x
        y_hat = self.c * self.s
        
        return self.s, y_hat, a_t

    def update(self, y: float, y_hat: float, x: float) -> Dict[str, float]:
        """
        Updates parameters online using prediction error and sensitivities.
        """
        e_t = y - y_hat
        
        # Gradient of loss L = 0.5 * e^2: dL/dtheta = - e * dy_hat/dtheta
        # dy_hat/dalpha = c * p_alpha
        # dy_hat/db = c * p_b
        # dy_hat/dc = s
        grad_alpha = - e_t * self.c * self.p_alpha
        grad_b = - e_t * self.c * self.p_b
        grad_c = - e_t * self.s if self.train_c else 0.0
        
        # Normalization factor for stability
        norm_sq = (self.c * self.p_alpha) ** 2 + (self.c * self.p_b) ** 2 + (self.s ** 2 if self.train_c else 0.0) + 1e-4
        step = self.lr / (norm_sq + 1.0)
        
        self.alpha -= step * grad_alpha
        self.b -= step * grad_b
        if self.train_c:
            self.c -= step * grad_c
        else:
            self.c = 1.0
            
        self.alpha = float(np.clip(self.alpha, -6.0, 6.0))
        self.b = float(np.clip(self.b, -10.0, 10.0))
        
        # Flop count: ~18 flops for forward + sensitivity + update
        return {
            "error": e_t,
            "a": float(np.tanh(self.alpha)),
            "b": self.b,
            "c": self.c,
            "flops": 18.0
        }

    def get_memory_bytes(self) -> int:
        # State s (8), alpha, b, c (24), p_alpha, p_b (16) = 48 bytes
        return 48


class GatedScalarState:
    """
    R3 & R4: Learned Gated Scalar State (STATE_DIM = 1)
        s_t = (1 - g_t) * s_{t-1} + g_t * v_t
        g_t = sigmoid(w_g^T * z_t + b_g)
        v_t = w_v^T * z_t + b_v
        y_hat_t = c_t * s_t
        
    Difference between R3 and R4:
        use_sensitivity_trace = False (R3): instantaneous gradient (p_{t-1} discarded)
        use_sensitivity_trace = True (R4): exact forward recursive sensitivity trace
    """
    def __init__(
        self,
        z_dim: int = 2,
        lr: float = 0.10,
        use_sensitivity_trace: bool = True,
        init_bg: float = -2.0, # conservative initial retention: sigmoid(-2) approx 0.119
        train_bv: bool = False,
        train_c: bool = True
    ):
        self.z_dim = z_dim
        self.lr = lr
        self.use_sensitivity_trace = use_sensitivity_trace
        self.train_bv = train_bv
        self.train_c = train_c
        
        # Parameters
        self.w_g = np.zeros(z_dim, dtype=np.float64)
        self.b_g = float(init_bg)
        self.w_v = np.zeros(z_dim, dtype=np.float64)
        self.b_v = 0.0
        self.c = 1.0 # output scaling
        
        self.s = 0.0 # scalar state
        
        # Forward sensitivities: p_theta = ds_t / dtheta
        self.p_wg = np.zeros(z_dim, dtype=np.float64)
        self.p_bg = 0.0
        self.p_wv = np.zeros(z_dim, dtype=np.float64)
        self.p_bv = 0.0
        
        self.last_g = 0.0
        self.last_v = 0.0
        self.last_z = np.zeros(z_dim, dtype=np.float64)

    def forward(self, z: np.ndarray) -> Tuple[float, float, float]:
        """
        Advances state by one step and computes prediction.
        Returns:
            s_t: new scalar state
            y_hat: prediction
            g_t: write gate value in [0, 1]
        """
        assert z.shape == (self.z_dim,)
        self.last_z = z.copy()
        
        # Compute gate and candidate value
        logit_g = float(np.dot(self.w_g, z) + self.b_g)
        g_t = sigmoid(logit_g)
        v_t = float(np.dot(self.w_v, z) + self.b_v)
        
        self.last_g = g_t
        self.last_v = v_t
        
        prev_s = self.s
        dg = g_t * (1.0 - g_t)
        
        if self.use_sensitivity_trace:
            # R4: Exact forward sensitivity recursion
            # ds_t / dtheta = (1 - g_t) * ds_{t-1}/dtheta + (v_t - s_{t-1}) * dg/dtheta + g_t * dv_t/dtheta
            self.p_wg = (1.0 - g_t) * self.p_wg + (v_t - prev_s) * dg * z
            self.p_bg = (1.0 - g_t) * self.p_bg + (v_t - prev_s) * dg
            self.p_wv = (1.0 - g_t) * self.p_wv + g_t * z
            self.p_bv = (1.0 - g_t) * self.p_bv + (g_t if self.train_bv else 0.0)
        else:
            # R3: Instantaneous truncated sensitivity (p_{t-1} = 0)
            self.p_wg = (v_t - prev_s) * dg * z
            self.p_bg = (v_t - prev_s) * dg
            self.p_wv = g_t * z
            self.p_bv = g_t if self.train_bv else 0.0
            
        # State update
        self.s = float((1.0 - g_t) * prev_s + g_t * v_t)
        y_hat = float(self.c * self.s)
        
        return self.s, y_hat, g_t

    def update(self, y: float, y_hat: float) -> Dict[str, Any]:
        """
        Updates parameters online using prediction error and sensitivities.
        """
        e_t = y - y_hat
        
        # dL/dtheta = - e * c * p_theta
        grad_wg = - e_t * self.c * self.p_wg
        grad_bg = - e_t * self.c * self.p_bg
        grad_wv = - e_t * self.c * self.p_wv
        grad_bv = - e_t * self.c * self.p_bv if self.train_bv else 0.0
        grad_c = - e_t * self.s if self.train_c else 0.0
        
        # Compute gradient norm for step size scaling
        norm_sq = float(np.sum(self.p_wg**2) + self.p_bg**2 + np.sum(self.p_wv**2) + (self.p_bv**2 if self.train_bv else 0.0) + (self.s**2 if self.train_c else 0.0))
        step = self.lr / (norm_sq + 1.0)
        
        self.w_g -= step * grad_wg
        self.b_g -= step * grad_bg
        self.w_v -= step * grad_wv
        if self.train_bv:
            self.b_v -= step * grad_bv
        else:
            self.b_v = 0.0
            
        if self.train_c:
            self.c -= (self.lr * 0.1) * grad_c # readout adapts more gently
        else:
            self.c = 1.0
        
        # Clamp parameters to prevent numerical blowup
        self.b_g = float(np.clip(self.b_g, -8.0, 8.0))
        self.w_g = np.clip(self.w_g, -10.0, 10.0)
        self.w_v = np.clip(self.w_v, -10.0, 10.0)
        
        # Flop count: ~28 flops for forward + sensitivity + update
        return {
            "error": e_t,
            "gate": self.last_g,
            "v": self.last_v,
            "w_g": self.w_g.copy(),
            "b_g": self.b_g,
            "w_v": self.w_v.copy(),
            "b_v": self.b_v,
            "c": self.c,
            "flops": 28.0 if self.use_sensitivity_trace else 18.0
        }

    def get_memory_bytes(self) -> int:
        # state s (8), params w_g(16), b_g(8), w_v(16), b_v(8), c(8) = 56 bytes
        # sensitivities p_wg(16), p_bg(8), p_wv(16), p_bv(8) = 48 bytes
        # Total = 104 bytes (R4) or 56 bytes (R3)
        return 104 if self.use_sensitivity_trace else 56


class ContextLagRouter:
    """
    Task C Model: Context-Dependent Lag Routing
    Uses a GatedScalarState to track latent mode from control inputs z_t = [x_{0, t}, x_{1, t}],
    and routes prediction between delay_a and delay_b:
        y_hat_t = s_t * x_{sig, t - delay_a} + (1 - s_t) * x_{sig, t - delay_b}
    """
    def __init__(self, delay_a: int = 2, delay_b: int = 7, use_sensitivity_trace: bool = True, lr: float = 0.10):
        self.delay_a = delay_a
        self.delay_b = delay_b
        self.state_model = GatedScalarState(
            z_dim=2,
            lr=lr,
            use_sensitivity_trace=use_sensitivity_trace,
            init_bg=-3.0,
            train_bv=False,
            train_c=False
        )
        self.state_model.w_g = np.array([3.0, 3.0])
        self.state_model.w_v = np.array([1.0, 0.0])

    def step(self, z_t: np.ndarray, x_delayed_a: float, x_delayed_b: float, y_t: float) -> Tuple[float, float, float]:
        """
        Advances state, computes routed prediction, and updates state parameters.
        Returns:
            s_t: mode state
            y_hat: routed prediction
            e_t: prediction error
        """
        # Forward state
        s_t, _, g_t = self.state_model.forward(z_t)
        
        # In Mode A (s_t approx 1), y_hat approx x_delayed_a
        # In Mode B (s_t approx 0), y_hat approx x_delayed_b
        s_route = float(np.clip(s_t, 0.0, 1.0))
        y_hat = float(s_route * x_delayed_a + (1.0 - s_route) * x_delayed_b)
        e_t = y_t - y_hat
        
        # Sensitivity update for routing: dL/ds_t = - e_t * (x_delayed_a - x_delayed_b)
        delta_x = float(np.clip(x_delayed_a - x_delayed_b, -3.0, 3.0))
        eff_err = float(np.clip(e_t * delta_x, -1.0, 1.0))
        eff_y = s_t + eff_err
        
        self.state_model.update(y=eff_y, y_hat=s_t)
        
        return s_t, y_hat, e_t

    def get_memory_bytes(self) -> int:
        return self.state_model.get_memory_bytes() + 16
