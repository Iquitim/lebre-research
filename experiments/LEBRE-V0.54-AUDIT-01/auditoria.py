"""auditoria.py — auditoria de estresse da v0.54 (PLANO_AUDITORIA.md, testes T1 a T9; o T10 roda no LEBRE Lab).
v0.54 = protótipo no commit cfe72ce (Lebre054 com m5a, m5b e m4); v0.53 = lebre==0.2.0. Séries sintéticas de
default_rng([2026101300, teste, tipo, k]).

Uso: LEBRE054_PROTO=<worktree>/experiments/LEBRE-V0.54-PROTO-01 python auditoria.py <pasta_saida> [T1 T2 ...]
"""
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

COMMIT = "cfe72ce"
BASE = 2026101300
KW054 = dict(m5a=True, m5b=True, m4=True)
TIPOS_T2 = ["constante", "picos", "entrada_travada", "faltas_em_blocos", "entradas_nan", "escala_1e-8", "escala_1e8",
            "degrau", "ar_0999", "caudas_t15", "d1", "d50_curta", "longa_200k"]
BLOCOS_T5 = [1000, 2500, 5000, 7500, 10000, 15000]
EFEITOS_T4 = [0.05, 0.1, 0.2, 0.4]
VARIANTES_T7 = [("abrupto", 20000), ("abrupto", 40000), ("gradual", 20000), ("gradual", 40000)]


def modelos():
    p = os.environ["LEBRE054_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)
    import lebre
    assert lebre.__version__ == "0.2.0"
    from lebre054.model054 import Lebre054
    return Lebre054, lebre


# ------------------------------------------------------------------ geradores
def rng_de(teste, tipo, k):
    return np.random.default_rng([BASE, teste, tipo, k])


def ar1(rng, T, d, rho=0.5):
    e = rng.standard_normal((T, d)) * math.sqrt(1 - rho ** 2); z = np.zeros((T, d))
    for t in range(1, T):
        z[t] = rho * z[t - 1] + e[t]
    return z


def lag(v, k):
    return np.r_[np.zeros(k), v[:-k]]


def base(rng, T=20000, d=3, b=0.8, ruido=None):
    X = ar1(rng, T, d)
    e = rng.standard_normal(T) if ruido is None else ruido
    return X, b * lag(X[:, 0], 3) + 0.6 * e


def serie_t2(tipo, k):
    rng = rng_de(2, TIPOS_T2.index(tipo), k)
    if tipo == "constante":
        X = ar1(rng, 20000, 3); y = np.full(20000, 5.0)
    elif tipo == "picos":
        X, y = base(rng); i = rng.choice(20000, 40, replace=False); y[i] = rng.choice([-1e6, 1e6], 40)
    elif tipo == "entrada_travada":
        X, y = base(rng); X[10000:, 0] = X[10000, 0]
    elif tipo == "faltas_em_blocos":
        X, y = base(rng)
        for s in rng.choice(np.arange(0, 20000 - 500, 500), 12, replace=False):
            y[s:s + 500] = np.nan
    elif tipo == "entradas_nan":
        X, y = base(rng); X[rng.random(X.shape) < 0.10] = np.nan
    elif tipo in ("escala_1e-8", "escala_1e8"):
        X, y = base(rng); f = 1e-8 if tipo == "escala_1e-8" else 1e8; X, y = X * f, y * f
    elif tipo == "degrau":
        X, y = base(rng); y[10000:] += 10 * np.std(y[:10000])
    elif tipo == "ar_0999":
        X = ar1(rng, 20000, 3); e = rng.standard_normal(20000); y = np.zeros(20000)
        for t in range(1, 20000):
            y[t] = 0.999 * y[t - 1] + 0.3 * (X[t - 3, 0] if t >= 3 else 0.0) + 0.5 * e[t]
    elif tipo == "caudas_t15":
        X, y = base(rng, ruido=rng.standard_t(1.5, 20000))
    elif tipo == "d1":
        X, y = base(rng, d=1)
    elif tipo == "d50_curta":
        X, y = base(rng, T=500, d=50)
    else:
        X, y = base(rng, T=200000, d=5)
    return X, y


def serie_t3(k):
    rng = rng_de(3, 0, k); T = 20000
    X = ar1(rng, T, 5); e = rng.standard_normal(T); y = np.zeros(T)
    for t in range(1, T):
        y[t] = 0.6 * y[t - 1] + e[t]
    return X, y


def serie_t4(b, k):
    rng = rng_de(4, EFEITOS_T4.index(b), k); T = 30000
    X = ar1(rng, T, 3)
    return X, b * lag(X[:, 0], 3) + rng.standard_normal(T)


def serie_t5(L, k):
    rng = rng_de(5, BLOCOS_T5.index(L), k); T = 60000
    X = ar1(rng, T, 2); on = (np.arange(T) // L) % 2 == 0
    return X, np.where(on, 0.9 * lag(X[:, 0], 3), 0.0) + 0.6 * rng.standard_normal(T)


def serie_t7(var, k):
    modo, t0 = var; rng = rng_de(7, VARIANTES_T7.index(var), k); T = t0 + 20000
    X = ar1(rng, T, 4, 0.6); e = rng.standard_normal(T); y = np.zeros(T)
    drive = 0.6 * np.mean([lag(X[:, 0], j) for j in (2, 3)], 0) + 0.4 * np.mean([lag(X[:, 1], j) for j in range(4, 8)], 0)
    for t in range(2, T):
        w = 0.0 if t < t0 else (1.0 if modo == "abrupto" else min(1.0, (t - t0) / 5000))
        a = 0.8 * X[t - 3, 0] + 0.6 * e[t]
        b = 1.2 * y[t - 1] - 0.35 * y[t - 2] + drive[t] + 0.3 * e[t]
        y[t] = (1 - w) * a + w * b
    return X, y


# ------------------------------------------------------------------ execução
def rodar(m, X, y, custo=False):
    T = len(y); f = np.full(T, np.nan); c = np.zeros(T) if custo else None; ant = 0.0
    t0 = time.perf_counter()
    for t in range(T):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]))
        if custo:
            tot = m.cost_per_step * m.n_steps; c[t] = tot - ant; ant = tot
    return f, c, time.perf_counter() - t0


