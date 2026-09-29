"""final6.py — the ONE measurement of evaluation set #6 (declared in DEV_LOG before the iteration), frozen code.
Configuration: measurement #4/#5 (final4.PADRAO, weekly memory on hourly buildings) with the base NLMS step mu = 0.05
(lower adaptation noise of the reference S). Sets: semi_synth6 SU0-SU4 (seeds 6601-6603), pure synthetics (9601-9603),
the NULL BATCH of criterion 7 (30 runs: white 6701-6715, heavy-tailed 6716-6730), real development tasks and the
1000-point protocol with the Chronos comparators."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronos_dev as CH  # noqa: E402
import data_v052 as D  # noqa: E402
import final4 as F4  # noqa: E402
import null_batch as NB  # noqa: E402
import semi_synth6 as S6  # noqa: E402

F4.S4 = S6                                                  # synthetic job of #4 pointed at set #6 (also in workers)
F4.PADRAO = dict(F4.PADRAO, mu=0.05)                        # the frozen configuration of this measurement
PADRAO = F4.PADRAO


def gmean(v):
    return round(float(np.exp(np.log(np.asarray(v, float)).mean())), 3)


if __name__ == "__main__":
    jobs = [("synth", t, s, mo) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9601, 9602, 9603) for mo in ("PADRAO", "ATOM")] + \
           [("semi6", t, s, mo) for t in S6.TRUTH for s in S6.SEEDS for mo in ("PADRAO", "ATOM")]
    njobs = [(k, s, PADRAO) for k, seeds in S6.NULL_SEEDS.items() for s in seeds]
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        SY = pd.DataFrame(list(ex.map(F4.syn_job, jobs, chunksize=1))); SY.to_csv(os.path.join(HERE, "FINAL6_SYNTH.csv"), index=False)
        NU = pd.DataFrame(list(ex.map(NB.job, njobs, chunksize=1))); NU.to_csv(os.path.join(HERE, "FINAL6_NULL.csv"), index=False)
        RE = list(ex.map(F4.real_job, tasks, chunksize=1))
    np.savez_compressed(os.path.join(HERE, "FINAL6_REAL_PREDS.npz"), **{t: pr for t, pr, _, _ in RE})
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []; ys = {t: D.load(t)["y"] for t in tasks}
    for task, pred, fp, st in RE:
        y = ys[task]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        mse = lambda p: float(np.mean((y[mask] - p[mask]) ** 2)); nl = mse(comp[f"{task}|NLINEAR_ONLINE"])
        rows.append({"task": task, "rel": mse(pred) / nl, "atom": mse(comp[f"{task}|v052"]) / nl, "fp": fp, "structure": st})
    RR = pd.DataFrame(rows); RR.to_csv(os.path.join(HERE, "FINAL6_REAL.csv"), index=False)
    P = pd.read_csv(os.path.join(HERE, "COMP_DEV_1000PTS.csv")); pts = []; preds = {t: pr for t, pr, _, _ in RE}
    for t in tasks:
        y = ys[t]; idx = CH.points(y); yt = y[idx]; ok = np.ones(len(idx), bool)
        for k in comp.files:
            if k.split("|")[0] == t and np.isfinite(comp[k][idx]).mean() > 0.95:
                ok &= np.isfinite(comp[k][idx])
        ok &= np.isfinite(preds[t][idx])
        assert int(ok.sum()) == int(P[P.task == t].n_points.iloc[0]), t
        var = float(np.var(yt[ok]))
        pts.append({"task": t, "model": "v052H", "nmse": float(np.mean((yt[ok] - preds[t][idx][ok]) ** 2) / var), "n_points": int(ok.sum())})
    A = pd.concat([P, pd.DataFrame(pts)]); A.to_csv(os.path.join(HERE, "FINAL6_1000PTS.csv"), index=False)
    pd.set_option("display.width", 250)
    print(SY.groupby(["suite", "task", "model"])[["nmse", "fp", "true_found", "n_true", "false_exo"]].agg(
        {"nmse": "mean", "fp": "mean", "true_found": "mean", "n_true": "mean", "false_exo": "sum"}).round(3))
    print(SY[SY.model != "ATOM"][["suite", "task", "seed", "structure", "groups_reported", "first_acc"]].to_string())
    print(NU[NU.n_acc > 0].to_string(index=False))
    print(f"NULL BATCH: runs with any accepted change {(NU.n_acc > 0).sum()} of {len(NU)} (criterion 7: <= 3)")
    for grp in ("ons", "camels", "bdg2", ""):
        q = RR[RR.task.str.startswith(grp)]
        print(f"{grp or 'ALL':7s} v052H {gmean(q.rel)} atom {gmean(q.atom)} fp {round(q.fp.mean())}")
    pv = A.pivot_table(index="task", columns="model", values="nmse")
    cols = ["v052H", "CHRONOS2_COV", "v052", "CHRONOS2", "ARX_NLMS", "AIRLINE_X"]
    for grp in ("ons", "camels", "bdg2", ""):
        q = pv[pv.index.str.startswith(grp)]
        print("1000pts", grp or "ALL", {m: gmean(q[m] / q["NLINEAR_ONLINE"]) for m in cols})
    print("v052H beats CHRONOS2_COV in", int((pv.v052H < pv.CHRONOS2_COV).sum()), "of", len(pv))
