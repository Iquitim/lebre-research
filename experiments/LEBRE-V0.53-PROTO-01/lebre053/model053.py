"""LEBRE v0.53 (protótipo de desenvolvimento): v0.52-r1 inalterada + M2, a porta da referência trivial.

Especificação: experiments/LEBRE-V0.53-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M2_r1.md (rascunho 1; as opções do rascunho 0
continuam disponíveis para reproduzir os resultados dele: alpha_porta=None e observar_quarentena_entradas=False) e
ALGORITHM_SPEC_DRAFT_M2_r2.md (rascunho 2: saida="adahedge" ou "flipflop"; a saída passa a ser a média ponderada de R e L
e a porta vira só auditoria, registrando eventos sem decidir a saída) e ALGORITHM_SPEC_DRAFT_M2_r3.md (rascunho 3:
saida="fixedshare", Fixed Share com alpha_t = 1/t sobre previsões gaussianas de R e L) e ALGORITHM_SPEC_DRAFT_M2_r4.md
(rascunho 4: saida="adahedge_recortada", AdaHedge sobre a perda recortada da v0.52) e ALGORITHM_SPEC_DRAFT_M2_r5.md
(rascunho 5: saida="adahedge_compartilhada", Fixed Share com taxas variáveis sobre a perda recortada) e
ALGORITHM_SPEC_DRAFT_M2_r6.md (rascunho 6: saida="adahedge_compartilhada_rapida", taxa de troca 2/(t+1)^2). Em
desenvolvimento depois do rascunho 6 (REFLEXAO_M2.md): saida="adahedge_ref_definida", o rascunho 2 comparando só os
passos em que a referência declarada está definida (a sazonal só depois de um ciclo completo); e
M2_CANDIDATA_S.md: saida="switch", switch distribution (van Erven et al., 2012) sobre gaussianas de variância comum; e
M2_CANDIDATA_M.md: saida="switch_mono", a mesma restrita a trocas num só sentido (referência -> LEBRE); e
M2_CANDIDATA_Q.md: saida="prod_q", a P com as perdas do Prod normalizadas pelo maior erro já visto (sem o recorte em 2σ).
M2_CANDIDATA_P.md: saida="prod", (A,B)-Prod anytime com a candidata D como referência de confiança e a M como oportunista.
M1 (ALGORITHM_SPEC_DRAFT_M1.md): precisao=True troca L pela combinação da v0.52 com o especialista de precisão (precisao.py);
precisao="r1" usa o especialista de defasagens conjuntas (ALGORITHM_SPEC_DRAFT_M1_r1.md); precisao="r2", o mesmo com
m <= 5 e previsão recortada (ALGORITHM_SPEC_DRAFT_M1_r2.md).
Os arquivos _core.py, _engine.py, _memory.py e _model052.py são cópias byte a byte da biblioteca congelada lebre==0.1.0
(hashes em SHA256_COPIAS.txt) e não são editados. A porta fica por fora: a v0.52 roda inteira por baixo e a porta decide
qual previsão sai. No rascunho 1 a porta tem motor de evidência próprio (orçamento alpha_porta), e o caminho estrutural
fica idêntico ao da v0.52.
"""
import math
from collections import deque

import numpy as np

from ._core import ALPHA_COV, CLIP_K, DECIDE_EVERY, EVERY, GAMMA_Q, LAM, N_MIN, SCALE_FLOOR, T_MAX
from ._engine import ChangeEngine
from ._model052 import Event, Forecast, Lebre as Lebre052
from .precisao import (EspecialistaConjuntoR3, EspecialistaDefasagens, EspecialistaDefasagensR2,
                       EspecialistaPrecisao)
from .agregacao import (FP_AGREGACAO_PASSO, FP_COMPARTILHADA_PASSO, FP_FIXED_SHARE_PASSO, FP_RECORTE_PASSO,
                        FP_SWITCH_MONO_PASSO, FP_SWITCH_PASSO, Agregador, FixedShare, FixedShareAdaptativo,
                        SwitchDistribution, SwitchMonotono, SwitchMonotonoExato, SwitchMonotonoJeffreys,
                        FP_PROD_PASSO, ProdAnytime)

REFERENCIAS = ("zero", "persistencia", "sazonal")
SAIDAS = ("porta", "adahedge", "flipflop", "fixedshare", "adahedge_recortada", "adahedge_compartilhada",
          "adahedge_compartilhada_rapida", "adahedge_ref_definida", "switch", "switch_mono", "switch_mono_exato",
          "switch_mono_jeffreys", "prod", "prod_q")
