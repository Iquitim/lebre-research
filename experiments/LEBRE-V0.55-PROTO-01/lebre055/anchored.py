"""Núcleo ancorado da v0.55 (rascunho 0 de experiments/LEBRE-V0.55-DESIGN-NOTE-01/DESIGN_NOTE.md, §4).

Duas alavancas, cada uma com a sua chave (atributos de classe):
- ANCHOR (âncora na memória): a estrutura aprende a inovação da memória, r = y − m, e a previsão de nível da estrutura
  passa a ser m + ŝ. A combinação do núcleo, L = m + wS·(nível − m), usa as mesmas constantes. Os testes comparam com
  m + ŝ.
- SLOW (referência lenta dos testes): uma cópia dos pesos da estrutura, aprendida por NLMS com μ_ref = 0,01 sobre os
  mesmos atributos e o seu próprio resíduo, é a referência R contra a qual desafiantes e remoções são medidos. A
  previsão viva continua com μ = 0,05. Nos primeiros N_SETTLE passos, a cópia lenta acompanha a rápida (cópia a cada
  passo) e nenhum teste abre. Depois de cada mudança aceita, nenhum teste novo abre por N_SETTLE passos, e a unidade
  aceita entra na cópia lenta com os pesos do desafiante.

O resto é o núcleo da v0.54, sem mudança. Com ANCHOR e SLOW falsos, predict e observe abaixo são cópias literais dos do
núcleo (`_core.py`), na mesma ordem de operações. A variante A0 do model055 confere isso bit a bit (teste de
identidade).

Desvio declarado: durante a janela de assentamento, `_fill` não roda, e isso inclui a atualização do pico de
contribuição da M4.

Rascunho 1 (16/10/2026, depois do teste de fumaça nos cenários dos testes, sementes 5471-5475, antes de qualquer
medição registrada): com a âncora, a estrutura recebe também os atributos da memória φ, normalizados pela raiz da média
exponencial de ‖φ‖²/k que a própria memória mantém (só passado). No rascunho 0, a estrutura aprendia r = y − m sem
poder corrigir os coeficientes da memória. Esses coeficientes são ajustados só com o passado do alvo e saem enviesados
quando o alvo depende das entradas (viés de variável omitida; Frisch–Waugh–Lovell: residualizar só o alvo, sem os
regressores da primeira etapa na segunda, dá estimativa enviesada). O erro ficava alto mesmo com a estrutura certa
aceita (0,31 contra 0,09 de MSE no cenário de atrasos opostos). Com φ na estrutura, o ajuste volta a ser conjunto:
nível = m + ŝ + w_φ·φ. Isso também é o que a hipótese (A2) do alvo teórico pede.

Rascunho 2 (16/10/2026, mesmo teste de fumaça): o rascunho 1 mal melhorou (MSE 0,43 → 0,35 contra 0,17). Com a
memória congelada em persistência pura, a perda continuou (0,20 contra 0,09). A causa é aprender a estrutura sobre a
inovação: o NLMS precisa cancelar yₜ₋₁ com coeficiente −1 sobre uma entrada padronizada e faz isso mal. A âncora na
previsão viva tem custo de precisão. Nova chave REF_CORE: a previsão viva fica a da v0.54, e só a **referência dos
testes** passa a ser a previsão combinada do núcleo, Rₜ = mₜ + wS·(sₜ − mₜ), que já contém a memória (com raiz
unitária). A remoção de uma unidade desconta wS × a sua contribuição; o desafiante de adição corrige R diretamente
(gₜ = Rₜ + aₜ). Com SLOW, sₜ na referência é a cópia lenta. Desvio declarado: os pesos aceitos entram em s como hoje,
embora o desafiante tenha aprendido a corrigir R.

Rascunho 3 (16/10/2026, depois da D1 do LEBRE Lab, analises/D1_V055_RESULTADO.md): B4 eliminou as entradas externas
espúrias em séries integradas, mas também barrou unidades **internas** (o passado do próprio alvo) que melhoram a
previsão viva quando a memória é fraca. Nova chave REF_SPLIT:
- unidades **externas** (entradas x0, …, x_{d−1} e as suas divisões) são testadas contra a previsão do núcleo
  R = m + wS·(s − m), e as suas remoções descontam wS × a contribuição;
- unidades **internas** (o passado do alvo, o estado residual e as divisões do passado do alvo) são testadas contra s,
  como na v0.54.
A triagem segue a mesma separação: entradas externas com o resíduo y − R; passado do alvo, estado residual e divisões
internas com y − s. Numa troca, o tipo é o da unidade que entra. A escala B vem de y − R.

Rascunho 4 (16/10/2026, depois da D2 do LEBRE Lab, analises/D2_V055_RESULTADO.md): numa série integrada, a estrutura de
nível perde para a memória (wS ≈ 0), e a informação de uma entrada verdadeira sobre as diferenças não chega à previsão,
nem na v0.54 nem em B6. Nova chave INNOV (sobre REF_SPLIT): um terceiro especialista, a **estrutura de inovação** ŝ_Δ,
prevê r = y − m com **as mesmas unidades aceitas e os mesmos atributos** da estrutura de nível, só com pesos próprios
(NLMS μ = 0,05). Uma descoberta serve às duas, sem uma segunda triagem. A combinação é aninhada:
- L₁ = m + wS·(s − m), o núcleo da v0.54;
- L = L₁ + wI·((m + ŝ_Δ) − L₁), com wI pela mesma média dinâmica (λ = 0,99, η = 0,5, atualizada a cada 8 passos) entre
  L₁ e m + ŝ_Δ.
Onde a inovação não ajuda, wI → 0 e o núcleo volta a ser L₁. A referência das unidades externas é L, e a contribuição
descontada de uma unidade externa é exata: (1 − wI)·wS·c_s + wI·c_Δ. As unidades internas continuam contra s. Uma
unidade aceita entra nas duas estruturas com os pesos do desafiante; divisões e remoções são aplicadas às duas.
Na fumaça do rascunho 0 (cascata), a estrutura de inovação errava onde precisava cancelar yₜ₋₁. Aqui ela não substitui
nada: só ganha peso onde ajuda.
"""
import math

