import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.policies.priority_policy import PriorityProbePolicy, OracleTargetingPolicy
from src.controllers.probe_controllers import ProbeBankController

class TestEXP0002(unittest.TestCase):
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

    def test_1_e0_reproduces_d2(self):
        """1. Verify that E0 reproduces D2 bit-for-bit on seed 42."""
        env_d2 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_e0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

        ctrl_d2 = ProbeBankController(total_steps=2000, target_budget=10000)
        d2 = AblationSparseLearner(
            d=100, variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            t_protect=0
        )

        ctrl_e0 = ProbeBankController(total_steps=2000, target_budget=10000)
        e0 = AblationSparseLearner(
            d=100, variant="B3", initial_support=init_supp,
            probe_policy=RoundRobinProbePolicy(), q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            t_protect=0
        )

        d2_losses = []
        e0_losses = []
        for t in range(1, 101):
            x_d2, y_d2, _, _ = env_d2.step()
            x_e0, y_e0, _, _ = env_e0.step()

            y_hat_d2 = d2.predict(x_d2)
            err_d2 = y_d2 - y_hat_d2
            q_d2 = ctrl_d2.get_q(err_d2, t)
            d2.update(x_d2, y_d2, q=q_d2)
            d2_losses.append(err_d2 ** 2)

            y_hat_e0 = e0.predict(x_e0)
            err_e0 = y_e0 - y_hat_e0
            q_e0 = ctrl_e0.get_q(err_e0, t)
            e0.update(x_e0, y_e0, q=q_e0)
            e0_losses.append(err_e0 ** 2)

        np.testing.assert_allclose(d2_losses, e0_losses, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(d2.weights, e0.weights, rtol=1e-12, atol=1e-12)
        self.assertEqual(d2.support, e0.support)

    def test_2_e1_changes_targeting_only(self):
        """2. Verify E1 uses PriorityProbePolicy and retains standard grace_period."""
        policy = PriorityProbePolicy(priority_fraction=0.60)
        learner = AblationSparseLearner(
            d=100, variant="B3", initial_support=[0, 1, 2, 3, 4],
            probe_policy=policy, q=5, t_protect=0
        )
        self.assertIsInstance(learner.probe_policy, PriorityProbePolicy)
        self.assertEqual(learner.t_protect, 0)
        self.assertEqual(learner.grace_period, 15)

    def test_3_e2_changes_protection_only(self):
        """3. Verify E2 uses RoundRobinProbePolicy and protects incumbents for t_protect=40."""
        policy = RoundRobinProbePolicy()
        learner = AblationSparseLearner(
            d=100, variant="B3", initial_support=[0, 1, 2, 3, 4],
            probe_policy=policy, q=5, t_protect=40
        )
        self.assertIsInstance(learner.probe_policy, RoundRobinProbePolicy)
        self.assertEqual(learner.t_protect, 40)
        
        # Test that incumbent with age < 40 cannot be evicted
        learner.support = list(range(10)) # full capacity 10
        learner.weights = np.array([0.01]*10)
        learner.ages = np.array([25]*10, dtype=np.int32) # age 25 < 40
        
        # Best candidate meets criteria
        learner.cand_n[50] = 10
        learner.cand_mean[50] = 0.90 # high score
        
        x = np.zeros(100)
        x[50] = 1.0
        stats = learner.update(x, y=1.0, q=5)
        # Should NOT swap because all incumbents have age 25 < 40
        self.assertEqual(stats["swaps"], 0)
        self.assertIsNone(stats["victim_feat"])
        self.assertEqual(len(learner.support), 10)

    def test_4_e3_combines_targeting_and_protection(self):
        """4. Verify E3 combines PriorityProbePolicy and t_protect=40."""
        policy = PriorityProbePolicy(priority_fraction=0.60)
        learner = AblationSparseLearner(
            d=100, variant="B3", initial_support=[0, 1, 2, 3, 4],
            probe_policy=policy, q=5, t_protect=40
        )
        self.assertIsInstance(learner.probe_policy, PriorityProbePolicy)
        self.assertEqual(learner.t_protect, 40)

    def test_5_e4_oracle_targeting_purity(self):
        """5. Verify E4 OracleTargetingPolicy targets true omitted features without leaking weights."""
        policy = OracleTargetingPolicy()
        active_supp = {0, 1, 2}
        true_supp = {0, 1, 2, 5, 7}
        # True omitted features are {5, 7}
        selected = policy.select_candidates(d=100, active_support=active_supp, q=5, true_support=true_supp)
        # First two selected must be 5 and 7
        self.assertIn(5, selected[:2])
        self.assertIn(7, selected[:2])
        self.assertEqual(len(selected), 5)
        self.assertEqual(len(set(selected)), 5)

    def test_6_budget_equality(self):
        """6. Verify probe bank total matches 10,000 exactly."""
        ctrl = ProbeBankController(total_steps=2000, target_budget=10000)
        rng = np.random.RandomState(123)
        for t in range(1, 2001):
            ctrl.get_q(float(rng.randn()), t)
        self.assertEqual(ctrl.cumulative_probes, 10000)

    def test_7_kmax_never_exceeded(self):
        """7. Verify K_max never exceeds 10 under any combination of protection and promotion."""
        policy = PriorityProbePolicy(priority_fraction=0.60)
        learner = AblationSparseLearner(
            d=100, variant="B3", initial_support=[0, 1, 2, 3, 4],
            probe_policy=policy, q=15, t_protect=40
        )
        rng = np.random.RandomState(456)
        for _ in range(100):
            x = rng.randn(100)
            y = float(rng.randn())
            learner.update(x, y, q=15)
            self.assertLessEqual(len(learner.support), 10)

    def test_8_priority_scoring_causal(self):
        """8. Verify PriorityProbePolicy uses strictly causal candidate stats."""
        policy = PriorityProbePolicy(priority_fraction=0.60)
        cand_n = np.zeros(100, dtype=np.int32)
        cand_mean = np.zeros(100, dtype=np.float64)
        
        # Candidate 12 has high correlation and 5 probes
        cand_n[12] = 5
        cand_mean[12] = 0.8
        
        # Candidate 34 has high correlation but only 1 probe
        cand_n[34] = 1
        cand_mean[34] = 0.8
        
        selected = policy.select_candidates(
            d=100, active_support={0, 1, 2, 3, 4}, q=5,
            cand_stats={"n": cand_n, "mean": cand_mean}
        )
        # Candidate 12 has score 0.8 * (5/7) = 0.571
        # Candidate 34 has score 0.8 * (1/3) = 0.267
        # Both should be prioritized, with 12 before 34
        self.assertIn(12, selected)
        self.assertIn(34, selected)
        self.assertLess(selected.index(12), selected.index(34))

if __name__ == "__main__":
    unittest.main()
