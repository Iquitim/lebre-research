import numpy as np
import pandas as pd
import os

def run_microtrace():
    np.random.seed(42)
    T = 8000
    D = 5
    L_MAX = 32
    K_MAX = 2
    
    # Phase 1: 0..2000 active lag (0, 6)
    # Phase 2: 2000..6000 silence on feature 0
    # Phase 3: 6000..8000 active lag (0, 6) returns
    X = np.random.randn(T, D)
    X[2000:6000, 0] = 0.0
    y = np.zeros(T)
    for t in range(6, T):
        y[t] = 0.8 * X[t-6, 0] + 0.1 * np.random.randn()
        
    variants = ["B7_PROPOSED_DYNAMIC_LAG", "B7_E0_ORIGINAL", "B7_E0_CORRECTED_UNGATED"]
    records = []
    
    for var in variants:
        # State tracking
        grid_pairs = [(i, k) for i in range(D) for k in range(1, L_MAX + 1)]
        corr_grid = np.zeros((D, L_MAX + 1))
        hist = np.zeros((D, L_MAX))
        h_ptr = 0
        w_base = np.zeros(D)
        w_out = 0.0
        s = 0.0
        active_taps = []
        provisional_cands = []
        probe_idx = 0
        
        # Scaling stats
        mu_x = np.zeros(D)
        var_x = np.ones(D)
        count_x = 0
        
        for t in range(T):
            x_raw = X[t]
            count_x += 1
            delta = x_raw - mu_x
            mu_x += delta / count_x
            var_x += delta * (x_raw - mu_x)
            std_x = np.sqrt(np.maximum(1e-4, var_x / max(1, count_x - 1)))
            x_t = np.clip((x_raw - mu_x) / std_x, -5.0, 5.0)
            
            # History buffer update
            hist[:, h_ptr] = x_t
            
            def get_delayed(i_feat, k_lag):
                idx = (h_ptr - k_lag) % L_MAX
                return hist[i_feat, idx]
                
            # Recurrent update
            if t > 0:
                s = 0.9 * s + 0.1 * float(np.dot(w_base[:D], x_t))
                
            # Feedforward
            y_base = float(np.dot(w_base, x_t))
            y_lag = sum(tap['w'] * get_delayed(tap['i'], tap['k']) for tap in active_taps)
            y_rec = w_out * s
            y_hat = y_base + y_lag + y_rec
            e_live = float(y[t]) - y_hat
            
            # Update provisional candidates
            promoted = []
            for cand in provisional_cands:
                val_cand = get_delayed(cand['i'], cand['k'])
                cand['w_shadow'] += 0.05 * e_live * val_cand
                cand['age'] += 1
                cand_gain = (e_live ** 2) - ((float(y[t]) - (y_hat + cand['w_shadow'] * val_cand)) ** 2)
                cand['evidence'] = 0.98 * cand['evidence'] + 0.02 * max(0.0, cand_gain)
                
                if cand['evidence'] > 0.15 and cand['age'] > 50:
                    if len(active_taps) < K_MAX:
                        active_taps.append({
                            'i': cand['i'], 'k': cand['k'], 'w': cand['w_shadow'],
                            'R': cand['evidence'], 'age': 0, 'zero_count': 0
                        })
                        promoted.append(cand)
            provisional_cands = [c for c in provisional_cands if c not in promoted and not (c['age'] > 150 and c['evidence'] < 0.02)]
            
            # Live base weights update
            denom_base = float(np.dot(x_t, x_t)) + 1e-4
            w_base += (0.05 / denom_base) * e_live * x_t
            
            # Active taps update & relevance
            evicted_tap = None
            for j, tap in enumerate(active_taps):
                val = get_delayed(tap['i'], tap['k'])
                tap['w'] += 0.05 * e_live * val
                tap['age'] += 1
                
                y_without_j = y_hat - tap['w'] * val
                e_without_j = float(y[t]) - y_without_j
                marginal_gain = (e_without_j ** 2) - (e_live ** 2)
                
                if var == "B7_PROPOSED_DYNAMIC_LAG":
                    if abs(val) > 0.1:
                        tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
                    # Eviction check: two-timescale + quiescence gate
                    if tap['R'] < 0.015 and tap['age'] > 300:
                        if abs(val) > 0.1:
                            tap['evict'] = True
                            evicted_tap = (tap['i'], tap['k'])
                            
                elif var == "B7_E0_ORIGINAL":
                    if abs(val) > 0.1:
                        tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
                    # Eviction check: original buggy check abs(w) < 0.05
                    if abs(tap['w']) < 0.05:
                        tap['zero_count'] += 1
                    else:
                        tap['zero_count'] = 0
                    if tap['zero_count'] > 50 and tap['age'] > 100:
                        tap['evict'] = True
                        evicted_tap = (tap['i'], tap['k'])
                        
                elif var == "B7_E0_CORRECTED_UNGATED":
                    # Ungated continuous relevance decay (no quiescence check)
                    tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
                    # Eviction check: standard relevance threshold WITHOUT quiescence gate
                    if tap['R'] < 0.015 and tap['age'] > 300:
                        tap['evict'] = True
                        evicted_tap = (tap['i'], tap['k'])
                        
            active_taps = [t_tap for t_tap in active_taps if not t_tap.get('evict', False)]
            
            # Recurrence
            w_out += 0.05 * e_live * s
            
            # Bounded candidate probing
            for _ in range(2):
                cand_pair = grid_pairs[probe_idx]
                probe_idx = (probe_idx + 1) % len(grid_pairs)
                i_p, k_p = cand_pair
                if not any(t_tap['i'] == i_p and t_tap['k'] == k_p for t_tap in active_taps) and \
                   not any(c['i'] == i_p and c['k'] == k_p for c in provisional_cands):
                    past_val = get_delayed(i_p, k_p)
                    corr_grid[i_p, k_p] = 0.95 * corr_grid[i_p, k_p] + 0.05 * (e_live * past_val)
                    if abs(corr_grid[i_p, k_p]) > 0.22 and len(provisional_cands) < 3:
                        provisional_cands.append({
                            'i': i_p, 'k': k_p, 'w_shadow': float(corr_grid[i_p, k_p]),
                            'evidence': 0.05, 'age': 0
                        })
                        
            h_ptr = (h_ptr + 1) % L_MAX
            
            # Record trajectory at critical boundaries and sample steps
            if t % 50 == 0 or t in [1999, 2000, 2001, 3000, 4000, 5000, 5999, 6000, 6001, 6100, 6500, 7000]:
                has_true_tap = any(t_tap['i'] == 0 and t_tap['k'] == 6 for t_tap in active_taps)
                tap_obj = next((t_tap for t_tap in active_taps if t_tap['i'] == 0 and t_tap['k'] == 6), None)
                records.append({
                    'variant': var,
                    'step': t,
                    'phase': 'ACTIVE_PRE' if t < 2000 else ('SILENCE' if t < 6000 else 'ACTIVE_POST'),
                    'pred_error': abs(e_live),
                    'num_active_taps': len(active_taps),
                    'has_true_lag': has_true_tap,
                    'tap_w': tap_obj['w'] if tap_obj else np.nan,
                    'tap_R': tap_obj['R'] if tap_obj else np.nan,
                    'tap_age': tap_obj['age'] if tap_obj else np.nan,
                    'tap_zero_count': tap_obj['zero_count'] if (tap_obj and 'zero_count' in tap_obj) else 0,
                    'evicted_event': evicted_tap is not None
                })
                
    df_out = pd.DataFrame(records)
    os.makedirs('experiments/DYNAMIC-LAG-LIFECYCLE-01A', exist_ok=True)
    out_csv = 'experiments/DYNAMIC-LAG-LIFECYCLE-01A/B7_B7E0_MICROTRACE.csv'
    df_out.to_csv(out_csv, index=False)
    print(f'Micro-trace written to {out_csv} ({len(df_out)} rows)')
    
    # Print key summary comparisons
    for var in variants:
        sub = df_out[df_out['variant'] == var]
        at_2000 = sub[sub['step'] == 1999]['has_true_lag'].values[0]
        at_5999 = sub[sub['step'] == 5999]['has_true_lag'].values[0]
        at_7000 = sub[sub['step'] == 7000]['has_true_lag'].values[0]
        err_post = sub[(sub['step'] >= 6000) & (sub['step'] <= 6500)]['pred_error'].mean()
        print(f'{var}:')
        print(f'  Alive at silence start (t=1999): {at_2000}')
        print(f'  Alive at silence end (t=5999): {at_5999}')
        print(f'  Alive post return (t=7000): {at_7000}')
        print(f'  Mean post-return error (t in 6000..6500): {err_post:.4f}')

if __name__ == '__main__':
    run_microtrace()
