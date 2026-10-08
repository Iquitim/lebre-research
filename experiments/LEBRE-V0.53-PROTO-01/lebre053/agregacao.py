"""Agregação de especialistas para a saída da M2, rascunho 2: AdaHedge e FlipFlop.

Fonte: de Rooij, van Erven, Grünwald e Koolen (2014), "Follow the leader if you can, hedge if you must", JMLR
15(37):1281-1316. Transcrição direta das Figuras 1 (AdaHedge) e 2 (FlipFlop) do artigo, incluindo a forma numericamente
estável de mix (subtrai o mínimo antes da exponencial). Parâmetros do FlipFlop: os do Corolário 16 (phi = 2,37,
alpha = 1,243), sem ajuste. Prioridade uniforme. As perdas não precisam de escala conhecida: o algoritmo é invariante a
translação e escala das perdas (seção 4 do artigo).
"""
import math

import numpy as np

PHI_FF, ALPHA_FF = 2.37, 1.243          # Corolário 16
# Contagem com a regra da v0.52 (1 FP por operação elementar, exp e log incluídos), K = 2: pesos na previsão (mix, 14),
# saída ponderada (3), perdas quadráticas (4), atualização (produto 3, soma 2, mix 14, incremento 3, acúmulo 1,
# comparação de regime 2, taxa 2). Total 48, tomado como teto também nos passos em que se segue o líder (mais baratos).
FP_AGREGACAO_PASSO = 48


def _mix(eta, L):
    """Pesos e perda de mistura acumulada para a taxa eta e as perdas acumuladas L (Figura 1, função mix)."""
    mn = L.min()
    if math.isinf(eta):                                       # limite: seguir o líder, empates com peso igual
        w = (L == mn).astype(float)
        s = w.sum()
        return w / s, mn
    w = np.exp(-eta * (L - mn))
    s = w.sum()
    return w / s, mn - math.log(s / len(L)) / eta


class Agregador:
    """AdaHedge (flipflop=False) ou FlipFlop (flipflop=True) para K especialistas."""

    def __init__(self, K=2, flipflop=False, phi=PHI_FF, alpha=ALPHA_FF):
        if flipflop and not (phi > 1 and alpha > 0):
            raise ValueError("FlipFlop exige phi > 1 e alpha > 0")
        self.K, self.flipflop = int(K), bool(flipflop)
        self.L = np.zeros(self.K)
        self.Delta = [0.0, 0.0]                               # [0] regime "flip" (seguir o líder), [1] "flop" (AdaHedge)
        self.escala = [phi / alpha, alpha]
        self.regime = 0 if self.flipflop else 1
        self.n = 0; self.trocas_regime = 0

    def eta(self):
        if self.regime == 0 or self.Delta[1] == 0.0:
            return math.inf
        return math.log(self.K) / self.Delta[1]

    def pesos(self):
        return _mix(self.eta(), self.L)[0]

    def atualizar(self, perdas):
        l = np.asarray(perdas, float)
        eta = self.eta()
        w, M0 = _mix(eta, self.L)
        h = float(w @ l)
        self.L = self.L + l
        _, M1 = _mix(eta, self.L)
        delta = max(0.0, h - (M1 - M0))                       # max corta violações numéricas de Jensen
        self.Delta[self.regime] += delta
        if self.flipflop and self.Delta[self.regime] > self.escala[self.regime] * self.Delta[1 - self.regime]:
            self.regime = 1 - self.regime; self.trocas_regime += 1
        self.n += 1


# ---------------------------------------------------------------------------------------------- rascunho 3
# Adamskiy, Koolen, Chernov e Vovk (2016), "A closer look at adaptive regret", JMLR 17(23): Fixed Share, equação (5),
# com taxa de troca alpha_t = 1/t (Corolário 6; alpha_1 = (N-1)/N, convenção (7)), sobre a perda de mistura.
# Contagem com a regra da v0.52, K = 2: perdas gaussianas (escalas 2, perdas 14), posterior (10), troca (8), saída (3).
FP_FIXED_SHARE_PASSO = 37


