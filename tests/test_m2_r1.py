import unittest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../experiments/M2-R1")))

from run_m2_r1 import (
    ParetoLifecycleManager,
    create_canonical_stream,
    compute_roc_auc_numpy,
    compute_pr_auc_numpy
)


class TestM2R1(unittest.TestCase):
    def test_seed_disjointness(self):
        """Verify calibration, validation, and holdout seed sets are strictly disjoint."""
        import json
        config_path = os.path.join(os.path.dirname(__file__), "../experiments/M2-R1/config.json")
        with open(config_path) as f:
            cfg = json.load(f)
        cal = set(cfg["calibration_seeds"])
        val = set(cfg["validation_seeds"])
        hold = set(cfg["holdout_seeds"])
        
        self.assertEqual(len(cal.intersection(val)), 0, "Calibration and Validation seeds overlap!")
        self.assertEqual(len(cal.intersection(hold)), 0, "Calibration and Holdout seeds overlap!")
        self.assertEqual(len(val.intersection(hold)), 0, "Validation and Holdout seeds overlap!")
        self.assertEqual(len(cal), 10)
        self.assertGreaterEqual(len(val), 30)
        self.assertGreaterEqual(len(hold), 30)

    def test_never_evict_control(self):
        """Verify F_NEVER_EVICT never calls eviction once active."""
        p_cfg = {"name": "F_NEVER_EVICT", "type": "CONTROL"}
        mgr = ParetoLifecycleManager(d_features=10, policy_config=p_cfg)
        from src.models.minimal_state import GatedScalarState
        mgr.active_state = GatedScalarState(z_dim=2)
        mgr.active_type = "GATED"
        mgr.w_state = 1.0
        mgr.active_age = 200 # mature

        # Feed 100 steps of pure zero state-free noise
        for _ in range(100):
            x = np.zeros(10)
            y = 0.0
            info = {"oracle_state_type": "NONE", "regime_type": "STATE_FREE", "phase_idx": 0}
            mgr.step(x, y, oracle_info=info)

        self.assertIsNotNone(mgr.active_state)
        self.assertEqual(mgr.eviction_count, 0)

    def test_timeout_control(self):
        """Verify F_TIMEOUT evicts after fixed timeout steps of quiescence."""
        p_cfg = {"name": "F_TIMEOUT", "type": "CONTROL", "timeout_steps": 30}
        mgr = ParetoLifecycleManager(d_features=10, policy_config=p_cfg)
        from src.models.minimal_state import GatedScalarState
        mgr.active_state = GatedScalarState(z_dim=2)
        mgr.active_type = "GATED"
        mgr.w_state = 1.0
        mgr.active_age = 200

        # Feed 35 steps of quiescence (x=0, y=0)
        for _ in range(35):
            x = np.zeros(10)
            y = 0.0
            info = {"oracle_state_type": "GATED", "regime_type": "GATED_NECESSARY", "phase_idx": 0}
            mgr.step(x, y, oracle_info=info)

        # F_TIMEOUT should have evicted after 30 quiescent steps
        self.assertIsNone(mgr.active_state)
        self.assertEqual(mgr.eviction_count, 1)

    def test_reconciled_eviction_latency(self):
        """Verify eviction latency correctly accounts for stale retention post-boundary."""
        p_cfg = {"name": "P2_Balanced", "type": "CANDIDATE", "alpha_slow": 0.005, "theta_obs": 1.0, "patience_obs": 10, "k_ret": 0.5, "theta_ret": 0.05}
        mgr = ParetoLifecycleManager(d_features=10, policy_config=p_cfg)
        from src.models.minimal_state import GatedScalarState
        mgr.active_state = GatedScalarState(z_dim=2)
        mgr.active_type = "GATED"
        mgr.w_state = 0.05
        mgr.active_age = 200
        mgr.temporal_c = 0.01
        mgr.temporal_o = 0.0025 # cxo <= 0.05

        # Phase 0: Needed
        mgr.step(np.zeros(10), 0.0, oracle_info={"oracle_state_type": "GATED", "regime_type": "GATED_NECESSARY", "phase_idx": 0})
        
        # Phase 1: Boundary to STATE_FREE at step 2
        for _ in range(25):
            mgr.step(np.zeros(10), 0.0, oracle_info={"oracle_state_type": "NONE", "regime_type": "STATE_FREE", "phase_idx": 1})

        # Eviction should have occurred with latency > 0
        self.assertGreater(len(mgr.eviction_latencies), 0)
        self.assertGreater(mgr.eviction_latencies[0], 0)
        self.assertGreaterEqual(mgr.stale_retention_steps, 1)

    def test_deterministic_execution(self):
        """Verify identical seed produces identical output."""
        p_cfg = {"name": "P2_Balanced", "type": "CANDIDATE", "alpha_slow": 0.005, "theta_obs": 2.0, "patience_obs": 25, "k_ret": 0.5, "theta_ret": 0.05}
        
        errors1 = []
        s1 = create_canonical_stream(seed=9001)
        m1 = ParetoLifecycleManager(d_features=10, policy_config=p_cfg)
        for _ in range(200):
            x, y, info = s1.step()
            r = m1.step(x, y, info)
            errors1.append(r["error"])

        errors2 = []
        s2 = create_canonical_stream(seed=9001)
        m2 = ParetoLifecycleManager(d_features=10, policy_config=p_cfg)
        for _ in range(200):
            x, y, info = s2.step()
            r = m2.step(x, y, info)
            errors2.append(r["error"])

        np.testing.assert_allclose(errors1, errors2, rtol=1e-10)


if __name__ == "__main__":
    unittest.main()
