"""final_run.py — EXECUÇÃO ÚNICA PRÉ-REGISTRADA da v0.53 na reserva (PREREG_V053_FINAL.md). Por série: v0.53 (M1 rascunho 5
+ M2 candidata Q2), v0.52 (a mesma base, porta desligada = lebre==0.1.0), a referência trivial da régua e SARIMAX com
entradas (teto de referência); também a versão curta (primeiros 360 passos) de v0.53, v0.52 e referência.
Saída: preds/<tarefa>.npz e .json. O código da v0.53 vem de uma cópia fixa (git worktree) no commit declarado.

Uso: LEBRE053_PROTO=<worktree>/experiments/LEBRE-V0.53-PROTO-01 python final_run.py
"""
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
import final_regua as R

COMMIT = "4a2620e"
AQUI = FD.AQUI
OUT = os.path.join(AQUI, "preds")
N_CURTA = 360
KW = dict(porta=True, eps_porta=0.002, recriar=True, alpha_porta=0.01, observar_quarentena_entradas=True,
          saida="prod_q2", precisao="r5")


def _proto():
    p = os.environ["LEBRE053_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre053.model053 import Lebre053
    return Lebre053


def _rodar(m, X, y, qu):
    T = len(y)
    f = np.full(T, np.nan)
    c = np.zeros(T)
    for t in range(T):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(qu[t]) if qu is not None else False)
    return f


def _modelos(Lebre053, s, X, y, qu):
    d = X.shape[1]
    ref = FD.referencia(s)
    m53 = Lebre053(d, season=s["season"], season2=s["season2"], referencia=ref, **KW)
    m52 = Lebre053(d, season=s["season"], season2=s["season2"], porta=False)
    f53, f52 = _rodar(m53, X, y, qu), _rodar(m52, X, y, qu)
    fr = R.rodar_ref(R.ref_modelo(ref, d, s["season"]), X, y)
    info = dict(custo_v053=m53.cost_per_step, custo_v052=m52.cost_per_step, externas_v053=R.externas(m53.events),
                externas_v052=R.externas(m52.events),
                estrutura_identica=R.estrutura(m53) == R.estrutura(m52) and m53.base.cost_per_step == m52.cost_per_step,
                peso_m1_final=m53.precisao.peso() if m53.precisao is not None else None)
    return f53, f52, fr, info


def nome_arq(familia, ident):
    return os.path.join(OUT, f"{familia}__{FD._seguro(str(ident))}")


def job(tarefa):
    familia, ident = tarefa
    base = nome_arq(familia, ident)
    if os.path.exists(base + ".npz"):
        return tarefa, "já feito"
    try:
        t0 = time.time()
        Lebre053 = _proto()
        s = FD.carregar(familia, ident)
        y, X, qu = s["y"], s["X"], s["quarantine"]
        f53, f52, fr, info = _modelos(Lebre053, s, X, y, qu)
        n = min(N_CURTA, len(y))
        c53, c52, cr, cinfo = _modelos(Lebre053, s, X[:n], y[:n], qu[:n] if qu is not None else None)
        sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-PROTO-01"))
        sys.path.insert(0, FD.RAIZ)
        import comp_dev as C
        Xs = C._scaled_inputs(X)
        fs, ok_s, inf_s = C.run_airline_x(y, Xs, s["season"])
        np.savez_compressed(base + ".npz", y=y, v053=f53, v052=f52, ref=fr, sarimax=fs, curta_y=y[:n], curta_v053=c53,
                            curta_v052=c52, curta_ref=cr)
        json.dump(dict(familia=familia, ident=str(ident), nome=s["nome"], T=len(y), d=int(X.shape[1]), season=s["season"],
                       season2=s["season2"], referencia=FD.referencia(s), entradas=s["entradas"], info=info,
                       info_curta=cinfo, sarimax_ok=bool(ok_s), sarimax_info=str(inf_s), seg=round(time.time() - t0),
                       commit=COMMIT), open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, default=str)
        return tarefa, f"ok {round(time.time() - t0)}s"
    except Exception:
        return tarefa, "ERRO " + traceback.format_exc()[-800:]


if __name__ == "__main__":
    _proto()
    os.makedirs(OUT, exist_ok=True)
    ts = FD.tarefas()
    print(len(ts), "séries da reserva", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for tarefa, st in ex.map(job, ts, chunksize=1):
            print(tarefa, st, flush=True)
