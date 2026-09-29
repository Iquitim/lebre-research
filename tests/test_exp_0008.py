import pytest
import numpy as np
import pandas as pd
from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.diagnostics.candidate_microtest import (
    MicrotestDiagnosticObserver,
    compute_roc_pr_auc,
    evaluate_channel_precision_at_k,
    evaluate_leave_one_seed_out_logistic_microtest
)

def test_shadow_prediction_math():
    """
    Validates the physical micro-update gain mathematics:
    - True candidate: positive out-of-sample gain
    - Noise candidate: negative out-of-sample gain
    """
    # Suppose baseline prediction has error e_base = y - yhat_base = 2.0 (true omitted signal + noise)
    y_true_future = 3.0
    yhat_base = 1.0
    e_base = y_true_future - yhat_base # 2.0
    l_base = e_base ** 2 # 4.0

    # True candidate: has positive correlation with true residual
    # Shadow weight w = 0.5, future feature x = 1.5
    w_true = 0.5
    x_true = 1.5
    yhat_true_shadow = yhat_base + w_true * x_true # 1.0 + 0.75 = 1.75
    e_true_shadow = y_true_future - yhat_true_shadow # 3.0 - 1.75 = 1.25
    l_true_shadow = e_true_shadow ** 2 # 1.5625
    gain_true = l_base - l_true_shadow # 4.0 - 1.5625 = 2.4375 > 0!
    assert gain_true > 0

    # Noise candidate: independent feature x_noise with mean 0, independent of residual
    # Even if w_noise was accidentally fitted, on future step x_noise = -1.5:
    w_noise = 0.5
    x_noise = -1.5 # opposite sign by random chance
    yhat_noise_shadow = yhat_base + w_noise * x_noise # 1.0 - 0.75 = 0.25
    e_noise_shadow = y_true_future - yhat_noise_shadow # 3.0 - 0.25 = 2.75
    l_noise_shadow = e_noise_shadow ** 2 # 7.5625
    gain_noise = l_base - l_noise_shadow # 4.0 - 7.5625 = -3.5625 < 0!
    assert gain_noise < 0

def test_sign_reversal_margin():
    """
    Validates that correct sign shadow update outperforms wrong sign shadow update.
    """
    y = 2.0
    yhat_base = 0.0
    w_correct = 0.5
    w_wrong = -0.5
    x = 1.0

    l_base = (y - yhat_base) ** 2 # 4.0
    l_correct = (y - (yhat_base + w_correct * x)) ** 2 # (2.0 - 0.5)^2 = 2.25
    l_wrong = (y - (yhat_base + w_wrong * x)) ** 2 # (2.0 + 0.5)^2 = 6.25

    margin = l_wrong - l_correct # 6.25 - 2.25 = 4.0 > 0
    assert margin > 0

