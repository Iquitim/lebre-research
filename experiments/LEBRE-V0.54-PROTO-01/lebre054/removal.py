"""M4 da v0.54 (em desenho, rascunho 1): remoções com evidência por episódio, acrescentadas ao calendário original.

No núcleo original, a hipótese de remoção de uma unidade é persistente: acumula a evidência de todos os episódios de teste
desde a aceitação. Numa série com troca de regime, a evidência de antes da troca (quando remover era claramente pior)
pesa para sempre e a remoção nunca chega ao limiar.

A M4 acrescenta, sem mudar nada do calendário original de testes de remoção, um teste **disparado**: quando a
contribuição média da unidade (contrib_ema, que o núcleo já mantém) cai abaixo de FRAC_REM × a referência (o pico desde a
aceitação, que volta ao valor atual a cada teste disparado), abre-se um episódio de remoção com hipótese nova ("nos
passos deste episódio, remover não melhora a perda recortada em mais que eps"), e-process do zero e nível e-LOND de uma
sequência própria: alpha × gamma_k × (remoções disparadas aceitas + 1), limitado a 0,5. As demais hipóteses ficam com o
orçamento original, sem contar as disparadas. O episódio dura até T_MAX_REM passos e a remoção só é aceita depois de
pelo menos N_REM_MIN passos de evidência (a remoção exige pelo menos o tempo máximo de uma adição; aceitar só depois de um
mínimo é um tempo de parada válido). Entre testes disparados da mesma unidade, pelo menos REM_PERIOD passos.

Enquanto nenhum teste disparado abre, as previsões são idênticas às do núcleo original.
Rascunho 0 (medição M4_E1, não seguiu): substituía o calendário original (mudou trajetórias em B03 sem remover nada) e
aceitava remoções sem duração mínima (removia relações intermitentes nos blocos desligados: A07, +14%).
"""
from ._core import ALPHA, EPS, N_MIN, REM_PERIOD, T_MAX, DECIDE_EVERY
from ._engine import ChangeEngine, Experiment, Hypothesis, gamma_k

FRAC_REM, T_MAX_REM, N_REM_MIN = 0.5, 10000, T_MAX


class EngineM4(ChangeEngine):
    """review() é cópia literal do original; só a duração máxima e a mínima para aceitar passam a ser as do episódio,
    quando ele as tem (linhas marcadas M4)."""

    def review(self):
        """[(decision, experiment, log_e)] with decision in {'accepted', 'closed'}; keeps the others running."""
        out, keep = [], []
        for ex in self.slots:
            le = ex.hyp.log_e(); self.fp += 3 * len(ex.hyp.lam)
            if le >= ex.hyp.log_thr and ex.n >= getattr(ex, "n_min_acc", 0):                       # M4
                out.append(("accepted", ex, le))
            elif ex.n >= getattr(ex, "t_max", self.T_max) or (ex.n >= self.n_min and ex.S <= 0.0):   # M4
                out.append(("closed", ex, le))
            else:
                keep.append(ex)
        self.slots = keep
        return out


class RemovalMixin:
    def __init__(self, d, season=None, season2=None):
        super().__init__(d, season=season, season2=season2)
        self.n_hyp_rem = 0; self.n_acc_rem = 0; self.ref_contrib = {}; self.last_trig = {}
        e = self.engine                                              # mesmo estado inicial, review com limites por episódio
        self.engine = EngineM4(e.alpha, e.P, e.m_slots, e.n_min, e.T_max)

    def _open_trig(self, a):
        self.n_hyp_rem += 1
        hyp = Hypothesis(EPS["rem"], min(ALPHA * gamma_k(self.n_hyp_rem) * (self.n_acc_rem + 1), 0.5), self.n_hyp_rem)
        ex = Experiment("rem", None, a, hyp, self.t); ex.t_max = T_MAX_REM; ex.n_min_acc = N_REM_MIN; ex.trig = True
        self.engine.k_started += 1
        self.engine.slots.append(ex)
        self.last_tested[a] = self.t; self.last_trig[a] = self.t; self.ref_contrib[a] = self.contrib_ema[a]

    def _accept(self, ex, le):
        super()._accept(ex, le)
        if getattr(ex, "trig", False):                               # a remoção disparada não conta no orçamento original
            self.engine.n_accepted -= 1; self.n_acc_rem += 1

    def _fill(self):
        for a in self.active:                                        # referência = pico desde a aceitação ou o último teste
            if a in self.contrib_ema:
                self.ref_contrib[a] = max(self.ref_contrib.get(a, 0.0), self.contrib_ema[a])
        for a in [a for a in self.ref_contrib if a not in self.active]:
            del self.ref_contrib[a]
        self.fp["control"] += 2 * len(self.active) / DECIDE_EVERY
        trig = [a for a in self.active if a in self.contrib_ema
                and self.t - self.last_trig.get(a, -10 ** 9) >= REM_PERIOD
                and self.t - self.last_tested.get(a, -10 ** 9) >= N_MIN
                and self.contrib_ema[a] < FRAC_REM * self.ref_contrib.get(a, float("inf"))]
        for a in trig:                                               # o disparado tem prioridade sobre o calendário original
            outros = [ex for ex in self.engine.slots if a in {self.unit_of(k) for k in (ex.add_key, ex.rem_key) if k}]
            if outros and not all(ex.kind == "rem" and not getattr(ex, "trig", False) for ex in outros):
                continue                                             # ocupada por adição, troca, divisão ou disparado
            for ex in outros:                                        # encerra o teste periódico (a hipótese persistente fica)
                self.engine.slots.remove(ex)
                self.events.append((self.t, "superseded", ex.kind, ex.add_key, ex.rem_key, None, ex.n))
            if self.engine.free_slots() > 0:
                self._open_trig(a)
        super()._fill()                                              # calendário original, sem outra mudança
