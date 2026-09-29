import pytest
import numpy as np
from src.utils.temporal_buffer import TemporalRingBuffer, pair_to_cand, cand_to_pair
from src.env.delayed_sparse_stream import DelayedSparseLinearStream
from src.policies.temporal_rate_policy import TemporalRatePolicy
from src.learners.tiered_evidence_learner import TieredEvidenceLearner

def test_multi_delay_stream_target_correctness():
    """Verify that DelayedSparseLinearStream computes sum_{m=1}^M beta_m * x_{j_m, t-d_m} exactly."""
    d = 10
    l_max = 8
    cfg = {
        "d_features": d,
        "l_max": l_max,
        "noise_std": 0.0,
        "total_steps": 30,
        "true_pairs": [(2, 1), (5, 4), (8, 7)],
        "betas": [1.0, 2.0, 0.5]
    }
    env = DelayedSparseLinearStream(cfg, seed=42)
    
    history_x = []
    for t in range(1, 31):
        x_t, y_t, true_pairs, true_cands = env.step()
        history_x.append(x_t)
        
        assert true_pairs == [(2, 1), (5, 4), (8, 7)]
        assert true_cands == [pair_to_cand(2, 1, d), pair_to_cand(5, 4, d), pair_to_cand(8, 7, d)]
        
        expected_y = 0.0
        # Term 1: feat 2 at lag 1
        if t > 1:
            expected_y += 1.0 * history_x[t - 1 - 1][2]
        # Term 2: feat 5 at lag 4
        if t > 4:
            expected_y += 2.0 * history_x[t - 1 - 4][5]
        # Term 3: feat 8 at lag 7
        if t > 7:
            expected_y += 0.5 * history_x[t - 1 - 7][8]
            
        assert abs(y_t - expected_y) < 1e-12, f"Target mismatch at step {t}: y_t={y_t}, expected={expected_y}"

def test_same_feature_multi_lag_correctness():
    """Verify that DelayedSparseLinearStream correctly supports the same feature at multiple distinct lags."""
    d = 10
    l_max = 6
    j_star = 4
    cfg = {
        "d_features": d,
        "l_max": l_max,
        "noise_std": 0.0,
        "total_steps": 25,
        "true_pairs": [(j_star, 2), (j_star, 5)],
        "betas": [1.2, -0.8]
    }
    env = DelayedSparseLinearStream(cfg, seed=100)
    
    history_x = []
    for t in range(1, 26):
        x_t, y_t, true_pairs, true_cands = env.step()
        history_x.append(x_t)
        
        expected_y = 0.0
        if t > 2:
            expected_y += 1.2 * history_x[t - 1 - 2][j_star]
        if t > 5:
            expected_y += -0.8 * history_x[t - 1 - 5][j_star]
            
        assert abs(y_t - expected_y) < 1e-12, f"Same-feature multi-lag mismatch at step {t}!"

def test_section_83_aliasing_sanity():
    """
    SECTION 83 ALIASING SANITY TEST:
    Verify that AR(1) process has expected empirical autocorrelation:
    - For rho=0: lag covariance near diagonal (|rho_1| < 0.05).
    - For rho=0.9: adjacent lag correlation in [0.88, 0.92] and lag-2 correlation in [0.78, 0.84].
    - Unit marginal variance Var(x_{j, t}) approx 1.0.
    """
    d = 5
    n_steps = 10000
    
    # Test rho = 0.0
    cfg_white = {"d_features": d, "noise_std": 0.1, "total_steps": n_steps, "rho": 0.0, "true_pairs": [(0, 0)]}
    env_white = DelayedSparseLinearStream(cfg_white, seed=2024)
    xs_white = np.array([env_white.step()[0] for _ in range(n_steps)])
    
    var_white = np.var(xs_white, axis=0)
    np.testing.assert_allclose(var_white, np.ones(d), atol=0.06)
    
    corr_white_lag1 = np.corrcoef(xs_white[:-1, 0], xs_white[1:, 0])[0, 1]
    assert abs(corr_white_lag1) < 0.05, f"rho=0 correlation too high: {corr_white_lag1}"
    
    # Test rho = 0.9
    cfg_ar = {"d_features": d, "noise_std": 0.1, "total_steps": n_steps, "rho": 0.9, "true_pairs": [(0, 0)]}
    env_ar = DelayedSparseLinearStream(cfg_ar, seed=2024)
    xs_ar = np.array([env_ar.step()[0] for _ in range(n_steps)])
    
    var_ar = np.var(xs_ar, axis=0)
    np.testing.assert_allclose(var_ar, np.ones(d), atol=0.15)
    
    corr_ar_lag1 = np.corrcoef(xs_ar[:-1, 0], xs_ar[1:, 0])[0, 1]
    corr_ar_lag2 = np.corrcoef(xs_ar[:-2, 0], xs_ar[2:, 0])[0, 1]
    
    assert 0.88 <= corr_ar_lag1 <= 0.92, f"rho=0.9 lag-1 correlation outside [0.88, 0.92]: {corr_ar_lag1}"
    assert 0.78 <= corr_ar_lag2 <= 0.84, f"rho=0.9 lag-2 correlation outside [0.78, 0.84]: {corr_ar_lag2}"

