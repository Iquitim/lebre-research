#!/usr/bin/env python3
"""val2_run.py — segunda validação da v0.56 (PREREG_V056_VAL2.md): A (v0.55) e D4 do protótipo 02 no commit c3074bd, nas
50 séries de LEBRE-V0.56-DATA-01/SPLIT_V056_VAL2.json. Grava preds/<família>__<id>.npz e .json (fora do git).
Uso: LEBRE056D_PROTO=<worktree c3074bd>/experiments/LEBRE-V0.56-PROTO-02 python val2_run.py
"""
import json
import math
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
OUT = AQUI / "preds"
COMMIT = "c3074bd"
sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.56-DATA-01"))


def proto():
    p = os.environ["LEBRE056D_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre056.model056d import Lebre056D
    return Lebre056D


def rodar(L, s, ref, v):
    m = L(s["X"].shape[1], season=s["season"], season2=s["season2"], reference=ref, variant=v)
    y, X, q = s["y"], s["X"], s["q"]
    f = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    m1 = getattr(m, "_m1", None)
    frac = (m1.n_upd / max(m1.n_dec, 1)) if m1 is not None and hasattr(m1, "n_upd") else None
    return f, dict(custo=m.cost_per_step, estrutura=m.structure, fracao_atualizacoes=frac)


def job(arg):
    familia, ident = arg
    base = OUT / f"{familia}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    if base.with_suffix(".json").exists():
        return arg, "já feito"
    try:
        t0 = time.time(); L = proto()
        import dados_v056 as D
        s, ref = D.carregar(familia, ident)
        prev, info = {}, {}
        for v in ("A", "D4"):
            prev[v], info[v] = rodar(L, s, ref, v)
        np.savez_compressed(base.with_suffix(".npz"), y=s["y"], **prev)
        info["_"] = dict(familia=familia, ident=str(ident), T=len(s["y"]))
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return arg, f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg, "ERRO " + traceback.format_exc()[-800:]


if __name__ == "__main__":
    import dados_v056 as D
    OUT.mkdir(exist_ok=True)
    ts = D.series("validacao2")
    print(len(ts), "séries", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for t, st in ex.map(job, ts, chunksize=1):
            print(t, st, flush=True)
