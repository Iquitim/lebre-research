"""posthoc_ablation.py — POST-HOC (not pre-registered): which v0.4 mechanism causes the BENCH-04 regression vs v0.3.2?
The frozen lebre_v042.py is used unchanged; only constructor switches differ. Same harness and tasks as BENCH-04."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), os.path.join(ROOT, "data", "external_bench04")):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from load04 import TASKS, load  # noqa: E402

VARIANTS = {"V042_FULL": {}, "NO_IPNLMS": {"ipnlms": False}, "IP_ALPHA_0.5": {"ip_alpha": 0.5},
            "GAIN_EVERY_10": {"gain_every": 10}, "NO_CLIP": {"clip": False},
            "NO_FREEZE_SIGMA": {"freeze_sigma_in_silence": False},
            "ALL_OFF": {"ipnlms": False, "clip": False, "freeze_sigma_in_silence": False}}


class S(B.Step):
    def __init__(self, d, kw):
        self.m = LebreV042(d=d, **kw)

    def step(self, x, y):
        return self.m.step(np.asarray(x, float), float(y)), 0.0


def run(args):
    task, v = args
    X, y, _, _, _, _ = load(task)
    m = B.LebreStep(X.shape[1]) if v == "V032" else S(X.shape[1], VARIANTS[v])
    r = B.R.run_full_stream(m, X, y, int(0.30 * len(X)), is_track_b=True)
    return {"task_id": task, "variant": v, "nmse": r["nmse"], "status": r["status"]}


if __name__ == "__main__":
    jobs = [(t, v) for t in TASKS for v in list(VARIANTS) + ["V032"]]
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(run, jobs)))
    df.to_csv(os.path.join(HERE, "POSTHOC_ABLATION.csv"), index=False)
    p = df.pivot(index="task_id", columns="variant", values="nmse")[list(VARIANTS) + ["V032"]]
    pd.set_option("display.width", 220)
    print(p.round(4).to_string())
    g = np.exp(np.log(p.div(p["V032"], axis=0)).mean())
    print("\nrazao geometrica vs V032:\n" + g.round(3).to_string())
    print("\nstatus nao-SUCCESS:", int((df.status != "SUCCESS").sum()))
