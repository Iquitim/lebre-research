"""dev2_modelos.py — variantes da etapa LEBRE-V0.56-DEV-02 (PLANO_DEV_DINAMICO.md, §1 e §2), sobre o protótipo congelado
(LEBRE056_PROTO, commit ef77728).

Parte A, a M1 com estudo sob demanda: PrecisionDyn herda precision056.PrecisionParam e muda só observe. A regressão é
atualizada quando a regra decide; a triagem segue a cada 8 alvos. Guardas: atualização obrigatória enquanto n_RLS < k + 100
(regressão indeterminada e aquecimento depois de cada troca de entradas) e quando já se passaram 7 alvos sem atualização
(nunca mais de 8). σ̂²_E (taxa 0,01) é atualizada depois da decisão. A regra "sempre" (só para o teste de fumaça) atualiza
a cada alvo e deve reproduzir C3 bit a bit.

Parte B, a triagem de sensibilidade: um número fixo da v0.55 trocado por outro valor fixo, aplicado na construção do
modelo (passo da memória, M1) ou num atributo do módulo do núcleo ancorado durante a execução (passo da estrutura,
cadência e esquecimento), sempre restaurado depois.
Uso (fumaça): LEBRE056_PROTO=... python dev2_modelos.py"""
import contextlib
import math
import os
import sys

import numpy as np

COMUM = dict(ylags=3, clip=False, nbands=3)
FIXAS = {"C3": dict(every=1), "C4": dict(every=2), "C5": dict(every=4)}
DINAMICAS = {"D1": dict(regra="faixa"), "D2": dict(regra="censura"), "D3": dict(regra="orcamento", rho=0.5),
             "D4": dict(regra="orcamento", rho=0.25)}
SENS = {"S1": ("mu_estrutura", 0.02), "S2": ("mu_estrutura", 0.2), "S3": ("mu_memoria", 0.02), "S4": ("mu_memoria", 0.2),
        "S5": ("ylags_m1", 1), "S6": ("ylags_m1", 5), "S7": ("every_nucleo", 4), "S8": ("every_nucleo", 16),
        "S9": ("lam_nucleo", 0.98), "S10": ("lam_nucleo", 0.995)}


def _proto():
    p = os.environ["LEBRE056_PROTO"]
    if p not in sys.path:
        sys.path.insert(0, p)


def classes():
    _proto()
    import lebre056._precision as P_
    from lebre056._core import EVERY, N_MIN, T_MAX
    from lebre056.dormancy import DormantPrecisionExpert
    from lebre056.precision056 import PrecisionParam

    class PrecisionDyn(PrecisionParam):
        def __init__(self, d, regra="faixa", rho=0.5, **kw):
            super().__init__(d, every=1, **kw)
            self.regra, self.rho = regra, float(rho)
            self.se2 = None; self.q = 1.0; self.gap = 0; self.n_dec = 0; self.n_upd = 0

        def _decidir(self, y):
            z = self.z; k = len(z)
            e = float(y) - float(self.w @ z); self.fp += 2 * k + 1                 # erro a priori da regressão
            forcar = self.n_rls < k + 100 or self.gap >= 7
            dec = True
            if self.regra == "sempre" or self.se2 is None:
                dec = True
            elif self.regra == "faixa":
                dec = abs(e) > math.sqrt(self.se2); self.fp += 3
            elif self.se2 <= 0.0:                                                   # erro esperado zero: qualquer erro surpreende
                dec = e != 0.0; self.fp += 1
            elif self.regra == "censura":
                zpz = float(z @ (self.P @ z)); self.fp += 2 * k * k + k
                dec = e * e / (self.se2 * (1.0 + zpz)) > 1.0; self.fp += 4
            else:                                                                   # orçamento médio rho
                u = e * e / self.se2; acima = u > self.q
                self.q = max(self.q + 0.01 * ((1.0 if acima else 0.0) - self.rho), 1e-6); dec = acima; self.fp += 6
            self.se2 = e * e if self.se2 is None else self.se2 + 0.01 * (e * e - self.se2); self.fp += 3
            return dec or forcar

        def observe(self, y, L_core, learn, floor):
            e_core = (y - L_core) ** 2
            if self.e is not None:
                le = (y - self.e) ** 2
                if math.isfinite(e_core) and math.isfinite(le):
                    self.ag.update((e_core, le))
                self.fp += P_.FP_ADAHEDGE_STEP
            self.e2_core = e_core if self.e2_core is None else self.e2_core + (1 - P_.LAM) * (e_core - self.e2_core)
            self._floor = floor
            if learn:
                self.n_obs += 1
                if self.n_obs % EVERY == 0:
                    self._screen(self._x, y)
                if self.z is not None:
                    self.n_dec += 1
                    if self._decidir(y):
                        self._rls(self.z, y); self.n_upd += 1; self.gap = 0
                    else:
                        self.gap += 1
                if self.n_obs >= N_MIN and (self.sel is None or self.n_obs - self.n_sel >= T_MAX):
                    self._select()
            self.yobs.append(float(y))

    class DormantPrecisionDyn(DormantPrecisionExpert, PrecisionDyn):
        def __init__(self, d, **kw):
            PrecisionDyn.__init__(self, d, **kw)
            self.dormant = False; self.trial = False; self.trials = 0; self.low = 0
            self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
            self._sampled = False; self._last_sample = -1
            self.ema_g = None; self.ema_s = None; self.n_samples = 0

    return DormantPrecisionDyn


