import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.learners.adaptive_evidence_learner import AdaptiveEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.policies.explore_confirm_policy import ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController

class TestEXP0006(unittest.TestCase):
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
            "cooldown_steps": 0,
            "w_max": 5,
            "h_max": 2,
            "n_hint": 2,
            "theta_hint": 0.15,
            "gamma_hint": 0.60,
            "theta_decay": 0.10,
            "warm_max_probes": 10,
            "hot_max_probes": 12,
            "theta_hot": 0.25,
            "gamma_hot": 0.75,
            "cold_fraction": 0.35,
            "warm_fraction": 0.65,
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

    def test_1_j0_reproduces_h0_baseline(self):
        """J0 uniform baseline must reproduce accepted EXP-0005 H0 baseline bit-for-bit."""
        env_h0 = DynamicSparseLinearStream(self.config, seed=self.seed)
        env_j0 = DynamicSparseLinearStream(self.config, seed=self.seed)

        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))

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
            q=5, mu=0.5, eps=1e-6, n_min=8, theta_promote=0.40,
            grace_period=15, swap_threshold=0.05,
            victim_strategy="age_normalized", tau_mature=50, cooldown_steps=0,
            evidence_rule="fixed_baseline"
        )

        ctrl_j0 = ProbeBankController(
            q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
            total_steps=2000, target_budget=10000
        )
        pol_j0 = TieredEvidenceRatePolicy(
            d=100, mode="uniform_baseline",
            c_max=3, n_screen=3, theta_screen=0.20, gamma_screen=0.75,
            theta_drop=0.10, gamma_drop=0.60, confirm_max_probes=12,
            confirm_fraction=0.60, coverage_fraction=0.40
        )
        j0 = TieredEvidenceLearner(
            d=100, initial_support=list(init_supp), probe_policy=pol_j0,
            q=5, mu=0.5, eps=1e-6, n_min=8, theta_promote=0.40,
            grace_period=15, swap_threshold=0.05,
            victim_strategy="age_normalized", tau_mature=50, cooldown_steps=0
        )

        for t in range(1, 150):
            x1, y1, supp1, _ = env_h0.step()
            x2, y2, supp2, _ = env_j0.step()

            yh1 = h0.predict(x1)
            err1 = y1 - yh1
            q1 = ctrl_h0.get_q(err1, t)

            yh2 = j0.predict(x2)
            err2 = y2 - yh2
            q2 = ctrl_j0.get_q(err2, t)
            self.assertEqual(q1, q2)

            res1 = h0.update(x1, y1, q=q1, true_support=supp1)
            res2 = j0.update(x2, y2, q=q2, true_support=supp2)

            self.assertEqual(h0.support, j0.support)
            np.testing.assert_allclose(h0.weights, j0.weights, atol=1e-12)

    def test_2_total_probes_strictly_matched_at_10000(self):
        """All variants must execute exactly 10,000 probes over 2,000 steps."""
        modes = ["uniform_baseline", "two_tier", "two_tier_decay", "three_tier", "queue_multi_rate", "oracle_rate"]
        for m in modes:
            env = DynamicSparseLinearStream(self.config, seed=self.seed)
            rng = np.random.RandomState(self.seed)
            init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))
            ctrl = ProbeBankController(
                q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
                total_steps=2000, target_budget=10000
            )
            pol = TieredEvidenceRatePolicy(d=100, mode=m)
            learner = TieredEvidenceLearner(
                d=100, initial_support=list(init_supp), probe_policy=pol,
                q=5, mu=0.5, eps=1e-6, n_min=8, theta_promote=0.40
            )

            total_p = 0
            for t in range(1, 2001):
                x, y, supp, _ = env.step()
                yh = learner.predict(x)
                err = y - yh
                q = ctrl.get_q(err, t)
                res = learner.update(x, y, q=q, true_support=supp)
                total_p += res["num_probed"]

            self.assertEqual(total_p, 10000, f"Variant {m} consumed {total_p} probes, expected 10,000!")

    def test_3_non_starvation_cold_candidates_receive_probes(self):
        """COLD candidates must receive regular probes across 2,000 steps."""
        env = DynamicSparseLinearStream(self.config, seed=self.seed)
        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))
        ctrl = ProbeBankController(q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05, total_steps=2000, target_budget=10000)
        pol = TieredEvidenceRatePolicy(d=100, mode="two_tier", cold_fraction=0.35)
        learner = TieredEvidenceLearner(d=100, initial_support=list(init_supp), probe_policy=pol, q=5)

        for t in range(1, 2001):
            x, y, supp, _ = env.step()
            yh = learner.predict(x)
            err = y - yh
            q = ctrl.get_q(err, t)
            learner.update(x, y, q=q, true_support=supp)

        # In 2000 steps, cold probes should be at least 30% of 10,000 = 3000
        cold_probes = pol.probes_by_tier["COLD"]
        self.assertGreater(cold_probes, 2500, f"Cold probes was only {cold_probes}")
        # Every feature in d=100 should have been probed at least once
        for feat in range(100):
            self.assertIn(feat, learner.last_probed_step, f"Feature {feat} was never probed (starvation)!")

    def test_4_decay_demotes_stale_warm_candidates(self):
        """In J2, weak/stale warm candidates must demote back to COLD."""
        pol = TieredEvidenceRatePolicy(d=100, mode="two_tier_decay", n_hint=2, theta_hint=0.15, theta_decay=0.10, warm_max_probes=5)
        # Put candidate 10 into warm_set manually or via stats
        cand_stats = {
            "n": np.zeros(100),
            "mean": np.zeros(100),
            "m2": np.zeros(100),
            "pos": np.zeros(100),
            "neg": np.zeros(100),
            "current_step": 1
        }
        cand_stats["n"][10] = 2
        cand_stats["mean"][10] = 0.20
        cand_stats["pos"][10] = 2
        pol.on_probes_evaluated([10], cand_stats, active_support=set([1, 2, 3]))
        self.assertIn(10, pol.warm_set)

        # Now simulate 5 warm probes where correlation decays to 0.02
        cand_stats["mean"][10] = 0.02
        for _ in range(5):
            pol.on_probes_evaluated([10], cand_stats, active_support=set([1, 2, 3]))

        self.assertNotIn(10, pol.warm_set, "Candidate 10 should have demoted back to COLD due to decay/timeout!")

    def test_5_compute_remains_under_25_percent_dense(self):
        """Tiered learner compute must remain <= 25% of Dense (602 FLOPs * 0.25 = 150.5 FLOPs/step)."""
        env = DynamicSparseLinearStream(self.config, seed=self.seed)
        rng = np.random.RandomState(self.seed)
        init_supp = list(rng.choice(self.config["d_features"], size=self.config["k_true"], replace=False))
        ctrl = ProbeBankController(q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05, total_steps=2000, target_budget=10000)
        pol = TieredEvidenceRatePolicy(d=100, mode="three_tier")
        learner = TieredEvidenceLearner(d=100, initial_support=list(init_supp), probe_policy=pol, q=5)

        total_flops = 0
        for t in range(1, 2001):
            x, y, supp, _ = env.step()
            yh = learner.predict(x)
            err = y - yh
            q = ctrl.get_q(err, t)
            res = learner.update(x, y, q=q, true_support=supp)
            total_flops += res["flops"]

        mean_flops = total_flops / 2000.0
        dense_flops = 602.0
        pct_dense = (mean_flops / dense_flops) * 100.0
        self.assertLess(pct_dense, 25.0, f"Mean FLOPs was {mean_flops:.2f} ({pct_dense:.2f}% of Dense)")

if __name__ == "__main__":
    unittest.main()
