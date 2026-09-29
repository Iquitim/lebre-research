import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.adaptive_evidence_learner import AdaptiveEvidenceLearner
from src.learners.stabilized_learner import StabilizedSparseLearner
from src.policies.explore_confirm_policy import ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController

class TestEXP0005(unittest.TestCase):
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
            "target_total_probes": 10000,
            "q_min": 1,
            "q_base": 5,
            "q_max": 8,
            "tau_low": 0.05,
            "tau_high": 0.50,
            "ema_alpha": 0.05,
            "nlms_mu": 0.5,
            "nlms_eps": 1e-6,
            "n_min": 5,
            "theta_promote": 0.10,
            "grace_period": 15,
            "swap_threshold": 0.05,
            "c_max": 3,
            "n_screen": 3,
            "theta_screen": 0.20,
            "gamma_screen": 0.75,
            "theta_drop": 0.10,
            "gamma_drop": 0.60,
            "confirm_max_probes": 12,
            "confirm_fraction_f4": 0.60,
            "coverage_fraction_f4": 0.40,
            "tau_mature": 50,
            "cooldown_steps": 0,
            "contrib_beta": 0.05,
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

    def test_1_h0_reproduces_g1_baseline(self):
        """H0 fixed baseline must reproduce accepted EXP-0004 G1 learner bit-for-bit."""
        env_g1 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_h0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

        ctrl_g1 = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )
        pol_g1 = ExploreConfirmPolicy(
            d=100, c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        g1 = StabilizedSparseLearner(
            d=100, initial_support=list(init_supp), probe_policy=pol_g1,
            q=5, mu=0.5, eps=1e-6, n_min=5, theta_promote=0.10,
            grace_period=15, swap_threshold=0.05,
            victim_strategy="age_normalized", tau_mature=50, cooldown_steps=0
        )

        ctrl_h0 = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )
        pol_h0 = ExploreConfirmPolicy(
            d=100, c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        h0 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(init_supp), probe_policy=pol_h0,
            q=5, mu=0.5, eps=1e-6, n_min=5, theta_promote=0.10,
            grace_period=15, swap_threshold=0.05,
            victim_strategy="age_normalized", tau_mature=50, cooldown_steps=0,
            evidence_rule="fixed_baseline"
        )

        for t in range(1, 101):
            x1, y1, supp1, _ = env_g1.step()
            x2, y2, supp2, _ = env_h0.step()

            yh1 = g1.predict(x1)
            err1 = y1 - yh1
            q1 = ctrl_g1.get_q(err1, t)

            yh2 = h0.predict(x2)
            err2 = y2 - yh2
            q2 = ctrl_h0.get_q(err2, t)
            assert q1 == q2

            res1 = g1.update(x1, y1, q=q1, true_support=supp1)
            res2 = h0.update(x2, y2, q=q2, true_support=supp2)

            self.assertEqual(g1.support, h0.support)
            np.testing.assert_allclose(g1.weights, h0.weights, atol=1e-12)
            self.assertAlmostEqual(res1["prediction"], res2["prediction"], places=10)

    def test_2_h1_lower_fixed_eligibility(self):
        """H1 with n_fast=2 allows promotion when n=2, while baseline requires n=5."""
        pol = ExploreConfirmPolicy(d=100)
        h1 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, n_fast=2, theta_promote=0.10, evidence_rule="lower_fixed"
        )
        h1.cand_n[15] = 2
        h1.cand_mean[15] = 0.15
        h1.cand_pos[15] = 2
        h1.cand_neg[15] = 0

        eligible, early, req_n, _, _ = h1.evaluate_candidate_readiness(15)
        self.assertTrue(eligible)
        self.assertTrue(early)
        self.assertEqual(req_n, 2)

        # H0 baseline should reject
        h0 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, theta_promote=0.10, evidence_rule="fixed_baseline"
        )
        h0.cand_n[15] = 2
        h0.cand_mean[15] = 0.15
        eligible_h0, _, req_n_h0, _, _ = h0.evaluate_candidate_readiness(15)
        self.assertFalse(eligible_h0)
        self.assertEqual(req_n_h0, 5)

    def test_3_h2_strength_adaptive(self):
        """H2 enables early readiness only if |mean| >= theta_strong (0.30)."""
        pol = ExploreConfirmPolicy(d=100)
        h2 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, n_fast=2, theta_promote=0.10, theta_strong=0.30,
            evidence_rule="strength_adaptive"
        )
        # Candidate A: strong correlation (0.35)
        h2.cand_n[20] = 2
        h2.cand_mean[20] = 0.35
        eligible, early, req_n, _, _ = h2.evaluate_candidate_readiness(20)
        self.assertTrue(eligible)
        self.assertTrue(early)
        self.assertEqual(req_n, 2)

        # Candidate B: weak correlation (0.15)
        h2.cand_n[21] = 2
        h2.cand_mean[21] = 0.15
        eligible, early, req_n, _, _ = h2.evaluate_candidate_readiness(21)
        self.assertFalse(eligible)
        self.assertEqual(req_n, 5)

    def test_4_h3_strength_consistency(self):
        """H3 requires both strong correlation AND high sign consistency."""
        pol = ExploreConfirmPolicy(d=100)
        h3 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, n_fast=2, theta_promote=0.10, theta_strong=0.30, gamma_strong=0.80,
            evidence_rule="strength_consistency"
        )
        # Strong (0.35) but noisy signs (pos=1, neg=1 -> 0.50 consistency)
        h3.cand_n[30] = 2
        h3.cand_mean[30] = 0.35
        h3.cand_pos[30] = 1
        h3.cand_neg[30] = 1
        eligible, early, req_n, _, sc = h3.evaluate_candidate_readiness(30)
        self.assertFalse(eligible)
        self.assertEqual(req_n, 5)
        self.assertEqual(sc, 0.50)

        # Strong (0.35) and consistent signs (pos=2, neg=0 -> 1.00 consistency)
        h3.cand_n[31] = 2
        h3.cand_mean[31] = 0.35
        h3.cand_pos[31] = 2
        h3.cand_neg[31] = 0
        eligible, early, req_n, _, sc = h3.evaluate_candidate_readiness(31)
        self.assertTrue(eligible)
        self.assertTrue(early)
        self.assertEqual(req_n, 2)
        self.assertEqual(sc, 1.00)

    def test_5_h5_oracle_stopping(self):
        """H5 grants fast stopping to true support features and requires n_min for noise."""
        pol = ExploreConfirmPolicy(d=100)
        h5 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, n_fast=2, theta_promote=0.10,
            evidence_rule="oracle_stopping"
        )
        true_supp = {7, 24, 49, 66, 92}

        # True feature 7 with n=2, mean=0.15
        h5.cand_n[7] = 2
        h5.cand_mean[7] = 0.15
        eligible, early, req_n, _, _ = h5.evaluate_candidate_readiness(7, true_support=true_supp)
        self.assertTrue(eligible)
        self.assertEqual(req_n, 2)

        # Noise feature 50 with n=2, mean=0.15
        h5.cand_n[50] = 2
        h5.cand_mean[50] = 0.15
        eligible, early, req_n, _, _ = h5.evaluate_candidate_readiness(50, true_support=true_supp)
        self.assertFalse(eligible)
        self.assertEqual(req_n, 5)

    def test_6_compute_overhead_below_threshold(self):
        """Verify that AdaptiveEvidenceLearner FLOPs stay well below 25% of Dense (< 150.5 FLOPs)."""
        env = DynamicSparseLinearStream(self.config, seed=self.seed)
        pol = ExploreConfirmPolicy(
            d=100, c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        h3 = AdaptiveEvidenceLearner(
            d=100, initial_support=list(range(10)), probe_policy=pol,
            n_min=5, n_fast=2, theta_promote=0.10, theta_strong=0.30, gamma_strong=0.80,
            evidence_rule="strength_consistency"
        )
        ctrl = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )

        total_flops = 0
        steps = 100
        for t in range(1, steps + 1):
            x, y, supp, _ = env.step()
            yh = h3.predict(x)
            err = y - yh
            q = ctrl.get_q(err, t)
            res = h3.update(x, y, q=q, true_support=supp)
            total_flops += res["flops"]

        mean_flops = total_flops / steps
        self.assertLess(mean_flops, 150.5, f"Mean FLOPs {mean_flops} exceeds 25% of Dense")

if __name__ == "__main__":
    unittest.main()
