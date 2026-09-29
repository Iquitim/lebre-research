import sys
sys.path.insert(0, '.')
from scratch.bench_v02_integration import generate_v02_stream
from scratch.run_v02_integration_experiments import IntegratedLEBREModel

X, y, meta = generate_v02_stream('I3_Single_Exact_Delay', 1301, 600)
m = IntegratedLEBREModel('T3')
for t in range(600):
    info = m.step(X[t], y[t])
    if t in [30, 60, 100, 150, 200, 250, 300, 350, 400, 500]:
        print(f"t={t:3d} | loss={info['loss']:.3f} | G_D_B={m.ema_G_D_B:+.4f} | G_R_B={m.ema_G_R_B:+.4f} | lags={len(m.active_taps)} | cands={len(m.provisional_cands)} | dec={info['decision']}")
