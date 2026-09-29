"""tune_screen.py — development-only tuning of the screening threshold (screen_z) + memory check on ONS/BDG2 dev tasks."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_dev as R  # noqa: E402


def sj(a):
    opt, z, task, seed = a
    data = R.synth(task, seed)
    r = R.run_model("v052-" + opt, data, screen_z=z)
    final = set(eval(r["structure"]))
    truth = R.TRUTH[task]
    ev = [e for e in eval(r["events"])] if r["events"] != "[]" else []
    return {"opt": opt, "z": z, "task": task, "seed": seed, "nmse": r["nmse"], "experiments": r["experiments"],
            "true_found": len(final & truth), "n_truth": len(truth), "false_add": sum(1 for e in ev if e[3] and e[3] not in truth),
            "first_true": min([e[0] for e in ev if e[3] in truth], default=None), "fp": r["fp"]}


def mj(task):
    import data_v052 as D
    d = D.load(task)
    return {"task": task, **{k: R.run_model(k, d)["nmse"] for k in ("v051", "M", "v052-II", "v052-IIb")}}


if __name__ == "__main__":
    jobs = [(o, z, t, s) for o in ("II", "IIb") for z in (2.0, 3.0) for t in ("N1", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103)]
    import data_v052 as D
    mt = [t for t in D.dev_tasks() if t.startswith(("bdg2", "camels"))]
    with ProcessPoolExecutor(14) as ex:
        S = pd.DataFrame(list(ex.map(sj, jobs, chunksize=1)))
        M = pd.DataFrame(list(ex.map(mj, mt, chunksize=1)))
    S.to_csv(os.path.join(HERE, "TUNE_SCREEN.csv"), index=False); M.to_csv(os.path.join(HERE, "MEMCHECK.csv"), index=False)
    pd.set_option("display.width", 200)
    print(S.groupby(["opt", "z", "task"])[["nmse", "experiments", "true_found", "n_truth", "false_add", "first_true"]].mean().round(3))
    print(M.round(3))
