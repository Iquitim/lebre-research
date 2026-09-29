import sys
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
from scratch.bench_dynamic_lags import generate_dynamic_lag_stream
from experiments.bench01.streams import CausalStandardScaler

X, y, meta = generate_dynamic_lag_stream('D1_Single_Static_Delay', seed=701)
T, D = X.shape
true_sup = meta['support_regimes'][0]['support']
print('True support:', true_sup)

L_MAX = 32
K_MAX = 4

w_base = np.zeros(D)
corr_grid = np.zeros((D, L_MAX + 1))
history = np.zeros((D, L_MAX + 1))
hist_ptr = 0

active_taps = []
provisional_cands = []
grid_pairs = [(i, k) for i in range(D) for k in range(1, L_MAX + 1)]
probe_idx = 0

losses = []
promotions = []
evictions = []

scaler = CausalStandardScaler(d=D)

for t in range(T):
    x_norm = scaler.transform(X[t])
    history[:, hist_ptr] = x_norm
    
    def get_delayed(i_feat, lag_k):
        return history[i_feat, (hist_ptr - lag_k) % (L_MAX + 1)]
        
    y_base = float(np.dot(w_base, x_norm))
    y_lag = sum(t['w'] * get_delayed(t['i'], t['k']) for t in active_taps)
    y_hat = y_base + y_lag
    e_live = float(y[t]) - y_hat
    
    # 1. Counterfactual candidate scoring
    for cand in provisional_cands:
        c_val = get_delayed(cand['i'], cand['k'])
        y_cand = y_hat + cand['w_shadow'] * c_val
        e_cand = float(y[t]) - y_cand
        gain = (e_live ** 2) - (e_cand ** 2)
        cand['evidence'] = 0.95 * cand['evidence'] + 0.05 * gain
        cand['age'] += 1
        cand['w_shadow'] += 0.05 * e_cand * c_val
        
    # 2. Promotion gate
    promoted = []
    for cand in provisional_cands:
        if cand['evidence'] >= 0.08 and cand['age'] >= 25:
            if not any(t['i'] == cand['i'] and t['k'] == cand['k'] for t in active_taps):
                if len(active_taps) < K_MAX:
                    active_taps.append({
                        'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                        'R': cand['evidence'], 'age': 0
                    })
                    promotions.append((t, cand['i'], cand['k']))
                    promoted.append(cand)
    provisional_cands = [c for c in provisional_cands if c not in promoted and not (c['age'] > 120 and c['evidence'] < 0.02)]
    
    # 3. Adaptation
    w_base += (0.10 / (np.dot(x_norm, x_norm) + 1e-4)) * e_live * x_norm
    for tap in active_taps:
        val = get_delayed(tap['i'], tap['k'])
        tap['w'] += 0.08 * e_live * val
        tap['age'] += 1
        e_without = float(y[t]) - (y_hat - tap['w'] * val)
        gain = (e_without ** 2) - (e_live ** 2)
        tap['R'] = 0.999 * tap['R'] + 0.001 * gain
        if tap['R'] < 0.01 and tap['age'] > 300 and abs(val) > 0.1:
            tap['evict'] = True
            evictions.append((t, tap['i'], tap['k']))
    active_taps = [t for t in active_taps if not t.get('evict', False)]
    
    # 4. Probing (M=2)
    for _ in range(2):
        i_p, k_p = grid_pairs[probe_idx]
        probe_idx = (probe_idx + 1) % len(grid_pairs)
        if not any(t['i'] == i_p and t['k'] == k_p for t in active_taps) and \
           not any(c['i'] == i_p and c['k'] == k_p for c in provisional_cands):
            c_val = get_delayed(i_p, k_p)
            corr_grid[i_p, k_p] = 0.95 * corr_grid[i_p, k_p] + 0.05 * (e_live * c_val)
            if abs(corr_grid[i_p, k_p]) > 0.18 and len(provisional_cands) < 3:
                provisional_cands.append({
                    'i': i_p, 'k': k_p, 'w_shadow': corr_grid[i_p, k_p],
                    'evidence': 0.04, 'age': 0
                })
                
    hist_ptr = (hist_ptr + 1) % (L_MAX + 1)
    scaler.update(X[t])
    if t >= 3000:
        losses.append(e_live ** 2)

mse = np.mean(losses)
test_var = np.var(y[3000:])
print('Refined B7 NMSE:', mse / test_var)
print('Promotions:', promotions)
print('Evictions:', evictions)
print('Final active taps:', [(t['i'], t['k'], round(t['w'], 3), round(t['R'], 3)) for t in active_taps])
