#!/usr/bin/env python3
"""
PROMOTION-POLICY-01: Sequential Structural Evidence & False-Promotion Control Engine.
Evaluates:
8 Variants:
  - LEBRE_v0.1_FIXED (P0)
  - FIXED_LONG (P1)
  - FIXED_STRICT (P2)
  - TWO_WINDOW_CONFIRM (P3)
  - CS_PROMOTION (P4)
  - GLOBAL_ERROR_BUDGET (P5)
  - CS_PLUS_BUDGET (P6)
  - LEBRE_NO_REC_BIRTH (Baseline)
6 Tasks:
  - Primary Negative Controls: A2, A3, A4
  - Primary Positive Controls: A5, A7
  - Neutral Transition Control: A8
Seeds:
  - Development: 301..310 (N=10)
  - Confirmatory Evaluation: 401..430 (N=30)
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import time
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

from experiments.bench01.streams import get_stream, CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper

EXP_DIR = ROOT / "experiments" / "PROMOTION-POLICY-01"
FIG_DIR = EXP_DIR / "figures"
EXP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

TASKS_PRIMARY = [
    "A2_Single_Delayed_Dependency",
    "A3_Multiple_Dispersed_Delays",
    "A4_Long_Delay_Scaling"
]
TASKS_CONTROL = [
    "A5_Set_Reset_Quiescent_Memory",
    "A7_Extended_Poisson_Quiescence",
    "A8_Abrupt_Tri_Regime_Transition"
]
ALL_TASKS = TASKS_PRIMARY + TASKS_CONTROL

DEV_SEEDS = list(range(301, 311)) # 10 seeds: 301..310
EVAL_SEEDS = list(range(401, 431)) # 30 seeds: 401..430

VARIANTS = [
    "LEBRE_v0.1_FIXED",
    "FIXED_LONG",
    "FIXED_STRICT",
    "TWO_WINDOW_CONFIRM",
    "CS_PROMOTION",
    "GLOBAL_ERROR_BUDGET",
    "CS_PLUS_BUDGET",
    "LEBRE_NO_REC_BIRTH"
]

def run_single_stream_policy(
    task_id: str,
    seed: int,
    variant: str,
    phase: str = "EVAL",
    test_split: float = 0.30
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    X, y = get_stream(task_id, seed=seed)
    T = len(X)
    D = X.shape[1]
    test_start = int(test_split * T)
    scaler = CausalStandardScaler(d=D)
    
    wrapper = TrackBFrozenWrapper(d_features=D)
    learner = wrapper.learner
    
    # Error budget state for P5 and P6
    wealth = 1.0
    birth_cost = 0.10
    success_reward = 0.25
    
    # Intercept birth for NO_REC_BIRTH or wealth constraint
    original_trigger_birth = learner._trigger_birth
    
    def controlled_trigger_birth(candidate_type="LINEAR", reason="causal_persistent_error"):
        nonlocal wealth
        if variant == "LEBRE_NO_REC_BIRTH":
            return
        if variant in ["GLOBAL_ERROR_BUDGET", "CS_PLUS_BUDGET"]:
            if wealth < birth_cost:
                return # Inhibit birth due to depleted opportunity budget
            wealth -= birth_cost
        original_trigger_birth(candidate_type=candidate_type, reason=reason)
        
    learner._trigger_birth = controlled_trigger_birth
    
    # Policy state tracking for provisional candidate
    # We will govern the promotion decision by custom policy evaluator
    cand_policy_state = {}
    
    # Event tracking
    events = []
    current_cand = None
    candidate_birth_idx = 0
    active_promoted_record = None
    harm_consecutive = 0
    
    losses = []
    base_losses = []
    flops_list = []
    
    # We disable learner's internal automatic promotion at probation expiration by overriding
    # and instead manage promotion decision precisely per policy
    original_promote = learner._promote_provisional_to_active
    
    for t in range(T):
        x_raw = X[t]
        y_true = float(y[t])
        x_norm = scaler.transform(x_raw)
        
        had_prov_before = learner.provisional_state is not None
        had_active_before = learner.active_state is not None
        
        # Step execution
        # To strictly enforce prequential evaluation, predict first
        pred, flops = wrapper.step(x_norm, y_true)
        info = wrapper.last_info
        y_base = float(info["y_base"])
        y_hat = float(pred)
        
        e_live_sq = (y_true - y_hat) ** 2
        e_base_sq = (y_true - y_base) ** 2
        
        has_prov_after = learner.provisional_state is not None
        has_active_after = learner.active_state is not None
        
        # 1. Candidate Birth Detection & Policy Initialization
        if not had_prov_before and has_prov_after:
            candidate_birth_idx += 1
            current_cand = {
                "birth_idx": candidate_birth_idx,
                "seed": seed,
                "task_id": task_id,
                "variant": variant,
                "phase": phase,
                "candidate_type": learner.provisional_type,
                "t_birth": t,
                "age_at_decision": 0,
                "decision": None,
                "t_decision": None,
                "G_prob": 0.0,
                "D_sum": 0.0,
                "promoted": False,
                "t_promotion": None,
                "t_eviction": None,
                "eviction_reason": None,
                "t_harm": None,
                "R_harm": 0.0,
                "prov_e_cand_sq_list": [],
                "prov_e_base_sq_list": [],
                "post_live_sq_list": [],
                "post_base_sq_list": []
            }
            cand_policy_state = {
                "age": 0,
                "sum_base_A": 0.0,
                "sum_cand_A": 0.0,
                "sum_base_B": 0.0,
                "sum_cand_B": 0.0,
                "mean_D": 0.0,
                "M2_D": 0.0,
                "t_cs": 0
            }
            
        # 2. Prequential Evidence Accumulation and Custom Policy Decision
        if current_cand is not None and has_prov_after:
            # Reconstruct shadow candidate prediction at step t
            s_p = learner.provisional_state.s if learner.provisional_state else 0.0
            yh_prov = y_base + learner.w_prov * s_p
            e_prov_sq = (y_true - yh_prov) ** 2
            D_t = e_base_sq - e_prov_sq
            
            current_cand["prov_e_cand_sq_list"].append(e_prov_sq)
            current_cand["prov_e_base_sq_list"].append(e_base_sq)
            current_cand["D_sum"] += D_t
            
            ps = cand_policy_state
            ps["age"] += 1
            age = ps["age"]
            
            # Update Welford for CS (P4 and P6)
            ps["t_cs"] += 1
            delta = D_t - ps["mean_D"]
            ps["mean_D"] += delta / ps["t_cs"]
            delta2 = D_t - ps["mean_D"]
            ps["M2_D"] += delta * delta2
            var_D = (ps["M2_D"] / (ps["t_cs"] - 1)) if ps["t_cs"] > 1 else 1.0
            std_D = max(1e-4, var_D ** 0.5)
            
            decision = "CONTINUE"
            
            # Policy Decision Rules
            if variant in ["LEBRE_v0.1_FIXED", "GLOBAL_ERROR_BUDGET"]:
                # Frozen baseline rule: age 50, gain > 0.05
                if age >= 50:
                    sum_c = sum(current_cand["prov_e_cand_sq_list"])
                    sum_b = sum(current_cand["prov_e_base_sq_list"])
                    g = 1.0 - sum_c / (sum_b + 1e-8)
                    if g > 0.05 or abs(learner.w_prov) > 0.30:
                        decision = "PROMOTE"
                    else:
                        decision = "DISCARD"
                        
            elif variant == "FIXED_LONG":
                # P1: 150 steps
                if age >= 150:
                    sum_c = sum(current_cand["prov_e_cand_sq_list"])
                    sum_b = sum(current_cand["prov_e_base_sq_list"])
                    g = 1.0 - sum_c / (sum_b + 1e-8)
                    if g > 0.05:
                        decision = "PROMOTE"
                    else:
                        decision = "DISCARD"
                        
            elif variant == "FIXED_STRICT":
                # P2: 50 steps, strict threshold 0.15
                if age >= 50:
                    sum_c = sum(current_cand["prov_e_cand_sq_list"])
                    sum_b = sum(current_cand["prov_e_base_sq_list"])
                    g = 1.0 - sum_c / (sum_b + 1e-8)
                    if g > 0.15:
                        decision = "PROMOTE"
                    else:
                        decision = "DISCARD"
                        
            elif variant == "TWO_WINDOW_CONFIRM":
                # P3: Two windows: Window A [1..50] (G_A > 0.05), Window B [51..100] (G_B > 0.02)
                if age <= 50:
                    ps["sum_base_A"] += e_base_sq
                    ps["sum_cand_A"] += e_prov_sq
                    if age == 50:
                        g_A = 1.0 - ps["sum_cand_A"] / (ps["sum_base_A"] + 1e-8)
                        if g_A <= 0.05:
                            decision = "DISCARD"
                elif age <= 100:
                    ps["sum_base_B"] += e_base_sq
                    ps["sum_cand_B"] += e_prov_sq
                    if age == 100:
                        g_B = 1.0 - ps["sum_cand_B"] / (ps["sum_base_B"] + 1e-8)
                        if g_B > 0.02:
                            decision = "PROMOTE"
                        else:
                            decision = "DISCARD"
                            
            elif variant in ["CS_PROMOTION", "CS_PLUS_BUDGET"]:
                # P4 & P6: Empirical Confidence Sequence
                # LCB = mean_D - z_crit * std_D / sqrt(t) * sqrt(1 + ln(t+1)/t)
                rad = 1.96 * (std_D / (age ** 0.5)) * ((1.0 + np.log(age + 1.0) / age) ** 0.5)
                lcb = ps["mean_D"] - rad
                ucb = ps["mean_D"] + rad
                
                if age >= 30 and lcb > 0.02:
                    decision = "PROMOTE"
                elif age >= 60 and ucb < 0.0:
                    decision = "DISCARD"
                elif age >= 150:
                    if ps["mean_D"] > 0.02:
                        decision = "PROMOTE"
                    else:
                        decision = "DISCARD"

            # Execute Decision
            if decision == "PROMOTE":
                current_cand["decision"] = "PROMOTE"
                current_cand["t_decision"] = t
                current_cand["age_at_decision"] = age
                current_cand["promoted"] = True
                current_cand["t_promotion"] = t
                sum_c = sum(current_cand["prov_e_cand_sq_list"])
                sum_b = sum(current_cand["prov_e_base_sq_list"])
                current_cand["G_prob"] = float(1.0 - sum_c / (sum_b + 1e-8))
                
                # Execute promotion on learner
                original_promote()
                active_promoted_record = current_cand
                events.append(current_cand)
                current_cand = None
                
            elif decision == "DISCARD":
                current_cand["decision"] = "DISCARD"
                current_cand["t_decision"] = t
                current_cand["age_at_decision"] = age
                sum_c = sum(current_cand["prov_e_cand_sq_list"])
                sum_b = sum(current_cand["prov_e_base_sq_list"])
                current_cand["G_prob"] = float(1.0 - sum_c / (sum_b + 1e-8))
                
                # Remove provisional
                learner.provisional_state = None
                learner.provisional_type = None
                learner.provisional_age = 0
                events.append(current_cand)
                current_cand = None

        # 3. Post-Promotion Realization & Harm Tracking
        if active_promoted_record is not None:
            active_promoted_record["post_live_sq_list"].append(e_live_sq)
            active_promoted_record["post_base_sq_list"].append(e_base_sq)
            
            # Check harm onset
            regret_t = e_live_sq - e_base_sq
            if regret_t > 0:
                harm_consecutive += 1
                if harm_consecutive >= 20 and active_promoted_record["t_harm"] is None:
                    active_promoted_record["t_harm"] = t - 19
            else:
                harm_consecutive = max(0, harm_consecutive - 1)
                
            if active_promoted_record["t_harm"] is not None:
                active_promoted_record["R_harm"] += regret_t
                
            # Eviction Detection
            if had_active_before and not has_active_after:
                active_promoted_record["t_eviction"] = t
                if learner.eviction_events:
                    active_promoted_record["eviction_reason"] = learner.eviction_events[-1].get("reason", "evicted")
                
                # Reward wealth in P5/P6 if the evicted state demonstrated net positive value
                sum_live = sum(active_promoted_record["post_live_sq_list"])
                sum_base = sum(active_promoted_record["post_base_sq_list"])
                if sum_live < sum_base:
                    wealth = min(2.0, wealth + success_reward)
                    
                active_promoted_record = None
                harm_consecutive = 0

        scaler.update(x_raw)
        
        if t >= test_start:
            losses.append(e_live_sq)
            base_losses.append(e_base_sq)
            flops_list.append(flops)
            
    # Handle censored state at end of stream
    if active_promoted_record is not None:
        active_promoted_record["t_eviction"] = T
        active_promoted_record["eviction_reason"] = "stream_end_censored"
        sum_live = sum(active_promoted_record["post_live_sq_list"])
        sum_base = sum(active_promoted_record["post_base_sq_list"])
        if sum_live < sum_base:
            wealth = min(2.0, wealth + success_reward)
        active_promoted_record = None

    test_var = float(np.var(y[test_start:])) + 1e-6
    mse = float(np.mean(losses))
    nmse = mse / test_var
    mean_flops = float(np.mean(flops_list))
    peak_flops = float(np.max(flops_list)) if flops_list else 0.0
    
    # Calculate policy-specific candidate metrics
    promotions = [e for e in events if e.get("promoted", False)]
    rejections = [e for e in events if not e.get("promoted", False)]
    
    # Count false promotions and useful promotions at H=250
    false_promotions = 0
    useful_promotions = 0
    latencies = []
    
    for p in promotions:
        latencies.append(p["age_at_decision"])
        post_l = p["post_live_sq_list"]
        post_b = p["post_base_sq_list"]
        h = min(250, len(post_l))
        if h > 0:
            gain_h = 1.0 - sum(post_l[:h]) / (sum(post_b[:h]) + 1e-8)
            if gain_h < 0.0:
                false_promotions += 1
            else:
                useful_promotions += 1
                
    summary = {
        "task_id": task_id,
        "seed": seed,
        "variant": variant,
        "phase": phase,
        "status": "SUCCESS",
        "mse": mse,
        "nmse": nmse,
        "base_mse": float(np.mean(base_losses)),
        "base_nmse": float(np.mean(base_losses) / test_var),
        "mean_flops": mean_flops,
        "peak_flops": peak_flops,
        "memory_bytes": wrapper.get_memory_bytes(),
        "births_count": candidate_birth_idx,
        "promotions_count": len(promotions),
        "rejections_count": len(rejections),
        "false_promotions_250": false_promotions,
        "useful_promotions_250": useful_promotions,
        "mean_decision_latency": float(np.mean(latencies)) if latencies else 0.0,
        "total_R_harm": sum(e.get("R_harm", 0.0) for e in events),
        "final_wealth": wealth
    }
    
    return summary, events

def run_all_experiments():
    print("Starting PROMOTION-POLICY-01 Execution...")
    
    # Phase 1: Development Runs (10 seeds: 301..310)
    print(f"--- Phase 1: Development Runs (Seeds {DEV_SEEDS[0]}..{DEV_SEEDS[-1]}) ---")
    dev_summaries = []
    dev_events = []
    
    dev_tasks_args = [
        (task_id, seed, variant, "DEV")
        for task_id in ALL_TASKS
        for seed in DEV_SEEDS
        for variant in VARIANTS
    ]
    print(f"Total DEV runs: {len(dev_tasks_args)}")
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_single_stream_policy, *args): args for args in dev_tasks_args}
        done_cnt = 0
        for future in as_completed(futures):
            done_cnt += 1
            summary, events = future.result()
            dev_summaries.append(summary)
            dev_events.extend(events)
            if done_cnt % 100 == 0 or done_cnt == len(dev_tasks_args):
                print(f"DEV progress: {done_cnt}/{len(dev_tasks_args)} completed")
                
    # Phase 2: Confirmatory Evaluation Runs (30 seeds: 401..430)
    print(f"\n--- Phase 2: Confirmatory Evaluation Runs (Seeds {EVAL_SEEDS[0]}..{EVAL_SEEDS[-1]}) ---")
    eval_summaries = []
    eval_events = []
    
    eval_tasks_args = [
        (task_id, seed, variant, "EVAL")
        for task_id in ALL_TASKS
        for seed in EVAL_SEEDS
        for variant in VARIANTS
    ]
    print(f"Total EVAL runs: {len(eval_tasks_args)}")
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(run_single_stream_policy, *args): args for args in eval_tasks_args}
        done_cnt = 0
        for future in as_completed(futures):
            done_cnt += 1
            summary, events = future.result()
            eval_summaries.append(summary)
            eval_events.extend(events)
            if done_cnt % 200 == 0 or done_cnt == len(eval_tasks_args):
                print(f"EVAL progress: {done_cnt}/{len(eval_tasks_args)} completed")

    all_summaries = dev_summaries + eval_summaries
    all_events = dev_events + eval_events
    
    # Save CSVs
    df_manifest = pd.DataFrame([
        {
            "task_id": s["task_id"],
            "seed": s["seed"],
            "variant": s["variant"],
            "phase": s["phase"],
            "status": s["status"]
        } for s in all_summaries
    ])
    df_manifest.to_csv(EXP_DIR / "PROMOTION_POLICY_01_RUN_MANIFEST.csv", index=False)
    print(f"Wrote {EXP_DIR / 'PROMOTION_POLICY_01_RUN_MANIFEST.csv'}")

    df_seeds = pd.DataFrame(all_summaries)
    df_seeds.to_csv(EXP_DIR / "PROMOTION_POLICY_01_SEED_RESULTS.csv", index=False)
    print(f"Wrote {EXP_DIR / 'PROMOTION_POLICY_01_SEED_RESULTS.csv'}")

    # Prepare events dataframe
    clean_events = []
    for e in all_events:
        post_l = e.get("post_live_sq_list", [])
        post_b = e.get("post_base_sq_list", [])
        g50 = 1.0 - sum(post_l[:50]) / (sum(post_b[:50]) + 1e-8) if len(post_l) >= 50 else None
        g100 = 1.0 - sum(post_l[:100]) / (sum(post_b[:100]) + 1e-8) if len(post_l) >= 100 else None
        g250 = 1.0 - sum(post_l[:250]) / (sum(post_b[:250]) + 1e-8) if len(post_l) >= 250 else None
        g500 = 1.0 - sum(post_l[:500]) / (sum(post_b[:500]) + 1e-8) if len(post_l) >= 500 else None
        
        clean_events.append({
            "task_id": e["task_id"],
            "seed": e["seed"],
            "variant": e["variant"],
            "phase": e["phase"],
            "birth_idx": e["birth_idx"],
            "candidate_type": e["candidate_type"],
            "t_birth": e["t_birth"],
            "decision": e["decision"],
            "t_decision": e["t_decision"],
            "age_at_decision": e["age_at_decision"],
            "promoted": e["promoted"],
            "t_promotion": e["t_promotion"],
            "t_eviction": e["t_eviction"],
            "eviction_reason": e.get("eviction_reason", "none"),
            "t_harm": e.get("t_harm", None),
            "R_harm": e.get("R_harm", 0.0),
            "G_prob": e["G_prob"],
            "G_post_50": g50,
            "G_post_100": g100,
            "G_post_250": g250,
            "G_post_500": g500
        })
        
    df_events = pd.DataFrame(clean_events)
    df_events.to_csv(EXP_DIR / "PROMOTION_POLICY_01_EVENTS.csv", index=False)
    print(f"Wrote {EXP_DIR / 'PROMOTION_POLICY_01_EVENTS.csv'}")

if __name__ == "__main__":
    run_all_experiments()