import numpy as np

from ._core import (ALPHA_COV, BANDS, CHAL_WARM, CLIP_K, CLIP_X, DECIDE_EVERY, ETA, EVERY, GAMMA_Q, LAM, MU, OUT_MARGIN,
                    OUT_RHO, PEAK_UNTIL, POLES, SCALE_FLOOR, SCREEN_EVERY, SCREEN_W, halves)
from .screening import SE_EQ

MU_REF, N_SETTLE = 0.01, 500


class AnchoredMixin:
    ANCHOR = False
    SLOW = False
    REF_CORE = False
    REF_SPLIT = False
    INNOV = False
    MU_REF = MU_REF
    N_SETTLE = N_SETTLE

    def __init__(self, d, season=None, season2=None):
        super().__init__(d, season=season, season2=season2)
        self.base_s = self.base.copy(); self.slow_w = {}           # cópia lenta: base e pesos por unidade ativa
        self.last_change = 0                                        # instante da última mudança aceita (o início conta)
        self._refs = None; self.res_prev_int = 0.0                  # rascunho 3: referência por experimento
        self.base_i = self.base.copy(); self.inn_w = {}             # rascunho 4: estrutura de inovação
        self.Di = 0.0; self.wI = 0.5; self._inn = None
        k = len(self.M.feats)
        self.wphi = np.zeros(k); self.wphi_s = np.zeros(k); self._ph = np.zeros(k)   # rascunho 1: atributos da memória

    # ---------------- referência lenta
    def _sync_slow(self):
        self.base_s = self.base.copy(); self.slow_w = {u: np.array(st["w"], float) for u, st in self.active.items()}
        self.wphi_s = self.wphi.copy()

    def _phi(self):
        """atributos da memória deste passo, normalizados por uma escala só do passado (zeros antes de existirem)"""
        M = self.M
        if M.phi is None:
            return np.zeros(len(M.feats))
        sc = math.sqrt(M.pp_ema / len(M.phi)) if M.pp_ema else 1.0
        return M.phi / max(sc, 1e-12)

    def _wref(self, u):
        return self.slow_w[u] if self.SLOW else self.active[u]["w"]

    def _internal(self, ex):
        """unidade interna (passado do alvo, estado residual e divisões do passado do alvo); numa troca, a que entra"""
        u = self.unit_of(ex.add_key) if ex.add_key else ex.rem_key
        return u[0] == "res" or (u[0] == "in" and u[1] == self.d - 1)

    def _contrib_L(self, u):
        """contribuição exata da unidade u na previsão do núcleo com o terceiro especialista (rascunho 4)"""
        b = self.block(u)
        return (1.0 - self.wI) * self.wS * float(self.active[u]["w"] @ b) + self.wI * float(self.inn_w[u] @ b)

    def _contrib_L_seg(self, key):
        i, sg = key[1], key[2:]
        u = ("in", i); st = self.active[u]; j = st["segs"].index(sg); mu_ = self._mean(i, sg)
        return (1.0 - self.wI) * self.wS * float(st["w"][j]) * mu_ + self.wI * float(self.inn_w[u][j]) * mu_

    def _seg_contrib_ref(self, key):
        i, sg = key[1], key[2:]
        st = self.active[("in", i)]
        return float(self._wref(("in", i))[st["segs"].index(sg)]) * self._mean(i, sg)

    # ---------------- one step, split in two halves
    def predict(self, x):
        if self._pending is not None:
            raise RuntimeError("predict() called twice without observe()")
        v = self.ylast
        x = np.append(np.asarray(x, float), (v - self.ym) / math.sqrt(self.yv + 1e-6))
        dlt = v - self.ym; self.ym += 1e-4 * dlt
        self.yv = max((1 - 1e-4) * self.yv + 1e-4 * (v - self.ym) * dlt, 1e-4); self.fp["structure"] += 9
        x = np.nan_to_num(x)
        if np.any(np.abs(x) > CLIP_X):
            self.quar_until = self.t + self.L
        x = np.clip(x, -CLIP_X, CLIP_X)
        self._shift(x)
        m = self.M.predict()
        s, xb = self._struct_pred(x)
        if self.ANCHOR:
            self._ph = self._phi()
            s = m + s + float(self.wphi @ self._ph)                 # nível: memória + estrutura sobre a inovação
            self.fp["structure"] += 2 * len(self._ph) + 3
        f = m + self.wS * (s - m)
        if self.INNOV:                                              # rascunho 4: terceiro especialista, aninhado
            si = float(self.base_i @ xb) + sum(float(self.inn_w[u] @ self.block(u)) for u in self.active)
            L1, Li = f, m + si
            f = L1 + self.wI * (Li - L1); self._inn = (L1, Li)
            self.fp["structure"] += 2 * (self.d + 1) + sum(3 * len(st["w"]) for st in self.active.values()) + 4
        f_core = f
        if self.env_n >= 50:
            w_ = OUT_MARGIN * (self.env_hi - self.env_lo)
            fc = min(max(f, self.env_lo - w_), self.env_hi + w_) if math.isfinite(f) else self.last_obs
            self.n_clipped += fc != f; f = fc; self.fp["control"] += 5
        if self.SLOW:
            if self.t < self.N_SETTLE:
                self._sync_slow()
            ss = float(self.base_s @ xb) + sum(float(self.slow_w[u] @ self.block(u)) for u in self.active)
            self.fp["structure"] += 2 * (self.d + 1) + sum(3 * len(st["w"]) for st in self.active.values())
            ref = m + ss + float(self.wphi_s @ self._ph) if self.ANCHOR else ss
        else:
            ref = s
        kr = 1.0                                                    # fator das contribuições descontadas
        if self.REF_CORE:
            ref = m + self.wS * (ref - m); kr = self.wS              # rascunho 2: referência = previsão do núcleo
        outs, rrs = [], []
        if self.REF_SPLIT:                                          # rascunho 3: referência pelo tipo da unidade
            refL = f_core if self.INNOV else m + self.wS * (s - m)
            self._refs = []
            for ex in self.engine.slots:
                internal = self._internal(ex)
                rx, kx = (s, 1.0) if internal else (refL, self.wS)
                self._refs.append(rx)
                if ex.kind == "split":
                    if self.INNOV and not internal:
                        c = self._contrib_L_seg(ex.add_key)
                    else:
                        c = kx * self._seg_contrib_ref(ex.add_key)
                    outs.append(rx - c + float(ex.w @ self._cf(ex))); rrs.append(c)
                    continue
                a = float(ex.w @ self._cf(ex)) if ex.add_key else 0.0
                if ex.rem_key and self.INNOV and not internal:
                    rm = self._contrib_L(ex.rem_key)
                else:
                    rm = kx * float(self._wref(ex.rem_key) @ self.block(ex.rem_key)) if ex.rem_key else 0.0
                outs.append(rx + a - rm); rrs.append(rm)
            ref = refL
            self.fp["experiments"] += 6 * len(outs)
            self._pending = (xb, m, s, f, ref, outs, rrs)
            return f
        for ex in self.engine.slots:
            if ex.kind == "split":
                c = kr * self._seg_contrib_ref(ex.add_key) if self.REF_CORE else self._seg_contrib_ref(ex.add_key)
                outs.append(ref - c + float(ex.w @ self._cf(ex))); rrs.append(c)
                continue
            a = float(ex.w @ self._cf(ex)) if ex.add_key else 0.0
            r = float(self._wref(ex.rem_key) @ self.block(ex.rem_key)) if ex.rem_key else 0.0
            if self.REF_CORE:
                r = kr * r
            outs.append(ref + a - r); rrs.append(r)
        self.fp["experiments"] += 6 * len(outs)
        self._pending = (xb, m, s, f, ref, outs, rrs)
        return f

    def observe(self, y, quarantine=False):
        if self._pending is None:
            raise RuntimeError("observe() called without a preceding predict()")
        xb, m, s, f, ref, outs, rrs = self._pending; self._pending = None
        y_ok = y is not None and np.isfinite(y)
        mem_learn = y_ok and not quarantine
        learn = mem_learn and not (self.t <= self.quar_until)
        if y_ok:
            e = y - f; er = y - ref
            self.e2r = er * er if self.e2r is None else self.e2r + (1 - LAM) * (er * er - self.e2r)
            if self.y_sm is None:
                self.y_sm = y; self.n_y = 0
            self.n_y += 1; ry = max(1e-4, 1.0 / self.n_y)
            dy = y - self.y_sm; self.y_sm += ry * dy; self.y_sv += ry * (dy * (y - self.y_sm) - self.y_sv)
            floor = SCALE_FLOOR * math.sqrt(max(self.y_sv, 0.0)) if self.t >= 200 else 0.0
            B = CLIP_K * max(self.sigr, floor)
            self.fp["control"] += 8
            lf = min(er * er / (B * B), 1.0)
            res = y - s
            res_ref = y - ref if (self.SLOW or self.REF_CORE or self.REF_SPLIT) else res   # resíduo da referência dos testes
            refs = self._refs if self.REF_SPLIT else None
            if learn:
                for j, (ex, g, back) in enumerate(zip(self.engine.slots, outs, rrs)):
                    ex.k += 1
                    lfx = lf if refs is None else min((y - refs[j]) ** 2 / (B * B), 1.0)
                    if ex.k > CHAL_WARM or not ex.add_key:
                        ex.observe(lfx - min((y - g) ** 2 / (B * B), 1.0) - ex.eps)
                    if ex.add_key:                                   # RLS on the residual the change would explain
                        rr = (res_ref if refs is None else y - refs[j]) + back
                        if ex.add_key[0] == "in" and ex.k <= PEAK_UNTIL:
                            self._peak_stats(ex, rr)
                        fx = self._cf(ex)
                        lam_ = 1.0
                        Pf = ex.P @ fx; kg = Pf / (lam_ + fx @ Pf)
                        ex.w = ex.w + kg * (rr - ex.w @ fx); ex.P = (ex.P - np.outer(kg, Pf)) / lam_
                        self.fp["experiments"] += 4 * len(fx) ** 2 + 6 * len(fx)
                self.fp["experiments"] += 8 * len(outs)
                blocks = {u: self.block(u) for u in self.active}
                bpow = sum(float(b @ b) for b in blocks.values())
                den = float(xb @ xb) + bpow + 1e-6
                if self.ANCHOR:
                    den += float(self._ph @ self._ph)
                g_ = MU * res / den
                self.base += g_ * xb
                if self.ANCHOR:
                    self.wphi = self.wphi + g_ * self._ph
                for u, b in blocks.items():
                    st = self.active[u]; st["w"] = st["w"] + g_ * b
                    c = abs(float(st["w"] @ b))
                    self.contrib_ema[u] = c if u not in self.contrib_ema else self.contrib_ema[u] + 0.01 * (c - self.contrib_ema[u])
                self.fp["structure"] += 4 * (len(xb) + sum(len(b) for b in blocks.values())) + 4
                if self.INNOV:                                       # rascunho 4: NLMS da estrutura de inovação
                    gi = MU * (y - self._inn[1]) / den
                    self.base_i += gi * xb
                    for u, b in blocks.items():
                        self.inn_w[u] = self.inn_w[u] + gi * b
                    self.fp["structure"] += 4 * (len(xb) + sum(len(b) for b in blocks.values())) + 4
                if self.SLOW and self.t >= self.N_SETTLE:            # NLMS lento da referência, sobre o próprio resíduo
                    gs = self.MU_REF * res_ref / den
                    self.base_s += gs * xb
                    if self.ANCHOR:
                        self.wphi_s = self.wphi_s + gs * self._ph
                    for u, b in blocks.items():
                        self.slow_w[u] = self.slow_w[u] + gs * b
                    self.fp["structure"] += 4 * (len(xb) + sum(len(b) for b in blocks.values())) + 4
                if self.REF_SPLIT:
                    self._screen_spread_split(res_ref, res)
                    self.res_prev = res_ref; self.res_prev_int = res
                else:
                    self._screen_spread(res_ref)
                    self.res_prev = res_ref
                self.res2 = res * res if self.res2 is None else self.res2 + (1 - LAM) * (res * res - self.res2)
            es, em = y - s, y - m
            self.D = LAM * self.D + (es * es - em * em) / (self.sig ** 2 + 1e-12)
            self.fp["control"] += 7
            if self.INNOV:                                           # rascunho 4: média dinâmica entre L₁ e m + ŝ_Δ
                e1, ei = y - self._inn[0], y - self._inn[1]
                self.Di = LAM * self.Di + (ei * ei - e1 * e1) / (self.sig ** 2 + 1e-12)
                self.fp["control"] += 7
            if self.t % EVERY == 0:
                z = ETA * self.D
                self.wS = 1.0 / (1.0 + math.exp(z)) if z < 700 else 0.0
                self.fp["control"] += 4
                if self.INNOV:
                    zi = ETA * self.Di
                    self.wI = 1.0 / (1.0 + math.exp(zi)) if zi < 700 else 0.0
                    self.fp["control"] += 4
            self.e2 = e * e if self.e2 is None else self.e2 + (1 - LAM) * (e * e - self.e2)
            if self.qhat is None:
                self.qhat = 1.645 * math.sqrt(self.e2)
            miss = 1.0 if abs(e) > self.qhat else 0.0
            self.hits_obs += 1; self.hits_ok += miss == 0.0
            self.qacc += miss - ALPHA_COV
            if self.t % EVERY == 0:
                self.sig = math.sqrt(max(self.e2, 1e-300)); self.sigr = math.sqrt(max(self.e2r, 1e-300))
                self.qhat = max(0.0, self.qhat + GAMMA_Q * self.sig * self.qacc); self.qacc = 0.0
            self.fp["control"] += 10
            u_ = e / self.sig
        else:
            u_ = 0.0
        if not y_ok and self.last_obs is not None:
            self.M.update(self.last_obs, m, learn=False)             # hold: history gets the last observed value
        else:
            self.M.update(y if y_ok else None, m, learn=mem_learn)
        if y_ok:
            self.last_obs = float(y)
            if self.env_hi is None:
                self.env_hi = self.env_lo = self.env_m = float(y)
            self.env_n += 1; r_ = OUT_RHO
            self.env_m += max(r_, 1.0 / self.env_n) * (y - self.env_m)
            self.env_hi = max(float(y), self.env_hi - r_ * (self.env_hi - self.env_m))
            self.env_lo = min(float(y), self.env_lo - r_ * (self.env_lo - self.env_m))
            self.fp["control"] += 10
        if y_ok:
            self.ylast = float(y)
        self.r = np.array(POLES) * self.r + (1 - np.array(POLES)) * u_
        self.fp["structure"] += 3 * len(POLES)
        if self.t % DECIDE_EVERY == 0 and self.t > 0:
            self._decide()
        self.t += 1

    # ---------------- triagem do rascunho 3: o _screen_spread da M5b com dois resíduos
    def _screen_spread_split(self, res, res_int):
        w, se, t = SCREEN_W, SCREEN_EVERY, self.t
        act = {u[1] for u in self.active if u[0] == "in"}
        due = [i for i in range(self.d) if (t + i) % se == 0]
        x, x1, ra = self.H[0], self.H[1], 1e-3 * se
        own = self.d - 1
        for i in due:
            self.a_c0[i] += ra * (x[i] * x[i] - self.a_c0[i]); self.a_c1[i] += ra * (x[i] * x1[i] - self.a_c1[i])
            self.fp["screening"] += 6
            if i in act:
                continue
            rz, rp = (res_int, self.res_prev_int) if i == own else (res, self.res_prev)
            a = float(self._a()[i]); pres = rz - a * rp
            for b, (lo, hi) in enumerate(BANDS):
                ub = (self.bs[b, i] - a * (self.bs[b, i] - self.H[lo, i] + self.H[hi + 1, i])) / (hi - lo + 1)
                self.sc_xy[b, i] += w * (pres * ub - self.sc_xy[b, i]); self.sc_xx[b, i] += w * (ub * ub - self.sc_xx[b, i])
            self.sc_yy[i] += w * (pres * pres - self.sc_yy[i])
            self.fp["screening"] += 11 * len(BANDS) + 5
        if t % se == self.d % se:                                   # residual latent unit (interna)
            self.sr_xy += w * (res_int * self.r - self.sr_xy); self.sr_xx += w * (self.r * self.r - self.sr_xx)
            self.sr_yy += w * (res_int * res_int - self.sr_yy); self.fp["screening"] += 12 * len(POLES)
        if t % SE_EQ == (self.d + 1) % SE_EQ:                       # equivalence groups (reporting only), M5b
            self._eq_flush()
            gw = 1e-3 * SE_EQ
            self.g_m += gw * (x - self.g_m); self._eq_xc = x - self.g_m; self._eq_next = 0
            self.fp["screening"] += 2 * self.d
        self._eq_rows(-(-self.d // (SE_EQ - 1)))
        for j, key in enumerate(self.split_keys()):
            if (t + j) % se:
                continue
            i, sg = key[1], key[2:]
            rz = res_int if i == own else res
            l_, r_ = halves(sg); dv = self._mean(i, l_) - self._mean(i, r_)
            st = self.sp.setdefault(key, [0.0, 1e-3, 1.0])
            st[0] += w * (rz * dv - st[0]); st[1] += w * (dv * dv - st[1]); st[2] += w * (rz * rz - st[2])
            self.fp["screening"] += 14

    # ---------------- lifecycle
    def _realign(self, store, old, ex, segs_of):
        """pesos de uma estrutura paralela (lenta ou de inovação) realinhados com as unidades ativas depois de uma
        aceitação: unidade sem mudança mantém; divisão aplica a mesma fusão; unidade nova recebe os pesos do desafiante"""
        new = {}
        for u, st in self.active.items():
            if u in old and old[u][0] == segs_of(st):
                new[u] = old[u][1]
            elif ex.kind == "split" and u == self.unit_of(ex.add_key) and u in old:
                segs_o, w_o = old[u]; sg = ex.add_key[2:]; j = segs_o.index(sg); l_, r_ = halves(sg)
                segs = segs_o[:j] + [l_, r_] + segs_o[j + 1:]
                w = np.concatenate([w_o[:j], ex.w, w_o[j + 1:]])
                merged = {}
                for sg_, w_ in zip(segs, w):
                    merged[sg_] = merged.get(sg_, 0.0) + float(w_)
                new[u] = np.array(list(merged.values()))
            else:
                new[u] = np.array(st["w"], float)
            assert len(new[u]) == len(st["w"])
        return new

    def _accept(self, ex, le):
        if self.INNOV:
            segs_of = lambda st: None if st["segs"] is None else list(st["segs"])
            old_i = {u: (segs_of(st), self.inn_w[u].copy()) for u, st in self.active.items()}
            super()._accept(ex, le) if not self.SLOW else self._accept_slow(ex, le)
            self.inn_w = self._realign(self.inn_w, old_i, ex, segs_of)
            if ex.kind != "split" and ex.add_key and ex.add_key[0] == "in":
                self.base_i[1 + ex.add_key[1]] += float(ex.w[-1])
            self.last_change = self.t
            return
        if not self.SLOW:
            super()._accept(ex, le)
            self.last_change = self.t
            return
        self._accept_slow(ex, le)

    def _accept_slow(self, ex, le):
        segs_of = lambda st: None if st["segs"] is None else list(st["segs"])
        old = {u: (segs_of(st), self.slow_w[u].copy()) for u, st in self.active.items()}
        super()._accept(ex, le)
        new = {}
        for u, st in self.active.items():
            if u in old and old[u][0] == segs_of(st):
                new[u] = old[u][1]                                   # unidade sem mudança: pesos lentos mantidos
            elif ex.kind == "split" and u == self.unit_of(ex.add_key) and u in old:
                segs_o, w_o = old[u]; sg = ex.add_key[2:]; j = segs_o.index(sg); l_, r_ = halves(sg)
                segs = segs_o[:j] + [l_, r_] + segs_o[j + 1:]
                w = np.concatenate([w_o[:j], ex.w, w_o[j + 1:]])
                merged = {}                                          # a mesma fusão do núcleo, sobre os pesos lentos
                for sg_, w_ in zip(segs, w):
                    merged[sg_] = merged.get(sg_, 0.0) + float(w_)
                new[u] = np.array(list(merged.values()))
            else:
                new[u] = np.array(st["w"], float)                    # unidade nova: os pesos do desafiante
            assert len(new[u]) == len(st["w"])
        self.slow_w = new
        if ex.kind != "split" and ex.add_key and ex.add_key[0] == "in":
            self.base_s[1 + ex.add_key[1]] += float(ex.w[-1])
        self.last_change = self.t

    def _fill(self):
        if self.SLOW and self.t - self.last_change < self.N_SETTLE:
            return                                                   # assentamento: nenhum teste novo
        super()._fill()
