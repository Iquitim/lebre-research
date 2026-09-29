#!/usr/bin/env python3
"""chronos04.py — PREREG_BENCH04.md, pretrained foundation models (zero-shot, rolling one-step-ahead, same information set).

CHRONOS_BOLT_TINY / CHRONOS_BOLT_SMALL (Ansari et al. 2024; Bolt release Nov 2024), CHRONOS2 (Oct 2025): target history only,
context 512. CHRONOS2_COV: Chronos-2 with every other variable as past covariate, context 256 (CPU budget), multivariate tasks only.
Forecast for y[t] uses values up to t-1 only. Point forecast = model median; interval = [q0.05, q0.95] (90 %) for Chronos-2;
Bolt was trained on quantiles 0.1..0.9 only, so its interval is [q0.1, q0.9] (nominal 80 %).
"""
import hashlib
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "data", "external_bench04"))
from load04 import TASKS, load  # noqa: E402

MODELS = {"CHRONOS_BOLT_TINY": ("amazon/chronos-bolt-tiny", 512, False, 0.10),
          "CHRONOS_BOLT_SMALL": ("amazon/chronos-bolt-small", 512, False, 0.10),
          "CHRONOS2": ("amazon/chronos-2", 512, False, 0.05),
          "CHRONOS2_COV": ("amazon/chronos-2", 256, True, 0.05)}
BATCH = 256


def run(pipe, model_id, task, ctx, cov, a_q):
    X, y, split, names, _, j = load(task)
    test_start = split if split is not None else int(0.30 * len(X))
    idx = np.arange(test_start, len(X))
    med, lo, hi = np.empty(len(idx)), np.empty(len(idx)), np.empty(len(idx))
    t0 = time.time()
    for b in range(0, len(idx), BATCH):
        inp = []
        for t in idx[b:b + BATCH]:
            a = max(0, t + 1 - ctx)
            if cov:
                inp.append({"target": X[a:t + 1, j].astype(np.float32),
                            "past_covariates": {f"c{k}": X[a:t + 1, k].astype(np.float32) for k in range(X.shape[1]) if k != j}})
            else:
                inp.append(torch.tensor(X[a:t + 1, j], dtype=torch.float32))
        q, _ = pipe.predict_quantiles(inp, prediction_length=1, quantile_levels=[a_q, 0.5, 1 - a_q])
        q = torch.stack([qq.reshape(-1, 3)[0] for qq in q]).numpy() if isinstance(q, list) else q.reshape(len(inp), -1, 3)[:, 0].numpy()
        n = len(inp)
        lo[b:b + n], med[b:b + n], hi[b:b + n] = q[:, 0], q[:, 1], q[:, 2]
    wall = time.time() - t0
    yt = y[idx]; e = yt - med
    ok = bool(np.all(np.isfinite(med)))
    sd = float(np.std(yt))
    return {"group": "BR" if task.startswith("BR") else "INTL", "task_id": task, "model_id": model_id, "seed": 0,
            "config": f'{{"context": {ctx}}}', "T": len(X), "D": X.shape[1],
            "status": "SUCCESS" if ok else "NUMERICAL_DIVERGENCE", "mse": float(np.mean(e ** 2)),
            "mae": float(np.mean(np.abs(e))), "nmse": float(np.mean(e ** 2) / (np.var(yt) + 1e-6)),
            "mean_flops": float("nan"), "memory_bytes": -1, "wall": wall, "ms_per_step": 1000.0 * wall / len(idx),
            "coverage": float(np.mean((yt >= lo) & (yt <= hi))), "nominal": 1 - 2 * a_q, "interval_width_rel": float(np.mean(hi - lo)) / sd}




def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_BENCH04.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_BENCH04_SHA256.txt")).read().split()[0]
    torch.set_num_threads(int(os.environ.get("THREADS", 16)))
    from chronos import BaseChronosPipeline
    out_path = os.path.join(HERE, "BENCH04_CHRONOS_RESULTS.csv")
    rows = pd.read_csv(out_path).to_dict("records") if os.path.exists(out_path) else []
    done = {(r["task_id"], r["model_id"]) for r in rows}
    for mid, (name, ctx, cov, a_q) in MODELS.items():
        pipe = BaseChronosPipeline.from_pretrained(name, device_map="cpu")
        for task in TASKS:
            if (task, mid) in done or (cov and load(task)[0].shape[1] == 1):
                continue
            r = run(pipe, mid, task, ctx, cov, a_q); rows.append(r)
            pd.DataFrame(rows).to_csv(out_path, index=False)
            print(f"{mid:20s} {task:24s} nmse={r['nmse']:.4f} cov={r['coverage']:.3f} {r['wall']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
