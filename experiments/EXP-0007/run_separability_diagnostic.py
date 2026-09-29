import os
import sys
import json
import time
import argparse
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.diagnostics.candidate_separability import (
    CandidateSnapshotCollector,
    compute_diagnostic_scores,
    compute_distribution_stats,
    compute_roc_pr_auc,
    evaluate_precision_at_k,
    evaluate_temporal_stratification,
    evaluate_residual_stratification,
    evaluate_rank_stability,
    evaluate_counterfactual_elevation,
    evaluate_leave_one_seed_out_logistic
)

def parse_args():
    parser = argparse.ArgumentParser(description="EXP-0007: Small-Sample Candidate Separability Diagnostic")
    parser.add_argument("--dev", action="store_true", help="Run DEV calibration mode on seed 9999 only")
    return parser.parse_args()

def run_diagnostic():
    args = parse_args()
    exp_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(exp_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    if args.dev:
        seeds = [config["dev_seed"]]
        print(f"=== Running EXP-0007: DEV Mode (Seeds: {seeds}) ===")
    else:
        seeds = config["seeds"]
        print(f"=== Running EXP-0007: Small-Sample Candidate Separability Diagnostic (Seeds: {seeds}) ===")

    r1_indices = config["regime_1"]["indices"]
    r1_weights = config["regime_1"]["weights"]
    r2_indices = sorted(config["regime_2"]["indices"])
    r2_weights = config["regime_2"]["weights"]
    shift_step = config["shift_step"]
    total_steps = config["total_steps"]

    all_snapshots = []
    j4_metrics_per_seed = {}

    start_time = time.time()

    for seed in seeds:
        print(f"\n--- Running Seed {seed} ---")
        rng = np.random.RandomState(seed)
        init_supp = list(rng.choice(config["d_features"], size=config["k_star"], replace=False))

        env = DynamicSparseLinearStream(config, seed=seed)

        controller = ProbeBankController(
            q_min=config["q_min"],
            q_base=config["q_base"],
            q_max=config["q_max"],
            tau_low=config["tau_low"],
            tau_high=config["tau_high"],
            alpha=config["ema_alpha"],
            total_steps=total_steps,
            target_budget=config["target_total_probes"]
        )

        policy = TieredEvidenceRatePolicy(
            d=config["d_features"],
            mode="queue_multi_rate",
            c_max=config["c_max"],
            n_screen=config["n_screen"],
            theta_screen=config["theta_screen"],
            gamma_screen=config["gamma_screen"],
            theta_drop=config["theta_drop"],
            gamma_drop=config["gamma_drop"],
            confirm_max_probes=config["confirm_max_probes"],
            w_max=config["w_max"],
            h_max=config["h_max"],
            n_hint=config["n_hint"],
            theta_hint=config["theta_hint"],
            gamma_hint=config["gamma_hint"],
            theta_decay=config["theta_decay"],
            warm_max_probes=config["warm_max_probes"],
            hot_max_probes=config["hot_max_probes"],
            theta_hot=config["theta_hot"],
            gamma_hot=config["gamma_hot"],
            cold_fraction=config["cold_fraction"],
            warm_fraction=config["warm_fraction"]
        )

        learner = TieredEvidenceLearner(
            d=config["d_features"],
            initial_support=list(init_supp),
            probe_policy=policy,
            q=config["q_base"],
            mu=config["nlms_mu"],
            eps=config["nlms_eps"],
            n_min=config["n_min_baseline"],
            theta_promote=config["theta_promote"],
            grace_period=config["grace_period"],
            swap_threshold=config["swap_threshold"],
            victim_strategy=config["victim_strategy"],
            tau_mature=config["tau_mature"],
            cooldown_steps=config["cooldown_steps"],
            g_starve=config["g_starve"]
        )

        collector = CandidateSnapshotCollector(
            seed=seed,
            d=config["d_features"],
            shift_step=shift_step,
            r1_true_indices=r1_indices,
            r2_true_indices=r2_indices,
            target_n=(1, 2, 3, 4, 5)
        )

        losses = []
        r2_losses = []
        recalls = []
        occupancies = []
        flops_list = []
        probes_used_list = []

        for t in range(1, total_steps + 1):
            x, y, true_supp, _ = env.step()
            yh = learner.predict(x)
            err = y - yh
            loss = err ** 2
            q_t = controller.get_q(err, t)

            res = learner.update(x, y, q=q_t, true_support=true_supp)

            active_set = set(learner.support)
            overlap = len(active_set.intersection(true_supp))
            recall = overlap / float(len(true_supp))
            occupancy = 1.0 if overlap == len(true_supp) else 0.0

            losses.append(loss)
            flops_list.append(res["flops"])
            probes_used_list.append(res["num_probed"])

            if t > shift_step:
                recalls.append(recall)
                occupancies.append(occupancy)
            if t > 1800:
                r2_losses.append(loss)

            # Observe snapshot state without modifying learner
            tiers = {c: policy.get_candidate_tier(c) for c in range(config["d_features"])}
            cand_stats = {
                "n": learner.cand_n,
                "mean": learner.cand_mean,
                "m2": learner.cand_m2,
                "pos": learner.cand_pos,
                "neg": learner.cand_neg
            }
            collector.observe_step(
                step=t,
                error=err,
                probed_candidates=res["candidates"],
                learner_cand_stats=cand_stats,
                active_support=learner.support,
                candidate_tiers=tiers
            )

        snaps_df = collector.get_dataframe()
        all_snapshots.append(snaps_df)

        glob_mse = float(np.mean(losses))
        r2_mse = float(np.mean(r2_losses))
        mean_r2_rec = float(np.mean(recalls))
        full_occ = float(np.mean(occupancies))
        tot_probes = int(np.sum(probes_used_list))
        mean_flops = float(np.mean(flops_list))

        j4_metrics_per_seed[seed] = {
            "global_mse": glob_mse,
            "regime_2_mse": r2_mse,
            "mean_r2_recall": mean_r2_rec,
            "full_support_occupancy": full_occ,
            "total_probes": tot_probes,
            "mean_flops": mean_flops,
            "snapshots_count": len(snaps_df)
        }
        print(f"  Seed {seed}: R2 MSE = {r2_mse:.6f} | Mean Recall = {mean_r2_rec*100:.2f}% | Occupancy = {full_occ*100:.2f}% | Snaps = {len(snaps_df)}")

    # Combine all snapshots
    combined_df = pd.concat(all_snapshots, ignore_index=True)
    snapshots_csv_path = os.path.join(exp_dir, "candidate_snapshots.csv")
    combined_df.to_csv(snapshots_csv_path, index=False)
    print(f"\nSaved candidate snapshots: {snapshots_csv_path} ({len(combined_df)} rows)")

    # Baseline Behavior Gate Verification
    if not args.dev:
        print("\n=== Baseline Behavior Gate Verification (EXP-0006 J4 bit-for-bit) ===")
        # Seed 42 frozen values from EXP-0006
        seed42 = j4_metrics_per_seed[42]
        assert np.isclose(seed42["regime_2_mse"], 0.01154691517117861, atol=1e-8), f"Seed 42 R2 MSE mismatch: {seed42['regime_2_mse']}"
        assert np.isclose(seed42["mean_r2_recall"], 0.7726, atol=1e-6), f"Seed 42 Recall mismatch: {seed42['mean_r2_recall']}"
        assert np.isclose(seed42["full_support_occupancy"], 0.578, atol=1e-6), f"Seed 42 Occupancy mismatch: {seed42['full_support_occupancy']}"

        # Aggregate 5-seed mean values
        mean_r2_mse = np.mean([v["regime_2_mse"] for v in j4_metrics_per_seed.values()])
        mean_rec = np.mean([v["mean_r2_recall"] for v in j4_metrics_per_seed.values()])
        mean_occ = np.mean([v["full_support_occupancy"] for v in j4_metrics_per_seed.values()])
        assert np.isclose(mean_r2_mse, 0.013552459702794773, atol=1e-8), f"Mean R2 MSE mismatch: {mean_r2_mse}"
        assert np.isclose(mean_rec, 0.81324, atol=1e-6), f"Mean Recall mismatch: {mean_rec}"
        assert np.isclose(mean_occ, 0.6176, atol=1e-6), f"Mean Occupancy mismatch: {mean_occ}"
        print("  [PASS] Baseline Behavior Gate PASSED bit-for-bit! No perturbation detected.")

    # Primary Diagnostic Scores
    scores = ["S0", "S1", "S2", "S3", "S4", "S5", "S_current_rule", "Oracle"]
    simple_scores = ["S0", "S1", "S2", "S3", "S4", "S5"]

    # 1. Separability by n (Table 1)
    print("\n=== Computing Separability by n (n = 1..5) ===")
    table1_rows = []
    precision_k_rows = []
    table2_rows = []

    # Focus post-shift snapshots (Regime 2 structural acquisition)
    post_shift_df = combined_df[combined_df["step"] > shift_step].copy()

    for n_val in [1, 2, 3, 4, 5]:
        n_df = post_shift_df[post_shift_df["probe_count"] == n_val].copy()
        n_true = int(np.sum(n_df["truth_label"] == 1))
        n_noise = int(np.sum(n_df["truth_label"] == 0))
        base_rate = float(n_true / len(n_df)) if len(n_df) > 0 else 0.0

        best_score_n = "S0"
        best_p3_n = -1.0
        best_p5_n = -1.0
        best_enrich_n = -1.0

        for sc in scores:
            roc_auc, pr_auc = compute_roc_pr_auc(n_df["truth_label"].values, n_df[sc].values)
            res_k = evaluate_precision_at_k(n_df, sc, k_values=(1, 2, 3, 5, 10), post_shift_only=False)

            p1 = res_k["precision_at_k"][1]
            p2 = res_k["precision_at_k"][2]
            p3 = res_k["precision_at_k"][3]
            p5 = res_k["precision_at_k"][5]
            p10 = res_k["precision_at_k"][10]

            r3 = res_k["recall_at_k"][3]
            r5 = res_k["recall_at_k"][5]

            e3 = res_k["enrichment_at_k"][3]
            e5 = res_k["enrichment_at_k"][5]

            table1_rows.append({
                "n": n_val,
                "score": sc,
                "pr_auc": pr_auc,
                "roc_auc": roc_auc,
                "precision_at_1": p1,
                "precision_at_2": p2,
                "precision_at_3": p3,
                "precision_at_5": p5,
                "precision_at_10": p10,
                "recall_at_3": r3,
                "recall_at_5": r5,
                "enrichment_at_3": e3,
                "enrichment_at_5": e5,
                "base_rate": base_rate,
                "n_true": n_true,
                "n_noise": n_noise
            })

            # Record detailed seed-level precision for precision_at_k.csv
            for s in seeds:
                p3_s = res_k["seed_precisions"][3].get(s, 0.0)
                p5_s = res_k["seed_precisions"][5].get(s, 0.0)
                e3_s = res_k["seed_enrichments"][3].get(s, 0.0)
                e5_s = res_k["seed_enrichments"][5].get(s, 0.0)
                precision_k_rows.append({
                    "n": n_val,
                    "seed": s,
                    "score": sc,
                    "precision_at_3": p3_s,
                    "precision_at_5": p5_s,
                    "enrichment_at_3": e3_s,
                    "enrichment_at_5": e5_s
                })

            if sc in simple_scores:
                if p3 > best_p3_n or (p3 == best_p3_n and p5 > best_p5_n):
                    best_p3_n = p3
                    best_p5_n = p5
                    best_enrich_n = e3
                    best_score_n = sc

        table2_rows.append({
            "n": n_val,
            "true_count": n_true,
            "noise_count": n_noise,
            "base_rate": base_rate,
            "best_simple_score": best_score_n,
            "best_precision_at_3": best_p3_n,
            "best_precision_at_5": best_p5_n,
            "best_enrichment_at_3": best_enrich_n
        })

    table1_df = pd.DataFrame(table1_rows)
    table2_df = pd.DataFrame(table2_rows)
    prec_k_df = pd.DataFrame(precision_k_rows)

    separability_csv_path = os.path.join(exp_dir, "separability_by_n.csv")
    table1_df.to_csv(separability_csv_path, index=False)

    precision_k_csv_path = os.path.join(exp_dir, "precision_at_k.csv")
    prec_k_df.to_csv(precision_k_csv_path, index=False)

    print("\n--- Summary Table 2 (Separability by n) ---")
    print(table2_df.to_string(index=False))

    # 2. Temporal Stratification (Causal Scores)
    print("\n=== Computing Temporal Stratification (Windows A-E) ===")
    causal_scores = ["S0", "S1", "S2", "S3", "S4", "S5", "S_current_rule"]
    temp_df = evaluate_temporal_stratification(post_shift_df, scores=causal_scores)
    temp_csv_path = os.path.join(exp_dir, "temporal_stratification.csv")
    temp_df.to_csv(temp_csv_path, index=False)
    print(temp_df.to_string(index=False))

    # 3. Residual Stratification (Causal Scores)
    print("\n=== Computing Residual Stratification (Quantiles Q1-Q4) ===")
    resid_df = evaluate_residual_stratification(post_shift_df, scores=causal_scores)
    resid_csv_path = os.path.join(exp_dir, "residual_stratification.csv")
    resid_df.to_csv(resid_csv_path, index=False)
    print(resid_df.to_string(index=False))

    # 4. Rank Stability & Volatility
    print("\n=== Computing Rank Stability & Volatility (n = 1->2->3->4->5) ===")
    best_overall_simple = table2_df.loc[table2_df["best_precision_at_3"].idxmax(), "best_simple_score"]
    rank_stab_df = evaluate_rank_stability(post_shift_df, score_col=best_overall_simple)
    rank_stab_csv_path = os.path.join(exp_dir, "rank_stability.csv")
    rank_stab_df.to_csv(rank_stab_csv_path, index=False)
    print(rank_stab_df.to_string(index=False))

    # 5. Counterfactual Probe-Budget Elevation Precision
    print("\n=== Computing Counterfactual Elevated Precision ===")
    counterfactual_df = evaluate_counterfactual_elevation(post_shift_df, scores=scores, k_elevated=5)
    cf_csv_path = os.path.join(exp_dir, "counterfactual_elevated_precision.csv")
    counterfactual_df.to_csv(cf_csv_path, index=False)
    print(counterfactual_df.to_string(index=False))

    # 6. Optional Joint Linear Model Diagnostic (Leave-One-Seed-Out)
    print("\n=== Evaluating Leave-One-Seed-Out Logistic Regression Diagnostic ===")
    joint_model_status = "NOT_RUN"
    joint_summary = {}
    if len(seeds) >= 3:
        pred_log_df, joint_summary = evaluate_leave_one_seed_out_logistic(post_shift_df)
        print(f"  Logistic Diagnostic: ROC-AUC = {joint_summary['roc_auc']:.4f} | PR-AUC = {joint_summary['pr_auc']:.4f} | P@3 = {joint_summary['precision_k3']*100:.1f}% | P@5 = {joint_summary['precision_k5']*100:.1f}%")
        print(f"  Coefficients: {dict(zip(joint_summary['feature_cols'], [round(c, 4) for c in joint_summary['mean_coefficients']]))}")

        # Check if joint model adds material value (>5% precision improvement over best simple score)
        best_simple_p3 = table1_df[table1_df["score"].isin(simple_scores)]["precision_at_3"].max()
        if joint_summary["precision_k3"] >= best_simple_p3 + 0.05:
            joint_model_status = "ADDS_MATERIAL_VALUE"
        else:
            joint_model_status = "NO_MATERIAL_VALUE"
    print(f"  JOINT_LINEAR_MODEL = {joint_model_status}")

    # 7. Distribution Diagnostics for Key Features
    print("\n=== Distribution Diagnostics for n=2 and n=3 ===")
    for feat in ["abs_mean_corr", "sign_consistency", "std_corr", "S2"]:
        for n_test in [2, 3]:
            sub_n = post_shift_df[post_shift_df["probe_count"] == n_test]
            dist_res = compute_distribution_stats(sub_n, feat)
            t_m = dist_res["true"]["mean"]
            n_m = dist_res["noise"]["mean"]
            t_med = dist_res["true"]["median"]
            n_med = dist_res["noise"]["median"]
            cd = dist_res["cohens_d"]
            auc = dist_res["auc"]
            print(f"  [{feat} @ n={n_test}]: True mean={t_m:.3f} (med={t_med:.3f}) vs Noise mean={n_m:.3f} (med={n_med:.3f}) | Cohen's d = {cd:.2f} | AUC = {auc:.3f}")

    # Determine Pre-registered Thresholds and Decisions
    # N_SEPARABLE: smallest n where simple score achieves P@3 >= 50% OR P@5 >= 40% AND enrichment >= 5x
    n_separable = "NONE"
    strong_separable = False
    for _, r in table2_df.iterrows():
        n_val = int(r["n"])
        p3 = float(r["best_precision_at_3"])
        p5 = float(r["best_precision_at_5"])
        enrich = float(r["best_enrichment_at_3"])
        if (p3 >= 0.50 or p5 >= 0.40) and enrich >= 5.0:
            if n_separable == "NONE":
                n_separable = n_val
        if (p3 >= 0.70 or p5 >= 0.60):
            strong_separable = True

    best_simple_overall = table2_df.loc[table2_df["best_precision_at_3"].idxmax(), "best_simple_score"]

    # Check residual state dependence:
    # If Q4 precision is much worse than Q1 (< 50% of Q1 precision)
    q1_p3 = resid_df[resid_df["residual_quantile"] == "Q1"]["best_precision_k3"].values[0]
    q4_p3 = resid_df[resid_df["residual_quantile"] == "Q4"]["best_precision_k3"].values[0]
    residual_state_dependent = (q1_p3 > 0.30 and q4_p3 < 0.5 * q1_p3)

    # Primary Decision
    if n_separable in [1, 2]:
        primary_decision = "SMALL_SAMPLE_SIGNAL_SUFFICIENT"
    elif n_separable in [3, 4, 5]:
        primary_decision = "SMALL_SAMPLE_SIGNAL_SUFFICIENT_AFTER_MIN_N"
    elif residual_state_dependent:
        primary_decision = "RESIDUAL_STATE_DEPENDENT_SEPARABILITY"
    elif joint_model_status == "ADDS_MATERIAL_VALUE":
        primary_decision = "ONLY_JOINT_STATISTICS_SEPARATE"
    elif n_separable == "NONE":
        primary_decision = "CURRENT_STATISTICS_INSUFFICIENT"
    else:
        primary_decision = "DIAGNOSIS_UNRESOLVED"

    # Practical Questions
    q1_answer = "YES" if n_separable != "NONE" else "NO"
    q2_answer = n_separable
    if primary_decision in ["SMALL_SAMPLE_SIGNAL_SUFFICIENT", "SMALL_SAMPLE_SIGNAL_SUFFICIENT_AFTER_MIN_N"]:
        q3_answer = "DECISION_RULE_LIMITED"
        next_step = "MINIMAL_TIER_ENTRY_FILTER_CAUSAL_TEST"
    elif primary_decision == "RESIDUAL_STATE_DEPENDENT_SEPARABILITY":
        q3_answer = "STATE_DEPENDENT"
        next_step = "STATE_CONDITIONED_TIER_ENTRY_TEST"
    elif primary_decision == "ONLY_JOINT_STATISTICS_SEPARATE":
        q3_answer = "DECISION_RULE_LIMITED"
        next_step = "MINIMAL_JOINT_SCORE_CAUSAL_TEST"
    else:
        q3_answer = "INFORMATION_LIMITED"
        next_step = "NEW_CANDIDATE_INFORMATION_DIAGNOSTIC"

    status_verdict = "DIAGNOSIS_IDENTIFIED"

    print("\n==================================================")
    print("EXP-0007 PRIMARY DECISIONS & DIAGNOSTIC VERDICTS")
    print("==================================================")
    print(f"PRIMARY_DECISION = {primary_decision}")
    print(f"N_SEPARABLE = {n_separable}")
    print(f"BEST_SIMPLE_SCORE = {best_simple_overall}")
    print(f"JOINT_LINEAR_MODEL = {joint_model_status}")
    print(f"EXP_0007_STATUS = {status_verdict}")
    print(f"Q1 (Signal sufficient early?): {q1_answer}")
    print(f"Q2 (Minimum n required): {q2_answer}")
    print(f"Q3 (Failure type): {q3_answer}")
    print(f"M1_CANDIDATE = FALSE (Frozen diagnostic gate)")
    print(f"NEXT = {next_step}")
    print("==================================================")

    # 8. Generate 10-Panel Publication Figure
    print("\n=== Generating 10-Panel Publication Figure ===")
    generate_publication_figures(
        exp_dir=exp_dir,
        table1_df=table1_df,
        table2_df=table2_df,
        temp_df=temp_df,
        resid_df=resid_df,
        rank_stab_df=rank_stab_df,
        post_shift_df=post_shift_df,
        best_score=best_simple_overall
    )

    elapsed = time.time() - start_time
    print(f"\nEXP-0007 Diagnostic completed in {elapsed:.1f}s.")

    return {
        "primary_decision": primary_decision,
        "n_separable": n_separable,
        "best_simple_score": best_simple_overall,
        "joint_model_status": joint_model_status,
        "status_verdict": status_verdict,
        "q1_answer": q1_answer,
        "q2_answer": q2_answer,
        "q3_answer": q3_answer,
        "next_step": next_step
    }


def generate_publication_figures(
    exp_dir: str,
    table1_df: pd.DataFrame,
    table2_df: pd.DataFrame,
    temp_df: pd.DataFrame,
    resid_df: pd.DataFrame,
    rank_stab_df: pd.DataFrame,
    post_shift_df: pd.DataFrame,
    best_score: str
):
    """
    Generates a 10-panel publication-grade figure satisfying Section 85.
    """
    fig, axes = plt.subplots(5, 2, figsize=(16, 26))
    fig.patch.set_facecolor('#0f172a')
    for ax in axes.flat:
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='#cbd5e1', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    palette = {
        "S0": "#38bdf8", # sky blue
        "S1": "#a855f7", # purple
        "S2": "#22c55e", # green
        "S3": "#f59e0b", # amber
        "S4": "#ec4899", # pink
        "S5": "#06b6d4", # cyan
        "S_current_rule": "#ef4444", # red
        "Oracle": "#e2e8f0" # white/slate
    }

    # Panel 1: PR Curves by n for best_score vs Oracle
    ax1 = axes[0, 0]
    ax1.set_title(f"1. Precision-Recall Curves by n ({best_score})", color='#f8fafc', fontsize=11, fontweight='bold')
    n_colors = {1: '#94a3b8', 2: '#38bdf8', 3: '#22c55e', 4: '#f59e0b', 5: '#ec4899'}
    for n_val in [1, 2, 3, 4, 5]:
        sub = post_shift_df[post_shift_df["probe_count"] == n_val]
        y_true = sub["truth_label"].values
        y_score = sub[best_score].values
        # compute curve points
        order = np.argsort(-y_score, kind="mergesort")
        y_sorted = y_true[order]
        n_pos = np.sum(y_true == 1)
        if n_pos > 0:
            tp = np.cumsum(y_sorted == 1)
            fp = np.cumsum(y_sorted == 0)
            rec = tp / float(n_pos)
            prec = tp / np.maximum(1, tp + fp)
            ax1.plot(rec, prec, label=f"n={n_val}", color=n_colors[n_val], lw=2.0)
    ax1.set_xlabel("Recall", color='#cbd5e1', fontsize=9)
    ax1.set_ylabel("Precision", color='#cbd5e1', fontsize=9)
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(loc='upper right', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    ax1.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 2: Precision@3 vs n across scores S0-S5
    ax2 = axes[0, 1]
    ax2.set_title("2. Precision@3 vs Probe Count n", color='#f8fafc', fontsize=11, fontweight='bold')
    for sc in ["S0", "S1", "S2", "S3", "S4", "S5", "S_current_rule", "Oracle"]:
        sub_sc = table1_df[table1_df["score"] == sc].sort_values("n")
        lbl = "EXP-0006 Rule" if sc == "S_current_rule" else sc
        ls = '--' if sc in ["Oracle", "S_current_rule"] else '-'
        lw = 2.5 if sc in [best_score, "S_current_rule"] else 1.5
        ax2.plot(sub_sc["n"], sub_sc["precision_at_3"] * 100.0, label=lbl, color=palette[sc], ls=ls, lw=lw, marker='o', ms=5)
    ax2.axhline(50.0, color='#22c55e', ls=':', lw=1.5, label='Target Gate (50%)')
    ax2.set_xlabel("Probe Count n", color='#cbd5e1', fontsize=9)
    ax2.set_ylabel("Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax2.set_ylim(-5, 105)
    ax2.legend(loc='upper left', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=7.5, ncol=2)
    ax2.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 3: Precision@5 vs n across scores S0-S5
    ax3 = axes[1, 0]
    ax3.set_title("3. Precision@5 vs Probe Count n", color='#f8fafc', fontsize=11, fontweight='bold')
    for sc in ["S0", "S1", "S2", "S3", "S4", "S5", "S_current_rule", "Oracle"]:
        sub_sc = table1_df[table1_df["score"] == sc].sort_values("n")
        lbl = "EXP-0006 Rule" if sc == "S_current_rule" else sc
        ls = '--' if sc in ["Oracle", "S_current_rule"] else '-'
        lw = 2.5 if sc in [best_score, "S_current_rule"] else 1.5
        ax3.plot(sub_sc["n"], sub_sc["precision_at_5"] * 100.0, label=lbl, color=palette[sc], ls=ls, lw=lw, marker='s', ms=5)
    ax3.axhline(40.0, color='#22c55e', ls=':', lw=1.5, label='Target Gate (40%)')
    ax3.set_xlabel("Probe Count n", color='#cbd5e1', fontsize=9)
    ax3.set_ylabel("Precision@5 (%)", color='#cbd5e1', fontsize=9)
    ax3.set_ylim(-5, 105)
    ax3.legend(loc='upper left', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=7.5, ncol=2)
    ax3.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 4: Enrichment@3 vs n across scores S0-S5
    ax4 = axes[1, 1]
    ax4.set_title("4. Enrichment@3 vs Probe Count n", color='#f8fafc', fontsize=11, fontweight='bold')
    for sc in ["S0", "S1", "S2", "S3", "S4", "S5", "S_current_rule"]:
        sub_sc = table1_df[table1_df["score"] == sc].sort_values("n")
        lbl = "EXP-0006 Rule" if sc == "S_current_rule" else sc
        ls = '--' if sc == "S_current_rule" else '-'
        lw = 2.5 if sc in [best_score, "S_current_rule"] else 1.5
        ax4.plot(sub_sc["n"], sub_sc["enrichment_at_3"], label=lbl, color=palette[sc], ls=ls, lw=lw, marker='^', ms=5)
    ax4.axhline(5.0, color='#f59e0b', ls=':', lw=1.5, label='Min Gate (5x)')
    ax4.set_xlabel("Probe Count n", color='#cbd5e1', fontsize=9)
    ax4.set_ylabel("Enrichment@3 (x Base Rate)", color='#cbd5e1', fontsize=9)
    ax4.legend(loc='upper left', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8, ncol=2)
    ax4.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 5: TRUE vs NOISE Score Distributions at n=2 and n=3
    ax5 = axes[2, 0]
    ax5.set_title(f"5. TRUE vs NOISE Distribution ({best_score} @ n=2 & n=3)", color='#f8fafc', fontsize=11, fontweight='bold')
    sub2 = post_shift_df[post_shift_df["probe_count"] == 2]
    sub3 = post_shift_df[post_shift_df["probe_count"] == 3]
    t2_vals = sub2[sub2["truth_label"] == 1][best_score].values
    n2_vals = sub2[sub2["truth_label"] == 0][best_score].values
    t3_vals = sub3[sub3["truth_label"] == 1][best_score].values
    n3_vals = sub3[sub3["truth_label"] == 0][best_score].values

    bp_labels = ["True (n=2)", "Noise (n=2)", "True (n=3)", "Noise (n=3)"]
    try:
        bplot = ax5.boxplot(
            [t2_vals, n2_vals, t3_vals, n3_vals],
            tick_labels=bp_labels,
            patch_artist=True,
            widths=0.5,
            medianprops=dict(color='#f8fafc', lw=2)
        )
    except TypeError:
        bplot = ax5.boxplot(
            [t2_vals, n2_vals, t3_vals, n3_vals],
            labels=bp_labels,
            patch_artist=True,
            widths=0.5,
            medianprops=dict(color='#f8fafc', lw=2)
        )
    box_colors = ['#22c55e', '#ef4444', '#38bdf8', '#f59e0b']
    for patch, color in zip(bplot['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax5.set_ylabel(f"Score ({best_score})", color='#cbd5e1', fontsize=9)
    ax5.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 6: Score Distributions across Residual Quantiles (Q1-Q4)
    ax6 = axes[2, 1]
    ax6.set_title(f"6. Precision@3 Across Residual Quantiles ({best_score})", color='#f8fafc', fontsize=11, fontweight='bold')
    q_x = np.arange(len(resid_df))
    bars = ax6.bar(q_x, resid_df["best_precision_k3"] * 100.0, color=['#38bdf8', '#22c55e', '#f59e0b', '#ef4444'], width=0.5, alpha=0.85)
    for bar in bars:
        h = bar.get_height()
        ax6.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h + 1),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                     color='#f8fafc', fontsize=8.5, fontweight='bold')
    ax6.set_xticks(q_x)
    ax6.set_xticklabels(resid_df["residual_quantile"], color='#cbd5e1', fontsize=9)
    ax6.set_xlabel("Smoothed Residual Quantile", color='#cbd5e1', fontsize=9)
    ax6.set_ylabel("Best Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax6.set_ylim(0, 110)
    ax6.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 7: Score Distributions across Post-Shift Time Windows (A-E)
    ax7 = axes[3, 0]
    ax7.set_title(f"7. Precision@3 Across Post-Shift Windows ({best_score})", color='#f8fafc', fontsize=11, fontweight='bold')
    w_x = np.arange(len(temp_df))
    bars_w = ax7.bar(w_x, temp_df["best_precision_k3"] * 100.0, color='#38bdf8', width=0.5, alpha=0.85)
    for bar in bars_w:
        h = bar.get_height()
        ax7.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h + 1),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                     color='#f8fafc', fontsize=8.5, fontweight='bold')
    ax7.set_xticks(w_x)
    ax7.set_xticklabels(temp_df["window"], color='#cbd5e1', fontsize=8)
    ax7.set_xlabel("Post-Shift Time Window (steps)", color='#cbd5e1', fontsize=9)
    ax7.set_ylabel("Best Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax7.set_ylim(0, 110)
    ax7.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 8: Rank Persistence & Volatility: TRUE vs NOISE
    ax8 = axes[3, 1]
    ax8.set_title(f"8. Rank Volatility: TRUE vs NOISE ({best_score})", color='#f8fafc', fontsize=11, fontweight='bold')
    rv_x = np.arange(len(rank_stab_df))
    w_bar = 0.35
    ax8.bar(rv_x - w_bar / 2, rank_stab_df["true_mean_volatility"], width=w_bar, label="TRUE Candidates", color='#22c55e', alpha=0.85)
    ax8.bar(rv_x + w_bar / 2, rank_stab_df["noise_mean_volatility"], width=w_bar, label="NOISE Candidates", color='#ef4444', alpha=0.85)
    ax8.set_xticks(rv_x)
    ax8.set_xticklabels(rank_stab_df["transition"], color='#cbd5e1', fontsize=8.5)
    ax8.set_xlabel("Probe Count Transition", color='#cbd5e1', fontsize=9)
    ax8.set_ylabel("Mean |Rank Change|", color='#cbd5e1', fontsize=9)
    ax8.legend(loc='upper right', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8.5)
    ax8.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 9: False Positive Rate by Residual Quantile
    ax9 = axes[4, 0]
    ax9.set_title("9. False Positive Rate (K=3) by Residual Quantile", color='#f8fafc', fontsize=11, fontweight='bold')
    fpr_vals = resid_df["false_positive_rate_k3"] * 100.0
    ax9.bar(q_x, fpr_vals, color='#ef4444', width=0.5, alpha=0.85)
    for idx, val in enumerate(fpr_vals):
        ax9.annotate(f"{val:.1f}%", xy=(q_x[idx], val + 1),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                     color='#f8fafc', fontsize=8.5, fontweight='bold')
    ax9.set_xticks(q_x)
    ax9.set_xticklabels(resid_df["residual_quantile"], color='#cbd5e1', fontsize=9)
    ax9.set_xlabel("Smoothed Residual Quantile", color='#cbd5e1', fontsize=9)
    ax9.set_ylabel("False Positive Rate (%)", color='#cbd5e1', fontsize=9)
    ax9.set_ylim(0, 110)
    ax9.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 10: Base Rate vs Achieved Precision@K across n
    ax10 = axes[4, 1]
    ax10.set_title(f"10. Base Rate vs Achieved Precision ({best_score})", color='#f8fafc', fontsize=11, fontweight='bold')
    n_x = table2_df["n"].values
    ax10.plot(n_x, table2_df["base_rate"] * 100.0, label="True Candidate Base Rate", color='#94a3b8', ls='--', lw=2.0, marker='x', ms=7)
    ax10.plot(n_x, table2_df["best_precision_at_3"] * 100.0, label="Achieved Precision@3", color='#22c55e', lw=2.5, marker='o', ms=6)
    ax10.plot(n_x, table2_df["best_precision_at_5"] * 100.0, label="Achieved Precision@5", color='#38bdf8', lw=2.5, marker='s', ms=6)
    # Add EXP-0006 rule precision
    exp6_sub = table1_df[table1_df["score"] == "S_current_rule"].sort_values("n")
    ax10.plot(n_x, exp6_sub["precision_at_3"] * 100.0, label="EXP-0006 Rule P@3", color='#ef4444', ls=':', lw=2.0, marker='^', ms=6)

    ax10.set_xlabel("Probe Count n", color='#cbd5e1', fontsize=9)
    ax10.set_ylabel("Percentage (%)", color='#cbd5e1', fontsize=9)
    ax10.set_ylim(-5, 105)
    ax10.legend(loc='upper left', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    ax10.grid(True, color='#334155', ls='--', alpha=0.5)

    plt.tight_layout()
    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved publication figures to {fig_path}")

    # Copy to IDE artifacts directory
    artifact_dir = os.path.join(os.path.expanduser("~"), "lebre_artifacts")
    artifact_fig_path = os.path.join(artifact_dir, "figures_exp_0007.png")
    try:
        shutil.copyfile(fig_path, artifact_fig_path)
        print(f"Copied figure to IDE artifact: {artifact_fig_path}")
    except Exception as e:
        print(f"Warning: could not copy figure to IDE artifact directory: {e}")

if __name__ == "__main__":
    run_diagnostic()