class FixedShare:
    """Fixed Share com alpha_t = 1/t para N especialistas; perdas são perdas logarítmicas (podem ser qualquer real)."""

    def __init__(self, N=2):
        self.N = int(N)
        self.u = np.full(self.N, 1.0 / self.N)
        self.n = 0; self.trocas_regime = 0

    def pesos(self):
        return self.u

    def atualizar(self, perdas):
        l = np.asarray(perdas, float)
        p = self.u * np.exp(-(l - l.min()))
        p = p / p.sum()
        self.n += 1
        a = 1.0 / (self.n + 1)                                   # alpha_{t+1}, t = rodadas concluídas
        self.u = a / (self.N - 1) + (1.0 - self.N / (self.N - 1) * a) * p


# ---------------------------------------------------------------------------------------------- rascunho 4
# AdaHedge (classe Agregador) sobre a perda recortada da v0.52, min(e^2 / B^2, 1). Acréscimo ao rascunho 2, com a regra de
# FP da v0.52: B^2 = CLIP_K^2 * max(min(s2_R, s2_L), piso^2) (3), duas divisões e dois mínimos (4), B^2 uma vez (1).
FP_RECORTE_PASSO = 8


# ---------------------------------------------------------------------------------------------- rascunho 5
# Cesa-Bianchi, Gaillard, Lugosi e Stoltz (2012), "Mirror descent meets fixed share (and feels no regret)", NeurIPS 25,
# seção 7.3, equação (13): v_{t+1} ∝ p_t^(eta_t/eta_{t-1}) exp(-eta_t l_t); p_{t+1} = alpha_t/d + (1 - alpha_t) v_{t+1};
# eta_0 = eta_1. Por padrão: alpha_t = 2/(t+1) (Corolário 6 de Adamskiy et al., 2016, nesta parametrização) e eta_t pela
# regra do AdaHedge (ln d / Delta_{t-1}) aplicada ao próprio previsor compartilhado. A combinação é nossa (ver PRA-08).
# Contagem com a regra da v0.52, K = 2, incluindo saída ponderada (3) e perdas recortadas (11): perda de mistura (13),
# pesos (11), produto h (3), incremento e acúmulo (3), taxas (4), compartilhamento (6). Total 54.
FP_COMPARTILHADA_PASSO = 54


class FixedShareAdaptativo:
    """Fixed Share com taxas variáveis (equação 13 de Cesa-Bianchi et al., 2012) para perdas em [0, 1].

    eta_fn, alpha_fn: funções do índice da rodada t (1, 2, ...); None usa a regra do AdaHedge e alpha_t = 2/(t+1).
    """

    def __init__(self, d=2, eta_fn=None, alpha_fn=None):
        self.d = int(d)
        self.p = np.full(self.d, 1.0 / self.d)
        self.eta_fn, self.alpha_fn = eta_fn, alpha_fn
        self.Delta = 0.0; self.eta_ant = None; self.t = 0; self.trocas_regime = 0
        self.etas = []; self.alphas = []                      # taxas usadas em cada rodada (para auditoria e testes)

    def pesos(self):
        return self.p

    def eta(self):
        if self.eta_fn is not None:
            return float(self.eta_fn(self.t + 1))
        return math.inf if self.Delta == 0.0 else math.log(self.d) / self.Delta

    def atualizar(self, perdas):
        l = np.asarray(perdas, float); p = self.p
        eta = self.eta()
        eta_ant = eta if self.eta_ant is None else self.eta_ant              # eta_0 = eta_1
        h = float(p @ l); mn = l.min()
        if math.isinf(eta):
            m = mn
            v = p * (l == mn)                                                # limite de p exp(-eta l)
        else:
            e = np.exp(-eta * (l - mn))
            m = mn - math.log(float(p @ e)) / eta
            r = 0.0 if math.isinf(eta_ant) else eta / eta_ant
            v = np.exp(r * np.log(p)) * e
        v = v / v.sum()
        self.Delta += max(0.0, h - m)
        self.t += 1
        a = float(self.alpha_fn(self.t)) if self.alpha_fn is not None else 2.0 / (self.t + 1)
        self.p = a / self.d + (1.0 - a) * v
        self.eta_ant = eta
        self.etas.append(eta); self.alphas.append(a)


