"""eval_synth.py — synthetic development check of the CURRENT defaults (safety + structure), 5 seeds x 6 tasks.
Truth keys refer to the exogenous inputs; with self_input the target's own past is input index d (not part of the truth)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_dev as R  # noqa: E402


def job(a):
    task, seed = a
    data = R.synth(task, seed)
    r = R.run_model("v052-IIb", data)
    final = set(eval(r["structure"])); truth = R.TRUTH[task]
    ev = eval(r["events"]) if r["events"] != "[]" else []
    self_idx = data["X"].shape[1]
    is_self = lambda k: k is not None and k[0] in ("lag", "lp") and k[1] == self_idx
    return {"task": task, "seed": seed, "nmse": r["nmse"], "fp": r["fp"], "true_found": len(final & truth), "n_truth": len(truth),
            "false_exog": sum(1 for e in ev if e[3] and e[3] not in truth and not is_self(e[3])),
            "self_atoms": sum(1 for k in final if is_self(k)),
            "first_true": min([e[0] for e in ev if e[3] in truth], default=None), "structure": r["structure"]}


if __name__ == "__main__":
    jobs = [(t, s) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103, 9104, 9105)]
    with ProcessPoolExecutor(14) as ex:
        S = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    S.to_csv(os.path.join(HERE, "EVAL_SYNTH.csv"), index=False)
    pd.set_option("display.width", 200)
    print(S.groupby("task")[["nmse", "fp", "true_found", "n_truth", "false_exog", "self_atoms", "first_true"]].mean().round(3))
