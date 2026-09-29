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
from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.policies.priority_policy import PriorityProbePolicy, OracleTargetingPolicy
from src.policies.explore_confirm_policy import PersistenceProbePolicy, ExploreConfirmPolicy
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
        "F0_Baseline",
        "F1_Priority",
        "F2_Persistence",
        "F3_ExploreConfirm",
        "F4_EC_Coverage",
        "F5_Oracle_Targeting"
    ]
    target_probes = config["target_total_probes"]
    shift_step = config["shift_step"]
    r2_true_indices = config["regime_2"]["indices"]
    
    print(f"=== Running EXP-0003: Cheap Noise-Resistant Explore/Confirm Candidate Screening (Seeds: {seeds}) ===")
    t_start = time.time()
    
    seed_summaries = []
    feature_latency_records = []
    probe_alloc_records = []
    confirm_event_records = []
    candidate_metrics_records = []
    events_seed42 = []
    
    # Store trajectories for representative seed 42 figures
    rep_seed = 42 if not dev_mode else dev_seed
    rep_trajectories = {m: {} for m in models}

    for seed in seeds:
        print(f"\n--- Running Seed {seed} ---")
        rng_init = np.random.RandomState(seed)
        init_supp = list(rng_init.choice(config["d_features"], size=config["k_true"], replace=False))
        
        # Instantiate learners and controllers for this seed
        dense = DenseNLMS(d=config["d_features"], mu=config["nlms_mu"], eps=config["nlms_eps"])
        w_oracle = np.zeros(config["k_true"], dtype=np.float64)
        
        # Policies
        f0_policy = RoundRobinProbePolicy()
        f1_policy = PriorityProbePolicy(priority_fraction=config["priority_fraction"])
        f2_policy = PersistenceProbePolicy(
            d=config["d_features"],
            priority_fraction=config["priority_fraction"],
            n_priority_min=config["n_priority_min"],
            c_conf=config["c_conf"]
        )
        f3_policy = ExploreConfirmPolicy(
            d=config["d_features"],
            c_max=config["c_max"],
            n_screen=config["n_screen"],
            theta_screen=config["theta_screen"],
            gamma_screen=config["gamma_screen"],
            theta_drop=config["theta_drop"],
            gamma_drop=config["gamma_drop"],
            confirm_max_probes=config["confirm_max_probes"],
            confirm_fraction=None,
            coverage_fraction=None
        )
        f4_policy = ExploreConfirmPolicy(
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
        )
        f5_policy = OracleTargetingPolicy()
        
        # Sparse learners
        learners = {
            "F0_Baseline": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f0_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
            "F1_Priority": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f1_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
            "F2_Persistence": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f2_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
            "F3_ExploreConfirm": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f3_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
            "F4_EC_Coverage": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f4_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
            "F5_Oracle_Targeting": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=f5_policy, q=config["q_base"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"], t_protect=0
            ),
        }
        
        # Probe bank controllers
        controllers = {
            m: ProbeBankController(
                q_min=config["q_min"], q_base=config["q_base"], q_max=config["q_max"],
                tau_low=config["tau_low"], tau_high=config["tau_high"], alpha=config["ema_alpha"],
                total_steps=config["total_steps"], target_budget=target_probes
            ) for m in ["F0_Baseline", "F1_Priority", "F2_Persistence", "F3_ExploreConfirm", "F4_EC_Coverage", "F5_Oracle_Targeting"]
        }
        
        sparse_models = ["F0_Baseline", "F1_Priority", "F2_Persistence", "F3_ExploreConfirm", "F4_EC_Coverage", "F5_Oracle_Targeting"]
        
        # Step-tracking structures
        histories = {m: {
            "losses": [],
            "r1_losses": [],
            "r2_losses": [],
            "full_r2_losses": [],
            "complete_supp_losses": [],
            "incomplete_supp_losses": [],
            "recalls": [],
            "r2_recalls": [],
            "full_supp_flags": [],
            "omitted_energy": [],
            "q_history": [],
            "flops_history": [],
            "true_probes": 0,
            "noise_probes": 0,
            "relevant_window_probes": 0,
            "relevant_true_probes": 0,
            "true_promotions": 0,
            "noise_promotions": 0,
            "candidate_probe_counts": np.zeros(config["d_features"], dtype=np.int32),
            "omitted_probe_counts": {f: 0 for f in r2_true_indices}, # probes while omitted in R2
            "promotions_list": [],
            "confirm_count_history": [],
            "explore_count_history": [],
        } for m in models}
        
        # Latency tracking for Regime 2 true features
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
            
            # --- 1. DENSE REFERENCE ---
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
                
            # --- 2. SPARSE ORACLE SUPPORT ---
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
                
            # --- 3. SPARSE MODELS (F0 to F5) ---
            for m in sparse_models:
                learner = learners[m]
                ctrl = controllers[m]
                
                # Predict
                y_hat = learner.predict(x)
                err = y - y_hat
                loss = err ** 2
                
                # Causal bank controller determines q_t
                q_t = ctrl.get_q(err, t)
                active_set_pre = set(learner.support)
                omitted_true_pre = set(true_supp).difference(active_set_pre)
                
                # Learner update
                stats = learner.update(x, y, q=q_t, true_support=true_supp)
                probed_candidates = stats["candidates"]
                
                # Track probes: relevant window auditing
                if len(omitted_true_pre) > 0:
                    histories[m]["relevant_window_probes"] += len(probed_candidates)
                    for cand in probed_candidates:
                        if cand in omitted_true_pre:
                            histories[m]["relevant_true_probes"] += 1
                            
                for cand in probed_candidates:
                    histories[m]["candidate_probe_counts"][cand] += 1
                    if cand in omitted_true_pre:
                        histories[m]["true_probes"] += 1
                    else:
                        histories[m]["noise_probes"] += 1
                        
                    # Track probes to omitted R2 features
                    if t > shift_step and cand in omitted_true_pre and cand in r2_true_indices:
                        histories[m]["omitted_probe_counts"][cand] += 1
                        
                    # First probe in Regime 2
                    if t > shift_step and cand in r2_true_indices:
                        if feat_tracking[m][cand]["first_probe"] is None:
                            feat_tracking[m][cand]["first_probe"] = t
                
                # Compute FLOPs accounting including screening overhead
                extra_flops = 0
                if m == "F1_Priority":
                    # Old heuristic: scored all inactive candidates with n > 0
                    scored_count = int(np.sum((learner.cand_n > 0) & np.isin(np.arange(learner.d), list(active_set_pre), invert=True)))
                    extra_flops += ResourceTracker.priority_scoring_flops(scored_count)
                elif m == "F2_Persistence":
                    # Lazy scoring: only probed candidates updated + 2 ops per inactive check
                    extra_flops += len(probed_candidates) * 6
                elif m in ["F3_ExploreConfirm", "F4_EC_Coverage"]:
                    # State machine check for confirmed candidates: 2 ops per confirmed candidate checked
                    policy_obj = learner.probe_policy
                    extra_flops += ResourceTracker.explore_confirm_check_flops(len(policy_obj.confirm_set))
                
                total_step_flops = stats["flops"] + extra_flops
                
                # Post-update support tracking
                act_supp = list(learner.support)
                true_in_supp = set(act_supp).intersection(true_supp)
                recall = len(true_in_supp) / float(config["k_star"])
                is_full = 1 if len(true_in_supp) == config["k_star"] else 0
                
                # Omitted energy
                omitted = [j for j in true_supp if j not in act_supp]
                e_omit = float(np.sum([true_beta[j] ** 2 for j in omitted])) if omitted else 0.0
                
                # Promotion tracking
                p_feat = stats["promoted_feat"]
                v_feat = stats["victim_feat"]
                
                if p_feat is not None:
                    is_true_promo = 1 if (p_feat in true_supp) else 0
                    if is_true_promo:
                        histories[m]["true_promotions"] += 1
                        if t > shift_step and p_feat in r2_true_indices and feat_tracking[m][p_feat]["promotion"] is None:
                            feat_tracking[m][p_feat]["promotion"] = t
                    else:
                        histories[m]["noise_promotions"] += 1
                        
                    promo_record = {
                        "seed": seed,
                        "model": m,
                        "feature": p_feat,
                        "is_true": is_true_promo,
                        "promotion_step": t,
                        "eviction_step": None,
                        "lifetime": None
                    }
                    histories[m]["promotions_list"].append(promo_record)
                    
                if v_feat is not None:
                    if t > shift_step and v_feat in r2_true_indices:
                        feat_tracking[m][v_feat]["evictions"].append(t)
                    # Close lifetime of evicted feature
                    for pr in reversed(histories[m]["promotions_list"]):
                        if pr["feature"] == v_feat and pr["eviction_step"] is None:
                            pr["eviction_step"] = t
                            pr["lifetime"] = t - pr["promotion_step"]
                            break
                            
                # Confirm / Explore candidate counts for F3 and F4
                if m in ["F3_ExploreConfirm", "F4_EC_Coverage"]:
                    c_len = len(learner.probe_policy.confirm_set)
                    histories[m]["confirm_count_history"].append(c_len)
                    histories[m]["explore_count_history"].append(config["d_features"] - len(act_supp) - c_len)
                else:
                    histories[m]["confirm_count_history"].append(0)
                    histories[m]["explore_count_history"].append(config["d_features"] - len(act_supp))
                    
                # Store histories
                histories[m]["losses"].append(loss)
                histories[m]["recalls"].append(recall)
                histories[m]["omitted_energy"].append(e_omit)
                histories[m]["q_history"].append(q_t)
                histories[m]["flops_history"].append(total_step_flops)
                
                if is_full:
                    histories[m]["complete_supp_losses"].append(loss)
                else:
                    histories[m]["incomplete_supp_losses"].append(loss)
                    
                if t <= shift_step:
                    histories[m]["r1_losses"].append(loss)
                else:
                    histories[m]["full_r2_losses"].append(loss)
                    histories[m]["r2_recalls"].append(recall)
                    histories[m]["full_supp_flags"].append(is_full)
                if t > 1800:
                    histories[m]["r2_losses"].append(loss)
                    
                # Candidate-level event logging for Seed 42
                if seed == rep_seed and t % 5 == 0:
                    # Log true features state
                    for tf in r2_true_indices:
                        is_conf = 1 if (m in ["F3_ExploreConfirm", "F4_EC_Coverage"] and tf in learner.probe_policy.confirm_set) else 0
                        events_seed42.append({
                            "step": t,
                            "model": m,
                            "candidate": tf,
                            "is_true": 1,
                            "in_support": 1 if tf in act_supp else 0,
                            "state": "CONFIRM" if is_conf else ("ACTIVE" if tf in act_supp else "EXPLORE"),
                            "n": learner.cand_n[tf],
                            "mean_corr": learner.cand_mean[tf],
                            "variance": learner.cand_m2[tf] / max(1, learner.cand_n[tf] - 1),
                            "sign_consistency": max(learner.cand_pos[tf], learner.cand_neg[tf]) / max(1, learner.cand_n[tf]),
                            "probed_this_step": 1 if tf in probed_candidates else 0,
                            "q_t": q_t,
                            "recall": recall
                        })

        # Feature Latency Decomposition per seed
        for m in sparse_models:
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
                
            # Probe allocation summary for this seed
            tot_p = sum(histories[m]["q_history"])
            tp = histories[m]["true_probes"]
            np_p = histories[m]["noise_probes"]
            rel_tp = histories[m]["relevant_true_probes"]
            rel_tot = histories[m]["relevant_window_probes"]
            rel_prec = rel_tp / float(rel_tot) if rel_tot > 0 else 0.0
            old_eff = tp / float(tp + np_p) if (tp + np_p) > 0 else 0.0
            
            # Candidate Coverage @1, @4, @8
            om_counts = list(histories[m]["omitted_probe_counts"].values())
            cov_1 = sum(1 for c in om_counts if c >= 1) / 5.0
            cov_4 = sum(1 for c in om_counts if c >= 4) / 5.0
            cov_8 = sum(1 for c in om_counts if c >= 8) / 5.0
            
            # Confirm specific metrics
            if m in ["F3_ExploreConfirm", "F4_EC_Coverage"]:
                pol = learners[m].probe_policy
                all_conf_entries = sum(1 for ev in pol.confirm_events_log if ev["event"] == "entry")
                true_conf_entries = sum(1 for ev in pol.confirm_events_log if ev["event"] == "entry" and ev["is_true"] == 1)
                conf_prec = true_conf_entries / float(all_conf_entries) if all_conf_entries > 0 else 0.0
                false_conf_probes = pol.false_confirm_probes
                true_conf_probes = pol.true_confirm_probes
                noise_locks = pol.noise_confirm_locks
                for ev in pol.confirm_events_log:
                    confirm_event_records.append({
                        "seed": seed,
                        "model": m,
                        **ev
                    })
            else:
                conf_prec = 0.0
                false_conf_probes = 0
                true_conf_probes = 0
                noise_locks = 0
                
            promo_prec = histories[m]["true_promotions"] / float(histories[m]["true_promotions"] + histories[m]["noise_promotions"]) if (histories[m]["true_promotions"] + histories[m]["noise_promotions"]) > 0 else 0.0
            
            probe_alloc_records.append({
                "seed": seed,
                "model": m,
                "total_probes": tot_p,
                "true_probes": tp,
                "noise_probes": np_p,
                "historical_efficiency": old_eff,
                "relevant_probe_precision": rel_prec,
                "true_candidate_coverage_1": cov_1,
                "true_candidate_coverage_4": cov_4,
                "true_candidate_coverage_8": cov_8,
                "confirm_precision": conf_prec,
                "false_confirm_probes": false_conf_probes,
                "true_confirm_probes": true_conf_probes,
                "promotion_precision": promo_prec,
                "noise_confirm_locks": noise_locks
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
                    "confirm_counts": histories[m]["confirm_count_history"],
                    "explore_counts": histories[m]["explore_count_history"],
                    "flops_history": histories[m]["flops_history"]
                }

        # Budget Validity Gate per seed
        for m in sparse_models:
            tot_probes = sum(histories[m]["q_history"])
            if tot_probes != target_probes:
                raise ValueError(f"BUDGET GATE VIOLATED: Model {m} used {tot_probes} probes (target: {target_probes}) on seed {seed}!")

        # Summary metrics per model for this seed
        for m in models:
            fl_recs = [r for r in feature_latency_records if r["seed"] == seed and r["model"] == m]
            mean_t_wait = np.mean([r["t_wait_probe"] for r in fl_recs]) if fl_recs else 0.0
            mean_t_evid = np.mean([r["t_evidence"] for r in fl_recs]) if fl_recs else 0.0
            mean_t_post = np.mean([r["t_post_promotion"] for r in fl_recs]) if fl_recs else 0.0
            stable_lat = np.max([r["first_stable_retention"] for r in fl_recs]) - 1001 if fl_recs else 0
            
            pa_rec = [r for r in probe_alloc_records if r["seed"] == seed and r["model"] == m]
            rel_prec = pa_rec[0]["relevant_probe_precision"] if pa_rec else 0.0
            cov_1 = pa_rec[0]["true_candidate_coverage_1"] if pa_rec else 1.0
            cov_4 = pa_rec[0]["true_candidate_coverage_4"] if pa_rec else 1.0
            cov_8 = pa_rec[0]["true_candidate_coverage_8"] if pa_rec else 1.0
            conf_prec = pa_rec[0]["confirm_precision"] if pa_rec else 0.0
            false_conf_probes = pa_rec[0]["false_confirm_probes"] if pa_rec else 0
            noise_locks = pa_rec[0]["noise_confirm_locks"] if pa_rec else 0
            promo_prec = pa_rec[0]["promotion_precision"] if pa_rec else 1.0
            tot_probes = pa_rec[0]["total_probes"] if pa_rec else 0

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
                "mse_complete": float(np.mean(histories[m]["complete_supp_losses"])) if histories[m]["complete_supp_losses"] else 0.0,
                "mse_incomplete": float(np.mean(histories[m]["incomplete_supp_losses"])) if histories[m]["incomplete_supp_losses"] else 0.0,
                "final_recall": float(histories[m]["recalls"][-1]),
                "mean_r2_recall": float(np.mean(histories[m]["r2_recalls"])) if histories[m]["r2_recalls"] else 1.0,
                "full_support_occupancy": float(np.mean(histories[m]["full_supp_flags"])) if histories[m]["full_supp_flags"] else 1.0,
                "stable_acquisition_latency": stable_lat,
                "t_wait_probe": mean_t_wait,
                "t_evidence": mean_t_evid,
                "t_post_promotion": mean_t_post,
                "cumulative_omitted_energy": float(np.sum(histories[m]["omitted_energy"])),
                "relevant_probe_precision": rel_prec,
                "true_candidate_coverage_1": cov_1,
                "true_candidate_coverage_4": cov_4,
                "true_candidate_coverage_8": cov_8,
                "confirm_precision": conf_prec,
                "false_confirm_probes": false_conf_probes,
                "promotion_precision": promo_prec,
                "noise_confirm_locks": noise_locks,
                "total_probes": tot_probes,
                "mean_flops": mean_flops,
                "peak_flops": peak_flops,
                "compute_ratio_dense": mean_flops / 602.0,
                "memory_bytes": mem_b
            })

    print(f"\nAll runs completed in {time.time() - t_start:.2f} seconds.")
    
    # Save CSV Artifacts
    df_feat_lat = pd.DataFrame(feature_latency_records)
    df_feat_lat.to_csv(os.path.join(exp_dir, "latency_decomposition.csv"), index=False)
    
    df_probe_alloc = pd.DataFrame(probe_alloc_records)
    df_probe_alloc.to_csv(os.path.join(exp_dir, "probe_allocation.csv"), index=False)
    
    if confirm_event_records:
        df_conf_ev = pd.DataFrame(confirm_event_records)
        df_conf_ev.to_csv(os.path.join(exp_dir, "confirm_events.csv"), index=False)
    else:
        pd.DataFrame(columns=["seed", "model", "step", "candidate", "is_true", "event", "confirm_probes", "mean_corr", "sign_consistency"]).to_csv(os.path.join(exp_dir, "confirm_events.csv"), index=False)
        
    if events_seed42:
        df_seed42 = pd.DataFrame(events_seed42)
        df_seed42.to_csv(os.path.join(exp_dir, "events_seed42.csv"), index=False)

    # Aggregate summaries across seeds
    df_summary = pd.DataFrame(seed_summaries)
    agg_cols = [
        "global_mse", "regime_1_mse", "regime_2_mse", "mse_complete", "mse_incomplete",
        "final_recall", "mean_r2_recall", "full_support_occupancy",
        "stable_acquisition_latency", "t_wait_probe", "t_evidence", "t_post_promotion",
        "cumulative_omitted_energy", "relevant_probe_precision",
        "true_candidate_coverage_1", "true_candidate_coverage_4", "true_candidate_coverage_8",
        "confirm_precision", "false_confirm_probes", "promotion_precision",
        "noise_confirm_locks", "total_probes", "mean_flops", "peak_flops",
        "compute_ratio_dense", "memory_bytes"
    ]
    
    grouped = df_summary.groupby("model")[agg_cols].mean().reset_index()
    # Ensure exact model ordering
    grouped["model_order"] = grouped["model"].apply(lambda m: models.index(m) if m in models else 99)
    grouped = grouped.sort_values("model_order").drop(columns=["model_order"])
    
    grouped.to_csv(os.path.join(exp_dir, "results.csv"), index=False)
    
    # Save candidate metrics per feature
    if not df_feat_lat.empty:
        df_feat_summary = df_feat_lat.groupby(["model", "feature"])[["t_wait_probe", "t_evidence", "t_post_promotion", "t_total"]].mean().reset_index()
        df_feat_summary.to_csv(os.path.join(exp_dir, "candidate_metrics.csv"), index=False)


    print("\n=== EXP-0003 AGGREGATE RESULTS SUMMARY ===")
    display_cols = ["model", "regime_2_mse", "mean_r2_recall", "full_support_occupancy", "stable_acquisition_latency", "t_evidence", "relevant_probe_precision", "true_candidate_coverage_8", "mean_flops", "compute_ratio_dense"]
    print(grouped[display_cols].to_string(index=False))

    # --- GENERATE 10-PANEL FIGURES ---
    generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, confirm_event_records, models, rep_seed)

    return grouped, df_summary

