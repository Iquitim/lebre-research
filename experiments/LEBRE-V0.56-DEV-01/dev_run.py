#!/usr/bin/env python3
"""dev_run.py — execuções da etapa LEBRE-V0.56-DEV-01 (PLANO_DEV_M1_BARATA.md, §3 e §4). Grava preds/<parte>__<id>.npz e
.json (fora do git). Roda no ambiente do LEBRE Lab (por causa do E20), com o protótipo congelado num worktree limpo.
Uso: LEBRE055_PROTO=<worktree b0522a0>/experiments/LEBRE-V0.55-PROTO-01 LEBRE053_PROTO=<...> \
     <python do Lab> dev_run.py escolha            (E20 + prédios P + bacias D-A, A e C0 a C6)
     <python do Lab> dev_run.py replica <Cx>       (bacias D-B + prédios R, A e a escolhida)
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
OUT = AQUI / "preds"
COMMIT = "b0522a0"
TODAS = ("A", "C0", "C1", "C2", "C3", "C4", "C5", "C6")


def proto():
    p = os.environ["LEBRE055_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")


def _serie(parte, ident):
    sys.path.insert(0, str(AQUI))
    import dev_dados as DD
    if parte == "e20":
        fam, k = ident
        E20, _ = DD.e20()
        origem, s = list(E20._series(fam))[k]
        ref = "zero" if s.get("zero_baseline") else ("seasonal" if s.get("season") else "persistence")
        return dict(nome=str(s.get("nome")), y=np.asarray(s["y"], float), X=np.asarray(s["X"], float), q=None,
                    season=s.get("season"), season2=s.get("season2"), ref=ref, origem=str(origem))
    if parte in ("P", "R"):
        s = DD.carregar_predio(ident); s["ref"] = "seasonal"
        return s
    B = DD.bacias(); s = B.carregar(ident)
    return dict(nome=s["nome"], y=s["y"], X=s["X"], q=s["q"], season=None, season2=None, ref="persistence")


def job(arg):
    parte, ident, variantes = arg
    nome = f"{parte}__{ident[0]}__{ident[1]}" if parte == "e20" else f"{parte}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    base = OUT / nome
    if base.with_suffix(".json").exists() and all(v in json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
                                                  for v in variantes):
        return nome, "já feito"                                       # retomada sem refazer o que está pronto
    try:
        t0 = time.time(); proto()
        sys.path.insert(0, str(AQUI))
        import dev_m1 as M
        novo = M.classes()
        s = _serie(parte, ident)
        y, X, q = s["y"], s["X"], s["q"]
        old = dict(np.load(base.with_suffix(".npz"))) if base.with_suffix(".npz").exists() else {}
        info = json.loads(base.with_suffix(".json").read_text(encoding="utf-8")) if base.with_suffix(".json").exists() else {}
        prev = {k: v for k, v in old.items() if k != "y"}
        for v in variantes:
            m = novo(v, X.shape[1], season=s["season"], season2=s["season2"], reference=s["ref"])
            f = M.rodar(m, y, X, q)
            prev[v] = f
            info[v] = dict(custo=m.cost_per_step, nan=int((np.isfinite(y) & ~np.isfinite(f)).sum()))
        np.savez_compressed(base.with_suffix(".npz"), y=y, **prev)
        info["_"] = dict(parte=parte, ident=list(ident) if parte == "e20" else str(ident), nome=s["nome"], T=len(y),
                         origem=s.get("origem"))
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, default=str) + "\n", encoding="utf-8",
                                             newline="\n")
        return nome, f"ok {round(time.time() - t0)}s"
    except Exception:
        return nome, "ERRO " + traceback.format_exc()[-900:]


def tarefas(modo, escolhida=None):
    sys.path.insert(0, str(AQUI))
    import dev_dados as DD
    P = DD.predios(); C, _ = DD.bacias().conjuntos()
    if modo == "escolha":
        E20, _ = DD.e20()
        t = [("e20", (fam, k), TODAS) for fam in E20.TODAS for k in range(len(list(E20._series(fam))))]
        t += [("P", m, TODAS) for m in P["P"]] + [("DA", g, TODAS) for g in C["A"]]
        return t
    assert escolhida in TODAS[1:]
    v = ("A", escolhida)
    return [("DB", g, v) for g in C["B"]] + [("R", m, v) for m in P["R"]]


if __name__ == "__main__":
    modo = sys.argv[1]
    ts = tarefas(modo, sys.argv[2] if len(sys.argv) > 2 else None)
    OUT.mkdir(exist_ok=True)
    print(len(ts), "tarefas", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for nome, st in ex.map(job, ts, chunksize=1):
            print(nome, st, flush=True)
