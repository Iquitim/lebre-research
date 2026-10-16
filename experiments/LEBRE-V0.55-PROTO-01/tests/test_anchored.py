"""Testes do protótipo v0.55 (núcleo ancorado, rascunho 0). Sementes 5471-5476 (conferidas como não usadas em
16/10/2026). Rodar da pasta experiments/LEBRE-V0.55-PROTO-01:  python -m pytest -q tests

1. Identidade: A0 (reescrita com as alavancas desligadas) = A (v0.54 canônica), bit a bit, em previsões, intervalos,
   eventos, custo e cobertura.
2. Não vazamento: em B, B1, B2, B4, B5, B6 e B7, trocar todo o futuro (entradas e alvos depois de t0) não muda nenhuma previsão até t0.
3. Coerência: em B, B2 e B5, os pesos lentos ficam alinhados com as unidades ativas depois de cada passo, e nenhum teste
   abre na janela de assentamento.
"""
import functools
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lebre055.anchored import N_SETTLE  # noqa: E402
from lebre055.model055 import Lebre055  # noqa: E402


def ar1(rng, rho, n, d):
    e = rng.standard_normal((n, d)) * np.sqrt(1 - rho ** 2); z = np.zeros((n, d)); z[0] = rng.standard_normal(d)
    for t in range(1, n):
        z[t] = rho * z[t - 1] + e[t]
    return z


def lag(v, k):
    return np.r_[np.zeros(k), v[:-k]]


def scenarios():
    S = {}
    rng = np.random.default_rng(5471); T = 9000; X = ar1(rng, 0.7, T, 3); t = np.arange(T)
    y = 0.6 * np.mean([lag(X[:, 0], k) for k in range(4, 8)], 0) + 0.5 * np.sin(2 * np.pi * t / 24) + 0.3 * rng.standard_normal(T)
    y[3000:3040] = np.nan; q = np.zeros(T, bool); q[5000:5010] = True; X[6000, 1] = 40.0
    S["band_season_gaps"] = dict(X=X, y=y, q=q, season=24, reference=None)
    rng = np.random.default_rng(5472); T = 14000; X = ar1(rng, 0.5, T, 3)
    y = np.where(np.arange(T) < 5000, 1.0, 0.0) * lag(X[:, 1], 3) + 0.4 * lag(X[:, 2], 1) + 0.3 * rng.standard_normal(T)
    S["relation_vanishes"] = dict(X=X, y=y, q=np.zeros(T, bool), season=None, reference=None)
    rng = np.random.default_rng(5473); T = 7000; base = ar1(rng, 0.8, T, 4)
    X = np.repeat(base, 3, axis=1) + 0.2 * rng.standard_normal((T, 12))
    y = 0.7 * lag(base[:, 0], 2) + 0.3 * rng.standard_normal(T)
    S["correlated_12"] = dict(X=X, y=y, q=np.zeros(T, bool), season=None, reference=None)
    rng = np.random.default_rng(5474); T = 7000; X = ar1(rng, 0.99, T, 3)
    y = np.cumsum(0.5 * rng.standard_normal(T))
    S["random_walk_level"] = dict(X=X, y=y, q=np.zeros(T, bool), season=None, reference="persistence")
    rng = np.random.default_rng(5475); T = 9000; X = ar1(rng, 0.3, T, 2)
    y = 0.9 * lag(X[:, 0], 2) - 0.6 * lag(X[:, 0], 12) + 0.3 * rng.standard_normal(T)
    S["opposite_lags_split"] = dict(X=X, y=y, q=np.zeros(T, bool), season=None, reference=None)
    return S


SC = scenarios()


