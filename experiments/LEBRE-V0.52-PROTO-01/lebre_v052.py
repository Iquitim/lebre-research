"""lebre_v052.py — PROTOTYPE of LEBRE v0.52: every structural change is an experiment.

A live forecaster f_t is run together with m "challengers" g_t = f_t + Delta_t (add / remove / swap one structural atom).
Each challenger accumulates anytime-valid evidence of predictive improvement over the live model with the
sub-exponential mixture e-process of Choe & Ramdas (2024, Thm 3) on clipped squared-loss differences minus a margin;
changes are accepted with online e-LOND-type levels fixed at experiment start (valid FDR over the whole change stream).
A scan scheduler (Xu, Mei & Moustakides 2021 style) decides which experiment occupies a free slot.

option="I":  f = M + base + sum(atoms)              (structure on top of the memory, no combiner)
option="II": f = M + w_S (S - M), S = base + atoms  (v0.51-like dynamic model averaging; changes judged on f)

Memory expert M: v0.51 features, plus (a) scale-relative epsilon in NLMS, (b) interval updated with the 8 accumulated
indicators. This file never touches the frozen v0.51 code.
"""
import math
from collections import deque

import numpy as np

from change_engine import ChangeEngine

POLES = (0.8, 0.95)            # pole 0.5 dropped (dev, 26/09): its ~2-step memory is covered by lags 1-2


# ------------------------------------------------------------------ memory expert (v0.51 + hygiene)
class Memory:
    def __init__(self, season=None, mu=0.05, a_prof=0.1, a_mean=0.01, eps_rel=1e-3):
        self.s, self.mu, self.ap, self.am, self.eps_rel = season, mu, a_prof, a_mean, eps_rel
        self.feats = ("mean", "d1", "sn", "si", "prof") if season else ("mean", "d1")
        self.Lb = 2 * season + 2 if season else 3
        self.buf = np.zeros(self.Lb); self.n = 0
        self.mew = None; self.G = np.zeros(season) if season else None
        self.w = np.zeros(len(self.feats)); self.phi = None; self.pp_ema = None; self.y2 = None; self.fp = 0.0

    def _b(self, k):
        return self.buf[(self.n - k) % self.Lb]

    def predict(self):
        if self.n < self.Lb:
            self.phi = None
            return self._b(1) if self.n else 0.0
        last, s = self._b(1), self.s
        v = [(self.mew - last) if self.mew is not None else 0.0, last - self._b(2)]   # mean not yet seen: no reversion
        if s:
            v += [self._b(s) - last, self._b(s - 1) - self._b(s), self.G[self.n % s]]
        self.phi = np.array(v); self.fp += 3 * len(v) + 1
        return last + float(self.w @ self.phi)

    def update(self, y, y_hat, learn=True):
        if y is None or not np.isfinite(y):
            y, learn = y_hat, False                    # causal imputation of the buffer; no learning
        if learn and self.phi is not None:
            pp = float(self.phi @ self.phi)
            self.pp_ema = pp if self.pp_ema is None else self.pp_ema + 0.01 * (pp - self.pp_ema)
            self.y2 = y * y if self.y2 is None else self.y2 + 1e-4 * (y * y - self.y2)   # slow scale (~10^4 steps)
            den = pp + self.eps_rel * self.pp_ema + 1e-4 * self.y2   # scale-relative floors: invariant, survive flat stretches
            if den > 0:
                self.w += (self.mu * (y - y_hat) / den) * self.phi; self.fp += 4 * len(self.w) + 6
        if learn and self.s and self.n >= 1:
            ph = self.n % self.s; self.G[ph] += self.ap * ((y - self._b(1)) - self.G[ph]); self.fp += 4
        if learn:
            self.mew = y if self.mew is None else self.mew + self.am * (y - self.mew); self.fp += 3
        self.buf[self.n % self.Lb] = y; self.n += 1


