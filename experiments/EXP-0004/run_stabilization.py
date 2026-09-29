import json
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.dense_nlms import DenseNLMS
from src.learners.stabilized_learner import StabilizedSparseLearner
from src.policies.explore_confirm_policy import ExploreConfirmPolicy
from src.controllers.probe_controllers import ProbeBankController
from src.utils.accounting import ResourceTracker

def run_experiment(dev_mode=False, dev_seed=9999):
    exp_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(exp_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    seeds = [dev_seed] if dev_mode else config["seeds"]
    models = [
        "Dense",
        "Sparse_Oracle",
        "G0_F4_Baseline",
        "G1_Age_Normalized",
        "G2_Update_Normalized",
        "G3_Contribution_Aware",
        "G4_Promotion_Cooldown",
        "G5_Oracle_Victim"
    ]
    sparse_models = [
        "G0_F4_Baseline",
        "G1_Age_Normalized",
        "G2_Update_Normalized",
        "G3_Contribution_Aware",
        "G4_Promotion_Cooldown",
        "G5_Oracle_Victim"
    ]
    target_probes = config["target_total_probes"]
    shift_step = config["shift_step"]
    r2_true_indices = config["regime_2"]["indices"]
    tau_mature = config["tau_mature"]
    
    print(f"=== Running EXP-0004: Post-Promotion Stabilization Without Blind Protection (Seeds: {seeds}) ===")
    t_start = time.time()
    
    seed_summaries = []
    feature_latency_records = []
    all_victim_events = []
    feature_maturation_records = []
    events_seed42 = []
    
    # Store trajectories for representative seed 42 figures
    rep_seed = 42 if not dev_mode else dev_seed
    rep_trajectories = {m: {} for m in models}

    for seed in seeds:
        print(f"\n--- Running Seed {seed} ---")
        rng_init = np.random.RandomState(seed)
        init_supp = list(rng_init.choice(config["d_features"], size=config["k_true"], replace=False))
        
        # Dense & Sparse Oracle references
        dense = DenseNLMS(d=config["d_features"], mu=config["nlms_mu"], eps=config["nlms_eps"])
        w_oracle = np.zeros(config["k_true"], dtype=np.float64)
        
        # Instantiate stabilized learners
        learners = {
            "G0_F4_Baseline": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="baseline", cooldown_steps=0
            ),
            "G1_Age_Normalized": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="age_normalized", tau_mature=tau_mature, cooldown_steps=0
            ),
            "G2_Update_Normalized": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="update_normalized", tau_mature=tau_mature, cooldown_steps=0
            ),
            "G3_Contribution_Aware": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="contribution_aware", contrib_beta=config["contrib_beta"], cooldown_steps=0
            ),
            "G4_Promotion_Cooldown": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="baseline", cooldown_steps=config["cooldown_steps"]
            ),
            "G5_Oracle_Victim": StabilizedSparseLearner(
                d=config["d_features"], initial_support=init_supp,
                probe_policy=ExploreConfirmPolicy(
                    d=config["d_features"], c_max=config["c_max"], n_screen=config["n_screen"],
                    theta_screen=config["theta_screen"], gamma_screen=config["gamma_screen"],
                    theta_drop=config["theta_drop"], gamma_drop=config["gamma_drop"],
                    confirm_max_probes=config["confirm_max_probes"],
                    confirm_fraction=config["confirm_fraction_f4"],
                    coverage_fraction=config["coverage_fraction_f4"]
                ),
                q=config["q_base"], mu=config["nlms_mu"], eps=config["nlms_eps"],
                n_min=config["n_min"], theta_promote=config["theta_promote"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"],
                victim_strategy="oracle_victim", cooldown_steps=0
            ),
        }
        
        controllers = {
            m: ProbeBankController(
                q_min=config["q_min"], q_base=config["q_base"], q_max=config["q_max"],
                tau_low=config["tau_low"], tau_high=config["tau_high"], alpha=config["ema_alpha"],
                total_steps=config["total_steps"], target_budget=target_probes
            ) for m in sparse_models
        }
        
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
            "premature_true_evictions": 0,
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
                
            # 3. Sparse Models G0 to G5
            for m in sparse_models:
                learner = learners[m]
                ctrl = controllers[m]
                
                y_hat = learner.predict(x)
                err = y - y_hat
                loss = err ** 2
                
                q_t = ctrl.get_q(err, t)
                active_set_pre = set(learner.support)
                
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
                
                # Promotion and eviction handling
                p_feat = stats["promoted_feat"]
                v_feat = stats["victim_feat"]
                v_age = stats["victim_age"]
                
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
                        
                    if v_is_true and v_age < tau_mature:
                        histories[m]["premature_true_evictions"] += 1
                    if v_is_true and (p_feat is not None and p_feat not in true_supp):
                        histories[m]["displacements"] += 1
                        
                    # Close lifetime of evicted feature
                    for pr in reversed(histories[m]["promotions_list"]):
                        if pr["feature"] == v_feat and pr["eviction_step"] is None:
                            pr["eviction_step"] = t
                            pr["lifetime"] = t - pr["promotion_step"]
                            pr["survived_50"] = 1 if pr["lifetime"] >= 50 else 0
                            pr["survived_100"] = 1 if pr["lifetime"] >= 100 else 0
                            break

                # Detailed Event Trace for Seed 42 on Support Edits (Section 68)
                if seed == rep_seed and (p_feat is not None or v_feat is not None):
                    events_seed42.append({
                        "step": t,
                        "model": m,
                        "promoted_candidate": p_feat,
                        "promoted_truth_status": 1 if (p_feat is not None and p_feat in true_supp) else 0,
                        "candidate_evidence_n": stats["cand_evidence_count"],
                        "candidate_score": stats["cand_score"],
                        "active_set": list(learner.support),
                        "victim": v_feat,
                        "victim_truth_status": 1 if (v_feat is not None and v_feat in true_supp) else 0,
                        "victim_age": v_age,
                        "victim_update_count": stats["victim_updates"],
                        "victim_abs_w": stats["victim_weight"],
                        "victim_contribution": stats["victim_contrib"],
                        "victim_score": stats["victim_score"],
                        "promotion_cooldown_state": stats["in_cooldown"],
                        "support_recall": recall,
                        "mse": loss
                    })

                histories[m]["losses"].append(loss)
                histories[m]["recalls"].append(recall)
                histories[m]["omitted_energy"].append(e_omit)
                histories[m]["q_history"].append(q_t)
                histories[m]["flops_history"].append(stats["flops"])
                
                if t <= shift_step:
                    histories[m]["r1_losses"].append(loss)
                else:
                    histories[m]["full_r2_losses"].append(loss)
                    histories[m]["r2_recalls"].append(recall)
                    histories[m]["full_supp_flags"].append(is_full)
                if t > 1800:
                    histories[m]["r2_losses"].append(loss)

        # Post-simulation processing for this seed
        for m in sparse_models:
            # Close open promotion records at step 2000
            for pr in histories[m]["promotions_list"]:
                if pr["eviction_step"] is None:
                    pr["lifetime"] = 2001 - pr["promotion_step"]
                    pr["survived_50"] = 1 if pr["lifetime"] >= 50 else 0
                    pr["survived_100"] = 1 if pr["lifetime"] >= 100 else 0

            # Collect victim audit events from learner
            for ve in learners[m].victim_events_log:
                all_victim_events.append({"seed": seed, "model": m, **ve})

            # Feature maturation records for true features (Section 69)
            mat_dict = learners[m].feature_maturation
            for feat in r2_true_indices:
                feat_u = mat_dict.get(feat, {})
                feature_maturation_records.append({
                    "seed": seed,
                    "model": m,
                    "feature": feat,
                    "w_at_1": feat_u.get(1, None),
                    "w_at_5": feat_u.get(5, None),
                    "w_at_10": feat_u.get(10, None),
                    "w_at_20": feat_u.get(20, None),
                    "w_at_50": feat_u.get(50, None),
                    "w_at_100": feat_u.get(100, None)
                })

            # Compute Latency Decomposition for Regime 2 true features
            final_supp = set(learners[m].support)
            for f in r2_true_indices:
                if f in final_supp:
                    p_step = feat_tracking[m][f]["promotion"]
                    evicts = [ev for ev in feat_tracking[m][f]["evictions"] if ev > p_step] if p_step else []
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

                t_wait = max(0, fp - 1001)
                t_evid = max(0, pr - fp)
                t_post = max(0, sr - pr)
                t_tot = max(0, sr - 1001)

                feature_latency_records.append({
                    "seed": seed,
                    "model": m,
                    "feature": f,
                    "first_relevant_step": 1001,
                    "first_probe": fp,
                    "promotion": pr,
                    "first_stable_retention": sr,
                    "t_wait_probe": t_wait,
                    "t_evidence": t_evid,
                    "t_post_promotion": t_post,
                    "t_total": t_tot
                })

        # Save representative trajectories for seed 42
        if seed == rep_seed:
            for m in models:
                rep_trajectories[m] = {
                    "losses": histories[m]["losses"],
                    "recalls": histories[m]["recalls"],
                    "q_history": histories[m]["q_history"],
                    "omitted_energy": histories[m]["omitted_energy"],
                    "full_supp_flags": histories[m]["full_supp_flags"],
                    "promotions_list": histories[m]["promotions_list"]
                }

        # Budget Gate Check
        for m in sparse_models:
            tot_probes = sum(histories[m]["q_history"])
            if tot_probes != target_probes:
                raise ValueError(f"BUDGET GATE VIOLATED: {m} used {tot_probes} probes (target: {target_probes}) on seed {seed}!")

        # Summary Metrics per model for this seed
        for m in models:
            fl_recs = [r for r in feature_latency_records if r["seed"] == seed and r["model"] == m]
            mean_t_wait = float(np.mean([r["t_wait_probe"] for r in fl_recs])) if fl_recs else 0.0
            mean_t_evid = float(np.mean([r["t_evidence"] for r in fl_recs])) if fl_recs else 0.0
            mean_t_post = float(np.mean([r["t_post_promotion"] for r in fl_recs])) if fl_recs else 0.0
            stable_lat = float(np.max([r["first_stable_retention"] for r in fl_recs])) - 1001 if fl_recs else 0.0

            # Survival metrics
            p_list = histories[m]["promotions_list"]
            true_promos = [p for p in p_list if p["is_true"] == 1]
            noise_promos = [p for p in p_list if p["is_true"] == 0]
            true_surv_50 = float(np.mean([p["survived_50"] for p in true_promos])) if true_promos else 1.0
            true_surv_100 = float(np.mean([p["survived_100"] for p in true_promos])) if true_promos else 1.0
            noise_surv_50 = float(np.mean([p["survived_50"] for p in noise_promos])) if noise_promos else 0.0

            tot_promos = len(p_list)
            promo_rate_100 = tot_promos / (config["total_steps"] / 100.0)
            
            # Support edits = promotions + swaps
            support_edits = tot_promos + (learners[m].total_swaps if m in sparse_models else 0)
            edits_rate_100 = support_edits / (config["total_steps"] / 100.0)

            mean_flops = float(np.mean(histories[m]["flops_history"]))
            peak_flops = int(np.max(histories[m]["flops_history"]))
            mem_b = ResourceTracker.estimate_memory_bytes(
                5 if m == "Sparse_Oracle" else (100 if m == "Dense" else 10),
                config["d_features"],
                config["d_features"],
                is_welford=(m in sparse_models),
                is_extended=(m in sparse_models)
            )

            seed_summaries.append({
                "seed": seed,
                "model": m,
                "global_mse": float(np.mean(histories[m]["losses"])),
                "regime_1_mse": float(np.mean(histories[m]["r1_losses"])) if histories[m]["r1_losses"] else 0.0,
                "regime_2_mse": float(np.mean(histories[m]["r2_losses"])) if histories[m]["r2_losses"] else 0.0,
                "final_recall": float(histories[m]["recalls"][-1]),
                "mean_r2_recall": float(np.mean(histories[m]["r2_recalls"])) if histories[m]["r2_recalls"] else 1.0,
                "full_support_occupancy": float(np.mean(histories[m]["full_supp_flags"])) if histories[m]["full_supp_flags"] else 1.0,
                "stable_acquisition_latency": stable_lat,
                "t_wait_probe": mean_t_wait,
                "t_evidence": mean_t_evid,
                "t_post_promotion": mean_t_post,
                "true_survival_50": true_surv_50,
                "true_survival_100": true_surv_100,
                "noise_survival_50": noise_surv_50,
                "premature_true_evictions": histories[m]["premature_true_evictions"],
                "noise_to_true_displacements": histories[m]["displacements"],
                "redundant_true_repromotions": histories[m]["redundant_repromotions"],
                "promotions_per_100_steps": promo_rate_100,
                "support_changes_per_100_steps": edits_rate_100,
                "total_probes": sum(histories[m]["q_history"]),
                "mean_flops": mean_flops,
                "peak_flops": peak_flops,
                "compute_ratio_dense": mean_flops / 602.0,
                "memory_bytes": mem_b
            })

    print(f"\nAll runs completed in {time.time() - t_start:.2f} seconds.")

    # Save CSV Artifacts
    df_feat_lat = pd.DataFrame(feature_latency_records)
    df_feat_lat.to_csv(os.path.join(exp_dir, "latency_decomposition.csv"), index=False)

    df_victims = pd.DataFrame(all_victim_events)
    df_victims.to_csv(os.path.join(exp_dir, "victim_events.csv"), index=False)

    df_mat = pd.DataFrame(feature_maturation_records)
    df_mat.to_csv(os.path.join(exp_dir, "feature_maturation.csv"), index=False)

    if events_seed42:
        df_seed42 = pd.DataFrame(events_seed42)
        df_seed42.to_csv(os.path.join(exp_dir, "events_seed42.csv"), index=False)

    # Summary Aggregation across seeds
    df_summary = pd.DataFrame(seed_summaries)
    agg_cols = [
        "global_mse", "regime_1_mse", "regime_2_mse", "final_recall", "mean_r2_recall",
        "full_support_occupancy", "stable_acquisition_latency", "t_wait_probe",
        "t_evidence", "t_post_promotion", "true_survival_50", "true_survival_100",
        "noise_survival_50", "premature_true_evictions", "noise_to_true_displacements",
        "redundant_true_repromotions", "promotions_per_100_steps",
        "support_changes_per_100_steps", "total_probes", "mean_flops",
        "peak_flops", "compute_ratio_dense", "memory_bytes"
    ]
    grouped = df_summary.groupby("model")[agg_cols].mean().reset_index()
    grouped["model_order"] = grouped["model"].apply(lambda m: models.index(m) if m in models else 99)
    grouped = grouped.sort_values("model_order").drop(columns=["model_order"])
    grouped.to_csv(os.path.join(exp_dir, "results.csv"), index=False)
    df_summary.to_csv(os.path.join(exp_dir, "seed_summaries.csv"), index=False)

    print("\n=== EXP-0004 AGGREGATE RESULTS SUMMARY ===")
    display_cols = [
        "model", "regime_2_mse", "mean_r2_recall", "full_support_occupancy",
        "t_post_promotion", "true_survival_50", "noise_to_true_displacements",
        "mean_flops", "compute_ratio_dense"
    ]
    print(grouped[display_cols].to_string(index=False))

    # Generate 10-Panel Figures
    generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, df_victims, df_mat, models, rep_seed, tau_mature=tau_mature)

    return grouped, df_summary

def generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, df_victims, df_mat, models, rep_seed, tau_mature=50):
    print("\nGenerating 10-panel figure artifact...")
    fig = plt.figure(figsize=(24, 20))
    
    colors = {
        "Dense": "black",
        "Sparse_Oracle": "green",
        "G0_F4_Baseline": "gray",
        "G1_Age_Normalized": "blue",
        "G2_Update_Normalized": "purple",
        "G3_Contribution_Aware": "orange",
        "G4_Promotion_Cooldown": "brown",
        "G5_Oracle_Victim": "teal"
    }

    def rolling_mean(arr, window=20):
        return pd.Series(arr).rolling(window, min_periods=1).mean().values

    # 1. Regime-2 MSE vs time
    ax1 = fig.add_subplot(4, 3, 1)
    for m in models:
        losses = rep_trajectories[m].get("losses", [])
        if losses:
            ax1.plot(range(1000, 2000), rolling_mean(losses[1000:], 30), label=m, color=colors.get(m, "blue"), alpha=0.85, lw=1.8)
    ax1.set_title("1. Regime-2 MSE vs Time (Seed 42)")
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
    ax2.set_title("2. Support Recall vs Time (Regime 2)")
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
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=8, loc="lower right")

    # 4. True feature survival curves
    ax4 = fig.add_subplot(4, 3, 4)
    sparse_models = [m for m in models if m not in ["Dense", "Sparse_Oracle"]]
    x = np.arange(len(sparse_models))
    s50 = [df_summary[df_summary["model"] == m]["true_survival_50"].mean() for m in sparse_models]
    s100 = [df_summary[df_summary["model"] == m]["true_survival_100"].mean() for m in sparse_models]
    ax4.bar(x - 0.15, s50, width=0.3, label="Survival @ 50 steps", color="forestgreen", alpha=0.85)
    ax4.bar(x + 0.15, s100, width=0.3, label="Survival @ 100 steps", color="darkgreen", alpha=0.85)
    ax4.set_xticks(x)
    ax4.set_xticklabels(sparse_models, rotation=30)
    ax4.set_title("4. True Feature Survival Rates")
    ax4.set_ylabel("Survival Rate")
    ax4.set_ylim(0, 1.1)
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    # 5. Noise feature survival curves
    ax5 = fig.add_subplot(4, 3, 5)
    ns50 = [df_summary[df_summary["model"] == m]["noise_survival_50"].mean() for m in sparse_models]
    ax5.bar(sparse_models, ns50, color="crimson", alpha=0.85)
    ax5.set_title("5. Noise Feature Survival @ 50 Steps")
    ax5.set_ylabel("Survival Rate (Lower is Better)")
    ax5.tick_params(axis='x', rotation=30)
    ax5.grid(True, alpha=0.3)

    # 6. T_post_promotion distribution
    ax6 = fig.add_subplot(4, 3, 6)
    t_post_data = []
    labels = []
    for m in sparse_models:
        vals = df_feat_lat[df_feat_lat["model"] == m]["t_post_promotion"].values
        t_post_data.append(vals)
        labels.append(m)
    ax6.boxplot(t_post_data, tick_labels=labels)
    ax6.axhline(80, color="red", linestyle="--", label="GO Target (<= 80 steps)")
    ax6.axhline(50, color="green", linestyle="--", label="STRONG_GO (<= 50 steps)")
    ax6.set_title("6. T_post_promotion Distribution")
    ax6.set_ylabel("Steps (Promotion -> Stable Retention)")
    ax6.tick_params(axis='x', rotation=30)
    ax6.grid(True, alpha=0.3)
    ax6.legend(fontsize=8)

    # 7. Victim Score by Truth/Age Class
    ax7 = fig.add_subplot(4, 3, 7)
    if not df_victims.empty:
        df_v = df_victims[df_victims["model"] == "G1_Age_Normalized"]
        if not df_v.empty:
            young_true = df_v[(df_v["victim_is_true"] == 1) & (df_v["victim_age"] < tau_mature)]["victim_score"].values
            young_noise = df_v[(df_v["victim_is_true"] == 0) & (df_v["victim_age"] < tau_mature)]["victim_score"].values
            mature_true = df_v[(df_v["victim_is_true"] == 1) & (df_v["victim_age"] >= tau_mature)]["victim_score"].values
            mature_noise = df_v[(df_v["victim_is_true"] == 0) & (df_v["victim_age"] >= tau_mature)]["victim_score"].values
            
            data_to_plot = [young_true, young_noise, mature_true, mature_noise]
            plot_labels = ["Young True", "Young Noise", "Mature True", "Mature Noise"]
            # Filter empty lists
            valid_plot = [(d, l) for d, l in zip(data_to_plot, plot_labels) if len(d) > 0]
            if valid_plot:
                d_list, l_list = zip(*valid_plot)
                ax7.boxplot(d_list, tick_labels=l_list)
        ax7.set_title("7. Victim Scores by Class (G1 Age-Norm)")
        ax7.set_ylabel("Adjusted Victim Score")
        ax7.tick_params(axis='x', rotation=30)
        ax7.grid(True, alpha=0.3)
    else:
        ax7.text(0.5, 0.5, "No Evictions", ha='center', va='center')
        ax7.set_title("7. Victim Scores by Class")

    # 8. Promotion Events Over Time (Seed 42)
    ax8 = fig.add_subplot(4, 3, 8)
    for m in ["G0_F4_Baseline", "G1_Age_Normalized", "G4_Promotion_Cooldown"]:
        plist = rep_trajectories[m].get("promotions_list", [])
        if plist:
            p_steps = [p["promotion_step"] for p in plist if p["promotion_step"] > 1000]
            ax8.hist(p_steps, bins=20, alpha=0.5, label=m, color=colors.get(m, "blue"))
    ax8.set_title("8. Promotion Frequency in Regime 2")
    ax8.set_xlabel("Simulation Step")
    ax8.set_ylabel("Promotions per Bin")
    ax8.grid(True, alpha=0.3)
    ax8.legend(fontsize=8)

    # 9. False->True Displacement Events Over Time
    ax9 = fig.add_subplot(4, 3, 9)
    displace_counts = [df_summary[df_summary["model"] == m]["noise_to_true_displacements"].mean() for m in sparse_models]
    ax9.bar(sparse_models, displace_counts, color="salmon", alpha=0.85)
    ax9.set_title("9. False->True Displacements (Premature Evictions)")
    ax9.set_ylabel("Total Displacement Count")
    ax9.tick_params(axis='x', rotation=30)
    ax9.grid(True, alpha=0.3)

    # 10. Weight Maturation Curves
    ax10 = fig.add_subplot(4, 3, 10)
    if not df_mat.empty:
        checkpoints = [1, 5, 10, 20, 50, 100]
        for m in ["G0_F4_Baseline", "G1_Age_Normalized", "G4_Promotion_Cooldown"]:
            sub_m = df_mat[df_mat["model"] == m]
            if not sub_m.empty:
                means = [sub_m[f"w_at_{u}"].dropna().mean() for u in checkpoints]
                ax10.plot(checkpoints, means, marker='o', label=m, color=colors.get(m, "blue"), lw=1.8)
        ax10.set_title("10. Weight Maturation Curve for True Features")
        ax10.set_xlabel("Updates Received (u_i)")
        ax10.set_ylabel("Mean |w_i|")
        ax10.grid(True, alpha=0.3)
        ax10.legend(fontsize=8)
    else:
        ax10.text(0.5, 0.5, "No Maturation Data", ha='center', va='center')
        ax10.set_title("10. Weight Maturation Curve")

    # 11. Mean FLOPs / Step vs 25% Dense Cap
    ax11 = fig.add_subplot(4, 3, 11)
    all_models = ["Dense", "Sparse_Oracle"] + sparse_models
    flops_list = [df_summary[df_summary["model"] == m]["mean_flops"].mean() for m in all_models]
    bar_cols = [colors.get(m, "blue") for m in all_models]
    ax11.bar(all_models, flops_list, color=bar_cols, alpha=0.85)
    ax11.axhline(150.5, color="crimson", linestyle="--", lw=2, label="25% Dense Cap (150.5 FLOPs)")
    ax11.set_title("11. Mean FLOPs / Step vs 25% Compute Cap")
    ax11.set_ylabel("FLOPs / Step")
    ax11.tick_params(axis='x', rotation=30)
    ax11.grid(True, alpha=0.3)
    ax11.legend(fontsize=8)

    # 12. Full Support Occupancy Summary
    ax12 = fig.add_subplot(4, 3, 12)
    occs = [df_summary[df_summary["model"] == m]["full_support_occupancy"].mean() for m in sparse_models]
    ax12.bar(sparse_models, occs, color=[colors.get(m, "blue") for m in sparse_models], alpha=0.85)
    ax12.axhline(0.70, color="red", linestyle="--", label="GO Target (>= 70%)")
    ax12.axhline(0.80, color="green", linestyle="--", label="STRONG_GO (>= 80%)")
    ax12.set_title("12. Full-Support Occupancy Comparison")
    ax12.set_ylabel("Occupancy Fraction")
    ax12.set_ylim(0, 1.05)
    ax12.tick_params(axis='x', rotation=30)
    ax12.grid(True, alpha=0.3)
    ax12.legend(fontsize=8)

    plt.tight_layout()
    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=200)
    plt.close()
    print(f"Saved 10-panel figures artifact to: {fig_path}")

if __name__ == "__main__":
    dev_flag = "--dev" in sys.argv
    run_experiment(dev_mode=dev_flag)
