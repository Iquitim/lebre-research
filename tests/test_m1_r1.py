import os
import json
import pytest
import numpy as np
from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.diagnostics.frontier_evaluator import (
    compute_energy_metrics,
    classify_prediction_sufficient
)

EXP_DIR = os.path.join(os.path.dirname(__file__), "..", "experiments", "M1-R1")

def test_holdout_seeds_disjointness():
    """Verify holdout seeds are fresh, unique, 30 in total, and strictly disjoint from prior seeds."""
    seeds_path = os.path.join(EXP_DIR, "holdout_seeds.json")
    assert os.path.exists(seeds_path), f"Missing {seeds_path}"

    with open(seeds_path, "r") as f:
        data = json.load(f)

    seeds = data["seeds"]
    assert len(seeds) == 30, f"Expected 30 seeds, got {len(seeds)}"
    assert len(set(seeds)) == 30, "Holdout seeds contain duplicates!"

    prior_seeds = set(data.get("prior_seeds_excluded", [42, 123, 456, 789, 1024, 9999]))
    overlap = set(seeds).intersection(prior_seeds)
    assert len(overlap) == 0, f"Holdout seeds overlap with prior seeds: {overlap}"

def test_spectrum_energy_normalization():
    """Verify all coefficient spectra maintain approximately matched total energy (~7.28)."""
    cfg_path = os.path.join(EXP_DIR, "config.json")
    with open(cfg_path, "r") as f:
        cfg = json.load(f)

    target_energy = cfg["v1_spectra"]["target_energy"]
    spectra = cfg["v1_spectra"]["spectra"]

    for name, spec in spectra.items():
        e1 = sum(w ** 2 for w in spec["r1_weights"])
        e2 = sum(w ** 2 for w in spec["r2_weights"])
        mean_e = (e1 + e2) / 2.0
        # Energy must be within 5% of target energy
        assert abs(mean_e - target_energy) / target_energy < 0.05, (
            f"Spectrum {name} energy {mean_e:.3f} deviates from target {target_energy}"
        )

def test_threshold_metrics_logic():
    """Verify threshold evaluation calculation logic."""
    # Synthetic ground truth
    y_true_sufficient = np.array([True, True, True, False, False, False, True, False])
    scores = np.array([0.95, 0.85, 0.82, 0.78, 0.72, 0.65, 0.90, 0.74])

    theta = 0.80
    passes = scores >= theta  # [True, True, True, False, False, False, True, False] -> indices 0, 1, 2, 6 (all True in y_true)
    fails = ~passes           # indices 3, 4, 5, 7 (all False in y_true)

    p_suff_given_pass = y_true_sufficient[passes].mean()
    p_fail_given_fail = (~y_true_sufficient[fails]).mean()
    false_pass_rate = (~y_true_sufficient[passes]).mean()
    false_fail_rate = y_true_sufficient[fails].mean()

    assert p_suff_given_pass == 1.0
    assert p_fail_given_fail == 1.0
    assert false_pass_rate == 0.0
    assert false_fail_rate == 0.0

def test_frozen_baseline_invariance():
    """Confirm frozen learner produces exact canonical Seed 42 MSE."""
    cfg = {
        "d_features": 100,
        "k_star": 5,
        "noise_std": 0.1,
        "total_steps": 2000,
        "shift_step": 1000,
        "regime_1": {"indices": [2, 15, 33, 58, 81], "weights": [1.5, -1.2, 0.8, -1.0, 1.3]},
        "regime_2": {"indices": [7, 24, 49, 66, 92], "weights": [-1.4, 1.0, -1.1, 1.6, -0.9]}
    }
    env = DynamicSparseLinearStream(cfg, seed=42)
    rng_supp = np.random.RandomState(42)
    init_supp = list(rng_supp.choice(100, size=5, replace=False))

    pol = TieredEvidenceRatePolicy(
        d=100, mode="queue_multi_rate", c_max=3, n_screen=3, theta_screen=0.2, gamma_screen=0.75,
        theta_drop=0.1, gamma_drop=0.6, confirm_max_probes=12, w_max=5, h_max=2, n_hint=2,
        theta_hint=0.15, gamma_hint=0.6, warm_max_probes=10, hot_max_probes=12,
        cold_fraction=0.35, warm_fraction=0.65
    )
    lrn = TieredEvidenceLearner(
        d=100, initial_support=list(init_supp), probe_policy=pol, q=5,
        mu=0.5, eps=1e-6, n_min=8, theta_promote=0.40, grace_period=15,
        swap_threshold=0.05, victim_strategy="age_normalized", tau_mature=50,
        cooldown_steps=0, g_starve=100, k_max=10
    )
    ctrl = ProbeBankController(
        q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
        total_steps=2000, target_budget=10000
    )

    r2_losses = []
    for t in range(1, 2001):
        x, y, true_supp, _ = env.step()
        yh = lrn.predict(x)
        err = y - yh
        loss = err ** 2
        qt = ctrl.get_q(err, t)
        lrn.update(x, y, q=qt, true_support=true_supp)
        if t > 1800:
            r2_losses.append(loss)

    mean_r2 = float(np.mean(r2_losses))
    assert pytest.approx(mean_r2, 1e-5) == 0.011546915
