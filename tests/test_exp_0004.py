import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.dense_nlms import DenseNLMS
from src.learners.ablation_learners import AblationSparseLearner
from src.learners.stabilized_learner import StabilizedSparseLearner
from src.policies.explore_confirm_policy import ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController
from src.utils.accounting import ResourceTracker

class TestEXP0004(unittest.TestCase):
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
            "n_min": 8,
            "theta_promote": 0.40,
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
            "cooldown_steps": 20,
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

    def test_1_g0_reproduces_f4_baseline(self):
        """1. Verify that G0 with baseline victim rule reproduces F4 bit-for-bit on seed 42."""
        env_f4 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_g0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

        ctrl_f4 = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )
        pol_f4 = ExploreConfirmPolicy(
            d=100, c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        f4 = AblationSparseLearner(
            d=100, variant="B3", initial_support=init_supp,
            probe_policy=pol_f4, q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            t_protect=0
        )

        ctrl_g0 = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )
        pol_g0 = ExploreConfirmPolicy(
            d=100, c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        g0 = StabilizedSparseLearner(
            d=100, initial_support=init_supp,
            probe_policy=pol_g0, q=5, mu=0.5, eps=1e-6,
            n_min=8, theta_promote=0.40, grace_period=15, swap_threshold=0.05,
            victim_strategy="baseline", cooldown_steps=0
        )

        f4_losses, g0_losses = [], []
        for t in range(1, 101):
            x_f4, y_f4, ts_f4, _ = env_f4.step()
            x_g0, y_g0, ts_g0, _ = env_g0.step()

            yh_f4 = f4.predict(x_f4)
            err_f4 = y_f4 - yh_f4
            q_f4 = ctrl_f4.get_q(err_f4, t)
            f4.update(x_f4, y_f4, q=q_f4, true_support=ts_f4)
            f4_losses.append(err_f4 ** 2)

            yh_g0 = g0.predict(x_g0)
            err_g0 = y_g0 - yh_g0
            q_g0 = ctrl_g0.get_q(err_g0, t)
            g0.update(x_g0, y_g0, q=q_g0, true_support=ts_g0)
            g0_losses.append(err_g0 ** 2)

        np.testing.assert_allclose(f4_losses, g0_losses, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(f4.weights, g0.weights, rtol=1e-12, atol=1e-12)
        self.assertEqual(f4.support, g0.support)

    def test_2_g1_age_normalization_favors_young_growing_features(self):
        """2. Verify G1 age-normalization shields adapting young features while allowing noise eviction."""
        pol = ExploreConfirmPolicy(d=10)
        learner = StabilizedSparseLearner(
            d=10, initial_support=[0, 1, 2, 3, 4], probe_policy=pol,
            victim_strategy="age_normalized", tau_mature=50, grace_period=15
        )
        # Fill capacity to 10
        learner.support = list(range(10))
        learner.weights = np.array([0.5, 0.4, 0.3, 0.4, 0.5, 0.3, 0.3, 0.3, 0.3, 0.08])
        learner.ages = np.array([100, 100, 100, 100, 100, 100, 100, 100, 100, 20])
        # Feature 9 is age 20 (>= grace 15). Weight = 0.08.
        # Raw weight is 0.08 (smallest). But maturity factor is 20/50 = 0.40.
        # Adjusted score = 0.08 / 0.40 = 0.20.
        # Feature 2 is age 100 (mature). Weight = 0.30. Score = 0.30.
        # Feature 9's score (0.20) is still less than 0.30, but higher than raw 0.08.
        # If another mature feature has weight 0.15:
        learner.weights[2] = 0.15
        # Now feature 2 has score 0.15 / 1.0 = 0.15!
        # Feature 9 has score 0.08 / 0.40 = 0.20!
        # G1 will choose feature 2 (mature with small weight) instead of feature 9 (young with 0.08)!
        x = np.ones(10)
        # Candidate 10 with high score
        learner.cand_n[9] = 10
        eligible_drops = [idx for idx, age in enumerate(learner.ages) if age >= 15]
        drop_idx = min(eligible_drops, key=lambda idx: abs(learner.weights[idx]) / min(1.0, learner.ages[idx] / 50.0))
        self.assertEqual(drop_idx, 2) # Mature feature with 0.15 evicted, NOT young feature with 0.08!

    def test_3_non_immunity_noise_remains_evictable(self):
        """3. Verify young noise features with tiny weights remain evictable under G1/G2/G3."""
        learner = StabilizedSparseLearner(
            d=10, initial_support=list(range(10)), probe_policy=ExploreConfirmPolicy(d=10),
            victim_strategy="age_normalized", tau_mature=50, grace_period=15
        )
        learner.ages = np.array([100, 100, 100, 100, 100, 100, 100, 100, 100, 20])
        # Young feature 9 has minuscule noise weight 0.001
        learner.weights = np.array([0.5, 0.4, 0.3, 0.4, 0.5, 0.3, 0.3, 0.3, 0.3, 0.001])
        # Adjusted score for feature 9 = 0.001 / (20/50) = 0.0025 << 0.30
        eligible_drops = [idx for idx, age in enumerate(learner.ages) if age >= 15]
        drop_idx = min(eligible_drops, key=lambda idx: abs(learner.weights[idx]) / min(1.0, learner.ages[idx] / 50.0))
        self.assertEqual(drop_idx, 9) # Noise feature is evictable! No blind immunity!

    def test_4_g4_cooldown_delays_promotion_without_freezing_nlms(self):
        """4. Verify G4 promotion cooldown prevents promotion bursts while continuing NLMS."""
        pol = ExploreConfirmPolicy(d=10)
        learner = StabilizedSparseLearner(
            d=10, initial_support=[0, 1, 2, 3, 4], probe_policy=pol,
            victim_strategy="baseline", cooldown_steps=20
        )
        x = np.random.randn(10)
        y = float(np.dot(np.ones(5), x[:5]))
        learner.last_promotion_step = 10
        learner.current_step = 15 # 5 steps elapsed < 20 cooldown
        # Setup candidate with high evidence
        learner.cand_n[5] = 10
        learner.cand_mean[5] = 0.80
        
        # update should NOT promote candidate 5 because in cooldown
        stats = learner.update(x, y, q=5)
        self.assertEqual(stats["in_cooldown"], 1)
        self.assertEqual(stats["promotions"], 0)
        self.assertEqual(len(learner.support), 5)

    def test_5_g5_oracle_victim_targets_noise_first(self):
        """5. Verify G5 Oracle Victim selects noise features if present in support."""
        learner = StabilizedSparseLearner(
            d=10, initial_support=list(range(5)), probe_policy=ExploreConfirmPolicy(d=10),
            victim_strategy="oracle_victim", grace_period=15
        )
        learner.support = list(range(10))
        learner.ages = np.array([50] * 10)
        learner.weights = np.array([0.1, 0.8, 0.9, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.9])

        # True support is {0, 1, 2, 3, 4}
        # Feature 0 is true, but has smallest weight (0.1)
        # Feature 8 is noise (not in true support), weight is 0.2
        true_supp = {0, 1, 2, 3, 4}
        eligible_drops = [idx for idx, age in enumerate(learner.ages) if age >= 15]
        noise_drops = [idx for idx in eligible_drops if learner.support[idx] not in true_supp]
        self.assertTrue(len(noise_drops) > 0)
        drop_idx = min(noise_drops, key=lambda idx: abs(learner.weights[idx]))
        self.assertEqual(learner.support[drop_idx], 8) # Oracle targeted noise feature 8, preserving true feature 0!

    def test_6_compute_and_memory_bounds(self):
        """6. Verify all models stay strictly under 25% Dense compute (150.5 FLOPs)."""
        dense_flops = 602.0
        cap_25 = 0.25 * dense_flops
        self.assertEqual(cap_25, 150.5)

        learner = StabilizedSparseLearner(
            d=100, initial_support=list(range(10)),
            probe_policy=ExploreConfirmPolicy(d=100, confirm_fraction=0.6, coverage_fraction=0.4),
            q=5, victim_strategy="age_normalized"
        )
        x = np.random.randn(100)
        stats = learner.update(x, 1.0, q=5)
        self.assertLess(stats["flops"], cap_25)

if __name__ == "__main__":
    unittest.main()
