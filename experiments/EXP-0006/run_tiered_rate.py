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
from src.learners.tiered_evidence_learner import TieredEvidenceLearner
from src.policies.tiered_rate_policy import TieredEvidenceRatePolicy
from src.controllers.probe_controllers import ProbeBankController
from src.utils.accounting import ResourceTracker

def parse_args():
    parser = argparse.ArgumentParser(description="EXP-0006: Tiered Evidence-Rate Allocation")
    parser.add_argument("--dev", action="store_true", help="Run DEV calibration mode on seed 9999 only")
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
        print(f"=== Running EXP-0006: DEV Calibration Mode (Seeds: {seeds}) ===")
    else:
        seeds = config["seeds"]
        rep_seed = 42
        print(f"=== Running EXP-0006: Tiered Evidence-Rate Allocation (Seeds: {seeds}) ===")

    models = [
        "Dense",
        "Sparse_Oracle",
        "J0_Uniform_Baseline",
        "J1_Two_Tier",
        "J2_Two_Tier_Decay",
        "J3_Three_Tier",
        "J4_Queue_Multi_Rate",
        "J5_Oracle_Rate"
    ]
    sparse_models = [m for m in models if m not in ["Dense", "Sparse_Oracle"]]

    seed_summaries = []
    all_tier_events = []
    all_candidate_latencies = []
    all_probe_allocations = []
    all_interprobe_gaps = []
    events_seed42 = []
    rep_trajectories = {m: {} for m in models}

    r2_true_indices = sorted(config["regime_2"]["indices"])
    shift_step = config["shift_step"]

    start_time = time.time()

    for seed in seeds:
        print(f"\n--- Running Seed {seed} ---")
        rng = np.random.RandomState(seed)
        init_supp = list(rng.choice(config["d_features"], size=config["k_true"], replace=False))

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

        mode_map = {
            "J0_Uniform_Baseline": "uniform_baseline",
            "J1_Two_Tier": "two_tier",
            "J2_Two_Tier_Decay": "two_tier_decay",
            "J3_Three_Tier": "three_tier",
            "J4_Queue_Multi_Rate": "queue_multi_rate",
            "J5_Oracle_Rate": "oracle_rate"
        }

        policies = {
            m: TieredEvidenceRatePolicy(
                d=config["d_features"],
                mode=mode_map[m],
                c_max=config["c_max"],
                n_screen=config["n_screen"],
                theta_screen=config["theta_screen"],
                gamma_screen=config["gamma_screen"],
                theta_drop=config["theta_drop"],
                gamma_drop=config["gamma_drop"],
                confirm_max_probes=config["confirm_max_probes"],
                confirm_fraction=config["confirm_fraction_f4"],
                coverage_fraction=config["coverage_fraction_f4"],
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
                warm_fraction=config["warm_fraction"],
                cold_fraction_j3=config["cold_fraction_j3"],
                warm_fraction_j3=config["warm_fraction_j3"],
                hot_fraction_j3=config["hot_fraction_j3"]
            ) for m in sparse_models
        }

        learners = {
            m: TieredEvidenceLearner(
                d=config["d_features"],
                initial_support=list(init_supp),
                probe_policy=policies[m],
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
            ) for m in sparse_models
        }

        feat_tracking = {m: {
            f: {
                "first_probe": None,
                "promotion": None,
                "evictions": [],
                "stable_retention": None
            } for f in r2_true_indices
        } for m in sparse_models}

        promotions_list = {m: [] for m in sparse_models}
        displacements_count = {m: 0 for m in sparse_models}

        histories = {m: {
            "losses": [],
            "r1_losses": [],
            "r2_losses": [],
            "full_r2_losses": [],
            "recalls": [],
            "occupancies": [],
            "flops": [],
            "q_t": [],
            "probes_used": []
        } for m in models}

        env = DynamicSparseLinearStream(config, seed=seed)

        for t in range(1, config["total_steps"] + 1):
            x, y, true_supp, true_w = env.step()

            # 1. Dense NLMS
            y_hat_dense = dense.predict(x)
            err_dense = y - y_hat_dense
            loss_dense = err_dense ** 2
            dense_res = dense.update(x, y)
            histories["Dense"]["losses"].append(loss_dense)
            histories["Dense"]["recalls"].append(1.0)
            histories["Dense"]["occupancies"].append(1.0)
            histories["Dense"]["flops"].append(dense_res["flops"])
            histories["Dense"]["q_t"].append(0)
            histories["Dense"]["probes_used"].append(0)
            if t <= shift_step:
                histories["Dense"]["r1_losses"].append(loss_dense)
            else:
                histories["Dense"]["full_r2_losses"].append(loss_dense)
            if t > 1800:
                histories["Dense"]["r2_losses"].append(loss_dense)

            # 2. Sparse Oracle Support
            x_orc = x[sorted(true_supp)]
            y_hat_orc = float(np.dot(w_oracle, x_orc))
            err_orc = y - y_hat_orc
            loss_orc = err_orc ** 2
            norm_orc = float(np.dot(x_orc, x_orc))
            w_oracle += (config["nlms_mu"] / (config["nlms_eps"] + norm_orc)) * err_orc * x_orc
            histories["Sparse_Oracle"]["losses"].append(loss_orc)
            histories["Sparse_Oracle"]["recalls"].append(1.0)
            histories["Sparse_Oracle"]["occupancies"].append(1.0)
            histories["Sparse_Oracle"]["flops"].append(32.0)
            histories["Sparse_Oracle"]["q_t"].append(0)
            histories["Sparse_Oracle"]["probes_used"].append(0)
            if t <= shift_step:
                histories["Sparse_Oracle"]["r1_losses"].append(loss_orc)
            else:
                histories["Sparse_Oracle"]["full_r2_losses"].append(loss_orc)
            if t > 1800:
                histories["Sparse_Oracle"]["r2_losses"].append(loss_orc)

            # 3. Sparse Models
            for m in sparse_models:
                learner = learners[m]
                ctrl = controllers[m]
                yh = learner.predict(x)
                err = y - yh
                loss = err ** 2
                q_t = ctrl.get_q(err, t)

                res = learner.update(x, y, q=q_t, true_support=true_supp)

                active_set = set(learner.support)
                overlap = len(active_set.intersection(true_supp))
                recall = overlap / float(len(true_supp))
                occupancy = 1.0 if overlap == len(true_supp) else 0.0

                p_feat = res["promoted"]
                v_feat = res["victim"]
                probed = res["candidates"]

                # First probe in Regime 2
                if t > shift_step:
                    for cand in probed:
                        if cand in r2_true_indices and feat_tracking[m][cand]["first_probe"] is None:
                            feat_tracking[m][cand]["first_probe"] = t

                if p_feat is not None:
                    is_p_true = 1 if (p_feat in true_supp) else 0
                    if t > shift_step and p_feat in r2_true_indices and feat_tracking[m][p_feat]["promotion"] is None:
                        feat_tracking[m][p_feat]["promotion"] = t
                    promotions_list[m].append({
                        "feature": p_feat,
                        "promotion_step": t,
                        "is_true": is_p_true
                    })

                if v_feat is not None:
                    v_is_true = 1 if (v_feat in true_supp) else 0
                    if t > shift_step and v_feat in r2_true_indices:
                        feat_tracking[m][v_feat]["evictions"].append(t)
                    if v_is_true and (p_feat is not None and p_feat not in true_supp):
                        displacements_count[m] += 1

                histories[m]["losses"].append(loss)
                histories[m]["recalls"].append(recall)
                histories[m]["occupancies"].append(occupancy)
                histories[m]["flops"].append(res["flops"])
                histories[m]["q_t"].append(q_t)
                histories[m]["probes_used"].append(res["num_probed"])

                if t <= shift_step:
                    histories[m]["r1_losses"].append(loss)
                else:
                    histories[m]["full_r2_losses"].append(loss)
                if t > 1800:
                    histories[m]["r2_losses"].append(loss)

                if seed == 42 and (p_feat is not None or v_feat is not None or t % 100 == 0):
                    events_seed42.append({
                        "step": t,
                        "model": m,
                        "loss": loss,
                        "recall": recall,
                        "occupancy": occupancy,
                        "support_size": len(learner.support),
                        "q_t": q_t,
                        "flops": res["flops"],
                        "promoted": p_feat,
                        "victim": v_feat
                    })

        # Save trajectory for representative seed
        if seed == rep_seed:
            for m in models:
                rep_trajectories[m] = {
                    "losses": np.array(histories[m]["losses"]),
                    "recalls": np.array(histories[m]["recalls"]),
                    "occupancies": np.array(histories[m]["occupancies"]),
                    "flops": np.array(histories[m]["flops"])
                }

        # Post-process Feature Latencies for Regime 2
        feat_latencies_by_model = {m: [] for m in sparse_models}
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
                        promos_after = [pr["promotion_step"] for pr in promotions_list[m] if pr["feature"] == f and pr["promotion_step"] > last_evict]
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

                record = {
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
                }
                all_candidate_latencies.append(record)
                feat_latencies_by_model[m].append(record)

        # Compute seed summary metrics
        dense_mean_flops = float(np.mean(histories["Dense"]["flops"]))

        for m in models:
            losses = np.array(histories[m]["losses"])
            recalls = np.array(histories[m]["recalls"])
            occupancies = np.array(histories[m]["occupancies"])
            flops = np.array(histories[m]["flops"])

            glob_mse = float(np.mean(losses))
            r2_losses = histories[m]["r2_losses"]
            r2_mse = float(np.mean(r2_losses)) if r2_losses else float(np.mean(losses[shift_step:]))
            mean_r2_recall = float(np.mean(recalls[shift_step:]))
            final_recall = float(recalls[-1])
            full_occupancy = float(np.mean(occupancies[shift_step:]))
            mean_flops = float(np.mean(flops))
            peak_flops = float(np.max(flops))
            compute_ratio = (mean_flops / dense_mean_flops) * 100.0
            tot_probes = int(np.sum(histories[m]["probes_used"]))

            # Candidate latency metrics
            t_first_probe = 0.0
            t_evidence = 0.0
            t_post = 0.0
            t_total = 0.0
            med_true_gap = 0.0
            p90_true_gap = 0.0
            med_noise_gap = 0.0
            true_velocity = 0.0
            true_starvations = 0
            cold_fraction = 0.0
            warm_prec = 0.0
            hot_prec = 0.0
            useful_elev_frac = 0.0
            false_elev_count = 0
            t1, t2, t3, t4, t5 = 0.0, 0.0, 0.0, 0.0, 0.0

            if m in sparse_models:
                lrn = learners[m]
                pol = policies[m]
                lat_records = feat_latencies_by_model[m]

                t_first_probe = float(np.mean([l["t_wait_probe"] for l in lat_records]))
                t_evidence = float(np.mean([l["t_evidence"] for l in lat_records]))
                t_post = float(np.mean([l["t_post_promotion"] for l in lat_records]))
                t_total = float(np.mean([l["t_total"] for l in lat_records]))

                t1_l, t2_l, t3_l, t4_l, t5_l = [], [], [], [], []
                for feat in r2_true_indices:
                    t_dict = lrn.r2_time_to_n.get(feat, {})
                    if 1 in t_dict: t1_l.append(t_dict[1])
                    if 2 in t_dict: t2_l.append(t_dict[2])
                    if 3 in t_dict: t3_l.append(t_dict[3])
                    if 4 in t_dict: t4_l.append(t_dict[4])
                    if 5 in t_dict: t5_l.append(t_dict[5])
                t1 = float(np.mean(t1_l)) if t1_l else 0.0
                t2 = float(np.mean(t2_l)) if t2_l else 0.0
                t3 = float(np.mean(t3_l)) if t3_l else 0.0
                t4 = float(np.mean(t4_l)) if t4_l else 0.0
                t5 = float(np.mean(t5_l)) if t5_l else 0.0

                # Gaps
                if lrn.true_interprobe_gaps:
                    med_true_gap = float(np.median(lrn.true_interprobe_gaps))
                    p90_true_gap = float(np.percentile(lrn.true_interprobe_gaps, 90))
                    all_interprobe_gaps.append({
                        "seed": seed, "model": m, "tier_type": "TRUE",
                        "mean": float(np.mean(lrn.true_interprobe_gaps)),
                        "median": med_true_gap,
                        "p10": float(np.percentile(lrn.true_interprobe_gaps, 10)),
                        "p50": med_true_gap,
                        "p90": p90_true_gap,
                        "max": float(np.max(lrn.true_interprobe_gaps))
                    })
                if lrn.noise_interprobe_gaps:
                    med_noise_gap = float(np.median(lrn.noise_interprobe_gaps))
                    all_interprobe_gaps.append({
                        "seed": seed, "model": m, "tier_type": "NOISE",
                        "mean": float(np.mean(lrn.noise_interprobe_gaps)),
                        "median": med_noise_gap,
                        "p10": float(np.percentile(lrn.noise_interprobe_gaps, 10)),
                        "p50": med_noise_gap,
                        "p90": float(np.percentile(lrn.noise_interprobe_gaps, 90)),
                        "max": float(np.max(lrn.noise_interprobe_gaps))
                    })

                true_starvations = lrn.true_starvation_events
                if lrn.steps_with_omitted_true > 0:
                    true_velocity = float(lrn.probes_to_omitted_true / lrn.steps_with_omitted_true)

                # Tier allocations
                tot_cand_probes = max(1, sum(pol.probes_by_tier.values()))
                cold_fraction = float(pol.probes_by_tier["COLD"] / tot_cand_probes)

                w_true = pol.tier_entry_counts["WARM_TRUE"]
                w_tot = w_true + pol.tier_entry_counts["WARM_NOISE"]
                warm_prec = float(w_true / w_tot) if w_tot > 0 else 0.0

                h_true = pol.tier_entry_counts["HOT_TRUE"]
                h_tot = h_true + pol.tier_entry_counts["HOT_NOISE"]
                hot_prec = float(h_true / h_tot) if h_tot > 0 else 0.0

                elev_tot = pol.useful_elevated_probes + pol.false_elevated_probes
                useful_elev_frac = float(pol.useful_elevated_probes / elev_tot) if elev_tot > 0 else 0.0
                false_elev_count = int(pol.false_elevated_probes)

                all_probe_allocations.append({
                    "seed": seed,
                    "model": m,
                    "probes_cold": pol.probes_by_tier["COLD"],
                    "probes_warm": pol.probes_by_tier["WARM"],
                    "probes_hot": pol.probes_by_tier["HOT"],
                    "probes_confirm": pol.probes_by_tier["CONFIRM"],
                    "useful_elevated": pol.useful_elevated_probes,
                    "false_elevated": pol.false_elevated_probes
                })

                for ev in pol.tier_events_log:
                    all_tier_events.append({"seed": seed, "model": m, **ev})

            seed_summaries.append({
                "seed": seed,
                "model": m,
                "global_mse": glob_mse,
                "regime_2_mse": r2_mse,
                "final_recall": final_recall,
                "mean_r2_recall": mean_r2_recall,
                "full_support_occupancy": full_occupancy,
                "t_first_probe": t_first_probe,
                "t_evidence": t_evidence,
                "t_post": t_post,
                "t_total": t_total,
                "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5,
                "med_true_gap": med_true_gap,
                "p90_true_gap": p90_true_gap,
                "med_noise_gap": med_noise_gap,
                "true_velocity": true_velocity,
                "true_starvations": true_starvations,
                "cold_fraction": cold_fraction,
                "warm_prec": warm_prec,
                "hot_prec": hot_prec,
                "useful_elev_frac": useful_elev_frac,
                "false_elev_count": false_elev_count,
                "mean_flops": mean_flops,
                "peak_flops": peak_flops,
                "compute_ratio": compute_ratio,
                "total_probes": tot_probes
            })

    # Convert to DataFrames
    df_seed_summaries = pd.DataFrame(seed_summaries)
    df_seed_summaries.to_csv(os.path.join(exp_dir, "seed_summaries.csv"), index=False)

    if all_candidate_latencies:
        pd.DataFrame(all_candidate_latencies).to_csv(os.path.join(exp_dir, "candidate_latency.csv"), index=False)
    if all_interprobe_gaps:
        pd.DataFrame(all_interprobe_gaps).to_csv(os.path.join(exp_dir, "interprobe_gaps.csv"), index=False)
    if all_tier_events:
        pd.DataFrame(all_tier_events).to_csv(os.path.join(exp_dir, "tier_events.csv"), index=False)
    if all_probe_allocations:
        pd.DataFrame(all_probe_allocations).to_csv(os.path.join(exp_dir, "probe_allocation.csv"), index=False)
    if events_seed42:
        pd.DataFrame(events_seed42).to_csv(os.path.join(exp_dir, "events_seed42.csv"), index=False)

    # Compute Aggregate Results Table across seeds
    summary_cols = [
        "global_mse", "regime_2_mse", "final_recall", "mean_r2_recall",
        "full_support_occupancy", "t_first_probe", "t_evidence", "t_post", "t_total",
        "t1", "t2", "t3", "t4", "t5",
        "med_true_gap", "p90_true_gap", "med_noise_gap", "true_velocity",
        "true_starvations", "cold_fraction", "warm_prec", "hot_prec",
        "useful_elev_frac", "false_elev_count", "mean_flops", "peak_flops",
        "compute_ratio", "total_probes"
    ]

    agg_df = df_seed_summaries.groupby("model")[summary_cols].mean().loc[models].reset_index()
    agg_df.to_csv(os.path.join(exp_dir, "results.csv"), index=False)

    print("\n=== EXP-0006 Aggregated Results across Seeds ===")
    print(agg_df[[
        "model", "global_mse", "regime_2_mse", "mean_r2_recall",
        "full_support_occupancy", "t_first_probe", "t_evidence", "t_post",
        "med_true_gap", "true_starvations", "mean_flops", "compute_ratio", "total_probes"
    ]].to_string(index=False))

    # Plot 12-Panel Figures
    print("\nGenerating 12-panel figure artifact...")
    fig, axes = plt.subplots(4, 3, figsize=(20, 22))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)

    # 1. Regime-2 MSE vs Time
    ax = axes[0, 0]
    for m in models:
        if m in rep_trajectories:
            l = rep_trajectories[m]["losses"][shift_step:]
            # 50-step smoothing
            w = 50
            if len(l) >= w:
                smoothed = np.convolve(l, np.ones(w)/w, mode="valid")
                ax.plot(np.arange(shift_step + w, shift_step + w + len(smoothed)), smoothed, label=m)
    ax.set_title("1. Regime-2 MSE vs Time (Smoothed)")
    ax.set_yscale("log")
    ax.set_xlabel("Step")
    ax.set_ylabel("MSE")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 2. Support Recall vs Time
    ax = axes[0, 1]
    for m in models:
        if m in rep_trajectories:
            r = rep_trajectories[m]["recalls"][shift_step:]
            ax.plot(np.arange(shift_step, shift_step + len(r)), r, label=m)
    ax.set_title("2. Support Recall vs Time (Regime 2)")
    ax.set_xlabel("Step")
    ax.set_ylabel("Recall")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 3. Full-Support Occupancy Timeline
    ax = axes[0, 2]
    for m in sparse_models:
        if m in rep_trajectories:
            occ = rep_trajectories[m]["occupancies"][shift_step:]
            cum_occ = np.cumsum(occ) / (np.arange(len(occ)) + 1)
            ax.plot(np.arange(shift_step, shift_step + len(occ)), cum_occ, label=m)
    ax.set_title("3. Cumulative Full-Support Occupancy")
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative Occupancy")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 4. True-Candidate Inter-Probe Gap Distribution
    ax = axes[1, 0]
    bar_models = [m for m in sparse_models]
    med_gaps = [agg_df.loc[agg_df["model"] == m, "med_true_gap"].values[0] for m in bar_models]
    p90_gaps = [agg_df.loc[agg_df["model"] == m, "p90_true_gap"].values[0] for m in bar_models]
    x_pos = np.arange(len(bar_models))
    ax.bar(x_pos - 0.15, med_gaps, width=0.3, label="Median Gap")
    ax.bar(x_pos + 0.15, p90_gaps, width=0.3, label="P90 Gap")
    ax.axhline(20, color="green", linestyle="--", label="GO Target (<=20)")
    ax.axhline(10, color="gold", linestyle=":", label="Strong GO (<=10)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("4. True Candidate Inter-Probe Gap (steps)")
    ax.set_ylabel("Steps between probes")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 5. Noise-Candidate Inter-Probe Gap Distribution
    ax = axes[1, 1]
    noise_gaps = [agg_df.loc[agg_df["model"] == m, "med_noise_gap"].values[0] for m in bar_models]
    ax.bar(x_pos, noise_gaps, width=0.4, color="gray", label="Median Noise Gap")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("5. Noise Candidate Inter-Probe Gap (steps)")
    ax.set_ylabel("Steps between probes")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 6. T_evidence Distribution
    ax = axes[1, 2]
    ev_vals = [agg_df.loc[agg_df["model"] == m, "t_evidence"].values[0] for m in bar_models]
    ax.bar(x_pos, ev_vals, width=0.4, color="crimson", label="Mean T_evidence")
    ax.axhline(70, color="green", linestyle="--", label="GO Target (<=70)")
    ax.axhline(50, color="gold", linestyle=":", label="Strong GO (<=50)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("6. Evidence Accumulation Latency (T_evidence)")
    ax.set_ylabel("Steps from 1st probe to promo")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 7. Cumulative Probes by Tier (Seed 42 / Rep)
    ax = axes[2, 0]
    if all_probe_allocations:
        df_pa = pd.DataFrame(all_probe_allocations)
        m_grouped = df_pa.groupby("model")[["probes_cold", "probes_warm", "probes_hot", "probes_confirm"]].mean().loc[bar_models]
        m_grouped.plot(kind="bar", stacked=True, ax=ax, colormap="tab10")
        ax.set_title("7. Mean Candidate Probes by Tier")
        ax.set_ylabel("Probes")
        ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    # 8. True vs Noise Tier Precision
    ax = axes[2, 1]
    warm_p = [agg_df.loc[agg_df["model"] == m, "warm_prec"].values[0] * 100 for m in bar_models]
    hot_p = [agg_df.loc[agg_df["model"] == m, "hot_prec"].values[0] * 100 for m in bar_models]
    ax.bar(x_pos - 0.15, warm_p, width=0.3, label="Warm Precision (%)", color="orange")
    ax.bar(x_pos + 0.15, hot_p, width=0.3, label="Hot Precision (%)", color="red")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("8. Tier Entry Precision (% True)")
    ax.set_ylabel("Precision (%)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 9. Wall-Clock Steps to N Evidence Observations (T1 - T5)
    ax = axes[2, 2]
    n_obs = [1, 2, 3, 4, 5]
    for m in bar_models:
        row = agg_df.loc[agg_df["model"] == m]
        t_vals = [row[f"t{i}"].values[0] for i in n_obs]
        ax.plot(n_obs, t_vals, marker="o", label=m)
    ax.axhline(135, color="black", linestyle=":", label="EXP-0005 T3 Baseline (~135)")
    ax.set_title("9. Time to N Evidence Samples (T1 - T5)")
    ax.set_xlabel("Number of Samples N")
    ax.set_ylabel("Steps from shift")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 10. Useful vs False Elevated Probes
    ax = axes[3, 0]
    useful_p = [agg_df.loc[agg_df["model"] == m, "useful_elev_frac"].values[0] * 100 for m in bar_models]
    ax.bar(x_pos, useful_p, width=0.4, color="darkgreen", label="Useful Elevated %")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("10. Useful Elevated Probe Fraction (%)")
    ax.set_ylabel("% probes to omitted true")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 11. True Evidence Velocity vs R2 MSE
    ax = axes[3, 1]
    vels = [agg_df.loc[agg_df["model"] == m, "true_velocity"].values[0] for m in bar_models]
    mses = [agg_df.loc[agg_df["model"] == m, "regime_2_mse"].values[0] for m in bar_models]
    ax.scatter(vels, mses, s=80, color="purple")
    for i, m in enumerate(bar_models):
        ax.annotate(m.replace("_", " "), (vels[i], mses[i]), fontsize=8, xytext=(5, 5), textcoords="offset points")
    ax.set_title("11. True Evidence Velocity vs Regime-2 MSE")
    ax.set_xlabel("True Evidence Velocity (probes/step)")
    ax.set_ylabel("Regime-2 MSE")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)

    # 12. Compute (FLOPs/step) vs Dense Limit
    ax = axes[3, 2]
    flops_vals = [agg_df.loc[agg_df["model"] == m, "mean_flops"].values[0] for m in bar_models]
    ax.bar(x_pos, flops_vals, width=0.4, color="royalblue", label="Mean FLOPs/step")
    ax.axhline(602.0 * 0.25, color="red", linestyle="--", label="25% Dense Cap (150.5)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_models, rotation=30, ha="right", fontsize=8)
    ax.set_title("12. Compute Cost per Step vs Dense Cap")
    ax.set_ylabel("FLOPs / Step")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved figure panel to: {fig_path}")

    # Copy to IDE artifacts directory
    brain_dir = os.path.join(os.path.expanduser("~"), "lebre_artifacts")
    if os.path.exists(brain_dir):
        artifact_fig = os.path.join(brain_dir, "figures_exp_0006.png")
        try:
            with open(fig_path, "rb") as fsrc, open(artifact_fig, "wb") as fdst:
                fdst.write(fsrc.read())
            print(f"Copied figure to IDE artifacts: {artifact_fig}")
        except Exception as e:
            print(f"Warning: could not copy artifact figure: {e}")

    elapsed = time.time() - start_time
    print(f"\nExperiment execution complete in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    run_experiment()
