import pytest
import numpy as np
import pandas as pd
from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.diagnostics.frontier_evaluator import (
    compute_gamma,
    compute_gamma_resource,
    compute_energy_metrics,
    classify_regime_identifiability,
    classify_prediction_sufficient,
    classify_2x2_matrix,
    compute_metric_correlations
)

def test_gamma_calculation_properties():
    """Verify Gamma calculation increases with signal and sample size, decreases with noise and dimension."""
    g_base = compute_gamma(beta_min=1.0, sigma_residual=2.5, d_noise=95, n_effective=5.0)
    assert g_base > 0

    # 1. Higher signal -> higher Gamma
    g_high_sig = compute_gamma(beta_min=2.0, sigma_residual=2.5, d_noise=95, n_effective=5.0)
    assert g_high_sig > g_base

    # 2. Lower residual noise -> higher Gamma
    g_low_noise = compute_gamma(beta_min=1.0, sigma_residual=1.0, d_noise=95, n_effective=5.0)
    assert g_low_noise > g_base

    # 3. Higher dimension (more noise competitors) -> lower Gamma
    g_high_d = compute_gamma(beta_min=1.0, sigma_residual=2.5, d_noise=195, n_effective=5.0)
    assert g_high_d < g_base

    # 4. More effective probes -> higher Gamma
    g_more_probes = compute_gamma(beta_min=1.0, sigma_residual=2.5, d_noise=95, n_effective=20.0)
    assert g_more_probes > g_base

    # Resource normalized Gamma
    g_res = compute_gamma_resource(gamma=g_base, total_budget=10000, d_noise=95)
    assert g_res > g_base

def test_energy_weighted_metrics():
    """Verify energy-weighted recall and omitted energy match analytical values."""
    true_supp = {1, 3, 5}
    true_beta = np.zeros(10)
    true_beta[1] = 2.0  # energy = 4.0
    true_beta[3] = 1.0  # energy = 1.0
    true_beta[5] = 0.5  # energy = 0.25
    # Total energy = 5.25

    # Case 1: All recovered
    active_all = [1, 3, 5]
    omit_energy, ew_recall, raw_rec = compute_energy_metrics(active_all, true_supp, true_beta)
    assert pytest.approx(omit_energy, 1e-9) == 0.0
    assert pytest.approx(ew_recall, 1e-9) == 1.0
    assert pytest.approx(raw_rec, 1e-9) == 1.0

    # Case 2: Recovered dominant feature (1) only
    active_dom = [1, 8]
    omit_energy, ew_recall, raw_rec = compute_energy_metrics(active_dom, true_supp, true_beta)
    # Recovered energy = 4.0 / 5.25 = 0.7619
    assert pytest.approx(ew_recall, 1e-4) == 4.0 / 5.25
    assert pytest.approx(raw_rec, 1e-4) == 1.0 / 3.0  # 33.3% raw recall, but 76.2% energy recall!
    assert pytest.approx(omit_energy, 1e-4) == 1.25

    # Case 3: None recovered
    active_none = [8, 9]
    omit_energy, ew_recall, raw_rec = compute_energy_metrics(active_none, true_supp, true_beta)
    assert pytest.approx(omit_energy, 1e-4) == 5.25
    assert pytest.approx(ew_recall, 1e-4) == 0.0
    assert pytest.approx(raw_rec, 1e-4) == 0.0

def test_classification_logic():
    """Verify 2x2 matrix and identifiability labels."""
    # Identifiable
    lbl_id = classify_regime_identifiability(
        full_support_occupancy=0.85, t_evidence=50, t_post=60,
        final_recall=1.0, post_shift_mse=0.012, dense_mse=0.034, pct_dense_compute=23.5
    )
    assert lbl_id == "IDENTIFIABLE"

    # Partially Identifiable
    lbl_part = classify_regime_identifiability(
        full_support_occupancy=0.60, t_evidence=120, t_post=90,
        final_recall=0.95, post_shift_mse=0.014, dense_mse=0.034, pct_dense_compute=23.5
    )
    assert lbl_part == "PARTIALLY_IDENTIFIABLE"

    # Prediction Sufficient
    is_suff, is_strong = classify_prediction_sufficient(
        post_shift_mse=0.013, dense_mse=0.034, sparse_oracle_mse=0.0148, pct_dense_compute=23.5
    )
    assert is_suff is True
    assert is_strong is True

    # 2x2 Matrix
    assert classify_2x2_matrix("IDENTIFIABLE", True) == "A"
    assert classify_2x2_matrix("PARTIALLY_IDENTIFIABLE", True) == "B"
    assert classify_2x2_matrix("NON_IDENTIFIABLE_UNDER_BUDGET", True) == "B"
    assert classify_2x2_matrix("NON_IDENTIFIABLE_UNDER_BUDGET", False) == "D"

