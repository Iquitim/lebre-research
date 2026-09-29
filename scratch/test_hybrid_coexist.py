import sys
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
from scratch.bench_dynamic_lags import generate_dynamic_lag_stream
from experiments.bench01.streams import CausalStandardScaler
from experiments.bench01.baselines import TrackBFrozenWrapper

for task_id in ["D1_Single_Static_Delay", "D9_Memoryless_Negative_Control", "D11_Continuous_State_Control", "D12_Hybrid_Memory"]:
    X, y, meta = generate_dynamic_lag_stream(task_id, seed=701)
    T, D = X.shape
    L_MAX = 32
    K_MAX = 4
    
    wrapper = TrackBFrozenWrapper(d_features=D)
    scaler = CausalStandardScaler(d=D)
    history = np.zeros((D, L_MAX + 1))
    hist_ptr = 0
    corr_grid = np.zeros((D, L_MAX + 1))
    grid_pairs = [(i, k) for i in range(D) for k in range(1, L_MAX + 1)]
    probe_idx = 0
    
    active_taps = []
    provisional_cands = []
    losses = []
    
    for t in range(T):
        x_norm = scaler.transform(X[t])
        history[:, hist_ptr] = x_norm
        
        def get_delayed(i_feat, lag_k):
            return history[i_feat, (hist_ptr - lag_k) % (L_MAX + 1)]
            
        y_lag = sum(tap['w'] * get_delayed(tap['i'], tap['k']) for tap in active_taps)
        
        # Base model prediction
        y_base, _ = wrapper.step(x_norm, float(y[t]) - y_lag)
        y_hat = y_base + y_lag
        e_live = float(y[t]) - y_hat
        
        # Candidate scoring
        for cand in provisional_cands:
            c_val = get_delayed(cand['i'], cand['k'])
            y_cand = y_hat + cand['w_shadow'] * c_val
            e_cand = float(y[t]) - y_cand
            gain = (e_live ** 2) - (e_cand ** 2)
            cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * gain
            cand['age'] += 1
            cand['w_shadow'] += 0.05 * e_cand * c_val
            
        # Promotion
        promoted = []
        for cand in provisional_cands:
            if cand['evidence'] >= 0.14 and cand['age'] >= 25:
                if not any(t['i'] == cand['i'] and t['k'] == cand['k'] for t in active_taps):
                    if len(active_taps) < K_MAX:
                        active_taps.append({
                            'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                            'R': cand['evidence'], 'age': 0
                        })
                        promoted.append(cand)
                    else:
                        weakest_idx = int(np.argmin([t['R'] for t in active_taps]))
                        if cand['evidence'] > active_taps[weakest_idx]['R'] + 0.05:
                            active_taps[weakest_idx] = {
                                'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                                'R': cand['evidence'], 'age': 0
                            }
                            promoted.append(cand)
        provisional_cands = [c for c in provisional_cands if c not in promoted and not (c['age'] > 120 and c['evidence'] < 0.02)]
        
        # Tap adaptation & relevance
        for tap in active_taps:
            val = get_delayed(tap['i'], tap['k'])
            tap['w'] += 0.08 * e_live * val
            tap['age'] += 1
            e_without = float(y[t]) - (y_hat - tap['w'] * val)
            gain = (e_without ** 2) - (e_live ** 2)
            if abs(val) > 0.1:
                tap['R'] = 0.999 * tap['R'] + 0.001 * gain
            if tap['R'] < 0.05 and tap['age'] > 300 and abs(val) > 0.1:
                tap['evict'] = True
        active_taps = [t for t in active_taps if not t.get('evict', False)]
        
        # Probing (M=2)
        for _ in range(2):
            i_p, k_p = grid_pairs[probe_idx]
            probe_idx = (probe_idx + 1) % len(grid_pairs)
            if not any(t['i'] == i_p and t['k'] == k_p for t in active_taps) and \
               not any(c['i'] == i_p and c['k'] == k_p for c in provisional_cands):
                c_val = get_delayed(i_p, k_p)
                corr_grid[i_p, k_p] = 0.95 * corr_grid[i_p, k_p] + 0.05 * (e_live * c_val)
                if abs(corr_grid[i_p, k_p]) > 0.22 and len(provisional_cands) < 3:
                    provisional_cands.append({
                        'i': i_p, 'k': k_p, 'w_shadow': float(corr_grid[i_p, k_p]),
                        'evidence': 0.05, 'age': 0
                    })
                    
        hist_ptr = (hist_ptr + 1) % (L_MAX + 1)
        scaler.update(X[t])
        if t >= 3000:
            losses.append(e_live ** 2)
            
    mse = np.mean(losses)
    test_var = np.var(y[3000:])
    print(f"Task: {task_id[:12]} | NMSE: {mse/test_var:.4f} | Active Taps: {len(active_taps)} | Recurrent Active: {wrapper.learner.active_state is not None}")
