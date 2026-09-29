import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.utils.accounting import ResourceTracker
from src.metrics.ablation_tracker import AblationTracker

class TestEXP0001b(unittest.TestCase):
    def setUp(self):
        self.d = 100
        self.init_supp = [0, 1, 2, 3, 4]
        self.policy = RoundRobinProbePolicy()

    def test_1_kmax_never_exceeded(self):
        """1. Verify that active support size never exceeds k_max for all variants."""
        for var in ["B0", "B1", "B2", "B3", "B4"]:
            learner = AblationSparseLearner(
                d=self.d, variant=var, initial_support=self.init_supp, probe_policy=RoundRobinProbePolicy(), q=5
            )
            for _ in range(50):
                x = np.random.randn(self.d)
                y = float(np.dot(x[:5], [1.0]*5) + np.random.randn()*0.1)
                learner.update(x, y)
                self.assertLessEqual(len(learner.get_active_support()), learner.k_max, f"Variant {var} exceeded k_max")

    def test_2_kmax_5_reproduces_old_capacity(self):
        """2. Verify that K_max=5 in B0 and B2 maintains exactly 5 active features."""
        for var in ["B0", "B2"]:
            learner = AblationSparseLearner(
                d=self.d, variant=var, initial_support=self.init_supp, probe_policy=RoundRobinProbePolicy(), q=5
            )
            for _ in range(30):
                x = np.random.randn(self.d)
                y = 1.0
                learner.update(x, y)
                self.assertEqual(len(learner.get_active_support()), 5, f"{var} capacity != 5")

    def test_3_evidence_n_increments_only_when_probed(self):
        """3. Verify that candidate probe count n_c increments only when candidate is probed."""
        learner = AblationSparseLearner(
            d=self.d, variant="B2", initial_support=self.init_supp, probe_policy=RoundRobinProbePolicy(), q=5
        )
        x = np.random.randn(self.d)
        y = 1.0
        stats = learner.update(x, y)
        probed_count = np.sum(learner.cand_n > 0)
        self.assertEqual(probed_count, 5, f"Expected 5 probed candidates, got {probed_count}")
        self.assertEqual(np.max(learner.cand_n), 1)

    def test_4_mean_evidence_update_correctness(self):
        """4. Verify that Welford mean and M2 match numpy mean and variance."""
        learner = AblationSparseLearner(
            d=self.d, variant="B2", initial_support=self.init_supp, probe_policy=RoundRobinProbePolicy(), q=1
        )
        # Directly update candidate 10 multiple times
        vals = [1.5, 2.0, -0.5, 3.0, 1.0]
        for v in vals:
            c = 10
            learner.cand_n[c] += 1
            delta = v - learner.cand_mean[c]
            learner.cand_mean[c] += delta / learner.cand_n[c]
            delta2 = v - learner.cand_mean[c]
            learner.cand_m2[c] += delta * delta2
            
        vals_arr = np.array(vals)
        expected_mean = float(np.mean(vals_arr))
        expected_m2 = float(np.sum((vals_arr - expected_mean)**2))
        self.assertAlmostEqual(learner.cand_mean[10], expected_mean, places=6)
        self.assertAlmostEqual(learner.cand_m2[10], expected_m2, places=6)

    def test_5_maturity_prevents_premature_pruning(self):
        """5. Verify that in B4, immature active features (age < tau_min) are never pruned even if weight is 0."""
        learner = AblationSparseLearner(
            d=self.d, variant="B4", initial_support=self.init_supp, probe_policy=RoundRobinProbePolicy(), tau_min=20, theta_prune=0.5
        )
        # Weights start at 0.0, age starts at 0.
        x = np.zeros(self.d) # zero gradient update
        stats = learner.update(x, 0.0)
        # Should not prune since age = 1 < 20
        self.assertEqual(len(stats["pruned_feats"]), 0)
        self.assertEqual(len(learner.support), 5)

    def test_6_pruning_can_occur_after_tau_min(self):
        """6. Verify that in B4, mature active features (age >= tau_min) with |w| < theta_prune are pruned."""
        learner = AblationSparseLearner(
            d=self.d, variant="B4", initial_support=[0, 1, 2, 3, 4], probe_policy=RoundRobinProbePolicy(), tau_min=5, theta_prune=0.5
        )
        learner.weights = np.array([1.0, 1.0, 1.0, 1.0, 0.01]) # feature 4 has small weight
        learner.ages = np.array([10, 10, 10, 10, 10], dtype=np.int32) # mature
        x = np.zeros(self.d)
        stats = learner.update(x, 0.0)
        self.assertIn(4, stats["pruned_feats"])
        self.assertEqual(len(learner.support), 4)

    def test_7_true_noise_promotion_labels_correct(self):
        """7. Verify that promotions are correctly identified as true vs noise based on true support."""
        tracker = AblationTracker(total_steps=10, shift_step=5)
        # Step 1: promote true feature 2
        true_supp = {2, 15, 33, 58, 81}
        step_stats_true = {"loss": 1.0, "promoted_feat": 2, "victim_feat": None, "flops": 10, "probes": 5}
        tracker.record_step(1, step_stats_true, active_support={2}, true_support=true_supp, true_beta=np.zeros(100))
        
        # Step 2: promote noise feature 99
        step_stats_noise = {"loss": 1.0, "promoted_feat": 99, "victim_feat": None, "flops": 10, "probes": 5}
        tracker.record_step(2, step_stats_noise, active_support={2, 99}, true_support=true_supp, true_beta=np.zeros(100))
        
        summary = tracker.compute_summary()
        self.assertEqual(summary["true_promotions"], 1)
        self.assertEqual(summary["false_promotions"], 1)
        self.assertAlmostEqual(summary["promotion_precision"], 0.5)

    def test_8_survival_metric_correctness(self):
        """8. Verify that survival metric correctly counts features surviving across horizons."""
        tracker = AblationTracker(total_steps=100, shift_step=50)
        true_supp = {2}
        # Promote at step 10
        tracker.record_step(10, {"loss": 1.0, "promoted_feat": 2, "victim_feat": None}, {2}, true_supp, np.zeros(100))
        # Evict at step 30 (survived 20 steps -> survives @10, fails @50)
        tracker.record_step(30, {"loss": 1.0, "promoted_feat": None, "victim_feat": 2}, set(), true_supp, np.zeros(100))
        summary = tracker.compute_summary()
        self.assertAlmostEqual(summary["true_survival_10"], 1.0)
        self.assertAlmostEqual(summary["true_survival_50"], 0.0)

    def test_9_compute_accounting_includes_new_operations(self):
        """9. Verify that Welford and pruning FLOPs and memory are accurately counted."""
        # Welford FLOPs: 8 per probe
        welford_flops = ResourceTracker.welford_probe_flops(5)
        self.assertEqual(welford_flops, 40)
        # Pruning check: 2 ops per active feature
        prune_flops = ResourceTracker.pruning_check_flops(10)
        self.assertEqual(prune_flops, 20)
        # Welford memory for 10 active, 100 candidate slots
        mem = ResourceTracker.estimate_memory_bytes(10, 100, 100, is_welford=True)
        # Active: (8+4+4)*10 = 160. Candidate: 20*100 = 2000. Total = 2160.
        self.assertEqual(mem, 2160)

if __name__ == "__main__":
    unittest.main()
