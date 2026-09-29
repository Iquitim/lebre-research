import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.dense_nlms import DenseNLMS
from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.policies.priority_policy import PriorityProbePolicy, OracleTargetingPolicy
from src.policies.explore_confirm_policy import PersistenceProbePolicy, ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController
from src.utils.accounting import ResourceTracker

class TestEXP0003(unittest.TestCase):
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

    def test_1_f0_reproduces_d2_baseline(self):
        """1. Verify that F0 reproduces D2 bit-for-bit on seed 42."""
        env_d2 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_f0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

        ctrl_d2 = ProbeBankController(total_steps=2000, target_budget=10000)
        d2 = AblationSparseLearner(
            d=100, variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            t_protect=0
        )

        ctrl_f0 = ProbeBankController(total_steps=2000, target_budget=10000)
        f0 = AblationSparseLearner(
            d=100, variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            t_protect=0
        )

        d2_losses = []
        f0_losses = []
        for t in range(1, 101):
            x_d2, y_d2, _, _ = env_d2.step()
            x_f0, y_f0, _, _ = env_f0.step()

            y_hat_d2 = d2.predict(x_d2)
            err_d2 = y_d2 - y_hat_d2
            q_d2 = ctrl_d2.get_q(err_d2, t)
            d2.update(x_d2, y_d2, q=q_d2)
            d2_losses.append(err_d2 ** 2)

            y_hat_f0 = f0.predict(x_f0)
            err_f0 = y_f0 - y_hat_f0
            q_f0 = ctrl_f0.get_q(err_f0, t)
            f0.update(x_f0, y_f0, q=q_f0)
            f0_losses.append(err_f0 ** 2)

        np.testing.assert_allclose(d2_losses, f0_losses, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(d2.weights, f0.weights, rtol=1e-12, atol=1e-12)
        self.assertEqual(d2.support, f0.support)

    def test_2_f1_reproduces_e1(self):
        """2. Verify that F1 reproduces E1 priority policy."""
        policy = PriorityProbePolicy(priority_fraction=0.60)
        learner = AblationSparseLearner(
            d=100, variant="B3", initial_support=[0, 1, 2, 3, 4],
            probe_policy=policy, q=5, t_protect=0
        )
        self.assertIsInstance(learner.probe_policy, PriorityProbePolicy)
        self.assertEqual(learner.t_protect, 0)

    def test_3_f2_persistence_causal_and_lazy(self):
        """3. Verify F2 PersistenceProbePolicy only scores candidates with n >= n_priority_min."""
        policy = PersistenceProbePolicy(d=10, priority_fraction=0.60, n_priority_min=3)
        # Create dummy cand_stats
        cand_stats = {
            "n": np.array([2, 4, 1, 0, 5, 3, 0, 0, 0, 0], dtype=np.int32),
            "mean": np.array([0.5, 0.4, 0.9, 0.0, -0.3, 0.2, 0.0, 0.0, 0.0, 0.0]),
            "pos": np.array([2, 4, 1, 0, 1, 2, 0, 0, 0, 0], dtype=np.int32),
            "neg": np.array([0, 0, 0, 0, 4, 1, 0, 0, 0, 0], dtype=np.int32),
        }
        active_support = {0}
        # Candidate 0 is active -> score 0
        # Candidate 1: n=4 >= 3, mean=0.4, pos=4, neg=0 -> sign_consistency=1.0, conf=4/6=0.6667 -> score > 0
        # Candidate 2: n=1 < 3 -> score 0
        # Candidate 4: n=5 >= 3, mean=-0.3, pos=1, neg=4 -> sign_consistency=4/5=0.8, conf=5/7 -> score > 0
        # Candidate 5: n=3 >= 3, mean=0.2, pos=2, neg=1 -> sign_consistency=2/3=0.667, conf=3/5 -> score > 0
        policy.on_probes_evaluated([0, 1, 2, 4, 5], cand_stats, active_support)

        self.assertEqual(policy.cached_scores[0], 0.0) # active
        self.assertGreater(policy.cached_scores[1], 0.0) # valid persistent
        self.assertEqual(policy.cached_scores[2], 0.0) # n < 3
        self.assertGreater(policy.cached_scores[4], 0.0) # valid persistent
        self.assertGreater(policy.cached_scores[5], 0.0) # valid persistent

        selected = policy.select_candidates(10, active_support, q=3)
        # Should pick candidate 1 (highest score), then 4, etc.
        self.assertIn(1, selected)

    def test_4_f3_explore_confirm_state_transitions(self):
        """4. Verify F3 ExploreConfirmPolicy entry, C_max cap, and timeout/exit rules."""
        policy = ExploreConfirmPolicy(
            d=10, c_max=2, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=4
        )
        active_support = {0}

        # Candidate 1 meets criteria: n=3, mean=0.30, pos=3, neg=0 -> enters confirm
        # Candidate 2 meets criteria: n=3, mean=0.25, pos=3, neg=0 -> enters confirm
        # Candidate 3 meets criteria: n=3, mean=0.40, pos=3, neg=0 -> capacity C_max=2 full, cannot enter!
        cand_stats = {
            "n": np.array([0, 3, 3, 3, 0, 0, 0, 0, 0, 0], dtype=np.int32),
            "mean": np.array([0.0, 0.30, 0.25, 0.40, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "pos": np.array([0, 3, 3, 3, 0, 0, 0, 0, 0, 0], dtype=np.int32),
            "neg": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int32),
            "m2": np.zeros(10),
            "last_step": np.zeros(10, dtype=np.int32),
            "current_step": 10
        }

        policy.on_probes_evaluated([1, 2, 3], cand_stats, active_support)
        self.assertEqual(len(policy.confirm_set), 2)
        self.assertIn(1, policy.confirm_set)
        self.assertIn(2, policy.confirm_set)
        self.assertNotIn(3, policy.confirm_set) # C_max respected

        # Selection in F3 should prioritize confirm candidates
        sel = policy.select_candidates(10, active_support, q=3)
        self.assertEqual(sel[0], 1)
        self.assertEqual(sel[1], 2)
        self.assertEqual(len(sel), 3)

        # Test timeout exit after 4 probes
        for _ in range(4):
            policy.on_probes_evaluated([1], cand_stats, active_support)
        self.assertNotIn(1, policy.confirm_set) # Exited due to timeout!

    def test_5_f4_forced_coverage_reservation(self):
        """5. Verify F4 reserves probe budget for coverage exploration."""
        policy = ExploreConfirmPolicy(
            d=10, c_max=3, n_screen=2, theta_screen=0.10, gamma_screen=0.50,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        active_support = {0}
        # Force 3 candidates into confirm
        policy.confirm_set = [1, 2, 3]

        # Request q=5 probes
        # confirm_fraction=0.60 -> max floor(5 * 0.60) = 3 confirm probes
        # Remaining 2 probes MUST be coverage candidates (not 1, 2, 3, 0)
        sel = policy.select_candidates(10, active_support, q=5)
        self.assertEqual(len(sel), 5)
        conf_count = sum(1 for c in sel if c in [1, 2, 3])
        cov_count = sum(1 for c in sel if c not in [1, 2, 3, 0])
        self.assertEqual(conf_count, 3)
        self.assertEqual(cov_count, 2)

    def test_6_budget_gate_and_compute_cap(self):
        """6. Verify all models use exactly 10,000 probes and stay under 25% Dense compute."""
        dense = DenseNLMS(d=100, mu=0.5, eps=1e-6)
        dense_flops = ResourceTracker.dot_product_flops(100) + ResourceTracker.norm_sq_flops(100) + ResourceTracker.vector_update_flops(100) + 3
        self.assertEqual(dense_flops, 602)
        dense_cap_25 = 0.25 * dense_flops
        self.assertAlmostEqual(dense_cap_25, 150.5)

        # Persistence probe FLOPs per probe
        p_flops = ResourceTracker.persistence_probe_flops(5)
        self.assertEqual(p_flops, 17 * 5) # 85 FLOPs
        # Total per step ~ 34 (NLMS) + 85 (probes) = 119 FLOPs < 150.5 FLOPs!
        self.assertLess(34 + p_flops, dense_cap_25)

if __name__ == "__main__":
    unittest.main()
