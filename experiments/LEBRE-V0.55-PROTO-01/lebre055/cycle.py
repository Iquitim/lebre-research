"""M6 da v0.54 (em desenho): ciclo como hipótese do próprio mecanismo.

Para cada ciclo candidato s (CANDIDATOS, em passos) que o usuário não declarou, mantém-se o perfil por fase dos
incrementos, G_s[fase] (média exponencial, taxa 0,1, de y − último valor naquela fase, como o perfil da memória com ciclo
declarado). O perfil é o componente que só um ciclo explica: atributos de defasagem, como y(t−s), ajudam a prever
qualquer série autocorrelacionada e por isso não servem de evidência de ciclo (a exploração mostrou ciclos falsos em
séries AR(1) quando a evidência era memória sazonal completa contra memória comum).

- Triagem: correlação, em média exponencial, entre o resíduo da memória (y − m, com os ciclos já aceitos) e G_s[fase],
  feita como a triagem das entradas (peso SCREEN_W, um candidato a cada SCREEN_EVERY passos; ~χ²(1) sem ciclo); limiar
  CYC_Q. Entre os candidatos que passam, testa-se o de menor período (parcimônia; rascunho 1).
- Teste (um por vez): desafiante m + c·G_s[fase], com c aprendido por NLMS no resíduo da memória a partir de zero, contra a
  memória m, na perda recortada com a escala do próprio resíduo da memória (2 × raiz da média exponencial, taxa 0,01, de
  (y − m)², só passado). E-process do núcleo, hipótese persistente ("cycle", s) no orçamento e-LOND das adições,
  margem EPS["add"], aquecimento CHAL_WARM, regra de varredura, T_MAX e nova tentativa só depois de COOLDOWN, como nas
  adições.
- Aceito: a memória passa a ser a memória com o ciclo, a mesma de um ciclo declarado (Memory(s), ou MemoryW com os dois
  ciclos, o menor primeiro). Ela roda como sombra durante o teste, aquecida no início com a história guardada (só
  passado), e por isso não parte a frio. A evidência é do perfil (específica do ciclo); a ação é declarar o ciclo.
  Com dois ciclos na memória, a M6 para.

Na Lebre054, se o usuário não declarou ciclo nem escolheu a referência, a referência da M2 passa a ser a sazonal do
menor ciclo aceito (como acontece quando o ciclo é declarado). A memória do núcleo é envolvida (CycleMemory) antes do
primeiro passo; o núcleo não muda. Sem ciclo aceito e sem teste aberto, a previsão é a da memória original, mas a
triagem custa ~3 operações por candidato por passo.

Rascunho 1 (depois da medição M6_E1): candidatos 7, 24 e 168 (sem 12); entre os que passam na triagem, o de menor
período primeiro; um candidato só abre teste depois de 1/A_PROF = 10 visitas por fase (o perfil na sua constante de
tempo). No rascunho 0, o harmônico 12 era aceito no lugar do ciclo diário na carga, e o múltiplo 168 no lugar dele na
solar. Perfis do resíduo da memória, em vez dos incrementos, foram explorados e descartados (pioraram uma série
sintética e não fizeram o ciclo semanal entrar).
"""
import math

import numpy as np

from ._memory import Memory, MemoryW
from ._core import CHAL_WARM, CLIP_K, COOLDOWN, EPS, N_MIN, SCREEN_EVERY, SCREEN_W, T_MAX

CANDIDATOS = (7, 24, 168)        # rascunho 1: sem 12 (harmônico de 24 em dados horários; aceito no lugar do dia na M6_E1)
CYC_Q, A_PROF, MU_C = 6.63, 0.1, 0.05
LB = 2 * max(CANDIDATOS) + 2