def mse(y, f, ini):
    ok = np.isfinite(y) & np.isfinite(f); ok[:ini] = False
    return float(np.mean((y[ok] - f[ok]) ** 2)) if ok.any() else float("nan")


def eventos(m):
    return [dict(t=int(e.t), outcome=e.outcome, change=e.change, added=e.added, removed=e.removed) for e in m.events]


def par(X, y, ini_aval=None, seg=None):
    L054, lebre = modelos()
    d = X.shape[1]
    a, b = lebre.Lebre(d), L054(d, **KW054)
    fa, ca, ta = rodar(a, X, y, custo=True)
    fb, cb, tb = rodar(b, X, y, custo=True)
    T = len(y); ini = int(0.2 * T) if ini_aval is None else ini_aval
    obs = np.isfinite(y)
    r = dict(T=T, d=d, mse53=mse(y, fa, ini), mse54=mse(y, fb, ini),
             nao_finitas53=int((obs & ~np.isfinite(fa)).sum()), nao_finitas54=int((obs & ~np.isfinite(fb)).sum()),
             nao_finitas54_total=int((~np.isfinite(fb)).sum()), nao_finitas53_total=int((~np.isfinite(fa)).sum()),
             custo53=dict(media=float(ca.mean()), p99=float(np.quantile(ca, 0.99)), max=float(ca.max())),
             custo54=dict(media=float(cb.mean()), p99=float(np.quantile(cb, 0.99)), max=float(cb.max())),
             tempo53=ta, tempo54=tb, estrutura53=a.structure, estrutura54=b.structure,
             eventos53=eventos(a), eventos54=eventos(b),
             remocoes54=[(int(e[0]), str(e[4])) for e in b.core._core.events if e[1] == "accepted" and e[2] == "rem"],
             m1=b.m1_state)
    if seg is not None:
        r.update(mse53_seg=mse(y, fa, seg), mse54_seg=mse(y, fb, seg))
    return r


def job(arg):
    teste, chave, k = arg
    try:
        if teste == "T2":
            X, y = serie_t2(chave, k); r = par(X, y)
        elif teste == "T3":
            X, y = serie_t3(k); r = par(X, y)
        elif teste == "T4":
            X, y = serie_t4(chave, k); r = par(X, y)
        elif teste == "T5":
            X, y = serie_t5(chave, k); r = par(X, y)
        else:
            X, y = serie_t7(tuple(chave), k); r = par(X, y, seg=chave[1])
        r.update(teste=teste, chave=chave, k=k)
        return r
    except Exception as ex:                                             # noqa: BLE001
        import traceback
        return dict(teste=teste, chave=chave, k=k, erro=traceback.format_exc()[-1500:])


