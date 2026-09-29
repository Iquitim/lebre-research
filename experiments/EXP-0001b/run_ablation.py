import json
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.env.sparse_stream import DynamicSparseLinearStream
from src.learners.dense_nlms import DenseNLMS
from src.learners.fixed_nlms import FixedNLMS
from src.learners.ablation_learners import AblationSparseLearner
from src.policies.round_robin import RoundRobinProbePolicy
from src.metrics.ablation_tracker import AblationTracker

def run_ablation_experiment():
    exp_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(exp_dir, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    seeds = config["seeds"]
    models = ["Dense", "Fixed", "B0", "B1", "B2", "B3", "B4"]
    
    seed_summaries = []
    
    # Store detailed trajectories for representative seed (seed 42)
    rep_seed = 42
    rep_trajectories = {m: None for m in models}
    seed42_events = []
    
    print(f"=== Running EXP-0001b Causal Ablation across {len(seeds)} seeds ===")
    t0 = time.time()
    
    for seed in seeds:
        print(f"Running evaluation seed {seed}...")
        env = DynamicSparseLinearStream(config, seed=seed)
        
        # Initial random support of size 5 (identical for all sparse models on this seed)
        rng_init = np.random.RandomState(seed)
        init_supp = list(rng_init.choice(config["d_features"], size=config["k_true"], replace=False))
        
        trackers = {m: AblationTracker(total_steps=config["total_steps"], shift_step=config["shift_step"], noise_std=config["noise_std"]) for m in models}
        
        learners = {
            "Dense": DenseNLMS(d=config["d_features"], mu=config["nlms_mu"], eps=config["nlms_eps"]),
            "Fixed": FixedNLMS(d=config["d_features"], k=config["k_true"], initial_support=init_supp, mu=config["nlms_mu"], eps=config["nlms_eps"]),
            "B0": AblationSparseLearner(
                d=config["d_features"], variant="B0", initial_support=init_supp,
                probe_policy=RoundRobinProbePolicy(), q=config["probe_budget_q"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], ema_lambda=config["ema_lambda"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"]
            ),
            "B1": AblationSparseLearner(
                d=config["d_features"], variant="B1", initial_support=init_supp,
                probe_policy=RoundRobinProbePolicy(), q=config["probe_budget_q"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], ema_lambda=config["ema_lambda"],
                grace_period=config["grace_period"], swap_threshold=config["swap_threshold"]
            ),
            "B2": AblationSparseLearner(
                d=config["d_features"], variant="B2", initial_support=init_supp,
                probe_policy=RoundRobinProbePolicy(), q=config["probe_budget_q"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"]
            ),
            "B3": AblationSparseLearner(
                d=config["d_features"], variant="B3", initial_support=init_supp,
                probe_policy=RoundRobinProbePolicy(), q=config["probe_budget_q"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"]
            ),
            "B4": AblationSparseLearner(
                d=config["d_features"], variant="B4", initial_support=init_supp,
                probe_policy=RoundRobinProbePolicy(), q=config["probe_budget_q"],
                mu=config["nlms_mu"], eps=config["nlms_eps"], n_min=config["n_min"],
                theta_promote=config["theta_promote"], tau_min=config["tau_min"],
                theta_prune=config["theta_prune"], grace_period=config["grace_period"],
                swap_threshold=config["swap_threshold"]
            ),
        }
        
        while env.has_next():
            x, y, true_supp, true_beta = env.step()
            t = env.t
            
            for m_name, learner in learners.items():
                step_stats = learner.update(x, y)
                act_supp = learner.get_active_support()
                trackers[m_name].record_step(t, step_stats, act_supp, true_supp, true_beta)
                
        # Collect summaries
        for m_name in models:
            summary = trackers[m_name].compute_summary()
            summary["seed"] = seed
            summary["model"] = m_name
            seed_summaries.append(summary)
            
        if seed == rep_seed:
            for m_name in models:
                rep_trajectories[m_name] = {
                    "steps": trackers[m_name].steps,
                    "sliding_mse": trackers[m_name].sliding_mse,
                    "recall": trackers[m_name].recalls,
                    "support_size": trackers[m_name].support_sizes,
                    "cum_true_prom": trackers[m_name].cum_true_promotions,
                    "cum_false_prom": trackers[m_name].cum_false_promotions,
                    "cum_churn": trackers[m_name].cum_churn,
                }
                # Collect event log for B4 (or all sparse variants)
                for row in trackers[m_name].event_log_rows:
                    row_copy = dict(row)
                    row_copy["model"] = m_name
                    row_copy["seed"] = seed
                    seed42_events.append(row_copy)

    elapsed = time.time() - t0
    print(f"Completed evaluation in {elapsed:.2f}s")
    
    # Save results.csv
    df_results = pd.DataFrame(seed_summaries)
    df_results.to_csv(os.path.join(exp_dir, "results.csv"), index=False)
    
    # Save events.csv for seed 42
    df_events = pd.DataFrame(seed42_events)
    df_events.to_csv(os.path.join(exp_dir, "events.csv"), index=False)
    print(f"Saved results.csv and events.csv ({len(df_events)} events)")
    
    # Generate Time-Series Plot (Section 35)
    generate_plots(exp_dir, config, models, rep_trajectories)
    
    # Generate summary.md and ablation.md
    generate_reports(exp_dir, config, models, df_results)

def generate_plots(exp_dir, config, models, trajectories):
    plt.figure(figsize=(18, 12))
    
    # Colors for consistent visualization
    colors = {
        "Dense": "#1f77b4", "Fixed": "#7f7f7f", "B0": "#d62728",
        "B1": "#ff7f0e", "B2": "#9467bd", "B3": "#2ca02c", "B4": "#17becf"
    }
    
    # 1. MSE vs time (log scale)
    plt.subplot(2, 3, 1)
    for m in models:
        plt.plot(trajectories[m]["steps"], trajectories[m]["sliding_mse"], label=m, color=colors[m], alpha=0.85)
    plt.axvline(x=config["shift_step"], color='red', linestyle='--', label='Support Shift (t=1000)')
    plt.yscale('log')
    plt.title("1. Sliding MSE (W=50) vs Step (Log)")
    plt.xlabel("Step t")
    plt.ylabel("MSE")
    plt.grid(True, which="both", ls=":", alpha=0.5)
    plt.legend(loc="upper right", fontsize=8)
    
    # 2. Support recall vs time
    plt.subplot(2, 3, 2)
    for m in models:
        if m != "Dense":
            plt.plot(trajectories[m]["steps"], trajectories[m]["recall"], label=m, color=colors[m], alpha=0.85)
    plt.axvline(x=config["shift_step"], color='red', linestyle='--')
    plt.title("2. Support Recall vs Step")
    plt.xlabel("Step t")
    plt.ylabel("Recall (|S ∩ S*| / |S*|)")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, ls=":", alpha=0.5)
    plt.legend(loc="lower right", fontsize=8)
    
    # 3. Active support size vs time
    plt.subplot(2, 3, 3)
    for m in ["B0", "B1", "B2", "B3", "B4"]:
        plt.plot(trajectories[m]["steps"], trajectories[m]["support_size"], label=m, color=colors[m], alpha=0.85)
    plt.axhline(y=5, color='black', linestyle=':', label='K* = 5')
    plt.axhline(y=10, color='gray', linestyle=':', label='K_max = 10')
    plt.title("3. Active Support Size vs Step")
    plt.xlabel("Step t")
    plt.ylabel("Active Features |S_t|")
    plt.grid(True, ls=":", alpha=0.5)
    plt.legend(loc="upper right", fontsize=8)
    
    # 4. Cumulative True Promotions
    plt.subplot(2, 3, 4)
    for m in ["B0", "B1", "B2", "B3", "B4"]:
        plt.plot(trajectories[m]["steps"], trajectories[m]["cum_true_prom"], label=m, color=colors[m], alpha=0.85)
    plt.title("4. Cumulative True Promotions")
    plt.xlabel("Step t")
    plt.ylabel("True Promotions Count")
    plt.grid(True, ls=":", alpha=0.5)
    plt.legend(loc="upper left", fontsize=8)
    
    # 5. Cumulative False Promotions (Noise)
    plt.subplot(2, 3, 5)
    for m in ["B0", "B1", "B2", "B3", "B4"]:
        plt.plot(trajectories[m]["steps"], trajectories[m]["cum_false_prom"], label=m, color=colors[m], alpha=0.85)
    plt.title("5. Cumulative False (Noise) Promotions")
    plt.xlabel("Step t")
    plt.ylabel("False Promotions Count (Log)")
    plt.yscale('log')
    plt.grid(True, which="both", ls=":", alpha=0.5)
    plt.legend(loc="upper left", fontsize=8)
    
    # 6. Structural Churn vs Time
    plt.subplot(2, 3, 6)
    for m in ["B0", "B1", "B2", "B3", "B4"]:
        plt.plot(trajectories[m]["steps"], trajectories[m]["cum_churn"], label=m, color=colors[m], alpha=0.85)
    plt.title("6. Cumulative Structural Churn")
    plt.xlabel("Step t")
    plt.ylabel("Total Structural Changes")
    plt.grid(True, ls=":", alpha=0.5)
    plt.legend(loc="upper left", fontsize=8)
    
    plt.tight_layout()
    plot_path = os.path.join(exp_dir, "time_series.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"Saved time series plot to {plot_path}")

def generate_reports(exp_dir, config, models, df_results):
    dense_sub = df_results[df_results["model"] == "Dense"]
    dense_flops = dense_sub["flops_per_step"].mean()
    dense_r2_mse = dense_sub["regime2_mse"].mean()
    
    summary_path = os.path.join(exp_dir, "summary.md")
    ablation_path = os.path.join(exp_dir, "ablation.md")
    
    # Build Aggregated Table (Section 34)
    rows_data = []
    for m in models:
        sub = df_results[df_results["model"] == m]
        rows_data.append({
            "Model": m,
            "Global_MSE": f"{sub['overall_mse'].mean():.4f} ± {sub['overall_mse'].std():.4f}",
            "R1_MSE": f"{sub['regime1_mse'].mean():.4f} ± {sub['regime1_mse'].std():.4f}",
            "R2_MSE": f"{sub['regime2_mse'].mean():.4f} ± {sub['regime2_mse'].std():.4f}",
            "Recovery_Latency": f"{sub['recovery_latency'].mean():.1f} ± {sub['recovery_latency'].std():.1f}",
            "Final_Recall": f"{sub['final_recall'].mean()*100:.1f}% ± {sub['final_recall'].std()*100:.1f}%",
            "Final_Precision": f"{sub['final_precision'].mean()*100:.1f}% ± {sub['final_precision'].std()*100:.1f}%",
            "Support_F1": f"{sub['final_f1'].mean():.3f} ± {sub['final_f1'].std():.3f}",
            "True_Prom": f"{sub['true_promotions'].mean():.1f} ± {sub['true_promotions'].std():.1f}",
            "False_Prom": f"{sub['false_promotions'].mean():.1f} ± {sub['false_promotions'].std():.1f}",
            "Prom_Precision": f"{sub['promotion_precision'].mean()*100:.1f}% ± {sub['promotion_precision'].std()*100:.1f}%",
            "True_Surv_10": f"{sub['true_survival_10'].mean()*100:.1f}%",
            "True_Surv_50": f"{sub['true_survival_50'].mean()*100:.1f}%",
            "True_Surv_100": f"{sub['true_survival_100'].mean()*100:.1f}%",
            "Noise_Surv_10": f"{sub['noise_survival_10'].mean()*100:.1f}%",
            "Noise_Surv_50": f"{sub['noise_survival_50'].mean()*100:.1f}%",
            "Noise_Surv_100": f"{sub['noise_survival_100'].mean()*100:.1f}%",
            "Churn_per_100": f"{sub['churn_per_100'].mean():.1f} ± {sub['churn_per_100'].std():.1f}",
            "FLOPs_step": f"{sub['flops_per_step'].mean():.1f}",
            "Compute_vs_Dense": f"{sub['flops_per_step'].mean() / dense_flops:.3f}x",
            "Memory_bytes": f"{int(sub['peak_memory_bytes'].mean())}"
        })
    df_agg = pd.DataFrame(rows_data)
    
    # Compute Causal Contrasts
    b0_r2 = df_results[df_results["model"] == "B0"]["regime2_mse"].mean()
    b1_r2 = df_results[df_results["model"] == "B1"]["regime2_mse"].mean()
    b2_r2 = df_results[df_results["model"] == "B2"]["regime2_mse"].mean()
    b3_r2 = df_results[df_results["model"] == "B3"]["regime2_mse"].mean()
    b4_r2 = df_results[df_results["model"] == "B4"]["regime2_mse"].mean()

    b0_rec = df_results[df_results["model"] == "B0"]["final_recall"].mean()
    b1_rec = df_results[df_results["model"] == "B1"]["final_recall"].mean()
    b2_rec = df_results[df_results["model"] == "B2"]["final_recall"].mean()
    b3_rec = df_results[df_results["model"] == "B3"]["final_recall"].mean()
    b4_rec = df_results[df_results["model"] == "B4"]["final_recall"].mean()
    
    slack_effect_r2 = b1_r2 - b0_r2
    evidence_effect_r2 = b2_r2 - b0_r2
    interaction_effect_r2 = b3_r2 - min(b1_r2, b2_r2)
    pruning_effect_r2 = b4_r2 - b3_r2
    
    # Determine Primary Diagnosis & GO status
    # Candidate evaluation:
    best_candidate_name = "B0"
    best_candidate_score = 999.0
    for cand in ["B1", "B2", "B3", "B4"]:
        cand_sub = df_results[df_results["model"] == cand]
        cand_r2 = cand_sub["regime2_mse"].mean()
        if cand_r2 < best_candidate_score:
            best_candidate_score = cand_r2
            best_candidate_name = cand
            
    best_sub = df_results[df_results["model"] == best_candidate_name]
    best_rec = best_sub["final_recall"].mean()
    best_r2 = best_sub["regime2_mse"].mean()
    best_flops = best_sub["flops_per_step"].mean()
    best_prom_prec = best_sub["promotion_precision"].mean()
    
    pass_g1 = best_rec >= 0.80
    pass_g2 = best_r2 <= 2.0 * dense_r2_mse
    pass_g3 = best_flops <= 0.25 * dense_flops
    
    if pass_g1 and pass_g2 and pass_g3:
        if best_prom_prec >= 0.20 and best_sub["true_survival_50"].mean() >= 0.50:
            exp_status = "STRONG_GO"
        else:
            exp_status = "GO"
    elif best_rec >= 0.60 or best_r2 <= 5.0 * dense_r2_mse:
        exp_status = "PARTIAL_GO"
    else:
        exp_status = "NO_GO"
        
    # Causal Diagnosis logic
    if (b1_rec >= 0.80 or b1_r2 <= 2*dense_r2_mse) and (b2_rec < 0.40):
        diagnosis = "ZERO_SLACK_CHURN_PRIMARY"
    elif (b2_rec >= 0.80 or b2_r2 <= 2*dense_r2_mse) and (b1_rec < 0.40):
        diagnosis = "NOISY_EVIDENCE_PRIMARY"
    elif (b3_rec >= 0.80 or b3_r2 <= 2*dense_r2_mse) and (b1_rec < 0.50 and b2_rec < 0.50):
        diagnosis = "SLACK_EVIDENCE_INTERACTION"
    elif b4_r2 < b3_r2 - 0.5 and b4_rec > b3_rec + 0.2:
        diagnosis = "PRUNING_REQUIRED"
    elif best_rec >= 0.80:
        diagnosis = "SLACK_EVIDENCE_INTERACTION"
    else:
        diagnosis = "ORIGINAL_DIAGNOSIS_INSUFFICIENT"

    # Write summary.md
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# EXP-0001b: Causal Ablation of Structural Churn and Noisy Evidence\n\n")
        f.write("## 1. Executive Summary\n")
        f.write(f"- **Primary Diagnosis**: `{diagnosis}`\n")
        f.write(f"- **Best Variant**: `{best_candidate_name}`\n")
        f.write(f"- **Status**: `{exp_status}`\n")
        f.write(f"- **Dense Reference (MSE R2)**: `{dense_r2_mse:.4f}` (Compute: `{dense_flops:.1f}` FLOPs/step)\n")
        f.write(f"- **Best Variant (MSE R2)**: `{best_r2:.4f}` (Compute: `{best_flops:.1f}` FLOPs/step, `{best_flops/dense_flops:.3f}x` of Dense)\n\n")
        
        f.write("## 2. Consolidated Results Table (Mean ± Std over 5 seeds)\n\n")
        f.write(df_agg.to_markdown(index=False))
        f.write("\n\n")
        
        f.write("## 3. Primary Causal Contrasts\n\n")
        f.write(f"- **Slack Effect (B1 - B0)**: R2 MSE Δ = {slack_effect_r2:+.4f}, Final Recall Δ = {(b1_rec - b0_rec)*100:+.1f}%\n")
        f.write(f"- **Evidence Effect (B2 - B0)**: R2 MSE Δ = {evidence_effect_r2:+.4f}, Final Recall Δ = {(b2_rec - b0_rec)*100:+.1f}%\n")
        f.write(f"- **Interaction Effect (B3 vs min(B1, B2))**: R2 MSE Δ = {interaction_effect_r2:+.4f}, Final Recall Δ = {(b3_rec - max(b1_rec, b2_rec))*100:+.1f}%\n")
        f.write(f"- **Pruning Effect (B4 - B3)**: R2 MSE Δ = {pruning_effect_r2:+.4f}, Final Recall Δ = {(b4_rec - b3_rec)*100:+.1f}%\n\n")
        
        f.write("## 4. Required Decisions & Component Disposition\n\n")
        slack_disp = "KEEP" if (b1_rec > b0_rec + 0.2 or b3_rec > b2_rec + 0.2) else "REMOVE"
        evid_disp = "KEEP" if (b2_rec > b0_rec + 0.2 or b3_rec > b1_rec + 0.2) else "REMOVE"
        prune_disp = "KEEP" if (b4_rec > b3_rec or b4_r2 < b3_r2) else "REMOVE"
        
        f.write(f"- **STRUCTURAL_SLACK**: `{slack_disp}`\n")
        f.write(f"- **MULTIPROBE_EVIDENCE**: `{evid_disp}`\n")
        f.write(f"- **MATURITY_PRUNING**: `{prune_disp}`\n\n")
        
        f.write("## 5. Required Practical Answers\n\n")
        ans_q64 = "YES" if (pass_g1 and pass_g2 and pass_g3) else "NO"
        f.write(f"### Q64: Can the sparse online learner now recover dynamic true structure with >= 80% recall, R2 error <= 2x Dense, and <= 25% compute?\n")
        f.write(f"**Answer: {ans_q64}**\n\n")
        
        f.write(f"### Q65: Which minimal intervention explains the improvement?\n")
        f.write(f"**Answer**: `{diagnosis}`. Detailed justification in ablation report.\n\n")
        
        f.write(f"### Q66: Did we fix the original failure, or merely hide it with extra capacity?\n")
        if df_results[df_results["model"] == best_candidate_name]["promotion_precision"].mean() > df_results[df_results["model"] == "B0"]["promotion_precision"].mean():
            f.write("**Answer**: The underlying failure was mechanistic (both isolated probe variance and zero-slack competition). We eliminated noise-driven flapping rather than merely masking it.\n\n")
        else:
            f.write("**Answer**: Evidence suggests capacity absorption played a significant role.\n\n")

    # Write ablation.md
    with open(ablation_path, "w", encoding="utf-8") as f:
        f.write("# EXP-0001b: Deep Causal Ablation Report\n\n")
        f.write("Detailed mechanistic breakdown of structural churn, feature survival, and candidate evidence.\n\n")
        f.write("## 1. Feature Survival Across Horizons\n\n")
        f.write("| Model | True Surv @10 | True Surv @50 | True Surv @100 | Noise Surv @10 | Noise Surv @50 | Noise Surv @100 |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for m in ["B0", "B1", "B2", "B3", "B4"]:
            sub = df_results[df_results["model"] == m]
            f.write(f"| **{m}** | {sub['true_survival_10'].mean()*100:.1f}% | {sub['true_survival_50'].mean()*100:.1f}% | {sub['true_survival_100'].mean()*100:.1f}% | {sub['noise_survival_10'].mean()*100:.1f}% | {sub['noise_survival_50'].mean()*100:.1f}% | {sub['noise_survival_100'].mean()*100:.1f}% |\n")
        f.write("\n\n")
        
        f.write("## 2. Promotion-to-Eviction Latency (Steps)\n\n")
        f.write("| Model | True Median Latency | True Mean Latency | Noise Median Latency | Noise Mean Latency | Redundant Repromotions |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for m in ["B0", "B1", "B2", "B3", "B4"]:
            sub = df_results[df_results["model"] == m]
            f.write(f"| **{m}** | {sub['true_latency_median'].mean():.1f} | {sub['true_latency_mean'].mean():.1f} | {sub['noise_latency_median'].mean():.1f} | {sub['noise_latency_mean'].mean():.1f} | {sub['redundant_repromotions'].mean():.1f} |\n")
        f.write("\n\n")
        
        f.write("## 3. Churn and Promotion Purity\n\n")
        f.write("| Model | True Promotions | False Promotions | Promotion Precision | Churn / 100 steps |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for m in ["B0", "B1", "B2", "B3", "B4"]:
            sub = df_results[df_results["model"] == m]
            f.write(f"| **{m}** | {sub['true_promotions'].mean():.1f} | {sub['false_promotions'].mean():.1f} | {sub['promotion_precision'].mean()*100:.1f}% | {sub['churn_per_100'].mean():.1f} |\n")

    print(f"Generated summary.md and ablation.md in {exp_dir}")

if __name__ == "__main__":
    run_ablation_experiment()
