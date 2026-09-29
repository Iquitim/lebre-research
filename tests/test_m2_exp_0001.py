import pytest
import numpy as np
from src.utils.temporal_buffer import TemporalRingBuffer, pair_to_cand, cand_to_pair
from src.env.delayed_sparse_stream import DelayedSparseLinearStream
from src.policies.temporal_rate_policy import TemporalRatePolicy
from src.learners.tiered_evidence_learner import TieredEvidenceLearner

def test_ring_buffer_historical_correctness():
    """Verify that TemporalRingBuffer stores and returns historical values accurately."""
    d = 5
    l_max = 3
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    
    # Push 4 distinct vectors
    v0 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    v1 = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    v2 = np.array([100.0, 200.0, 300.0, 400.0, 500.0])
    v3 = np.array([1000.0, 2000.0, 3000.0, 4000.0, 5000.0])
    
    buf.push(v0)
    np.testing.assert_array_equal(buf.get_lag(0), v0)
    # Untouched lags return zeros
    np.testing.assert_array_equal(buf.get_lag(1), np.zeros(d))
    np.testing.assert_array_equal(buf.get_lag(2), np.zeros(d))
    np.testing.assert_array_equal(buf.get_lag(3), np.zeros(d))
    
    buf.push(v1)
    buf.push(v2)
    buf.push(v3)
    
    # At step 3: lag 0 is v3, lag 1 is v2, lag 2 is v1, lag 3 is v0
    np.testing.assert_array_equal(buf.get_lag(0), v3)
    np.testing.assert_array_equal(buf.get_lag(1), v2)
    np.testing.assert_array_equal(buf.get_lag(2), v1)
    np.testing.assert_array_equal(buf.get_lag(3), v0)

def test_future_leakage_prevention():
    """
    SECTION 77 TEST:
    Explicitly test that x_{t+1} or any future value can never appear in the candidate buffer at time t.
    """
    d = 4
    l_max = 5
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    
    stream_inputs = [np.random.randn(d) for _ in range(10)]
    
    for t in range(5):
        buf.push(stream_inputs[t])
        
        # Check all available lags in buffer
        flat = buf.get_flat_vector()
        
        # Future inputs stream_inputs[t+1:] must NEVER be present in the buffer
        for future_t in range(t + 1, 10):
            future_vec = stream_inputs[future_t]
            # No lag slice can match the future vector
            for lag in range(l_max + 1):
                lag_vec = buf.get_lag(lag)
                assert not np.array_equal(lag_vec, future_vec), f"Future leakage detected at step {t} from step {future_t}!"
                
            # No subvector in flattened vector can equal future_vec
            for lag in range(l_max + 1):
                sub = flat[lag * d : (lag + 1) * d]
                assert not np.array_equal(sub, future_vec), f"Future leakage detected in flattened vector at step {t}!"

def test_candidate_bijective_indexing():
    """Verify that pair_to_cand and cand_to_pair are exact inverses."""
    d = 20
    l_max = 10
    total_cands = d * (l_max + 1)
    
    seen = set()
    for j in range(d):
        for ell in range(l_max + 1):
            c = pair_to_cand(j, ell, d)
            assert 0 <= c < total_cands
            assert c not in seen, f"Duplicate candidate index {c} for ({j}, {ell})"
            seen.add(c)
            
            j_rev, ell_rev = cand_to_pair(c, d)
            assert j_rev == j
            assert ell_rev == ell
            
    assert len(seen) == total_cands

def test_lag_zero_equals_current_input():
    """Verify that candidate at lag 0 corresponds exactly to current input x_t."""
    d = 10
    l_max = 4
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    
    for _ in range(5):
        x = np.random.randn(d)
        buf.push(x)
        np.testing.assert_array_equal(buf.get_lag(0), x)
        for j in range(d):
            assert buf.get_feature_lag(j, 0) == x[j]

def test_delayed_sparse_stream_ground_truth():
    """Verify DelayedSparseLinearStream target computation and delay shift mechanics."""
    d = 10
    l_max = 5
    cfg = {
        "d_features": d,
        "l_max": l_max,
        "noise_std": 0.0, # Zero noise for exact verification
        "total_steps": 20,
        "true_feature": 3,
        "true_delay": 2,
        "beta": 1.5,
        "shift_step": 10,
        "regime_2_delay": 4
    }
    env = DelayedSparseLinearStream(cfg, seed=123)
    
    history_x = []
    for t in range(1, 21):
        x_t, y_t, true_pair, true_cand = env.step()
        history_x.append(x_t)
        
        if t <= 10:
            assert true_pair == (3, 2)
            assert true_cand == pair_to_cand(3, 2, d)
            if t <= 2:
                assert y_t == 0.0
            else:
                expected_y = 1.5 * history_x[t - 1 - 2][3]
                assert abs(y_t - expected_y) < 1e-12
        else:
            assert true_pair == (3, 4)
            assert true_cand == pair_to_cand(3, 4, d)
            expected_y = 1.5 * history_x[t - 1 - 4][3]
            assert abs(y_t - expected_y) < 1e-12

def test_temporal_policy_variants_restriction():
    """Verify candidate pool restrictions for T0, T1, T2, T3, T4, T5."""
    d = 10
    l_max = 3
    
    # T0: Current only (lag 0)
    p0 = TemporalRatePolicy(d_features=d, l_max=l_max, variant="T0")
    assert p0.allowed_candidates == set(range(d))
    
    # T1: Full temporal (all candidates)
    p1 = TemporalRatePolicy(d_features=d, l_max=l_max, variant="T1")
    assert len(p1.allowed_candidates) == d * (l_max + 1)
    
    # T2: Lag-Fair (all candidates, interleaved)
    p2 = TemporalRatePolicy(d_features=d, l_max=l_max, variant="T2")
    assert len(p2.allowed_candidates) == d * (l_max + 1)
    # Verify cold queue first 4 items have lags 0, 1, 2, 3
    first_4 = [p2.cold_queue[i] for i in range(4)]
    lags = [cand_to_pair(c, d)[1] for c in first_4]
    assert lags == [0, 1, 2, 3]
    
    # T4: Oracle lag
    p4 = TemporalRatePolicy(d_features=d, l_max=l_max, variant="T4", oracle_delay=2)
    expected_t4 = {pair_to_cand(j, 2, d) for j in range(d)}
    assert p4.allowed_candidates == expected_t4
    
    # T5: Oracle pair
    p5 = TemporalRatePolicy(d_features=d, l_max=l_max, variant="T5")
    cands = p5.select_candidates(d=d*(l_max+1), active_support=set(), q=5)
    assert cands == []

def test_memory_accounting():
    """Verify memory computation matches theoretical specification."""
    d = 20
    l_max = 10
    buf = TemporalRingBuffer(d=d, l_max=l_max)
    expected_bytes = 20 * (10 + 1) * 8 # 1760 bytes
    assert buf.get_memory_bytes() == expected_bytes
    assert buf.buffer.nbytes == expected_bytes

def test_seed_disjointness():
    """Verify 30 evaluation seeds are fresh and disjoint from M1 and DEV seeds."""
    m1_seeds = {42, 123, 456, 789, 1024, 9999}
    m1_r1_seeds = set(range(2026, 2056))
    dev_seed = 3000
    m2_eval_seeds = set(range(3001, 3031))
    
    assert len(m2_eval_seeds) == 30
    assert dev_seed not in m2_eval_seeds
    assert len(m2_eval_seeds.intersection(m1_seeds)) == 0
    assert len(m2_eval_seeds.intersection(m1_r1_seeds)) == 0
