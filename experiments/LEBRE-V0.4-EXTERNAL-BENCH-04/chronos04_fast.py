"""chronos04_fast.py — PREREG_BENCH04_AMENDMENT_01: Chronos-Bolt-small / Chronos-2 on evenly spaced test points."""
import os, sys, time
import numpy as np, pandas as pd, torch
import chronos04 as C
from load04 import TASKS, load

N = {"CHRONOS_BOLT_SMALL": 1000, "CHRONOS2": 1000, "CHRONOS2_COV": 500}


def run(pipe, mid, task, ctx, cov, a_q, n):
    X, y, split, names, _, j = load(task)
    ts = int(0.30 * len(X)); idx = np.unique(np.linspace(ts, len(X) - 1, n).astype(int))
    inp = []
    for t in idx:
        a = max(0, t + 1 - ctx)
        inp.append({"target": X[a:t + 1, j].astype(np.float32),
                    "past_covariates": {f"c{k}": X[a:t + 1, k].astype(np.float32) for k in range(X.shape[1]) if k != j}}
                   if cov else torch.tensor(X[a:t + 1, j], dtype=torch.float32))
    t0 = time.time(); out = []
    for b in range(0, len(inp), 256):
        q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[a_q, 0.5, 1 - a_q])
        out.append(torch.stack([qq.reshape(-1, 3)[0] for qq in q]).numpy() if isinstance(q, list)
                   else q.reshape(len(inp[b:b + 256]), -1, 3)[:, 0].numpy())
    q = np.concatenate(out); wall = time.time() - t0
    yt = y[idx]; e = yt - q[:, 1]; yall = y[ts:]
    return {"group": "BR" if task.startswith("BR") else "INTL", "task_id": task, "model_id": mid, "seed": 0,
            "config": f'{{"context": {ctx}, "n_points": {len(idx)}}}', "T": len(X), "D": X.shape[1],
            "status": "SUCCESS" if np.all(np.isfinite(q)) else "NUMERICAL_DIVERGENCE", "mse": float(np.mean(e ** 2)),
            "mae": float(np.mean(np.abs(e))), "nmse": float(np.mean(e ** 2) / (np.var(yall) + 1e-6)),
            "mean_flops": float("nan"), "memory_bytes": -1, "wall": wall, "ms_per_step": 1000 * wall / len(idx),
            "coverage": float(np.mean((yt >= q[:, 0]) & (yt <= q[:, 2]))), "nominal": 1 - 2 * a_q,
            "interval_width_rel": float(np.mean(q[:, 2] - q[:, 0])) / float(np.std(yall)), "sampled": True}


if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    path = os.path.join(C.HERE, "BENCH04_CHRONOS_RESULTS.csv"); rows = pd.read_csv(path).to_dict("records")
    for mid, n in N.items():
        name, ctx, cov, a_q = C.MODELS[mid]; pipe = BaseChronosPipeline.from_pretrained(name, device_map="cpu")
        for task in TASKS:
            if cov and load(task)[0].shape[1] == 1:
                continue
            r = run(pipe, mid, task, ctx, cov, a_q, n); rows.append(r); pd.DataFrame(rows).to_csv(path, index=False)
            print(f"{mid:20s} {task:24s} nmse={r['nmse']:.4f} cov={r['coverage']:.3f} {r['wall']:.0f}s", flush=True)
