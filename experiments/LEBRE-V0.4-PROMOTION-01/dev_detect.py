"""DEV-only: switching latency, detection delay, I7, NMSE and FP for candidate variants (seeds 3301..3310)."""
import os, sys, numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (ROOT, HERE, os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")): sys.path.insert(0, p)
from scratch.bench_v02_integration import generate_v02_stream, BENCHMARK_TASKS
from lebre_v032 import LebreV032
from lebre_v04 import LebreV04
from lebre_v041 import LebreV041
from lebre_v042 import LebreV042
V = {"V032": lambda: LebreV032(d=5), "V04": lambda: LebreV04(d=5),
     "blk_g50": lambda: LebreV041(d=5), "blk_g20": lambda: LebreV041(d=5, gain_every=20),
     "blk_g50_noPfreeze": lambda: LebreV041(d=5, freeze_power_in_silence=False),
     "mat16_g50": lambda: LebreV041(d=5, evidence_mode="mature"), "mat4_g50": lambda: LebreV041(d=5, evidence_mode="mature", mature_every=4, interval_every=2),
     "V041_final": lambda: LebreV041(d=5), "V041_m2": lambda: LebreV041(d=5, mature_every=2),
     "V042": lambda: LebreV042(d=5), "V042_m2": lambda: LebreV042(d=5, mature_every=2),
     "V042_m2_g100_i8": lambda: LebreV042(d=5, mature_every=2, gain_every=100, interval_every=8),
     "V042_m2_g100_i4": lambda: LebreV042(d=5, mature_every=2, gain_every=100)}
CH = {"I5_Moving_Delay_Support": [3000], "I11_Regime_Switch_Delay_To_Latent": [3000], "I12_Regime_Switch_Latent_To_Delay": [3000],
      "I13_Regime_Switch_Hybrid_To_Memoryless": [3000], "I14_Intermittent_Hybrid": [1500, 3000, 4500]}
def run(a):
    task, seed, v = a
    X, y, _ = generate_v02_stream(task, seed=seed); m = V[v](); err = np.empty(6000); fp0 = 0
    for t in range(6000): err[t] = y[t] - m.step(X[t], float(y[t]))
    o = {"task": task, "seed": seed, "v": v, "nmse": float(np.mean(err**2)/np.var(y)), "fp": sum(m.fp.values())/6000}
    if task in CH:
        ev = [e[0] for e in m.events]; o["delay"] = float(np.mean([min([t-c for t in ev if t >= c] or [3000]) for c in CH[task]]))
        roll = np.convolve(err[3000:]**2, np.ones(100)/100, mode="valid"); idx = np.where(roll <= 0.15*np.var(y[3000:]))[0]
        o["switch"] = float(idx[0]+100) if len(idx) else 3000.0
    return o
SEEDS = [int(x) for x in os.environ.get("DEV_SEEDS", "3301-3310").split("-")]
SEEDS = list(range(SEEDS[0], SEEDS[1] + 1))
if __name__ == "__main__":
    vs = sys.argv[1].split(",")
    jobs = [(t, s, v) for t in BENCHMARK_TASKS for s in SEEDS for v in vs]
    with ProcessPoolExecutor(16) as ex: d = pd.DataFrame(list(ex.map(run, jobs, chunksize=4)))
    pd.set_option("display.width", 200)
    g = d.groupby("v").agg(nmse=("nmse","mean"), fp=("fp","mean"), delay=("delay","mean"))
    g["I7_nmse"] = d[d.task.str.startswith("I7")].groupby("v").nmse.mean()
    g["I4_nmse"] = d[d.task.str.startswith("I4")].groupby("v").nmse.mean()
    sw = d.pivot_table(index="v", columns="task", values="switch"); sw.columns=[c[:3] for c in sw.columns]
    print(g.join(sw).round(3).to_string())
