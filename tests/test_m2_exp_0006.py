import unittest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../experiments/M2-EXP-0006")))

from run_m2_exp_0006 import (
    EnhancedLifecycleManager,
    compute_roc_auc_numpy,
    compute_pr_auc_numpy
)


class TestM2Exp0006(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.RandomState(42)

    def test_roc_auc_numpy(self):
        y_true = np.array([1, 0, 1, 0, 1])
        scores = np.array([0.9, 0.1, 0.8, 0.4, 0.7])
        roc = compute_roc_auc_numpy(y_true, scores)
        self.assertAlmostEqual(roc, 1.0, places=4)

        # Inverted scores should yield 0.0
        roc_inv = compute_roc_auc_numpy(y_true, -scores)
        self.assertAlmostEqual(roc_inv, 0.0, places=4)

    def test_pr_auc_numpy(self):
        y_true = np.array([1, 0, 1, 0, 1])
        scores = np.array([0.9, 0.1, 0.8, 0.4, 0.7])
        pr = compute_pr_auc_numpy(y_true, scores)
        self.assertAlmostEqual(pr, 1.0, places=4)

    def test_structural_observability_maintenance(self):
        """Structural observability w_state^2 should remain high even if state s_t = 0."""
        mgr = EnhancedLifecycleManager(d_features=10, policy_mode="C2_Temporal_CxO_Accumulator")
        from src.models.minimal_state import GatedScalarState
        mgr.active_state = GatedScalarState(z_dim=2)
        mgr.active_type = "GATED"
        mgr.w_state = 1.0
        mgr.active_state.s = 0.0 # quiescent state value
        mgr.active_age = 150 # Mature
        mgr.temporal_o = 1.0

        x = np.zeros(10)
        y = 0.0
        res = mgr.step(x, y)

        # In C2, structural observability O_struct = w_state^2 = 1.0
        self.assertGreater(mgr.temporal_o, 0.5)
        # Even with zero instant delta loss, temporal C x O retains the state
        self.assertIsNotNone(mgr.active_state)

    def test_obsolescence_accumulator_in_state_free_regime(self):
        """In state-free regime where base error is near zero, obsolescence evidence accumulates."""
        mgr = EnhancedLifecycleManager(d_features=10, policy_mode="C2_Temporal_CxO_Accumulator", evict_patience=10)
        from src.models.minimal_state import GatedScalarState
        mgr.active_state = GatedScalarState(z_dim=2)
        mgr.active_type = "GATED"
        mgr.w_state = 0.05
        mgr.active_state.s = 0.0
        mgr.active_age = 150

        # Feed 35 steps of pure zero noise matching base model
        for _ in range(35):
            x = np.zeros(10)
            y = 0.0
            res = mgr.step(x, y)

        # Obsolescence evidence should have accumulated
        self.assertGreater(mgr.obsolescence_evidence, 0.0)

    def test_c2_policy_prevents_premature_eviction_on_latch_reset(self):
        """Test that C2 policy avoids premature eviction during quiescent period."""
        mgr_c0 = EnhancedLifecycleManager(d_features=10, policy_mode="C0_Original_Eviction", evict_patience=15)
        mgr_c2 = EnhancedLifecycleManager(d_features=10, policy_mode="C2_Temporal_CxO_Accumulator", evict_patience=15)

        for mgr in [mgr_c0, mgr_c2]:
            from src.models.minimal_state import GatedScalarState
            mgr.active_state = GatedScalarState(z_dim=2)
            mgr.active_type = "GATED"
            mgr.w_state = 1.0
            mgr.active_state.s = 0.0
            mgr.active_age = 150
            mgr.windowed_utility = 0.001
            mgr.temporal_c = 0.15
            mgr.temporal_o = 1.0

        # Step 20 steps of quiescent state (y=0, x=0)
        for _ in range(20):
            x = np.zeros(10)
            y = 0.0
            mgr_c0.step(x, y)
            mgr_c2.step(x, y)

        # C0 should have prematurely evicted because windowed_utility < evict_threshold
        self.assertIsNone(mgr_c0.active_state)
        # C2 should retain because temporal_c * temporal_o is maintained
        self.assertIsNotNone(mgr_c2.active_state)


if __name__ == "__main__":
    unittest.main()
