#!/usr/bin/env python3
"""
lebre_v04.py — LEBRE v0.4 candidate (EXPERIMENTAL, NON-CANONICAL). Evolution of v0.3.2 (lebre_v032.py).

Every change reuses existing machinery or removes a special case; each one can be switched off for ablation.

  C1 anchor     persistence atom phi = y_{t-1} in the target's own units; tested / evicted by the same
                lifecycle (mixture martingale in, CUSUM out). Recovers persistence and ARX as special cases.
  C2 ipnlms     learning = improved proportionate NLMS (Benesty & Gay 2002; Duttweiler 2000) in
                power-normalised coordinates: theta_j += mu e (g_j/P_j) phi_j / (sum_k g_k phi_k^2 / P_k + delta).
                Gains refreshed every `gain_every` steps (slowly varying quantities).
  C3 prune_base the current inputs are atoms ("lag", i, 0) that start ACTIVE and live under the same lifecycle
                (CUSUM + rent, re-promotion by test). Only the bias is always on. Removes the dense-base
                special case; cost becomes O(|A|) instead of O(d).
  C4 mature     atoms active for >= T_mature steps with an empty CUSUM are MATURE and are monitored every
                `mature_every` steps (rent scaled -> stream-time rate unchanged; ARL guarantee unaffected).
  C5 clip       standardised inputs are clipped to +-clip_c (environment standardises inputs, cf. P6).
  C6 intervals  online quantile tracking of |e| (Angelopoulos, Candes & Tibshirani 2023; Gibbs & Candes 2021):
                q <- q + eta (1{|e_t| > q} - alpha_cov), eta = gamma * sigma_hat. Output interval y_hat +- q.

Also: exact additive explanation of each prediction (explain_prediction), change alarms from CUSUM evictions.
Unchanged from v0.3.2: self-normalised promotion test, CUSUM eviction with MDL rent, excitation gate, latent
innovations pathway with drive atom, stream-time evidence, warm-up estimators.
"""

import heapq
import math
from typing import Dict, List, Tuple, Any

import numpy as np


