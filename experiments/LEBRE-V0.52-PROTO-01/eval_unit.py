"""eval_unit.py — dev-only: input-level hypotheses (lebre_v052u) vs the atomic v0.52, on the pure synthetics (with nulls)
and the semi-synthetics with real inputs. Truth mapped to units: any atom of input i -> ("in", i); residual atoms -> ("res",)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, run_dev as R, semi_synth as SS, semi_synth2 as SS2  # noqa: E402

def to_units(keys):
    return {("res",) if k[0] == "res" else ("in", k[1]) for k in keys}

def job(a):
    suite, task, seed, model, kw = a
    if suite == "synth":
        d_ = R.synth(task, seed); X, y = d_["X"], d_["y"]; Xs = X; truth = R.TRUTH[task]; season = None
    elif suite == "semi2":                                            # declared evaluation set (new structures, new seeds)
        X = SS2.inputs(); y = SS2.generate(task, seed, X); Xs = C._scaled_inputs(X); season = None
        truth = {(("res", 0.8) if u[0] == "res" else ("lag", u[1], 1)) for u in SS2.TRUTH[task]}   # unit-level truth
    else:
        X = SS.inputs(); y = SS.generate(task, seed, X); Xs = C._scaled_inputs(X); truth = SS.TRUTH[task]
        season = 8 if task == "SS4" else None
    if model == "atom":
        from lebre_v052 import LebreV052
        m = LebreV052(d=X.shape[1], season=season, **kw)
    elif model == "hier":
        from lebre_v052h import LebreV052H
        m = LebreV052H(d=X.shape[1], season=season, **{k: v for k, v in kw.items() if k != "weekly"})
    else:
        from lebre_v052u import LebreV052U
        m = LebreV052U(d=X.shape[1], season=season, **kw)
    pred = np.array([m.step(Xs[t], float(y[t])) for t in range(len(y))]); ts = int(0.3 * len(y))
    self_i = X.shape[1]
    tu = to_units(truth); fu = to_units(m.structure()); acc = [e for e in m.events if e[1] == "accepted"]
    exo = lambda u: u[0] == "in" and u[1] != self_i
    return {"suite": suite, "task": task, "seed": seed, "model": model,
            "nmse": float(np.mean((y[ts:] - pred[ts:]) ** 2) / np.var(y[ts:])), "fp": m.fp_total() / len(y),
            "true_units": len(fu & tu), "n_true": len(tu), "true_exo": len({u for u in fu & tu if exo(u)}),
            "n_true_exo": len({u for u in tu if exo(u)}),
            "false_exo": len({u for u in (to_units([e[3]]) if e[3] else set() for e in acc) for u in u if exo(u) and u not in tu}),
            "first_acc": acc[0][0] if acc else None, "structure": str(sorted(fu)),
            "response": str({u: [(sg, round(w, 2)) for sg, w in m.response(u)] for u in m.active if u[0] == "in"}) if model == "hier" else "",
            "fp_parts": str({k: round(v / len(y)) for k, v in m.fp.items()}) + f" mem {m.M.fp / len(y):.0f} eng {m.engine.fp / len(y):.0f}"}

if __name__ == "__main__":
    kw = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
    out = sys.argv[2] if len(sys.argv) > 2 else "EVAL_UNIT.csv"
    models = [a for a in ("unit", "hier", "atom") if "--" + a in sys.argv] or ["hier"]
    if "--final" in sys.argv:                                        # the declared evaluation set, measured once
        jobs = [("synth", t, s, mo, {}) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9201, 9202, 9203) for mo in models] + \
               [("semi2", t, s, mo, {}) for t in ("SN0", "SN1", "SN2", "SN3", "SN4") for s in SS2.SEEDS for mo in models]
    else:
        jobs = [("synth", t, s, mo, kw if mo == "hier" else {}) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103) for mo in models] + \
               [("semi", t, s, mo, kw if mo == "hier" else {}) for t in ("SS0", "SS1", "SS2", "SS3", "SS4") for s in (6101, 6102, 6103) for mo in models]
    with ProcessPoolExecutor(15) as ex:
        D = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    D.to_csv(os.path.join(HERE, out), index=False)
    pd.set_option("display.width", 220)
    print(D.groupby(["suite", "task", "model"])[["nmse", "fp", "true_exo", "n_true_exo", "true_units", "n_true", "false_exo"]].mean().round(3))
    print(D[D.model == "hier"][["task", "seed", "structure", "first_acc", "response"]].to_string(max_colwidth=120))
