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
from lebre053.agregacao import (Agregador, FixedShare, FixedShareAdaptativo, SwitchDistribution,  # noqa: E402
                                SwitchMonotono)


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


@pytest.mark.parametrize("saida", ["adahedge", "flipflop", "fixedshare", "adahedge_recortada", "adahedge_compartilhada",
                                   "adahedge_compartilhada_rapida", "adahedge_ref_definida",
                                   "switch", "switch_mono"])
@pytest.mark.parametrize("season", [None, 24])
def test_rascunho2_mantem_o_caminho_estrutural_da_v052(saida, season):
    X, y, q = _serie(T=8000)
    ref = lebre052.Lebre(3, season=season); _rodar(ref, X, y, q)
    m = Lebre053(3, season=season, referencia="persistencia", saida=saida); _rodar(m, X, y, q)
    estr = [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.events if e.change != "gate"]
    assert estr == [(e.t, e.outcome, e.change, e.added, e.removed) for e in ref.events]
    assert m.base.cost_per_step == ref.cost_per_step


@pytest.mark.parametrize("saida", ["adahedge", "flipflop", "fixedshare", "adahedge_recortada", "adahedge_compartilhada"])
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


@pytest.mark.parametrize("saida", ["adahedge", "flipflop", "fixedshare", "adahedge_recortada"])
def test_sinal_forte_concentra_na_lebre_cedo(saida):
    """Não se aplica ao rascunho 5: o compartilhamento mantém peso >= alpha_t/2 no outro previsor e, com o eta efetivo
    observado (~0,3), o peso de L fica em ~0,94 no passo 400 nesta série (registrado antes da medição; a medição decide)."""
    X, y, q = _serie()
    m = Lebre053(3, referencia="persistencia", saida=saida)
    _rodar(m, X[:400], y[:400], np.zeros(400, bool))
    assert m.pesos[1] > 0.99


@pytest.mark.parametrize("saida", ["adahedge", "flipflop", "fixedshare", "adahedge_recortada", "adahedge_compartilhada"])
def test_ruido_puro_concentra_na_referencia_zero(saida):
    rng = np.random.default_rng(11); T = 8000
    X = rng.standard_normal((T, 2)); y = rng.standard_normal(T)
    m = Lebre053(2, referencia="zero", saida=saida)
    _rodar(m, X, y, np.zeros(T, bool))
    assert m.pesos[0] > 0.9


def test_saida_invalida():
    with pytest.raises(ValueError):
        Lebre053(2, saida="media")


# ------------------------------------------------------------------------------------------- rascunho 3
def _perdas_mistura(fs, perdas):
    """Perda de mistura por rodada: -ln sum_n u_t^n exp(-l_t^n) (Protocolo 1 de Adamskiy et al., 2016)."""
    out = []
    for l in perdas:
        u = fs.pesos(); m = l.min()
        out.append(m - math.log(float(u @ np.exp(-(l - m)))))
        fs.atualizar(l)
    return np.array(out)


@pytest.mark.parametrize("N", [2, 3])
@pytest.mark.parametrize("seed", [0, 1])
def test_fixed_share_respeita_o_corolario_6_em_todo_intervalo(N, seed):
    rng = np.random.default_rng(seed); T = 150
    perdas = rng.standard_exponential((T, N)) * rng.choice([0.1, 1.0, 30.0], size=(T, 1))
    h = _perdas_mistura(FixedShare(N), perdas)
    H = np.r_[0, np.cumsum(h)]; Lc = np.vstack([np.zeros(N), np.cumsum(perdas, 0)])
    for t1 in range(1, T + 1):
        for t2 in range(t1, T + 1):
            reg = H[t2] - H[t1 - 1] - (Lc[t2] - Lc[t1 - 1]).min()
            lim = (math.log(N) if t1 == 1 else math.log(N - 1)) + math.log(t2)
            assert reg <= lim + 1e-9


def test_fixed_share_atinge_o_pior_caso_do_teorema_4():
    """Um bom especialista no intervalo [t1, t2], perda 'infinita' do bom na rodada anterior: regret = ln t2 (N = 2)."""
    t1, t2, M = 40, 120, 800.0
    perdas = np.array([[0.0, M]] * (t1 - 2) + [[M, 0.0]] + [[0.0, M]] * (t2 - t1 + 1))
    h = _perdas_mistura(FixedShare(2), perdas)
    reg = h[t1 - 1:t2].sum() - perdas[t1 - 1:t2].sum(0).min()
    assert reg == pytest.approx(math.log(t2), abs=1e-6)


def test_fixed_share_esquece_deficit_inicial():
    """Cenário de B02: L muito pior no início, depois muito melhor; o peso de L recupera em poucos passos."""
    fs = FixedShare(2)
    for _ in range(24):
        fs.atualizar([0.0, 1e6])
    for k in range(1, 30):
        fs.atualizar([1.0, 0.0])
        if fs.pesos()[1] > 0.9:
            break
    assert k <= 10


