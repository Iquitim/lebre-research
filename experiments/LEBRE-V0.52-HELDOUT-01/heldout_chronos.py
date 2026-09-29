#!/usr/bin/env python3
"""heldout_chronos.py — PRE-REGISTERED single run of the foundation-model comparators on the HELD-OUT series, with the
protocol of the development comparison (chronos_dev.py): zero-shot, context = last 512 targets before t, one-step median,
1000 evenly spaced observed test points (test region from 30%). CHRONOS2_COV receives the inputs as past covariates over
the same window and their CURRENT value as a known future covariate (the information of the online models).
Models: Chronos-2 with covariates, Chronos-2 univariate, Chronos-Bolt small. Output: chronos/<series>.npz (idx + preds)."""
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01")))
import chronos_dev as CH  # noqa: E402
import data_v052 as D  # noqa: E402
from heldout_run import heldout_tasks  # noqa: E402

MODELS = {"CHRONOS2_COV": "amazon/chronos-2", "CHRONOS2": "amazon/chronos-2", "CHRONOS_BOLT_SMALL": "amazon/chronos-bolt-small"}
OUT = os.path.join(HERE, "chronos")

if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    os.makedirs(OUT, exist_ok=True)
    tasks = heldout_tasks()
    data = {t: D.load(t, final=True) for t in tasks}
    idxs = {t: CH.points(data[t]["y"]) for t in tasks}
    preds = {t: {} for t in tasks}
    for mid, name in MODELS.items():
        pipe = BaseChronosPipeline.from_pretrained(name, device_map="cpu")
        for t in tasks:
            t0 = time.time()
            inp = CH.contexts(data[t]["y"], idxs[t], data[t]["X"] if mid == "CHRONOS2_COV" else None); out = []
            for b in range(0, len(inp), 256):
                q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
                q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
                out.append(q.float().numpy())
            preds[t][mid] = np.concatenate(out)
            print(f"{mid:20s} {t:45s} {time.time() - t0:5.0f}s", flush=True)
    for t in tasks:
        np.savez_compressed(os.path.join(OUT, t.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz"), idx=idxs[t], **preds[t])
