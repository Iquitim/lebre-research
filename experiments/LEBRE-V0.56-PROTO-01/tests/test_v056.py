"""Testes do protótipo da v0.56. Rodar da pasta experiments/LEBRE-V0.56-PROTO-01: python -m pytest tests

1. As cópias da v0.55 conferem com SHA256_COPIAS.txt.
2. A0 (a M1 reescrita com os parâmetros da v0.55) é idêntica, bit a bit, à v0.55 canônica (A): previsões e custo.
3. C5 é idêntica, bit a bit, à variante C5 medida em experiments/LEBRE-V0.56-DEV-01 (dev_m1.py sobre o protótipo
   congelado da v0.55): previsões e custo.
4. A mudança da M1 não muda o núcleo: eventos do núcleo, estrutura e previsão do núcleo idênticos entre A e C5.
"""
import hashlib
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

AQUI = Path(__file__).resolve().parents[1]
E = AQUI.parent
sys.path.insert(0, str(AQUI))
from lebre056.model056 import Lebre056  # noqa: E402


def _cenarios():
    out = []
    rng = np.random.default_rng(5671); T = 6000; X = rng.standard_normal((T, 8))           # muitas entradas, atrasos
    y = 0.6 * np.r_[0.0, X[:-1, 2]] + 0.3 * np.r_[0.0, 0.0, X[:-2, 5]] + 0.4 * rng.standard_normal(T)
    out.append(("oito_entradas", X, y, None))
    rng = np.random.default_rng(5672); T = 8000; x = np.zeros((T, 3)); e = rng.standard_normal((T, 3))
    for t in range(1, T):
        x[t] = 0.6 * x[t - 1] + e[t]
    y = np.zeros(T)
    for t in range(3, T):                                                                   # dinâmica autorregressiva
        y[t] = 0.85 * y[t - 1] + 0.5 * max(x[t, 0], 0) + 0.2 * x[t - 2, 0] + 0.3 * rng.standard_normal()
    y[3000:3050] = np.nan                                                                   # lacuna no alvo
    out.append(("tipo_vazao", x, y, None))
    rng = np.random.default_rng(5673); T = 7000; X = rng.standard_normal((T, 2))
    s = np.sin(2 * np.pi * np.arange(T) / 24)
    y = 2 * s + 0.7 * np.r_[0.0, X[:-1, 0]] + 0.3 * rng.standard_normal(T)
    out.append(("ciclo_24", X, y, 24))
    return out


def _rodar(m, X, y):
    f = np.full(len(y), np.nan); nuc = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value; nuc[t] = m._L_core
        m.observe(None if not math.isfinite(y[t]) else float(y[t]))
    return f, nuc


def test_copias_conferem():
    for ln in (AQUI / "SHA256_COPIAS.txt").read_text().splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        h, rel = ln.split(" *")
        assert hashlib.sha256((AQUI / rel).read_bytes()).hexdigest() == h, rel


@pytest.mark.parametrize("cen", _cenarios(), ids=lambda c: c[0])
def test_A0_igual_a_v055(cen):
    _, X, y, season = cen
    a, b = Lebre056(X.shape[1], season=season, variant="A"), Lebre056(X.shape[1], season=season, variant="A0")
    fa, _ = _rodar(a, X, y); fb, _ = _rodar(b, X, y)
    assert np.array_equal(fa, fb, equal_nan=True) and a.cost_per_step == b.cost_per_step


@pytest.mark.parametrize("cen", _cenarios(), ids=lambda c: c[0])
def test_C5_igual_a_medida_no_dev01(cen):
    _, X, y, season = cen
    os.environ.setdefault("LEBRE055_PROTO", str(E / "LEBRE-V0.55-PROTO-01"))
    sys.path.insert(0, str(E / "LEBRE-V0.56-DEV-01"))
    import dev_m1
    ref = dev_m1.classes()("C5", X.shape[1], season=season, reference=None)
    c = Lebre056(X.shape[1], season=season, variant="C5")
    fr, _ = _rodar(ref, X, y); fc, _ = _rodar(c, X, y)
    assert np.array_equal(fr, fc, equal_nan=True) and ref.cost_per_step == c.cost_per_step


@pytest.mark.parametrize("cen", _cenarios(), ids=lambda c: c[0])
def test_nucleo_nao_muda(cen):
    _, X, y, season = cen
    a, c = Lebre056(X.shape[1], season=season, variant="A"), Lebre056(X.shape[1], season=season, variant="C5")
    fa, na = _rodar(a, X, y); fc, nc = _rodar(c, X, y)
    ev = lambda m: [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.core.events]  # noqa: E731
    assert ev(a) == ev(c) and a.structure == c.structure and np.array_equal(na, nc, equal_nan=True)
    assert not np.array_equal(fa, fc, equal_nan=True)                                       # a saída muda (a M1 mudou)


def test_variante_invalida_e_so_nucleo():
    with pytest.raises(ValueError):
        Lebre056(2, variant="B10")
    m = Lebre056(2, core_only=True, variant="C5")
    assert m.layer_weights is None
