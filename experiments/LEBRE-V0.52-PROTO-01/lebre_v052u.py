"""lebre_v052u.py — PROTOTYPE of LEBRE v0.52 with INPUT-LEVEL hypotheses (reformulation of 27/09/2026).

Diagnosis that motivated it (DEV_LOG, semi-synthetics): with real, smooth and collinear inputs the atomic version
(one hypothesis per (input, lag), 412 in total) had neither a usable screen (~5 effective samples per candidate) nor
power (each atom carries a small share of the gain; ~2e4 samples per discovery). Here the unit of change is a whole input:

  unit ("in", i): response block of input i = means of its past over dyadic lag bands [1], [2-3], [4-7], [8-15],
                  [16-32]; the challenger also re-fits the coefficient of x_i(t), so the block is judged net of what
                  the current value already carries;
  unit ("res",):  the residual latent states (poles 0.8, 0.95), as before.

Everything else is the v0.52 of lebre_v052.py: memory expert M, structural expert S (base = bias + current inputs),
option IIb (changes judged on S), dynamic model averaging, the same ChangeEngine (Choe & Ramdas e-process on clipped
loss differences minus a margin, persistent hypotheses, e-LOND-type levels, scan rule). Changes:
  * the challenger's block is fitted by recursive least squares within the episode; the first `chal_warm` samples of
    an episode only train it (a predictable subsequence) and produce no evidence;
  * the screen is one group statistic per unit, on AR(1)-prewhitened band means (Box-Jenkins identification),
    updated every `screen_every` steps for every unit (no round robin).
"""
import math

import numpy as np

from change_engine import ChangeEngine
from lebre_v052 import POLES, Memory

BANDS = ((1, 1), (2, 3), (4, 7), (8, 15), (16, 32))


