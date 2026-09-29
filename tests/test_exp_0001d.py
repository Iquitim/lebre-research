import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.controllers.probe_controllers import (
    FixedProbeController,
    ErrorAdaptiveGovernorController,
    ProbeBankController,
    RandomPermutationController,
    OracleTimingController,
)

class TestEXP0001d(unittest.TestCase):
    def setUp(self):
        self.config = {
            "d_features": 100,
            "k_star": 5,
            "k_true": 5,
            "k_slack_max": 10,
            "noise_std": 0.1,
            "total_steps": 2000,
            "shift_step": 1000,
            "seeds": [42],
            "probe_budget_q": 5,
            "nlms_mu": 0.5,
            "nlms_eps": 1e-6,
            "n_min": 8,
            "theta_promote": 0.40,
            "grace_period": 15,
            "swap_threshold": 0.05,
            "regime_1": {
                "indices": [2, 15, 33, 58, 81],
                "weights": [1.5, -1.2, 0.8, -1.0, 1.3]
            },
            "regime_2": {
                "indices": [7, 24, 49, 66, 92],
                "weights": [-1.4, 1.0, -1.1, 1.6, -0.9]
            }
        }
        self.seed = 42

    def test_1_d0_reproduces_b3(self):
        """1. Verify that D0 with FixedProbeController reproduces exact B3 trajectory."""
        env_b3 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_d0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

        # Standard B3 (fixed self.q = 5, no q passed to update)
        b3 = AblationSparseLearner(
            d=self.config["d_features"], variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05
        )

        # D0 using FixedProbeController passing q_t = 5 to update
        d0_ctrl = FixedProbeController(q=5, total_steps=2000, target_budget=10000)
        d0 = AblationSparseLearner(
            d=self.config["d_features"], variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05
        )

        b3_errors = []
        d0_errors = []

        for t in range(1, 101):
            x_b3, y_b3, _, _ = env_b3.step()
            x_d0, y_d0, _, _ = env_d0.step()

            # B3 update without q
            y_hat_b3 = b3.predict(x_b3)
            err_b3 = y_b3 - y_hat_b3
            b3.update(x_b3, y_b3)
            b3_errors.append(err_b3)

            # D0 update with q from controller
            y_hat_d0 = d0.predict(x_d0)
            err_d0 = y_d0 - y_hat_d0
            q_t = d0_ctrl.get_q(err_d0, t)
            d0.update(x_d0, y_d0, q=q_t)
            d0_errors.append(err_d0)

        # Assert predictions and weights match bit-for-bit
        np.testing.assert_allclose(b3_errors, d0_errors, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(b3.weights, d0.weights, rtol=1e-12, atol=1e-12)
        self.assertEqual(b3.support, d0.support)

    def test_2_d1_cumulative_budget_exact(self):
        """2. Verify that D1 cumulative budget matches 10,000 exactly across full 2000 steps."""
        controller = ErrorAdaptiveGovernorController(
            q_min=2, q_base=5, q_max=15, total_steps=2000, target_budget=10000
        )
        rng = np.random.RandomState(999)
        for t in range(1, 2001):
            err = float(rng.randn() * (2.0 if t > 1000 and t < 1200 else 0.1))
            q_t = controller.get_q(err, t)
            self.assertGreaterEqual(q_t, 2)
            self.assertLessEqual(q_t, 15)

        self.assertEqual(controller.cumulative_probes, 10000)
        self.assertEqual(len(controller.history), 2000)

    def test_3_d2_budget_exact_and_bank_non_negative(self):
        """3. Verify D2 matches 10,000 exactly and bank never drops below zero (no borrowing)."""
        controller = ProbeBankController(
            q_min=2, q_base=5, q_max=15, total_steps=2000, target_budget=10000
        )
        rng = np.random.RandomState(888)
        for t in range(1, 2001):
            err = float(rng.randn() * (3.0 if 1000 < t < 1300 else 0.05))
            q_t = controller.get_q(err, t)
            self.assertGreaterEqual(q_t, 2)
            self.assertLessEqual(q_t, 15)
            self.assertGreaterEqual(controller.bank, 0, f"Bank negative at step {t}!")

        self.assertEqual(controller.cumulative_probes, 10000)
        self.assertEqual(controller.bank, 0)
        self.assertEqual(len(controller.history), 2000)

    def test_4_peak_q_never_exceeded(self):
        """4. Verify q_t <= q_max across all controllers."""
        d1 = ErrorAdaptiveGovernorController(q_max=15)
        d2 = ProbeBankController(q_max=15)
        for t in range(1, 100):
            # Massive error spike
            err = 100.0
            self.assertLessEqual(d1.get_q(err, t), 15)
            self.assertLessEqual(d2.get_q(err, t), 15)

    def test_5_d3_permutation_matches_d2_distribution(self):
        """5. Verify D3 uses identical total budget and empirical q distribution as D2."""
        d2 = ProbeBankController(q_min=2, q_base=5, q_max=15, total_steps=2000, target_budget=10000)
        rng = np.random.RandomState(777)
        for t in range(1, 2001):
            err = float(rng.randn() * (2.5 if 1000 < t < 1200 else 0.1))
            d2.get_q(err, t)

        d2_schedule = d2.history
        rng_perm = np.random.RandomState(12345)
        d3_schedule = list(rng_perm.permutation(d2_schedule))

        d3 = RandomPermutationController(q_schedule=d3_schedule, total_steps=2000, target_budget=10000)
        for t in range(1, 2001):
            d3.get_q(0.0, t)

        self.assertEqual(sum(d3.history), 10000)
        self.assertEqual(sorted(d3.history), sorted(d2_schedule))

    def test_6_d4_oracle_timing_budget_exact(self):
        """6. Verify D4 matches 10,000 probes and concentrates 15 post-shift."""
        d4 = OracleTimingController(shift_step=1000, burst_len=200, q_max=15, total_steps=2000, target_budget=10000)
        self.assertEqual(sum(d4.schedule), 10000)
        self.assertEqual(len(d4.schedule), 2000)
        # Check post-shift burst
        self.assertEqual(d4.schedule[1000], 15)
        self.assertEqual(d4.schedule[1199], 15)
        # Check pre-shift
        self.assertEqual(d4.schedule[0], 5)
        self.assertEqual(d4.schedule[999], 5)

    def test_7_causal_purity(self):
        """7. Verify controller only receives current causal scalar error."""
        ctrl = ProbeBankController()
        # Controller should only need float error and integer step
        q1 = ctrl.get_q(error=1.5, step=1)
        self.assertIsInstance(q1, int)
        self.assertTrue(hasattr(ctrl, "smoothed_error"))

if __name__ == "__main__":
    unittest.main()
