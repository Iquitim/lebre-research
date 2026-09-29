"""lebre_v052h.py — PROTOTYPE of LEBRE v0.52 with HIERARCHICAL input-level hypotheses (27/09/2026).

Builds on lebre_v052u.py (input-level units), which improved the real development data but diluted sharp lags (a band
mean keeps ~1/width of a single-lag effect on white inputs). Here the response of an accepted input is refined as a tree:

  level 0  unit ("in", i): does input i help? block = means of its past over the octave bands
           [1], [2-3], [4-7], [8-15], [16-31] (+ the challenger re-fits the coefficient of x_i(t));
  level 1+ split ("split", i, lo, hi) of a band of an ACTIVE unit: replace mean(lo..hi) by the means of its two halves.
           Each split is one more hypothesis of the same change stream (hierarchical testing: Meinshausen 2008,
           Yekutieli 2008 — a child is only tested after its parent was accepted).

On smooth inputs the halves carry the same information and splits are not accepted (the response stays coarse); on
white inputs a split gains and the response is refined down to single lags. Units ("res",) = residual latent states.

Statistics are those of lebre_v052.py (ChangeEngine: Choe & Ramdas e-process on clipped loss differences minus a margin,
persistent hypotheses, e-LOND-type levels, scan rule; option IIb, changes judged on the structural expert S).
Cost: band sums are running sums (2 FP per tracked segment per step); the prewhitened band means of the unit screen are
derived on demand from them; the screen runs every `screen_every` steps for every unit and every candidate split.
"""
import math

import numpy as np

from change_engine import ChangeEngine
from lebre_v052 import POLES, Memory

BANDS = ((1, 1), (2, 3), (4, 7), (8, 15), (16, 31))


class MemoryW(Memory):
    """memory expert with a second declared cycle (e.g. the week, 168 h, on top of the day, 24 h): two more features,
    the second-cycle naive y_{t-S2} - y_{t-1} and its one-cycle increment y_{t-S2+1} - y_{t-S2}"""

    def __init__(self, season, season2, **kw):
        super().__init__(season, **kw)
        self.s2 = season2
        self.feats = self.feats + ("sn2", "si2")
        self.Lb = max(self.Lb, season2 + 2)
        self.buf = np.zeros(self.Lb); self.w = np.zeros(len(self.feats))

    def predict(self):
        if self.n < self.Lb:
            self.phi = None
            return self._b(1) if self.n else 0.0
        last, s = self._b(1), self.s
        v = [(self.mew - last) if self.mew is not None else 0.0, last - self._b(2)]
        if s:
            v += [self._b(s) - last, self._b(s - 1) - self._b(s), self.G[self.n % s]]
        v += [self._b(self.s2) - last, self._b(self.s2 - 1) - self._b(self.s2)]
        self.phi = np.array(v); self.fp += 3 * len(v) + 1
        return last + float(self.w @ self.phi)


def halves(seg):
    lo, hi = seg; mid = (lo + hi) // 2
    return (lo, mid), (mid + 1, hi)


