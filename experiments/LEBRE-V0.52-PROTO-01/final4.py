"""final4.py — the ONE measurement of evaluation set #4 (declared in DEV_LOG before the iteration), frozen code.
Profile PADRAO (#3) + screen_skip_active + track_groups + weekly memory (season2 = 168 on the hourly building series).
Equivalence groups for the criteria: full-sample |corr| >= 0.95 between raw inputs (semi_synth4.groups).
Sets: pure synthetics seeds 9401-9403; semi_synth4 SQ0-SQ4 seeds 6401-6403; real development tasks (COMP_DEV mask) and
the 1000-point protocol with the Chronos comparators. Atomic v0.52 (default) on the same synthetic sets."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronos_dev as CH  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
import run_dev as R  # noqa: E402
import semi_synth4 as S4  # noqa: E402

PADRAO = dict(scale_floor=0.1, peak_persist=True, evidence="psiE1", lazy_halves=True, screen_skip_active=True,
              track_groups=True)


def units(keys):
    return {("res",) if k[0] == "res" else ("in", k[1]) for k in keys}


def syn_job(a):
    suite, task, seed, model = a
    if suite == "synth":
        d_ = R.synth(task, seed); X, y = d_["X"], d_["y"]; Xs = X; tu = units(R.TRUTH[task])
    else:
        X = S4.inputs(); y = S4.generate(task, seed, X); Xs = C._scaled_inputs(X); tu = set(S4.TRUTH[task])
    self_i = X.shape[1]; grp = S4.groups(X)
    if model == "ATOM":
        from lebre_v052 import LebreV052
        m = LebreV052(d=X.shape[1])
    else:
        from lebre_v052h import LebreV052H
        m = LebreV052H(d=X.shape[1], **PADRAO)
    pred = np.array([m.step(Xs[t], float(y[t])) for t in range(len(y))]); ts = int(0.3 * len(y))
    acc = [e for e in m.events if e[1] == "accepted"]; fu = units(m.structure())
    acc_units = set().union(*[units([e[3]]) for e in acc if e[3]]) if acc else set()
    tex = {u[1] for u in tu if u[0] == "in" and u[1] != self_i}                 # true exogenous inputs
    ok_group = set().union(*[grp[i] for i in tex]) if tex else set()           # true inputs and their groups
    fin = {u[1] for u in fu if u[0] == "in" and u[1] != self_i}
    accx = {u[1] for u in acc_units if u[0] == "in" and u[1] != self_i}
    reported = {str(u): sorted(m.equivalents(u)) for u in fu if u[0] == "in"} if model != "ATOM" else {}
    return {"suite": suite, "task": task, "seed": seed, "model": model,
            "nmse": float(np.mean((y[ts:] - pred[ts:]) ** 2) / np.var(y[ts:])), "fp": m.fp_total() / len(y),
            "true_found": sum(1 for i in tex if grp[i] & fin), "n_true": len(tex),
            "false_exo": len(accx - ok_group), "structure": str(sorted(fu)), "groups_reported": str(reported),
            "first_acc": acc[0][0] if acc else None}


def real_job(task):
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    kw = dict(PADRAO)
    if task.startswith("bdg2"):
        kw["season2"] = 168                                          # hourly buildings: the week, declared like the day
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    return task, pred, m.fp_total() / len(y), str(m.structure())


def gmean(v):
    return round(float(np.exp(np.log(np.asarray(v, float)).mean())), 3)


if __name__ == "__main__":
    jobs = [("synth", t, s, mo) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9401, 9402, 9403) for mo in ("PADRAO", "ATOM")] + \
           [("semi4", t, s, mo) for t in S4.TRUTH for s in S4.SEEDS for mo in ("PADRAO", "ATOM")]
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        SY = pd.DataFrame(list(ex.map(syn_job, jobs, chunksize=1)))
        SY.to_csv(os.path.join(HERE, "FINAL4_SYNTH.csv"), index=False)
        RE = list(ex.map(real_job, tasks, chunksize=1))
    np.savez_compressed(os.path.join(HERE, "FINAL4_REAL_PREDS.npz"), **{t: pr for t, pr, _, _ in RE})
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []; ys = {t: D.load(t)["y"] for t in tasks}
    for task, pred, fp, st in RE:
        y = ys[task]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        mse = lambda p: float(np.mean((y[mask] - p[mask]) ** 2)); nl = mse(comp[f"{task}|NLINEAR_ONLINE"])
        rows.append({"task": task, "rel": mse(pred) / nl, "atom": mse(comp[f"{task}|v052"]) / nl, "fp": fp, "structure": st})
    RR = pd.DataFrame(rows); RR.to_csv(os.path.join(HERE, "FINAL4_REAL.csv"), index=False)
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
    A = pd.concat([P, pd.DataFrame(pts)]); A.to_csv(os.path.join(HERE, "FINAL4_1000PTS.csv"), index=False)
    pd.set_option("display.width", 250)
    print(SY.groupby(["suite", "task", "model"])[["nmse", "fp", "true_found", "n_true", "false_exo"]].agg(
        {"nmse": "mean", "fp": "mean", "true_found": "mean", "n_true": "mean", "false_exo": "sum"}).round(3))
    print(SY[SY.model != "ATOM"][["suite", "task", "seed", "structure", "groups_reported", "first_acc"]].to_string())
    for grp in ("ons", "camels", "bdg2", ""):
        q = RR[RR.task.str.startswith(grp)]
        print(f"{grp or 'ALL':7s} v052H {gmean(q.rel)} atom {gmean(q.atom)} fp {round(q.fp.mean())}")
    pv = A.pivot_table(index="task", columns="model", values="nmse")
    cols = ["v052H", "CHRONOS2_COV", "v052", "CHRONOS2", "ARX_NLMS", "AIRLINE_X"]
    for grp in ("ons", "camels", "bdg2", ""):
        q = pv[pv.index.str.startswith(grp)]
        print("1000pts", grp or "ALL", {m: gmean(q[m] / q["NLINEAR_ONLINE"]) for m in cols})
    print("v052H beats CHRONOS2_COV in", int((pv.v052H < pv.CHRONOS2_COV).sum()), "of", len(pv))