class LebreV04:
    def __init__(
        self,
        d: int = 5,
        L: int = 32,
        mu: float = 0.1,
        n_sigma: int = 200,
        alpha_add: float = 0.05,
        arl_target: float = 6000.0,
        T_idle: float = 500.0,
        rho: float = 1.0,
        poles: Tuple[float, ...] = (0.0, 0.5, 0.8, 0.95),
        M_max: int = 4,                   # structural (non-base) atom budget
        B_probe: int = 2,
        H_hot: int = 4,
        screen_w: float = 0.2,
        decide_every: int = 10,
        test_every: int = 2,
        T_max: int = 200,
        evidence_every: int = 2,
        latent_test_every: int = 2,
        pe_fraction: float = 0.1,
        n_power: int = 1000,
        # ---- v0.4 switches
        anchor: bool = False,            # C1 kept only for ablation: redundant with C2, hurts explainability
        ipnlms: bool = True,
        prune_base: bool = False,        # C3 kept only for ablation (see DEV report)
        mature: bool = True,
        clip: bool = True,
        intervals: bool = True,
        gain_every: int = 50,
        ip_alpha: float = 0.0,
        T_mature: int = 300,
        mature_every: int = 16,
        clip_c: float = 8.0,
        alpha_cov: float = 0.1,
        gamma_q: float = 0.1,
    ):
        self.d, self.L = d, L
        self.mu = mu
        self.beta_s = 1.0 / n_sigma
        self.rho = rho
        self.poles = poles
        self.M_max = M_max
        self.B_probe = B_probe
        self.H_hot = H_hot
        self.screen_w = screen_w
        self.decide_every = decide_every
        self.test_every = test_every
        self.T_max = T_max
        self.evidence_every = evidence_every
        self.latent_test_every = latent_test_every
        self.pe_fraction = pe_fraction
        self.beta_p = 1.0 / n_power
        self.use_anchor, self.use_ip, self.use_prune = anchor, ipnlms, prune_base
        self.use_mature, self.use_clip, self.use_int = mature, clip, intervals
        self.gain_every, self.ip_alpha = gain_every, ip_alpha
        self.T_mature, self.mature_every = T_mature, mature_every
        self.clip_c, self.alpha_cov, self.gamma_q = clip_c, alpha_cov, gamma_q

        k0 = 0 if prune_base else 1
        self.lag_cands = [(i, k) for i in range(d) for k in range(k0, L + 1)]
        self.p_dict = len(self.lag_cands) + len(poles) + d + (1 if anchor else 0)
        self.thr_add = math.log(self.p_dict / alpha_add)
        self.thr_rem = math.log(arl_target)
        self.rent = self.thr_rem / T_idle

        self.hist = np.zeros((L + 1, d))
        self.y_prev = 0.0
        self.y_pow = None
        self.t = 0
        self.theta_bias = 0.0
        self.P_bias, self.a_bias = 1.0, 1.0
        # dense base only when prune_base is off (v0.3.2 behaviour)
        self.theta_b = np.zeros(d)
        self.P_b = np.ones(d)
        self.a_b = np.ones(d)
        self.active: List[Dict[str, Any]] = []
        if prune_base:
            for i in range(d):
                self.active.append(self._new_atom(("lag", i, 0), 0.0, 0.0, 1.0))
        self.s = {p: 0.0 for p in poles}
        self.q: Dict[int, float] = {}
        self.sigma2 = None
        self.sigma2_peak = 0.0
        self.screen = {c: 0.0 for c in self.lag_cands}
        self.qptr = 0
        self.hot: Dict[Any, Dict[str, float]] = {}
        self.p_in = 1.0
        for p in poles:
            self.hot[("res", p)] = self._fresh(("res", p))
        if anchor:
            self.hot[("anc",)] = self._fresh(("anc",))
        self.qhat = None
        self.cover_hits = 0
        self.cover_n = 0

        self.fp = {"live": 0.0, "latent_bank": 0.0, "eviction_cusum": 0.0, "search_screen": 0.0,
                   "test_hot": 0.0, "decision": 0.0, "gains": 0.0, "observability": 0.0}
        self.transcendental = 0
        self.n_provisional = 0
        self.n_futility = 0
        self.n_rank_compares = 0
        self.n_warm = 20
        self.n_clipped = 0
        self.events: List[Tuple[int, str, str, float]] = []
        self.alarms: List[Tuple[int, str]] = []

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _new_atom(key, theta, E, inv_vref, t_on=0):
        return {"key": key, "theta": theta, "R": 0.0, "E": E, "t_on": t_on, "inv_vref": inv_vref,
                "P": 1.0, "a": 1.0}

    def _fresh(self, key=None):
        s2 = self.sigma2 if self.sigma2 else 1.0
        if key is not None and key[0] == "res":
            m_phi = (1.0 - key[1]) / (1.0 + key[1])
        elif key is not None and key[0] == "anc":
            m_phi = max(self.y_pow if self.y_pow else 1.0, 1e-12)
        else:
            m_phi = max(float(np.mean(self.P_b)), 1e-12)     # raw input power (standardised inputs -> ~1)
        return {"S": 0.0, "Q": 0.0, "n": 0, "tau": self.rho / (s2 * m_phi), "m_phi": m_phi}

    def _x_lag(self, i: int, k: int) -> float:
        return float(self.hist[(self.t - k) % (self.L + 1), i])

    def _phi(self, key) -> float:
        if key[0] == "lag":
            return self._x_lag(key[1], key[2])
        if key[0] == "res":
            return self.s[key[1]]
        if key[0] == "anc":
            return self.y_prev
        return self.q[key[1]]

    @staticmethod
    def _is_base(a):
        return a["key"][0] == "lag" and a["key"][2] == 0

    def n_struct(self):
        return sum(1 for a in self.active if not self._is_base(a))

    def latent_atom(self):
        return next((a for a in self.active if a["key"][0] == "res"), None)

    def drive_atom(self):
        return next((a for a in self.active if a["key"][0] == "drv"), None)

    def label(self, key) -> str:
        if key[0] == "lag":
            return f"x{key[1]} (atual)" if key[2] == 0 else f"x{key[1]} atrasado {key[2]} passos"
        if key[0] == "anc":
            return "persistência: y(t-1)"
        if key[0] == "res":
            return f"estado latente (tau~{1.0 / (1.0 - key[1]):.0f} passos, polo {key[1]:.2f})"
        lat = self.latent_atom()
        p = lat["key"][1] if lat else float("nan")
        return f"x{key[1]} alimenta o estado latente (polo {p:.2f})"

    def is_active(self, key) -> bool:
        return any(a["key"] == key for a in self.active)

    # ------------------------------------------------------------------ gains (C2)
    def _refresh_gains(self, phis, x):
        """Power normalisation + proportionate gains (IPNLMS), refreshed every gain_every steps."""
        if not self.use_ip:
            return
        fp = self.fp
        b = min(0.5, self.gain_every / 200.0)          # subsampled EMA of phi^2, ~200-step memory in stream time
        for a, ph in zip(self.active, phis):
            a["P"] += b * (ph * ph - a["P"]); fp["gains"] += 4
        dense = not self.use_prune
        if dense:
            self.P_b += b * (x * x - self.P_b); fp["gains"] += 4 * self.d
        n = len(self.active) + 1 + (self.d if dense else 0)
        w = [abs(a["theta"]) * math.sqrt(max(a["P"], 1e-12)) for a in self.active]
        wbase = np.abs(self.theta_b) * np.sqrt(np.maximum(self.P_b, 1e-12)) if dense else np.zeros(0)
        wb = abs(self.theta_bias)
        tot = sum(w) + float(wbase.sum()) + wb + 1e-12; fp["gains"] += 3 * n + 1
        c0, c1 = (1 - self.ip_alpha) / (2 * n), (1 + self.ip_alpha) / (2 * tot)
        for a, wi in zip(self.active, w):
            a["a"] = (c0 + c1 * wi) * n / max(a["P"], 1e-12); fp["gains"] += 4
        if dense:
            self.a_b = (c0 + c1 * wbase) * n / np.maximum(self.P_b, 1e-12); fp["gains"] += 4 * self.d
        self.a_bias = (c0 + c1 * wb) * n; fp["gains"] += 3

    # ------------------------------------------------------------------ step
    def step(self, x: np.ndarray, y: float) -> float:
        fp = self.fp
        if self.use_clip:
            if np.any(np.abs(x) > self.clip_c):
                self.n_clipped += 1
                x = np.clip(x, -self.clip_c, self.clip_c)
        self.hist[self.t % (self.L + 1)] = x                       # lag 0 = current input

        # 1. prediction (bias + dense base if prune_base off + atoms)
        y_hat = self.theta_bias; fp["live"] += 1
        if not self.use_prune:
            y_hat += float(self.theta_b @ x); fp["live"] += 2 * self.d
        phis, contribs = [], []
        for a in self.active:
            ph = self._phi(a["key"])
            c = a["theta"] * ph
            phis.append(ph); contribs.append(c)
            y_hat += c; fp["live"] += 2
        e = y - y_hat; fp["live"] += 1

        # 2. learning (C2: per-coordinate gains; without C2 this is exactly the v0.3.2 NLMS)
        if self.t % self.gain_every == 0:
            self._refresh_gains(phis, x)
        bias_pred = self.theta_bias
        den = self.a_bias; ph2s, qs = [], []
        den_x = 0.0
        if not self.use_prune:
            if self.use_ip:
                qb = self.a_b * x; den_x = float(qb @ x); fp["live"] += 3 * self.d
            else:
                qb = x; den_x = float(x @ x); fp["live"] += 2 * self.d
            den += den_x
        for a, ph in zip(self.active, phis):
            ph2 = ph * ph
            qj = a["a"] * ph if self.use_ip else ph
            qs.append(qj); ph2s.append(ph2)
            den += qj * ph; fp["live"] += 3 if self.use_ip else 2
            if a["key"][0] == "lag":
                den_x += qj * ph
        g = self.mu * e / (1e-6 + den); fp["live"] += 3
        self._last = (y_hat, bias_pred, [(a["key"], c) for a, c in zip(self.active, contribs)],
                      (float(self.theta_b @ x) if not self.use_prune else 0.0))   # frozen at prediction time
        self.theta_bias += g * self.a_bias; fp["live"] += 2
        if not self.use_prune:
            self.theta_b += g * qb; fp["live"] += 2 * self.d
        for a, qj in zip(self.active, qs):
            a["theta"] += g * qj; fp["live"] += 2

        # 3. noise scale
        if self.sigma2 is None:
            self.sigma2 = e * e
        b_s = max(1.0 / (self.t + 1), self.beta_s)
        self.sigma2 += b_s * (e * e - self.sigma2); fp["live"] += 4
        if self.sigma2 > self.sigma2_peak:
            self.sigma2_peak = self.sigma2
        if self.sigma2 < 1e-10 * self.sigma2_peak:
            self.sigma2 = 1e-10 * self.sigma2_peak
        if self.sigma2 <= 0.0:
            self.sigma2 = 1e-300
        inv2s = 0.5 / self.sigma2
        two_e = 2.0 * e; fp["eviction_cusum"] += 2

        # C6: interval calibration (quantile tracking of |e|), scale-equivariant step
        sig = math.sqrt(self.sigma2); fp["latent_bank"] += 1          # shared by latent pathway and intervals
        if self.use_int:
            if self.qhat is None:
                self.qhat = 1.645 * sig
            miss = 1.0 if abs(e) > self.qhat else 0.0
            if self.t >= self.n_warm:
                self.cover_n += 1; self.cover_hits += int(miss == 0.0)
            if self.t % 2 == 0:                                            # step x2 keeps the stream-time rate
                self.qhat = max(0.0, self.qhat + 2.0 * self.gamma_q * sig * (miss - self.alpha_cov)); fp["observability"] += 3

        # excitation gate: power of the inputs actually read this step (active x-atoms + screening probes)
        probes = []
        for _ in range(self.B_probe):
            c = self.lag_cands[self.qptr]
            self.qptr = (self.qptr + 1) % len(self.lag_cands)
            probes.append((c, self._x_lag(*c)))
        p_x = den_x if (not self.use_prune or den_x > 0) else sum(v * v for _, v in probes)
        excited = p_x >= self.pe_fraction * self.p_in
        b_p = max(1.0 / (self.t + 1), self.beta_p)
        self.p_in += b_p * (p_x - self.p_in); fp["live"] += 3
        if self.use_anchor and (self.y_pow is None or self.t % 10 == 0):
            self.y_pow = y * y if self.y_pow is None else self.y_pow + min(1.0, 10 * b_p) * (y * y - self.y_pow); fp["live"] += 4

        # 4. eviction evidence (C4: mature atoms monitored every mature_every steps)
        if excited and self.t >= self.n_warm:
            for a, c, ph2 in zip(self.active, contribs, ph2s):
                every = self.evidence_every
                if self.use_mature and a["R"] < 1.0 and self.t - a["t_on"] >= self.T_mature:
                    every = self.mature_every
                if self.t % every:
                    continue
                llr_keep = c * (two_e + c) * inv2s; fp["eviction_cusum"] += 3
                rent = self.rent * every * min(1.0, ph2 * a["inv_vref"]); fp["eviction_cusum"] += 3
                a["R"] = max(0.0, a["R"] - llr_keep + rent); fp["eviction_cusum"] += 2
                a["E"] += every * llr_keep; fp["eviction_cusum"] += 1   # every*llr folded at report time (int scale)

        # 5. provisional tests
        if self.t == self.n_warm:
            for k in list(self.hot):
                self.hot[k] = self._fresh(k)
        if excited and self.t >= self.n_warm and self.t % self.test_every == 0:
            lat_on = self.latent_atom() is not None
            lat_tick = self.t % self.latent_test_every == 0
            for key, st in self.hot.items():
                if self.is_active(key) or (key[0] == "res" and lat_on):
                    continue
                if key[0] in ("res", "drv") and not lat_tick:
                    continue
                z = e * self._phi(key)
                st["S"] += z; st["Q"] += z * z; st["n"] += 1; fp["test_hot"] += 4

        # 6. screening (uses the probe values read above)
        for c, v in probes:
            z = e * v; fp["search_screen"] += 1
            self.screen[c] += self.screen_w * (z - self.screen[c]); fp["search_screen"] += 3

        # 7. latent pathway states
        u = e
        lat = self.latent_atom()
        for a, c in zip(self.active, contribs):
            if a["key"][0] in ("res", "drv"):
                u += c; fp["latent_bank"] += 1
        u = u / sig; fp["latent_bank"] += 1
        for p in self.poles:
            if p == 0.0:
                self.s[p] = u
            else:
                self.s[p] = p * self.s[p] + (1.0 - p) * u; fp["latent_bank"] += 3
        if lat is not None and self.q:
            p = lat["key"][1]
            for i in self.q:
                self.q[i] = p * self.q[i] + (1.0 - p) * float(x[i]); fp["latent_bank"] += 3

        self.y_prev = float(y)
        # 8. decisions
        if self.t >= self.n_warm and self.t % self.decide_every == 0:
            self._decide()
        self.t += 1
        return y_hat

    # ------------------------------------------------------------------ lifecycle
    def _log_mixture(self, st) -> float:
        # exact necessary condition: tau S^2/(2(1+tau Q)) <= S^2/(2Q), so S^2 < 2 thr Q cannot cross
        S2 = st["S"] * st["S"]; self.fp["decision"] += 2
        if S2 < 2.0 * self.thr_add * st["Q"]:
            return -1.0
        B = 1.0 + st["tau"] * st["Q"]
        quad = st["tau"] * S2 / (2.0 * B); self.fp["decision"] += 5
        if quad < self.thr_add:
            return quad - self.thr_add - 1.0
        self.fp["decision"] += 4; self.transcendental += 1
        return quad - 0.5 * math.log(B)

    def _evict(self, a, why):
        self.active.remove(a)
        self.events.append((self.t, why, self.label(a["key"]), a["R"]))
        self.alarms.append((self.t, self.label(a["key"])))
        if a["key"][0] == "res":
            self.hot[a["key"]] = self._fresh(a["key"])
            drv = self.drive_atom()
            if drv is not None:
                self.active.remove(drv)
                self.events.append((self.t, "ACTIVE->EVICTED(coupled)",
                                    f"x{drv['key'][1]} alimenta o estado latente (polo {a['key'][1]:.2f})", drv["R"]))
            for k in [k for k in self.hot if k[0] == "drv"]:
                del self.hot[k]
            self.q = {}
        elif a["key"][0] == "anc":
            self.hot[a["key"]] = self._fresh(a["key"])

    def _open_drive_tests(self, p: float):
        for i in range(self.d):
            v = 0.0
            for k in range(self.L, -1, -1):              # includes the current input (lag 0)
                v = p * v + (1.0 - p) * self._x_lag(i, k)
            self.q[i] = v
            self.fp["latent_bank"] += 3 * (self.L + 1)
            self.hot[("drv", i)] = self._fresh(("drv", i))

    def _decide(self):
        worst = max(self.active, key=lambda a: a["R"], default=None)
        if worst is not None and worst["R"] > self.thr_rem:
            self._evict(worst, "ACTIVE->EVICTED")

        best, best_lm = None, -1.0
        lat_on = self.latent_atom() is not None
        for key, st in list(self.hot.items()):
            if self.is_active(key) or st["n"] == 0 or (key[0] == "res" and lat_on):
                continue
            lm = self._log_mixture(st)
            if lm >= self.thr_add and lm > best_lm:
                best, best_lm = key, lm
            elif st["n"] >= self.T_max:
                self.n_futility += 1
                if key[0] in ("res", "anc"):
                    self.hot[key] = self._fresh(key)
                else:
                    del self.hot[key]
                    if key[0] == "drv" and not any(k[0] == "drv" for k in self.hot) and self.drive_atom() is None:
                        self.q = {}
        is_base_cand = best is not None and best[0] == "lag" and best[2] == 0
        if best is not None and not is_base_cand and self.n_struct() >= self.M_max:
            pool = [a for a in self.active if not self._is_base(a) and a["R"] >= 0.5 * self.thr_rem
                    and not (best[0] == "drv" and a["key"][0] == "res")]
            if pool:
                self._evict(max(pool, key=lambda a: a["R"]), "ACTIVE->EVICTED(replaced)")
            else:
                best = None
        if best is not None and best in self.hot:
            st = self.hot.pop(best)
            V_est = st["Q"] / self.sigma2
            theta0 = st["S"] / (V_est + st["m_phi"] / self.rho); self.fp["decision"] += 4
            inv_vref = st["n"] / V_est if V_est > 0 else 0.0; self.fp["decision"] += 1
            atom = self._new_atom(best, theta0, best_lm, inv_vref, self.t)
            atom["P"] = max(V_est / max(st["n"], 1), 1e-12)
            atom["a"] = 1.0 / atom["P"] if self.use_ip else 1.0
            self.active.append(atom)
            self.events.append((self.t, "PROVISIONAL->ACTIVE", self.label(best), best_lm))
            if best[0] in ("res", "anc", "drv"):
                # hidden-dynamics candidates share one explanatory role: their null hypotheses changed,
                # so their evidence (accumulated under the previous model) restarts
                for k in list(self.hot):
                    if k[0] in ("res", "anc", "drv") and k != best:
                        self.hot[k] = self._fresh(k)
            if best[0] in ("res", "anc"):
                self.hot[best] = self._fresh(best)
                if best[0] == "res":
                    self._open_drive_tests(best[1])
            elif best[0] == "drv":
                for k in [k for k in self.hot if k[0] == "drv"]:
                    del self.hot[k]
                self.q = {best[1]: self.q[best[1]]}

        n_lag_hot = sum(1 for k in self.hot if k[0] == "lag")
        if n_lag_hot < self.H_hot:
            taken = {k[1:] for k in self.hot if k[0] == "lag"} | \
                    {a["key"][1:] for a in self.active if a["key"][0] == "lag"}
            ranked = heapq.nlargest(self.H_hot - n_lag_hot, (c for c in self.lag_cands if c not in taken),
                                    key=lambda c: abs(self.screen[c]))
            self.n_rank_compares += len(self.lag_cands)
            for c in ranked:
                self.hot[("lag",) + c] = self._fresh(("lag",) + c)
                self.screen[c] = 0.0
                self.n_provisional += 1

    # ------------------------------------------------------------------ explanation / observability
    def explain_prediction(self):
        """Exact additive decomposition of the last prediction: sum of contributions == y_hat."""
        y_hat, bias_pred, contribs, base_pred = self._last
        parts = [("viés", bias_pred)]
        if not self.use_prune:
            parts.append(("entradas atuais (base)", base_pred))
        parts += [(self.label(k), c) for k, c in contribs]
        return y_hat, parts

    def interval(self):
        return self.qhat if self.qhat is not None else float("nan")

    def explain(self) -> List[str]:
        out = [f"viés {self.theta_bias:+.3f}"]
        for a in self.active:
            out.append(f"{self.label(a['key'])}: coef {a['theta']:+.3f}, evidencia {a['E']:.1f} nats, "
                       f"CUSUM {a['R']:.1f}/{self.thr_rem:.1f}, ativo desde t={a['t_on']}")
        out.append(f"ruido residual sigma={math.sqrt(self.sigma2):.3f}; intervalo 90% +-{self.interval():.3f}")
        return out

    def memory_bytes(self) -> int:
        return (4 * (self.L + 1) * self.d + 8 + 28 * len(self.active) + 4 * len(self.poles)
                + 4 * len(self.q) + 2 * len(self.lag_cands) + 12 * len(self.hot) + 24)
