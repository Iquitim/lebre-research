import pandas as pd

df = pd.read_csv('experiments/BENCH-01B/BENCH_01B_AGGREGATE_SUMMARY.csv')

def get_row(tid, mid):
    r = df[(df['task_id'] == tid) & (df['model_id'] == mid)]
    if len(r) == 0: return 'N/A'
    nmse = r['nmse_mean'].values[0]
    div = r['divergence_rate'].values[0]
    if pd.isna(nmse) or div > 0.5: return 'DIVERGED'
    return f'{nmse:.4f}'

def get_val(tid, mid, col):
    r = df[(df['task_id'] == tid) & (df['model_id'] == mid)]
    return r[col].values[0]

print("=== TABLE 7.1 BLOCK A ===")
a_tasks = [
    ('A1_Sparse_Support_Shift', 'A1', 'Sparse Support Shift', 'RZA-LMS won (0.0169); LEBRE adapts in 205 FLOPs'),
    ('A2_Single_Delayed_Dependency', 'A2', 'Single Delayed Dependency', 'Boundary: dense ESN won (0.9680); scalar state 1.1327'),
    ('A3_Multiple_Dispersed_Delays', 'A3', 'Multiple Dispersed Delays', 'Boundary: dense ESN won (0.9593); scalar state 1.1287'),
    ('A4_Long_Delay_Scaling', 'A4', 'Long-Delay Scaling', 'Boundary: GRU won (1.0001); scalar state 1.1356'),
    ('A5_Set_Reset_Quiescent_Memory', 'A5', 'Set/Reset Quiescent Memory', 'CCN won (0.4076); LEBRE 0.7901; LMS/GRU failed (>1.02)'),
    ('A6_Context_Routing', 'A6', 'Context Routing', 'RZA-LMS won (0.5245); LEBRE 0.5668 at 56.3 FLOPs'),
    ('A7_Extended_Poisson_Quiescence', 'A7', 'Extended Poisson Quiescence', 'CCN won (0.6017); LEBRE 0.8535; LMS/GRU failed (>1.01)'),
    ('A8_Abrupt_Tri_Regime_Transition', 'A8', 'Abrupt Tri-Regime Transition', 'LEBRE won (0.9540); dynamic scale 38->92->40 FLOPs')
]
for tid, sid, name, note in a_tasks:
    tb = get_row(tid, 'Track_B')
    lms = get_row(tid, 'B1_RZA_LMS')
    ccn = get_row(tid, 'B2_CCN')
    gru = get_row(tid, 'B4_MINIMAL_GRU')
    esn = get_row(tid, 'B5_ONLINE_ESN')
    flops = get_val(tid, 'Track_B', 'mean_flops')
    print(f'        <tr><td><strong>{sid}</strong></td><td>{name}</td><td>{lms}</td><td>{ccn}</td><td>{gru}</td><td>{esn}</td><td class="highlight-row">{tb}</td><td>{flops:.1f}</td><td>{note}</td></tr>')

print("\n=== TABLE 7.2 BLOCK B ===")
b_tasks = [
    ('B1_NSW_Electricity_Derived_Regression', 'B1', 'NSW Electricity Continuous', 'CCN won (0.4632); LEBRE competitive at 24.0 FLOPs'),
    ('B2_Jena_Weather', 'B2', 'Jena Weather Temperature', 'LEBRE won (0.0248); RZA-LMS & CCN diverged'),
    ('B3_Gas_Dynamic_Mixture', 'B3', 'Gas Dynamic Mixture', 'LEBRE won (0.0020); strictly led all competitive baselines'),
    ('B4_Silverbox_System_ID', 'B4', 'Silverbox System ID', 'ESN won (0.9136); documented boundary of scalar recurrence'),
    ('B5_Household_Power_Control', 'B5', 'Household Active Power', 'LEBRE won (0.0040); led CCN (0.0120) and GRU (0.0924)')
]
for tid, sid, name, note in b_tasks:
    tb = get_row(tid, 'Track_B')
    lms = get_row(tid, 'B1_RZA_LMS')
    ccn = get_row(tid, 'B2_CCN')
    gru = get_row(tid, 'B4_MINIMAL_GRU')
    esn = get_row(tid, 'B5_ONLINE_ESN')
    flops = get_val(tid, 'Track_B', 'mean_flops')
    print(f'        <tr><td><strong>{sid}</strong></td><td>{name}</td><td>{lms}</td><td>{ccn}</td><td>{gru}</td><td>{esn}</td><td class="highlight-row">{tb}</td><td>{flops:.1f}</td><td>{note}</td></tr>')
