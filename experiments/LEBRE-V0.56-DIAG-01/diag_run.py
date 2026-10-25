#!/usr/bin/env python3
"""diag_run.py — execuções do diagnóstico das bacias (PLANO_DIAG_BACIAS.md, §3). Grava preds/<conjunto>__<id>.npz e
.json (fora do git).

- Escada do ARX (R0 a R6): classe ArxGen, que generaliza a ArxRls de LEBRE-V0.55-COMP-01/comp_run.py (defasagens das
  entradas e do alvo separadas; RLS ou NLMS). Na configuração R0, ArxGen é conferida bit a bit contra a ArxRls importada
  sem alteração (python diag_run.py fumaca).
- LEBRE (L0 a L4): protótipo congelado no commit b0522a0 (worktree limpo, conferido como na avaliação final).
Uso: LEBRE055_PROTO=<worktree b0522a0>/experiments/LEBRE-V0.55-PROTO-01 python diag_run.py {fumaca|A|B} [modelos...]
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
E = RAIZ / "experiments"
OUT = AQUI / "preds"
COMMIT = "b0522a0"
LAMBDAS = (0.99, 0.999, 0.9999)
MUS = (0.01, 0.05, 0.2)
MUS_X = (0.5, 1.0)                                               # checagem suplementar R6x (RUN_NOTAS.md, §2)
# código: (lags das entradas, colunas das entradas, lags do alvo, algoritmo, lambda fixo)
ESCADA = {"R0": (3, (0, 1, 2), 3, "rls", None), "R1": (3, (), 3, "rls", None), "R2": (3, (0,), 3, "rls", None),
          "R3": (0, (0, 1, 2), 3, "rls", None), "R4": (3, (0, 1, 2), 1, "rls", None), "R5": (3, (0, 1, 2), 3, "rls", 1.0),
          "R6": (3, (0, 1, 2), 3, "nlms", None), "R6x": (3, (0, 1, 2), 3, "nlms_x", None)}
LEBRE = ("L0", "L1", "L2", "L3")                                 # L4 (memória) é gravada dentro de L2
TODOS = tuple(k for k in ESCADA if k != "R6x") + LEBRE


def _modulo(nome, caminho):
    sp = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def _cd():
    p = str(E / "LEBRE-V0.52-PROTO-01")
    if p not in sys.path:
        sys.path.insert(0, p)
    import comp_dev
    return comp_dev


def proto():
    p = os.environ["LEBRE055_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)


# ------------------------------------------------------------------ escada do ARX
class ArxGen:
    """ArxRls de comp_run.py com as defasagens das entradas (Kx) e do alvo (Ky) separadas e opção NLMS. Mesma ordem de
    operações da original quando Kx = Ky = K e algoritmo = RLS."""

    def __init__(self, d, Kx, Ky, alg, par, p0=100.0):
        self.d, self.Kx, self.Ky, self.alg, self.par, self.p0 = d, Kx, Ky, alg, par, p0
        self.H = np.zeros((Kx + 1, d)); self.Y = np.zeros(Ky + 1)
        self.n = 1 + d * (Kx + 1) + Ky
        self.w = np.zeros(self.n); self.P = np.eye(self.n) * p0

    def _phi(self):
        return np.concatenate(([1.0], self.H.ravel(), self.Y[:self.Ky]))

    def step(self, x, y):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = np.clip(np.nan_to_num(x), -8, 8)
        phi = self._phi()
        p = float(self.w @ phi)
        e = float(y) - p
        if self.alg == "rls":
            lam = self.par
            Pf = self.P @ phi; g = Pf / (lam + phi @ Pf)
            self.w = self.w + g * e
            P = (self.P - np.outer(g, Pf)) / lam; P = (P + P.T) / 2
            self.P = P if (np.isfinite(P).all() and np.diag(P).min() > 0) else np.eye(self.n) * self.p0
            fp = 6 * self.n * self.n + 8 * self.n
        else:
            self.w = self.w + self.par * e * phi / (float(phi @ phi) + 1e-6)
            fp = 6 * self.n
        self.Y = np.roll(self.Y, 1); self.Y[0] = float(y)
        return float(p), float(fp)


def run_arx(Xs, y, cfg, par):
    Kx, cols, Ky, alg, _ = cfg
    m = ArxGen(len(cols), Kx, Ky, "nlms" if alg == "nlms_x" else alg, par); Xc = Xs[:, list(cols)]
    pred = np.full(len(y), np.nan); fp = []
    for t in range(len(y)):
        if not np.isfinite(y[t]):
            continue
        p, f = m.step(Xc[t], float(y[t]))
        pred[t] = p; fp.append(f)
        if not np.isfinite(p) or abs(p) > 1e12:
            return pred, float("nan"), False
    return pred, float(np.mean(fp)), True


def calib_arx(Xs, y, cfg, idx):
    grade = (cfg[4],) if cfg[4] is not None else {"rls": LAMBDAS, "nlms": MUS, "nlms_x": MUS_X}[cfg[3]]
    best, bm = grade[0], float("inf")
    for par in grade:
        p, _, ok = run_arx(Xs[idx], y[idx], cfg, par)
        mse = float(np.nanmean((y[idx] - p) ** 2)) if ok else float("inf")
        if mse < bm:
            best, bm = par, mse
    return best


# ------------------------------------------------------------------ LEBRE
def run_lebre(cod, s):
    from lebre055.model055 import Lebre055
    import diag_allon
    y, X, q = s["y"], s["X"], s["q"]
    if cod == "L3":
        m = diag_allon.classes()[1](3, None, None, "persistence", all_on=True)
    else:
        m = Lebre055(3, season=None, season2=None, reference="persistence", core_only=(cod == "L2"),
                     variant="A" if cod == "L1" else "B10")
    f = np.full(len(y), np.nan); mem = np.full(len(y), np.nan) if cod == "L2" else None
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        if mem is not None:
            mem[t] = m.core._core._pending[1]                         # a previsão m da memória (L4)
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]))
    acc = [(int(e.t), e.added) for e in m.events if e.outcome == "accepted" and e.change in ("add", "swap") and e.added]
    info = dict(custo=m.cost_per_step, estrutura=m.structure, aceitas=acc, wS=float(m.core._core.wS),
                wI=float(getattr(m.core._core, "wI", float("nan"))))
    return f, mem, info


def job(arg):
    conj, gid, modelos = arg
    base = OUT / f"{conj}__{gid}"
    try:
        t0 = time.time(); proto(); CD = _cd()
        import diag_dados as DD
        s = DD.carregar(gid)
        y = s["y"]; Xs = CD._scaled_inputs(pd.DataFrame(s["X"]).ffill().fillna(0.0).to_numpy(float))
        idx = CD._calib_n(y)
        old = dict(np.load(base.with_suffix(".npz"))) if base.with_suffix(".npz").exists() else {}
        info = json.loads(base.with_suffix(".json").read_text(encoding="utf-8")) if base.with_suffix(".json").exists() else {}
        prev = {k: v for k, v in old.items() if k != "y"}
        for cod in modelos:
            if cod in ESCADA:
                par = calib_arx(Xs, y, ESCADA[cod], idx)
                p, fp, ok = run_arx(Xs, y, ESCADA[cod], par)
                prev[cod] = p; info[cod] = dict(par=par, fp=fp, ok=ok)
            else:
                f, mem, inf = run_lebre(cod, s)
                prev[cod] = f; info[cod] = inf
                if mem is not None:
                    prev["L4"] = mem
        np.savez_compressed(base.with_suffix(".npz"), y=y, **prev)
        info["_"] = dict(conjunto=conj, pos=s["pos"], T=len(y), calib_n=len(idx))
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, default=str) + "\n", encoding="utf-8",
                                             newline="\n")
        return arg[:2], f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg[:2], "ERRO " + traceback.format_exc()[-900:]


def fumaca():
    """ArxGen em R0 contra a ArxRls importada sem alteração, numa bacia de fumaça (bit a bit)"""
    CR = _modulo("comp_run_v055", E / "LEBRE-V0.55-COMP-01" / "comp_run.py"); CD = _cd()
    import diag_dados as DD
    C, pos = DD.conjuntos()
    for gid in C["fumaca"][:2]:
        s = DD.carregar(gid, C, pos); y = s["y"]
        Xs = CD._scaled_inputs(pd.DataFrame(s["X"]).ffill().fillna(0.0).to_numpy(float))
        for lam in LAMBDAS:
            a, fa, _ = CR.run_rls(Xs, y, None, lam)
            b, fb, _ = run_arx(Xs, y, ESCADA["R0"], lam)
            assert np.array_equal(a, b, equal_nan=True) and fa == fb, (gid, lam)
        print("fumaça ok: ArxGen(R0) = ArxRls bit a bit,", s["nome"], "nos três lambdas")


if __name__ == "__main__":
    conj = sys.argv[1]
    if conj == "fumaca":
        fumaca(); sys.exit(0)
    assert conj in ("A", "B")
    modelos = tuple(sys.argv[2:]) or TODOS
    assert set(modelos) <= set(TODOS) | {"R6x"}, modelos
    import diag_dados as DD
    C, _ = DD.conjuntos()
    OUT.mkdir(exist_ok=True)
    tarefas = [(conj, g, modelos) for g in C[conj]]
    print(len(tarefas), "bacias", modelos, flush=True)
    with ProcessPoolExecutor(14) as ex:
        for t, st in ex.map(job, tarefas, chunksize=1):
            print(t, st, flush=True)
