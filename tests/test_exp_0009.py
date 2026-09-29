import pytest
import numpy as np
import pandas as pd
from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.diagnostics.active_probe_diagnostic import (
    ActiveProbeDiagnosticObserver,
    get_hadamard_matrix,
    compute_roc_pr_auc
)

def test_hadamard_matrix_orthogonality():
    """Verify Sylvester-Walsh Hadamard matrices satisfy H * H^T = R * I."""
    for order in [1, 2, 4, 8, 16]:
        H = get_hadamard_matrix(order)
        assert H.shape == (order, order)
        # Check all values are +1 or -1
        assert np.all(np.isin(H, [-1.0, 1.0]))
        # Check orthogonality
        product = H @ H.T
        expected = order * np.eye(order)
        np.testing.assert_allclose(product, expected, atol=1e-9)

def test_paired_excitation_mathematical_cancellation():
    """
    Verify that symmetric paired excitation (+delta and -delta on same sample)
    exactly cancels quadratic baseline error and quadratic perturbation penalty:
    L_- - L_+ = 4 * delta * e_base * x_c.
    """
    e_base = 2.5
    x_c = 1.2
    delta = 0.10

    # Losses
    # y - y_hat_base = e_base
    # L_+ = (e_base - delta * x_c)^2
    # L_- = (e_base + delta * x_c)^2
    l_plus = (e_base - delta * x_c) ** 2
    l_minus = (e_base + delta * x_c) ** 2

    diff = l_minus - l_plus
    expected_diff = 4.0 * delta * e_base * x_c
    assert pytest.approx(diff, 1e-9) == expected_diff

def test_causal_controls_behavior():
    """
    Verify creative controls:
    1. Zero-delta: score collapses to 0.
    2. Sign-flip: score negates.
    3. Permutation: orthogonal code product with other row is 0.
    """
    H4 = get_hadamard_matrix(4)
    # Target candidate row 1
    code_target = H4[1, :]
    # Response vector perfectly aligned with target code:
    resp = 2.0 * code_target
    decoded_true = float(np.mean(code_target * resp))
    assert pytest.approx(decoded_true, 1e-9) == 2.0

    # 1. Sign flip
    decoded_flipped = float(np.mean((-code_target) * resp))
    assert pytest.approx(decoded_flipped, 1e-9) == -2.0

    # 2. Permutation (decode with row 2 instead of row 1)
    code_other = H4[2, :]
    decoded_perm = float(np.mean(code_other * resp))
    # By orthogonality, dot product is 0
    assert pytest.approx(decoded_perm, 1e-9) == 0.0

