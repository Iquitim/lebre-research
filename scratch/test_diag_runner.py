import os
import sys
sys.path.insert(0, os.path.abspath("."))
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from experiments.bench01.streams import get_stream, CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper

def run_diagnostic_stream(
    task_id: str,
    seed: int,
    variant: str, # "LEBRE_FROZEN", "LEBRE_NO_REC_BIRTH", "LEBRE_SHADOW_ONLY", "LEBRE_ORACLE_HARM_STOP"
    test_split: float = 0.30,
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
        orig_promote = learner._promote_provisional_to_active
        def shadow_promote():
            # Record promotion event but do not couple to live active_state
            learner.provisional_state = None
            learner.provisional_type = None
            learner.provisional_age = 0
        learner._promote_provisional_to_active = shadow_promote
        
    losses = []
    base_losses = []
    flops_list = []
    
    # Event tracking
    events = []
    active_candidate_event = None
    promoted_events = [] # To track post-promotion horizons
    
    # Oracle harm tracking
    harm_consecutive = 0
    
    # Track candidate probation history for exact G_prob
    prov_history = []
    
    for t in range(T):
        x_raw = X[t]
        y_true = float(y[t])
        x_norm = scaler.transform(x_raw)
        
        # Capture state before step
        status_before = learner.get_lifecycle_status()
        prov_before = learner.provisional_state is not None
        active_before = learner.active_state is not None
        
        # Step
        pred, flops = wrapper.step(x_norm, y_true)
        info = wrapper.last_info
        y_base = float(info["y_base"])
        y_hat = float(pred)
        
        e_live_sq = (y_true - y_hat) ** 2
        e_base_sq = (y_true - y_base) ** 2
        
        if t >= test_start:
            losses.append(e_live_sq)
            base_losses.append(e_base_sq)
            flops_list.append(flops)
            
        scaler.update(x_raw)
        
        # Oracle Harm Stop logic:
        if variant == "LEBRE_ORACLE_HARM_STOP" and learner.active_state is not None:
            regret = e_live_sq - e_base_sq
            if regret > 0:
                harm_consecutive += 1
                if harm_consecutive >= 20: # 20 consecutive steps of harmful recurrent state
                    learner._evict_active_state(reason="oracle_harm_stop")
                    harm_consecutive = 0
            else:
                harm_consecutive = max(0, harm_consecutive - 1)
                
    test_var = float(np.var(y[test_start:])) + 1e-6
    mse = float(np.mean(losses))
    nmse = mse / test_var
    mean_flops = float(np.mean(flops_list))
    
    summary = {
        "task_id": task_id,
        "seed": seed,
        "variant": variant,
        "mse": mse,
        "nmse": nmse,
        "mean_flops": mean_flops,
        "births_count": len(learner.birth_events),
        "evictions_count": len(learner.eviction_events),
    }
    return summary, events

if __name__ == "__main__":
    for v in ["LEBRE_FROZEN", "LEBRE_NO_REC_BIRTH", "LEBRE_SHADOW_ONLY", "LEBRE_ORACLE_HARM_STOP"]:
        s, _ = run_diagnostic_stream("A2_Single_Delayed_Dependency", 201, v)
        print(f"{v}: NMSE={s['nmse']:.4f}, FLOPs={s['mean_flops']:.2f}, Births={s['births_count']}, Evicts={s['evictions_count']}")
