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

POLES = (0.8, 0.95)            # pole 0.5 dropped (dev, 26/09): its ~2-step memory is covered by lags 1-2


# ------------------------------------------------------------------ e-LOND gamma sequence (sum <= 1)
def _gamma_const(n=10 ** 6):
    k = np.arange(1, n + 1, dtype=float)
    s = float(np.sum(1.0 / (k * np.log(k + 1) ** 2)))
    return 1.0 / (s + 1.0 / math.log(n + 1))          # tail bound of the integral


GAMMA_C = _gamma_const()


def gamma_k(k):
    return GAMMA_C / (k * math.log(k + 1) ** 2)


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


# ------------------------------------------------------------------ persistent hypothesis (one e-process per candidate change)
class Hypothesis:
    """Weak null (Choe & Ramdas 2024): over the steps at which this change was tested, the challenger did not improve the
    clipped loss of the live model by more than eps on average. The e-process accumulates across episodes; pauses between
    episodes are a predictable subsequence (Choe & Ramdas, Sec. F.1), so validity is preserved."""
    LAMBDAS_FRAC = 0.9 * 2.0 ** -np.arange(8)            # lambda grid as fraction of 1/c (uniform mixture)

    def __init__(self, eps, alpha_level, idx):
        self.eps = eps; self.c = 2.0 * (1.0 + abs(eps))
        self.alpha = alpha_level; self.log_thr = math.log(1.0 / alpha_level); self.idx = idx
        self.S = 0.0; self.V = 0.0; self.n = 0; self.mean = 0.0
        self.lam = self.LAMBDAS_FRAC / self.c
        self.psi = (-np.log(1 - self.c * self.lam) - self.c * self.lam) / self.c ** 2

    def observe(self, d):
        gamma = max(-self.c / 2, min(self.c / 2, self.mean))   # predictable centring (past mean)
        self.S += d; self.V += (d - gamma) ** 2; self.n += 1
        self.mean += (d - self.mean) / self.n

    def log_e(self):
        a = self.lam * self.S - self.psi * self.V
        m = a.max()
        return float(m + math.log(np.mean(np.exp(a - m))))


class Experiment:
    """One episode: a challenger (its own coefficient) evaluated on a slot; evidence goes to the persistent hypothesis."""

    def __init__(self, kind, add_key, rem_key, hyp, t0):
        self.kind, self.add_key, self.rem_key, self.hyp, self.t0 = kind, add_key, rem_key, hyp, t0
        self.theta = 0.0; self.pow = None; self.S = 0.0; self.n = 0
        self.eps = hyp.eps

    def observe(self, d):
        self.hyp.observe(d); self.S += d; self.n += 1


