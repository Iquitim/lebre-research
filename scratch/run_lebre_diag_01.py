#!/usr/bin/env python3
"""
LEBRE-DIAG-01: Comprehensive Mechanistic Diagnostic Engine.
Evaluates 720 runs:
6 tasks: A2, A3, A4 (primary), A5, A7, A8 (controls)
30 seeds: 201..230
4 variants: LEBRE_FROZEN, LEBRE_NO_REC_BIRTH, LEBRE_SHADOW_ONLY, LEBRE_ORACLE_HARM_STOP
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
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple, Optional

from experiments.bench01.streams import get_stream, CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper

EXP_DIR = ROOT / "experiments" / "LEBRE-DIAG-01"
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
SEEDS = list(range(201, 231)) # 30 fresh seeds: 201 to 230
VARIANTS = [
    "LEBRE_FROZEN",
    "LEBRE_NO_REC_BIRTH",
    "LEBRE_SHADOW_ONLY",
    "LEBRE_ORACLE_HARM_STOP"
]

def run_single_stream_diagnostic(
    task_id: str,
    seed: int,
    variant: str,
    test_split: float = 0.30
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    X, y = get_stream(task_id, seed=seed)
    T = len(X)
    D = X.shape[1]
    test_start = int(test_split * T)
    scaler = CausalStandardScaler(d=D)
    
    wrapper = TrackBFrozenWrapper(d_features=D)
    learner = wrapper.learner
    
    # Configure variants
    if variant == "LEBRE_NO_REC_BIRTH":
        learner._trigger_birth = lambda *args, **kwargs: None
    elif variant == "LEBRE_SHADOW_ONLY":
        def shadow_promote():
            learner.provisional_state = None
            learner.provisional_type = None
            learner.provisional_age = 0
        learner._promote_provisional_to_active = shadow_promote

    step_records = []
    losses = []
    base_losses = []
    flops_list = []
    
    # Event tracking
    events = []
    current_cand = None
    candidate_birth_idx = 0
    active_promoted_record = None
    
    # Regret / harm tracking
    harm_consecutive = 0
    
    for t in range(T):
        x_raw = X[t]
        y_true = float(y[t])
        x_norm = scaler.transform(x_raw)
        
        # Pre-step state inspection
        had_prov_before = learner.provisional_state is not None
        had_active_before = learner.active_state is not None
        prev_cand_type = learner.provisional_type
        
        # Run standard step
        pred, flops = wrapper.step(x_norm, y_true)
        info = wrapper.last_info
        y_base = float(info["y_base"])
        y_hat = float(pred)
        
        e_live = y_true - y_hat
        e_base = y_true - y_base
        e_live_sq = e_live ** 2
        e_base_sq = e_base ** 2
        
        has_prov_after = learner.provisional_state is not None
        has_active_after = learner.active_state is not None
        status_after = learner.get_lifecycle_status()
        
        # 1. Detect Birth Event
        if not had_prov_before and has_prov_after:
            candidate_birth_idx += 1
            current_cand = {
                "birth_idx": candidate_birth_idx,
                "seed": seed,
                "task_id": task_id,
                "variant": variant,
                "candidate_type": learner.provisional_type,
                "t_birth": t,
                "prov_e_cand_sq_list": [],
                "prov_e_base_sq_list": [],
                "w_prov_at_birth": float(learner.w_prov),
                "promoted": False,
                "t_promotion": None,
                "w_state_at_promotion": None,
                "t_maturity": None,
                "t_harm": None,
                "t_eviction": None,
                "eviction_reason": None,
                "G_prob": 0.0,
                "post_live_sq_list": [],
                "post_base_sq_list": [],
                "R_harm": 0.0,
                "U_ret_at_evict": 0.0,
                "O_obs_at_evict": 0.0,
            }
            
        # Accumulate probation metrics if provisional is present
        if current_cand is not None and has_prov_after:
            # Reconstruct shadow candidate prediction at step t
            s_p = learner.provisional_state.s if learner.provisional_state else 0.0
            yh_prov = y_base + learner.w_prov * s_p
            e_prov_sq = (y_true - yh_prov) ** 2
            current_cand["prov_e_cand_sq_list"].append(e_prov_sq)
            current_cand["prov_e_base_sq_list"].append(e_base_sq)
            
        # 2. Detect Promotion Event
        if had_prov_before and not has_prov_after and has_active_after:
            if current_cand is not None:
                current_cand["promoted"] = True
                current_cand["t_promotion"] = t
                current_cand["w_state_at_promotion"] = float(learner.w_state)
                # Compute G_prob
                sum_cand = sum(current_cand["prov_e_cand_sq_list"])
                sum_base = sum(current_cand["prov_e_base_sq_list"])
                current_cand["G_prob"] = float(1.0 - sum_cand / (sum_base + 1e-8))
                active_promoted_record = current_cand
                events.append(current_cand)
                current_cand = None
        elif had_prov_before and not has_prov_after and not has_active_after:
            # Candidate rejected without promotion
            if current_cand is not None:
                sum_cand = sum(current_cand["prov_e_cand_sq_list"])
                sum_base = sum(current_cand["prov_e_base_sq_list"])
                current_cand["G_prob"] = float(1.0 - sum_cand / (sum_base + 1e-8))
                events.append(current_cand)
                current_cand = None
                
        # 3. Track Post-Promotion Progression
        if active_promoted_record is not None:
            active_promoted_record["post_live_sq_list"].append(e_live_sq)
            active_promoted_record["post_base_sq_list"].append(e_base_sq)
            
            # Check for maturity transition
            if learner.active_age == learner.maturity_window and active_promoted_record["t_maturity"] is None:
                active_promoted_record["t_maturity"] = t
                
            # Check for harm onset (t_harm): 20 consecutive steps where live error exceeds base error
            regret_t = e_live_sq - e_base_sq
            if regret_t > 0:
                harm_consecutive += 1
                if harm_consecutive >= 20 and active_promoted_record["t_harm"] is None:
                    active_promoted_record["t_harm"] = t - 19 # point of onset
            else:
                harm_consecutive = max(0, harm_consecutive - 1)
                
            if active_promoted_record["t_harm"] is not None:
                active_promoted_record["R_harm"] += regret_t
                
        # 4. Detect Eviction Event
        if had_active_before and not has_active_after:
            if active_promoted_record is not None:
                active_promoted_record["t_eviction"] = t
                active_promoted_record["U_ret_at_evict"] = float(info.get("delta_loss", 0.0))
                active_promoted_record["O_obs_at_evict"] = float(info.get("o_proxy", 0.0))
                if learner.eviction_events:
                    active_promoted_record["eviction_reason"] = learner.eviction_events[-1].get("reason", "unknown")
                active_promoted_record = None
                harm_consecutive = 0
                
        # 5. Oracle Harm Stop logic
        if variant == "LEBRE_ORACLE_HARM_STOP" and learner.active_state is not None:
            reg = e_live_sq - e_base_sq
            if reg > 0:
                harm_consecutive += 1
                if harm_consecutive >= 20:
                    learner._evict_active_state(reason="oracle_harm_stop")
                    harm_consecutive = 0
            else:
                harm_consecutive = max(0, harm_consecutive - 1)
                
        scaler.update(x_raw)
        
        if t >= test_start:
            losses.append(e_live_sq)
            base_losses.append(e_base_sq)
            flops_list.append(flops)
            
    # Handle right-censored active state at stream end
    if active_promoted_record is not None:
        active_promoted_record["t_eviction"] = T
        active_promoted_record["eviction_reason"] = "stream_end_censored"
        active_promoted_record = None

    test_var = float(np.var(y[test_start:])) + 1e-6
    mse = float(np.mean(losses))
    nmse = mse / test_var
    mean_flops = float(np.mean(flops_list))
    peak_flops = float(np.max(flops_list)) if flops_list else 0.0
    
    summary = {
        "task_id": task_id,
        "seed": seed,
        "variant": variant,
        "status": "SUCCESS",
        "mse": mse,
        "nmse": nmse,
        "base_mse": float(np.mean(base_losses)),
        "base_nmse": float(np.mean(base_losses) / test_var),
        "mean_flops": mean_flops,
        "peak_flops": peak_flops,
        "memory_bytes": wrapper.get_memory_bytes(),
        "births_count": len(learner.birth_events),
        "evictions_count": len(learner.eviction_events),
    }
    
    # Process event-level horizons
    for ev in events:
        if ev["promoted"]:
            live_posts = ev["post_live_sq_list"]
            base_posts = ev["post_base_sq_list"]
            for H in [50, 100, 250, 500]:
                if len(live_posts) >= H:
                    s_l = sum(live_posts[:H])
                    s_b = sum(base_posts[:H])
                    ev[f"G_post_{H}"] = float(1.0 - s_l / (s_b + 1e-8))
                    ev[f"false_promotion_{H}"] = bool(ev[f"G_post_{H}"] < 0.0)
                else:
                    ev[f"G_post_{H}"] = None
                    ev[f"false_promotion_{H}"] = None
                    
            # Trajectory classification
            g50 = ev.get("G_post_50")
            g250 = ev.get("G_post_250")
            if g50 is None:
                ev["trajectory"] = "INDETERMINATE"
            elif g50 < 0:
                ev["trajectory"] = "IMMEDIATE_NEGATIVE"
            elif g250 is not None and g250 < 0:
                ev["trajectory"] = "SIGN_FLIP"
            elif g250 is not None and g250 < g50:
                ev["trajectory"] = "DECAYING_POSITIVE"
            elif g250 is not None and g250 >= g50:
                ev["trajectory"] = "STABLE_POSITIVE"
            else:
                ev["trajectory"] = "INDETERMINATE"
                
            # Eviction response latency
            if ev["t_harm"] is not None and ev["t_eviction"] is not None:
                ev["t_evict_response"] = ev["t_eviction"] - ev["t_harm"]
                ev["censored"] = bool(ev["t_eviction"] >= T)
            else:
                ev["t_evict_response"] = None
                ev["censored"] = False
        else:
            for H in [50, 100, 250, 500]:
                ev[f"G_post_{H}"] = None
                ev[f"false_promotion_{H}"] = None
            ev["trajectory"] = "NOT_PROMOTED"
            ev["t_evict_response"] = None
            ev["censored"] = False
            
    return summary, events

def main():
    print("=" * 80)
    print("LEBRE-DIAG-01: EXECUTION OF 720 PREREGISTERED RUNS")
    print(f"Tasks ({len(ALL_TASKS)}): {ALL_TASKS}")
    print(f"Seeds ({len(SEEDS)}): {SEEDS[0]}..{SEEDS[-1]}")
    print(f"Variants ({len(VARIANTS)}): {VARIANTS}")
    print("=" * 80)
    
    # 1. Build and save Run Manifest
    manifest_rows = []
    for task in ALL_TASKS:
        for seed in SEEDS:
            for var in VARIANTS:
                manifest_rows.append({
                    "run_id": f"DIAG01_{task}_{var}_SEED_{seed}",
                    "task_id": task,
                    "seed": seed,
                    "variant": var,
                    "status": "PREREGISTERED"
                })
    df_manifest = pd.DataFrame(manifest_rows)
    manifest_path = EXP_DIR / "LEBRE_DIAG_01_RUN_MANIFEST.csv"
    df_manifest.to_csv(manifest_path, index=False)
    print(f"Run Manifest saved: {manifest_path} ({len(df_manifest)} runs)")
    
    # 2. Execute runs
    seed_results = []
    all_events = []
    t_start = time.time()
    
    total = len(manifest_rows)
    for idx, row in enumerate(manifest_rows):
        t_id = row["task_id"]
        s_val = row["seed"]
        v_val = row["variant"]
        
        res_summary, ev_list = run_single_stream_diagnostic(t_id, s_val, v_val)
        seed_results.append(res_summary)
        
        # Only log events for FROZEN variant to maintain clean canonical accounting
        if v_val == "LEBRE_FROZEN":
            all_events.extend(ev_list)
            
        if (idx + 1) % 40 == 0 or (idx + 1) == total:
            elapsed = time.time() - t_start
            print(f"[{idx+1}/{total}] Completed in {elapsed:.1f}s | Latest: {t_id} {v_val} s={s_val} NMSE={res_summary['nmse']:.4f}")
            
    # 3. Save Seed Results
    df_seed_results = pd.DataFrame(seed_results)
    seed_csv_path = EXP_DIR / "LEBRE_DIAG_01_SEED_RESULTS.csv"
    df_seed_results.to_csv(seed_csv_path, index=False)
    print(f"Seed Results saved: {seed_csv_path} ({len(df_seed_results)} rows)")
    
    # 4. Save Event-Level Results
    df_events = pd.DataFrame(all_events)
    # Clean list columns for clean CSV storage
    cols_to_drop = ["prov_e_cand_sq_list", "prov_e_base_sq_list", "post_live_sq_list", "post_base_sq_list"]
    df_events_clean = df_events.drop(columns=[c for c in cols_to_drop if c in df_events.columns])
    event_csv_path = EXP_DIR / "LEBRE_DIAG_01_PROMOTION_EVENTS.csv"
    df_events_clean.to_csv(event_csv_path, index=False)
    print(f"Promotion Events saved: {event_csv_path} ({len(df_events_clean)} events)")
    
    print("\nAll 720 runs completed successfully!")

if __name__ == "__main__":
    main()