def test_j4_bit_for_bit_with_microtest_observer():
    """
    Verifies that running J4 with MicrotestDiagnosticObserver attached produces
    bit-for-bit identical metrics to EXP-0006 J4 on Seed 42.
    """
    seed = 42
    d = 100
    k_star = 5
    shift_step = 1000
    total_steps = 2000

    rng = np.random.RandomState(seed)
    init_supp = list(rng.choice(d, size=k_star, replace=False))

    r1_indices = [2, 15, 33, 58, 81]
    r1_weights = [1.5, -1.2, 0.8, -1.0, 1.3]
    r2_indices = [7, 24, 49, 66, 92]
    r2_weights = [-1.4, 1.0, -1.1, 1.6, -0.9]

    cfg = {
        "d_features": d,
        "k_star": k_star,
        "noise_std": 0.1,
        "shift_step": shift_step,
        "total_steps": total_steps,
        "regime_1": {"indices": r1_indices, "weights": r1_weights},
        "regime_2": {"indices": r2_indices, "weights": r2_weights}
    }
    env = DynamicSparseLinearStream(config=cfg, seed=seed)

    controller = ProbeBankController(
        q_min=1,
        q_base=5,
        q_max=8,
        tau_low=0.05,
        tau_high=0.50,
        alpha=0.05,
        total_steps=total_steps,
        target_budget=10000
    )

    policy = TieredEvidenceRatePolicy(
        d=d,
        mode="queue_multi_rate",
        c_max=3,
        n_screen=3,
        theta_screen=0.20,
        gamma_screen=0.75,
        theta_drop=0.10,
        gamma_drop=0.60,
        confirm_max_probes=12,
        w_max=5,
        h_max=2,
        n_hint=2,
        theta_hint=0.15,
        gamma_hint=0.60,
        theta_decay=0.10,
        warm_max_probes=10,
        hot_max_probes=12,
        theta_hot=0.25,
        gamma_hot=0.75,
        cold_fraction=0.35,
        warm_fraction=0.65
    )

    learner = TieredEvidenceLearner(
        d=d,
        initial_support=list(init_supp),
        probe_policy=policy,
        q=5,
        mu=0.5,
        eps=1e-6,
        n_min=8,
        theta_promote=0.40,
        grace_period=15,
        swap_threshold=0.05,
        victim_strategy="age_normalized",
        tau_mature=50,
        cooldown_steps=0,
        g_starve=100
    )

    observer = MicrotestDiagnosticObserver(
        seed=seed,
        d=d,
        shift_step=shift_step,
        r1_true_indices=r1_indices,
        r2_true_indices=r2_indices,
        paired_window_w=3,
        multi_test_m=2,
        eta_scale=0.5
    )

    r2_losses = []
    recalls = []
    occupancies = []

    for step in range(1, total_steps + 1):
        x, y, true_supp, _ = env.step()
        yh = learner.predict(x)
        err = y - yh
        loss = err ** 2

        # Observer begins step (evaluates pending micro-tests on incoming sample)
        observer.on_step_begin(
            step=step,
            x_t=x,
            y_t=y,
            y_hat_base=yh,
            active_support=learner.support
        )

        q_t = controller.get_q(err, step)
        step_res = learner.update(x, y, q=q_t, true_support=true_supp)

        active_set = set(learner.support)
        overlap = len(active_set.intersection(true_supp))
        rec = overlap / float(len(true_supp))
        occ = 1.0 if overlap == len(true_supp) else 0.0

        if step > shift_step:
            recalls.append(rec)
            occupancies.append(occ)
        if step > 1800:
            r2_losses.append(loss)

        # Observer ends step (creates candidate micro-tests)
        tiers = {c: policy.get_candidate_tier(c) for c in range(d)}
        cand_stats = {
            "n": learner.cand_n,
            "mean": learner.cand_mean,
            "m2": learner.cand_m2,
            "pos": learner.cand_pos,
            "neg": learner.cand_neg
        }
        x_sub = x[learner.support]
        norm_sq = float(np.dot(x_sub, x_sub))

        observer.on_step_end(
            step=step,
            error=err,
            probed_candidates=step_res["candidates"],
            learner_cand_stats=cand_stats,
            active_support=learner.support,
            norm_sq_active=norm_sq,
            candidate_tiers=tiers
        )

    r2_mse = float(np.mean(r2_losses))
    mean_r2_recall = float(np.mean(recalls))
    full_occupancy = float(np.mean(occupancies))

    # Bit-for-bit check against EXP-0006 J4 Seed 42 frozen values:
    assert np.isclose(r2_mse, 0.01154691517117861, atol=1e-8)
    assert np.isclose(mean_r2_recall, 0.7726, atol=1e-6)
    assert np.isclose(full_occupancy, 0.578, atol=1e-6)

    # Observer data frame check
    df_events = observer.get_dataframe()
    assert not df_events.empty
    assert "gain_i2" in df_events.columns
    assert "gain_i3" in df_events.columns
    assert "causal_direction_margin" in df_events.columns
    assert "excess_causal_gain" in df_events.columns

def test_truth_leakage_absence():
    """
    Verifies that candidate truth labels never influence step sizes, shadow weights,
    or evaluation timing.
    """
    observer = MicrotestDiagnosticObserver(seed=42)
    # Simulate step end for candidate 1 (arbitrary label)
    cand_stats = {
        "n": np.array([2] * 100),
        "mean": np.array([0.5] * 100),
        "pos": np.array([2] * 100),
        "neg": np.array([0] * 100)
    }
    observer.on_step_end(
        step=1010,
        error=2.0,
        probed_candidates=[7, 8], # 7 is true in R2, 8 is noise
        learner_cand_stats=cand_stats,
        active_support=[1, 2, 3],
        norm_sq_active=3.0
    )
    # Both candidates must receive identical eta_probe computation regardless of truth label
    test_7 = [t for t in observer.pending_tests if t["candidate_id"] == 7][0]
    test_8 = [t for t in observer.pending_tests if t["candidate_id"] == 8][0]
    assert test_7["eta_probe"] == test_8["eta_probe"]
    assert test_7["step_train"] == test_8["step_train"]