def test_zero_future_leakage_multi_delay():
    """Verify that buffer never exposes future inputs at any step t under multi-delay stream."""
    d = 6
    l_max = 5
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    
    inputs = [np.random.randn(d) for _ in range(20)]
    for t, x in enumerate(inputs):
        buf.push(x)
        flat = buf.get_flat_vector()
        
        # Check that none of future inputs (t+1 .. 19) appear in buffer
        for future_t in range(t + 1, 20):
            future_x = inputs[future_t]
            for lag in range(l_max + 1):
                lag_x = buf.get_lag(lag)
                assert not np.array_equal(lag_x, future_x)
            for lag in range(l_max + 1):
                slice_x = flat[lag * d : (lag + 1) * d]
                assert not np.array_equal(slice_x, future_x)

def test_variant_u4_oracle_features():
    """Verify that Variant U4 restricts candidate pool strictly to oracle_features across all lags."""
    d = 20
    l_max = 10
    oracle_feats = {3, 7}
    policy = TemporalRatePolicy(
        d_features=d,
        l_max=l_max,
        variant="U4",
        oracle_features=oracle_feats
    )
    
    # Total candidates for 2 features across 11 lags = 2 * 11 = 22
    assert len(policy.allowed_candidates) == 22
    for c in policy.allowed_candidates:
        j, ell = cand_to_pair(c, d)
        assert j in oracle_feats
        assert 0 <= ell <= l_max
        
    # Test selection
    cands = policy.select_candidates(d=policy.total_candidates, active_support=set(), q=5)
    assert len(cands) == 5
    for c in cands:
        j, _ = cand_to_pair(c, d)
        assert j in oracle_feats

def test_variant_u5_oracle_lags():
    """Verify that Variant U5 restricts candidate pool strictly to oracle_lags across all features."""
    d = 20
    l_max = 10
    oracle_lags = {2, 7}
    policy = TemporalRatePolicy(
        d_features=d,
        l_max=l_max,
        variant="U5",
        oracle_lags=oracle_lags
    )
    
    # Total candidates for 20 features across 2 lags = 20 * 2 = 40
    assert len(policy.allowed_candidates) == 40
    for c in policy.allowed_candidates:
        j, ell = cand_to_pair(c, d)
        assert 0 <= j < d
        assert ell in oracle_lags
        
    cands = policy.select_candidates(d=policy.total_candidates, active_support=set(), q=5)
    assert len(cands) == 5
    for c in cands:
        _, ell = cand_to_pair(c, d)
        assert ell in oracle_lags

def test_variant_u6_oracle_full_set():
    """Verify that Variant U6 disables exploration probes (returns 0 probes)."""
    d = 20
    l_max = 10
    policy = TemporalRatePolicy(
        d_features=d,
        l_max=l_max,
        variant="U6"
    )
    assert len(policy.cold_queue) == 0
    assert len(policy.allowed_candidates) == 0
    cands = policy.select_candidates(d=policy.total_candidates, active_support={pair_to_cand(1, 2, d)}, q=5)
    assert len(cands) == 0

def test_dynamic_multi_delay_shift():
    """Verify that dynamic transitions accurately swap active true pairs at shift_step."""
    d = 8
    l_max = 5
    cfg = {
        "d_features": d,
        "l_max": l_max,
        "noise_std": 0.0,
        "total_steps": 20,
        "shift_step": 10,
        "true_pairs": [(1, 2), (3, 4)],
        "regime_2_pairs": [(1, 1), (5, 3)],
        "betas": [1.0, 1.0],
        "regime_2_betas": [1.0, 1.0]
    }
    env = DelayedSparseLinearStream(cfg, seed=555)
    
    for t in range(1, 21):
        x_t, y_t, true_pairs, true_cands = env.step()
        if t <= 10:
            assert true_pairs == [(1, 2), (3, 4)]
        else:
            assert true_pairs == [(1, 1), (5, 3)]
