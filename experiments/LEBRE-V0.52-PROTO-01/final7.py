"""final7.py — the ONE measurement of evaluation set #7 (declared in DEV_LOG before the iteration), frozen code.
Configuration: measurement #6 (final6.PADRAO: #4 + base mu = 0.05) + cost-peak control: staggered warm-ups, spread
screen, split peak-lag statistic (peak_until = 200, chal_warm = 250). Sets: semi_synth7 SW0-SW4 (6801-6803), pure
synthetics (9701-9703), NULL BATCH (6901-6930), real development tasks with the per-step cost profile (criterion 8:
max per-step FP <= 1000) and the 1000-point protocol with the Chronos comparators."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronos_dev as CH  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
import final4 as F4  # noqa: E402
import null_batch as NB  # noqa: E402
import semi_synth7 as S7  # noqa: E402

F4.S4 = S7
F4.PADRAO = dict(F4.PADRAO, mu=0.05, stagger=True, screen_spread=True, peak_split=True, peak_until=200, chal_warm=250)
PADRAO = F4.PADRAO


def real_job(task):
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    kw = dict(PADRAO)
    if task.startswith("bdg2"):
        kw["season2"] = 168
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.empty(len(y)); c = np.empty(len(y)); prev = 0.0
    for t in range(len(y)):
        pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        tot = m.fp_total(); c[t] = tot - prev; prev = tot
    return task, pred, c.mean(), str(m.structure()), float(np.percentile(c, 99.9)), float(c.max()), 144 + 132 * X.shape[1]


def gmean(v):
    return round(float(np.exp(np.log(np.asarray(v, float)).mean())), 3)


if __name__ == "__main__":
    jobs = [("synth", t, s, mo) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9701, 9702, 9703) for mo in ("PADRAO", "ATOM")] + \
           [("semi7", t, s, mo) for t in S7.TRUTH for s in S7.SEEDS for mo in ("PADRAO", "ATOM")]
    njobs = [(k, s, PADRAO) for k, seeds in S7.NULL_SEEDS.items() for s in seeds]
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        SY = pd.DataFrame(list(ex.map(F4.syn_job, jobs, chunksize=1))); SY.to_csv(os.path.join(HERE, "FINAL7_SYNTH.csv"), index=False)
        NU = pd.DataFrame(list(ex.map(NB.job, njobs, chunksize=1))); NU.to_csv(os.path.join(HERE, "FINAL7_NULL.csv"), index=False)
        RE = list(ex.map(real_job, tasks, chunksize=1))
    np.savez_compressed(os.path.join(HERE, "FINAL7_REAL_PREDS.npz"), **{r[0]: r[1] for r in RE})
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []; ys = {t: D.load(t)["y"] for t in tasks}
    for task, pred, fp, st, p999, mx, arx in RE:
        y = ys[task]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        mse = lambda p: float(np.mean((y[mask] - p[mask]) ** 2)); nl = mse(comp[f"{task}|NLINEAR_ONLINE"])
        rows.append({"task": task, "rel": mse(pred) / nl, "atom": mse(comp[f"{task}|v052"]) / nl, "fp": fp, "p999": p999, "max": mx,
                     "arx": arx, "structure": st})
    RR = pd.DataFrame(rows); RR.to_csv(os.path.join(HERE, "FINAL7_REAL.csv"), index=False)
    P = pd.read_csv(os.path.join(HERE, "COMP_DEV_1000PTS.csv")); pts = []; preds = {r[0]: r[1] for r in RE}
    for t in tasks:
        y = ys[t]; idx = CH.points(y); yt = y[idx]; ok = np.ones(len(idx), bool)
        for k in comp.files:
            if k.split("|")[0] == t and np.isfinite(comp[k][idx]).mean() > 0.95:
                ok &= np.isfinite(comp[k][idx])
        ok &= np.isfinite(preds[t][idx])
        assert int(ok.sum()) == int(P[P.task == t].n_points.iloc[0]), t
        var = float(np.var(yt[ok]))
        pts.append({"task": t, "model": "v052H", "nmse": float(np.mean((yt[ok] - preds[t][idx][ok]) ** 2) / var), "n_points": int(ok.sum())})
    A = pd.concat([P, pd.DataFrame(pts)]); A.to_csv(os.path.join(HERE, "FINAL7_1000PTS.csv"), index=False)
    pd.set_option("display.width", 250)
    print(SY.groupby(["suite", "task", "model"])[["nmse", "fp", "true_found", "n_true", "false_exo"]].agg(
        {"nmse": "mean", "fp": "mean", "true_found": "mean", "n_true": "mean", "false_exo": "sum"}).round(3))
    print(SY[SY.model != "ATOM"][["suite", "task", "seed", "structure", "groups_reported", "first_acc"]].to_string())
    print(NU[NU.n_acc > 0].to_string(index=False))
    print(f"NULL BATCH: runs with any accepted change {(NU.n_acc > 0).sum()} of {len(NU)} (criterion 7: <= 3)")
    for grp in ("ons", "camels", "bdg2", ""):
        q = RR[RR.task.str.startswith(grp)]
        print(f"{grp or 'ALL':7s} v052H {gmean(q.rel)} atom {gmean(q.atom)} fp {round(q.fp.mean())} p99.9max {round(q.p999.max())} max {round(q['max'].max())}")
    pv = A.pivot_table(index="task", columns="model", values="nmse")
    cols = ["v052H", "CHRONOS2_COV", "v052", "CHRONOS2", "ARX_NLMS", "AIRLINE_X"]
    for grp in ("ons", "camels", "bdg2", ""):
        q = pv[pv.index.str.startswith(grp)]
        print("1000pts", grp or "ALL", {m: gmean(q[m] / q["NLINEAR_ONLINE"]) for m in cols})
    print("v052H beats CHRONOS2_COV in", int((pv.v052H < pv.CHRONOS2_COV).sum()), "of", len(pv))
