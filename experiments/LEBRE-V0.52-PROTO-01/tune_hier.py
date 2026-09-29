"""tune_hier.py — dev-only tuning of the hierarchical v0.52 on the OLD development sets only
(pure synthetics seeds 9101-9103, semi-synthetics SS0-SS4 seeds 6101-6103)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eval_unit as E  # noqa: E402
CFGS = eval(open(sys.argv[1], encoding="utf-8").read()) if len(sys.argv) > 1 else {"meas2": {}}
OUT = sys.argv[2] if len(sys.argv) > 2 else "TUNE_HIER_X.csv"
if __name__ == "__main__":
    jobs = [("synth", t, s, "hier", kw) for t in ("N1", "N2", "T1", "B1", "B2", "B3") for s in (9101, 9102, 9103) for kw in CFGS.values()] + \
           [("semi", t, s, "hier", kw) for t in ("SS0", "SS1", "SS2", "SS3", "SS4") for s in (6101, 6102, 6103) for kw in CFGS.values()]
    names = {str(v): k for k, v in CFGS.items()}
    with ProcessPoolExecutor(15) as ex:
        rows = list(ex.map(E.job, jobs, chunksize=1))
    for r, j in zip(rows, jobs):
        r["cfg"] = names[str(j[4])]
    D = pd.DataFrame(rows); D.to_csv(os.path.join(HERE, OUT), index=False)
    pd.set_option("display.width", 220)
    for v in ("nmse", "true_exo", "false_exo", "fp"):
        print(v); print(D.pivot_table(index=["suite", "task"], columns="cfg", values=v, aggfunc="sum" if v == "false_exo" else "mean").round(3))