def test_canonical_baseline_bit_for_bit_match():
    """Verify that canonical baseline reproduces Seed 42 exact MSE and occupancy."""
    config = {
        "d_features": 100,
        "k_star": 5,
        "k_slack_max": 10,
        "noise_std": 0.1,
        "total_steps": 2000,
        "shift_step": 1000,
        "q_min": 1,
        "q_base": 5,
        "q_max": 8,
        "tau_low": 0.05,
        "tau_high": 0.50,
        "ema_alpha": 0.05,
        "nlms_mu": 0.5,
        "nlms_eps": 1e-6,
        "n_min_baseline": 8,
        "theta_promote": 0.40,
        "grace_period": 15,
        "swap_threshold": 0.05,
        "victim_strategy": "age_normalized",
        "tau_mature": 50,
        "cooldown_steps": 0,
        "c_max": 3,
        "n_screen": 3,
        "theta_screen": 0.20,
        "gamma_screen": 0.75,
        "theta_drop": 0.10,
        "gamma_drop": 0.60,
        "confirm_max_probes": 12,
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
        "g_starve": 100,
        "target_total_probes": 10000,
        "regime_1": {
            "indices": [2, 15, 33, 58, 81],
            "weights": [1.5, -1.2, 0.8, -1.0, 1.3]
        },
        "regime_2": {
            "indices": [7, 24, 49, 66, 92],
            "weights": [-1.4, 1.0, -1.1, 1.6, -0.9]
        }
    }

    env = DynamicSparseLinearStream(config, seed=42)
    rng = np.random.RandomState(42)
    init_supp = list(rng.choice(100, size=5, replace=False))

    ctrl = ProbeBankController(
        q_min=1, q_base=5, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05,
        total_steps=2000, target_budget=10000
    )
    pol = TieredEvidenceRatePolicy(
        d=100, mode="queue_multi_rate", c_max=3, n_screen=3, theta_screen=0.2, gamma_screen=0.75,
        theta_drop=0.1, gamma_drop=0.6, confirm_max_probes=12, w_max=5, h_max=2, n_hint=2,
        theta_hint=0.15, gamma_hint=0.6, theta_decay=0.1, warm_max_probes=10, hot_max_probes=12,
        theta_hot=0.25, gamma_hot=0.75, cold_fraction=0.35, warm_fraction=0.65
    )
    lrn = TieredEvidenceLearner(
        d=100, initial_support=list(init_supp), probe_policy=pol, q=5,
        mu=0.5, eps=1e-6, n_min=8, theta_promote=0.40, grace_period=15,
        swap_threshold=0.05, victim_strategy="age_normalized", tau_mature=50,
        cooldown_steps=0, g_starve=100
    )

    r2_losses = []
    occupancies = []

    for t in range(1, 2001):
        x, y, true_supp, _ = env.step()
        yh = lrn.predict(x)
        err = y - yh
        loss = err ** 2

        q_t = ctrl.get_q(err, t)
        lrn.update(x, y, q=q_t, true_support=true_supp)

        if t > 1000:
            active_set = set(lrn.support)
            overlap = len(active_set.intersection(true_supp))
            occupancy = 1.0 if overlap == len(true_supp) else 0.0
            occupancies.append(occupancy)
        if t > 1800:
            r2_losses.append(loss)

    mean_r2 = float(np.mean(r2_losses))
    mean_occ = float(np.mean(occupancies))

    # Bit-for-bit check
    assert pytest.approx(mean_r2, 1e-5) == 0.011546915
    assert pytest.approx(mean_occ, 1e-4) == 0.5780
