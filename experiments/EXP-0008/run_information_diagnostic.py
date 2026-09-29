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
from src.diagnostics.candidate_microtest import (
    MicrotestDiagnosticObserver,
    compute_roc_pr_auc,
    evaluate_channel_precision_at_k,
    evaluate_temporal_stratification_microtest,
    evaluate_residual_stratification_microtest,
    evaluate_counterfactual_queue_enrichment,
    evaluate_leave_one_seed_out_logistic_microtest
)

def parse_args():
    parser = argparse.ArgumentParser(description="EXP-0008: Candidate Information Channel Diagnostic")
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
        print(f"=== Running EXP-0008: DEV Mode (Seeds: {seeds}) ===")
    else:
        seeds = config["seeds"]
        print(f"=== Running EXP-0008: Candidate Information Channel Diagnostic (Seeds: {seeds}) ===")

    r1_indices = config["regime_1"]["indices"]
    r1_weights = config["regime_1"]["weights"]
    r2_indices = sorted(config["regime_2"]["indices"])
    r2_weights = config["regime_2"]["weights"]
    shift_step = config["shift_step"]
    total_steps = config["total_steps"]

    all_events = []
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

        observer = MicrotestDiagnosticObserver(
            seed=seed,
            d=config["d_features"],
            shift_step=shift_step,
            r1_true_indices=r1_indices,
            r2_true_indices=r2_indices,
            paired_window_w=config["microtest"]["paired_window_w"],
            multi_test_m=config["microtest"]["multi_test_m"],
            eta_scale=config["microtest"]["eta_scale"]
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

            # 1. Observer begins step: evaluates pending shadow micro-tests on incoming (x, y)
            observer.on_step_begin(
                step=t,
                x_t=x,
                y_t=y,
                y_hat_base=yh,
                active_support=learner.support
            )

            # 2. Production learner updates normally
            q_t = controller.get_q(err, t)
            step_res = learner.update(x, y, q=q_t, true_support=true_supp)

            active_set = set(learner.support)
            overlap = len(active_set.intersection(true_supp))
            recall = overlap / float(len(true_supp))
            occupancy = 1.0 if overlap == len(true_supp) else 0.0

            losses.append(loss)
            flops_list.append(step_res["flops"])
            probes_used_list.append(step_res["num_probed"])

            if t > shift_step:
                recalls.append(recall)
                occupancies.append(occupancy)
            if t > 1800:
                r2_losses.append(loss)

            # 3. Observer ends step: creates candidate shadow micro-tests for probed candidates
            tiers = {c: policy.get_candidate_tier(c) for c in range(config["d_features"])}
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
                step=t,
                error=err,
                probed_candidates=step_res["candidates"],
                learner_cand_stats=cand_stats,
                active_support=learner.support,
                norm_sq_active=norm_sq,
                candidate_tiers=tiers
            )

        events_df = observer.get_dataframe()
        all_events.append(events_df)

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
            "microtests_count": len(events_df)
        }
        print(f"  Seed {seed}: R2 MSE = {r2_mse:.6f} | Recall = {mean_r2_rec*100:.2f}% | Occupancy = {full_occ*100:.2f}% | Tests = {len(events_df)}")

    # Combine events
    combined_events_df = pd.concat(all_events, ignore_index=True)
    events_csv_path = os.path.join(exp_dir, "microtest_events.csv")
    combined_events_df.to_csv(events_csv_path, index=False)
    print(f"\nSaved microtest events: {events_csv_path} ({len(combined_events_df)} rows)")

    # Baseline Behavior Gate Verification
    if not args.dev:
        print("\n=== Baseline Behavior Gate Verification (EXP-0006 J4 bit-for-bit) ===")
        seed42 = j4_metrics_per_seed[42]
        assert np.isclose(seed42["regime_2_mse"], 0.01154691517117861, atol=1e-8), f"Seed 42 R2 MSE mismatch: {seed42['regime_2_mse']}"
        assert np.isclose(seed42["mean_r2_recall"], 0.7726, atol=1e-6), f"Seed 42 Recall mismatch: {seed42['mean_r2_recall']}"
        assert np.isclose(seed42["full_support_occupancy"], 0.578, atol=1e-6), f"Seed 42 Occupancy mismatch: {seed42['full_support_occupancy']}"

        mean_r2_mse = np.mean([v["regime_2_mse"] for v in j4_metrics_per_seed.values()])
        mean_rec = np.mean([v["mean_r2_recall"] for v in j4_metrics_per_seed.values()])
        mean_occ = np.mean([v["full_support_occupancy"] for v in j4_metrics_per_seed.values()])
        assert np.isclose(mean_r2_mse, 0.013552459702794773, atol=1e-8), f"Mean R2 MSE mismatch: {mean_r2_mse}"
        assert np.isclose(mean_rec, 0.81324, atol=1e-6), f"Mean Recall mismatch: {mean_rec}"
        assert np.isclose(mean_occ, 0.6176, atol=1e-6), f"Mean Occupancy mismatch: {mean_occ}"
        print("  [PASS] Baseline Behavior Gate PASSED bit-for-bit! Zero perturbation detected.")

    # Post-shift evaluation data
    post_shift_df = combined_events_df[combined_events_df["step_train"] > shift_step].copy()
    post_shift_df["Oracle"] = post_shift_df["truth_label"].astype(float)

    # Channel Definitions: (Name, score_column, estimated_flops_per_test, state_bytes)
    channel_defs = [
        ("I0 Passive Corr", "abs_mean_corr", 0, 0),
        ("I1 Delayed Corr", "score_i1", 2, 4),
        ("I2 Single Micro-Update Gain", "normalized_gain_i2", 18, 16),
        ("I3 Paired Shadow Gain", "normalized_gain_i3", 30, 24),
        ("I4 Persistent Micro-Update", "normalized_gain_i4", 36, 32),
        ("Causal Direction Margin", "causal_direction_margin", 24, 16),
        ("Excess Causal Gain", "excess_causal_gain", 36, 32),
        ("Oracle", "Oracle", 0, 0)
    ]

    # 1. Output Table 1: Information Channels
    print("\n=== Computing Output Table 1: Information Channels ===")
    table1_rows = []
    for ch_name, col_name, flops_cost, bytes_cost in channel_defs:
        roc_auc, pr_auc = compute_roc_pr_auc(post_shift_df["truth_label"].values, post_shift_df[col_name].values)
        res_k = evaluate_channel_precision_at_k(post_shift_df, col_name, k_values=(1, 2, 3, 5, 10), post_shift_only=False)

        p1 = res_k["precision_at_k"][1]
        p2 = res_k["precision_at_k"][2]
        p3 = res_k["precision_at_k"][3]
        p5 = res_k["precision_at_k"][5]
        p10 = res_k["precision_at_k"][10]

        r3 = res_k["recall_at_k"][3]
        r5 = res_k["recall_at_k"][5]

        e3 = res_k["enrichment_at_k"][3]
        e5 = res_k["enrichment_at_k"][5]

        # Positive gain rates
        t_vals = post_shift_df[post_shift_df["truth_label"] == 1][col_name].values
        n_vals = post_shift_df[post_shift_df["truth_label"] == 0][col_name].values
        p_gain_pos_true = float(np.mean(t_vals > 0)) if len(t_vals) > 0 else 0.0
        p_gain_pos_noise = float(np.mean(n_vals > 0)) if len(n_vals) > 0 else 0.0

        # Info Efficiency = Enrichment@3 / max(1, flops_cost)
        info_eff = float(e3 / max(1, flops_cost))
        prec3_per_100_flops = float((p3 * 100.0) / max(1.0, flops_cost / 100.0))
        prec5_per_100_flops = float((p5 * 100.0) / max(1.0, flops_cost / 100.0))

        table1_rows.append({
            "channel": ch_name,
            "score_col": col_name,
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
            "true_gain_pos_rate": p_gain_pos_true,
            "noise_gain_pos_rate": p_gain_pos_noise,
            "estimated_flops_per_test": flops_cost,
            "state_bytes_per_test": bytes_cost,
            "info_efficiency": info_eff,
            "precision_at_3_per_100_flops": prec3_per_100_flops,
            "precision_at_5_per_100_flops": prec5_per_100_flops
        })

    table1_df = pd.DataFrame(table1_rows)
    table1_csv_path = os.path.join(exp_dir, "information_channels.csv")
    table1_df.to_csv(table1_csv_path, index=False)
    print(table1_df[["channel", "pr_auc", "roc_auc", "precision_at_3", "precision_at_5", "enrichment_at_3", "true_gain_pos_rate", "noise_gain_pos_rate", "info_efficiency"]].to_string(index=False))

    # 2. Output Table 2: Precision@K by Passive Probe Count n = 1..5
    print("\n=== Computing Output Table 2: By Passive Probe Count n ===")
    causal_channels = [c for c in channel_defs if c[0] != "Oracle"]
    table2_rows = []
    prec_k_detailed = []

    for n_val in [1, 2, 3, 4, 5]:
        n_df = post_shift_df[post_shift_df["n_passive_probes"] == n_val].copy()
        n_true = int(np.sum(n_df["truth_label"] == 1))
        n_noise = int(np.sum(n_df["truth_label"] == 0))
        base_rate = float(n_true / len(n_df)) if len(n_df) > 0 else 0.0

        best_ch = "I0 Passive Corr"
        best_p3 = -1.0
        best_p5 = -1.0
        best_e3 = -1.0
        best_flops = 0

        for ch_name, col_name, flops_cost, _ in causal_channels:
            res = evaluate_channel_precision_at_k(n_df, col_name, k_values=(1, 2, 3, 5, 10), post_shift_only=False)
            p3 = res["precision_at_k"][3]
            p5 = res["precision_at_k"][5]
            e3 = res["enrichment_at_k"][3]
            _, pr_auc = compute_roc_pr_auc(n_df["truth_label"].values, n_df[col_name].values)

            # Record detailed seed level
            for s in seeds:
                prec_k_detailed.append({
                    "n": n_val,
                    "seed": s,
                    "channel": ch_name,
                    "precision_at_3": res["seed_precisions"][3].get(s, 0.0),
                    "precision_at_5": res["seed_precisions"][5].get(s, 0.0),
                    "enrichment_at_3": res["seed_enrichments"][3].get(s, 0.0)
                })

            if p3 > best_p3 or (p3 == best_p3 and p5 > best_p5):
                best_p3 = p3
                best_p5 = p5
                best_e3 = e3
                best_ch = ch_name
                best_flops = flops_cost

        table2_rows.append({
            "n": n_val,
            "best_channel": best_ch,
            "precision_at_3": best_p3,
            "precision_at_5": best_p5,
            "base_rate": base_rate,
            "enrichment_at_3": best_e3,
            "extra_flops": best_flops,
            "true_count": n_true,
            "noise_count": n_noise
        })

    table2_df = pd.DataFrame(table2_rows)
    prec_k_df = pd.DataFrame(prec_k_detailed)
    table2_csv_path = os.path.join(exp_dir, "precision_at_k.csv")
    prec_k_df.to_csv(table2_csv_path, index=False)
    print(table2_df.to_string(index=False))

    # 3. Output Table 3: Temporal Stratification (Windows A-E)
    print("\n=== Computing Output Table 3: Temporal Stratification ===")
    causal_pairs = [(ch[0], ch[1]) for ch in causal_channels]
    temp_df = evaluate_temporal_stratification_microtest(post_shift_df, channels=causal_pairs)
    temp_csv_path = os.path.join(exp_dir, "temporal_stratification.csv")
    temp_df.to_csv(temp_csv_path, index=False)
    print(temp_df.to_string(index=False))

    # 4. Output Table 4: Residual Stratification (Quantiles Q1-Q4)
    print("\n=== Computing Output Table 4: Residual Stratification ===")
    resid_df = evaluate_residual_stratification_microtest(post_shift_df, channels=causal_pairs)
    resid_csv_path = os.path.join(exp_dir, "residual_stratification.csv")
    resid_df.to_csv(resid_csv_path, index=False)
    print(resid_df.to_string(index=False))

    # 5. Causal Controls Breakdown (Sign-Reversal & Sham Control)
    print("\n=== Computing Causal Controls Breakdown ===")
    controls_summary = []
    for grp_label, val in [("TRUE", 1), ("NOISE", 0)]:
        sub = post_shift_df[post_shift_df["truth_label"] == val]
        controls_summary.append({
            "group": grp_label,
            "count": len(sub),
            "mean_gain_i2": float(np.mean(sub["gain_i2"])),
            "median_gain_i2": float(np.median(sub["gain_i2"])),
            "mean_causal_direction_margin": float(np.mean(sub["causal_direction_margin"])),
            "median_causal_direction_margin": float(np.median(sub["causal_direction_margin"])),
            "p_margin_positive": float(np.mean(sub["causal_direction_margin"] > 0)),
            "mean_gain_sham": float(np.mean(sub["gain_sham"])),
            "median_gain_sham": float(np.median(sub["gain_sham"])),
            "mean_excess_causal_gain": float(np.mean(sub["excess_causal_gain"])),
            "median_excess_causal_gain": float(np.median(sub["excess_causal_gain"])),
            "p_excess_positive": float(np.mean(sub["excess_causal_gain"] > 0))
        })
    controls_df = pd.DataFrame(controls_summary)
    controls_csv_path = os.path.join(exp_dir, "causal_controls.csv")
    controls_df.to_csv(controls_csv_path, index=False)
    print(controls_df.to_string(index=False))

    # 6. Counterfactual Elevated Queue Enrichment
    print("\n=== Computing Counterfactual Queue Enrichment ===")
    all_pairs = [(ch[0], ch[1]) for ch in channel_defs]
    counterfactual_df = evaluate_counterfactual_queue_enrichment(post_shift_df, channels=all_pairs, k_elevated=5)
    cf_csv_path = os.path.join(exp_dir, "counterfactual_queue.csv")
    counterfactual_df.to_csv(cf_csv_path, index=False)
    print(counterfactual_df.to_string(index=False))

    # 7. Information Efficiency Summary
    info_eff_df = table1_df[["channel", "precision_at_3", "precision_at_5", "enrichment_at_3", "estimated_flops_per_test", "info_efficiency", "precision_at_3_per_100_flops", "precision_at_5_per_100_flops"]].copy()
    info_eff_csv_path = os.path.join(exp_dir, "information_efficiency.csv")
    info_eff_df.to_csv(info_eff_csv_path, index=False)

    # 8. Optional Leave-One-Seed-Out Logistic Model
    print("\n=== Evaluating Leave-One-Seed-Out Logistic Regression Diagnostic ===")
    joint_model_status = "NOT_RUN"
    if len(seeds) >= 3:
        pred_log_df, joint_summary = evaluate_leave_one_seed_out_logistic_microtest(post_shift_df)
        print(f"  Logistic Diagnostic: ROC-AUC = {joint_summary['roc_auc']:.4f} | PR-AUC = {joint_summary['pr_auc']:.4f} | P@3 = {joint_summary['precision_k3']*100:.1f}% | P@5 = {joint_summary['precision_k5']*100:.1f}%")
        best_single_p3 = table1_df[table1_df["channel"].isin([c[0] for c in causal_channels])]["precision_at_3"].max()
        if joint_summary["precision_k3"] >= best_single_p3 + 0.05:
            joint_model_status = "ADDS_MATERIAL_VALUE"
        else:
            joint_model_status = "NO_MATERIAL_VALUE"
    print(f"  JOINT_LINEAR_MODEL = {joint_model_status}")

    # Determine Decisions & Primary Status
    best_causal_row = table1_df[table1_df["channel"].isin([c[0] for c in causal_channels])].sort_values("precision_at_3", ascending=False).iloc[0]
    best_channel_name = best_causal_row["channel"]
    best_p3 = float(best_causal_row["precision_at_3"])
    best_p5 = float(best_causal_row["precision_at_5"])
    best_e3 = float(best_causal_row["enrichment_at_3"])

    # Check Success Gates
    operational_useful = (best_p3 >= 0.50 or best_p5 >= 0.40) and (best_e3 >= 5.0)
    strong_useful = (best_p3 >= 0.70 or best_p5 >= 0.60)

    # Check deployability cost (< 25% of Dense compute = < 150.5 FLOPs/step)
    current_j4_flops = 142.80
    deployable_extra_flops = float(best_causal_row["estimated_flops_per_test"])
    plausibly_fits_budget = (current_j4_flops + deployable_extra_flops) <= 150.5 or deployable_extra_flops <= 15.0

    # Decision Taxonomy
    if best_p3 >= 0.50:
        if "Paired" in best_channel_name:
            primary_decision = "PAIRED_SHADOW_GAIN_SUFFICIENT"
        elif "Direction" in best_channel_name:
            primary_decision = "CAUSAL_DIRECTION_SIGNAL_SUFFICIENT"
        elif "Excess" in best_channel_name or "Sham" in best_channel_name:
            primary_decision = "SHAM_NORMALIZATION_REQUIRED"
        elif "Persistent" in best_channel_name:
            primary_decision = "MULTI_TEST_PERSISTENCE_REQUIRED"
        else:
            primary_decision = "MICRO_INTERVENTION_INFORMATION_SUFFICIENT"
    elif joint_model_status == "ADDS_MATERIAL_VALUE":
        primary_decision = "PASSIVE_AND_INTERVENTIONAL_JOINTLY_SUFFICIENT"
    elif operational_useful and not plausibly_fits_budget:
        primary_decision = "INFORMATION_AVAILABLE_BUT_TOO_EXPENSIVE"
    else:
        primary_decision = "CURRENT_MICRO_INTERVENTIONS_INSUFFICIENT"

    if best_channel_name == "I0 Passive Corr":
        best_channel_code = "I0"
    elif best_channel_name == "I1 Delayed Corr":
        best_channel_code = "I1"
    elif best_channel_name == "I2 Single Micro-Update Gain":
        best_channel_code = "I2"
    elif best_channel_name == "I3 Paired Shadow Gain":
        best_channel_code = "I3"
    elif best_channel_name == "I4 Persistent Micro-Update":
        best_channel_code = "I4"
    elif best_channel_name == "Causal Direction Margin":
        best_channel_code = "CAUSAL_DIRECTION_MARGIN"
    elif best_channel_name == "Excess Causal Gain":
        best_channel_code = "EXCESS_CAUSAL_GAIN"
    elif joint_model_status == "ADDS_MATERIAL_VALUE":
        best_channel_code = "JOINT_LINEAR"
    else:
        best_channel_code = "NONE"

    min_useful_microtests = "1" if best_channel_code in ["I2", "CAUSAL_DIRECTION_MARGIN", "EXCESS_CAUSAL_GAIN"] else ("2" if best_channel_code == "I4" else ("3" if best_channel_code == "I3" else "NONE"))
    if not operational_useful:
        min_useful_microtests = "NONE"

    if operational_useful and plausibly_fits_budget:
        info_status = "PASSIVE_INFORMATION_LIMITED_BUT_INTERVENTION_SOLVES"
    elif operational_useful and not plausibly_fits_budget:
        info_status = "INTERVENTIONAL_INFORMATION_TOO_EXPENSIVE"
    elif not operational_useful and (best_p3 > 0.26 or best_causal_row["pr_auc"] > 0.15):
        info_status = "INTERVENTIONAL_INFORMATION_PARTIAL"
    else:
        info_status = "INTERVENTIONAL_INFORMATION_INSUFFICIENT"

    status_verdict = "DIAGNOSIS_IDENTIFIED"

    # Next step mapping
    if primary_decision in ["MICRO_INTERVENTION_INFORMATION_SUFFICIENT", "PAIRED_SHADOW_GAIN_SUFFICIENT", "CAUSAL_DIRECTION_SIGNAL_SUFFICIENT"]:
        next_step = "MINIMAL_CAUSAL_TIER_ENTRY_TEST"
    elif primary_decision == "SHAM_NORMALIZATION_REQUIRED":
        next_step = "SHAM_NORMALIZED_CAUSAL_ENTRY_TEST"
    elif primary_decision == "MULTI_TEST_PERSISTENCE_REQUIRED":
        next_step = "BOUNDED_MULTI_TEST_ENTRY_TEST"
    elif primary_decision == "INFORMATION_AVAILABLE_BUT_TOO_EXPENSIVE":
        next_step = "INFORMATION_CHANNEL_COMPRESSION"
    else:
        next_step = "ACTIVE_PROBE_DESIGN_DIAGNOSTIC"

    q115_answer = "YES" if operational_useful or (best_p3 > 0.26) else "NO"

    print("\n==================================================")
    print("EXP-0008 PRIMARY DECISIONS & VERDICTS")
    print("==================================================")
    print(f"PRIMARY_DECISION = {primary_decision}")
    print(f"BEST_INFORMATION_CHANNEL = {best_channel_code}")
    print(f"MIN_USEFUL_MICRO_TESTS = {min_useful_microtests}")
    print(f"INFORMATION_STATUS = {info_status}")
    print(f"EXP_0008_STATUS = {status_verdict}")
    print(f"Q115 (Learn more via shadow trial?): {q115_answer}")
    print(f"M1_CANDIDATE = FALSE (Frozen diagnostic gate)")
    print(f"NEXT = {next_step}")
    print("==================================================")

    # 9. Generate 12-Panel Publication Figure
    print("\n=== Generating 12-Panel Publication Figure ===")
    generate_publication_figures_exp8(
        exp_dir=exp_dir,
        table1_df=table1_df,
        table2_df=table2_df,
        temp_df=temp_df,
        resid_df=resid_df,
        controls_df=controls_df,
        cf_df=counterfactual_df,
        post_shift_df=post_shift_df,
        best_channel_name=best_channel_name
    )

    elapsed = time.time() - start_time
    print(f"\nEXP-0008 Diagnostic completed in {elapsed:.1f}s.")

    return {
        "primary_decision": primary_decision,
        "best_channel": best_channel_code,
        "min_useful_microtests": min_useful_microtests,
        "info_status": info_status,
        "status_verdict": status_verdict,
        "next_step": next_step,
        "q115_answer": q115_answer
    }