# ------------------------------------------------------------------------------------------- rascunho 4
def test_recortada_limita_o_deficit_de_partida():
    """Erros gigantes de L no início contam no máximo 1 por passo (perdas recortadas em [0, 1])."""
    rng = np.random.default_rng(5); T = 400
    X = rng.standard_normal((T, 1)); y = 3e4 + 50 * rng.standard_normal(T)
    m = Lebre053(1, referencia="persistencia", saida="adahedge_recortada")
    for t in range(T):
        m.predict(X[t]); m.observe(float(y[t]))
    assert np.all(m.agregador.L <= m.agregador.n + 1e-12)                  # perdas em [0, 1]


# ------------------------------------------------------------------------------------------- rascunho 5
def _cota_teorema_4(etas, alphas, t1, t2, d):
    """Lado direito do Teorema 4 de Cesa-Bianchi et al. (2012) para u_t = e_k em [t1, t2] e 0 fora (rodadas 1..T)."""
    T = len(etas); eta = lambda t: etas[t - 1]; alpha = lambda t: alphas[t - 1]
    eta_ant = lambda t: eta(1) if t == 1 else eta(t - 1)
    u = lambda t: 1.0 if t1 <= t <= t2 else 0.0
    A = (u(1) / eta(1) + sum(u(t) * (1 / eta(t) - 1 / eta(t - 1)) for t in range(2, T + 1))) * math.log(d)
    m = 1.0 if t1 >= 2 else 0.0
    B = m / eta(T) * math.log(d * (1 - alpha(T)) / alpha(T))
    C = sum(u(t) / eta(t - 1) * math.log(1 / (1 - alpha(t))) for t in range(2, T + 1))
    D = sum(eta_ant(t) / 8 * u(t) for t in range(1, T + 1))
    return A + B + C + D


