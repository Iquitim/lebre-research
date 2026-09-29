#!/usr/bin/env python3
"""heldout3_ttm_chronos.py — PRE-REGISTERED single run of the small and large foundation-model references on RESERVA 3,
1000-point protocol (chronos_dev.points): TTM zero-shot (univariate) and TTM fine-tuned on the calibration segment with the
inputs as exogenous channels (ttm_run.run defaults: lr 1e-3, 5 epochs — the better of the two configurations tried on
development data), and Chronos-2 with covariates (past covariates + current inputs as known future covariates).
Outputs: fm/<series>.npz (idx + predictions + FLOPs per forecast)."""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-EXT-01"))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, EXT); sys.path.insert(0, HERE)
import chronos_dev as CH  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
from heldout3_run import tasks  # noqa: E402

OUT = os.path.join(HERE, "fm")


def fn(t):
    return os.path.join(OUT, t.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")


def ttm_job(task):
    import torch
    torch.set_num_threads(3)
    import ttm_run as TT
    d = D.load(task, final=True); X, y = d["X"], d["y"]; Xs = C._scaled_inputs(X)
    pts = CH.points(y); r = TT.run(Xs, y, C._calib_n(y), pts)
    return task, pts, {k: v[0] for k, v in r.items()}, {k: v[1] for k, v in r.items()}


if __name__ == "__main__":
    import torch
    os.makedirs(OUT, exist_ok=True)
    ts = tasks(); t0 = time.time()
    with ProcessPoolExecutor(5) as ex:
        res = {t: (p, pr, fl) for t, p, pr, fl in ex.map(ttm_job, ts, chunksize=1)}
    print(f"TTM done {time.time() - t0:.0f}s", flush=True)
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    pipe = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
    for t in ts:
        d = D.load(t, final=True); pts, pr, fl = res[t]
        inp = CH.contexts(d["y"], pts, d["X"]); out = []
        for b in range(0, len(inp), 256):
            q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
            q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
            out.append(q.float().numpy())
        np.savez_compressed(fn(t), idx=pts, CHRONOS2_COV=np.concatenate(out), **pr, **{f"flops_{k}": np.array(v) for k, v in fl.items()})
        print("CHRONOS2_COV", t, flush=True)
