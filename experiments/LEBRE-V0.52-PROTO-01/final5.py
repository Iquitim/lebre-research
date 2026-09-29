"""final5.py — the ONE measurement of evaluation set #5 (declared in DEV_LOG before running): the frozen code and
configuration of measurement #4 (final4.PADRAO, weekly memory on hourly buildings), on semi_synth5 (SR0-SR4, seeds
6501-6503) and pure synthetics (seeds 9501-9503). The real development series repeat measurement #4 (deterministic model):
their predictions are compared bit by bit with FINAL4_REAL_PREDS.npz as an integrity check. Revised cost criterion:
mean over the real series <= 400 FP/step (per-step profile in COST_PROFILE_DEV.csv, same code and data)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import data_v052 as D  # noqa: E402
import final4 as F4  # noqa: E402
import semi_synth5 as S5  # noqa: E402

F4.S4 = S5                     # the synthetic job of measurement #4, pointed at set #5 (also in the worker processes)

if __name__ == "__main__":
    jobs = [("synth", t, s, mo) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9501, 9502, 9503) for mo in ("PADRAO", "ATOM")] + \
           [("semi5", t, s, mo) for t in S5.TRUTH for s in S5.SEEDS for mo in ("PADRAO", "ATOM")]
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        SY = pd.DataFrame(list(ex.map(F4.syn_job, jobs, chunksize=1)))
        SY.to_csv(os.path.join(HERE, "FINAL5_SYNTH.csv"), index=False)
        RE = list(ex.map(F4.real_job, tasks, chunksize=1))
    old = np.load(os.path.join(HERE, "FINAL4_REAL_PREDS.npz"))
    same = [bool(np.array_equal(pr, old[t], equal_nan=True)) for t, pr, _, _ in RE]
    fps = np.array([fp for _, _, fp, _ in RE])
    pd.set_option("display.width", 250)
    print(SY.groupby(["suite", "task", "model"])[["nmse", "fp", "true_found", "n_true", "false_exo"]].agg(
        {"nmse": "mean", "fp": "mean", "true_found": "mean", "n_true": "mean", "false_exo": "sum"}).round(3))
    print(SY[SY.model != "ATOM"][["suite", "task", "seed", "structure", "groups_reported", "first_acc"]].to_string())
    print(f"real series: predictions identical to measurement #4 in {sum(same)} of {len(same)}; mean FP over series {fps.mean():.0f} (<= 400?)")
    cp = pd.read_csv(os.path.join(HERE, "COST_PROFILE_DEV.csv"))
    print("per-series profile (same code/data): mean", round(cp["mean"].min()), "-", round(cp["mean"].max()),
          "| p99.9", round(cp.p999.min()), "-", round(cp.p999.max()), "| max", round(cp["max"].max()),
          "| series with mean > ARX:", int((cp["mean/arx"] > 1).sum()), "of", len(cp))