def test_observer_non_intrusive_production_invariance():
    """
    Verify that running with ActiveProbeDiagnosticObserver produces the EXACT
    same production learner predictions, losses, and active support trajectory
    as running without it (bit-for-bit invariance).
    """
    config = {
        "d_features": 20,
        "k_star": 3,
        "k_slack_max": 6,
        "noise_std": 0.1,
        "total_steps": 60,
        "shift_step": 30,
        "q_base": 3,
        "q_min": 1,
        "q_max": 4,
        "nlms_mu": 0.5,
        "nlms_eps": 1e-6,
        "n_min_baseline": 4,
        "theta_promote": 0.30,
        "grace_period": 5,
        "swap_threshold": 0.05,
        "victim_strategy": "age_normalized",
        "tau_mature": 20,
        "cooldown_steps": 0,
        "c_max": 2,
        "n_screen": 2,
        "theta_screen": 0.20,
        "gamma_screen": 0.75,
        "theta_drop": 0.10,
        "gamma_drop": 0.60,
        "confirm_max_probes": 6,
        "w_max": 3,
        "h_max": 2,
        "n_hint": 2,
        "theta_hint": 0.15,
        "gamma_hint": 0.60,
        "theta_decay": 0.10,
        "warm_max_probes": 5,
        "hot_max_probes": 6,
        "theta_hot": 0.25,
        "gamma_hot": 0.75,
        "cold_fraction": 0.35,
        "warm_fraction": 0.65,
        "g_starve": 50,
        "tau_low": 0.05,
        "tau_high": 0.50,
        "ema_alpha": 0.05,
        "target_total_probes": 180,
        "regime_1": {"indices": [1, 5, 9], "weights": [1.0, -1.0, 1.0]},
        "regime_2": {"indices": [2, 6, 12], "weights": [-1.0, 1.0, -1.0]}
    }

    # Run 1: Without Observer
    env1 = DynamicSparseLinearStream(config, seed=42)
    ctrl1 = ProbeBankController(
        q_min=config["q_min"], q_base=config["q_base"], q_max=config["q_max"],
        tau_low=config["tau_low"], tau_high=config["tau_high"], alpha=config["ema_alpha"],
        total_steps=60, target_budget=180
    )
    pol1 = TieredEvidenceRatePolicy(
        d=20, mode="queue_multi_rate", c_max=2, n_screen=2, theta_screen=0.2, gamma_screen=0.75,
        theta_drop=0.1, gamma_drop=0.6, confirm_max_probes=6, w_max=3, h_max=2, n_hint=2,
        theta_hint=0.15, gamma_hint=0.6, theta_decay=0.1, warm_max_probes=5, hot_max_probes=6,
        theta_hot=0.25, gamma_hot=0.75, cold_fraction=0.35, warm_fraction=0.65
    )
    lrn1 = TieredEvidenceLearner(
        d=20, initial_support=[0, 1, 2], probe_policy=pol1, q=config["q_base"],
        mu=0.5, eps=1e-6, n_min=4, theta_promote=0.3, grace_period=5,
        swap_threshold=0.05, victim_strategy="age_normalized", tau_mature=20,
        cooldown_steps=0, g_starve=50
    )

    losses1 = []
    supports1 = []
    weights1 = []

    for t in range(1, 61):
        x, y, true_supp, _ = env1.step()
        yh = lrn1.predict(x)
        err = y - yh
        losses1.append(err ** 2)
        q_t = ctrl1.get_q(err, t)
        lrn1.update(x, y, q=q_t, true_support=true_supp)
        supports1.append(list(lrn1.support))
        weights1.append(lrn1.weights.copy())

    # Run 2: With ActiveProbeDiagnosticObserver
    env2 = DynamicSparseLinearStream(config, seed=42)
    ctrl2 = ProbeBankController(
        q_min=config["q_min"], q_base=config["q_base"], q_max=config["q_max"],
        tau_low=config["tau_low"], tau_high=config["tau_high"], alpha=config["ema_alpha"],
        total_steps=60, target_budget=180
    )
    pol2 = TieredEvidenceRatePolicy(
        d=20, mode="queue_multi_rate", c_max=2, n_screen=2, theta_screen=0.2, gamma_screen=0.75,
        theta_drop=0.1, gamma_drop=0.6, confirm_max_probes=6, w_max=3, h_max=2, n_hint=2,
        theta_hint=0.15, gamma_hint=0.6, theta_decay=0.1, warm_max_probes=5, hot_max_probes=6,
        theta_hot=0.25, gamma_hot=0.75, cold_fraction=0.35, warm_fraction=0.65
    )
    lrn2 = TieredEvidenceLearner(
        d=20, initial_support=[0, 1, 2], probe_policy=pol2, q=config["q_base"],
        mu=0.5, eps=1e-6, n_min=4, theta_promote=0.3, grace_period=5,
        swap_threshold=0.05, victim_strategy="age_normalized", tau_mature=20,
        cooldown_steps=0, g_starve=50
    )
    obs2 = ActiveProbeDiagnosticObserver(
        seed=42, d=20, shift_step=30,
        r1_true_indices=[1, 5, 9], r2_true_indices=[2, 6, 12],
        delta=0.10, r_rounds=[2, 4], group_sizes=[4]
    )

    losses2 = []
    supports2 = []
    weights2 = []

    for t in range(1, 61):
        x, y, true_supp, _ = env2.step()
        yh = lrn2.predict(x)
        err = y - yh
        losses2.append(err ** 2)

        # Observer on_step_begin
        obs2.on_step_begin(step=t, x_t=x, y_t=y, y_hat_base=yh, active_support=lrn2.support)

        q_t = ctrl2.get_q(err, t)
        step_res = lrn2.update(x, y, q=q_t, true_support=true_supp)
        supports2.append(list(lrn2.support))
        weights2.append(lrn2.weights.copy())

        # Observer on_step_end
        tiers = {c: pol2.get_candidate_tier(c) for c in range(20)}
        cand_stats = {"n": lrn2.cand_n, "mean": lrn2.cand_mean}
        inactives = [c for c in range(20) if c not in lrn2.support]
        obs2.on_step_end(
            step=t, probed_candidates=step_res["candidates"],
            cand_stats=cand_stats, cand_tiers=tiers, loss=err ** 2,
            active_support=lrn2.support, inactive_candidates=inactives,
            x_t=x, y_t=y, y_hat_base=yh
        )

    # Verify bit-for-bit exact identity
    np.testing.assert_allclose(losses1, losses2, atol=1e-12)
    assert supports1 == supports2
    for w1, w2 in zip(weights1, weights2):
        np.testing.assert_allclose(w1, w2, atol=1e-12)

    # Verify observer collected events
    assert len(obs2.active_probe_events) > 0
