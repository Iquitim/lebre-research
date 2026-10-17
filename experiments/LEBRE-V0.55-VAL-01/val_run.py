#!/usr/bin/env python3
"""val_run.py — validação da v0.55 (PREREG_V055_VAL.md): A (v0.54) e B10 do protótipo no commit b0522a0, nas 50 séries
reais de SPLIT_V055_VAL.json. Grava preds/<família>__<id>.npz e .json (fora do git).
Uso: LEBRE055_PROTO=<worktree b0522a0>/experiments/LEBRE-V0.55-PROTO-01 python val_run.py
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
COMMIT = "b0522a0"
SPLIT = json.loads((RAIZ / "experiments" / "LEBRE-V0.55-DATA-01" / "SPLIT_V055_VAL.json").read_text(encoding="utf-8"))
OUT = AQUI / "preds"
ESPERADO = {"camels": (None, None, 3, "persistence"), "bdg2": (24, 168, 2, "seasonal")}


def proto():
    p = os.environ["LEBRE055_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre055.model055 import Lebre055
    return Lebre055


def carregar(familia, ident):
    sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.52-PROTO-01"))
    import data_v052 as D
    d = D.load(f"{'camels' if familia == 'camels' else 'bdg2'}:{ident}", final=True)   # uso único, pré-registrado
    s = dict(y=np.asarray(d["y"], float), X=np.asarray(d["X"], float), q=np.asarray(d["quarantine"], bool),
             season=d["season"], season2=168 if familia == "bdg2" else None, nome=d["task"])
    season, season2, dd, ref = ESPERADO[familia]
    assert s["season"] == season and s["season2"] == season2 and s["X"].shape[1] == dd, (familia, ident)
    assert np.isfinite(s["y"]).mean() > 0.5, (familia, ident, "alvo quase todo faltante")
    return s, ref


def job(arg):
    familia, ident = arg
    base = OUT / f"{familia}__{str(ident).replace(':', '_')}"
    if (base.with_suffix(".json")).exists():
        return arg, "já feito"
    try:
        t0 = time.time(); L = proto(); s, ref = carregar(familia, ident)
        y, X, q = s["y"], s["X"], s["q"]
        out, info = {}, {}
        for v in ("A", "B10"):
            m = L(X.shape[1], season=s["season"], season2=s["season2"], reference=ref, variant=v)
            f = np.full(len(y), np.nan)
            for t in range(len(y)):
                f[t] = m.predict(X[t]).value
                m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]))
            out[v] = f
            c = m.core._core
            info[v] = dict(custo=m.cost_per_step, estrutura=m.structure,
                           externas_final=sorted(u for u in m.structure if u.startswith("x")),
                           wI=float(getattr(c, "wI", float("nan"))), wS=float(c.wS))
        np.savez_compressed(base.with_suffix(".npz"), y=y, A=out["A"], B10=out["B10"])
        base.with_suffix(".json").write_text(json.dumps(dict(familia=familia, ident=str(ident), nome=s["nome"], T=len(y),
                                                             referencia=ref, commit=COMMIT, info=info,
                                                             seg=round(time.time() - t0)), ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
        return arg, f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg, "ERRO " + traceback.format_exc()[-600:]


if __name__ == "__main__":
    proto(); OUT.mkdir(exist_ok=True)
    tarefas = [("camels", g) for g in SPLIT["camels_br"]["validacao"]] + [("bdg2", m) for m in SPLIT["bdg2"]["validacao"]]
    print(len(tarefas), "séries", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for tarefa, st in ex.map(job, tarefas, chunksize=1):
            print(tarefa, st, flush=True)
