"""Testes do protótipo da v0.54 (M4: remoções com evidência por episódio, orçamento próprio, abertura por queda da
contribuição e episódio de até T_MAX_REM passos). Precisam de lebre==0.2.0.
Rodar da pasta experiments/LEBRE-V0.54-PROTO-01:  python -m pytest -q tests
Séries sintéticas com sementes 20261300 a 20261304 (faixa dos testes do protótipo, conferida como livre).
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from lebre054.model054 import Lebre054  # noqa: E402


def ar1(rng, n, d, rho=0.5):
    e = rng.standard_normal((n, d)) * np.sqrt(1 - rho ** 2); z = np.zeros((n, d))
    for t in range(1, n):
        z[t] = rho * z[t - 1] + e[t]
    return z


def lag(v, k):
    return np.r_[np.zeros(k), v[:-k]]


def troca(seed, T=30000, tc=15000):
    rng = np.random.default_rng(seed); X = ar1(rng, T, 3)
    y = np.where(np.arange(T) < tc, 0.8 * lag(X[:, 0], 3), 0.8 * lag(X[:, 1], 5)) + 0.6 * rng.standard_normal(T)
    return X, y


def run(m, X, y):
    return np.array([m.step(X[t], float(y[t])).value for t in range(len(y))])


def removidas(m):
    return [(e[0], e[4]) for e in m.core._core.events if e[1] == "accepted" and e[2] == "rem"]


def test_identical_while_nothing_is_accepted():
    rng = np.random.default_rng(20261300); X = rng.standard_normal((4000, 3)); y = rng.standard_normal(4000)
    a, b = Lebre054(3), Lebre054(3, m4=True)
    assert np.array_equal(run(a, X, y), run(b, X, y))
    assert b.structure == []


def test_old_input_removed_after_regime_change_and_budgets_separate():
    X, y = troca(20261301)
    m = Lebre054(3, m4=True); run(m, X, y); c = m.core._core
    rem = removidas(m)
    assert [k for _, k in rem] == [("in", 0)] and rem[0][0] > 15000
    assert "x0" not in m.structure and "x1" in m.structure
    adds = sum(e[1] == "accepted" and e[2] != "rem" for e in c.events)
    assert c.engine.n_accepted == adds and c.n_acc_rem == 1


def test_no_removal_of_true_inputs_when_stationary():
    rng = np.random.default_rng(20261302); T = 20000; X = ar1(rng, T, 6)
    y = 0.7 * lag(X[:, 0], 3) + 0.5 * lag(X[:, 1], 10) + 0.7 * rng.standard_normal(T)
    m = Lebre054(6, m4=True); run(m, X, y)
    assert removidas(m) == []
    assert {"x0", "x1"} <= set(m.structure)


def test_combines_with_m5b():
    X, y = troca(20261303, T=8000, tc=6000)
    a, b = Lebre054(3, m4=True), Lebre054(3, m4=True, m5b=True)
    assert np.array_equal(run(a, X, y), run(b, X, y))
