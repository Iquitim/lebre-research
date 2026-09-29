"""ttm_tune_dev.py — DEVELOPMENT-ONLY: fairer TTM fine-tuning (lr 1e-4, up to 30 epochs, early stopping inside the
calibration segment) vs the first configuration and zero-shot, on 9 development series (1000-point protocol)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, HERE)
import chronos_dev as CH, comp_dev as C, data_v052 as D
TASKS = ["ons:ITUTINGA", "ons:IGARAPAVA", "ons:MARIMBONDO", "camels:17350000", "camels:61510000", "camels:71350001",
         "bdg2:chilledwater:Bull_education_Hayley", "bdg2:steam:Hog_education_Luvenia", "bdg2:hotwater:Moose_education_Lori"]
def job(task):
    import torch; torch.set_num_threads(3)
    import ttm_run as TT
    d = D.load(task); X, y = d["X"], d["y"]; Xs = C._scaled_inputs(X); idx = C._calib_n(y); pts = CH.points(y)
    a = TT.run(Xs, y, idx, pts); b = TT.run(Xs, y, idx, pts, lr=1e-4, epochs=30, early_stop=True)
    comp = np.load(os.path.join(PROTO, "COMP_DEV_PREDS.npz")); nl = comp[f"{task}|NLINEAR_ONLINE"][pts]; yt = y[pts]
    ok = np.isfinite(yt) & np.isfinite(nl); e = lambda p: float(np.mean((yt[ok] - p[ok]) ** 2) / np.mean((yt[ok] - nl[ok]) ** 2))
    return {"task": task, "ZS": e(a["TTM_ZS"][0]), "FT_v1": e(a["TTM_FT_EXOG"][0]), "FT_v2": e(b["TTM_FT_EXOG"][0])}
if __name__ == "__main__":
    with ProcessPoolExecutor(5) as ex:
        R = pd.DataFrame(list(ex.map(job, TASKS)))
    R.to_csv(os.path.join(HERE, "TTM_TUNE_DEV.csv"), index=False); print(R.round(3).to_string(index=False))
    print({c: round(float(np.exp(np.log(R[c]).mean())), 3) for c in ("ZS", "FT_v1", "FT_v2")})