# ------------------------------------------------------------------ the forecaster
class LebreV052:
    def __init__(self, d, season=None, option="IIb", L=32, M_max=4, m_slots=2, mu=0.1, alpha=0.05,
                 eps_add=0.002, eps_swap=0.002, eps_rem=-0.002, clip_k=2.0, probes=2, screen_w=0.2,
                 decide_every=10, n_min=100, T_max=3000, cooldown=2000, rem_period=2000, lam=0.99, eta=0.5,
                 alpha_cov=0.1, gamma_q=0.1, every=8, clip_x=8.0, screen_z=2.0, test_every=1, init_from_screen=False):
        self.d, self.L, self.option = d, L, option
        self.M = Memory(season)
        self.M_max, self.m_slots, self.mu, self.alpha = M_max, m_slots, mu, alpha
        self.eps = {"add": eps_add, "swap": eps_swap, "rem": eps_rem}
        self.clip_k, self.probes, self.screen_w, self.screen_z = clip_k, probes, screen_w, screen_z
        self.decide_every, self.n_min, self.T_max, self.cooldown, self.rem_period = decide_every, n_min, T_max, cooldown, rem_period
        self.lam, self.eta, self.alpha_cov, self.gamma_q, self.every, self.clip_x = lam, eta, alpha_cov, gamma_q, every, clip_x
        self.test_every, self.init_from_screen = test_every, init_from_screen
        # dictionary: lags, low-pass filtered inputs, residual latent states
        self.cands = [("lag", i, k) for i in range(d) for k in range(1, L + 1)] + \
                     [("lp", i, p) for i in range(d) for p in POLES] + [("res", p) for p in POLES]
        self.H = np.zeros((L + 1, d)); self.q = np.zeros((d, len(POLES))); self.r = np.zeros(len(POLES))
        self.base = np.zeros(d + 1)                                  # bias + current inputs
        self.active = {}                                             # key -> theta
        self.contrib_ema = {}
        self.screen = {c: 0.0 for c in self.cands}; self.spow = {c: 1.0 for c in self.cands}; self.probe_ptr = 0
        self.slots = []; self.k_started = 0; self.n_accepted = 0; self.hyps = {}; self.n_hyp = 0
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
        x = np.clip(np.nan_to_num(x), -self.clip_x, self.clip_x)
        # shift lag history (H[k] = x_{t-k}); H[0] = x_t is the base
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = x
        m = self.M.predict()
        s, xb = self._struct_pred(x)
        wS = 1.0 if self.option == "I" else self.wS
        f = (m + s) if self.option == "I" else (m + wS * (s - m))
        judge_S = self.option == "IIb"                                  # IIb: experiments compare S vs S + Delta
        ref = s if judge_S else f; wD = 1.0 if judge_S else wS
        # challenger outputs
        test_step = self.t % self.test_every == 0          # evidence on a predictable subsequence (as v0.51)
        outs = []
        for ex in (self.slots if test_step else []):
            a = ex.theta * self.phi(ex.add_key) if ex.add_key else 0.0
            r = self.active.get(ex.rem_key, 0.0) * self.phi(ex.rem_key) if ex.rem_key else 0.0
            outs.append(ref + wD * (a - r))
        self.fp["experiments"] += 4 * len(outs)
        y_ok = y is not None and np.isfinite(y)
        learn = y_ok and not quarantine
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
                for ex, g in zip(self.slots if test_step else [], outs):
                    lg = min((y - g) ** 2 / (B * B), 1.0)
                    ex.observe(lf - lg - ex.eps)
                    if ex.add_key:
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
                for _ in range(self.probes):
                    c = self.cands[self.probe_ptr]; self.probe_ptr = (self.probe_ptr + 1) % len(self.cands)
                    ph = self.phi(c)
                    self.screen[c] += self.screen_w * (res * ph - self.screen[c])
                    if self.init_from_screen:
                        self.spow[c] += self.screen_w * (ph * ph - self.spow[c])
                self.res2 = res * res if self.res2 is None else self.res2 + (1 - self.lam) * (res * res - self.res2)
                self.fp["screening"] += (7 if self.init_from_screen else 4) * self.probes
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
        self.M.update(y if y_ok else None, m, learn=learn)
        # update filtered states (predictable for t+1)
        xq = x[:, None]
        self.q = np.array(POLES)[None, :] * self.q + (1 - np.array(POLES))[None, :] * xq
        self.r = np.array(POLES) * self.r + (1 - np.array(POLES)) * u
        self.fp["structure"] += 3 * self.d * len(POLES) + 3 * len(POLES)
        if self.t % self.decide_every == 0 and self.t > 0:
            self._decide()
        self.t += 1
        return f

    # ---------------- lifecycle
    def _hyp(self, hkey, eps):
        """persistent hypothesis for a change; level fixed at creation (LOND-type, async-safe)."""
        if hkey not in self.hyps:
            self.n_hyp += 1; P = 2 * len(self.cands)
            g = 1.0 / (2 * P) if self.n_hyp <= P else 0.5 * gamma_k(self.n_hyp - P)   # sum of gammas <= 1
            self.hyps[hkey] = Hypothesis(eps, min(self.alpha * g * (self.n_accepted + 1), 0.5), self.n_hyp)
        return self.hyps[hkey]

    def _open(self, kind, add_key, rem_key):
        self.k_started += 1
        hkey = ("out", rem_key) if kind == "rem" else ("in", add_key)
        ex = Experiment(kind, add_key, rem_key, self._hyp(hkey, self.eps[kind]), self.t)
        if add_key and self.init_from_screen:
            ex.theta = self.screen[add_key] / max(self.spow[add_key], 1e-6)   # least-squares slope from the screen (past only)
        self.slots.append(ex)
        for k in (add_key, rem_key):
            if k:
                self.last_tested[k] = self.t

    def _decide(self):
        keep = []
        for ex in self.slots:
            le = ex.hyp.log_e(); self.fp["control"] += 3 * len(ex.hyp.lam)
            if le >= ex.hyp.log_thr:
                self._accept(ex, le)
            elif ex.n >= self.T_max or (ex.n >= self.n_min and ex.S <= 0.0):   # scan rule: not ahead -> free the slot
                self.events.append((self.t, "closed", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.n))
            else:
                keep.append(ex)
        self.slots = keep
        self._fill()

    def _accept(self, ex, le):
        if ex.rem_key and ex.rem_key in self.active:
            del self.active[ex.rem_key]; self.contrib_ema.pop(ex.rem_key, None)
        if ex.add_key:
            self.active[ex.add_key] = ex.theta
        self.n_accepted += 1
        self.events.append((self.t, "accepted", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.hyp.n))
        self.hyps = {k: h for k, h in self.hyps.items() if h is not ex.hyp}   # consumed: a new instance if ever retested
        # experiments involving changed atoms are no longer about the live model -> close them
        changed = {ex.add_key, ex.rem_key}
        self.slots = [s for s in self.slots if s is ex or not ({s.add_key, s.rem_key} & changed - {None})]

    def _busy(self):
        return {k for ex in self.slots for k in (ex.add_key, ex.rem_key) if k}

    def _fill(self):
        busy = self._busy()
        while len(self.slots) < self.m_slots:
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
            c = max(pool, key=lambda k: abs(self.screen[k]))
            # open only if the screen is ~screen_z noise s.d. away from 0 (EMA of residual x unit-power feature)
            sres = math.sqrt(self.res2) if self.res2 else self.sig   # scale of the residual the screen is built on
            if abs(self.screen[c]) < self.screen_z * sres * math.sqrt(self.screen_w / (2 - self.screen_w)):
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
    def structure(self):
        return sorted(self.active)

    def coverage(self):
        h = [v for v in self.hits if v is not None]
        return float(np.mean(h)) if h else float("nan")

    def fp_total(self):
        return sum(self.fp.values()) + self.M.fp