FP_NORMALIZACAO_Q = 3        # candidata Q: dois máximos e a normalização (as divisões substituem as do recorte)
FP_PORTA_PASSO = 16           # perdas recortadas, incremento e médias exponenciais da porta (contagem aproximada)


class Lebre053:
    """Previsor da v0.53 em desenvolvimento. Mesma interface da biblioteca (predict, observe, step, events, structure).

    referencia: "zero" (só se declarada: o alvo é uma variação), "persistencia" ou "sazonal"; None deduz "sazonal" se
        houver ciclo declarado, senão "persistencia".
    porta: False desliga M2; a saída é então idêntica, bit a bit, à da v0.52 (teste em tests/).
    eps_porta: margem das duas hipóteses da porta.
    recriar: True aposenta e recria a hipótese da porta ao fim de um episódio sem avanço; False a mantém persistente.
    alpha_porta: orçamento de erro próprio da porta (rascunho 1); None usa o motor e a sequência e-LOND da estrutura
        (rascunho 0).
    observar_quarentena_entradas: True (rascunho 1) faz a porta observar também os passos em quarentena por entradas
        fora do contrato; a marcação do próprio alvo (quarantine=True) continua excluindo o passo.
    saida: "porta" (rascunhos 0 e 1: a porta decide a saída); "adahedge" ou "flipflop" (rascunho 2: média ponderada de
        R e L com pesos do algoritmo, sobre a perda quadrática, nos mesmos passos que a porta observa; a porta continua
        rodando só como auditoria); "fixedshare" (rascunho 3: pesos do Fixed Share com alpha_t = 1/t sobre a perda
        logarítmica de N(previsão, sigma^2), sigma^2 = média exponencial dos erros quadráticos do próprio previsor);
        "adahedge_recortada" (rascunho 4: AdaHedge sobre min(e^2 / B^2, 1), B = CLIP_K * max(menor sigma dos dois, piso));
        "adahedge_compartilhada" (rascunho 5: a mesma perda recortada, pesos do Fixed Share com taxas variáveis);
        "adahedge_compartilhada_rapida" (rascunho 6: idem, com taxa de troca 2/(t+1)^2, Adamskiy et al. 2016, 4.1.3);
        "adahedge_ref_definida" (desenvolvimento: como "adahedge", mas enquanto a referência declarada não está definida
        a saída é L e os pesos não aprendem; a sazonal fica definida com um ciclo completo de alvos);
        "switch" (candidata S: switch distribution sobre N(previsão, s2) com s2 comum = max(min(s2_R, s2_L), piso^2),
        mesma regra da referência definida); "switch_mono" (candidata M: idem, trocas só da referência para a LEBRE).
    """

    def __init__(self, n_inputs, season=None, season2=None, standardize=True, referencia=None, porta=True,
                 eps_porta=0.002, recriar=True, alpha_porta=0.01, observar_quarentena_entradas=True, saida="porta",
                 precisao=False):
        if saida not in SAIDAS:
            raise ValueError(f"saida deve ser uma de {SAIDAS}")
        self.base = Lebre052(n_inputs, season=season, season2=season2, standardize=standardize)
        if precisao and not porta:
            raise ValueError("precisao=True exige porta=True (a M1 alimenta a M2)")
        self.precisao = (EspecialistaConjuntoR3(n_inputs) if precisao == "r3"
                         else EspecialistaDefasagensR2(n_inputs) if precisao == "r2"
                         else EspecialistaDefasagens(n_inputs) if precisao == "r1"
                         else EspecialistaPrecisao(n_inputs) if precisao else None)
        self._L52 = None
        if referencia is None:
            referencia = "sazonal" if season else "persistencia"
        if referencia not in REFERENCIAS:
            raise ValueError(f"referencia deve ser uma de {REFERENCIAS}")
        if referencia == "sazonal" and not season:
            raise ValueError("referencia 'sazonal' exige um ciclo declarado (season)")
        self.referencia, self.porta, self.eps, self.recriar = referencia, bool(porta), float(eps_porta), bool(recriar)
        self.season = season
        self.alpha_porta, self.obs_quar = alpha_porta, bool(observar_quarentena_entradas)
        self._motor_porta = ChangeEngine(alpha_porta, 2, 1, N_MIN, T_MAX) if alpha_porta is not None else None
        self.hist = deque(maxlen=season) if referencia == "sazonal" else None
        self.ultimo = None
        self.modo = "REF" if self.porta else "LEBRE"
        self.e2 = {"REF": None, "LEBRE": None}; self.sig = {"REF": 1.0, "LEBRE": 1.0}
        self._hyp = None; self._hkey = None; self._inst = 0; self._ep_n = 0; self._ep_S = 0.0
        self.eventos_porta = []; self.trocas = 0; self.fp_porta = 0.0
        self._out = None; self._R = None; self._L = None; self._R_def = False
        self.saida = saida
        if saida == "fixedshare":
            self.agregador = FixedShare(2)
        elif saida == "adahedge_compartilhada":
            self.agregador = FixedShareAdaptativo(2)
        elif saida == "switch":
            self.agregador = SwitchDistribution(2)
        elif saida == "switch_mono":
            self.agregador = SwitchMonotono()
        elif saida == "switch_mono_exato":                        # oráculo de diagnóstico, custo O(t)
            self.agregador = SwitchMonotonoExato()
        elif saida == "switch_mono_jeffreys":                     # oráculo de diagnóstico, custo O(t)
            self.agregador = SwitchMonotonoJeffreys()
        elif saida in ("prod", "prod_q"):                         # candidatas P e Q: D (B) e M (A) combinadas pelo Prod
            self.agregador = ProdAnytime()
            self._subD = Agregador(2); self._subM = SwitchMonotono()
            self._d = None; self._m = None; self._Nq = 0.0
        elif saida == "adahedge_compartilhada_rapida":
            self.agregador = FixedShareAdaptativo(2, alpha_fn=lambda t: 2.0 / (t + 1) ** 2)
        else:
            self.agregador = Agregador(2, flipflop=saida == "flipflop") if saida != "porta" else None
        self._recortada = saida in ("adahedge_recortada", "adahedge_compartilhada", "adahedge_compartilhada_rapida")
        self.pesos = None                                               # [peso de R, peso de L] na última previsão
        # intervalo da saída (mesma regra adaptativa da v0.52, aplicada ao erro da saída)
        self.e2o = None; self.sigo = 1.0; self.qhat = None; self.qacc = 0.0; self.hits_obs = 0; self.hits_ok = 0
        if self.porta:
            self._nova_hipotese()

    # ------------------------------------------------------------------ porta
    @property
    def _engine(self):
        return self._motor_porta if self._motor_porta is not None else self.base._core.engine

    def _nova_hipotese(self):
        self._inst += 1
        direcao = "promover" if self.modo == "REF" else "rebaixar"
        self._hkey = ("porta", direcao, self._inst)
        self._hyp = self._engine.hypothesis(self._hkey, self.eps)
        self._ep_n = 0; self._ep_S = 0.0

    def _referencia(self):
        if self.referencia == "zero":
            return 0.0
        if self.referencia == "sazonal" and len(self.hist) == self.season and math.isfinite(self.hist[0]):
            return float(self.hist[0])
        return float(self.ultimo) if self.ultimo is not None else math.nan

    def _revisar(self, t):
        h = self._hyp
        le = h.log_e(); self.fp_porta += 3 * len(h.lam)
        if le >= h.log_thr:
            novo = "LEBRE" if self.modo == "REF" else "REF"
            self.eventos_porta.append(Event(int(t), "accepted", "gate", "lebre" if novo == "LEBRE" else "referencia",
                                            None, round(float(le), 2), int(h.n)))
            self._engine.n_accepted += 1                                # conta como descoberta (sequência e-LOND)
            self._engine.hyps.pop(self._hkey, None)                      # hipótese consumida
            self.modo = novo; self.trocas += 1
            self._nova_hipotese()
        elif (self._ep_n >= N_MIN and self._ep_S <= 0.0) or self._ep_n >= T_MAX:
            if self.recriar:
                self._engine.hyps.pop(self._hkey, None)
                self._nova_hipotese()
            else:
                self._ep_n = 0; self._ep_S = 0.0

    # ------------------------------------------------------------------ passos
    def predict(self, x):
        fb = self.base.predict(x)
        if not self.porta:
            self._out = fb.value
            return fb
        self._L52 = fb.value
        self._L = self.precisao.prever(x, fb.value) if self.precisao is not None else fb.value
        self._R = self._referencia()
        self._R_def = math.isfinite(self._R) and (self.referencia != "sazonal" or (
            len(self.hist) == self.season and math.isfinite(self.hist[0])))
        if self.saida in ("prod", "prod_q"):
            if self._R_def:
                wd, wm, sp = self._subD.pesos(), self._subM.pesos(), self.agregador.s()
                self._d = float(wd[0] * self._R + wd[1] * self._L)
                self._m = float(wm[0] * self._R + wm[1] * self._L)
                self.pesos = sp * wm + (1.0 - sp) * wd
                out = sp * self._m + (1.0 - sp) * self._d
            else:
                self.pesos = None; out = self._L
        elif self.agregador is not None:
            if math.isfinite(self._R) and (self._R_def or self.saida not in ("adahedge_ref_definida", "switch", "switch_mono",
                                                                       "switch_mono_exato", "switch_mono_jeffreys")):
                if self.saida in ("switch_mono_exato", "switch_mono_jeffreys"):
                    c = self.base._core
                    piso = SCALE_FLOOR * math.sqrt(max(c.y_sv, 0.0)) if c.t >= 200 else 0.0
                    s2 = max(min(self.e2["REF"], self.e2["LEBRE"]), piso * piso, 1e-300) if self.e2["REF"] is not None else 1.0
                    self.agregador.calcular(s2)
                self.pesos = self.agregador.pesos()
                out = float(self.pesos[0] * self._R + self.pesos[1] * self._L)
            else:
                self.pesos = None; out = self._L
        else:
            out = self._R if (self.modo == "REF" and math.isfinite(self._R)) else self._L
        self._out = out
        q = self.qhat
        lo, hi = (out - q, out + q) if q is not None else (math.nan, math.nan)
        return Forecast(float(out), float(lo), float(hi), fb.t)

    def observe(self, y, quarantine=False):
        if not self.porta:
            self.base.observe(y, quarantine)
            return
        c = self.base._core
        t0, quar, ysv = c.t, c.quar_until, c.y_sv
        y_ok = y is not None and math.isfinite(y)
        aprende = y_ok and not quarantine and (self.obs_quar or not (t0 <= quar))
        piso = SCALE_FLOOR * math.sqrt(max(ysv, 0.0)) if t0 >= 200 else 0.0     # só passado (antes de ver y)
        self.base.observe(y, quarantine)
        if self.precisao is not None and y_ok:
            self.precisao.observar(float(y), self._L52, (not quarantine) and not (t0 <= quar), piso)
        R, L = self._R, self._L
        if aprende and math.isfinite(R) and math.isfinite(L):
            vig, des = (R, L) if self.modo == "REF" else (L, R)
            B = CLIP_K * max(self.sig[self.modo], piso)
            lv = min((y - vig) ** 2 / (B * B), 1.0); ld = min((y - des) ** 2 / (B * B), 1.0)
            d = lv - ld - self.eps
            self._hyp.observe(d); self._ep_n += 1; self._ep_S += d
            if self.saida == "fixedshare" and self.e2["REF"] is not None:   # escalas só do passado (antes deste erro)
                pis2 = piso * piso
                perdas = []
                for k, v in (("REF", R), ("LEBRE", L)):
                    s2 = max(self.e2[k], pis2, 1e-300)
                    perdas.append((y - v) ** 2 / (2.0 * s2) + 0.5 * math.log(s2))
                self.agregador.atualizar(perdas)
                self.fp_porta += FP_FIXED_SHARE_PASSO
            if self.saida in ("prod", "prod_q") and self._R_def:
                fin = lambda v: v if math.isfinite(v) else 1e300           # rascunho 2 da M1: não propagar NaN
                self._subD.atualizar((fin((y - R) ** 2), fin((y - L) ** 2)))  # D: como "adahedge_ref_definida"
                self.fp_porta += FP_AGREGACAO_PASSO
                if self.e2["REF"] is not None:                          # M e Prod: escalas só do passado
                    s2 = max(min(self.e2["REF"], self.e2["LEBRE"]), piso * piso, 1e-300)
                    self._subM.atualizar((fin((y - R) ** 2 / (2.0 * s2)), fin((y - L) ** 2 / (2.0 * s2))))
                    if self.saida == "prod":
                        B2 = CLIP_K * CLIP_K * s2
                        self.agregador.atualizar(min((y - self._d) ** 2 / B2, 1.0), min((y - self._m) ** 2 / B2, 1.0))
                    else:                                               # candidata Q: normalizado pelo maior erro já visto
                        ld, lm = fin((y - self._d) ** 2), fin((y - self._m) ** 2)
                        self._Nq = max(self._Nq, ld, lm)
                        if self._Nq > 0:
                            self.agregador.atualizar(ld / self._Nq, lm / self._Nq)
                        self.fp_porta += FP_NORMALIZACAO_Q
                    self.fp_porta += FP_SWITCH_MONO_PASSO + FP_PROD_PASSO
            if self.saida in ("switch_mono_exato", "switch_mono_jeffreys") and self.e2["REF"] is not None and self._R_def:
                self.agregador.atualizar(((y - R) ** 2, (y - L) ** 2))
                self.fp_porta += 5 * self.agregador.n                  # O(t): oráculo, não candidata
            if self.saida in ("switch", "switch_mono") and self.e2["REF"] is not None and self._R_def:
                s2 = max(min(self.e2["REF"], self.e2["LEBRE"]), piso * piso, 1e-300)
                self.agregador.atualizar(((y - R) ** 2 / (2.0 * s2), (y - L) ** 2 / (2.0 * s2)))
                self.fp_porta += FP_SWITCH_PASSO if self.saida == "switch" else FP_SWITCH_MONO_PASSO
            if self._recortada and self.e2["REF"] is not None:              # escalas só do passado (antes deste erro)
                B2 = CLIP_K * CLIP_K * max(min(self.e2["REF"], self.e2["LEBRE"]), piso * piso, 1e-300)
                self.agregador.atualizar((min((y - R) ** 2 / B2, 1.0), min((y - L) ** 2 / B2, 1.0)))
                self.fp_porta += (FP_COMPARTILHADA_PASSO if self.saida.startswith("adahedge_compartilhada")
                                  else FP_AGREGACAO_PASSO + FP_RECORTE_PASSO)
            for k, v in (("REF", R), ("LEBRE", L)):                    # erro de cada lado, para a escala do vigente
                e2 = (y - v) ** 2
                self.e2[k] = e2 if self.e2[k] is None else self.e2[k] + (1 - LAM) * (e2 - self.e2[k])
            if t0 % EVERY == 0:
                for k in ("REF", "LEBRE"):
                    self.sig[k] = math.sqrt(max(self.e2[k], 1e-300))
            self.fp_porta += FP_PORTA_PASSO
            if self.agregador is not None and (self.saida in ("adahedge", "flipflop") or (
                    self.saida == "adahedge_ref_definida" and self._R_def)):
                self.agregador.atualizar(((y - R) ** 2, (y - L) ** 2))
                self.fp_porta += FP_AGREGACAO_PASSO
        if y_ok:                                                        # intervalo da saída
            e = y - self._out
            self.e2o = e * e if self.e2o is None else self.e2o + (1 - LAM) * (e * e - self.e2o)
            if self.qhat is None:
                self.qhat = 1.645 * math.sqrt(self.e2o)
            miss = 1.0 if abs(e) > self.qhat else 0.0
            self.hits_obs += 1; self.hits_ok += miss == 0.0; self.qacc += miss - ALPHA_COV
            if t0 % EVERY == 0:
                self.sigo = math.sqrt(max(self.e2o, 1e-300))
                self.qhat = max(0.0, self.qhat + GAMMA_Q * self.sigo * self.qacc); self.qacc = 0.0
            self.ultimo = float(y)
        if self.hist is not None:
            self.hist.append(float(y) if y_ok else (self.ultimo if self.ultimo is not None else math.nan))
        if t0 % DECIDE_EVERY == 0 and t0 > 0:
            self._revisar(t0)

    def step(self, x, y, quarantine=False):
        f = self.predict(x)
        self.observe(None if y is None or (isinstance(y, float) and math.isnan(y)) else y, quarantine)
        return f

    # ------------------------------------------------------------------ auditoria
    @property
    def events(self):
        return sorted(self.base.events + self.eventos_porta, key=lambda e: e.t)

    @property
    def structure(self):
        return self.base.structure

    @property
    def coverage(self):
        if not self.porta:
            return self.base.coverage
        return self.hits_ok / self.hits_obs if self.hits_obs else math.nan

    @property
    def cost_per_step(self):
        t = self.base.n_steps
        extra = self.fp_porta + (self.precisao.fp if self.precisao is not None else 0.0)
        return self.base.cost_per_step + (extra / t if t else 0.0)

    def unit_name(self, key):
        return self.base.unit_name(key)
