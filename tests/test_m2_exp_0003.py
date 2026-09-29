import pytest
import numpy as np
from src.env.necessity_diagnostic_stream import (
    LongDelayStream,
    DistributedIntegrationStream,
    FiniteStateMemoryStream,
    ContextDependentRuleStream
)
from src.utils.temporal_buffer import TemporalRingBuffer, pair_to_cand, cand_to_pair

def test_long_delay_stream_correctness():
    """Verify Stage A stream generates exact delayed dependencies up to d*=500 without future leakage."""
    for delay in [10, 50, 500]:
        cfg = {
            "d_features": 10,
            "true_delay": delay,
            "true_feature": 0,
            "beta": 1.0,
            "noise_std": 0.0,
            "total_steps": delay + 50
        }
        stream = LongDelayStream(cfg, seed=42)
        xs = []
        ys = []
        while stream.has_next():
            x_t, y_t, true_pair, true_cand = stream.step()
            xs.append(x_t[0])
            ys.append(y_t)
            
        assert len(ys) == delay + 50
        # Check initial steps <= delay are zero
        for t in range(delay):
            assert ys[t] == 0.0, f"Expected zero target before delay elapsed at t={t}"
            
        # Check steps > delay match exactly
        for t in range(delay, len(ys)):
            expected = xs[t - delay]
            np.testing.assert_allclose(ys[t], expected, atol=1e-7)

def test_distributed_integration_recurrence():
    """Verify Stage B stream exactly follows s_t = lambda * s_{t-1} + x_{0, t}."""
    for decay in [0.5, 0.8, 0.95]:
        cfg = {
            "d_features": 10,
            "driving_feature": 0,
            "decay": decay,
            "noise_std": 0.0,
            "total_steps": 100
        }
        stream = DistributedIntegrationStream(cfg, seed=123)
        xs = []
        ss = []
        while stream.has_next():
            x_t, y_t, s_t = stream.step()
            xs.append(x_t[0])
            ss.append(s_t)
            assert y_t == s_t
            
        # Manually verify convolution expansion
        for t in range(len(ss)):
            expected_s = sum((decay ** k) * xs[t - k] for k in range(t + 1))
            np.testing.assert_allclose(ss[t], expected_s, atol=1e-7)

def test_finite_state_memory_set_reset():
    """Verify Stage C SET/RESET retains state indefinitely until overwritten."""
    cfg = {
        "d_features": 10,
        "mode": "set_reset",
        "p_event": 0.1,
        "noise_std": 0.0,
        "total_steps": 500
    }
    stream = FiniteStateMemoryStream(cfg, seed=777)
    prev_s = 0.0
    while stream.has_next():
        x_t, y_t, s_t = stream.step()
        assert y_t == s_t
        if x_t[0] == 1.0:
            assert s_t == 1.0
        elif x_t[1] == 1.0:
            assert s_t == 0.0
        else:
            assert s_t == prev_s
        prev_s = s_t

def test_finite_state_memory_xor_parity():
    """Verify Stage C XOR/parity correctly flips on events and retains parity."""
    cfg = {
        "d_features": 10,
        "mode": "xor_parity",
        "p_event": 0.1,
        "noise_std": 0.0,
        "total_steps": 500
    }
    stream = FiniteStateMemoryStream(cfg, seed=888)
    prev_s = 0.0
    while stream.has_next():
        x_t, y_t, s_t = stream.step()
        assert y_t == s_t
        if x_t[0] == 1.0:
            assert s_t == 1.0 - prev_s
        else:
            assert s_t == prev_s
        prev_s = s_t

def test_context_dependent_rule_causality():
    """Verify Stage D mode switching and delayed targeting match mode semantics."""
    cfg = {
        "d_features": 10,
        "delay_a": 2,
        "delay_b": 7,
        "signal_feature": 2,
        "p_switch": 0.05,
        "noise_std": 0.0,
        "total_steps": 500
    }
    stream = ContextDependentRuleStream(cfg, seed=999)
    sig_history = []
    t = 0
    while stream.has_next():
        x_t, y_t, mode = stream.step()
        t += 1
        sig_history.append(x_t[2])
        active_delay = 2 if mode == 0 else 7
        if t <= active_delay:
            assert y_t == 0.0
        else:
            expected = sig_history[t - 1 - active_delay]
            np.testing.assert_allclose(y_t, expected, atol=1e-7)

def test_temporal_ring_buffer_large_horizon():
    """Verify TemporalRingBuffer functions correctly for L_max = 500."""
    d = 10
    l_max = 500
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    assert buf.get_memory_bytes() == 501 * 10 * 8 # 40,080 bytes
    
    rng = np.random.RandomState(42)
    inputs = []
    for step in range(600):
        x = rng.randn(d)
        inputs.append(x)
        buf.push(x)
        
        # Test random lag checks
        if step >= 500:
            for test_lag in [0, 10, 50, 100, 250, 500]:
                expected = inputs[step - test_lag]
                retrieved = buf.get_lag(test_lag)
                np.testing.assert_array_equal(retrieved, expected)

def test_no_future_leakage():
    """Verify that no stream or buffer allows any future observation to be accessed."""
    # Check buffer bounds
    buf = TemporalRingBuffer(d=5, l_max=20)
    with pytest.raises(ValueError):
        buf.get_lag(-1)
    with pytest.raises(ValueError):
        buf.get_lag(21)
        
    # Check that t <= lag returns zeros
    buf.push(np.ones(5))
    lag10 = buf.get_lag(10)
    np.testing.assert_array_equal(lag10, np.zeros(5))
