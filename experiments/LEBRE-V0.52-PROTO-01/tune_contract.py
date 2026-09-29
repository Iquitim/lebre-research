"""tune_contract.py — dev-only: effect of the P6 input-contract quarantine on the real development tasks."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_dev as R  # noqa: E402
import data_v052 as D  # noqa: E402


def job(a):
    task, ic = a
    r = R.run_model("v052-IIb", D.load(task), input_contract=ic)
    return {"task": task, "contract": ic, "nmse": r["nmse"], "structure": r["structure"]}


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(14) as ex:
        df = pd.DataFrame(list(ex.map(job, [(t, c) for t in tasks for c in (False, True)], chunksize=1)))
    df.to_csv(os.path.join(HERE, "TUNE_CONTRACT.csv"), index=False)
    base = pd.read_csv(os.path.join(HERE, "DEV_REAL.csv")); v51 = base[base.model == "v051"].set_index("task").nmse
    p = df.pivot_table(index="task", columns="contract", values="nmse"); p["v051"] = v51
    pd.set_option("display.width", 200)
    print(p.round(4))
    for grp in ("ons", "camels", "bdg2", ""):
        q = p[p.index.str.startswith(grp)]
        print(grp or "ALL", {c: round(float(np.exp(np.log(q[c] / q["v051"]).mean())), 3) for c in (False, True)})