# ------------------------------------------------------------------------------------- candidata S (switch distribution)
# van Erven, Grünwald e de Rooij (2012), "Catching up faster by switching sooner", JRSS-B 74(3), seções 2.2-2.3: mistura
# bayesiana sobre sequências de previsores, prioridade (11): mu(m) = 2^-m (cada trecho é o último com chance 1/2),
# tau(t) = 1/(t(t-1)) (o trecho atual acaba antes do passo t com chance 1/t), kappa e lambda uniformes. Algoritmo forward
# de um modelo oculto de Markov com estado (previsor, trecho final?). Perdas: -log-verossimilhança de cada previsor.
# Contagem com a regra da v0.52, K = 2: escala comum (3), perdas (8), verossimilhanças (8), atualização (4),
# transição (13), normalização (5), pesos (4), saída ponderada (3). Total 48.
FP_SWITCH_PASSO = 48


class SwitchDistribution:
    """Posterior da switch distribution sobre K previsores; atualizar(perdas) recebe -log-verossimilhanças."""

    def __init__(self, K=2):
        self.K = int(K)
        self.w = np.full((self.K, 2), 0.5 / self.K)          # [previsor, 0 = trecho não final / 1 = final]
        self.n = 0; self.trocas_regime = 0

    def pesos(self):
        p = self.w.sum(1)
        return p / p.sum()

    def atualizar(self, perdas):
        l = np.asarray(perdas, float)
        v = np.exp(-(l - l.min()))
        w = self.w * v[:, None]
        w = w / w.sum()
        self.n += 1
        h = 1.0 / (self.n + 1)                                # chance de um trecho não final acabar antes do próximo passo
        s = h * w[:, 0].sum()
        w[:, 0] *= 1.0 - h
        w += s * 0.5 / self.K                                 # novo trecho: final ou não com 1/2, previsor uniforme
        self.w = w


# ------------------------------------------------------------------------------- candidata M (troca num só sentido)
# A switch distribution acima restrita às sequências "sempre R", "sempre L" e "R até t, L a partir de t" (M2_CANDIDATA_M.md):
# prioridade (11) do artigo restrita e renormalizada: 1/3 para cada forma, instante da troca com tau(t) = 1/(t(t-1)).
# Contagem com a regra da v0.52: escala comum (3), perdas (8), verossimilhanças (8), atualização (4), transição (3),
# normalização (5), pesos (3), saída ponderada (3). Total 37.
FP_SWITCH_MONO_PASSO = 37


class SwitchMonotono:
    """Posterior sobre "sempre R", "sempre L" e "R até t, L depois"; atualizar recebe -log-verossimilhanças (R, L)."""

    def __init__(self):
        self.w = np.array([1.0, 1.0, 1.0, 0.0]) / 3.0          # [sempre R, sempre L, R com troca pendente, já trocou]
        self.n = 0; self.trocas_regime = 0

    def pesos(self):
        w = self.w
        p = np.array([w[0] + w[2], w[1] + w[3]])
        return p / p.sum()

    def atualizar(self, perdas):
        lr, ll = float(perdas[0]), float(perdas[1])
        m = min(lr, ll)
        vr, vl = math.exp(-(lr - m)), math.exp(-(ll - m))
        w = self.w * np.array([vr, vl, vr, vl])
        w = w / w.sum()
        self.n += 1
        h = 1.0 / (self.n + 1)                                 # chance de a troca ocorrer no próximo instante
        mov = h * w[2]
        w[2] -= mov; w[3] += mov
        self.w = w


