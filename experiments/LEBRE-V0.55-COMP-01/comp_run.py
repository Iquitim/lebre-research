#!/usr/bin/env python3
"""comp_run.py — modelos externos de série completa (COMP_PLANO.md, §2) nas 84 séries da reserva final da v0.55:
REF, ARX_NLMS, NLINEAR_ONLINE, DLINEAR_ONLINE, ARX_RLS, SARIMAX_X e GBM. Grava preds/<família>__<id>.npz e .json
(fora do git). A LEBRE (v0.55 e v0.54) vem de LEBRE-V0.55-FINAL-01/preds, sem rodar de novo.
Uso: python comp_run.py
"""
import importlib.util
import json
import math
import sys
import time
import traceback
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
OUT = AQUI / "preds"
ONLINE = ["ARX_NLMS", "NLINEAR_ONLINE", "DLINEAR_ONLINE"]
LAMBDAS_RLS = (0.99, 0.999, 0.9999)


def _modulo(nome, caminho):
    sp = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def _fr():
    return _modulo("final_run_v055", RAIZ / "experiments" / "LEBRE-V0.55-FINAL-01" / "final_run.py")


def _cd():
    sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.52-PROTO-01"))
    import comp_dev
    return comp_dev


# ------------------------------------------------------------------ referência trivial da família
def ref_prev(y, season):
    yf = pd.Series(y).ffill().to_numpy()
    k = season if season else 1
    p = np.full(len(y), np.nan); p[k:] = yf[:-k]
    return p


# ------------------------------------------------------------------ ARX com mínimos quadrados recursivos
class ArxRls:
    """RLS com esquecimento em [1, x_t..x_{t-3}, y_{t-1}..y_{t-3}, y_{t-s}]; entradas padronizadas causalmente (as de
    comp_dev._scaled_inputs) e alvo na escala original (o RLS é invariante à escala do alvo; padronizar o alvo com uma
    média e um desvio lentos fazia os coeficientes derivarem em séries integradas: corrigido antes de qualquer execução
    na reserva, num teste sintético); P simetrizada a cada passo e reiniciada se perder a positividade."""

    def __init__(self, d, lam, season=None, K=3, p0=100.0):
        self.d, self.lam, self.s, self.K, self.p0 = d, lam, season, K, p0
        self.H = np.zeros((K + 1, d)); self.Y = np.zeros(max(K, season or 0) + 1)
        self.n = 1 + d * (K + 1) + K + (1 if season else 0)
        self.w = np.zeros(self.n); self.P = np.eye(self.n) * p0

    def _phi(self):
        extra = [self.Y[self.s - 1]] if self.s else []
        return np.concatenate(([1.0], self.H.ravel(), self.Y[:self.K], extra))

    def step(self, x, y):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = np.clip(np.nan_to_num(x), -8, 8)
        phi = self._phi()
        p = float(self.w @ phi)
        e = float(y) - p
        Pf = self.P @ phi; g = Pf / (self.lam + phi @ Pf)
        self.w = self.w + g * e
        P = (self.P - np.outer(g, Pf)) / self.lam; P = (P + P.T) / 2
        self.P = P if (np.isfinite(P).all() and np.diag(P).min() > 0) else np.eye(self.n) * self.p0
        self.Y = np.roll(self.Y, 1); self.Y[0] = float(y)
        return float(p), float(6 * self.n * self.n + 8 * self.n)


def run_rls(Xs, y, season, lam):
    m = ArxRls(Xs.shape[1], lam, season); pred = np.full(len(y), np.nan); fp = []
    for t in range(len(y)):
        if not np.isfinite(y[t]):
            continue
        p, f = m.step(Xs[t], float(y[t]))
        pred[t] = p; fp.append(f)
        if not np.isfinite(p) or abs(p) > 1e12:
            return pred, float("nan"), False
    return pred, float(np.mean(fp)), True


def calib_rls(Xs, y, season, idx):
    best, bm = LAMBDAS_RLS[0], float("inf")
    for lam in LAMBDAS_RLS:
        p, _, ok = run_rls(Xs[idx], y[idx], season, lam)
        mse = float(np.nanmean((y[idx] - p) ** 2)) if ok else float("inf")
        if mse < bm:
            best, bm = lam, mse
    return best