# ------------------------------------------------------------------ T1 e T9 (sem paralelismo)
def t1():
    L054, lebre = modelos()
    out = []
    casos = []
    rng = rng_de(1, 0, 0); X, y = base(rng, T=6000); casos.append(("sem_ciclo", X, y, {}, None))
    rng = rng_de(1, 1, 0); X, y = base(rng, T=6000); t = np.arange(6000); y = y + 2 * np.sin(2 * np.pi * t / 24)
    casos.append(("ciclo_24", X, y, dict(season=24), None))
    casos.append(("ciclo_24_168", X, y + np.where((t // 24) % 7 >= 5, 1.0, 0.0), dict(season=24, season2=168), None))
    rng = rng_de(1, 3, 0); X, y = base(rng, T=6000); y[rng.random(6000) < 0.1] = np.nan; X[rng.random(X.shape) < 0.05] = np.nan
    casos.append(("faltas", X, y, {}, None))
    rng = rng_de(1, 4, 0); X, y = base(rng, T=6000); qu = rng.random(6000) < 0.03
    casos.append(("quarentena", X, y, {}, qu))
    rng = rng_de(1, 5, 0); X, y = base(rng, T=6000, d=8); casos.append(("d8_ref_zero", X, y, dict(reference="zero"), None))

    def roda(m, X, y, qu, step=False):
        f = np.full(len(y), np.nan)
        for t in range(len(y)):
            yt = None if not math.isfinite(y[t]) else float(y[t]); q = bool(qu[t]) if qu is not None else False
            if step:
                f[t] = m.step(X[t], yt, q).value
            else:
                f[t] = m.predict(X[t]).value; m.observe(yt, q)
        return f
    for nome, X, y, kw, qu in casos:
        d = X.shape[1]
        ref = roda(lebre.Lebre(d, **kw), X, y, qu)
        off = roda(L054(d, m5a=False, m5b=False, m4=False, **kw), X, y, qu)
        core_ref = roda(lebre.LebreCore(d, season=kw.get("season"), season2=kw.get("season2")), X, y, qu)
        core_off = roda(L054(d, core_only=True, m5a=False, **kw), X, y, qu)
        v1 = roda(L054(d, **KW054, **kw), X, y, qu); v2 = roda(L054(d, **KW054, **kw), X, y, qu)
        vs = roda(L054(d, **KW054, **kw), X, y, qu, step=True)
        eq = lambda a, b: bool(np.array_equal(a, b, equal_nan=True))   # noqa: E731
        out.append(dict(caso=nome, desligada_igual_v053=eq(ref, off), core_only_igual_LebreCore=eq(core_ref, core_off),
                        deterministica=eq(v1, v2), step_igual_predict_observe=eq(v1, vs)))
    return out


def tamanhos(obj, prefixo="m", prof=0, vistos=None, out=None):
    vistos = set() if vistos is None else vistos; out = {} if out is None else out
    if id(obj) in vistos or prof > 4:
        return out
    vistos.add(id(obj))
    if isinstance(obj, (list, tuple, dict, set)) or type(obj).__name__ == "deque":
        out[prefixo] = len(obj)
        if isinstance(obj, dict):
            for k, v in list(obj.items())[:50]:
                if hasattr(v, "__dict__"):
                    tamanhos(v, f"{prefixo}[{type(v).__name__}]", prof + 1, vistos, out)
        return out
    if isinstance(obj, np.ndarray):
        out[prefixo] = int(obj.size); return out
    if hasattr(obj, "__dict__"):
        for k, v in vars(obj).items():
            tamanhos(v, f"{prefixo}.{k}", prof + 1, vistos, out)
    return out


def t9():
    L054, lebre = modelos()
    res = []
    for d in (5, 50):
        X, y = base(rng_de(9, d, 0), T=200000, d=d)
        for nome, m in (("v053", lebre.Lebre(d)), ("v054", L054(d, **KW054))):
            snap = {}
            for t in range(len(y)):
                m.predict(X[t]); m.observe(float(y[t]))
                if t + 1 in (50000, 200000):
                    snap[t + 1] = tamanhos(m)
            cresce = {k: (snap[50000].get(k), v) for k, v in snap[200000].items() if v != snap[50000].get(k)}
            res.append(dict(d=d, modelo=nome, cresce=cresce, n_contenedores=len(snap[200000])))
            print("T9", d, nome, cresce, flush=True)
    return res


if __name__ == "__main__":
    saida = sys.argv[1]; testes = sys.argv[2:] or ["T1", "T2", "T3", "T4", "T5", "T7", "T9"]
    os.makedirs(saida, exist_ok=True)
    if "T1" in testes:
        r = t1(); json.dump(r, open(os.path.join(saida, "T1.json"), "w"), indent=1); print("T1", r, flush=True)
    jobs = []
    if "T2" in testes:
        jobs += [("T2", tp, k) for tp in TIPOS_T2 for k in range(3)]
    if "T3" in testes:
        jobs += [("T3", "nulo", k) for k in range(100)]
    if "T4" in testes:
        jobs += [("T4", b, k) for b in EFEITOS_T4 for k in range(20)]
    if "T5" in testes:
        jobs += [("T5", L, k) for L in BLOCOS_T5 for k in range(10)]
    if "T7" in testes:
        jobs += [("T7", list(v), k) for v in VARIANTES_T7 for k in range(10)]
    if jobs:
        jobs.sort(key=lambda j: 0 if (j[0] == "T2" and j[1] == "longa_200k") else 1)   # a longa primeiro
        res = []
        with ProcessPoolExecutor(14) as ex:
            for r in ex.map(job, jobs, chunksize=1):
                res.append(r)
                print(r["teste"], r["chave"], r["k"], "ERRO" if "erro" in r else
                      f"{r['mse54'] / r['mse53'] if r['mse53'] else float('nan'):.4f}", flush=True)
        for tst in sorted({r["teste"] for r in res}):
            json.dump([r for r in res if r["teste"] == tst], open(os.path.join(saida, f"{tst}.json"), "w"), default=str)
    if "T9" in testes:
        json.dump(t9(), open(os.path.join(saida, "T9.json"), "w"), indent=1, default=str)
