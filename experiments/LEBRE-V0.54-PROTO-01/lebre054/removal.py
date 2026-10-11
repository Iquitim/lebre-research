"""M4 da v0.54 (em desenho): remoções com evidência por episódio e orçamento próprio.

No núcleo original, a hipótese de remoção de uma unidade é persistente: acumula a evidência de todos os episódios de teste
desde a aceitação. Numa série com troca de regime, a evidência de antes da troca (quando remover era claramente pior)
pesa para sempre e a remoção nunca chega ao limiar. Aqui cada episódio de remoção é uma hipótese nova ("nos passos deste
episódio, remover não melhora a perda recortada em mais que eps"), com e-process que começa do zero e nível e-LOND de
uma sequência própria das remoções: alpha × gamma_k × (remoções aceitas + 1), limitado a 0,5. As hipóteses de adição,
troca e divisão continuam com o orçamento original, sem contar as remoções.

Como cada teste consome orçamento, um teste de remoção só abre quando a contribuição média da unidade (contrib_ema, que o
núcleo já mantém) cai abaixo de FRAC_REM × a referência: o pico desde a aceitação, que volta ao valor atual a cada teste
(cada novo teste exige mais uma queda pela metade). A regra usa só o passado. Mantidos do núcleo: intervalo mínimo
REM_PERIOD entre testes da mesma unidade, margem EPS["rem"] e regra de varredura. O ganho por passo de uma remoção
correta é pequeno na escala da perda recortada, e a evidência cresce devagar: o episódio de remoção pode durar até
T_MAX_REM passos (os demais continuam com T_MAX); a validade do e-process não depende de quando o episódio termina.
_fill e review abaixo são cópias literais do original, com as linhas marcadas "M4".
"""
from ._core import ALPHA, CHAL_WARM, COOLDOWN, EPS, M_MAX, N_MIN, REM_PERIOD, SCREEN_Q, SPLIT_Q, DECIDE_EVERY
from ._engine import ChangeEngine, Experiment, Hypothesis, gamma_k

FRAC_REM, T_MAX_REM = 0.5, 10000


class EngineM4(ChangeEngine):
    """review() é cópia literal do original; só o limite de duração passa a ser o do episódio, quando ele tem um."""

    def review(self):
        """[(decision, experiment, log_e)] with decision in {'accepted', 'closed'}; keeps the others running."""
        out, keep = [], []
        for ex in self.slots:
            le = ex.hyp.log_e(); self.fp += 3 * len(ex.hyp.lam)
            if le >= ex.hyp.log_thr:
                out.append(("accepted", ex, le))
            elif ex.n >= getattr(ex, "t_max", self.T_max) or (ex.n >= self.n_min and ex.S <= 0.0):   # M4: t_max do episódio
                out.append(("closed", ex, le))
            else:
                keep.append(ex)
        self.slots = keep
        return out


class RemovalMixin:
    def __init__(self, d, season=None, season2=None):
        super().__init__(d, season=season, season2=season2)
        self.n_hyp_rem = 0; self.n_acc_rem = 0; self.ref_contrib = {}
        e = self.engine                                              # mesmo estado inicial, review com t_max por episódio
        self.engine = EngineM4(e.alpha, e.P, e.m_slots, e.n_min, e.T_max)

    def _open(self, kind, add_key, rem_key):
        if kind != "rem":
            return super()._open(kind, add_key, rem_key)
        self.n_hyp_rem += 1
        hyp = Hypothesis(EPS["rem"], min(ALPHA * gamma_k(self.n_hyp_rem) * (self.n_acc_rem + 1), 0.5), self.n_hyp_rem)
        self.engine.k_started += 1
        ex = Experiment(kind, None, rem_key, hyp, self.t); ex.t_max = T_MAX_REM
        self.engine.slots.append(ex)
        self.last_tested[rem_key] = self.t

    def _accept(self, ex, le):
        super()._accept(ex, le)
        if ex.kind == "rem":                                         # a remoção não conta no orçamento das adições
            self.engine.n_accepted -= 1; self.n_acc_rem += 1

    def _fill(self):
        for a in self.active:                                        # M4: referência = pico desde a aceitação ou o último teste
            if a in self.contrib_ema:
                self.ref_contrib[a] = max(self.ref_contrib.get(a, 0.0), self.contrib_ema[a])
        for a in [a for a in self.ref_contrib if a not in self.active]:
            del self.ref_contrib[a]
        self.fp["control"] += 2 * len(self.active) / DECIDE_EVERY                                       # M4
        busy = {self.unit_of(k) for k in self.engine.busy_keys()}
        while self.engine.free_slots() > 0:
            due = [a for a in self.active if a not in busy and self.t - self.last_rem.get(a, -10 ** 9) >= REM_PERIOD
                   and self.t - self.last_tested.get(a, -10 ** 9) >= N_MIN
                   and self.contrib_ema.get(a, float("inf")) < FRAC_REM * self.ref_contrib.get(a, float("inf"))]   # M4
            if due:
                a = due[0]; self.last_rem[a] = self.t; self.ref_contrib[a] = self.contrib_ema[a]               # M4
                self._open("rem", None, a); busy.add(a); continue
            if any(ex.add_key and ex.k <= CHAL_WARM for ex in self.engine.slots):
                break                                                # one warm-up at a time
            cands = []
            pool = [u for u in self.units if u not in self.active and u not in busy
                    and self.t - self.last_tested.get(u, -10 ** 9) >= COOLDOWN]
            if pool:
                c = max(pool, key=self.screen_stat)
                if self.screen_stat(c) >= SCREEN_Q:
                    cands.append((self.screen_stat(c) / SCREEN_Q, "unit", c))
            sp = [k for k in self.split_keys() if self.unit_of(k) not in busy
                  and self.t - self.last_tested.get(k, -10 ** 9) >= COOLDOWN]
            if sp:
                c = max(sp, key=self.screen_stat)
                if self.screen_stat(c) >= SPLIT_Q:
                    cands.append((self.screen_stat(c) / SPLIT_Q, "split", c))
            if not cands:
                break
            _, typ, c = max(cands)
            if typ == "split":
                self._open("split", c, None)
            elif len(self.active) < M_MAX:
                self._open("add", c, None)
            else:
                a = min((k for k in self.active if k not in busy), key=lambda k: self.contrib_ema.get(k, float("inf")), default=None)
                if a is None:
                    break
                self._open("swap", c, a); busy.add(a)
            busy.add(self.unit_of(c))
            self.fp["control"] += (len(self.units) + len(self.sp)) / DECIDE_EVERY
