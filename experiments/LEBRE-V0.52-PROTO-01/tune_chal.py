"""tune_chal.py — dev-only: challenger coefficient learner (nlms vs rls2) and evidence warm-up, on the pure synthetics
(including the nulls) and on the semi-synthetics with real inputs."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, run_dev as R, semi_synth as SS  # noqa: E402

CFGS = {"nlms/0": dict(chal="nlms"), "pw/nlms": dict(screen_norm="prewhite"),
        "pw/rls2": dict(screen_norm="prewhite", chal="rls2"),
        "pw/rls2P": dict(screen_norm="prewhite", chal="rls2", chal_persist=True, chal_forget=0.9995)}

def job(a):
    suite, task, seed, cfg = a
    if suite == "synth":
        data = R.synth(task, seed); r = R.run_model("v052-IIb", data, **CFGS[cfg]); truth = R.TRUTH[task]
        self_idx = data["X"].shape[1]; ev = eval(r["events"]) if r["events"] != "[]" else []; final = set(eval(r["structure"]))
        nmse = r["nmse"]
    else:
        from lebre_v052 import LebreV052
        X = SS.inputs(); y = SS.generate(task, seed, X); Xs = C._scaled_inputs(X); self_idx = X.shape[1]
        m = LebreV052(d=X.shape[1], season=8 if task == "SS4" else None, **CFGS[cfg])
        pred = np.array([m.step(Xs[t], float(y[t])) for t in range(len(y))]); ts = int(0.3 * len(y))
        nmse = float(np.mean((y[ts:] - pred[ts:]) ** 2) / np.var(y[ts:])); truth = SS.TRUTH[task]
        ev = [e for e in m.events if e[1] == "accepted"]; final = set(m.structure())
    is_self = lambda k: k is not None and k[0] in ("lag", "lp") and k[1] == self_idx
    return {"suite": suite, "task": task, "seed": seed, "cfg": cfg, "nmse": nmse, "true_found": len(final & truth),
            "n_truth": len(truth), "false_exog": sum(1 for e in ev if e[1] == "accepted" and e[3] and e[3] not in truth and not is_self(e[3])),
            "structure": str(sorted(final))}

if __name__ == "__main__":
    jobs = [("synth", t, s, c) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103) for c in CFGS] + \
           [("semi", t, s, c) for t in ("SS0", "SS1", "SS2", "SS3", "SS4") for s in (6101, 6102, 6103) for c in CFGS]
    with ProcessPoolExecutor(15) as ex:
        D = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    D.to_csv(os.path.join(HERE, "TUNE_CHAL_3.csv"), index=False)
    pd.set_option("display.width", 220)
    print(D.pivot_table(index=["suite", "task"], columns="cfg", values="nmse").round(3))
    print(D.pivot_table(index=["suite", "task"], columns="cfg", values="true_found").round(2))
    print(D.pivot_table(index=["suite", "task"], columns="cfg", values="false_exog", aggfunc="sum"))
