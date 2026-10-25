#!/usr/bin/env python3
"""final_run.py — avaliação final da v0.56 (PREREG_V056_FINAL.md): A (v0.55) e C5 do protótipo no commit ef77728, com as
entradas reais e com duas entradas placebo, nas 93 séries da avaliação final de LEBRE-V0.56-DATA-01/SPLIT_V056.json.
Só roda se a validação tiver passado. Grava preds/<família>__<id>.npz e .json (fora do git).
Uso: LEBRE056_PROTO=<worktree ef77728>/experiments/LEBRE-V0.56-PROTO-01 python final_run.py
"""
import hashlib
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
COMMIT = "ef77728"
SEMENTE_PLACEBO = 2026102900
FAMILIAS = ["camels_cl", "bdg2", "eolica", "solar", "camels_br"]
sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.56-DATA-01"))


def validacao_passou():
    r = json.loads((RAIZ / "experiments" / "LEBRE-V0.56-VAL-01" / "VAL_RESULTADO.json").read_text(encoding="utf-8"))
    return bool(r["criterios"]["PASSA"])


def proto():
    p = os.environ["LEBRE056_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre056.model056 import Lebre056
    return Lebre056


def rodar(L, s, ref, X, v):
    m = L(X.shape[1], season=s["season"], season2=s["season2"], reference=ref, variant=v)
    y, q = s["y"], s["q"]
    f = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    eventos_nucleo = [(int(e.t), e.outcome, e.change, e.added, e.removed) for e in m.core.events]
    return f, dict(custo=m.cost_per_step, estrutura=m.structure, externas_final=sorted(u for u in m.structure if u.startswith("x")),
                   eventos_nucleo=len(eventos_nucleo), portao=sum(e.change == "gate" for e in m.events),
                   assinatura_nucleo=hashlib.sha256(repr(eventos_nucleo).encode()).hexdigest())


def job(arg):
    (familia, ident), fi, si = arg
    base = OUT / f"{familia}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    if base.with_suffix(".json").exists():
        return arg[0], "já feito"
    try:
        t0 = time.time(); L = proto()
        import dados_v056 as D
        s, ref = D.carregar(familia, ident)
        X = s["X"]; T = len(s["y"])
        rng = np.random.default_rng([SEMENTE_PLACEBO, fi, si])
        Xp = np.column_stack([X, np.cumsum(rng.standard_normal((T, 2)), 0)])
        placebo = [f"x{X.shape[1]}", f"x{X.shape[1] + 1}"]
        prev, info = {}, {}
        for v in ("A", "C5"):
            prev[v], info[v] = rodar(L, s, ref, X, v)
            prev[v + "_pl"], info[v + "_pl"] = rodar(L, s, ref, Xp, v)
        np.savez_compressed(base.with_suffix(".npz"), y=s["y"], **prev)
        base.with_suffix(".json").write_text(json.dumps(dict(familia=familia, ident=str(ident), nome=s["nome"], T=T, d=int(X.shape[1]),
                                                             referencia=ref, placebo=placebo, commit=COMMIT, info=info,
                                                             seg=round(time.time() - t0)), ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
        return arg[0], f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg[0], "ERRO " + traceback.format_exc()[-800:]


if __name__ == "__main__":
    if not validacao_passou():
        raise SystemExit("a validação não passou: pelo pré-registro, a avaliação final não é executada")
    proto(); OUT.mkdir(exist_ok=True)
    import dados_v056 as D
    ts = D.series("final")
    args = [(t, fi, si) for fi, fam in enumerate(FAMILIAS) for si, t in enumerate([x for x in ts if x[0] == fam])]
    print(len(args), "séries", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for tarefa, st in ex.map(job, args, chunksize=1):
            print(tarefa, st, flush=True)
