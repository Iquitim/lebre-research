#!/usr/bin/env python3
"""final_run.py — avaliação final da v0.55 (PREREG_V055_FINAL.md): A (v0.54) e B10 do protótipo no commit b0522a0, com as
entradas reais e com duas entradas placebo, nas 84 séries de LEBRE-V0.55-DATA-02/SPLIT_V055.json.
Grava preds/<família>__<id>.npz e .json (fora do git). Uso:
  LEBRE055_PROTO=<worktree b0522a0>/experiments/LEBRE-V0.55-PROTO-01 python final_run.py
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
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
COMMIT = "b0522a0"
SPLIT = json.loads((RAIZ / "experiments" / "LEBRE-V0.55-DATA-02" / "SPLIT_V055.json").read_text(encoding="utf-8"))
SNAP55, SNAP53, SNAP54 = (RAIZ / "data" / f"external_v05{k}" for k in (5, 3, 4))
OUT = AQUI / "preds"
FAMILIAS = ["camels", "bdg2", "eolica", "solar", "niveis_ecb"]
SEMENTE_PLACEBO = 2026102500
DIAS = pd.bdate_range("2010-01-01", "2025-12-31")
ESPERADO = {"camels": (None, None, 3, "persistence"), "bdg2": (24, 168, 2, "seasonal"), "eolica": (24, None, 5, "seasonal"),
            "solar": (24, None, 4, "seasonal"), "niveis_ecb": (None, None, 4, "persistence")}


def _f54():
    sp = importlib.util.spec_from_file_location("final_dados_v054", RAIZ / "experiments" / "LEBRE-V0.54-FINAL-01" / "final_dados.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


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


def tarefas():
    t = [("camels", str(g)) for g in SPLIT["camels_br"]["reservadas"]]
    t += [("bdg2", m) for m in SPLIT["bdg2"]["reservadas"]]
    t += [("eolica", u["nome"]) for u in SPLIT["eolica"]["reservadas"]]
    t += [("solar", u["nome"]) for u in SPLIT["solar"]["reservadas"]]
    t += [("niveis_ecb", c) for c in SPLIT["niveis_ecb"]["reservadas"]]
    return t


def ecb(cur):
    df = pd.read_csv(SNAP55 / "ecb" / f"EUR_{cur}.csv")
    s = pd.Series(pd.to_numeric(df["OBS_VALUE"], errors="coerce").to_numpy(), index=pd.to_datetime(df["TIME_PERIOD"]))
    return s[~s.index.duplicated()].sort_index()


def carregar(familia, ident):
    """Só na execução final pré-registrada."""
    if familia in ("camels", "bdg2"):
        sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.52-PROTO-01"))
        import data_v052 as D
        d = D.load(f"{familia}:{ident}", final=True)
        s = dict(nome=d["task"], y=np.asarray(d["y"], float), X=np.asarray(d["X"], float), q=np.asarray(d["quarantine"], bool),
                 season=d["season"], season2=168 if familia == "bdg2" else None)
    elif familia in ("eolica", "solar"):
        F = _f54()
        u = next(x for x in SPLIT[familia]["reservadas"] if x["nome"] == ident)
        pasta = SNAP54 / "ons_fator_2026" if familia == "solar" else SNAP53 / "ons_fator"
        ons = sorted(str(p) for p in pasta.iterdir())
        horas = F.HORAS_SOLAR if familia == "solar" else F.HORAS_EOLICA
        safe = "".join(c if c.isalnum() else "_" for c in ident)
        r = F.usina(familia, ident, ons, str(SNAP55 / "open_meteo" / f"{familia}_{safe}.json"), horas)
        s = dict(nome=r["nome"], y=r["y"], X=r["X"], q=None, season=r["season"], season2=r["season2"])
    else:
        F = _f54()
        cal = lambda x: x[~x.index.duplicated()].reindex(DIAS)                        # noqa: E731
        ent = pd.DataFrame({c: cal(ecb(c)) for c in SPLIT["niveis_ecb"]["entradas"]}).shift(1)
        r = F.serie(f"ecb_EUR_{ident}", cal(ecb(ident)), ent, freq=None)
        s = dict(nome=r["nome"], y=r["y"], X=r["X"], q=None, season=None, season2=None)
    season, season2, d, ref = ESPERADO[familia]
    assert s["season"] == season and s["season2"] == season2 and s["X"].shape[1] == d, (familia, ident, s["X"].shape)
    assert len(s["y"]) == s["X"].shape[0] and np.isfinite(s["y"]).mean() > 0.5, (familia, ident)
    return s, ref


def rodar(L, s, ref, X, v):
    m = L(X.shape[1], season=s["season"], season2=s["season2"], reference=ref, variant=v)
    y, q = s["y"], s["q"]
    f = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    c = m.core._core
    acc = [(int(e.t), e.added) for e in m.events if e.outcome == "accepted" and e.change in ("add", "swap") and e.added
           and e.added.startswith("x")]
    return f, dict(custo=m.cost_per_step, estrutura=m.structure, externas_final=sorted(u for u in m.structure if u.startswith("x")),
                   aceitas=acc, wI=float(getattr(c, "wI", float("nan"))), wS=float(c.wS))


def job(arg):
    (familia, ident), fi, si = arg
    base = OUT / f"{familia}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    if base.with_suffix(".json").exists():
        return arg[0], "já feito"
    try:
        t0 = time.time(); L = proto(); s, ref = carregar(familia, ident)
        X = s["X"]; T = len(s["y"])
        rng = np.random.default_rng([SEMENTE_PLACEBO, fi, si])
        Xp = np.column_stack([X, np.cumsum(rng.standard_normal((T, 2)), 0)])
        placebo = [f"x{X.shape[1]}", f"x{X.shape[1] + 1}"]
        prev, info = {}, {}
        for v in ("A", "B10"):
            prev[v], info[v] = rodar(L, s, ref, X, v)
            prev[v + "_pl"], info[v + "_pl"] = rodar(L, s, ref, Xp, v)
        np.savez_compressed(base.with_suffix(".npz"), y=s["y"], **prev)
        base.with_suffix(".json").write_text(json.dumps(dict(familia=familia, ident=str(ident), nome=s["nome"], T=T, d=int(X.shape[1]),
                                                             referencia=ref, placebo=placebo, commit=COMMIT, info=info,
                                                             seg=round(time.time() - t0)), ensure_ascii=False) + "\n",
                                             encoding="utf-8", newline="\n")
        return arg[0], f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg[0], "ERRO " + traceback.format_exc()[-700:]


if __name__ == "__main__":
    proto(); OUT.mkdir(exist_ok=True)
    ts = tarefas()
    args = []
    for fi, fam in enumerate(FAMILIAS):
        for si, t in enumerate([x for x in ts if x[0] == fam]):
            args.append((t, fi, si))
    print(len(args), "séries", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for tarefa, st in ex.map(job, args, chunksize=1):
            print(tarefa, st, flush=True)