class CycleMemory:
    """memória do núcleo + termos de perfil dos ciclos aceitos; guarda a triagem e o teste em andamento."""

    def __init__(self, M, declared):
        self.M = M; self.n = 0; self.last = None; self.yb = []
        self.declared = sorted(declared)
        self.cands = [s for s in CANDIDATOS if s not in declared] if len(declared) < 2 else []
        self.G = {s: np.zeros(s) for s in self.cands}
        self.cst = {s: [0.0, 1e-3, 1.0] for s in self.cands}
        self.acc = []                                                # ciclos aceitos
        self.test = None                                             # dict: s, c, hyp, k, n, S
        self.e2 = None; self.learn_ev = False; self.t = 0               # e2: escala do resíduo da memória (só passado)
        self.fp_extra = 0.0
        self._m0 = self._m = None; self._g = {}

    @property
    def fp(self):
        return self.M.fp + self.fp_extra + (self.test["M"].fp if self.test else 0.0)

    def _prof_feats(self):
        ph_ok = self.last is not None
        return {s: (float(self.G[s][self.n % s]) if ph_ok else 0.0) for s in self.cands}

    def predict(self):
        self._m = self.M.predict()
        self._g = self._prof_feats()
        if self.test:
            self._mc = self._m + self.test["c"] * self._g[self.test["s"]]
            self._ms = self.test["M"].predict()
            self.fp_extra += 2
        return self._m

    def update(self, y, y_hat, learn=True):
        obs = y is not None and np.isfinite(y)
        m = self._m
        if obs and learn and m is not None:
            e = y - m
            for j, s in enumerate(self.open_cands()):
                if (self.t + j) % SCREEN_EVERY == 0:
                    st = self.cst[s]; z = self._g[s]; w = SCREEN_W
                    st[0] += w * (e * z - st[0]); st[1] += w * (z * z - st[1]); st[2] += w * (e * e - st[2])
                    self.fp_extra += 10
            if self.test:
                tx = self.test; z = self._g[tx["s"]]; ec = y - self._mc
                if self.learn_ev and self.e2 is not None:
                    tx["k"] += 1
                    if tx["k"] > CHAL_WARM:
                        B2 = CLIP_K * CLIP_K * self.e2
                        d = min(e * e / B2, 1.0) - min(ec * ec / B2, 1.0) - EPS["add"]
                        tx["hyp"].observe(d); tx["S"] += d; tx["n"] += 1
                        self.fp_extra += 8
                tx["c"] += MU_C * ec * z / (z * z + self.cst[tx["s"]][1] + 1e-9)   # NLMS normalizado pela potência média
                self.fp_extra += 6
        if obs and learn and m is not None:
            self.e2 = (y - m) ** 2 if self.e2 is None else self.e2 + 1e-2 * ((y - m) ** 2 - self.e2)
            self.fp_extra += 4
        if obs and learn and self.last is not None:                  # perfis por fase dos incrementos
            for s in self.cands:
                ph = self.n % s; self.G[s][ph] += A_PROF * ((y - self.last) - self.G[s][ph])
            self.fp_extra += 4 * len(self.cands)
        self.M.update(y, m if m is not None else y_hat, learn=learn)
        if self.test:                                                # a sombra aprende como a memória
            self.test["M"].update(y, self._ms, learn=learn)
        if obs:
            self.last = float(y)
            self.yb.append(self.last)
            if len(self.yb) > LB:
                del self.yb[0]
        self.n += 1; self.t += 1

    def open_cands(self):
        return [s for s in self.cands if s not in self.acc] if len(self.declared) + len(self.acc) < 2 else []

    def shadow(self, s):
        cyc = sorted(self.declared + self.acc + [s])
        M = MemoryW(cyc[0], cyc[1]) if len(cyc) == 2 else Memory(cyc[0])
        for v in self.yb[-M.Lb:]:                                    # aquecimento com a história guardada
            M.update(v, M.predict(), learn=True)
        return M

    def stat(self, s):
        xy, xx, yy = self.cst[s]
        return xy * xy / (xx * yy + 1e-12) / (SCREEN_W / (2 - SCREEN_W))


class CycleMixin:
    def __init__(self, d, season=None, season2=None):
        super().__init__(d, season=season, season2=season2)
        self.M = CycleMemory(self.M, [s for s in (season, season2) if s])
        self.c_last = {}

    def observe(self, y, quarantine=False):
        y_ok = y is not None and math.isfinite(y)
        self.M.learn_ev = y_ok and not quarantine and not (self.t <= self.quar_until)
        super().observe(y, quarantine)

    def _decide(self):
        super()._decide()
        C = self.M; tx = C.test
        if tx:
            le = tx["hyp"].log_e(); self.engine.fp += 3 * len(tx["hyp"].lam)
            if le >= tx["hyp"].log_thr:
                C.fp_extra += C.M.fp; C.M = tx["M"]; C.acc.append(tx["s"]); C.test = None
                self.engine.n_accepted += 1
                self.engine.hyps = {k: h for k, h in self.engine.hyps.items() if h is not tx["hyp"]}
                self.events.append((self.t, "accepted", "cycle", ("cycle", tx["s"]), None, round(le, 2), tx["hyp"].n))
            elif tx["n"] >= T_MAX or (tx["n"] >= N_MIN and tx["S"] <= 0.0):
                C.fp_extra += tx["M"].fp; C.test = None
                self.events.append((self.t, "closed", "cycle", ("cycle", tx["s"]), None, round(le, 2), tx["n"]))
        if C.test is None:
            cands = [s for s in C.open_cands() if self.t - self.c_last.get(s, -10 ** 9) >= COOLDOWN
                     and C.n >= s / A_PROF]                          # rascunho 1: perfil já na sua constante de tempo
            cands = [s for s in cands if C.stat(s) >= CYC_Q]
            if cands:
                s = min(cands)                                       # rascunho 1: o menor período que passa na triagem
                C.test = dict(s=s, c=0.0, hyp=self.engine.hypothesis(("cycle", s), EPS["add"]), k=0, n=0, S=0.0,
                              M=C.shadow(s))
                self.c_last[s] = self.t

    @property
    def cycles(self):
        return sorted(self.M.declared + self.M.acc)