class SwitchMonotonoExato:
    """Oráculo de diagnóstico (não é candidata: custo O(t) por passo). A posterior da candidata M calculada a cada passo
    com a escala atual aplicada a TODA a evidência acumulada (verossimilhança gaussiana de variância s2 sobre todos os
    dados), em vez do produto de verossimilhanças de um passo com escalas diferentes. Recebe erros quadráticos brutos."""

    def __init__(self):
        self.CR = 0.0; self.CL = 0.0; self.D = []; self.n = 0; self.trocas_regime = 0
        self._p = np.array([2.0 / 3.0, 1.0 / 3.0])

    def calcular(self, s2):
        """Pesos (R, L) para a próxima rodada, com a escala s2 (só passado)."""
        n = self.n
        if n == 0:
            self._p = np.array([2.0 / 3.0, 1.0 / 3.0])
            return self._p
        eta = 1.0 / (2.0 * s2)
        s = np.arange(2, n + 2)                                   # trocas em s = 2..n+1 (rodadas s.. usam L)
        Ds = np.array(self.D)                                     # D[s-2] = C_R(s-1) - C_L(s-1)
        logs = [math.log(1 / 3) - eta * self.CR + math.log(1.0 / (n + 1)),   # troca ainda pendente: prevê R
                math.log(1 / 3) - eta * self.CR]                                  # sempre R
        logl = np.concatenate([[math.log(1 / 3) - eta * self.CL],               # sempre L
                               math.log(1 / 3) - np.log(s * (s - 1.0)) - eta * (Ds + self.CL)])
        a = np.logaddexp.reduce(logs); b = np.logaddexp.reduce(logl)
        m = max(a, b)
        p = np.array([math.exp(a - m), math.exp(b - m)])
        self._p = p / p.sum()
        return self._p

    def pesos(self):
        return self._p

    def atualizar(self, sq):
        self.CR += float(sq[0]); self.CL += float(sq[1]); self.n += 1
        self.D.append(self.CR - self.CL)                          # D[k-1] = C_R(k) - C_L(k), usado pela troca em s = k + 1


class SwitchMonotonoJeffreys(SwitchMonotonoExato):
    """Oráculo de diagnóstico (custo O(t)): como SwitchMonotonoExato, mas a variância do ruído é integrada com a
    prioridade de Jeffreys (1/sigma) em vez de estimada: a verossimilhança marginal de uma hipótese com erro quadrático
    acumulado C em n rodadas é proporcional a C^(-n/2) (Gamma(n/2) (C/2)^(-n/2), igual para todas). Sem escala nem
    parâmetro."""

    def calcular(self, s2=None):
        n = self.n
        if n == 0:
            self._p = np.array([2.0 / 3.0, 1.0 / 3.0])
            return self._p
        h = n / 2.0
        lg = lambda c: np.log(np.maximum(c, 1e-300))
        s = np.arange(2, n + 2)
        Ds = np.array(self.D)
        logs = [math.log(1 / 3) + math.log(1.0 / (n + 1)) - h * lg(self.CR),
                math.log(1 / 3) - h * lg(self.CR)]
        logl = np.concatenate([[math.log(1 / 3) - h * lg(self.CL)],
                               math.log(1 / 3) - np.log(s * (s - 1.0)) - h * lg(Ds + self.CL)])
        a = np.logaddexp.reduce(logs); b = np.logaddexp.reduce(logl)
        m = max(a, b)
        p = np.array([math.exp(a - m), math.exp(b - m)])
        self._p = p / p.sum()
        return self._p


# ------------------------------------------------------------------------------- candidata P ((A,B)-Prod "anytime")
# Sani, Neu e Lazaric (2014), NeurIPS 27, material suplementar, apêndice B, Algoritmo 1 (Teorema 6): w_B = 1/2 fixo,
# w_A começa em 1/2; s_t = eta_t w_A / (eta_t w_A + w_B / 2); depois da rodada, com delta = f(b) - f(a) em [-1, 1]:
# w_A <- w_A (1 + eta_r delta)^(eta_novo / eta_r), eta = min(1/2, sqrt(1 / (1 + soma de delta^2))) (eta_1 = 1/2; ver
# M2_CANDIDATA_P.md sobre o mínimo com 1/2). Contagem com a regra da v0.52: taxa (6), s (4), saída misturada (3), perdas
# recortadas das duas saídas (11), atualização (7). Total 31 (D e M contados à parte).
FP_PROD_PASSO = 31


class ProdAnytime:
    """(A,B)-Prod anytime para perdas em [0, 1]; s() é a fração dada a A."""

    def __init__(self):
        self.wA = 0.5; self.wB = 0.5; self.S2 = 0.0; self.n = 0; self.trocas_regime = 0

    def eta(self):
        return min(0.5, math.sqrt(1.0 / (1.0 + self.S2)))

    def s(self):
        e = self.eta()
        return e * self.wA / (e * self.wA + self.wB / 2.0)

    def atualizar(self, fB, fA):
        d = float(fB) - float(fA)
        er = self.eta()
        self.S2 += d * d
        en = self.eta()
        self.wA *= (1.0 + er * d) ** (en / er)
        self.n += 1
