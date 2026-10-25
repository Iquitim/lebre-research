"""Testes do protótipo da candidata D4. Rodar da pasta experiments/LEBRE-V0.56-PROTO-02: python -m pytest tests

1. As cópias conferem com SHA256_COPIAS.txt.
2. "A" é idêntica, bit a bit, à v0.55 (Lebre055 B10 do mesmo pacote).
3. "D4" é idêntica, bit a bit, à D4 medida em experiments/LEBRE-V0.56-DEV-02 (dev2_modelos.py sobre o protótipo congelado
   em ef77728): previsões e custo.
4. A M1 não muda o núcleo: eventos do núcleo, estrutura e previsão do núcleo idênticos entre A e D4.
5. Um alvo constante (σ̂²_E = 0) não interrompe a execução.
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
from lebre056.model055 import Lebre055  # noqa: E402
from lebre056.model056d import Lebre056D  # noqa: E402


def _cenarios():
    out = []
    rng = np.random.default_rng(5675); T = 6000; X = rng.standard_normal((T, 8))
    y = 0.6 * np.r_[0.0, X[:-1, 2]] + 0.3 * np.r_[0.0, 0.0, X[:-2, 5]] + 0.4 * rng.standard_normal(T)
    out.append(("oito_entradas", X, y, None))
    rng = np.random.default_rng(5676); T = 8000; x = np.zeros((T, 3)); e = rng.standard_normal((T, 3))
    for t in range(1, T):
        x[t] = 0.6 * x[t - 1] + e[t]
    y = np.zeros(T)
    for t in range(3, T):
        y[t] = 0.85 * y[t - 1] + 0.5 * max(x[t, 0], 0) + 0.2 * x[t - 2, 0] + 0.3 * rng.standard_normal()
    y[3000:3050] = np.nan
    out.append(("tipo_vazao", x, y, None))
    rng = np.random.default_rng(5677); T = 7000; X = rng.standard_normal((T, 2))
    y = 2 * np.sin(2 * np.pi * np.arange(T) / 24) + 0.7 * np.r_[0.0, X[:-1, 0]] + 0.3 * rng.standard_normal(T)
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
def test_A_igual_a_v055(cen):
    _, X, y, season = cen
    a, b = Lebre056D(X.shape[1], season=season, variant="A"), Lebre055(X.shape[1], season=season, variant="B10")
    fa, _ = _rodar(a, X, y); fb, _ = _rodar(b, X, y)
    assert np.array_equal(fa, fb, equal_nan=True) and a.cost_per_step == b.cost_per_step


@pytest.mark.parametrize("cen", _cenarios(), ids=lambda c: c[0])
def test_D4_igual_a_medida_no_dev02(cen):
    _, X, y, season = cen
    os.environ.setdefault("LEBRE056_PROTO", str(E / "LEBRE-V0.56-PROTO-01"))
    sys.path.insert(0, str(E / "LEBRE-V0.56-DEV-02"))
    import dev2_modelos
    ref, ctx = dev2_modelos.construir("D4", X.shape[1], season=season, reference=None)
    d = Lebre056D(X.shape[1], season=season, variant="D4")
    with ctx:
        fr, _ = _rodar(ref, X, y)
    fd, _ = _rodar(d, X, y)
    assert np.array_equal(fr, fd, equal_nan=True) and ref.cost_per_step == d.cost_per_step


@pytest.mark.parametrize("cen", _cenarios(), ids=lambda c: c[0])
def test_nucleo_nao_muda(cen):
    _, X, y, season = cen
    a, d = Lebre056D(X.shape[1], season=season, variant="A"), Lebre056D(X.shape[1], season=season, variant="D4")
    fa, na = _rodar(a, X, y); fd, nd = _rodar(d, X, y)
    ev = lambda m: [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.core.events]  # noqa: E731
    assert ev(a) == ev(d) and a.structure == d.structure and np.array_equal(na, nd, equal_nan=True)
    assert not np.array_equal(fa, fd, equal_nan=True)


def test_alvo_constante_nao_interrompe():
    rng = np.random.default_rng(5678); T = 3000; X = rng.standard_normal((T, 2)); y = np.zeros(T)
    f, _ = _rodar(Lebre056D(2, variant="D4"), X, y)
    assert np.isfinite(f[200:]).all()