def run(name, variant, X=None, y=None, check=None):
    sc = SC[name]; X = sc["X"] if X is None else X; y = sc["y"] if y is None else y
    m = Lebre055(X.shape[1], season=sc["season"], reference=sc["reference"], variant=variant)
    f, lo, hi = (np.empty(len(y)) for _ in range(3))
    for t in range(len(y)):
        fc = m.step(X[t], None if not np.isfinite(y[t]) else float(y[t]), quarantine=bool(sc["q"][t]))
        f[t], lo[t], hi[t] = fc.value, fc.lower, fc.upper
        if check is not None:
            check(m, t)
    return m, f, lo, hi


@functools.lru_cache(maxsize=None)
def run_cached(name, variant):
    return run(name, variant)


@pytest.mark.parametrize("name", sorted(SC))
def test_identity_A0_equals_v054(name):
    ma, fa, la, ha = run_cached(name, "A")
    m0, f0, l0, h0 = run_cached(name, "A0")
    assert np.array_equal(fa, f0) and np.array_equal(la, l0, equal_nan=True) and np.array_equal(ha, h0, equal_nan=True)
    assert ma.events == m0.events and len(ma.events) > 0
    assert ma.cost_per_step == m0.cost_per_step and ma.coverage == m0.coverage


def test_scenarios_exercise_the_core():
    kinds = set()
    for name in SC:
        ma = run_cached(name, "A")[0]
        kinds |= {(e.outcome, e.change) for e in ma.events}
    assert ("accepted", "add") in kinds and ("accepted", "split") in kinds and ("accepted", "remove") in kinds


@pytest.mark.parametrize("variant", ["B", "B1", "B2", "B4", "B5", "B6", "B7"])
@pytest.mark.parametrize("name", ["band_season_gaps", "relation_vanishes"])
def test_no_leakage(name, variant):
    sc = SC[name]; T = len(sc["y"]); t0 = T // 2
    rng = np.random.default_rng(5476)
    X2, y2 = sc["X"].copy(), sc["y"].copy()
    X2[t0 + 1:] = rng.standard_normal(X2[t0 + 1:].shape) * 3      # entradas depois de t0
    y2[t0:] = rng.standard_normal(T - t0) * 5                      # alvos a partir de t0 (a previsão de t0 vem antes de y_t0)
    _, f1, l1, h1 = run_cached(name, variant)
    _, f2, l2, h2 = run(name, variant, X=X2, y=y2)
    assert np.array_equal(f1[:t0 + 1], f2[:t0 + 1])
    assert np.array_equal(l1[:t0 + 1], l2[:t0 + 1], equal_nan=True) and np.array_equal(h1[:t0 + 1], h2[:t0 + 1], equal_nan=True)
    assert not np.array_equal(f1[t0 + 1:], f2[t0 + 1:])           # o futuro trocado muda o futuro


@pytest.mark.parametrize("variant", ["B", "B2", "B5"])
@pytest.mark.parametrize("name", ["opposite_lags_split", "relation_vanishes"])
def test_slow_reference_alignment_and_settling(name, variant):
    seen = {"opened_in_settle": 0, "steps": 0}

    def check(m, t):
        c = m.core._core
        assert set(c.slow_w) == set(c.active)
        for u, st in c.active.items():
            assert len(c.slow_w[u]) == len(st["w"])
        if c.t - c.last_change < N_SETTLE:
            seen["opened_in_settle"] += sum(1 for ex in c.engine.slots if ex.t0 > c.last_change)
        seen["steps"] += 1

    m, f, _, _ = run(name, variant, check=check)
    assert np.isfinite(f).all()
    assert seen["opened_in_settle"] == 0
    assert any(e.outcome == "accepted" for e in m.events)


@pytest.mark.parametrize("name", ["opposite_lags_split", "relation_vanishes", "random_walk_level"])
def test_innovation_structure_alignment(name):
    def check(m, t):
        c = m.core._core
        assert set(c.inn_w) == set(c.active)
        for u, st in c.active.items():
            assert len(c.inn_w[u]) == len(st["w"])
        assert 0.0 <= c.wI <= 1.0

    m, f, _, _ = run(name, "B7", check=check)
    assert np.isfinite(f).all()
