"""Testes da agregação (M2, rascunho 2): garantias do artigo de de Rooij et al. (2014) e integração com o modelo."""
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
from lebre053.agregacao import Agregador                                  # noqa: E402


def _jogar(ag, perdas):
    H = 0.0
    for l in perdas:
        H += float(ag.pesos() @ l)
        ag.atualizar(l)
    return H - perdas.sum(0).min()                                        # arrependimento


def _jogar_ftl(perdas):
    L = np.zeros(perdas.shape[1]); H = 0.0
    for l in perdas:
        w = (L == L.min()).astype(float); H += float(w @ l) / w.sum(); L += l
    return H - L.min()


def _sequencias():
    rng = np.random.default_rng(7)
    yield rng.random((3000, 2))                                           # iid, sem melhor claro
    yield np.column_stack([rng.random(3000), rng.random(3000) + 0.1])     # um especialista melhor
    alt = np.array([[1.0, 0.0]] + [[1.0, 0.0], [0.0, 1.0]] * 1500)        # exemplo da seção 3.1
    yield alt
    yield rng.standard_exponential((3000, 2)) * 1e6                        # escala grande, sem limite conhecido


@pytest.mark.parametrize("i", range(4))
def test_adahedge_respeita_o_corolario_9(i):
    p = list(_sequencias())[i]
    s = p.max(1) - p.min(1); S = s.max()
    R = _jogar(Agregador(2), p)
    assert R <= math.sqrt((s ** 2).sum() * math.log(2)) + S * (4 / 3 * math.log(2) + 2) + 1e-9 * p.sum()


@pytest.mark.parametrize("i", range(4))
def test_flipflop_respeita_o_corolario_16(i):
    p = list(_sequencias())[i]
    S = (p.max(1) - p.min(1)).max()
    R = _jogar(Agregador(2, flipflop=True), p)
    assert R <= 5.64 * _jogar_ftl(p) + 3.73 * S + 1e-9 * p.sum()


def test_exemplo_da_secao_3_1():
    """Perdas (1,0) e depois alternando (1,0), (0,1), ...: FTL tem arrependimento 1/2 e AdaHedge vai a pesos (1/2, 1/2)."""
    p = np.array([[1.0, 0.0]] + [[1.0, 0.0], [0.0, 1.0]] * 500)
    assert abs(_jogar_ftl(p) - 0.5) < 1e-12
    ag = Agregador(2); _jogar(ag, p)
    assert np.allclose(ag.pesos(), 0.5, atol=0.05)
    assert _jogar(Agregador(2, flipflop=True), p) < _jogar(Agregador(2), p)


def test_invariancia_a_escala_e_translacao():
    rng = np.random.default_rng(1); p = rng.random((500, 2))
    a, b = Agregador(2, flipflop=True), Agregador(2, flipflop=True)
    for l in p:
        assert np.allclose(a.pesos(), b.pesos(), rtol=1e-9, atol=1e-12)
        a.atualizar(l); b.atualizar(1e4 * l + 3.0)


def test_comeca_com_pesos_iguais():
    assert np.array_equal(Agregador(2).pesos(), [0.5, 0.5])
    assert np.array_equal(Agregador(2, flipflop=True).pesos(), [0.5, 0.5])


def _serie(T=6000, seed=3):
    rng = np.random.default_rng(seed); X = rng.standard_normal((T, 3))
    y = 0.8 * np.r_[np.zeros(3), X[:-3, 0]] + 0.3 * rng.standard_normal(T)
    y[rng.random(T) < 0.03] = np.nan; X[rng.random(T) < 0.01, 1] = np.nan
    return X, y, rng.random(T) < 0.005


def _rodar(m, X, y, q):
    return np.array([m.step(X[t], None if not math.isfinite(y[t]) else float(y[t]), quarantine=bool(q[t])).value
                     for t in range(len(y))])


@pytest.mark.parametrize("saida", ["adahedge", "flipflop"])
@pytest.mark.parametrize("season", [None, 24])
def test_rascunho2_mantem_o_caminho_estrutural_da_v052(saida, season):
    X, y, q = _serie(T=8000)
    ref = lebre052.Lebre(3, season=season); _rodar(ref, X, y, q)
    m = Lebre053(3, season=season, referencia="persistencia", saida=saida); _rodar(m, X, y, q)
    estr = [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.events if e.change != "gate"]
    assert estr == [(e.t, e.outcome, e.change, e.added, e.removed) for e in ref.events]
    assert m.base.cost_per_step == ref.cost_per_step


@pytest.mark.parametrize("saida", ["adahedge", "flipflop"])
def test_saida_e_a_media_ponderada(saida):
    X, y, q = _serie()
    m = Lebre053(3, referencia="persistencia", saida=saida)
    for t in range(2000):
        f = m.predict(X[t])
        if math.isfinite(m._R):
            assert f.value == pytest.approx(m.pesos[0] * m._R + m.pesos[1] * m._L, rel=1e-12, abs=1e-12)
        else:
            assert f.value == m._L
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), quarantine=bool(q[t]))


@pytest.mark.parametrize("saida", ["adahedge", "flipflop"])
def test_sinal_forte_concentra_na_lebre_cedo(saida):
    X, y, q = _serie()
    m = Lebre053(3, referencia="persistencia", saida=saida)
    _rodar(m, X[:400], y[:400], np.zeros(400, bool))
    assert m.pesos[1] > 0.99


@pytest.mark.parametrize("saida", ["adahedge", "flipflop"])
def test_ruido_puro_concentra_na_referencia_zero(saida):
    rng = np.random.default_rng(11); T = 8000
    X = rng.standard_normal((T, 2)); y = rng.standard_normal(T)
    m = Lebre053(2, referencia="zero", saida=saida)
    _rodar(m, X, y, np.zeros(T, bool))
    assert m.pesos[0] > 0.9


def test_saida_invalida():
    with pytest.raises(ValueError):
        Lebre053(2, saida="media")