@pytest.mark.parametrize("taxa", ["1/t", "1/t2"])
@pytest.mark.parametrize("c", [0.3, 1.0, 3.0])
@pytest.mark.parametrize("d", [2, 3])
def test_compartilhada_respeita_o_teorema_4_em_todo_intervalo(c, d, taxa):
    rng = np.random.default_rng(int(10 * c) + d); T = 60
    perdas = rng.random((T, d)) * (rng.random((T, 1)) < 0.8)
    perdas[T // 2:, 0] *= 0.2                                            # o melhor muda no meio
    afn = None if taxa == "1/t" else (lambda t: 2.0 / (t + 1) ** 2)
    fs = FixedShareAdaptativo(d, eta_fn=lambda t: c / math.sqrt(t), alpha_fn=afn)
    jog = []
    for l in perdas:
        jog.append(float(fs.pesos() @ l)); fs.atualizar(l)
    jog = np.array(jog)
    for t1 in range(1, T + 1):
        for t2 in range(t1, T + 1):
            for k in range(d):
                reg = jog[t1 - 1:t2].sum() - perdas[t1 - 1:t2, k].sum()
                assert reg <= _cota_teorema_4(fs.etas, fs.alphas, t1, t2, d) + 1e-9


def test_compartilhada_sem_troca_e_taxa_fixa_e_hedge():
    """Com alpha_t = 0 e eta constante, a equação (13) é o Hedge de pesos exponenciais."""
    rng = np.random.default_rng(2); perdas = rng.random((50, 2))
    fs = FixedShareAdaptativo(2, eta_fn=lambda t: 0.7, alpha_fn=lambda t: 0.0)
    L = np.zeros(2)
    for l in perdas:
        w = np.exp(-0.7 * (L - L.min())); w /= w.sum()
        assert np.allclose(fs.pesos(), w, rtol=1e-12)
        fs.atualizar(l); L += l


def test_compartilhada_taxas_nao_crescentes_e_esquece_deficit():
    fs = FixedShareAdaptativo(2)
    for _ in range(200):
        fs.atualizar([0.0, 1.0])                                         # L muito pior por 200 rodadas
    for k in range(1, 400):
        fs.atualizar([0.6, 0.1])                                         # depois L melhor
        if fs.pesos()[1] > 0.9:
            break
    assert all(a >= b for a, b in zip(fs.etas, fs.etas[1:]))
    assert all(a >= b for a, b in zip(fs.alphas, fs.alphas[1:]))
    assert k < 200                                                       # recupera antes de igualar o déficit


# ------------------------------------------------------------------------------- desenvolvimento pós-rascunho 6
def test_ref_definida_espera_um_ciclo_completo():
    rng = np.random.default_rng(4); T = 200
    X = rng.standard_normal((T, 1)); y = np.sin(np.arange(T) * 2 * np.pi / 24) + 0.1 * rng.standard_normal(T)
    m = Lebre053(1, season=24, referencia="sazonal", saida="adahedge_ref_definida")
    for t in range(T):
        f = m.predict(X[t])
        if t < 24:
            assert m.pesos is None and f.value == m._L and m.agregador.n == 0
        m.observe(float(y[t]))
    assert m.agregador.n == T - 24


# ------------------------------------------------------------------------------------- candidata S (switch distribution)
def _enumeracao(perdas, K):
    """Pesos preditivos da switch distribution por enumeração de todos os prefixos de sequências de troca, com a
    prioridade das equações (10)-(11) de van Erven et al. (2012): mu(m) = 2^-m, tau(t) = 1/(t(t-1)), kappa e lambda
    uniformes. Independente do algoritmo forward: usa P(Z > T | Z > t_j) = t_j / T e tau(t | Z > t_j) = t_j/(t(t-1))."""
    import itertools
    T = len(perdas)
    out = np.zeros((T, K))
    for nsw in range(T):                                     # número de trocas dentro do horizonte
        for tempos in itertools.combinations(range(2, T + 1), nsw):
            ts = (1,) + tempos
            for ks in itertools.product(range(K), repeat=nsw + 1):
                pri = 1.0
                for j in range(nsw):                         # trechos não finais que terminam dentro do horizonte
                    pri *= 0.5 / K * ts[j] / (ts[j + 1] * (ts[j + 1] - 1))
                tj = ts[-1]                                  # último trecho começado: final, ou não final que acaba depois de T
                pri *= 0.5 / K + 0.5 / K * tj / T
                caminho = [ks[max(j for j in range(nsw + 1) if ts[j] <= t)] for t in range(1, T + 1)]
                verossim = 1.0
                for t in range(T):
                    out[t, caminho[t]] += pri * verossim
                    verossim *= math.exp(-perdas[t][caminho[t]])
    return out / out.sum(1, keepdims=True)


@pytest.mark.parametrize("K", [2, 3])
def test_switch_igual_a_enumeracao_direta(K):
    rng = np.random.default_rng(K); T = 7
    perdas = rng.exponential(1.0, (T, K)) * 2
    sw = SwitchDistribution(K); fw = []
    for l in perdas:
        fw.append(sw.pesos().copy()); sw.atualizar(l)
    assert np.allclose(np.array(fw), _enumeracao(perdas, K), rtol=1e-10, atol=1e-12)


def test_switch_domina_cada_sequencia_pela_prioridade():
    """Perda logarítmica acumulada da mistura <= perda de uma sequência com uma troca em t + custo -ln pi."""
    rng = np.random.default_rng(9); T = 400
    perdas = np.column_stack([rng.exponential(1.0, T), rng.exponential(1.0, T)])
    perdas[:150, 1] += 3.0; perdas[150:, 0] += 3.0                      # o melhor muda em t = 151
    sw = SwitchDistribution(2); mix = 0.0
    for l in perdas:
        mix += -math.log(float(sw.pesos() @ np.exp(-l))); sw.atualizar(l)
    seq = perdas[:150, 0].sum() + perdas[150:, 1].sum()
    t2 = 151
    custo = -math.log(0.5 / 2 * 1.0 / (t2 * (t2 - 1)) * 0.5 / 2)     # 2 trechos: 1o não final, troca em t2, 2o final
    assert mix <= seq + custo + 1e-9


def test_switch_esquece_fase_de_aprendizado():
    """Cenário de Abaiara: L muito pior por 800 passos, depois bem melhor; o peso de L passa de 0,9 logo depois."""
    sw = SwitchDistribution(2)
    for _ in range(800):
        sw.atualizar([0.5, 20.0])
    for k in range(1, 200):
        sw.atualizar([2.0, 0.5])
        if sw.pesos()[1] > 0.9:
            break
    assert k <= 20


# ------------------------------------------------------------------------------- candidata M (troca num só sentido)
def test_switch_mono_igual_a_enumeracao_direta():
    """Prioridade: 1/3 sempre R, 1/3 sempre L, 1/3 * 1/(t(t-1)) para trocar em t >= 2; trocas depois de T somam 1/(3T)."""
    rng = np.random.default_rng(12); T = 9
    perdas = rng.exponential(1.0, (T, 2)) * 2
    hip = [(1 / 3, [0] * T), (1 / 3, [1] * T), (1 / (3 * T), [0] * T)]
    hip += [(1 / (3 * t * (t - 1)), [0] * (t - 1) + [1] * (T - t + 1)) for t in range(2, T + 1)]
    esperado = np.zeros((T, 2))
    for pri, cam in hip:
        v = pri
        for t in range(T):
            esperado[t, cam[t]] += v
            v *= math.exp(-perdas[t][cam[t]])
    esperado /= esperado.sum(1, keepdims=True)
    sw = SwitchMonotono(); fw = []
    for l in perdas:
        fw.append(sw.pesos().copy()); sw.atualizar(l)
    assert np.allclose(np.array(fw), esperado, rtol=1e-10, atol=1e-12)


def test_switch_mono_esquece_aprendizado_e_nao_volta_por_erro_isolado():
    sw = SwitchMonotono()
    for _ in range(800):
        sw.atualizar([0.5, 20.0])                                  # L muito pior (aprendendo)
    for k in range(1, 200):
        sw.atualizar([2.0, 0.5])                                   # L melhor
        if sw.pesos()[1] > 0.9:
            break
    assert k <= 20
    for _ in range(300):
        sw.atualizar([2.0, 0.5])
    sw.atualizar([0.5, 30.0])                                      # um erro isolado enorme de L
    assert sw.pesos()[1] > 0.99