# ------------------------------------------------------------------ gradient boosting em janela crescente
def gbm_atributos(y, Xs, season):
    yf = pd.Series(y).ffill().to_numpy(); X = pd.DataFrame(Xs)
    col = {}
    d1 = pd.Series(yf).diff()
    for k in (1, 2, 3):
        col[f"dy{k}"] = d1.shift(k)                                   # Δy_{t-k} = y_{t-k} - y_{t-k-1}
    if season:
        col["sazonal"] = pd.Series(yf).shift(1) - pd.Series(yf).shift(season)
    for j in range(Xs.shape[1]):
        for k in range(4):
            col[f"x{j}_{k}"] = X[j].shift(k)
        col[f"x{j}_m4_7"] = X[j].shift(4).rolling(4).mean(); col[f"x{j}_m8_15"] = X[j].shift(8).rolling(8).mean()
    F = pd.DataFrame(col).to_numpy(float)
    alvo = yf - np.r_[np.nan, yf[:-1]]                                # y_t - y_{t-1}
    base = np.r_[np.nan, yf[:-1]]
    return F, alvo, base


def run_gbm(y, Xs, season, nc):
    from sklearn.ensemble import HistGradientBoostingRegressor
    F, alvo, base = gbm_atributos(y, Xs, season)
    T = len(y); pred = np.full(T, np.nan)
    cortes = np.unique(np.linspace(nc, T, 11).astype(int))
    ok_y = np.isfinite(y) & np.isfinite(alvo)
    for a, b in zip(cortes[:-1], cortes[1:]):
        tr = np.flatnonzero(ok_y[:a])
        if len(tr) < 50:
            continue
        m = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=31, early_stopping=False,
                                          random_state=0)
        m.fit(F[tr], alvo[tr])
        pred[a:b] = base[a:b] + m.predict(F[a:b])
    return pred, float(200 * 5), True                                 # 200 árvores × ~5 comparações (31 folhas)


# ------------------------------------------------------------------ uma série
def job(arg):
    (familia, ident), = arg
    nome = f"{familia}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    base = OUT / nome
    if base.with_suffix(".json").exists():
        return arg[0], "já feito"
    try:
        warnings.filterwarnings("ignore")
        t0 = time.time(); FR = _fr(); CD = _cd()
        s, ref = FR.carregar(familia, ident)
        y = s["y"]; X = pd.DataFrame(s["X"]).ffill().fillna(0.0).to_numpy(float)
        Xs = CD._scaled_inputs(X); season = s["season"]
        idx = CD._calib_n(y); nc = int(idx[-1]) + 1
        prev, info = {"REF": ref_prev(y, season)}, {}
        for mid in ONLINE:
            cfg = CD.calibrate(mid, Xs, y, season)
            p, fp, ok = CD.run_online(mid, Xs, y, season, cfg, 0)
            prev[mid] = p; info[mid] = dict(cfg=cfg, fp=fp, ok=ok)
        lam = calib_rls(Xs, y, season, idx)
        p, fp, ok = run_rls(Xs, y, season, lam); prev["ARX_RLS"] = p; info["ARX_RLS"] = dict(cfg={"lam": lam}, fp=fp, ok=ok)
        p, ok, msg = CD.run_airline_x(y, Xs, season); prev["SARIMAX_X"] = p; info["SARIMAX_X"] = dict(ok=ok, msg=msg)
        p, fp, ok = run_gbm(y, Xs, season, nc); prev["GBM"] = p; info["GBM"] = dict(fp=fp, ok=ok)
        np.savez_compressed(base.with_suffix(".npz"), y=y, **prev)
        base.with_suffix(".json").write_text(json.dumps(dict(familia=familia, ident=str(ident), T=len(y), season=season,
                                                             calib_fim=nc, info=info, seg=round(time.time() - t0)),
                                                        ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
        return arg[0], f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg[0], "ERRO " + traceback.format_exc()[-700:]


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    ts = _fr().tarefas()
    print(len(ts), "séries", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for tarefa, st in ex.map(job, [(t,) for t in ts], chunksize=1):
            print(tarefa, st, flush=True)