class LebreV052U:
    def __init__(self, d, season=None, M_max=4, m_slots=2, mu=0.1, alpha=0.05, eps_add=0.002, eps_swap=0.002,
                 eps_rem=-0.002, clip_k=2.0, decide_every=10, n_min=100, T_max=5000, cooldown=2000, rem_period=2000,
                 lam=0.99, eta=0.5, alpha_cov=0.1, gamma_q=0.1, every=8, clip_x=8.0, input_contract=True,
                 self_input=True, chal_warm=200, screen_every=4, screen_w=0.02, screen_q=15.09, rls_p0=10.0):
        self.self_input = self_input; self.ylast = 0.0; self.ym = 0.0; self.yv = 1.0
        d = d + 1 if self_input else d
        self.d, self.L = d, BANDS[-1][1]
        self.M = Memory(season)
        self.M_max, self.mu, self.alpha, self.clip_k = M_max, mu, alpha, clip_k
        self.eps = {"add": eps_add, "swap": eps_swap, "rem": eps_rem}
        self.decide_every, self.n_min, self.cooldown, self.rem_period = decide_every, n_min, cooldown, rem_period
        self.lam, self.eta, self.alpha_cov, self.gamma_q, self.every, self.clip_x = lam, eta, alpha_cov, gamma_q, every, clip_x
        self.input_contract = input_contract; self.quar_until = -1
        self.chal_warm, self.screen_every, self.screen_w, self.screen_q, self.rls_p0 = chal_warm, screen_every, screen_w, screen_q, rls_p0
        self.units = [("in", i) for i in range(d)] + [("res",)]
        nb = len(BANDS)
        self.H = np.zeros((self.L + 2, d))                           # H[k] = x_{t-k}
        self.bs = np.zeros((nb, d))                                  # running band sums of x
        self.U = np.zeros((self.L + 2, d)); self.us = np.zeros((nb, d))   # prewhitened input u = x_t - a x_{t-1}
        self.r = np.zeros(len(POLES))
        self.base = np.zeros(d + 1)                                  # bias + current inputs
        self.active = {}                                             # unit -> weight vector of its block
        self.contrib_ema = {}
        # screen (group statistic per unit)
        self.a_c0 = np.ones(d); self.a_c1 = np.zeros(d); self.res_prev = 0.0
        self.sc_xy = np.zeros((nb, d)); self.sc_xx = np.ones((nb, d)) * 1e-3; self.sc_yy = np.ones(d)
        self.sr_xy = np.zeros(len(POLES)); self.sr_xx = np.ones(len(POLES)) * 1e-3; self.sr_yy = 1.0
        self.engine = ChangeEngine(alpha, 2 * len(self.units), m_slots, n_min, T_max)
        self.last_tested = {}; self.last_rem = {}
        self.events = []; self.t = 0
        self.e2 = None; self.sig = 1.0; self.e2r = None; self.sigr = 1.0; self.res2 = None
        self.D = 0.0; self.wS = 0.5
        self.qhat = None; self.qacc = 0.0; self.hits = []
        self.fp = {"memory": 0.0, "structure": 0.0, "experiments": 0.0, "screening": 0.0, "control": 0.0}

    # ---------------- features (values available before y_t)
    def block(self, unit):
        if unit[0] == "in":
            i = unit[1]
            return np.array([self.bs[b, i] / (hi - lo + 1) for b, (lo, hi) in enumerate(BANDS)])
        return self.r.copy()

    def cfeat(self, unit):
        """challenger regressors: the block and, for an input, its current value (re-fitted jointly)"""
        f = self.block(unit)
        return np.append(f, self.H[0, unit[1]]) if unit[0] == "in" else f

    def label(self, unit):
        return f"entrada x{unit[1]} (bloco de resposta)" if unit[0] == "in" else "estado latente do resíduo"

    def _struct_pred(self, x):
        xb = np.concatenate(([1.0], x))
        s = float(self.base @ xb) + sum(float(w @ self.block(u)) for u, w in self.active.items())
        self.fp["structure"] += 2 * (self.d + 1) + sum(2 * len(w) for w in self.active.values())
        return s, xb

    def _a(self):
        return np.clip(self.a_c1 / np.maximum(self.a_c0, 1e-6), -0.999, 0.999)

    def _shift(self, x):
        """shift histories and band sums (each band sum: + entering lag lo, - leaving lag hi+1)"""
        a = self._a()
        u = x - a * self.H[0]                                        # prewhitened with the coefficient known before t
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = x
        self.U = np.roll(self.U, 1, axis=0); self.U[0] = u
        for b, (lo, hi) in enumerate(BANDS):
            self.bs[b] += self.H[lo] - self.H[hi + 1]
            self.us[b] += self.U[lo] - self.U[hi + 1]
        self.a_c0 += 1e-3 * (x * x - self.a_c0); self.a_c1 += 1e-3 * (x * self.H[1] - self.a_c1)
        self.fp["structure"] += 4 * len(BANDS) * self.d + 8 * self.d

    # ---------------- one step
    def step(self, x, y, quarantine=False):
        if self.self_input:
            v = self.ylast
            x = np.append(np.asarray(x, float), (v - self.ym) / math.sqrt(self.yv + 1e-6))
            dlt = v - self.ym; self.ym += 1e-4 * dlt
            self.yv = max((1 - 1e-4) * self.yv + 1e-4 * (v - self.ym) * dlt, 1e-4); self.fp["structure"] += 9
        x = np.nan_to_num(x)
        if self.input_contract and np.any(np.abs(x) > self.clip_x):   # P6: structure neither learns nor tests for L steps
            self.quar_until = self.t + self.L
        x = np.clip(x, -self.clip_x, self.clip_x)
        self._shift(x)
        m = self.M.predict()
        s, xb = self._struct_pred(x)
        f = m + self.wS * (s - m)
        ref = s                                                      # IIb: experiments compare S vs S + Delta
        outs = []
        for ex in self.engine.slots:
            a = float(ex.w @ self.cfeat(ex.add_key)) if ex.add_key else 0.0
            r = float(self.active[ex.rem_key] @ self.block(ex.rem_key)) if ex.rem_key else 0.0
            outs.append(ref + a - r)
        self.fp["experiments"] += 4 * len(outs)
        y_ok = y is not None and np.isfinite(y)
        mem_learn = y_ok and not quarantine
        learn = mem_learn and not (self.input_contract and self.t <= self.quar_until)
        if y_ok:
            e = y - f; er = y - ref
            self.e2r = er * er if self.e2r is None else self.e2r + (1 - self.lam) * (er * er - self.e2r)
            B = self.clip_k * self.sigr
            lf = min(er * er / (B * B), 1.0)
            res = y - s
            if learn:
                for ex, g in zip(self.engine.slots, outs):
                    ex.k = getattr(ex, "k", 0) + 1
                    if ex.k > self.chal_warm or not ex.add_key:      # a removal has nothing to learn
                        ex.observe(lf - min((y - g) ** 2 / (B * B), 1.0) - ex.eps)
                    if ex.add_key:                                   # RLS on the residual the block would explain
                        fx = self.cfeat(ex.add_key)
                        rr = res + (float(self.active[ex.rem_key] @ self.block(ex.rem_key)) if ex.rem_key else 0.0)
                        Pf = ex.P @ fx; kg = Pf / (1.0 + fx @ Pf)
                        ex.w = ex.w + kg * (rr - ex.w @ fx); ex.P = ex.P - np.outer(kg, Pf)
                        self.fp["experiments"] += 4 * len(fx) ** 2 + 6 * len(fx)
                self.fp["experiments"] += 8 * len(outs)
                # live structure: NLMS on base + active blocks
                blocks = {u: self.block(u) for u in self.active}
                den = float(xb @ xb) + sum(float(b @ b) for b in blocks.values()) + 1e-6
                g_ = self.mu * res / den
                self.base += g_ * xb
                for u, b in blocks.items():
                    self.active[u] += g_ * b
                    c = abs(float(self.active[u] @ b))
                    self.contrib_ema[u] = c if u not in self.contrib_ema else self.contrib_ema[u] + 0.01 * (c - self.contrib_ema[u])
                self.fp["structure"] += 4 * (len(xb) + sum(len(b) for b in blocks.values())) + 4
                if self.t % self.screen_every == 0:
                    self._screen(res)
                self.res_prev = res
                self.res2 = res * res if self.res2 is None else self.res2 + (1 - self.lam) * (res * res - self.res2)
            # dynamic model averaging
            es, em = y - s, y - m
            self.D = self.lam * self.D + (es * es - em * em) / (self.sig ** 2 + 1e-12)
            self.fp["control"] += 7
            if self.t % self.every == 0:
                z = self.eta * self.D
                self.wS = 1.0 / (1.0 + math.exp(z)) if z < 700 else 0.0
                self.fp["control"] += 4
            # scale and interval (accumulated indicators)
            self.e2 = e * e if self.e2 is None else self.e2 + (1 - self.lam) * (e * e - self.e2)
            if self.qhat is None:
                self.qhat = 1.645 * math.sqrt(self.e2)
            miss = 1.0 if abs(e) > self.qhat else 0.0
            self.hits.append(miss == 0.0)
            self.qacc += miss - self.alpha_cov
            if self.t % self.every == 0:
                self.sig = math.sqrt(max(self.e2, 1e-300)); self.sigr = math.sqrt(max(self.e2r, 1e-300))
                self.qhat = max(0.0, self.qhat + self.gamma_q * self.sig * self.qacc); self.qacc = 0.0
            self.fp["control"] += 10
            u_ = e / self.sig
        else:
            u_ = 0.0; self.hits.append(None)
        self.M.update(y if y_ok else None, m, learn=mem_learn)
        if self.self_input and y_ok:
            self.ylast = float(y)
        self.r = np.array(POLES) * self.r + (1 - np.array(POLES)) * u_
        self.fp["structure"] += 3 * len(POLES)
        if self.t % self.decide_every == 0 and self.t > 0:
            self._decide()
        self.t += 1
        return f

    def _screen(self, res):
        """group statistic per unit: EMA correlations of the prewhitened residual with the prewhitened band means"""
        w = self.screen_w; a = self._a()
        pres = res - a * self.res_prev                               # residual filtered by each input's own AR(1)
        ub = self.us / np.array([hi - lo + 1 for lo, hi in BANDS])[:, None]
        self.sc_xy += w * (pres[None, :] * ub - self.sc_xy)
        self.sc_xx += w * (ub * ub - self.sc_xx)
        self.sc_yy += w * (pres * pres - self.sc_yy)
        self.sr_xy += w * (res * self.r - self.sr_xy); self.sr_xx += w * (self.r * self.r - self.sr_xx)
        self.sr_yy += w * (res * res - self.sr_yy)
        self.fp["screening"] += (12 * len(BANDS) + 6) * self.d + 12 * len(POLES)

    def screen_stat(self, unit):
        """sum over the block of squared EMA correlations, in units of its null s.d. scale w/(2-w)"""
        k = self.screen_w / (2 - self.screen_w)
        if unit[0] == "in":
            i = unit[1]
            c2 = self.sc_xy[:, i] ** 2 / (self.sc_xx[:, i] * self.sc_yy[i] + 1e-12)
        else:
            c2 = self.sr_xy ** 2 / (self.sr_xx * self.sr_yy + 1e-12)
        return float(c2.sum()) / k

    # ---------------- lifecycle (policy; the statistics live in ChangeEngine)
    def _open(self, kind, add_key, rem_key):
        hkey = ("out", rem_key) if kind == "rem" else ("in", add_key)
        ex = self.engine.open(kind, add_key, rem_key, hkey, self.eps[kind], self.t)
        if add_key:
            n_ = len(self.cfeat(add_key)); ex.w = np.zeros(n_); ex.P = self.rls_p0 * np.eye(n_)
        for k in (add_key, rem_key):
            if k:
                self.last_tested[k] = self.t

    def _decide(self):
        changed = set()
        for decision, ex, le in self.engine.review():
            if decision == "accepted":
                self._accept(ex, le); changed |= {ex.add_key, ex.rem_key} - {None}
            else:
                self.events.append((self.t, "closed", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.n))
        if changed:
            keep = []
            for ex in self.engine.slots:
                if {ex.add_key, ex.rem_key} & changed:
                    self.events.append((self.t, "superseded", ex.kind, ex.add_key, ex.rem_key, None, ex.n))
                else:
                    keep.append(ex)
            self.engine.slots = keep
        self._fill()

    def _accept(self, ex, le):
        if ex.rem_key and ex.rem_key in self.active:
            del self.active[ex.rem_key]; self.contrib_ema.pop(ex.rem_key, None)
        if ex.add_key:
            nb = len(self.block(ex.add_key))
            self.active[ex.add_key] = ex.w[:nb].copy()
            if ex.add_key[0] == "in":                                # the current-value correction moves to the base
                self.base[1 + ex.add_key[1]] += float(ex.w[nb])
        self.engine.consume(ex)
        self.events.append((self.t, "accepted", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.hyp.n))

    def _fill(self):
        busy = self.engine.busy_keys()
        while self.engine.free_slots() > 0:
            due = [a for a in self.active if a not in busy and self.t - self.last_rem.get(a, -10 ** 9) >= self.rem_period
                   and self.t - self.last_tested.get(a, -10 ** 9) >= self.n_min]
            if due:
                a = due[0]; self.last_rem[a] = self.t; self._open("rem", None, a); busy.add(a); continue
            pool = [u for u in self.units if u not in self.active and u not in busy
                    and self.t - self.last_tested.get(u, -10 ** 9) >= self.cooldown]
            if not pool:
                break
            c = max(pool, key=self.screen_stat)
            if self.screen_stat(c) < self.screen_q:                  # ~ chi2(5) 99% quantile in null-scale units
                break
            if len(self.active) < self.M_max:
                self._open("add", c, None)
            else:
                a = min((k for k in self.active if k not in busy), key=lambda k: self.contrib_ema.get(k, float("inf")), default=None)
                if a is None:
                    break
                self._open("swap", c, a); busy.add(a)
            busy.add(c)
            self.fp["control"] += len(self.units) / self.decide_every

    # ---------------- reporting
    @property
    def k_started(self):
        return self.engine.k_started

    def structure(self):
        return sorted(self.active)

    def coverage(self):
        h = [v for v in self.hits if v is not None]
        return float(np.mean(h)) if h else float("nan")

    def fp_total(self):
        return sum(self.fp.values()) + self.M.fp + self.engine.fp
