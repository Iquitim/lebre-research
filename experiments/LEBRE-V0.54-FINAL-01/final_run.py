"""final_run.py — EXECUÇÃO ÚNICA PRÉ-REGISTRADA da v0.54 na reserva (PREREG_V054_FINAL.md). Por série: v0.54, v0.53
(lebre==0.2.0), a referência trivial da régua e SARIMAX com entradas (teto de referência); também a versão curta
(primeiros 360 passos) de v0.54, v0.53 e referência. Saída: preds/<tarefa>.npz e .json. O código da v0.54 vem de uma
cópia fixa (git worktree) no commit declarado; a v0.53 é a biblioteca publicada lebre==0.2.0.

Uso: LEBRE054_PROTO=<worktree>/experiments/LEBRE-V0.54-PROTO-01 python final_run.py [pasta_saida]
"""
import importlib.util
import json
import math
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import final_dados as FD

# RUN_NOTAS.md, item 1: carregar por caminho, sem pôr a pasta da v0.53 no sys.path (os processos filhos herdavam esse
# sys.path e importavam o final_dados da v0.53 no lugar deste)
_sr = importlib.util.spec_from_file_location("final_regua_v053",
                                             os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.53-FINAL-01", "final_regua.py"))
R = importlib.util.module_from_spec(_sr); _sr.loader.exec_module(R)

COMMIT = "cfe72ce"
KW054 = dict(m5a=True, m5b=True, m4=True)
AQUI = FD.AQUI
N_CURTA = 360
REF_LIB = {"zero": "zero", "sazonal": "seasonal", "persistencia": "persistence"}


def _proto():
    p = os.environ["LEBRE054_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    import lebre
    if lebre.__version__ != "0.2.0":
        raise SystemExit(f"a v0.53 de comparação é lebre==0.2.0 (encontrada {lebre.__version__})")
    from lebre054.model054 import Lebre054
    return Lebre054, lebre.Lebre


def _rodar(m, X, y, qu):
    f = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(qu[t]) if qu is not None else False)
    return f


def externas(m):
    return sum(1 for e in m.events if e.outcome == "accepted" and e.added and e.added.startswith("x"))


def _modelos(L054, L053, s, X, y, qu):
    d = X.shape[1]
    ref = FD.referencia(s)
    kw = dict(season=s["season"], season2=s["season2"], reference=REF_LIB[ref])
    m54, m53 = L054(d, **kw, **KW054), L053(d, **kw)
    f54, f53 = _rodar(m54, X, y, qu), _rodar(m53, X, y, qu)
    fr = R.rodar_ref(R.ref_modelo(ref, d, s["season"]), X, y)
    c = m54.core._core
    info = dict(custo_v054=m54.cost_per_step, custo_v053=m53.cost_per_step, externas_v054=externas(m54),
                externas_v053=externas(m53), estrutura_v054=m54.structure, estrutura_v053=m53.structure,
                remocoes=[(int(e[0]), str(e[4])) for e in c.events if e[1] == "accepted" and e[2] == "rem"],
                m1=m54.m1_state, identica=bool(np.array_equal(f54, f53, equal_nan=True)))
    return f54, f53, fr, info


def job(arg):
    (familia, ident), out = arg
    base = os.path.join(out, f"{familia}__{FD._seguro(str(ident))}")
    if os.path.exists(base + ".npz"):
        return (familia, ident), "já feito"
    try:
        return (familia, ident), processar(FD.carregar(familia, ident), familia, ident, base)
    except Exception:
        return (familia, ident), "ERRO " + traceback.format_exc()[-800:]


def processar(s, familia, ident, base):
    """Uma série já carregada: os modelos, a versão curta e o SARIMAX; grava base.npz e base.json."""
    t0 = time.time()
    L054, L053 = _proto()
    y, X, qu = s["y"], s["X"], s.get("quarantine")
    f54, f53, fr, info = _modelos(L054, L053, s, X, y, qu)
    n = min(N_CURTA, len(y))
    c54, c53, cr, cinfo = _modelos(L054, L053, s, X[:n], y[:n], qu[:n] if qu is not None else None)
    sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-PROTO-01"))
    sys.path.insert(0, FD.RAIZ)
    import comp_dev as C
    fs, ok_s, inf_s = C.run_airline_x(y, C._scaled_inputs(X), s["season"])
    np.savez_compressed(base + ".npz", y=y, v054=f54, v053=f53, ref=fr, sarimax=fs, curta_y=y[:n], curta_v054=c54,
                        curta_v053=c53, curta_ref=cr)
    json.dump(dict(familia=familia, ident=str(ident), nome=s["nome"], T=len(y), d=int(X.shape[1]), season=s["season"],
                   season2=s["season2"], referencia=FD.referencia(s), entradas=s["entradas"], info=info,
                   info_curta=cinfo, sarimax_ok=bool(ok_s), sarimax_info=str(inf_s), seg=round(time.time() - t0),
                   commit=COMMIT, kw054=KW054), open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, default=str)
    return f"ok {round(time.time() - t0)}s"


def executar(tarefas, out, n_proc=14):
    os.makedirs(out, exist_ok=True)
    with ProcessPoolExecutor(n_proc) as ex:
        for tarefa, st in ex.map(job, [(t, out) for t in tarefas], chunksize=1):
            print(tarefa, st, flush=True)


if __name__ == "__main__":
    _proto()
    ts = FD.tarefas()
    print(len(ts), "séries da reserva", flush=True)
    executar(ts, sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "preds"))
