import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.dense_nlms import DenseNLMS
from src.learners.adaptive_evidence_learner import AdaptiveEvidenceLearner
from src.policies.explore_confirm_policy import ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController
from src.utils.accounting import ResourceTracker

def parse_args():
    parser = argparse.ArgumentParser(description="EXP-0005: Adaptive Evidence Accumulation")
    parser.add_argument("--dev", action="store_true", help="Run DEV calibration mode on seed 9999 only")
    parser.add_argument("--n-fast", type=int, default=3, help="Fast evidence requirement threshold (default 3)")
    parser.add_argument("--theta-strong", type=float, default=0.50, help="Strong correlation threshold (default 0.50)")
    parser.add_argument("--gamma-strong", type=float, default=1.00, help="Sign consistency threshold (default 1.00)")
    return parser.parse_args()

def run_experiment():
    args = parse_args()
    exp_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(exp_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    if args.dev:
        seeds = [config["dev_seed"]]
        rep_seed = config["dev_seed"]
        print(f"=== Running EXP-0005: DEV Calibration Mode (Seeds: {seeds}) ===")
    else:
        seeds = config["seeds"]
        rep_seed = 42
        print(f"=== Running EXP-0005: Adaptive Evidence Accumulation (Seeds: {seeds}) ===")

    models = [
        "Dense",
        "Sparse_Oracle",
        "H0_Fixed_Baseline",
        "H1_Lower_Fixed",
        "H2_Strength_Adaptive",
        "H3_Strength_Consistency",
        "H4_Early_Accept",
        "H5_Oracle_Stopping"
    ]
    sparse_models = [m for m in models if m not in ["Dense", "Sparse_Oracle"]]

    n_fast = args.n_fast
    theta_strong = args.theta_strong
    gamma_strong = args.gamma_strong

    seed_summaries = []
    all_evidence_events = []
    all_feat_latencies = []
    all_promotion_metrics = []
    events_seed42 = []
    rep_trajectories = {m: {} for m in models}

    r2_true_indices = sorted(config["regime_2"]["indices"])
    shift_step = config["shift_step"]
    tau_mature = config["tau_mature"]

    start_time = time.time()

    for seed in seeds:
        print(f"\n--- Running Seed {seed} ---")
        rng = np.random.RandomState(seed)
        init_supp = list(rng.choice(config["d_features"], size=config["k_true"], replace=False))

        # Initialize Models
        dense = DenseNLMS(d=config["d_features"], mu=config["nlms_mu"], eps=config["nlms_eps"])
        w_oracle = np.zeros(config["k_star"], dtype=np.float64)

        controllers = {
            m: ProbeBankController(
                q_min=config["q_min"],
                q_base=config["q_base"],
                q_max=config["q_max"],
                tau_low=config["tau_low"],
                tau_high=config["tau_high"],
                alpha=config["ema_alpha"],
                total_steps=config["total_steps"],
                target_budget=config["target_total_probes"]
            ) for m in sparse_models
        }

        policies = {
            m: ExploreConfirmPolicy(
                d=config["d_features"],
                c_max=config["c_max"],
                n_screen=config["n_screen"],
                theta_screen=config["theta_screen"],
                gamma_screen=config["gamma_screen"],
                theta_drop=config["theta_drop"],
                gamma_drop=config["gamma_drop"],
                confirm_max_probes=config["confirm_max_probes"],
                confirm_fraction=config["confirm_fraction_f4"],
                coverage_fraction=config["coverage_fraction_f4"]
            ) for m in sparse_models
        }

        def build_learner(model_name):
            rule_map = {
                "H0_Fixed_Baseline": "fixed_baseline",
                "H1_Lower_Fixed": "lower_fixed",
                "H2_Strength_Adaptive": "strength_adaptive",
                "H3_Strength_Consistency": "strength_consistency",
                "H4_Early_Accept": "early_accept",
                "H5_Oracle_Stopping": "oracle_stopping"
            }
            return AdaptiveEvidenceLearner(
                d=config["d_features"],
                initial_support=list(init_supp),
                probe_policy=policies[model_name],
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
                evidence_rule=rule_map[model_name],
                n_fast=n_fast,
                theta_strong=theta_strong,
                gamma_strong=gamma_strong
            )

        learners = {m: build_learner(m) for m in sparse_models}

        histories = {m: {
            "losses": [],
            "r1_losses": [],
            "r2_losses": [],
            "full_r2_losses": [],
            "recalls": [],
            "r2_recalls": [],
            "full_supp_flags": [],
            "omitted_energy": [],
            "q_history": [],
            "flops_history": [],
            "promotions_list": [],
            "displacements": 0,
            "redundant_repromotions": 0,
            "seen_promoted_true": set(),
        } for m in models}

        feat_tracking = {m: {
            f: {
                "first_probe": None,
                "promotion": None,
                "evictions": [],
                "stable_retention": None
            } for f in r2_true_indices
        } for m in sparse_models}

        env = DynamicSparseLinearStream(config, seed=seed)

        for t in range(1, config["total_steps"] + 1):
            x, y, true_supp, true_beta = env.step()
            true_idx = sorted(list(true_supp))

            # 1. Dense Reference
            y_hat_dense = dense.predict(x)
            dense_stats = dense.update(x, y)
            err_dense = y - y_hat_dense
            loss_dense = err_dense ** 2
            histories["Dense"]["losses"].append(loss_dense)
            histories["Dense"]["flops_history"].append(dense_stats["flops"])
            histories["Dense"]["recalls"].append(1.0)
            histories["Dense"]["omitted_energy"].append(0.0)
            histories["Dense"]["q_history"].append(0)
            if t <= shift_step:
                histories["Dense"]["r1_losses"].append(loss_dense)
            else:
                histories["Dense"]["full_r2_losses"].append(loss_dense)
                histories["Dense"]["r2_recalls"].append(1.0)
                histories["Dense"]["full_supp_flags"].append(1)
            if t > 1800:
                histories["Dense"]["r2_losses"].append(loss_dense)

            # 2. Sparse Oracle Support
            x_orc = x[true_idx]
            y_hat_orc = float(np.dot(w_oracle, x_orc))
            err_orc = y - y_hat_orc
            loss_orc = err_orc ** 2
            norm_orc = float(np.dot(x_orc, x_orc))
            w_oracle += (config["nlms_mu"] / (config["nlms_eps"] + norm_orc)) * err_orc * x_orc
            orc_flops = ResourceTracker.dot_product_flops(5) + ResourceTracker.norm_sq_flops(5) + ResourceTracker.vector_update_flops(5) + 3
            histories["Sparse_Oracle"]["losses"].append(loss_orc)
            histories["Sparse_Oracle"]["flops_history"].append(orc_flops)
            histories["Sparse_Oracle"]["recalls"].append(1.0)
            histories["Sparse_Oracle"]["omitted_energy"].append(0.0)
            histories["Sparse_Oracle"]["q_history"].append(0)
            if t <= shift_step:
                histories["Sparse_Oracle"]["r1_losses"].append(loss_orc)
            else:
                histories["Sparse_Oracle"]["full_r2_losses"].append(loss_orc)
                histories["Sparse_Oracle"]["r2_recalls"].append(1.0)
                histories["Sparse_Oracle"]["full_supp_flags"].append(1)
            if t > 1800:
                histories["Sparse_Oracle"]["r2_losses"].append(loss_orc)

            # 3. Sparse Models H0 to H5
            for m in sparse_models:
                learner = learners[m]
                ctrl = controllers[m]

                y_hat = learner.predict(x)
                err = y - y_hat
                loss = err ** 2

                q_t = ctrl.get_q(err, t)
                stats = learner.update(x, y, q=q_t, true_support=true_supp)
                probed_candidates = stats["candidates"]

                # First probe in Regime 2
                if t > shift_step:
                    for cand in probed_candidates:
                        if cand in r2_true_indices and feat_tracking[m][cand]["first_probe"] is None:
                            feat_tracking[m][cand]["first_probe"] = t

                # Post-update support tracking
                act_supp = list(learner.support)
                true_in_supp = set(act_supp).intersection(true_supp)
                recall = len(true_in_supp) / float(config["k_star"])
                is_full = 1 if len(true_in_supp) == config["k_star"] else 0

                omitted = [j for j in true_supp if j not in act_supp]
                e_omit = float(np.sum([true_beta[j] ** 2 for j in omitted])) if omitted else 0.0

                p_feat = stats["promoted_feat"]
                v_feat = stats["victim_feat"]

                if p_feat is not None:
                    is_true_promo = 1 if (p_feat in true_supp) else 0
                    if is_true_promo:
                        if p_feat in histories[m]["seen_promoted_true"]:
                            histories[m]["redundant_repromotions"] += 1
                        histories[m]["seen_promoted_true"].add(p_feat)
                        if t > shift_step and p_feat in r2_true_indices and feat_tracking[m][p_feat]["promotion"] is None:
                            feat_tracking[m][p_feat]["promotion"] = t

                    promo_record = {
                        "seed": seed,
                        "model": m,
                        "feature": p_feat,
                        "is_true": is_true_promo,
                        "promotion_step": t,
                        "eviction_step": None,
                        "lifetime": None,
                        "survived_50": 0,
                        "survived_100": 0
                    }
                    histories[m]["promotions_list"].append(promo_record)

                if v_feat is not None:
                    v_is_true = 1 if (v_feat in true_supp) else 0
                    if t > shift_step and v_feat in r2_true_indices:
                        feat_tracking[m][v_feat]["evictions"].append(t)

                    if v_is_true and (p_feat is not None and p_feat not in true_supp):
                        histories[m]["displacements"] += 1

                    for pr in reversed(histories[m]["promotions_list"]):
                        if pr["feature"] == v_feat and pr["eviction_step"] is None:
                            pr["eviction_step"] = t
                            pr["lifetime"] = t - pr["promotion_step"]
                            pr["survived_50"] = 1 if pr["lifetime"] >= 50 else 0
                            pr["survived_100"] = 1 if pr["lifetime"] >= 100 else 0
                            break

                # Detailed Event Trace for Seed 42 on Support Edits (Section 73)
                if seed == rep_seed and (p_feat is not None or v_feat is not None):
                    events_seed42.append({
                        "step": t,
                        "model": m,
                        "candidate_id": p_feat,
                        "truth_status": 1 if (p_feat is not None and p_feat in true_supp) else 0,
                        "candidate_state": "CONFIRM" if (p_feat in policies[m].confirm_set) else "EXPLORE",
                        "n_j": stats["cand_evidence_count"],
                        "mean_corr_j": stats["cand_score"],
                        "sign_consistency_j": stats["sign_consistency"],
                        "required_n_j": stats["required_n"],
                        "early_stop_triggered": stats["used_early_stop"],
                        "promotion_decision": "SWAP" if v_feat is not None else ("GROW" if p_feat is not None else "NONE"),
                        "victim": v_feat,
                        "victim_truth_status": 1 if (v_feat is not None and v_feat in true_supp) else 0,
                        "support_recall": recall
                    })

                histories[m]["losses"].append(loss)
                histories[m]["flops_history"].append(stats["flops"])
                histories[m]["recalls"].append(recall)
                histories[m]["omitted_energy"].append(e_omit)
                histories[m]["q_history"].append(q_t)
                if t <= shift_step:
                    histories[m]["r1_losses"].append(loss)
                else:
                    histories[m]["full_r2_losses"].append(loss)
                    histories[m]["r2_recalls"].append(recall)
                    histories[m]["full_supp_flags"].append(is_full)
                if t > 1800:
                    histories[m]["r2_losses"].append(loss)

        if seed == rep_seed:
            for m in models:
                rep_trajectories[m] = histories[m]

        # Post-process Feature Latencies for Regime 2
        for m in sparse_models:
            final_supp = set(learners[m].support)
            for f in r2_true_indices:
                if f in final_supp:
                    p_step = feat_tracking[m][f]["promotion"]
                    evicts = [ev for ev in feat_tracking[m][f]["evictions"] if (p_step and ev > p_step)] if p_step else []
                    if not evicts:
                        feat_tracking[m][f]["stable_retention"] = p_step
                    else:
                        last_evict = max(evicts)
                        promos_after = [pr["promotion_step"] for pr in histories[m]["promotions_list"] if pr["feature"] == f and pr["promotion_step"] > last_evict]
                        feat_tracking[m][f]["stable_retention"] = min(promos_after) if promos_after else 2000
                else:
                    feat_tracking[m][f]["stable_retention"] = 2000

                fp = feat_tracking[m][f]["first_probe"] if feat_tracking[m][f]["first_probe"] is not None else 2000
                pr = feat_tracking[m][f]["promotion"] if feat_tracking[m][f]["promotion"] is not None else 2000
                sr = feat_tracking[m][f]["stable_retention"] if feat_tracking[m][f]["stable_retention"] is not None else 2000

                t_wait = max(0, fp - (shift_step + 1))
                t_evid = max(0, pr - fp)
                t_post = max(0, sr - pr)
                t_tot = max(0, sr - (shift_step + 1))

                all_feat_latencies.append({
                    "seed": seed,
                    "model": m,
                    "feature": f,
                    "first_relevant_step": shift_step + 1,
                    "first_probe": fp,
                    "promotion": pr,
                    "first_stable_retention": sr,
                    "t_wait_probe": t_wait,
                    "t_evidence": t_evid,
                    "t_post_promotion": t_post,
                    "t_total": t_tot
                })

            # Append evidence events from learner log
            for ev in learners[m].evidence_events_log:
                ev_copy = dict(ev)
                ev_copy["seed"] = seed
                ev_copy["model"] = m
                all_evidence_events.append(ev_copy)

            # Promotion safety metrics
            tot_p = learners[m].total_promotions
            true_p = learners[m].true_promotions
            false_p = learners[m].false_promotions
            p_prec = true_p / max(1, tot_p)

            early_p = learners[m].early_promotions
            t_early_p = learners[m].true_early_promotions
            f_early_p = learners[m].false_early_promotions
            early_prec = t_early_p / max(1, early_p)
            early_rec = t_early_p / max(1, true_p)

            # Mean N at promotion for true vs noise
            ev_model = [ev for ev in learners[m].evidence_events_log]
            true_ns = [ev["n_at_promotion"] for ev in ev_model if ev["is_true"] == 1]
            noise_ns = [ev["n_at_promotion"] for ev in ev_model if ev["is_true"] == 0]
            mean_n_true = float(np.mean(true_ns)) if true_ns else 0.0
            mean_n_noise = float(np.mean(noise_ns)) if noise_ns else 0.0

            # Survival metrics
            all_true_promos = [pr for pr in histories[m]["promotions_list"] if pr["is_true"] == 1]
            for pr in all_true_promos:
                if pr["eviction_step"] is None:
                    life = (config["total_steps"] + 1) - pr["promotion_step"]
                    pr["survived_50"] = 1 if life >= 50 else 0
                    pr["survived_100"] = 1 if life >= 100 else 0
            surv_50 = np.mean([pr["survived_50"] for pr in all_true_promos]) if all_true_promos else 1.0

            # Flops
            m_flops = float(np.mean(histories[m]["flops_history"]))
            peak_flops = float(np.max(histories[m]["flops_history"]))
            c_ratio = m_flops / 602.0

            # Summary metrics
            seed_summaries.append({
                "seed": seed,
                "model": m,
                "global_mse": float(np.mean(histories[m]["losses"])),
                "regime_1_mse": float(np.mean(histories[m]["r1_losses"])),
                "regime_2_mse": float(np.mean(histories[m]["r2_losses"])),
                "final_recall": float(histories[m]["recalls"][-1]),
                "mean_r2_recall": float(np.mean(histories[m]["r2_recalls"])),
                "full_support_occupancy": float(np.mean(histories[m]["full_supp_flags"])),
                "stable_acquisition_latency": float(np.mean([l["t_total"] for l in all_feat_latencies if l["seed"] == seed and l["model"] == m])),
                "t_wait_probe": float(np.mean([l["t_wait_probe"] for l in all_feat_latencies if l["seed"] == seed and l["model"] == m])),
                "t_evidence": float(np.mean([l["t_evidence"] for l in all_feat_latencies if l["seed"] == seed and l["model"] == m])),
                "t_post_promotion": float(np.mean([l["t_post_promotion"] for l in all_feat_latencies if l["seed"] == seed and l["model"] == m])),
                "mean_n_at_promotion_true": mean_n_true,
                "mean_n_at_promotion_noise": mean_n_noise,
                "early_promotion_precision": early_prec,
                "early_promotion_recall": early_rec,
                "promotion_precision": p_prec,
                "false_promotions_per_100_steps": float(false_p / 20.0),
                "noise_to_true_displacements": histories[m]["displacements"],
                "true_survival_50": float(surv_50),
                "total_probes": sum(histories[m]["q_history"]),
                "mean_flops": m_flops,
                "peak_flops": peak_flops,
                "compute_ratio_dense": c_ratio,
                "memory_bytes": int(ResourceTracker.estimate_memory_bytes(len(learners[m].support), config["d_features"], config["d_features"], is_welford=True, is_extended=True))
            })

            all_promotion_metrics.append({
                "seed": seed,
                "model": m,
                "total_promotions": tot_p,
                "true_promotions": true_p,
                "false_promotions": false_p,
                "promotion_precision": p_prec,
                "early_promotions": early_p,
                "true_early_promotions": t_early_p,
                "false_early_promotions": f_early_p,
                "early_promotion_precision": early_prec,
                "early_promotion_recall": early_rec,
                "mean_n_true": mean_n_true,
                "mean_n_noise": mean_n_noise
            })

        # Add Dense and Sparse_Oracle summaries
        for ref_m, fl_ref, mem_ref in [("Dense", 602.0, 2400), ("Sparse_Oracle", 32.0, 880)]:
            seed_summaries.append({
                "seed": seed,
                "model": ref_m,
                "global_mse": float(np.mean(histories[ref_m]["losses"])),
                "regime_1_mse": float(np.mean(histories[ref_m]["r1_losses"])),
                "regime_2_mse": float(np.mean(histories[ref_m]["r2_losses"])),
                "final_recall": 1.0,
                "mean_r2_recall": 1.0,
                "full_support_occupancy": 1.0,
                "stable_acquisition_latency": 0.0,
                "t_wait_probe": 0.0,
                "t_evidence": 0.0,
                "t_post_promotion": 0.0,
                "mean_n_at_promotion_true": 0.0,
                "mean_n_at_promotion_noise": 0.0,
                "early_promotion_precision": 1.0,
                "early_promotion_recall": 0.0,
                "promotion_precision": 1.0,
                "false_promotions_per_100_steps": 0.0,
                "noise_to_true_displacements": 0,
                "true_survival_50": 1.0,
                "total_probes": 0,
                "mean_flops": fl_ref,
                "peak_flops": fl_ref,
                "compute_ratio_dense": fl_ref / 602.0,
                "memory_bytes": mem_ref
            })

    elapsed = time.time() - start_time
    print(f"\nAll runs completed in {elapsed:.2f} seconds.")

    # Save CSV Artifacts
    df_evidence = pd.DataFrame(all_evidence_events)
    df_evidence.to_csv(os.path.join(exp_dir, "evidence_events.csv"), index=False)

    df_promo_metrics = pd.DataFrame(all_promotion_metrics)
    df_promo_metrics.to_csv(os.path.join(exp_dir, "promotion_metrics.csv"), index=False)

    df_feat_lat = pd.DataFrame(all_feat_latencies)
    df_feat_lat.to_csv(os.path.join(exp_dir, "latency_decomposition.csv"), index=False)

    if events_seed42:
        df_seed42 = pd.DataFrame(events_seed42)
        df_seed42.to_csv(os.path.join(exp_dir, "events_seed42.csv"), index=False)

    df_summary = pd.DataFrame(seed_summaries)
    df_summary.to_csv(os.path.join(exp_dir, "seed_summaries.csv"), index=False)

    agg_cols = [
        "global_mse", "regime_1_mse", "regime_2_mse", "final_recall", "mean_r2_recall",
        "full_support_occupancy", "stable_acquisition_latency", "t_wait_probe",
        "t_evidence", "t_post_promotion", "mean_n_at_promotion_true", "mean_n_at_promotion_noise",
        "early_promotion_precision", "early_promotion_recall", "promotion_precision",
        "false_promotions_per_100_steps", "noise_to_true_displacements", "true_survival_50",
        "total_probes", "mean_flops", "peak_flops", "compute_ratio_dense", "memory_bytes"
    ]
    grouped = df_summary.groupby("model")[agg_cols].mean().reset_index()
    grouped["model_order"] = grouped["model"].apply(lambda m: models.index(m) if m in models else 99)
    grouped = grouped.sort_values("model_order").drop(columns=["model_order"])
    grouped.to_csv(os.path.join(exp_dir, "results.csv"), index=False)

    print("\n=== EXP-0005 AGGREGATE RESULTS SUMMARY ===")
    display_cols = [
        "model", "regime_2_mse", "mean_r2_recall", "full_support_occupancy",
        "t_evidence", "t_post_promotion", "promotion_precision", "early_promotion_precision",
        "noise_to_true_displacements", "mean_flops", "compute_ratio_dense"
    ]
    print(grouped[display_cols].to_string(index=False))

    # Generate 10-Panel Figures
    generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, df_evidence, models, rep_seed)

    return grouped, df_summary

def generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, df_evidence, models, rep_seed):
    print("\nGenerating 10-panel figure artifact...")
    fig = plt.figure(figsize=(24, 20))

    colors = {
        "Dense": "black",
        "Sparse_Oracle": "green",
        "H0_Fixed_Baseline": "gray",
        "H1_Lower_Fixed": "red",
        "H2_Strength_Adaptive": "purple",
        "H3_Strength_Consistency": "blue",
        "H4_Early_Accept": "orange",
        "H5_Oracle_Stopping": "teal"
    }

    def rolling_mean(arr, window=20):
        return pd.Series(arr).rolling(window, min_periods=1).mean().values

    # 1. Regime-2 MSE vs time
    ax1 = fig.add_subplot(4, 3, 1)
    for m in models:
        losses = rep_trajectories[m].get("losses", [])
        if losses:
            ax1.plot(range(1000, 2000), rolling_mean(losses[1000:], 30), label=m, color=colors.get(m, "blue"), alpha=0.85, lw=1.8)
    ax1.set_title(f"1. Regime-2 MSE vs Time (Seed {rep_seed})")
    ax1.set_xlabel("Simulation Step")
    ax1.set_ylabel("MSE (Rolling 30)")
    ax1.set_yscale("log")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8, loc="upper right")

    # 2. Support recall vs time
    ax2 = fig.add_subplot(4, 3, 2)
    for m in models:
        rec = rep_trajectories[m].get("recalls", [])
        if rec:
            ax2.plot(range(1000, 2000), rec[1000:], label=m, color=colors.get(m, "blue"), alpha=0.85, lw=1.8)
    ax2.set_title(f"2. Support Recall vs Time (Regime 2, Seed {rep_seed})")
    ax2.set_xlabel("Simulation Step")
    ax2.set_ylabel("Recall")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8, loc="lower right")

    # 3. Full-support occupancy timeline
    ax3 = fig.add_subplot(4, 3, 3)
    for m in [m for m in models if m not in ["Dense", "Sparse_Oracle"]]:
        flags = rep_trajectories[m].get("full_supp_flags", [])
        if flags:
            cum_occ = np.cumsum(flags) / (np.arange(len(flags)) + 1)
            ax3.plot(range(1001, 2001), cum_occ, label=m, color=colors.get(m, "blue"), lw=1.8)
    ax3.set_title("3. Full-Support Occupancy Timeline")
    ax3.set_xlabel("Simulation Step")
    ax3.set_ylabel("Cumulative Occupancy")
    ax3.axhline(0.75, color="red", linestyle="--", alpha=0.7, label="GO Target (>= 75%)")
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=8, loc="lower right")

    # 4. T_evidence distribution
    ax4 = fig.add_subplot(4, 3, 4)
    sparse_models = [m for m in models if m not in ["Dense", "Sparse_Oracle"]]
    t_evid_data = []
    labels = []
    for m in sparse_models:
        vals = df_feat_lat[df_feat_lat["model"] == m]["t_evidence"].values
        t_evid_data.append(vals)
        labels.append(m)
    ax4.boxplot(t_evid_data, tick_labels=labels)
    ax4.axhline(70, color="red", linestyle="--", label="GO Target (<= 70 steps)")
    ax4.axhline(50, color="green", linestyle="--", label="STRONG_GO (<= 50 steps)")
    ax4.set_title("4. T_evidence Distribution")
    ax4.set_ylabel("Steps (First Probe -> Promotion)")
    ax4.tick_params(axis='x', rotation=30)
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=8)

    # 5. N_at_promotion True vs Noise
    ax5 = fig.add_subplot(4, 3, 5)
    if not df_evidence.empty:
        n_true = []
        n_noise = []
        m_labels = []
        for m in sparse_models:
            sub = df_evidence[df_evidence["model"] == m]
            t_vals = sub[sub["is_true"] == 1]["n_at_promotion"].values
            n_vals = sub[sub["is_true"] == 0]["n_at_promotion"].values
            n_true.append(np.mean(t_vals) if len(t_vals) > 0 else 0)
            n_noise.append(np.mean(n_vals) if len(n_vals) > 0 else 0)
            m_labels.append(m)
        x_idx = np.arange(len(m_labels))
        w = 0.35
        ax5.bar(x_idx - w/2, n_true, width=w, label="True Candidates", color="teal")
        ax5.bar(x_idx + w/2, n_noise, width=w, label="Noise Candidates", color="crimson")
        ax5.set_xticks(x_idx)
        ax5.set_xticklabels(m_labels, rotation=30)
        ax5.set_title("5. Mean N at Promotion: True vs Noise")
        ax5.set_ylabel("Evidence Count (n)")
        ax5.grid(True, alpha=0.3)
        ax5.legend(fontsize=8)
    else:
        ax5.text(0.5, 0.5, "No Evidence Events", ha='center', va='center')
        ax5.set_title("5. Mean N at Promotion")

    # 6. Mean correlation at promotion True vs Noise
    ax6 = fig.add_subplot(4, 3, 6)
    if not df_evidence.empty:
        corr_true = []
        corr_noise = []
        for m in sparse_models:
            sub = df_evidence[df_evidence["model"] == m]
            t_vals = sub[sub["is_true"] == 1]["mean_corr"].values
            n_vals = sub[sub["is_true"] == 0]["mean_corr"].values
            corr_true.append(np.mean(t_vals) if len(t_vals) > 0 else 0)
            corr_noise.append(np.mean(n_vals) if len(n_vals) > 0 else 0)
        x_idx = np.arange(len(sparse_models))
        w = 0.35
        ax6.bar(x_idx - w/2, corr_true, width=w, label="True Candidates", color="teal")
        ax6.bar(x_idx + w/2, corr_noise, width=w, label="Noise Candidates", color="crimson")
        ax6.set_xticks(x_idx)
        ax6.set_xticklabels(sparse_models, rotation=30)
        ax6.set_title("6. Mean |Correlation| at Promotion")
        ax6.set_ylabel("|Mean Correlation|")
        ax6.grid(True, alpha=0.3)
        ax6.legend(fontsize=8)
    else:
        ax6.text(0.5, 0.5, "No Evidence Events", ha='center', va='center')
        ax6.set_title("6. Mean |Correlation| at Promotion")

    # 7. Sign consistency at promotion True vs Noise
    ax7 = fig.add_subplot(4, 3, 7)
    if not df_evidence.empty:
        sc_true = []
        sc_noise = []
        for m in sparse_models:
            sub = df_evidence[df_evidence["model"] == m]
            t_vals = sub[sub["is_true"] == 1]["sign_consistency"].values
            n_vals = sub[sub["is_true"] == 0]["sign_consistency"].values
            sc_true.append(np.mean(t_vals) if len(t_vals) > 0 else 0)
            sc_noise.append(np.mean(n_vals) if len(n_vals) > 0 else 0)
        x_idx = np.arange(len(sparse_models))
        w = 0.35
        ax7.bar(x_idx - w/2, sc_true, width=w, label="True Candidates", color="teal")
        ax7.bar(x_idx + w/2, sc_noise, width=w, label="Noise Candidates", color="crimson")
        ax7.set_xticks(x_idx)
        ax7.set_xticklabels(sparse_models, rotation=30)
        ax7.set_title("7. Sign Consistency at Promotion")
        ax7.set_ylabel("Sign Consistency")
        ax7.axhline(0.80, color="blue", linestyle="--", alpha=0.5, label="gamma_strong (0.80)")
        ax7.grid(True, alpha=0.3)
        ax7.legend(fontsize=8)
    else:
        ax7.text(0.5, 0.5, "No Evidence Events", ha='center', va='center')
        ax7.set_title("7. Sign Consistency at Promotion")

    # 8. Cumulative True vs False Promotions
    ax8 = fig.add_subplot(4, 3, 8)
    if not df_evidence.empty:
        for m in ["H0_Fixed_Baseline", "H1_Lower_Fixed", "H3_Strength_Consistency"]:
            sub = df_evidence[(df_evidence["model"] == m) & (df_evidence["seed"] == rep_seed)].sort_values("step")
            if not sub.empty:
                steps = sub["step"].values
                cum_true = np.cumsum(sub["is_true"].values)
                cum_false = np.cumsum(1 - sub["is_true"].values)
                ax8.plot(steps, cum_true, label=f"{m} (True)", linestyle="-", color=colors.get(m, "blue"))
                ax8.plot(steps, cum_false, label=f"{m} (False)", linestyle="--", color=colors.get(m, "blue"), alpha=0.7)
        ax8.set_title(f"8. Cumulative Promotions (Seed {rep_seed})")
        ax8.set_xlabel("Simulation Step")
        ax8.set_ylabel("Cumulative Count")
        ax8.grid(True, alpha=0.3)
        ax8.legend(fontsize=8)
    else:
        ax8.text(0.5, 0.5, "No Events", ha='center', va='center')
        ax8.set_title("8. Cumulative Promotions")

    # 9. Early Promotion Events Over Time
    ax9 = fig.add_subplot(4, 3, 9)
    if not df_evidence.empty:
        early_sub = df_evidence[(df_evidence["used_early_stop"] == 1) & (df_evidence["seed"] == rep_seed)]
        if not early_sub.empty:
            for m in ["H1_Lower_Fixed", "H2_Strength_Adaptive", "H3_Strength_Consistency", "H4_Early_Accept"]:
                m_early = early_sub[early_sub["model"] == m]
                if not m_early.empty:
                    ax9.hist(m_early["step"].values, bins=20, alpha=0.5, label=m, color=colors.get(m, "blue"))
        ax9.set_title(f"9. Early Promotion Events Over Time (Seed {rep_seed})")
        ax9.set_xlabel("Simulation Step")
        ax9.set_ylabel("Count")
        ax9.grid(True, alpha=0.3)
        ax9.legend(fontsize=8)
    else:
        ax9.text(0.5, 0.5, "No Early Promotions", ha='center', va='center')
        ax9.set_title("9. Early Promotion Events")

    # 10. Latency Decomposition Comparison
    ax10 = fig.add_subplot(4, 3, 10)
    lat_summary = df_feat_lat.groupby("model")[["t_wait_probe", "t_evidence", "t_post_promotion"]].mean().reset_index()
    lat_summary["model_order"] = lat_summary["model"].apply(lambda m: sparse_models.index(m) if m in sparse_models else 99)
    lat_summary = lat_summary.sort_values("model_order").drop(columns=["model_order"])

    x_idx = np.arange(len(lat_summary))
    w = 0.55
    ax10.bar(x_idx, lat_summary["t_wait_probe"], width=w, label="T_wait_probe", color="lightgray")
    ax10.bar(x_idx, lat_summary["t_evidence"], width=w, bottom=lat_summary["t_wait_probe"], label="T_evidence", color="steelblue")
    ax10.bar(x_idx, lat_summary["t_post_promotion"], width=w, bottom=lat_summary["t_wait_probe"] + lat_summary["t_evidence"], label="T_post_promotion", color="darkorange")
    ax10.set_xticks(x_idx)
    ax10.set_xticklabels(lat_summary["model"], rotation=30)
    ax10.set_title("10. Latency Decomposition by Model")
    ax10.set_ylabel("Mean Steps")
    ax10.grid(True, alpha=0.3)
    ax10.legend(fontsize=8)

    plt.tight_layout()
    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Saved 10-panel figures artifact to: {fig_path}")

if __name__ == "__main__":
    run_experiment()