@contextlib.contextmanager
def _modulo_nucleo(nome, valor):
    """troca temporária de um número do módulo do núcleo ancorado (passo, cadência, esquecimento)"""
    import lebre056.anchored as AN
    antigo = getattr(AN, nome)
    setattr(AN, nome, valor)
    try:
        yield
    finally:
        setattr(AN, nome, antigo)


def construir(var, d, season=None, season2=None, reference="persistence"):
    """(modelo, contexto de execução) da variante"""
    _proto()
    from lebre056.model056 import Lebre056
    from lebre056.precision056 import DormantPrecisionParam
    m = Lebre056(d, season=season, season2=season2, reference=reference, variant="A")
    ctx = contextlib.nullcontext()
    if var in FIXAS:
        m._m1 = DormantPrecisionParam(m.n_inputs, **COMUM, **FIXAS[var])
    elif var in DINAMICAS or var == "sempre":
        Dyn = classes()
        m._m1 = Dyn(m.n_inputs, **COMUM, **(DINAMICAS.get(var) or dict(regra="sempre")))
    elif var in SENS:
        chave, v = SENS[var]
        if chave == "mu_estrutura":
            ctx = _modulo_nucleo("MU", v)
        elif chave == "mu_memoria":
            m.core._core.M.mu = v
        elif chave == "ylags_m1":
            m._m1 = DormantPrecisionParam(m.n_inputs, every=8, clip=True, ylags=v, nbands=5)
        elif chave == "every_nucleo":
            ctx = _modulo_nucleo("EVERY", v)
        else:
            ctx = _modulo_nucleo("LAM", v)
    else:
        assert var == "A", var
    return m, ctx


def rodar(var, s, ref):
    m, ctx = construir(var, s["X"].shape[1], s.get("season"), s.get("season2"), ref)
    y, X, q = s["y"], s["X"], s.get("q")
    f = np.full(len(y), np.nan)
    with ctx:
        for t in range(len(y)):
            f[t] = m.predict(X[t]).value
            m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    m1 = getattr(m, "_m1", None)
    info = dict(custo=m.cost_per_step, estrutura=m.structure)
    if m1 is not None and hasattr(m1, "n_upd"):
        info["fracao_atualizacoes"] = m1.n_upd / max(m1.n_dec, 1)
    return f, info


if __name__ == "__main__":
    rng = np.random.default_rng(5674); T = 8000; x = np.zeros((T, 3)); e = rng.standard_normal((T, 3))
    for t in range(1, T):
        x[t] = 0.6 * x[t - 1] + e[t]
    y = np.zeros(T)
    for t in range(3, T):
        y[t] = 0.85 * y[t - 1] + 0.5 * max(x[t, 0], 0) + 0.2 * x[t - 2, 0] + 0.3 * rng.standard_normal()
    s = dict(y=y, X=x, q=None)
    a, ia = rodar("C3", s, "persistence"); b, ib = rodar("sempre", s, "persistence")
    assert np.array_equal(a, b, equal_nan=True), "a regra 'sempre' difere de C3"
    import lebre056.anchored as AN
    mu0, ev0, lam0 = AN.MU, AN.EVERY, AN.LAM
    for v in ("S1", "S7", "S9"):
        rodar(v, s, "persistence")
    assert (AN.MU, AN.EVERY, AN.LAM) == (mu0, ev0, lam0), "número do núcleo não restaurado"
    A, _ = rodar("A", s, "persistence"); S1, _ = rodar("S1", s, "persistence")
    assert not np.array_equal(A, S1), "S1 não teve efeito"
    out = {v: rodar(v, s, "persistence")[1] for v in ("D1", "D2", "D3", "D4")}
    print("fumaça ok: 'sempre' = C3 bit a bit; números do núcleo restaurados; S1 muda a previsão;",
          {v: (round(i["fracao_atualizacoes"], 2), round(i["custo"])) for v, i in out.items()}, "custo C3", round(ia["custo"]))
