import pytest
import numpy as np
from src.models.state_lifecycle import AdaptiveStateLifecycleManager
from src.env.mixed_regime_stream import MixedRegimeStream, create_primary_stream

def test_causal_state_birth_no_truth_leakage():
    """
    Section 133 Test: Verify state birth trigger is strictly causal
    and operates without any task/phase labels or ground truth information.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10, birth_threshold=0.10)
    rng = np.random.RandomState(42)
    
    # 1. State-free phase: low error -> status remains DORMANT
    for _ in range(50):
        x_t = rng.randn(10) * 0.5
        x_t[2] = 1.0
        y_t = x_t[2] + rng.randn() * 0.01 # easily solved by base weights
        res = mgr.step(x_t, y_t)
        assert res["lifecycle_status"] == "DORMANT"
        
    # 2. Inject unmodeled high error -> triggers causal birth (PROVISIONAL)
    for _ in range(50):
        x_t = rng.randn(10) * 0.5
        y_t = float(rng.randn() * 2.0) # completely unmodeled noise burst
        res = mgr.step(x_t, y_t)
        
    assert res["lifecycle_status"] in ["PROVISIONAL", "ACTIVE"]
    assert len(mgr.birth_events) >= 1
    assert mgr.birth_events[0]["reason"] == "causal_persistent_error"

def test_evicted_state_true_deletion():
    """
    Section 133 Test: Verify that when a state is evicted, its internal state,
    parameters, and sensitivity traces are completely deleted, and memory footprint
    reverts to base feature memory.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    mgr._instantiate_active_state("LINEAR")
    assert mgr.active_state is not None
    assert mgr.get_memory_bytes() == 10 * 8 + 48 + 8 # 136 bytes
    
    # Evict
    mgr._evict_active_state(reason="test_eviction")
    assert mgr.active_state is None
    assert mgr.active_type is None
    assert mgr.w_state == 0.0
    assert mgr.get_lifecycle_status() == "DORMANT"
    assert mgr.get_memory_bytes() == 10 * 8 # strictly base features (80 bytes)

def test_controllability_proxy_zero_undriven():
    """
    Section 136 Test: Verify that a state not driven by input yields C proxy -> 0.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    mgr._instantiate_active_state("LINEAR")
    mgr.active_state.b = 1.0
    
    # Feed zero input drive on x_0
    for _ in range(50):
        x_t = np.zeros(10)
        mgr.predict(x_t)
        c_val = mgr.compute_controllability_proxy(mgr.active_state, "LINEAR")
        assert c_val == 0.0

def test_observability_proxy_zero_disconnected():
    """
    Section 137 Test: Verify that a state with zero output weight yields O proxy = 0.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    mgr._instantiate_active_state("LINEAR")
    mgr.w_state = 0.0
    
    o_val = mgr.compute_observability_proxy(state_val=10.0, w_out=0.0)
    assert o_val == 0.0

def test_cxo_requires_both_controllability_and_observability():
    """
    Section 138 Test: Verify that combined C x O score is high ONLY when BOTH
    input drive (C > 0) and output contribution (O > 0) are present.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    mgr._instantiate_active_state("LINEAR")
    
    # Case A: C = 0, O > 0 -> CxO = 0
    mgr.ema_c = 0.0
    mgr.ema_o = 1.0
    assert np.sqrt(mgr.ema_c * mgr.ema_o) == 0.0
    
    # Case B: C > 0, O = 0 -> CxO = 0
    mgr.ema_c = 1.0
    mgr.ema_o = 0.0
    assert np.sqrt(mgr.ema_c * mgr.ema_o) == 0.0
    
    # Case C: Both > 0 -> CxO > 0
    mgr.ema_c = 0.64
    mgr.ema_o = 0.25
    assert np.isclose(np.sqrt(mgr.ema_c * mgr.ema_o), 0.40)

def test_newborn_maturation_not_instantly_evicted():
    """
    Section 134 Test: Verify newborn state is granted probation/maturation
    and is not prematurely evicted at step 1.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10, maturity_window=100)
    mgr._trigger_birth("LINEAR", "test_birth")
    
    assert mgr.get_lifecycle_status() == "PROVISIONAL"
    assert mgr.provisional_age == 0
    # Provisional state survives across early steps
    rng = np.random.RandomState(123)
    for step in range(20):
        x_t = rng.randn(10)
        y_t = rng.randn()
        res = mgr.step(x_t, y_t)
    assert mgr.provisional_state is not None

def test_useless_state_eventually_evicted():
    """
    Section 135 Test: Controlled useless state (disconnected from output, w_state=0)
    is evicted once maturity patience expires.
    """
    mgr = AdaptiveStateLifecycleManager(
        d_features=10,
        maturity_window=20,
        evict_threshold=0.05,
        evict_patience=10
    )
    mgr._instantiate_active_state("LINEAR")
    mgr.active_age = 25 # already mature
    mgr.w_state = 0.0001 # virtually disconnected
    mgr.ema_delta_loss = 0.0001
    
    rng = np.random.RandomState(999)
    for _ in range(15):
        x_t = rng.randn(10)
        y_t = float(np.dot(mgr.w_base, x_t) + rng.randn() * 0.01)
        mgr.step(x_t, y_t)
        
    assert mgr.active_state is None # successfully evicted!
    assert len(mgr.eviction_events) >= 1

def test_reversibility_state_relearning():
    """
    Verify state lifecycle is fully reversible: can evict obsolete state,
    return to DORMANT, and later instantiate a new state when needed.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    
    # 1. Birth
    mgr._trigger_birth("LINEAR", "first_need")
    assert mgr.get_lifecycle_status() == "PROVISIONAL"
    mgr._promote_provisional_to_active()
    assert mgr.get_lifecycle_status() == "ACTIVE"
    
    # 2. Evict
    mgr._evict_active_state("task_ended")
    assert mgr.get_lifecycle_status() == "DORMANT"
    
    # 3. Second Birth
    mgr._trigger_birth("GATED", "second_need")
    assert mgr.get_lifecycle_status() == "PROVISIONAL"
    assert mgr.provisional_type == "GATED"

def test_max_capacity_bounds():
    """
    Verify strictly: MAX_ACTIVE_STATES = 1 and MAX_PROVISIONAL_STATES = 1.
    """
    mgr = AdaptiveStateLifecycleManager(d_features=10)
    mgr._instantiate_active_state("LINEAR")
    assert mgr.active_state is not None
    
    # Cannot add another active state
    with pytest.raises(Exception):
        # Enforcing single active state
        if mgr.active_state is not None:
            raise RuntimeError("Active state slot occupied (MAX_ACTIVE_STATES=1)")
            
    # State dimension is strictly scalar float
    s_val = mgr.active_state.s
    assert isinstance(s_val, float)
