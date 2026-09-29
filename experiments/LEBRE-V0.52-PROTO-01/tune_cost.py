"""tune_cost.py — dev-only check of cost/power changes (test_every, decide_every, init_from_screen) on synthetic tasks."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_dev as R  # noqa: E402

CONFIGS = {"raw": dict(screen_norm=None), "ema": dict(screen_norm="ema"), "analytic": dict(screen_norm="analytic")}


def sj(a):
    cfg, task, seed = a
    data = R.synth(task, seed)
    r = R.run_model("v052-IIb", data, **CONFIGS[cfg])
    final = set(eval(r["structure"])); truth = R.TRUTH[task]
    ev = eval(r["events"]) if r["events"] != "[]" else []
    return {"cfg": cfg, "task": task, "seed": seed, "nmse": r["nmse"], "fp": r["fp"], "true_found": len(final & truth),
            "n_truth": len(truth), "false_add": sum(1 for e in ev if e[3] and e[3] not in truth),
            "first_true": min([e[0] for e in ev if e[3] in truth], default=None)}


if __name__ == "__main__":
    jobs = [(c, t, s) for c in CONFIGS for t in ("N1", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103, 9104, 9105)]
    with ProcessPoolExecutor(14) as ex:
        S = pd.DataFrame(list(ex.map(sj, jobs, chunksize=1)))
    S.to_csv(os.path.join(HERE, "TUNE_SCREENNORM.csv"), index=False)
    pd.set_option("display.width", 200)
    print(S.groupby(["cfg", "task"])[["nmse", "fp", "true_found", "n_truth", "false_add", "first_true"]].mean().round(3))
