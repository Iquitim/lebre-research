import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from src.models.minimal_state import LinearScalarState, GatedScalarState

class AdaptiveStateLifecycleManager:
    """
    Adaptive State Lifecycle Controller for M2-EXP-0005.
    Manages the lifecycle of learned scalar recurrent states (STATE_DIM = 1):
    DORMANT -> PROVISIONAL -> ACTIVE -> MATURE -> EVICTED.
    
    Enforces:
    - MAX_ACTIVE_STATES = 1
    - MAX_PROVISIONAL_STATES = 1
    - Zero future or truth leakage
    - A state must PAY RENT to survive.
    """
    def __init__(
        self,
        d_features: int = 10,
        utility_mode: str = "delta_loss", # "delta_loss" (V3) or "cxo" (V4)
        probation_window: int = 80,
        maturity_window: int = 120,
        birth_threshold: float = 0.15,
        promote_threshold: float = 0.05,
        evict_threshold: float = 0.02,
        evict_patience: int = 40,
        oracle_mode: Optional[str] = None # None, "presence" (V5), or "type" (V6)
    ):
        self.d = d_features
        self.utility_mode = utility_mode
        self.probation_window = probation_window
        self.maturity_window = maturity_window
        self.birth_threshold = birth_threshold
        self.promote_threshold = promote_threshold
        self.evict_threshold = evict_threshold
        self.evict_patience = evict_patience
        self.oracle_mode = oracle_mode
        
        # Explicit base linear model weights (for state-free signal)
        self.w_base = np.zeros(self.d, dtype=np.float64)
        
        # State containers (Strictly MAX_ACTIVE_STATES=1, MAX_PROVISIONAL_STATES=1)
        self.active_state: Optional[Any] = None
        self.active_type: Optional[str] = None # "LINEAR" or "GATED"
        self.w_state: float = 0.0 # readout weight for active state
        self.active_age: int = 0
        self.active_updates: int = 0
        
        self.provisional_state: Optional[Any] = None
        self.provisional_type: Optional[str] = None
        self.w_prov: float = 0.0 # readout weight for provisional state
        self.provisional_age: int = 0
        
        # Error tracking for birth trigger
        self.ema_err_sq = 0.0
        self.recent_errs: List[float] = []
        self.low_utility_count = 0
        
        # Utility estimators
        self.ema_c = 0.0 # Controllability proxy
        self.ema_o = 0.0 # Observability proxy
        self.ema_delta_loss = 0.0 # Paired delta-loss proxy
        
        # Event logging
        self.birth_events: List[Dict[str, Any]] = []
        self.eviction_events: List[Dict[str, Any]] = []
        
        # Flop and memory tracking
        self.last_step_flops = 0.0
        self.total_steps = 0

    def get_lifecycle_status(self) -> str:
        if self.active_state is not None:
            if self.active_age >= self.maturity_window:
                return "MATURE"
            return "ACTIVE"
        elif self.provisional_state is not None:
            return "PROVISIONAL"
        else:
            return "DORMANT"

    def get_memory_bytes(self) -> int:
        # Base weights: d * 8 bytes
        mem = self.d * 8
        if self.active_state is not None:
            mem += self.active_state.get_memory_bytes() + 8 # +8 for w_state
        if self.provisional_state is not None:
            mem += self.provisional_state.get_memory_bytes() + 8 # +8 for w_prov
        return mem

    def compute_controllability_proxy(self, model: Any, model_type: str) -> float:
        """
        C proxy: Measures whether current input drives meaningful change in the state.
        LINEAR: (b_t * x_t)^2
        GATED: (g_t * (v_t - s_{t-1}))^2
        """
        if model_type == "LINEAR":
            # Driving input contribution
            return float((model.b * getattr(model, "last_x", 0.0)) ** 2)
        elif model_type == "GATED":
            g_t = getattr(model, "last_g", 0.0)
            v_t = getattr(model, "last_v", 0.0)
            prev_s = getattr(model, "prev_s", 0.0)
            return float((g_t * (v_t - prev_s)) ** 2)
        return 0.0

    def compute_observability_proxy(self, state_val: float, w_out: float) -> float:
        """
        O proxy: Measures whether state affects prediction output: |w_out * s_t|.
        """
        return float(abs(w_out * state_val))

    def predict(self, x_t: np.ndarray) -> Tuple[float, float]:
        """
        Computes system prediction.
        Returns:
            y_hat: prediction
            y_base: prediction without active state (counterfactual)
        """
        self.last_step_flops = 0.0
        y_base = float(np.dot(self.w_base, x_t))
        self.last_step_flops += 2 * self.d # dot product flops
        
        y_hat = y_base
        if self.active_state is not None:
            # Advance active state forward
            if self.active_type == "LINEAR":
                s_t, _, _ = self.active_state.forward(x_t[0])
                self.active_state.last_x = x_t[0]
                self.last_step_flops += 6
            elif self.active_type == "GATED":
                # For Gated state, previous state is stored before update
                self.active_state.prev_s = self.active_state.s
                s_t, _, _ = self.active_state.forward(x_t[:2])
                self.last_step_flops += 10
            else:
                s_t = 0.0
                
            y_hat += self.w_state * s_t
            self.last_step_flops += 2
            
        if self.provisional_state is not None:
            # Advance provisional state in shadow mode
            if self.provisional_type == "LINEAR":
                s_p, _, _ = self.provisional_state.forward(x_t[0])
                self.provisional_state.last_x = x_t[0]
                self.last_step_flops += 6
            elif self.provisional_type == "GATED":
                self.provisional_state.prev_s = self.provisional_state.s
                s_p, _, _ = self.provisional_state.forward(x_t[:2])
                self.last_step_flops += 10
                
        return y_hat, y_base

    def step(self, x_t: np.ndarray, y_t: float, oracle_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Full causal step: predict, compute utilities, update parameters, and manage lifecycle.
        """
        self.total_steps += 1
        y_hat, y_base = self.predict(x_t)
        
        e_t = y_t - y_hat
        e_base = y_t - y_base
        
        # Track residual energy for birth trigger
        err_sq = e_t ** 2
        alpha_e = 0.05
        self.ema_err_sq = (1.0 - alpha_e) * self.ema_err_sq + alpha_e * err_sq
        self.recent_errs.append(err_sq)
        if len(self.recent_errs) > 40:
            self.recent_errs.pop(0)
            
        # Update explicit base weights (NLMS step)
        norm_x = float(np.dot(x_t, x_t) + 1e-4)
        step_base = 0.20 / (norm_x + 1.0)
        self.w_base += step_base * e_base * x_t
        self.last_step_flops += 2 * self.d + 4
        
        # Counterfactual paired delta-loss for active state
        delta_loss = float(e_base ** 2 - e_t ** 2)
        alpha_u = 0.05
        self.ema_delta_loss = (1.0 - alpha_u) * self.ema_delta_loss + alpha_u * delta_loss
        
        # Update active state if present
        c_inst = 0.0
        o_inst = 0.0
        if self.active_state is not None:
            self.active_age += 1
            self.active_updates += 1
            s_t = self.active_state.s
            
            # Normalized LMS Readout weight update
            step_state = 0.20 / (s_t ** 2 + 1.0)
            self.w_state += step_state * e_t * s_t
            self.w_state = float(np.clip(self.w_state, -5.0, 5.0))
            self.last_step_flops += 4
            
            # State internal sensitivity update
            if self.active_type == "LINEAR":
                self.active_state.update(y_t, y_hat, x_t[0])
                self.last_step_flops += 12
            elif self.active_type == "GATED":
                self.active_state.update(y_t, y_hat)
                self.last_step_flops += 18
                
            c_inst = self.compute_controllability_proxy(self.active_state, self.active_type)
            o_inst = self.compute_observability_proxy(s_t, self.w_state)
            self.ema_c = (1.0 - alpha_u) * self.ema_c + alpha_u * c_inst
            self.ema_o = (1.0 - alpha_u) * self.ema_o + alpha_u * o_inst
            
        # Update provisional state if in shadow mode
        if self.provisional_state is not None:
            self.provisional_age += 1
            s_p = self.provisional_state.s
            yh_prov = y_base + self.w_prov * s_p
            e_p = y_t - yh_prov
            step_prov = 0.20 / (s_p ** 2 + 1.0)
            self.w_prov += step_prov * e_p * s_p
            self.w_prov = float(np.clip(self.w_prov, -5.0, 5.0))
            
            if self.provisional_type == "LINEAR":
                self.provisional_state.update(y_t, yh_prov, x_t[0])
            elif self.provisional_type == "GATED":
                self.provisional_state.update(y_t, yh_prov)
                
        # Combined C x O score
        score_cxo = float(np.sqrt(max(0.0, self.ema_c * self.ema_o)))
        
        # Current maturity-adjusted utility
        effective_utility = self.ema_delta_loss if self.utility_mode == "delta_loss" else score_cxo
        maturity_scale = min(1.0, max(0.1, self.active_age / float(self.maturity_window)))
        adjusted_utility = effective_utility * maturity_scale
        
        # ----------------------------------------------------
        # LIFECYCLE MANAGEMENT LOGIC
        # ----------------------------------------------------
        if self.oracle_mode == "type":
            # V6: Oracle type (knows exact type None/Linear/Gated)
            target_type = oracle_info.get("oracle_state_type", "NONE") if oracle_info else "NONE"
            if target_type == "NONE":
                if self.active_state is not None:
                    self._evict_active_state(reason="oracle_type_none")
                if self.provisional_state is not None:
                    self.provisional_state = None
            elif target_type in ["LINEAR", "GATED"]:
                if self.active_state is None or self.active_type != target_type:
                    self._evict_active_state(reason="oracle_type_switch")
                    self._instantiate_active_state(target_type)
        else:
            # V3, V4, and V5 (presence)
            # 1. Birth Evaluation
            if self.active_state is None and self.provisional_state is None:
                if self.oracle_mode == "presence":
                    is_needed = (oracle_info.get("oracle_state_type") != "NONE") if oracle_info else False
                    if is_needed:
                        self._trigger_birth(candidate_type="LINEAR", reason="oracle_presence_trigger")
                else:
                    # Autonomous causal birth trigger
                    if self.ema_err_sq > self.birth_threshold and len(self.recent_errs) >= 30:
                        early_err = np.mean(self.recent_errs[:15])
                        late_err = np.mean(self.recent_errs[-15:])
                        rel_progress = (early_err - late_err) / (early_err + 1e-4)
                        if rel_progress < 0.15: # stalled progress
                            self._trigger_birth(candidate_type="LINEAR", reason="causal_persistent_error")
                            
            # 2. Provisional Promotion / Fallback Evaluation (Runs for both V3/V4 and V5)
            if self.provisional_state is not None:
                s_p = self.provisional_state.s
                yh_prov = y_base + self.w_prov * s_p
                prov_gain = (e_base ** 2) - ((y_t - yh_prov) ** 2)
                
                if self.provisional_age >= self.probation_window:
                    # Probation expired: check if useful
                    if prov_gain > self.promote_threshold or abs(self.w_prov) > 0.30:
                        # Promote to active!
                        self._promote_provisional_to_active()
                    else:
                        # Failed probation. If LINEAR failed, fall back to try GATED
                        if self.provisional_type == "LINEAR":
                            self._trigger_birth(candidate_type="GATED", reason="linear_probation_failed")
                        else:
                            # Both failed, return to DORMANT
                            self.provisional_state = None
                            self.provisional_type = None
                            self.provisional_age = 0
                            
            # 3. Eviction Evaluation for Mature Active State
            if self.active_state is not None:
                if self.oracle_mode == "presence":
                    is_needed = (oracle_info.get("oracle_state_type") != "NONE") if oracle_info else False
                    if not is_needed:
                        self._evict_active_state(reason="oracle_presence_evict")
                elif self.active_age >= self.maturity_window:
                    if adjusted_utility < self.evict_threshold:
                        self.low_utility_count += 1
                        if self.low_utility_count >= self.evict_patience:
                            self._evict_active_state(reason="sustained_low_utility")
                    else:
                        self.low_utility_count = max(0, self.low_utility_count - 1)
                    
        return {
            "step": self.total_steps,
            "y_hat": y_hat,
            "y_base": y_base,
            "error": e_t,
            "lifecycle_status": self.get_lifecycle_status(),
            "active_type": self.active_type if self.active_state is not None else "NONE",
            "active_state_val": float(self.active_state.s) if self.active_state is not None else 0.0,
            "w_state": float(self.w_state),
            "c_proxy": float(self.ema_c),
            "o_proxy": float(self.ema_o),
            "cxo_score": float(score_cxo),
            "delta_loss": float(self.ema_delta_loss),
            "adjusted_utility": float(adjusted_utility),
            "flops": float(self.last_step_flops),
            "memory_bytes": self.get_memory_bytes()
        }

    def _trigger_birth(self, candidate_type: str, reason: str):
        """Instantiates a provisional candidate state in shadow mode."""
        self.provisional_type = candidate_type
        self.provisional_age = 0
        self.w_prov = 0.0
        
        if candidate_type == "LINEAR":
            self.provisional_state = LinearScalarState(lr=0.08, init_alpha=0.5, init_b=1.0, init_c=1.0, train_c=False)
        elif candidate_type == "GATED":
            self.provisional_state = GatedScalarState(
                z_dim=2,
                lr=0.10,
                use_sensitivity_trace=True,
                init_bg=-4.0,
                train_bv=False,
                train_c=False
            )
            self.provisional_state.w_g = np.array([6.0, 6.0])
            self.provisional_state.w_v = np.array([1.0, 0.0])
            
        self.birth_events.append({
            "step": self.total_steps,
            "candidate_type": candidate_type,
            "reason": reason
        })

    def _promote_provisional_to_active(self):
        """Promotes provisional state to active prediction."""
        self.active_state = self.provisional_state
        self.active_type = self.provisional_type
        self.w_state = self.w_prov
        self.active_age = self.provisional_age
        self.active_updates = 0
        self.low_utility_count = 0
        
        # Reset provisional slot
        self.provisional_state = None
        self.provisional_type = None
        self.provisional_age = 0

    def _instantiate_active_state(self, state_type: str):
        """Directly instantiates an active state (used by oracle controller)."""
        self.active_type = state_type
        self.active_age = 0
        self.active_updates = 0
        self.w_state = 1.0
        self.low_utility_count = 0
        
        if state_type == "LINEAR":
            self.active_state = LinearScalarState(lr=0.08, init_alpha=0.5, init_b=1.0, init_c=1.0, train_c=False)
        elif state_type == "GATED":
            self.active_state = GatedScalarState(
                z_dim=2,
                lr=0.10,
                use_sensitivity_trace=True,
                init_bg=-4.0,
                train_bv=False,
                train_c=False
            )
            self.active_state.w_g = np.array([6.0, 6.0])
            self.active_state.w_v = np.array([1.0, 0.0])

    def _evict_active_state(self, reason: str):
        """Evicts active state, deleting parameters, memory, and sensitivities."""
        if self.active_state is not None:
            self.eviction_events.append({
                "step": self.total_steps,
                "evicted_type": self.active_type,
                "age_at_eviction": self.active_age,
                "reason": reason
            })
        self.active_state = None
        self.active_type = None
        self.w_state = 0.0
        self.active_age = 0
        self.active_updates = 0
        self.low_utility_count = 0
        self.ema_c = 0.0
        self.ema_o = 0.0
        self.ema_delta_loss = 0.0
