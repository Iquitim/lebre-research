"""dev_instab.py — DEV: which v0.4.5 mechanism causes start-point instability? (previously used data only)"""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "LEBRE-V0.45-ROBUST-GUARD-01")); sys.path.insert(0, HERE)
import dev_guard as G  # loaders for DEV data (BENCH-02, BENCH-03 series 1, external_v03)
from lebre_v045 import LebreV045
from experiments.bench01.streams import CausalStandardScaler
TASKS = [t for t in G.TASKS if t not in ("M_USBirths",)]
OFFSETS = list(range(0, 500, 50))
ARMS = {"V032": lambda d: G.B.LebreStep(d).m, "V045": lambda d: LebreV045(d=d),
        "NO_IP": lambda d: LebreV045(d=d, ipnlms=False), "IP_A05": lambda d: LebreV045(d=d, ip_alpha=0.5),
        "NO_FREEZE": lambda d: LebreV045(d=d, freeze_sigma_in_silence=False),
        "NO_IP_NO_FREEZE": lambda d: LebreV045(d=d, ipnlms=False, freeze_sigma_in_silence=False)}
def run(a):
    task, arm, off = a
    X, y = G.load(task); T = len(X); ts = int(.3 * T)
    sc = CausalStandardScaler(d=X.shape[1]); m = ARMS[arm](X.shape[1]); e = []
    for i in range(off, T):
        p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i])
        if i >= ts: e.append((y[i] - p) ** 2)
    return {"task_id": task, "arm": arm, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if np.all(np.isfinite(e)) else np.inf}
if __name__ == "__main__":
    jobs = [(t, a, o) for t in TASKS for a in ARMS for o in OFFSETS]
    with ProcessPoolExecutor(16) as ex: df = pd.DataFrame(list(ex.map(run, jobs, chunksize=2)))
    df.to_csv(os.path.join(HERE, "DEV_INSTAB.csv"), index=False)
    g = df.groupby(["task_id", "arm"]).nmse
    pd.set_option("display.width", 220)
    print("mediana\n" + g.median().unstack().round(4).to_string())
    ins = (g.quantile(.9) / g.quantile(.1)).unstack()
    print("p90/p10\n" + ins.round(2).to_string())
    w = df.pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
    for a in ARMS:
        print(f"{a:16s} geo/V032 {np.exp(np.log(w[a]/w.V032).mean()):.3f}  instab mediana {ins[a].median():.2f}  max {ins[a].max():.2f}")
