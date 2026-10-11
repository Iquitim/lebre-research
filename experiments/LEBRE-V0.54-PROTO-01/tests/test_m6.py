"""Testes do protótipo da v0.54 (M6: ciclo como hipótese). Precisam de lebre==0.2.0.
Rodar da pasta experiments/LEBRE-V0.54-PROTO-01:  python -m pytest -q tests
Séries sintéticas com sementes 20261300 a 20261304 (faixa dos testes do protótipo, conferida como livre).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from lebre054.model054 import Lebre054  # noqa: E402


def carga(seed, T=6000):
    """ciclo diário de 24 passos com amplitude que persiste de um dia para o outro, e semana"""
    rng = np.random.default_rng(seed); t = np.arange(T); D = T // 24 + 1; A = np.ones(D)
    for k in range(1, D):
        A[k] = 1 + 0.9 * (A[k - 1] - 1) + 0.15 * rng.standard_normal()
    prof = np.sin(2 * np.pi * (t % 24) / 24 - 1) + 0.4 * np.sin(4 * np.pi * (t % 24) / 24)
    wk = np.where((t // 24) % 7 >= 5, 0.7, 1.0)
    e = np.zeros(T); u = rng.standard_normal(T)
    for k in range(1, T):
        e[k] = 0.6 * e[k - 1] + 0.15 * u[k]
    X = rng.standard_normal((T, 2))
    return X, 3 * A[t // 24] * wk * (1.2 + prof) + e


def run(m, X, y):
    return np.array([m.step(X[t], float(y[t])).value for t in range(len(y))])


def test_daily_cycle_found_without_declaring():
    X, y = carga(20261300)
    m = Lebre054(2, m6=True); f = run(m, X, y)
    assert 24 in m.core._core.cycles
    n = run(Lebre054(2), X, y)
    e = lambda g: np.mean((y[1200:] - g[1200:]) ** 2)
    assert e(f) < 0.9 * e(n)
    assert m.reference == "seasonal" and m.season == 24                # referência automática da M2


def test_no_cycle_in_autoregressive_series():
    rng = np.random.default_rng(20261301); T = 6000; u = rng.standard_normal(T); y = np.zeros(T)
    for k in range(1, T):
        y[k] = 0.8 * y[k - 1] + u[k]
    X = rng.standard_normal((T, 2))
    a, b = Lebre054(2), Lebre054(2, m6=True)
    assert np.array_equal(run(a, X, y), run(b, X, y))
    assert b.core._core.cycles == []


def test_both_cycles_declared_means_off():
    X, y = carga(20261302, T=3000)
    a, b = Lebre054(2, season=24, season2=168), Lebre054(2, season=24, season2=168, m6=True)
    assert np.array_equal(run(a, X, y), run(b, X, y))
    assert b.core._core.M.open_cands() == []