# ------------------------------------------------------------------ the forecaster
class LebreV052:
    def __init__(self, d, season=None, option="IIb", L=32, M_max=4, m_slots=2, mu=0.1, alpha=0.05,
                 eps_add=0.002, eps_swap=0.002, eps_rem=-0.002, clip_k=2.0, probes=2, screen_w=0.2,
                 decide_every=10, n_min=100, T_max=3000, cooldown=2000, rem_period=2000, lam=0.99, eta=0.5,
                 alpha_cov=0.1, gamma_q=0.1, every=8, clip_x=8.0, screen_z=2.0, test_every=1, init_from_screen=False,
                 screen_norm="analytic", input_contract=True, self_input=True, target_contract=False, kappa=8.0,
                 chal="nlms", chal_warm=0, chal_persist=False, chal_forget=1.0):
        # the target's own past (y_{t-1}, forward-filled) is one more dictionary input, standardised causally exactly as
        # the environment standardises the exogenous inputs (EMA, alpha = 1e-4, from mean 0 / variance 1)
        self.self_input = self_input; self.ylast = 0.0; self.ym = 0.0; self.yv = 1.0
        d = d + 1 if self_input else d
        self.d, self.L, self.option = d, L, option
        self.M = Memory(season)
        self.M_max, self.m_slots, self.mu, self.alpha = M_max, m_slots, mu, alpha
        self.eps = {"add": eps_add, "swap": eps_swap, "rem": eps_rem}
        self.clip_k, self.probes, self.screen_w, self.screen_z = clip_k, probes, screen_w, screen_z
        self.decide_every, self.n_min, self.T_max, self.cooldown, self.rem_period = decide_every, n_min, T_max, cooldown, rem_period
        self.lam, self.eta, self.alpha_cov, self.gamma_q, self.every, self.clip_x = lam, eta, alpha_cov, gamma_q, every, clip_x
        self.test_every, self.init_from_screen, self.screen_norm = test_every, init_from_screen, screen_norm
        self.input_contract = input_contract; self.quar_until = -1
        self.target_contract, self.kappa, self.n_target_out = target_contract, kappa, 0
        # challenger coefficient learner: "nlms" (one coefficient, as before) or "rls2" (recursive least squares, within
        # the episode, on [atom, current value of the atom's own source input] so a lag is judged net of what x_t already
        # carries); the first chal_warm samples of an episode only train the challenger (a predictable subsequence)
        self.chal, self.chal_warm = chal, chal_warm
        # chal_persist: the challenger's own estimate (w, P, samples seen) lives with its persistent hypothesis, so a paused
        # experiment resumes where it stopped instead of relearning from zero (forgetting chal_forget: the base keeps moving)
        self.chal_persist, self.chal_forget = chal_persist, chal_forget
        # dictionary: lags, low-pass filtered inputs, residual latent states
        self.cands = [("lag", i, k) for i in range(d) for k in range(1, L + 1)] + \
                     [("lp", i, p) for i in range(d) for p in POLES] + [("res", p) for p in POLES]
        self.H = np.zeros((L + 2, d)); self.q = np.zeros((d, len(POLES))); self.r = np.zeros(len(POLES))
        self.base = np.zeros(d + 1)                                  # bias + current inputs
        self.active = {}                                             # key -> theta
        self.contrib_ema = {}
        self.screen = {c: 0.0 for c in self.cands}; self.spow = {c: 1.0 for c in self.cands}; self.probe_ptr = 0
        # prewhitened screening (Box-Jenkins identification, AR(1) per input): a lag atom is scored on the correlation of
        # u_i(t-k) = x_i(t-k) - a_i x_i(t-k-1) with the residual filtered by the SAME a_i, so smooth, collinear inputs no
        # longer smear the cross-correlation over neighbouring lags; a_i = causal EMA estimate of the lag-1 autocorrelation
        self.pw_c0 = np.ones(d); self.pw_c1 = np.zeros(d); self.res_prev = 0.0; self.pres2 = np.ones(d)
        self.engine = ChangeEngine(alpha, 2 * len(self.cands), m_slots, n_min, T_max)
        self.last_tested = {}; self.last_rem = {}
        self.events = []; self.t = 0
        self.e2 = None; self.sig = 1.0; self.e2r = None; self.sigr = 1.0; self.res2 = None
        self.D = 0.0; self.wS = 0.5                                  # option II
        self.qhat = None; self.qacc = 0.0; self.hits = []
        self.fp = {"memory": 0.0, "structure": 0.0, "experiments": 0.0, "screening": 0.0, "control": 0.0}

    # ---------------- features (values available before y_t)
    def phi(self, key):
        if key[0] == "lag":
            return self.H[key[2], key[1]]
        if key[0] == "lp":
            return self.q[key[1], POLES.index(key[2])]
        return self.r[POLES.index(key[1])]

    def _pw_a(self):
        return np.clip(self.pw_c1 / np.maximum(self.pw_c0, 1e-6), -0.999, 0.999)

    def _cfeat(self, key):
        """challenger regressors: the atom and, for input atoms, the current value of its source input"""
        if key[0] in ("lag", "lp"):
            return np.array([self.phi(key), self.H[0, key[1]]])
        return np.array([self.phi(key)])

    @staticmethod
    def design_power(key):
        """power of a feature under the input contract (standardised inputs; unit-variance innovations), as in v0.51"""
        if key[0] == "lag":
            return 1.0
        p = key[2] if key[0] == "lp" else key[1]
        return (1.0 - p) / (1.0 + p)

    def label(self, key):
        if key[0] == "lag":
            return f"x{key[1]} atrasado {key[2]}"
        if key[0] == "lp":
            return f"x{key[1]} filtrado (polo {key[2]})"
        return f"estado latente do resíduo (polo {key[1]})"

    def _struct_pred(self, x):
        xb = np.concatenate(([1.0], x))
        s = float(self.base @ xb) + sum(th * self.phi(k) for k, th in self.active.items())
        self.fp["structure"] += 2 * (self.d + 1) + 2 * len(self.active)
        return s, xb

    # ---------------- one step
    def step(self, x, y, quarantine=False):
        if self.self_input:
            v = self.ylast
            x = np.append(np.asarray(x, float), (v - self.ym) / math.sqrt(self.yv + 1e-6))
            dlt = v - self.ym; self.ym += 1e-4 * dlt
            self.yv = max((1 - 1e-4) * self.yv + 1e-4 * (v - self.ym) * dlt, 1e-4); self.fp["structure"] += 9
        x = np.nan_to_num(x)
        if self.input_contract and np.any(np.abs(x) > self.clip_x):   # P6 (as v0.45/v0.51): a clipped value stays readable
            self.quar_until = self.t + self.L                          # for L lags, so structure neither learns nor tests
        x = np.clip(x, -self.clip_x, self.clip_x)
        # shift lag history (H[k] = x_{t-k}); H[0] = x_t is the base
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = x
        if self.screen_norm == "prewhite":
            self.pw_c0 += 1e-3 * (x * x - self.pw_c0); self.pw_c1 += 1e-3 * (x * self.H[1] - self.pw_c1)
            self.fp["screening"] += 6 * self.d
        m = self.M.predict()
        s, xb = self._struct_pred(x)
        wS = 1.0 if self.option == "I" else self.wS
        f = (m + s) if self.option == "I" else (m + wS * (s - m))
        judge_S = self.option == "IIb"                                  # IIb: experiments compare S vs S + Delta
        ref = s if judge_S else f; wD = 1.0 if judge_S else wS
        # challenger outputs
        test_step = self.t % self.test_every == 0          # evidence on a predictable subsequence (as v0.51)
        outs = []
        for ex in (self.engine.slots if test_step else []):
            a = (float(ex.w @ self._cfeat(ex.add_key)) if self.chal == "rls2" else ex.theta * self.phi(ex.add_key)) if ex.add_key else 0.0
            r = self.active.get(ex.rem_key, 0.0) * self.phi(ex.rem_key) if ex.rem_key else 0.0
            outs.append(ref + wD * (a - r))
        self.fp["experiments"] += 4 * len(outs)
        y_ok = y is not None and np.isfinite(y)
        mem_learn = y_ok and not quarantine
        if y_ok and self.target_contract and self.t >= 200 and abs(y - f) > self.kappa * self.sig:   # after the scale warms up
            # P6 for the target: a value > kappa sigma from the forecast is outside the contract. It is stored clipped
            # (memory buffer, own-past input, residual states) and produces neither learning nor evidence.
            y = f + math.copysign(self.kappa * self.sig, y - f); mem_learn = False; self.n_target_out += 1
        learn = mem_learn and not (self.input_contract and self.t <= self.quar_until)   # structural learning/evidence
        if y_ok:
            e = y - f
            er = y - ref
            self.e2r = er * er if self.e2r is None else self.e2r + (1 - self.lam) * (er * er - self.e2r)
            B = self.clip_k * (self.sig if not judge_S else self.sigr)
            lf = min(er * er / (B * B), 1.0)
            # structure residual target
            res = (y - m - s) if self.option == "I" else (y - s)
            if learn:
                # experiments: evidence + challenger coefficient (NLMS on the same residual)
                for ex, g in zip(self.engine.slots if test_step else [], outs):
                    lg = min((y - g) ** 2 / (B * B), 1.0)
                    ex.k = getattr(ex, "k", 0) + 1
                    if ex.k > self.chal_warm:
                        ex.observe(lf - lg - ex.eps)
                    if ex.add_key and self.chal == "rls2":
                        f_ = self._cfeat(ex.add_key)
                        rr = res + (self.active.get(ex.rem_key, 0.0) * self.phi(ex.rem_key) if ex.rem_key else 0.0)
                        lam_ = self.chal_forget
                        Pf = ex.P @ f_; kg = Pf / (lam_ + f_ @ Pf)
                        ex.w = ex.w + kg * (rr - ex.w @ f_); ex.P = (ex.P - np.outer(kg, Pf)) / lam_
                        if self.chal_persist:
                            ex.hyp.chal_state = (ex.w, ex.P, ex.k)
                        ex.theta = float(ex.w[0])
                        self.fp["experiments"] += 4 * len(f_) ** 2 + 4 * len(f_)
                    elif ex.add_key:
                        ph = self.phi(ex.add_key)
                        rr = res + (self.active.get(ex.rem_key, 0.0) * self.phi(ex.rem_key) if ex.rem_key else 0.0)
                        tgt = rr - ex.theta * ph
                        ex.pow = ph * ph if ex.pow is None else ex.pow + 0.01 * (ph * ph - ex.pow)
                        ex.theta += self.mu * tgt * ph / (ex.pow + 1e-6)   # normalised by the feature's running power
                self.fp["experiments"] += 24 * len(outs)
                # live structure: NLMS on base + active atoms
                feats = list(xb) + [self.phi(k) for k in self.active]
                den = sum(v * v for v in feats) + 1e-6
                g_ = self.mu * res / den
                self.base += g_ * xb
                for k in self.active:
                    ph = self.phi(k); self.active[k] += g_ * ph
                    c = abs(self.active[k] * ph)
                    self.contrib_ema[k] = c if k not in self.contrib_ema else self.contrib_ema[k] + 0.01 * (c - self.contrib_ema[k])
                self.fp["structure"] += 4 * len(feats) + 4
                # screening: probe a few dictionary candidates (EMA of residual x feature)
                if self.screen_norm == "prewhite":
                    a_ = self._pw_a(); pres = res - a_ * self.res_prev
                    self.pres2 += 0.01 * (pres * pres - self.pres2); self.fp["screening"] += 5 * self.d
                for _ in range(self.probes):
                    c = self.cands[self.probe_ptr]; self.probe_ptr = (self.probe_ptr + 1) % len(self.cands)
                    if self.screen_norm == "prewhite" and c[0] == "lag":
                        i_, k_ = c[1], c[2]
                        ph = self.H[k_, i_] - a_[i_] * self.H[k_ + 1, i_]
                        self.screen[c] += self.screen_w * (pres[i_] * ph - self.screen[c])
                        continue
                    ph = self.phi(c)
                    self.screen[c] += self.screen_w * (res * ph - self.screen[c])
                    if self.init_from_screen or self.screen_norm == "ema":
                        self.spow[c] += self.screen_w * (ph * ph - self.spow[c])
                self.res2 = res * res if self.res2 is None else self.res2 + (1 - self.lam) * (res * res - self.res2)
                self.res_prev = res
                self.fp["screening"] += (7 if (self.init_from_screen or self.screen_norm == "ema") else 4) * self.probes
            # option II: dynamic model averaging
            if self.option in ("II", "IIb"):
                es, em = y - s, y - m
                self.D = self.lam * self.D + (es * es - em * em) / (self.sig ** 2 + 1e-12)
                self.fp["control"] += 7
                if self.t % self.every == 0:                   # one exp every `every` steps (as v0.51)
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
            u = e / self.sig
        else:
            u = 0.0; self.hits.append(None)
        self.M.update(y if y_ok else None, m, learn=mem_learn)
        if self.self_input and y_ok:
            self.ylast = float(y)
        # update filtered states (predictable for t+1)
        xq = x[:, None]
        self.q = np.array(POLES)[None, :] * self.q + (1 - np.array(POLES))[None, :] * xq
        self.r = np.array(POLES) * self.r + (1 - np.array(POLES)) * u
        self.fp["structure"] += 3 * self.d * len(POLES) + 3 * len(POLES)
        if self.t % self.decide_every == 0 and self.t > 0:
            self._decide()
        self.t += 1
        return f

    # ---------------- lifecycle (policy; the statistics live in ChangeEngine)
    def _open(self, kind, add_key, rem_key):
        hkey = ("out", rem_key) if kind == "rem" else ("in", add_key)
        ex = self.engine.open(kind, add_key, rem_key, hkey, self.eps[kind], self.t)
        if add_key and self.chal == "rls2":
            n_ = len(self._cfeat(add_key)); ex.w = np.zeros(n_); ex.P = 10.0 * np.eye(n_)
            st = getattr(ex.hyp, "chal_state", None)
            if self.chal_persist and st is not None:
                ex.w, ex.P, ex.k = st[0].copy(), st[1].copy(), st[2]
        if add_key and self.init_from_screen:
            ex.theta = self.screen[add_key] / max(self.spow[add_key], 1e-6)   # least-squares slope from the screen (past only)
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
        if changed:   # running experiments about atoms that just changed no longer describe the live model: stop them
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
            self.active[ex.add_key] = ex.theta
            if self.chal == "rls2" and ex.add_key[0] in ("lag", "lp"):
                self.base[1 + ex.add_key[1]] += float(ex.w[1])
        self.engine.consume(ex)
        self.events.append((self.t, "accepted", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.hyp.n))

    def _fill(self):
        busy = self.engine.busy_keys()
        while self.engine.free_slots() > 0:
            # 1) periodic removal test of active atoms
            due = [a for a in self.active if a not in busy and self.t - self.last_rem.get(a, -10 ** 9) >= self.rem_period
                   and self.t - self.last_tested.get(a, -10 ** 9) >= self.n_min]
            if due:
                a = due[0]; self.last_rem[a] = self.t; self._open("rem", None, a); busy.add(a); continue
            # 2) best screened candidate not active, not busy, not in cool-down
            pool = [c for c in self.cands if c not in self.active and c not in busy
                    and self.t - self.last_tested.get(c, -10 ** 9) >= self.cooldown]
            if not pool:
                break
            # rank by a correlation-like score: every atom type competes on the same scale (low-pass states have low power)
            sres = math.sqrt(self.res2) if self.res2 else self.sig
            if self.screen_norm == "prewhite":
                # every score in residual-s.d. units so lag (prewhitened) and filter/latent atoms share one scale
                a_ = self._pw_a()
                def sc(k):
                    if k[0] == "lag":
                        return abs(self.screen[k]) / math.sqrt(max(1.0 - a_[k[1]] ** 2, 1e-3) * self.pres2[k[1]]) * sres
                    return abs(self.screen[k]) / math.sqrt(self.design_power(k))
            elif self.screen_norm == "analytic":
                sc = lambda k: abs(self.screen[k]) / math.sqrt(self.design_power(k))
            elif self.screen_norm == "ema":
                sc = lambda k: abs(self.screen[k]) / math.sqrt(max(self.spow[k], 1e-12))
            else:
                sc = lambda k: abs(self.screen[k])
            c = max(pool, key=sc)
            # open only if the score is ~screen_z noise s.d. away from 0 (EMA of residual x unit-power feature)
            sres = math.sqrt(self.res2) if self.res2 else self.sig   # scale of the residual the screen is built on
            if sc(c) < self.screen_z * sres * math.sqrt(self.screen_w / (2 - self.screen_w)):
                break
            if len(self.active) < self.M_max:
                self._open("add", c, None)
            else:
                a = min((k for k in self.active if k not in busy), key=lambda k: self.contrib_ema.get(k, float('inf')), default=None)
                if a is None:
                    break
                self._open("swap", c, a); busy.add(a)
            busy.add(c)
            self.fp["control"] += len(self.cands) / self.decide_every   # ranking cost, amortised

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
