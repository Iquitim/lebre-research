"""Testes do protótipo da v0.54 (M5b: grupos de equivalentes atualizados a cada 32 passos). Precisam de lebre==0.2.0.
Rodar da pasta experiments/LEBRE-V0.54-PROTO-01:  python -m pytest -q tests
Séries sintéticas com sementes 20261300 a 20261304 (conferidas como livres no código e nos documentos dos três repositórios).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import lebre  # noqa: E402
from lebre054.model054 import Lebre054  # noqa: E402


def muitas(seed, T, d):
    """y = 0,7 x0(t-3) + 0,5 x1(t-10) + ruído 0,7; entradas AR(1) com coeficiente 0,5 (como o cenário de custo)."""
    rng = np.random.default_rng(seed); X = np.zeros((T, d)); e = rng.standard_normal((T, d)) * np.sqrt(0.75)
    for t in range(1, T):
        X[t] = 0.5 * X[t - 1] + e[t]
    y = 0.7 * np.r_[np.zeros(3), X[:-3, 0]] + 0.5 * np.r_[np.zeros(10), X[:-10, 1]] + 0.7 * rng.standard_normal(T)
    return X, y


def run(m, X, y):
    return np.array([m.step(X[t], float(y[t])).value for t in range(len(y))])


def test_predictions_and_structure_identical():
    for seed, d, m5a in ((20261300, 5, True), (20261301, 20, True), (20261302, 20, False)):
        X, y = muitas(seed, 8000, d)
        a, b = Lebre054(d, m5a=m5a), Lebre054(d, m5a=m5a, m5b=True)
        fa, fb = run(a, X, y), run(b, X, y)
        assert np.array_equal(fa, fb)
        assert a.structure == b.structure


def test_with_missing_inputs_and_season():
    X, y = muitas(20261303, 6000, 6)
    X[np.random.default_rng(20261303).random(X.shape) < 0.05] = np.nan
    a, b = Lebre054(6, season=24), Lebre054(6, season=24, m5b=True)
    assert np.array_equal(run(a, X, y), run(b, X, y), equal_nan=True)


def test_cost_lower_with_many_inputs():
    X, y = muitas(20261301, 3000, 50)
    a, b = Lebre054(50), Lebre054(50, m5b=True)
    run(a, X, y); run(b, X, y)
    assert b.core.cost_per_step < 0.85 * a.core.cost_per_step


def test_equivalent_inputs_still_found():
    X, y = muitas(20261304, 10000, 6)
    X[:, 5] = X[:, 0] + 0.05 * np.random.default_rng(20261304).standard_normal(len(y))   # substituta quase exata de x0
    a, b = Lebre054(6), Lebre054(6, m5b=True)
    run(a, X, y); run(b, X, y)
    assert "x0" in a.structure and a.structure == b.structure
    assert set(a.equivalent_inputs("x0")) == set(b.equivalent_inputs("x0"))
    assert "x5" in b.equivalent_inputs("x0")
