#!/usr/bin/env python3
"""heldout2_chronos.py — PRE-REGISTERED single run of Chronos-2 with covariates (the accuracy ceiling reference) on
RESERVA 2, protocol of chronos_dev.py: zero-shot, context 512, one-step median, 1000 evenly spaced observed test points;
inputs as past covariates and their current value as a known future covariate. Output: chronos/<series>.npz."""
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01")))
import chronos_dev as CH  # noqa: E402
import data_v052 as D  # noqa: E402
from heldout2_run import tasks  # noqa: E402

OUT = os.path.join(HERE, "chronos")

if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    os.makedirs(OUT, exist_ok=True)
    pipe = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
    for t in tasks():
        f = os.path.join(OUT, t.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")
        if os.path.exists(f):
            continue
        t0 = time.time(); d = D.load(t, final=True); idx = CH.points(d["y"])
        inp = CH.contexts(d["y"], idx, d["X"]); out = []
        for b in range(0, len(inp), 256):
            q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
            q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
            out.append(q.float().numpy())
        np.savez_compressed(f, idx=idx, CHRONOS2_COV=np.concatenate(out))
        print(f"CHRONOS2_COV {t:45s} {time.time() - t0:5.0f}s", flush=True)