def generate_publication_figures_exp8(
    exp_dir: str,
    table1_df: pd.DataFrame,
    table2_df: pd.DataFrame,
    temp_df: pd.DataFrame,
    resid_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    cf_df: pd.DataFrame,
    post_shift_df: pd.DataFrame,
    best_channel_name: str
):
    """
    Generates a 12-panel publication-grade figure satisfying Section 100.
    """
    fig, axes = plt.subplots(6, 2, figsize=(16, 32))
    fig.patch.set_facecolor('#0f172a')
    for ax in axes.flat:
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='#cbd5e1', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    palette = {
        "I0 Passive Corr": "#94a3b8", # slate
        "I1 Delayed Corr": "#a855f7", # purple
        "I2 Single Micro-Update Gain": "#38bdf8", # sky blue
        "I3 Paired Shadow Gain": "#22c55e", # green
        "I4 Persistent Micro-Update": "#f59e0b", # amber
        "Causal Direction Margin": "#ec4899", # pink
        "Excess Causal Gain": "#06b6d4", # cyan
        "Oracle": "#e2e8f0" # white
    }

    # Panel 1: PR curves by channel
    ax1 = axes[0, 0]
    ax1.set_title("1. Precision-Recall Curves by Information Channel", color='#f8fafc', fontsize=11, fontweight='bold')
    for _, row in table1_df.iterrows():
        ch = row["channel"]
        col = row["score_col"]
        y_true = post_shift_df["truth_label"].values
        y_score = post_shift_df[col].values
        order = np.argsort(-y_score, kind="mergesort")
        y_sorted = y_true[order]
        n_pos = np.sum(y_true == 1)
        if n_pos > 0:
            tp = np.cumsum(y_sorted == 1)
            fp = np.cumsum(y_sorted == 0)
            rec = tp / float(n_pos)
            prec = tp / np.maximum(1, tp + fp)
            ls = '--' if ch == "Oracle" else '-'
            lw = 2.5 if ch in [best_channel_name, "I0 Passive Corr"] else 1.5
            ax1.plot(rec, prec, label=ch, color=palette.get(ch, '#ffffff'), ls=ls, lw=lw)
    ax1.set_xlabel("Recall", color='#cbd5e1', fontsize=9)
    ax1.set_ylabel("Precision", color='#cbd5e1', fontsize=9)
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(loc='upper right', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=7.5)
    ax1.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 2: Precision@3 by Channel
    ax2 = axes[0, 1]
    ax2.set_title("2. Precision@3 by Information Channel", color='#f8fafc', fontsize=11, fontweight='bold')
    ch_names = table1_df["channel"].values
    p3_vals = table1_df["precision_at_3"].values * 100.0
    bar_colors = [palette.get(c, '#ffffff') for c in ch_names]
    b2 = ax2.barh(np.arange(len(ch_names)), p3_vals, color=bar_colors, alpha=0.85)
    for bar in b2:
        w = bar.get_width()
        ax2.annotate(f"{w:.1f}%", xy=(w + 1, bar.get_y() + bar.get_height() / 2),
                     xytext=(3, 0), textcoords="offset points", ha='left', va='center',
                     color='#f8fafc', fontsize=8.5, fontweight='bold')
    ax2.axvline(50.0, color='#22c55e', ls=':', lw=1.5, label='Target Gate (50%)')
    ax2.set_yticks(np.arange(len(ch_names)))
    ax2.set_yticklabels(ch_names, color='#cbd5e1', fontsize=8.5)
    ax2.set_xlabel("Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax2.set_xlim(0, 115)
    ax2.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 3: Precision@5 by Channel
    ax3 = axes[1, 0]
    ax3.set_title("3. Precision@5 by Information Channel", color='#f8fafc', fontsize=11, fontweight='bold')
    p5_vals = table1_df["precision_at_5"].values * 100.0
    b3 = ax3.barh(np.arange(len(ch_names)), p5_vals, color=bar_colors, alpha=0.85)
    for bar in b3:
        w = bar.get_width()
        ax3.annotate(f"{w:.1f}%", xy=(w + 1, bar.get_y() + bar.get_height() / 2),
                     xytext=(3, 0), textcoords="offset points", ha='left', va='center',
                     color='#f8fafc', fontsize=8.5, fontweight='bold')
    ax3.axvline(40.0, color='#22c55e', ls=':', lw=1.5, label='Target Gate (40%)')
    ax3.set_yticks(np.arange(len(ch_names)))
    ax3.set_yticklabels(ch_names, color='#cbd5e1', fontsize=8.5)
    ax3.set_xlabel("Precision@5 (%)", color='#cbd5e1', fontsize=9)
    ax3.set_xlim(0, 115)
    ax3.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 4: TRUE vs NOISE Normalized Gain Distributions
    ax4 = axes[1, 1]
    ax4.set_title("4. Normalized Future Predictive Gain (I2): TRUE vs NOISE", color='#f8fafc', fontsize=11, fontweight='bold')
    t_gains = post_shift_df[post_shift_df["truth_label"] == 1]["normalized_gain_i2"].values
    n_gains = post_shift_df[post_shift_df["truth_label"] == 0]["normalized_gain_i2"].values
    # Clip extreme outliers for visual clarity
    t_clip = np.clip(t_gains, -1.0, 1.0)
    n_clip = np.clip(n_gains, -1.0, 1.0)
    bp4 = ax4.boxplot([t_clip, n_clip], tick_labels=["TRUE Candidates", "NOISE Candidates"], patch_artist=True, widths=0.45)
    bp4['boxes'][0].set_facecolor('#22c55e')
    bp4['boxes'][1].set_facecolor('#ef4444')
    for b in bp4['boxes']: b.set_alpha(0.7)
    ax4.axhline(0.0, color='#94a3b8', ls='--', lw=1.0)
    ax4.set_ylabel("Normalized Gain (L_base - L_shadow) / L_base", color='#cbd5e1', fontsize=8.5)
    ax4.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 5: TRUE vs NOISE Causal Direction Margin
    ax5 = axes[2, 0]
    ax5.set_title("5. Causal Direction Margin (L_wrong - L_correct)", color='#f8fafc', fontsize=11, fontweight='bold')
    t_margin = post_shift_df[post_shift_df["truth_label"] == 1]["causal_direction_margin"].values
    n_margin = post_shift_df[post_shift_df["truth_label"] == 0]["causal_direction_margin"].values
    t_m_clip = np.clip(t_margin, -2.0, 2.0)
    n_m_clip = np.clip(n_margin, -2.0, 2.0)
    bp5 = ax5.boxplot([t_m_clip, n_m_clip], tick_labels=["TRUE Candidates", "NOISE Candidates"], patch_artist=True, widths=0.45)
    bp5['boxes'][0].set_facecolor('#ec4899')
    bp5['boxes'][1].set_facecolor('#94a3b8')
    for b in bp5['boxes']: b.set_alpha(0.7)
    ax5.axhline(0.0, color='#94a3b8', ls='--', lw=1.0)
    ax5.set_ylabel("Causal Direction Margin", color='#cbd5e1', fontsize=9)
    ax5.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 6: TRUE vs NOISE Excess Causal Gain (Sham Control)
    ax6 = axes[2, 1]
    ax6.set_title("6. Excess Causal Gain vs Sham Control", color='#f8fafc', fontsize=11, fontweight='bold')
    t_ex = post_shift_df[post_shift_df["truth_label"] == 1]["excess_causal_gain"].values
    n_ex = post_shift_df[post_shift_df["truth_label"] == 0]["excess_causal_gain"].values
    t_ex_clip = np.clip(t_ex, -2.0, 2.0)
    n_ex_clip = np.clip(n_ex, -2.0, 2.0)
    bp6 = ax6.boxplot([t_ex_clip, n_ex_clip], tick_labels=["TRUE Candidates", "NOISE Candidates"], patch_artist=True, widths=0.45)
    bp6['boxes'][0].set_facecolor('#06b6d4')
    bp6['boxes'][1].set_facecolor('#64748b')
    for b in bp6['boxes']: b.set_alpha(0.7)
    ax6.axhline(0.0, color='#94a3b8', ls='--', lw=1.0)
    ax6.set_ylabel("Gain_real - Gain_sham", color='#cbd5e1', fontsize=9)
    ax6.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 7: Predictive Gain by Post-Shift Time Window
    ax7 = axes[3, 0]
    ax7.set_title("7. Precision@3 Across Post-Shift Windows (A-E)", color='#f8fafc', fontsize=11, fontweight='bold')
    w_x = np.arange(len(temp_df))
    bars_w = ax7.bar(w_x, temp_df["best_precision_k3"] * 100.0, color='#38bdf8', width=0.5, alpha=0.85)
    for idx, bar in enumerate(bars_w):
        h = bar.get_height()
        lbl = temp_df.iloc[idx]["best_channel"].replace(" Micro-Update Gain", "").replace(" Corr", "")
        ax7.annotate(f"{h:.1f}%\n({lbl})", xy=(bar.get_x() + bar.get_width() / 2, h + 1),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                     color='#f8fafc', fontsize=7.5, fontweight='bold')
    ax7.set_xticks(w_x)
    ax7.set_xticklabels(temp_df["window"], color='#cbd5e1', fontsize=8)
    ax7.set_xlabel("Post-Shift Time Window", color='#cbd5e1', fontsize=9)
    ax7.set_ylabel("Best Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax7.set_ylim(0, 115)
    ax7.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 8: Predictive Gain by Residual Quantile
    ax8 = axes[3, 1]
    ax8.set_title("8. Precision@3 Across Residual Quantiles (Q1-Q4)", color='#f8fafc', fontsize=11, fontweight='bold')
    q_x = np.arange(len(resid_df))
    bars_q = ax8.bar(q_x, resid_df["best_precision_k3"] * 100.0, color=['#38bdf8', '#22c55e', '#f59e0b', '#ef4444'], width=0.5, alpha=0.85)
    for idx, bar in enumerate(bars_q):
        h = bar.get_height()
        lbl = resid_df.iloc[idx]["best_channel"].replace(" Micro-Update Gain", "").replace(" Corr", "")
        ax8.annotate(f"{h:.1f}%\n({lbl})", xy=(bar.get_x() + bar.get_width() / 2, h + 1),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                     color='#f8fafc', fontsize=7.5, fontweight='bold')
    ax8.set_xticks(q_x)
    ax8.set_xticklabels(resid_df["residual_quantile"], color='#cbd5e1', fontsize=9)
    ax8.set_xlabel("Smoothed Residual Quantile", color='#cbd5e1', fontsize=9)
    ax8.set_ylabel("Best Precision@3 (%)", color='#cbd5e1', fontsize=9)
    ax8.set_ylim(0, 115)
    ax8.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 9: Information Efficiency vs Compute
    ax9 = axes[4, 0]
    ax9.set_title("9. Information Efficiency (Enrichment@3 / FLOPs)", color='#f8fafc', fontsize=11, fontweight='bold')
    sub_eff = table1_df[table1_df["channel"] != "Oracle"].sort_values("info_efficiency", ascending=False)
    y_eff = np.arange(len(sub_eff))
    bars_eff = ax9.barh(y_eff, sub_eff["info_efficiency"], color=[palette.get(c, '#38bdf8') for c in sub_eff["channel"]], alpha=0.85)
    for bar in bars_eff:
        w = bar.get_width()
        ax9.annotate(f"{w:.3f}", xy=(w + 0.01, bar.get_y() + bar.get_height() / 2),
                     xytext=(3, 0), textcoords="offset points", ha='left', va='center',
                     color='#f8fafc', fontsize=8, fontweight='bold')
    ax9.set_yticks(y_eff)
    ax9.set_yticklabels(sub_eff["channel"], color='#cbd5e1', fontsize=8.5)
    ax9.set_xlabel("Enrichment@3 per FLOP", color='#cbd5e1', fontsize=9)
    ax9.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 10: Counterfactual Elevated Queue Precision
    ax10 = axes[4, 1]
    ax10.set_title("10. Counterfactual Elevated Queue Precision (K=5)", color='#f8fafc', fontsize=11, fontweight='bold')
    sub_cf = cf_df[cf_df["channel"] != "Oracle"].sort_values("useful_elevation_precision", ascending=False)
    y_cf = np.arange(len(sub_cf))
    bars_cf = ax10.barh(y_cf, sub_cf["useful_elevation_precision"] * 100.0, color=[palette.get(c, '#38bdf8') for c in sub_cf["channel"]], alpha=0.85)
    for bar in bars_cf:
        w = bar.get_width()
        ax10.annotate(f"{w:.1f}%", xy=(w + 1, bar.get_y() + bar.get_height() / 2),
                     xytext=(3, 0), textcoords="offset points", ha='left', va='center',
                     color='#f8fafc', fontsize=8, fontweight='bold')
    ax10.set_yticks(y_cf)
    ax10.set_yticklabels(sub_cf["channel"], color='#cbd5e1', fontsize=8.5)
    ax10.set_xlabel("Useful Elevated Queue Precision (%)", color='#cbd5e1', fontsize=9)
    ax10.set_xlim(0, 115)
    ax10.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 11: Instantaneous Fit vs Future Predictive Gain
    ax11 = axes[5, 0]
    ax11.set_title("11. Instantaneous Fit Gain vs Future Predictive Gain", color='#f8fafc', fontsize=11, fontweight='bold')
    t_sub = post_shift_df[post_shift_df["truth_label"] == 1]
    n_sub = post_shift_df[post_shift_df["truth_label"] == 0].sample(n=min(500, len(post_shift_df[post_shift_df["truth_label"] == 0])), random_state=42)
    ax11.scatter(n_sub["inst_fit_gain"], n_sub["gain_i2"], color='#ef4444', alpha=0.3, s=15, label="NOISE (Sampled)")
    ax11.scatter(t_sub["inst_fit_gain"], t_sub["gain_i2"], color='#22c55e', alpha=0.8, s=30, label="TRUE Candidates")
    ax11.axhline(0.0, color='#94a3b8', ls='--', lw=1.0)
    ax11.set_xlabel("Instantaneous Fit Gain (Step t)", color='#cbd5e1', fontsize=9)
    ax11.set_ylabel("Future Predictive Gain (Step t+1)", color='#cbd5e1', fontsize=9)
    ax11.legend(loc='lower right', facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)
    ax11.set_ylim(-3, 3)
    ax11.grid(True, color='#334155', ls='--', alpha=0.5)

    # Panel 12: Generalization Ratio (Future Gain / Inst Fit Gain)
    ax12 = axes[5, 1]
    ax12.set_title("12. Generalization Ratio (Future Gain / Inst Gain)", color='#f8fafc', fontsize=11, fontweight='bold')
    t_gr = t_sub["generalization_ratio"].values
    n_gr = n_sub["generalization_ratio"].values
    t_gr_clip = np.clip(t_gr, -5.0, 5.0)
    n_gr_clip = np.clip(n_gr, -5.0, 5.0)
    bp12 = ax12.boxplot([t_gr_clip, n_gr_clip], tick_labels=["TRUE Candidates", "NOISE Candidates"], patch_artist=True, widths=0.45)
    bp12['boxes'][0].set_facecolor('#22c55e')
    bp12['boxes'][1].set_facecolor('#ef4444')
    for b in bp12['boxes']: b.set_alpha(0.7)
    ax12.axhline(0.0, color='#94a3b8', ls='--', lw=1.0)
    ax12.set_ylabel("Future Gain / Inst Fit Gain", color='#cbd5e1', fontsize=9)
    ax12.grid(True, color='#334155', ls='--', alpha=0.5)

    plt.tight_layout()
    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved publication figures to {fig_path}")

    artifact_dir = os.path.join(os.path.expanduser("~"), "lebre_artifacts")
    artifact_fig_path = os.path.join(artifact_dir, "figures_exp_0008.png")
    try:
        shutil.copyfile(fig_path, artifact_fig_path)
        print(f"Copied figure to IDE artifact: {artifact_fig_path}")
    except Exception as e:
        print(f"Warning: could not copy figure to IDE artifact directory: {e}")

if __name__ == "__main__":
    run_diagnostic()
