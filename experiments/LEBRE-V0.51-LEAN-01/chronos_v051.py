#!/usr/bin/env python3
"""chronos_v051.py — PREREG_V051.md: Chronos comparators on the HELD-OUT set (protocol of BENCH-04 amendment 01):
Bolt-tiny on the full test; Bolt-small and Chronos-2 on 1000 evenly spaced test points; Chronos-2 with covariates on 500."""
import os
import sys

import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
B04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-EXTERNAL-BENCH-04")
for p in (B04, os.path.join(ROOT, "data", "external_bench04"), os.path.join(ROOT, "data", "external_v051")):
    sys.path.insert(0, p)
import chronos04 as C  # noqa: E402
import chronos04_fast as F  # noqa: E402
import load051 as load05  # noqa: E402

if __name__ == "__main__":
    import eval_v051
    eval_v051.check()
    C.load = load05.load; F.load = load05.load
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    out = os.path.join(HERE, "HELDOUT_V051_CHRONOS_RESULTS.csv"); rows = []
    for mid in ("CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"):
        name, ctx, cov, a_q = C.MODELS[mid]; pipe = BaseChronosPipeline.from_pretrained(name, device_map="cpu")
        for task in load05.TASKS:
            if cov and load05.load(task)[0].shape[1] == 1:
                continue
            r = C.run(pipe, mid, task, ctx, cov, a_q) if mid == "CHRONOS_BOLT_TINY" else F.run(pipe, mid, task, ctx, cov, a_q, F.N[mid])
            rows.append(r); pd.DataFrame(rows).to_csv(out, index=False)
            print(f"{mid:20s} {task:28s} nmse={r['nmse']:.4f} {r['wall']:.0f}s", flush=True)