def generate_figures(exp_dir, rep_trajectories, df_summary, df_feat_lat, confirm_event_records, models, rep_seed):
    print("\nGenerating 10-panel figure artifact...")
    fig = plt.figure(figsize=(24, 20))
    
    colors = {
        "Dense": "black",
        "Sparse_Oracle": "green",
        "F0_Baseline": "gray",
        "F1_Priority": "red",
        "F2_Persistence": "orange",
        "F3_ExploreConfirm": "blue",
        "F4_EC_Coverage": "purple",
        "F5_Oracle_Targeting": "teal"
    }

    # Helper rolling mean
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
    for m in ["F0_Baseline", "F1_Priority", "F2_Persistence", "F3_ExploreConfirm", "F4_EC_Coverage", "F5_Oracle_Targeting"]:
        flags = rep_trajectories[m].get("full_supp_flags", [])
        if flags:
            cum_occ = np.cumsum(flags) / (np.arange(len(flags)) + 1)
            ax3.plot(range(1001, 2001), cum_occ, label=m, color=colors.get(m, "blue"), lw=1.8)
    ax3.set_title("3. Full-Support Occupancy Timeline (Regime 2)")
    ax3.set_xlabel("Simulation Step")
    ax3.set_ylabel("Cumulative Occupancy")
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=8, loc="lower right")

    # 4. Cumulative Probes to True Omitted Candidates (Audit Comparison)
    ax4 = fig.add_subplot(4, 3, 4)
    sparse_models = ["F0_Baseline", "F1_Priority", "F2_Persistence", "F3_ExploreConfirm", "F4_EC_Coverage", "F5_Oracle_Targeting"]
    for m in sparse_models:
        sub_df = df_summary[df_summary["model"] == m]
        ax4.bar(m, sub_df["relevant_probe_precision"].mean(), color=colors.get(m, "blue"), alpha=0.85)
    ax4.set_title("4. Relevant Probe Precision (Omitted Steps)")
    ax4.set_ylabel("Precision (True / Total Probed)")
    ax4.tick_params(axis='x', rotation=30)
    ax4.grid(True, alpha=0.3)

    # 5. False Confirm Probes vs Noise Confirm Locks
    ax5 = fig.add_subplot(4, 3, 5)
    ec_models = ["F3_ExploreConfirm", "F4_EC_Coverage"]
    fcp = [df_summary[df_summary["model"] == m]["false_confirm_probes"].mean() for m in ec_models]
    tcp = [df_summary[df_summary["model"] == m]["true_confirm_probes"].mean() if "true_confirm_probes" in df_summary else 0 for m in ec_models]
    x_pos = np.arange(len(ec_models))
    ax5.bar(x_pos - 0.15, fcp, width=0.3, label="False Confirm Probes", color="crimson", alpha=0.85)
    ax5.bar(x_pos + 0.15, tcp, width=0.3, label="True Confirm Probes", color="forestgreen", alpha=0.85)
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(ec_models)
    ax5.set_title("5. Probes Spent in CONFIRM State")
    ax5.set_ylabel("Total Probes in CONFIRM")
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)

    # 6. EXPLORE vs CONFIRM candidate counts over time (Seed 42, F4)
    ax6 = fig.add_subplot(4, 3, 6)
    conf_c = rep_trajectories["F4_EC_Coverage"].get("confirm_counts", [])
    if conf_c:
        ax6.plot(range(1000, 2000), conf_c[1000:], label="CONFIRM Set Size (C_max=3)", color="purple", lw=2)
        ax6.axhline(3, color="red", linestyle="--", alpha=0.7, label="C_max Bound")
    ax6.set_title("6. Active Confirm Candidates (F4 Seed 42)")
    ax6.set_xlabel("Simulation Step")
    ax6.set_ylabel("Candidate Count")
    ax6.set_ylim(-0.2, 4)
    ax6.grid(True, alpha=0.3)
    ax6.legend(fontsize=8)

    # 7. Confirmation entries by truth status
    ax7 = fig.add_subplot(4, 3, 7)
    if confirm_event_records:
        df_conf = pd.DataFrame(confirm_event_records)
        entries = df_conf[df_conf["event"] == "entry"]
        if not entries.empty:
            grouped_entries = entries.groupby(["model", "is_true"]).size().unstack(fill_value=0)
            grouped_entries.plot(kind="bar", stacked=True, ax=ax7, color=["salmon", "lightgreen"], alpha=0.85)
            ax7.set_title("7. Confirm Entries by Truth Status")
            ax7.set_ylabel("Entry Count")
            ax7.legend(["Noise", "True Omitted"], fontsize=8)
            ax7.tick_params(axis='x', rotation=30)
    else:
        ax7.text(0.5, 0.5, "No Confirm Records", ha='center', va='center')
        ax7.set_title("7. Confirm Entries by Truth Status")

    # 8. T_evidence distribution across seeds
    ax8 = fig.add_subplot(4, 3, 8)
    t_evid_data = []
    labels = []
    for m in sparse_models:
        vals = df_feat_lat[df_feat_lat["model"] == m]["t_evidence"].values
        t_evid_data.append(vals)
        labels.append(m)
    ax8.boxplot(t_evid_data, tick_labels=labels)
    ax8.set_title("8. T_evidence Distribution (Target: 60% Cut)")
    ax8.set_ylabel("Steps (First Probe -> Promotion)")
    ax8.tick_params(axis='x', rotation=30)
    ax8.grid(True, alpha=0.3)

    # 9. Cumulative Omitted Energy vs time
    ax9 = fig.add_subplot(4, 3, 9)
    for m in sparse_models:
        oe = rep_trajectories[m].get("omitted_energy", [])
        if oe:
            cum_oe = np.cumsum(oe[1000:])
            ax9.plot(range(1000, 2000), cum_oe, label=m, color=colors.get(m, "blue"), lw=1.8)
    ax9.set_title("9. Cumulative Omitted Energy (Regime 2)")
    ax9.set_xlabel("Simulation Step")
    ax9.set_ylabel("Sum(beta_j^2)")
    ax9.grid(True, alpha=0.3)
    ax9.legend(fontsize=8)

    # 10. Compute (Mean FLOPs / Step vs 25% Dense Cap)
    ax10 = fig.add_subplot(4, 3, 10)
    all_models = ["Dense", "Sparse_Oracle"] + sparse_models
    mean_flops_list = [df_summary[df_summary["model"] == m]["mean_flops"].mean() for m in all_models]
    bar_colors = [colors.get(m, "blue") for m in all_models]
    ax10.bar(all_models, mean_flops_list, color=bar_colors, alpha=0.85)
    ax10.axhline(150.5, color="crimson", linestyle="--", lw=2, label="25% Dense Cap (150.5 FLOPs)")
    ax10.set_title("10. Mean FLOPs / Step vs 25% Compute Cap")
    ax10.set_ylabel("FLOPs / Step")
    ax10.tick_params(axis='x', rotation=30)
    ax10.grid(True, alpha=0.3)
    ax10.legend(fontsize=8)

    # 11. True Candidate Coverage @1, @4, @8
    ax11 = fig.add_subplot(4, 3, 11)
    x = np.arange(len(sparse_models))
    c1 = [df_summary[df_summary["model"] == m]["true_candidate_coverage_1"].mean() for m in sparse_models]
    c4 = [df_summary[df_summary["model"] == m]["true_candidate_coverage_4"].mean() for m in sparse_models]
    c8 = [df_summary[df_summary["model"] == m]["true_candidate_coverage_8"].mean() for m in sparse_models]
    ax11.bar(x - 0.25, c1, width=0.25, label="Cov @ 1 probe", color="lightblue")
    ax11.bar(x, c4, width=0.25, label="Cov @ 4 probes", color="royalblue")
    ax11.bar(x + 0.25, c8, width=0.25, label="Cov @ 8 probes", color="navy")
    ax11.set_xticks(x)
    ax11.set_xticklabels(sparse_models, rotation=30)
    ax11.set_title("11. True Candidate Coverage @ 1, 4, 8 Probes")
    ax11.set_ylabel("Coverage Rate")
    ax11.set_ylim(0, 1.1)
    ax11.legend(fontsize=8)
    ax11.grid(True, alpha=0.3)

    # 12. Oracle Gap Closed (MSE and Occupancy)
    ax12 = fig.add_subplot(4, 3, 12)
    f0_mse = df_summary[df_summary["model"] == "F0_Baseline"]["regime_2_mse"].mean()
    f5_mse = df_summary[df_summary["model"] == "F5_Oracle_Targeting"]["regime_2_mse"].mean()
    f0_occ = df_summary[df_summary["model"] == "F0_Baseline"]["full_support_occupancy"].mean()
    f5_occ = df_summary[df_summary["model"] == "F5_Oracle_Targeting"]["full_support_occupancy"].mean()
    
    test_models = ["F1_Priority", "F2_Persistence", "F3_ExploreConfirm", "F4_EC_Coverage"]
    gap_mse = []
    gap_occ = []
    for m in test_models:
        m_mse = df_summary[df_summary["model"] == m]["regime_2_mse"].mean()
        m_occ = df_summary[df_summary["model"] == m]["full_support_occupancy"].mean()
        gap_mse.append(max(0, (f0_mse - m_mse) / (f0_mse - f5_mse)))
        gap_occ.append(max(0, (m_occ - f0_occ) / (f5_occ - f0_occ)))
        
    x_gap = np.arange(len(test_models))
    ax12.bar(x_gap - 0.15, gap_mse, width=0.3, label="Oracle Gap Closed (MSE)", color="seagreen", alpha=0.85)
    ax12.bar(x_gap + 0.15, gap_occ, width=0.3, label="Oracle Gap Closed (Occupancy)", color="royalblue", alpha=0.85)
    ax12.set_xticks(x_gap)
    ax12.set_xticklabels(test_models, rotation=30)
    ax12.set_title("12. Oracle Gap Closed Diagnostics")
    ax12.set_ylabel("Fraction Closed")
    ax12.set_ylim(0, 1.1)
    ax12.legend(fontsize=8)
    ax12.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_path = os.path.join(exp_dir, "figures.png")
    plt.savefig(fig_path, dpi=200)
    plt.close()
    print(f"Saved 10-panel figures artifact to: {fig_path}")

if __name__ == "__main__":
    dev_flag = "--dev" in sys.argv
    run_experiment(dev_mode=dev_flag)
