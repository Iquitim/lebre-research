import pytest
import numpy as np
import pandas as pd
from src.diagnostics.candidate_separability import (
    CandidateSnapshotCollector,
    compute_diagnostic_scores,
    compute_roc_pr_auc,
    compute_distribution_stats,
    evaluate_precision_at_k,
    evaluate_temporal_stratification,
    evaluate_residual_stratification,
    evaluate_rank_stability,
    evaluate_leave_one_seed_out_logistic
)
from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController

def test_roc_pr_auc_exact():
    y_true = np.array([1, 1, 0, 0])
    y_score = np.array([0.9, 0.8, 0.2, 0.1])
    roc, pr = compute_roc_pr_auc(y_true, y_score)
    assert roc == 1.0
    assert pr == 1.0

    # Inverted
    y_score_inv = np.array([0.1, 0.2, 0.8, 0.9])
    roc_inv, pr_inv = compute_roc_pr_auc(y_true, y_score_inv)
    assert roc_inv == 0.0

def test_diagnostic_scores():
    data = {
        "candidate_id": [1, 2],
        "seed": [42, 42],
        "step": [1010, 1020],
        "probe_count": [4, 4],
        "truth_label": [1, 0],
        "mean_corr": [0.20, -0.10],
        "abs_mean_corr": [0.20, 0.10],
        "variance_corr": [0.04, 0.01],
        "std_corr": [0.20, 0.10],
        "sign_consistency": [0.75, 0.50],
        "positive_fraction": [0.75, 0.50],
        "negative_fraction": [0.25, 0.50],
        "last_probe_gap": [5, 10],
        "mean_probe_gap": [5.0, 10.0],
        "candidate_age": [20, 40],
        "time_since_first_probe": [20, 40],
        "current_residual_abs": [0.5, 0.5],
        "current_residual_sq": [0.25, 0.25],
        "smoothed_residual": [0.4, 0.4],
        "smoothed_residual_sq": [0.16, 0.16],
        "candidate_tier": ["WARM", "COLD"],
        "candidate_state": ["ACTIVE_CANDIDATE", "ACTIVE_CANDIDATE"],
        "current_active_support_recall": [0.4, 0.4],
        "current_support_size": [10, 10]
    }
    df = pd.DataFrame(data)
    df_scored = compute_diagnostic_scores(df)

    # Check S0: |mean_corr|
    assert np.isclose(df_scored["S0"].iloc[0], 0.20)
    assert np.isclose(df_scored["S0"].iloc[1], 0.10)

    # Check S1: sign_consistency
    assert np.isclose(df_scored["S1"].iloc[0], 0.75)

    # Check S2: |mean_corr| * sign_consistency
    assert np.isclose(df_scored["S2"].iloc[0], 0.20 * 0.75)

    # Check S3: |mean_corr| / (std + eps)
    assert np.isclose(df_scored["S3"].iloc[0], 0.20 / (0.20 + 1e-6))

    # Check S4: sqrt(n) * |mean_corr| -> 2 * 0.20 = 0.40
    assert np.isclose(df_scored["S4"].iloc[0], 2.0 * 0.20)

    # Check S5: sqrt(n) * |mean_corr| * sign_consistency -> 2 * 0.20 * 0.75 = 0.30
    assert np.isclose(df_scored["S5"].iloc[0], 2.0 * 0.20 * 0.75)

def test_precision_at_k_and_enrichment():
    # 2 seeds, 10 candidates each, 2 true candidates per seed (base rate = 0.20)
    rows = []
    for s in [42, 123]:
        for c in range(10):
            is_true = 1 if c < 2 else 0
            # score gives true candidates higher scores
            score = 1.0 - 0.05 * c if is_true else 0.5 - 0.05 * c
            rows.append({
                "candidate_id": c,
                "seed": s,
                "step": 1050,
                "probe_count": 3,
                "truth_label": is_true,
                "score": score
            })
    df = pd.DataFrame(rows)
    res = evaluate_precision_at_k(df, "score", k_values=(1, 2, 3), post_shift_only=False)

    # Top 1 and 2 are always true candidates
    assert np.isclose(res["precision_at_k"][1], 1.0)
    assert np.isclose(res["precision_at_k"][2], 1.0)
    # Top 3 has 2 true and 1 noise -> 2/3
    assert np.isclose(res["precision_at_k"][3], 2.0 / 3.0)
    # Base rate is 0.20
    assert np.isclose(res["mean_base_rate"], 0.20)
    # Enrichment@1 = 1.0 / 0.20 = 5.0x
    assert np.isclose(res["enrichment_at_k"][1], 5.0)

def test_j4_bit_for_bit_reproducibility():
    """
    Verifies that running J4 with CandidateSnapshotCollector attached produces
    identical bit-for-bit metrics to EXP-0006 J4 on Seed 42.
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

    collector = CandidateSnapshotCollector(
        seed=seed,
        d=d,
        shift_step=shift_step,
        r1_true_indices=r1_indices,
        r2_true_indices=r2_indices
    )

    r2_losses = []
    recalls = []
    occupancies = []

    for step in range(1, total_steps + 1):
        x, y, true_supp, _ = env.step()
        yh = learner.predict(x)
        err = y - yh
        loss = err ** 2
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

        # Capture tiers for collector
        tiers = {c: policy.get_candidate_tier(c) for c in range(d)}
        cand_stats = {
            "n": learner.cand_n,
            "mean": learner.cand_mean,
            "m2": learner.cand_m2,
            "pos": learner.cand_pos,
            "neg": learner.cand_neg
        }
        collector.observe_step(
            step=step,
            error=err,
            probed_candidates=step_res["candidates"],
            learner_cand_stats=cand_stats,
            active_support=learner.support,
            candidate_tiers=tiers
        )

    r2_mse = float(np.mean(r2_losses))
    mean_r2_recall = float(np.mean(recalls))
    full_occupancy = float(np.mean(occupancies))

    # Frozen EXP-0006 J4 Seed 42 values from seed_summaries.csv:
    # regime_2_mse: 0.01154691517117861
    # mean_r2_recall: 0.7726
    # full_support_occupancy: 0.578
    assert np.isclose(r2_mse, 0.01154691517117861, atol=1e-8)
    assert np.isclose(mean_r2_recall, 0.7726, atol=1e-6)
    assert np.isclose(full_occupancy, 0.578, atol=1e-6)

    # Verify collector captured snapshots at n=1..5
    df_snaps = collector.get_dataframe()
    assert not df_snaps.empty
    assert set(df_snaps["probe_count"].unique()) == {1, 2, 3, 4, 5}
    assert "S0" in df_snaps.columns
    assert "S5" in df_snaps.columns

def test_leave_one_seed_out_logistic():
    # Synthetic test dataset across 3 seeds
    rows = []
    for s in [42, 123, 456]:
        for i in range(20):
            is_true = 1 if i < 4 else 0
            rows.append({
                "candidate_id": i,
                "seed": s,
                "step": 1050,
                "probe_count": 3,
                "truth_label": is_true,
                "abs_mean_corr": 0.3 if is_true else 0.05,
                "std_corr": 0.1 if is_true else 0.2,
                "sign_consistency": 0.8 if is_true else 0.5,
                "smoothed_residual": 0.4
            })
    df = pd.DataFrame(rows)
    pred_df, summary = evaluate_leave_one_seed_out_logistic(df)
    assert len(pred_df) == len(df)
    assert summary["roc_auc"] > 0.80