class LebreV052H:
    def __init__(self, d, season=None, M_max=4, m_slots=2, mu=0.1, alpha=0.05, eps_add=0.002, eps_swap=0.002,
                 eps_rem=-0.002, eps_split=0.002, clip_k=2.0, decide_every=10, n_min=100, T_max=5000, cooldown=2000,
                 rem_period=2000, lam=0.99, eta=0.5, alpha_cov=0.1, gamma_q=0.1, every=8, clip_x=8.0,
                 input_contract=True, self_input=True, chal_warm=200, screen_every=4, screen_w=0.02,
                 screen_q=15.09, split_q=6.63, rls_p0=10.0, splits=True, peak=True, rls_every=1,
                 evidence="psiE2", peak_persist=False, scale_floor=0.0, lazy_halves=False,
                 live_every=1, rls_after_warm=False, screen_skip_active=False, track_groups=False, season2=None,
                 paired=False, screen_raw=False, chal_persist=False, chal_forget=1.0, stagger=False,
                 screen_spread=False, peak_split=False, peak_until=None,
                 all_on=False, rls_live=False, gap_hold=False, out_contract=False, out_margin=0.5, out_rho=1e-3):
        self.self_input = self_input; self.ylast = 0.0; self.ym = 0.0; self.yv = 1.0
        d = d + 1 if self_input else d
        self.d, self.L = d, BANDS[-1][1]
        self.M = MemoryW(season, season2) if season2 else Memory(season)
        self.M_max, self.mu, self.alpha, self.clip_k = M_max, mu, alpha, clip_k
        self.eps = {"add": eps_add, "swap": eps_swap, "rem": eps_rem, "split": eps_split}
        self.decide_every, self.n_min, self.cooldown, self.rem_period = decide_every, n_min, cooldown, rem_period
        self.lam, self.eta, self.alpha_cov, self.gamma_q, self.every, self.clip_x = lam, eta, alpha_cov, gamma_q, every, clip_x
        self.input_contract = input_contract; self.quar_until = -1
        self.chal_warm, self.screen_every, self.screen_w = chal_warm, screen_every, screen_w
        self.screen_q, self.split_q, self.rls_p0, self.splits = screen_q, split_q, rls_p0, splits
        # peak: an input challenger also carries its single strongest lag, chosen by the challenger itself from the
        # prewhitened cross-correlation over the first half of its warm-up (past only: the evidence starts after the
        # warm-up), so a sharp lag is not diluted in its band mean
        self.peak = peak
        self.rls_every = rls_every                                   # challenger RLS on every k-th sample
        # peak_persist: the prewhitened cross-products that choose the peak lag live with the persistent hypothesis, so a
        # retest starts from all the (past) samples of earlier episodes instead of 100 new ones
        self.peak_persist = peak_persist
        # scale_floor: the loss scale of the experiments never drops below this fraction of the slow scale of y (EMA,
        # 1e-4), as the memory's slow floor: on a flat stretch (y constant) a tiny absolute gain must not look large
        self.scale_floor = scale_floor; self.y_sm = None; self.y_sv = 0.0
        # lazy_halves: the halves of active segments are read only by the split screen / split challengers, so they are
        # summed from the stored history when needed instead of being kept as running sums (same values)
        self.lazy_halves = lazy_halves
        # cost options (27/09/2026): live_every — the weights of the active blocks follow NLMS every k-th step (the base
        # every step, with the last block power in the normaliser); rls_after_warm — rls_every applies only after the
        # challenger's warm-up; screen_skip_active — the unit screen skips inputs already active (their statistics are
        # not used); track_groups — causal EMA correlation of the inputs, to report equivalence groups (no decision uses it)
        self.live_every, self.rls_after_warm, self.screen_skip_active = live_every, rls_after_warm, screen_skip_active
        self.track_groups = track_groups; self._bpow = 0.0
        # paired: an input challenger (block + re-fit of x_i(t)) is judged against a paired CONTROL that re-fits only
        # x_i(t) (1-parameter RLS, same samples and warm-up), not against S: the evidence measures the block alone, not
        # the gain of estimating an existing coefficient better (DEV_LOG, measurement #5)
        self.paired = paired
        # smooth inputs (27/09/2026): screen_raw — the unit screen also uses the RAW band means (detection of a unit does
        # not need prewhitening, which kills the signal of a very smooth input); chal_persist — an input challenger's
        # RLS state (and peak lag) lives with its persistent hypothesis and resumes after a short re-warm-up, with
        # forgetting chal_forget; stagger — at most one experiment in warm-up at a time (bounds the cost peaks)
        self.screen_raw, self.chal_persist, self.chal_forget, self.stagger = screen_raw, chal_persist, chal_forget, stagger
        self.rw_xy = np.zeros((len(BANDS), d)); self.rw_xx = np.ones((len(BANDS), d)) * 1e-3
        # screen_spread: every part of the screen (each input, the residual unit, the groups, each split) is updated on
        # its OWN phase, once every screen_every steps as before — same statistics, the cost is spread over the steps
        self.screen_spread = screen_spread
        # peak_split: the peak-lag statistic processes half of the lags per step (alternating), until peak_until samples
        # of the episode (default chal_warm // 2), so each lag keeps the same number of samples at half the peak cost
        self.peak_split = peak_split; self.peak_until = peak_until if peak_until is not None else chal_warm // 2
        self.g_m = np.zeros(d); self.g_c = np.eye(d)
        self.units = [("in", i) for i in range(d)] + [("res",)]
        nb = len(BANDS)
        self.H = np.zeros((self.L + 2, d))                           # H[k] = x_{t-k}
        self.bs = np.zeros((nb, d))                                  # running sums of the octave bands (all inputs)
        self.seg = {}                                                # (i, lo, hi) -> running sum, tracked on demand
        self.r = np.zeros(len(POLES))
        self.base = np.zeros(d + 1)
        self.active = {}                                             # unit -> {"segs": [(lo, hi)...] | None, "w": array}
        self.contrib_ema = {}
        self.a_c0 = np.ones(d); self.a_c1 = np.zeros(d); self.res_prev = 0.0
        self.sc_xy = np.zeros((nb, d)); self.sc_xx = np.ones((nb, d)) * 1e-3; self.sc_yy = np.ones(d)
        self.sr_xy = np.zeros(len(POLES)); self.sr_xx = np.ones(len(POLES)) * 1e-3; self.sr_yy = 1.0
        self.sp = {}                                                 # split key -> [xy, xx, yy] EMA
        self.engine = ChangeEngine(alpha, 2 * len(self.units), m_slots, n_min, T_max, evidence)
        self.last_tested = {}; self.last_rem = {}
        self.events = []; self.t = 0
        self.e2 = None; self.sig = 1.0; self.e2r = None; self.sigr = 1.0; self.res2 = None
        self.D = 0.0; self.wS = 0.5
        self.qhat = None; self.qacc = 0.0; self.hits = []
        self.fp = {"memory": 0.0, "structure": 0.0, "experiments": 0.0, "screening": 0.0, "control": 0.0}
        # ABLATIONS (27/09/2026): all_on — every unit active from the start (octave-band blocks of all inputs + residual
        # latent), no experiments; rls_live — the live structure (base + blocks) learned jointly by RLS (forgetting 0.9995)
        self.all_on, self.rls_live = all_on, rls_live; self.lP = None
        # GAPS (27/09/2026, after the held-out evaluation): gap_hold — while the target is missing, the memory's history
        # receives the LAST OBSERVED value (hold), never its own prediction: no closed loop through the learned weights,
        # so no recursion can diverge. out_contract — the forecast is limited to the envelope of the observed targets
        # (running max/min that relax slowly toward the slow mean, rate out_rho) widened by out_margin x its width; a
        # non-finite forecast falls back to the last observed value. Both act only on the output path (P6 for outputs).
        self.gap_hold, self.out_contract, self.out_margin, self.out_rho = gap_hold, out_contract, out_margin, out_rho
        self.last_obs = None; self.env_hi = None; self.env_lo = None; self.env_m = None; self.env_n = 0; self.n_clipped = 0
        if all_on:
            for u in self.units:
                self.active[u] = {"segs": list(BANDS) if u[0] == "in" else None, "w": np.zeros(len(BANDS) if u[0] == "in" else len(POLES))}
            self.engine.m_slots = 0; self._retrack()

    # ---------------- segment sums
    def _track(self, i, seg):
        k = (i, seg[0], seg[1])
        if k not in self.seg:
            self.seg[k] = float(self.H[seg[0]:seg[1] + 1, i].sum())   # initialised from the stored history (once)
            self.fp["structure"] += seg[1] - seg[0] + 1

    def _mean(self, i, seg):
        k = (i, seg[0], seg[1])
        if k in self.seg:
            return self.seg[k] / (seg[1] - seg[0] + 1)
        self.fp["structure"] += seg[1] - seg[0] + 1                   # untracked (lazy half): sum from the history
        return float(self.H[seg[0]:seg[1] + 1, i].sum()) / (seg[1] - seg[0] + 1)

    def _retrack(self):
        """keep exactly the segments needed: active segments and their halves"""
        need = set()
        for u, st in self.active.items():
            if u[0] == "in":
                for sg in st["segs"]:
                    need.add((u[1],) + sg)
                    if sg[1] > sg[0] and not self.lazy_halves:
                        for h in halves(sg):
                            need.add((u[1],) + h)
        for k in need:
            self._track(k[0], k[1:])
        for k in [k for k in self.seg if k not in need]:
            del self.seg[k]

    # ---------------- features (values available before y_t)
    def block(self, unit):
        if unit[0] == "in":
            i = unit[1]
            st = self.active.get(unit)
            if st is None:                                           # candidate unit: the octave bands
                return np.array([self.bs[b, i] / (hi - lo + 1) for b, (lo, hi) in enumerate(BANDS)])
            return np.array([self._mean(i, sg) for sg in st["segs"]])
        return self.r.copy()

    def cfeat(self, key):
        if key[0] == "split":
            i, sg = key[1], key[2:]
            return np.array([self._mean(i, h) for h in halves(sg)])
        f = self.block(key)
        return np.append(f, self.H[0, key[1]]) if key[0] == "in" else f

    def _cf(self, ex):
        """challenger regressors of an experiment: [block (+ peak lag), current value] for inputs"""
        key = ex.add_key
        if key[0] == "in" and getattr(ex, "kstar", None):
            f = self.cfeat(key)
            return np.concatenate([f[:-1], [self.H[ex.kstar, key[1]]], f[-1:]])
        return self.cfeat(key)

    def _seg_contrib(self, key):
        """current contribution of the segment a split would replace"""
        i, sg = key[1], key[2:]
        st = self.active[("in", i)]
        return float(st["w"][st["segs"].index(sg)]) * self._mean(i, sg)

    def label(self, unit):
        return f"entrada x{unit[1]} (resposta por faixas)" if unit[0] == "in" else "estado latente do resíduo"

    def response(self, unit):
        """recovered response of an active input: list of ((lo, hi), weight per lag)"""
        st = self.active[unit]
        return [(sg, float(w) / (sg[1] - sg[0] + 1)) for sg, w in zip(st["segs"], st["w"])]

    def _struct_pred(self, x):
        xb = np.concatenate(([1.0], x))
        s = float(self.base @ xb) + sum(float(st["w"] @ self.block(u)) for u, st in self.active.items())
        self.fp["structure"] += 2 * (self.d + 1) + sum(3 * len(st["w"]) for st in self.active.values())
        return s, xb

    def _a(self):
        return np.clip(self.a_c1 / np.maximum(self.a_c0, 1e-6), -0.999, 0.999)

    def _shift(self, x):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = x
        for b, (lo, hi) in enumerate(BANDS):
            self.bs[b] += self.H[lo] - self.H[hi + 1]
        for k in self.seg:
            i, lo, hi = k
            self.seg[k] += self.H[lo, i] - self.H[hi + 1, i]
        self.fp["structure"] += 2 * len(BANDS) * self.d + 2 * len(self.seg)

    # ---------------- one step
    def step(self, x, y, quarantine=False):
        if self.self_input:
            v = self.ylast
            x = np.append(np.asarray(x, float), (v - self.ym) / math.sqrt(self.yv + 1e-6))
            dlt = v - self.ym; self.ym += 1e-4 * dlt
            self.yv = max((1 - 1e-4) * self.yv + 1e-4 * (v - self.ym) * dlt, 1e-4); self.fp["structure"] += 9
        x = np.nan_to_num(x)
        if self.input_contract and np.any(np.abs(x) > self.clip_x):
            self.quar_until = self.t + self.L
        x = np.clip(x, -self.clip_x, self.clip_x)
        self._shift(x)
        m = self.M.predict()
        s, xb = self._struct_pred(x)
        f = m + self.wS * (s - m)
        if self.out_contract and self.env_n >= 50:
            w_ = self.out_margin * (self.env_hi - self.env_lo)
            fc = min(max(f, self.env_lo - w_), self.env_hi + w_) if math.isfinite(f) else self.last_obs
            self.n_clipped += fc != f; f = fc; self.fp["control"] += 5
        ref = s
        outs, rrs, ctrl = [], [], []
        for ex in self.engine.slots:
            if ex.kind == "split":
                c = self._seg_contrib(ex.add_key)
                outs.append(ref - c + float(ex.w @ self._cf(ex))); rrs.append(c); ctrl.append(None)
                continue
            a = float(ex.w @ self._cf(ex)) if ex.add_key else 0.0
            r = float(self.active[ex.rem_key]["w"] @ self.block(ex.rem_key)) if ex.rem_key else 0.0
            outs.append(ref + a - r); rrs.append(r)
            has_c = getattr(ex, "wc", None) is not None
            ctrl.append(ref + ex.wc * self.H[0, ex.add_key[1]] - r if has_c else None)
        self.fp["experiments"] += 6 * len(outs)
        y_ok = y is not None and np.isfinite(y)
        mem_learn = y_ok and not quarantine
        learn = mem_learn and not (self.input_contract and self.t <= self.quar_until)
        if y_ok:
            e = y - f; er = y - ref
            self.e2r = er * er if self.e2r is None else self.e2r + (1 - self.lam) * (er * er - self.e2r)
            if self.y_sm is None:
                self.y_sm = y; self.n_y = 0
            self.n_y += 1; ry = max(1e-4, 1.0 / self.n_y)            # plain average at first, then EMA 1e-4
            dy = y - self.y_sm; self.y_sm += ry * dy; self.y_sv += ry * (dy * (y - self.y_sm) - self.y_sv)
            floor = self.scale_floor * math.sqrt(max(self.y_sv, 0.0)) if self.t >= 200 else 0.0
            B = self.clip_k * max(self.sigr, floor)
            self.fp["control"] += 8
            lf = min(er * er / (B * B), 1.0)
            res = y - s
            if learn:
                for ex, g, back, gc in zip(self.engine.slots, outs, rrs, ctrl):
                    ex.k = getattr(ex, "k", 0) + 1
                    lref = lf if gc is None else min((y - gc) ** 2 / (B * B), 1.0)   # paired control as reference
                    if ex.k > self.chal_warm or not ex.add_key:
                        ex.observe(lref - min((y - g) ** 2 / (B * B), 1.0) - ex.eps)
                    if ex.add_key:                                   # RLS on the residual the change would explain
                        rr = res + back
                        if gc is not None:                          # control: 1-parameter RLS on x_i(t)
                            xc = self.H[0, ex.add_key[1]]; pc = ex.Pc * xc; kc = pc / (1.0 + xc * pc)
                            ex.wc += kc * (rr - ex.wc * xc); ex.Pc -= kc * pc
                            self.fp["experiments"] += 12
                        if self.peak and ex.add_key[0] == "in" and ex.k <= self.peak_until:
                            self._peak_stats(ex, rr)
                        re_ = self.rls_every if (not self.rls_after_warm or ex.k > self.chal_warm) else 1
                        if ex.k % re_:
                            continue
                        fx = self._cf(ex)
                        lam_ = self.chal_forget
                        Pf = ex.P @ fx; kg = Pf / (lam_ + fx @ Pf)
                        ex.w = ex.w + kg * (rr - ex.w @ fx); ex.P = (ex.P - np.outer(kg, Pf)) / lam_
                        self.fp["experiments"] += 4 * len(fx) ** 2 + 6 * len(fx)
                self.fp["experiments"] += 8 * len(outs)
                if self.rls_live:                                        # joint RLS on base + all active blocks
                    blocks = {u: self.block(u) for u in self.active}
                    fz = np.concatenate([xb] + list(blocks.values()))
                    wz = np.concatenate([self.base] + [self.active[u]["w"] for u in blocks])
                    if self.lP is None or len(self.lP) != len(fz):
                        self.lP = 10.0 * np.eye(len(fz))
                    Pf = self.lP @ fz; kg = Pf / (0.9995 + fz @ Pf)
                    wz = wz + kg * res; self.lP = (self.lP - np.outer(kg, Pf)) / 0.9995       # res = a-priori error
                    self.base = wz[:len(xb)]; o = len(xb)
                    for u, b in blocks.items():
                        self.active[u]["w"] = wz[o:o + len(b)]; o += len(b)
                    self.fp["structure"] += 4 * len(fz) ** 2 + 6 * len(fz)
                elif self.live_every == 1 or self.t % self.live_every == 0:
                    blocks = {u: self.block(u) for u in self.active}
                    self._bpow = sum(float(b @ b) for b in blocks.values())
                    den = float(xb @ xb) + self._bpow + 1e-6
                    g_ = self.mu * res / den
                    self.base += g_ * xb
                    for u, b in blocks.items():
                        st = self.active[u]; st["w"] = st["w"] + g_ * b
                        c = abs(float(st["w"] @ b))
                        self.contrib_ema[u] = c if u not in self.contrib_ema else self.contrib_ema[u] + 0.01 * (c - self.contrib_ema[u])
                    self.fp["structure"] += 4 * (len(xb) + sum(len(b) for b in blocks.values())) + 4
                else:                                                    # base only; last block power in the normaliser
                    self.base += (self.mu * res / (float(xb @ xb) + self._bpow + 1e-6)) * xb
                    self.fp["structure"] += 4 * len(xb) + 4
                if self.screen_spread:
                    self._screen_spread(res)
                elif self.t % self.screen_every == 0:
                    self._screen(res)
                self.res_prev = res
                self.res2 = res * res if self.res2 is None else self.res2 + (1 - self.lam) * (res * res - self.res2)
            es, em = y - s, y - m
            self.D = self.lam * self.D + (es * es - em * em) / (self.sig ** 2 + 1e-12)
            self.fp["control"] += 7
            if self.t % self.every == 0:
                z = self.eta * self.D
                self.wS = 1.0 / (1.0 + math.exp(z)) if z < 700 else 0.0
                self.fp["control"] += 4
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
        if self.gap_hold and not y_ok and self.last_obs is not None:
            self.M.update(self.last_obs, m, learn=False)             # hold: history gets the last observed value
        else:
            self.M.update(y if y_ok else None, m, learn=mem_learn)
        if y_ok:
            self.last_obs = float(y)
            if self.out_contract:                                    # envelope of the observed targets (past only)
                if self.env_hi is None:
                    self.env_hi = self.env_lo = self.env_m = float(y)
                self.env_n += 1; r_ = self.out_rho
                self.env_m += max(r_, 1.0 / self.env_n) * (y - self.env_m)
                self.env_hi = max(float(y), self.env_hi - r_ * (self.env_hi - self.env_m))
                self.env_lo = min(float(y), self.env_lo - r_ * (self.env_lo - self.env_m))
                self.fp["control"] += 10
        if self.self_input and y_ok:
            self.ylast = float(y)
        self.r = np.array(POLES) * self.r + (1 - np.array(POLES)) * u_
        self.fp["structure"] += 3 * len(POLES)
        if self.t % self.decide_every == 0 and self.t > 0:
            self._decide()
        self.t += 1
        return f

    def _peak_stats(self, ex, rr):
        i = ex.add_key[1]; a = self._a()[i]
        u = self.H[1:self.L + 1, i] - a * self.H[2:self.L + 2, i]       # prewhitened lags 1..L
        pr = rr - a * getattr(ex, "rprev", 0.0); ex.rprev = rr
        if getattr(ex, "cxy", None) is None:
            prev = getattr(ex.hyp, "peak_stats", None) if self.peak_persist else None
            if prev is not None:
                ex.cxy, ex.cxx = prev
            else:
                ex.cxy = np.zeros(self.L); ex.cxx = np.full(self.L, 1e-9)
            if self.peak_persist:
                ex.hyp.peak_stats = (ex.cxy, ex.cxx)                    # same arrays: updated in place
        if self.peak_split:
            msk = (np.arange(self.L) + ex.k) % 2 == 0
            ex.cxy[msk] += pr * u[msk]; ex.cxx[msk] += u[msk] * u[msk]
            self.fp["experiments"] += 3 * self.L + 4
        else:
            ex.cxy += pr * u; ex.cxx += u * u
            self.fp["experiments"] += 6 * self.L
        if ex.k == self.peak_until:
            k = int(np.argmax(ex.cxy ** 2 / ex.cxx)) + 1
            if k > 1:                                                   # lag 1 is already its own band
                ex.kstar = k
                n = len(ex.w)                                           # insert the peak before the current-value term
                w = np.insert(ex.w, n - 1, 0.0)
                P = np.insert(np.insert(ex.P, n - 1, 0.0, axis=0), n - 1, 0.0, axis=1); P[n - 1, n - 1] = self.rls_p0
                ex.w, ex.P = w, P

    # ---------------- screening
    def _screen(self, res):
        w = self.screen_w
        x, x1, ra = self.H[0], self.H[1], 1e-3 * self.screen_every   # AR(1) of each input, updated on screen steps only
        self.a_c0 += ra * (x * x - self.a_c0); self.a_c1 += ra * (x * x1 - self.a_c1)
        a = self._a()
        pres = res - a * self.res_prev
        # prewhitened band means from the running sums: sum_k (x_{t-k} - a x_{t-k-1}) over the band
        ub = np.empty_like(self.bs)
        for b, (lo, hi) in enumerate(BANDS):
            ub[b] = (self.bs[b] - a * (self.bs[b] - self.H[lo] + self.H[hi + 1])) / (hi - lo + 1)
        if self.screen_skip_active:
            act = {u[1] for u in self.active if u[0] == "in"}
            idx = np.array([i for i in range(self.d) if i not in act], dtype=int)
        else:
            idx = np.arange(self.d)
        self.sc_xy[:, idx] += w * (pres[None, idx] * ub[:, idx] - self.sc_xy[:, idx])
        self.sc_xx[:, idx] += w * (ub[:, idx] * ub[:, idx] - self.sc_xx[:, idx])
        self.sc_yy[idx] += w * (pres[idx] * pres[idx] - self.sc_yy[idx])
        self.sr_xy += w * (res * self.r - self.sr_xy); self.sr_xx += w * (self.r * self.r - self.sr_xx)
        self.sr_yy += w * (res * res - self.sr_yy)
        self.fp["screening"] += (11 * len(BANDS) + 5) * len(idx) + 6 * self.d + 12 * len(POLES)
        if self.screen_raw:                                          # raw band means vs the (unfiltered) residual
            rb = self.bs[:, idx] / np.array([hi - lo + 1 for lo, hi in BANDS])[:, None]
            self.rw_xy[:, idx] += w * (res * rb - self.rw_xy[:, idx]); self.rw_xx[:, idx] += w * (rb * rb - self.rw_xx[:, idx])
            self.fp["screening"] += 7 * len(BANDS) * len(idx)
        if self.track_groups:
            gw = 1e-3 * self.screen_every
            self.g_m += gw * (x - self.g_m); xc = x - self.g_m
            self.g_c += gw * (np.outer(xc, xc) - self.g_c)
            self.fp["screening"] += 3 * self.d * (self.d + 1) // 2 + 2 * self.d
        if self.splits:                                              # Haar detail of each splittable active segment
            for key in self.split_keys():
                i, sg = key[1], key[2:]
                l_, r_ = halves(sg); dv = self._mean(i, l_) - self._mean(i, r_)
                st = self.sp.setdefault(key, [0.0, 1e-3, 1.0])
                st[0] += w * (res * dv - st[0]); st[1] += w * (dv * dv - st[1]); st[2] += w * (res * res - st[2])
                self.fp["screening"] += 14

    def _screen_spread(self, res):
        w, se, t = self.screen_w, self.screen_every, self.t
        act = {u[1] for u in self.active if u[0] == "in"} if self.screen_skip_active else set()
        due = [i for i in range(self.d) if (t + i) % se == 0]
        x, x1, ra = self.H[0], self.H[1], 1e-3 * se
        for i in due:                                               # AR(1) of the input and its unit statistics
            self.a_c0[i] += ra * (x[i] * x[i] - self.a_c0[i]); self.a_c1[i] += ra * (x[i] * x1[i] - self.a_c1[i])
            self.fp["screening"] += 6
            if i in act:
                continue
            a = float(self._a()[i]); pres = res - a * self.res_prev
            for b, (lo, hi) in enumerate(BANDS):
                ub = (self.bs[b, i] - a * (self.bs[b, i] - self.H[lo, i] + self.H[hi + 1, i])) / (hi - lo + 1)
                self.sc_xy[b, i] += w * (pres * ub - self.sc_xy[b, i]); self.sc_xx[b, i] += w * (ub * ub - self.sc_xx[b, i])
                if self.screen_raw:
                    rb = self.bs[b, i] / (hi - lo + 1)
                    self.rw_xy[b, i] += w * (res * rb - self.rw_xy[b, i]); self.rw_xx[b, i] += w * (rb * rb - self.rw_xx[b, i])
            self.sc_yy[i] += w * (pres * pres - self.sc_yy[i])
            self.fp["screening"] += 11 * len(BANDS) + 5 + (7 * len(BANDS) if self.screen_raw else 0)
        if t % se == self.d % se:                                   # residual latent unit
            self.sr_xy += w * (res * self.r - self.sr_xy); self.sr_xx += w * (self.r * self.r - self.sr_xx)
            self.sr_yy += w * (res * res - self.sr_yy); self.fp["screening"] += 12 * len(POLES)
        if self.track_groups and t % se == (self.d + 1) % se:
            gw = 1e-3 * se
            self.g_m += gw * (x - self.g_m); xc = x - self.g_m
            self.g_c += gw * (np.outer(xc, xc) - self.g_c)
            self.fp["screening"] += 3 * self.d * (self.d + 1) // 2 + 2 * self.d
        if self.splits:
            for j, key in enumerate(self.split_keys()):
                if (t + j) % se:
                    continue
                i, sg = key[1], key[2:]
                l_, r_ = halves(sg); dv = self._mean(i, l_) - self._mean(i, r_)
                st = self.sp.setdefault(key, [0.0, 1e-3, 1.0])
                st[0] += w * (res * dv - st[0]); st[1] += w * (dv * dv - st[1]); st[2] += w * (res * res - st[2])
                self.fp["screening"] += 14

    def equivalents(self, unit, thr=0.95):
        """inputs whose causal correlation with the input of `unit` is >= thr (reported with the structure)"""
        if unit[0] != "in" or not self.track_groups:
            return {unit[1]} if unit[0] == "in" else set()
        i = unit[1]; sd = np.sqrt(np.maximum(np.diag(self.g_c), 1e-12))
        r = np.abs(self.g_c[i]) / (sd[i] * sd)
        return {int(j) for j in np.flatnonzero(r >= thr)}

    def split_keys(self):
        out = []
        for u, st in self.active.items():
            if u[0] == "in":
                out += [("split", u[1]) + sg for sg in st["segs"] if sg[1] > sg[0]]
        return out

    def screen_stat(self, key):
        k = self.screen_w / (2 - self.screen_w)
        if key[0] == "split":
            st = self.sp.get(key)
            return 0.0 if st is None else st[0] ** 2 / (st[1] * st[2] + 1e-12) / k
        if key[0] == "in":
            i = key[1]
            c2 = self.sc_xy[:, i] ** 2 / (self.sc_xx[:, i] * self.sc_yy[i] + 1e-12)
            if self.screen_raw:
                c2r = self.rw_xy[:, i] ** 2 / (self.rw_xx[:, i] * self.sr_yy + 1e-12)
                return max(float(c2.sum()), float(c2r.sum())) / k
        else:
            c2 = self.sr_xy ** 2 / (self.sr_xx * self.sr_yy + 1e-12)
        return float(c2.sum()) / k

    # ---------------- lifecycle
    @staticmethod
    def unit_of(key):
        return ("in", key[1]) if key[0] == "split" else key

    def _open(self, kind, add_key, rem_key):
        hkey = ("out", rem_key) if kind == "rem" else ("in", add_key)
        ex = self.engine.open(kind, add_key, rem_key, hkey, self.eps[kind], self.t)
        if add_key:
            n_ = len(self.cfeat(add_key)); ex.w = np.zeros(n_); ex.P = self.rls_p0 * np.eye(n_)
            ex.wc = 0.0 if (self.paired and kind in ("add", "swap") and add_key[0] == "in") else None
            ex.Pc = self.rls_p0
            st_ = getattr(ex.hyp, "chal_state", None) if (self.chal_persist and kind in ("add", "swap")) else None
            if st_ is not None:                                      # resume: short re-warm-up, peak already chosen
                ex.w, ex.P = st_[0].copy(), st_[1].copy()
                if st_[2]:
                    ex.kstar = st_[2]
                ex.k = self.chal_warm - 50
            if kind == "split":                                      # start from the parent's weight on both halves
                st = self.active[self.unit_of(add_key)]
                ex.w[:] = float(st["w"][st["segs"].index(add_key[2:])])
        for k in (add_key, rem_key):
            if k:
                self.last_tested[k] = self.t

    def _decide(self):
        changed = set()
        for decision, ex, le in self.engine.review():
            if decision == "accepted":
                self._accept(ex, le)
                changed |= {self.unit_of(k) for k in (ex.add_key, ex.rem_key) if k}
            else:
                self.events.append((self.t, "closed", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.n))
                if self.chal_persist and ex.kind in ("add", "swap") and ex.add_key[0] == "in":
                    ex.hyp.chal_state = (ex.w.copy(), ex.P.copy(), getattr(ex, "kstar", None))
        if changed:   # experiments about units that just changed no longer describe the live model
            keep = []
            for ex in self.engine.slots:
                if {self.unit_of(k) for k in (ex.add_key, ex.rem_key) if k} & changed:
                    self.events.append((self.t, "superseded", ex.kind, ex.add_key, ex.rem_key, None, ex.n))
                else:
                    keep.append(ex)
            self.engine.slots = keep
            self._retrack()
            self.sp = {k: v for k, v in self.sp.items() if k in set(self.split_keys())}
        self._fill()

    def _accept(self, ex, le):
        if ex.kind == "split":
            u = self.unit_of(ex.add_key); st = self.active[u]; sg = ex.add_key[2:]
            j = st["segs"].index(sg); l_, r_ = halves(sg)
            st["segs"] = st["segs"][:j] + [l_, r_] + st["segs"][j + 1:]
            st["w"] = np.concatenate([st["w"][:j], ex.w, st["w"][j + 1:]])
            merged = {}                                              # a half equal to the peak segment: one weight
            for sg_, w_ in zip(st["segs"], st["w"]):
                merged[sg_] = merged.get(sg_, 0.0) + float(w_)
            st["segs"], st["w"] = list(merged), np.array(list(merged.values()))
        else:
            if ex.rem_key and ex.rem_key in self.active:
                del self.active[ex.rem_key]; self.contrib_ema.pop(ex.rem_key, None)
            if ex.add_key:
                if ex.add_key[0] == "in":
                    segs = list(BANDS) + ([(ex.kstar, ex.kstar)] if getattr(ex, "kstar", None) else [])
                    self.active[ex.add_key] = {"segs": segs, "w": ex.w[:-1].copy()}
                    self.base[1 + ex.add_key[1]] += float(ex.w[-1])
                else:
                    self.active[ex.add_key] = {"segs": None, "w": ex.w.copy()}
        self.engine.consume(ex)
        self._retrack()
        self.events.append((self.t, "accepted", ex.kind, ex.add_key, ex.rem_key, round(le, 2), ex.hyp.n))

    def _fill(self):
        busy = {self.unit_of(k) for k in self.engine.busy_keys()}
        while self.engine.free_slots() > 0:
            due = [a for a in self.active if a not in busy and self.t - self.last_rem.get(a, -10 ** 9) >= self.rem_period
                   and self.t - self.last_tested.get(a, -10 ** 9) >= self.n_min]
            if due:
                a = due[0]; self.last_rem[a] = self.t; self._open("rem", None, a); busy.add(a); continue
            if self.stagger and any(ex.add_key and getattr(ex, "k", 0) <= self.chal_warm for ex in self.engine.slots):
                break                                                # one warm-up at a time
            cands = []
            pool = [u for u in self.units if u not in self.active and u not in busy
                    and self.t - self.last_tested.get(u, -10 ** 9) >= self.cooldown]
            if pool:
                c = max(pool, key=self.screen_stat)
                if self.screen_stat(c) >= self.screen_q:
                    cands.append((self.screen_stat(c) / self.screen_q, "unit", c))
            if self.splits:
                sp = [k for k in self.split_keys() if self.unit_of(k) not in busy
                      and self.t - self.last_tested.get(k, -10 ** 9) >= self.cooldown]
                if sp:
                    c = max(sp, key=self.screen_stat)
                    if self.screen_stat(c) >= self.split_q:
                        cands.append((self.screen_stat(c) / self.split_q, "split", c))
            if not cands:
                break
            _, typ, c = max(cands)
            if typ == "split":
                self._open("split", c, None)
            elif len(self.active) < self.M_max:
                self._open("add", c, None)
            else:
                a = min((k for k in self.active if k not in busy), key=lambda k: self.contrib_ema.get(k, float("inf")), default=None)
                if a is None:
                    break
                self._open("swap", c, a); busy.add(a)
            busy.add(self.unit_of(c))
            self.fp["control"] += (len(self.units) + len(self.sp)) / self.decide_every

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
