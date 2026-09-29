import pytest
import numpy as np
from src.models.minimal_state import LinearScalarState, GatedScalarState, ContextLagRouter

def test_linear_scalar_finite_difference_gradient():
    """
    Section 115 Test: Verify that forward sensitivity-derived gradients
    match numerical finite-difference gradients on short synthetic sequences.
    """
    rng = np.random.RandomState(42)
    T = 5
    xs = rng.randn(T)
    ys = rng.randn(T)
    
    eps = 1e-5
    
    # We will test parameter b
    # Compute analytical gradient via forward sensitivity accumulation
    model = LinearScalarState(init_alpha=0.5, init_b=1.2, init_c=1.0)
    analytic_grad_b = 0.0
    for t in range(T):
        s_t, y_hat, a_t = model.forward(xs[t])
        e_t = ys[t] - y_hat
        # Loss is 0.5 * e_t^2, dL/db = - e_t * c * p_b
        analytic_grad_b += - e_t * model.c * model.p_b
        
    # Compute numerical gradient via central finite difference
    def compute_loss(b_val):
        m = LinearScalarState(init_alpha=0.5, init_b=b_val, init_c=1.0)
        total_loss = 0.0
        for t in range(T):
            _, yh, _ = m.forward(xs[t])
            total_loss += 0.5 * (ys[t] - yh) ** 2
        return total_loss
        
    loss_plus = compute_loss(1.2 + eps)
    loss_minus = compute_loss(1.2 - eps)
    num_grad_b = (loss_plus - loss_minus) / (2.0 * eps)
    
    np.testing.assert_allclose(analytic_grad_b, num_grad_b, rtol=1e-3, atol=1e-3)

def test_gated_scalar_finite_difference_gradient():
    """
    Section 115 Test: Verify R4 gated forward sensitivity gradients
    match numerical finite differences on short synthetic sequences.
    """
    rng = np.random.RandomState(123)
    T = 6
    zs = rng.randn(T, 2)
    ys = rng.randn(T)
    eps = 1e-5
    
    # Test w_g[0]
    base_wg0 = 0.5
    model = GatedScalarState(z_dim=2, use_sensitivity_trace=True, init_bg=-0.5)
    model.w_g[0] = base_wg0
    model.w_v[0] = 1.0
    
    analytic_grad_wg0 = 0.0
    for t in range(T):
        s_t, y_hat, g_t = model.forward(zs[t])
        e_t = ys[t] - y_hat
        analytic_grad_wg0 += - e_t * model.c * model.p_wg[0]
        
    def compute_loss(wg0_val):
        m = GatedScalarState(z_dim=2, use_sensitivity_trace=True, init_bg=-0.5)
        m.w_g[0] = wg0_val
        m.w_v[0] = 1.0
        total_loss = 0.0
        for t in range(T):
            _, yh, _ = m.forward(zs[t])
            total_loss += 0.5 * (ys[t] - yh) ** 2
        return total_loss
        
    num_grad_wg0 = (compute_loss(base_wg0 + eps) - compute_loss(base_wg0 - eps)) / (2.0 * eps)
    np.testing.assert_allclose(analytic_grad_wg0, num_grad_wg0, rtol=1e-3, atol=1e-3)

def test_stability_zero_input():
    """
    Section 116 Test: Run 10,000 zero-input steps and verify state does not explode.
    """
    model = LinearScalarState(init_alpha=1.5, init_b=1.0) # a approx 0.905
    model.s = 1.0
    for _ in range(10000):
        s_t, _, _ = model.forward(0.0)
        assert np.isfinite(s_t)
        assert abs(s_t) <= 1.0 # strictly decaying to 0
    assert abs(model.s) < 1e-12

def test_retention_none_events():
    """
    Section 117 Test: After SET event, feed 10,000 NONE events (z=0)
    and verify retained state remains intact.
    """
    model = GatedScalarState(z_dim=2, use_sensitivity_trace=True, init_bg=-4.0)
    # Set weights to act as clean SET/RESET latch
    model.w_g = np.array([5.0, 5.0])
    model.b_g = -3.0 # gate is sigmoid(-3) approx 0.047 during NONE
    model.w_v = np.array([1.0, 0.0])
    
    # 1. SET event
    set_z = np.array([1.0, 0.0])
    s_set, _, g_set = model.forward(set_z)
    assert g_set > 0.85
    assert s_set > 0.85
    
    # 2. 10,000 NONE events with zero gate
    model.b_g = -10.0 # near zero gate: sigmoid(-10) approx 4.5e-5
    none_z = np.array([0.0, 0.0])
    for _ in range(10000):
        s_t, _, g_t = model.forward(none_z)
        
    # State should remain virtually intact
    assert s_t > 0.5
    assert np.isfinite(s_t)

def test_r3_r4_forward_identity():
    """
    Verify that R3 and R4 produce bit-for-bit identical forward states
    given identical inputs and parameters.
    """
    rng = np.random.RandomState(999)
    zs = rng.randn(100, 2)
    
    r3 = GatedScalarState(z_dim=2, use_sensitivity_trace=False, init_bg=-1.0)
    r4 = GatedScalarState(z_dim=2, use_sensitivity_trace=True, init_bg=-1.0)
    
    for t in range(100):
        s3, yh3, g3 = r3.forward(zs[t])
        s4, yh4, g4 = r4.forward(zs[t])
        assert s3 == s4
        assert yh3 == yh4
        assert g3 == g4

def test_state_dimension_strictly_one():
    """
    Verify that internal state is strictly a 1D scalar float.
    """
    r2 = LinearScalarState()
    s2, _, _ = r2.forward(1.0)
    assert isinstance(s2, float)
    
    r3 = GatedScalarState(z_dim=2)
    s3, _, _ = r3.forward(np.array([1.0, 0.0]))
    assert isinstance(s3, float)
