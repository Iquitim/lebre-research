"""Testes do protótipo da v0.54 (M5a). Precisam da biblioteca publicada lebre==0.2.0 (a v0.53) instalada, como referência.
Rodar da pasta experiments/LEBRE-V0.54-PROTO-01:  python -m pytest -q tests
Séries sintéticas com sementes 5600 a 5604 (faixa da M5a, conferida como livre; ver ALGORITHM_SPEC_DRAFT_M5a.md).
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import lebre  # noqa: E402
from lebre054.model054 import Lebre054  # noqa: E402

assert lebre.__version__ == "0.2.0", "os testes comparam com lebre==0.2.0"


def ar1(rng, n, d, rho=0.6):
    e = rng.standard_normal((n, d)) * np.sqrt(1 - rho ** 2); z = np.zeros((n, d))
    for t in range(1, n):
        z[t] = rho * z[t - 1] + e[t]
    return z


def lag(v, k):
    return np.r_[np.zeros(k), v[:-k]]


def joint(seed, T, inicio=0):
    """y com dinâmica AR2 + bandas de entradas a partir de `inicio` (antes: só a entrada x0 com atraso 3 e ruído)."""
    rng = np.random.default_rng(seed); X = ar1(rng, T, 4); y = np.zeros(T); e = 0.3 * rng.standard_normal(T)
    drive = 0.6 * np.mean([lag(X[:, 0], k) for k in range(2, 4)], 0) + 0.4 * np.mean([lag(X[:, 1], k) for k in range(4, 8)], 0)
    for t in range(2, T):
        y[t] = (1.2 * y[t - 1] - 0.35 * y[t - 2] + drive[t] + e[t]) if t >= inicio else 0.8 * X[t - 3, 0] + 0.6 * e[t] / 0.3
    return X, y


def run(m, X, y):
    return np.array([m.step(X[t], float(y[t])).value for t in range(len(y))])


def test_copies_are_unchanged():
    for ln in (HERE / "SHA256_COPIAS.txt").read_text().splitlines():
        h, p = ln.split(" *")
        assert hashlib.sha256((HERE / p).read_bytes()).hexdigest() == h, p


def test_m5a_off_is_v053():
    X, y = joint(5600, 4000, inicio=2000)
    a = run(Lebre054(4, m5a=False), X, y); b = run(lebre.Lebre(4), X, y)
    assert np.array_equal(a, b)


def test_identical_while_never_dormant():
    X, y = joint(5601, 12000)                                    # M1 útil desde o início: não deve dormir
    m = Lebre054(4); a = run(m, X, y); b = run(lebre.Lebre(4), X, y)
    assert m.m1_state["sleeps"] == 0
    assert np.array_equal(a, b)


def test_sleeps_and_saves_cost_where_m1_has_no_weight():
    rng = np.random.default_rng(5602); T = 12000; X = ar1(rng, T, 3, 0.5)
    y = 0.8 * lag(X[:, 0], 3) + 0.6 * rng.standard_normal(T)     # tipo A05 antes da troca: a M1 não pesa
    m = Lebre054(3); r = lebre.Lebre(3)
    a = run(m, X, y); b = run(r, X, y)
    st = m.m1_state
    assert st["sleeps"] >= 1 and st["dormant"]
    assert st["m1_fp_per_step"] < r._m1.fp / r.n_steps
    assert np.all(np.isfinite(a))
    ini = T // 5
    assert np.mean((y[ini:] - a[ini:]) ** 2) <= 1.01 * np.mean((y[ini:] - b[ini:]) ** 2)


def test_wake_mechanism():
    """Mecanismo de despertar, isolado: dormente, com amostras em que E erra muito menos que L, a M1 desperta e o AdaHedge
    recomeça com sombra. (O cenário de reativação em série completa depende de a M1 voltar a ser útil; ver o registro do
    achado de 10/10/2026 em ALGORITHM_SPEC_DRAFT_M5a.md.)"""
    from lebre054.dormancy import N_WAKE, DormantPrecisionExpert
    X, y = joint(5603, 3000)                                     # M1 útil: regressão determinada, E bom
    m = Lebre054(4); run(m, X, y)
    ex = m._m1
    assert isinstance(ex, DormantPrecisionExpert) and ex.e is not None
    ex.dormant = True; ex.ema_g = ex.ema_s = None; ex.n_samples = 0
    n0 = ex.n_obs
    while ex.dormant and ex.n_obs < n0 + 8 * (N_WAKE + 50):
        L = 0.0; ex.predict(np.ones(4), L)
        e = ex.e if ex._sampled else None
        yv = (e if e is not None else 0.0) + 0.01                 # E quase exato; L = 0 longe de y
        ex.observe(yv + 1.0 if e is None else yv, L, True, 0.0)
    assert not ex.dormant and ex.wakes == 1 and ex.ag.n < 100


@pytest.mark.parametrize("ref", [None, "zero", "persistence"])
def test_finite_and_interface(ref):
    X, y = joint(5604, 3000, inicio=1500)
    m = Lebre054(4, reference=ref)
    f = run(m, X, y)
    assert np.all(np.isfinite(f)) and m.layer_weights is not None and m.cost_per_step > 0


def test_reselection_while_dormant_does_not_wake():
    """Rascunho 1: troca da seleção de entradas durante o sono não desperta; AdaHedge e estatística recomeçam."""
    X, y = joint(5603, 3000)
    X = np.c_[X, np.random.default_rng(5604).standard_normal((len(y), 3))]     # 7 entradas: a seleção (5) pode mudar
    m = Lebre054(7); run(m, X, y)
    ex = m._m1
    ex.dormant = True; ex.ema_g = 1.0; ex.ema_s = 1.0; ex.n_samples = 50
    sel_antes = tuple(ex.sel)
    ex.m[2][:] = 0.0; ex.m[2][2:] = 10.0                          # força a correlação a favorecer as entradas 2 a 6
    ex.n_sel = ex.n_obs - 10 ** 6                                 # força a nova seleção agora
    ex._select()
    assert tuple(ex.sel) != sel_antes
    assert ex.dormant and ex.wakes == 0 and ex.n_samples == 0 and ex.ema_g is None and ex.ag.n == 0
