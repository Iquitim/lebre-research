"""Testes do protótipo da v0.53 (M2). Rodar a partir de experiments/LEBRE-V0.53-PROTO-01: python -m pytest -q tests"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "lebre" / "src"))      # cópia de referência da lebre==0.1.0

import lebre as lebre052                                                  # noqa: E402
from lebre053 import Lebre053                                             # noqa: E402


def _serie(T=6000, seed=3, faltas=True):
    rng = np.random.default_rng(seed); X = rng.standard_normal((T, 3))
    y = 0.8 * np.r_[np.zeros(3), X[:-3, 0]] + 0.3 * rng.standard_normal(T)
    if faltas:
        y[rng.random(T) < 0.03] = np.nan; X[rng.random(T) < 0.01, 1] = np.nan
    q = rng.random(T) < 0.005
    return X, y, q


def _rodar(m, X, y, q):
    out = []
    for t in range(len(y)):
        f = m.step(X[t], None if not math.isfinite(y[t]) else float(y[t]), quarantine=bool(q[t]))
        out.append((f.value, f.lower, f.upper))
    return np.array(out)


def test_copias_identicas_a_biblioteca_congelada():
    import hashlib
    for linha in (AQUI / "SHA256_COPIAS.txt").read_text().splitlines():
        h, p = linha.split(" *")
        assert hashlib.sha256((AQUI / p).read_bytes()).hexdigest() == h


@pytest.mark.parametrize("season", [None, 24])
def test_porta_desligada_e_identica_a_v052(season):
    X, y, q = _serie()
    a = _rodar(lebre052.Lebre(3, season=season), X, y, q)
    m = Lebre053(3, season=season, porta=False)
    b = _rodar(m, X, y, q)
    assert np.array_equal(a, b, equal_nan=True)
    ref = lebre052.Lebre(3, season=season); _rodar(ref, X, y, q)
    assert [(e.t, e.outcome, e.added) for e in ref.events] == [(e.t, e.outcome, e.added) for e in m.events]
    assert ref.cost_per_step == m.cost_per_step and ref.coverage == m.coverage


def test_ruido_puro_fica_na_referencia_zero():
    rng = np.random.default_rng(11); T = 8000
    X = rng.standard_normal((T, 2)); y = rng.standard_normal(T)
    m = Lebre053(2, referencia="zero")
    saidas = _rodar(m, X, y, np.zeros(T, bool))[:, 0]
    assert m.trocas <= 1
    assert np.mean(saidas == 0.0) > 0.9


def test_sinal_forte_promove_a_lebre():
    X, y, q = _serie(faltas=False)
    m = Lebre053(3, referencia="persistencia")
    _rodar(m, X, y, q)
    portas = [e for e in m.events if e.change == "gate"]
    assert m.modo == "LEBRE" and portas and portas[0].added == "lebre" and portas[0].t < 1500


def test_saida_segue_o_modo():
    X, y, q = _serie(faltas=False)
    m = Lebre053(3, referencia="persistencia")
    for t in range(3000):
        modo = m.modo
        f = m.predict(X[t])
        if modo == "LEBRE":
            assert f.value == m._L
        else:
            assert f.value == m._R or not math.isfinite(m._R)
        m.observe(float(y[t]))


def test_argumentos_invalidos():
    with pytest.raises(ValueError):
        Lebre053(2, referencia="sazonal")
    with pytest.raises(ValueError):
        Lebre053(2, referencia="media")


@pytest.mark.parametrize("season", [None, 24])
def test_rascunho1_mantem_o_caminho_estrutural_da_v052(season):
    """Com orçamento próprio, a porta não altera eventos estruturais nem o custo da parte v0.52."""
    X, y, q = _serie(T=8000)
    ref = lebre052.Lebre(3, season=season); _rodar(ref, X, y, q)
    m = Lebre053(3, season=season, referencia="persistencia", alpha_porta=0.01, observar_quarentena_entradas=True)
    _rodar(m, X, y, q)
    estr = [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.events if e.change != "gate"]
    assert estr == [(e.t, e.outcome, e.change, e.added, e.removed) for e in ref.events]
    assert m.base.cost_per_step == ref.cost_per_step


def test_rascunho0_continua_disponivel_e_compartilha_a_sequencia():
    X, y, q = _serie(T=4000)
    m = Lebre053(3, referencia="persistencia", alpha_porta=None, observar_quarentena_entradas=False)
    _rodar(m, X, y, q)
    assert m._engine is m.base._core.engine and any(k[0] == "porta" for k in m.base._core.engine.hyps)
