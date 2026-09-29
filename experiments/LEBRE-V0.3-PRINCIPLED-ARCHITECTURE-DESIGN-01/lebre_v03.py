#!/usr/bin/env python3
"""
lebre_v03.py — LEBRE v0.3 research candidate: principled evolution of the LEBRE v0.2 lifecycle.
EXPERIMENTAL, NON-CANONICAL, working prototype (DEV). Not frozen. Not validated.

Keeps the LEBRE identity:
  * always-on memoryless base pathway;
  * sparse discrete-delay pathway (lag atoms x_{t-k,i});
  * one recurrent latent-state pathway;
  * candidate lifecycle DORMANT -> PROVISIONAL -> ACTIVE -> EVICTED;
  * rotating sparse search frontier and an explicit resource budget.

Replaces heuristic internals with principled ones:
  * latent pathway = innovations-form (steady-state Kalman) predictor of a first-order hidden state:
        s_t = p s_{t-1} + (1-p) u_{t-1}         (innovation part, u = residual w/o latent atoms)
        q_t = p q_{t-1} + (1-p) x_{t-1,i}       (drive part: which input feeds the hidden state)
    with p chosen from a small bank of timescales (tau = 1, 2, 5, 20 steps);
  * PROVISIONAL -> ACTIVE: Gaussian-mixture test martingale on the residual score; threshold
    log(p_dict / alpha) (Ville's inequality + Bonferroni over the dictionary);
  * ACTIVE -> EVICTED: Page CUSUM on the per-step Gaussian log-likelihood ratio "without vs with"
    the atom, plus an excitation-weighted parsimony rent r = h / T_idle (MDL / resource price);
    threshold h = log(ARL_target) (Lorden: ARL to false eviction >= e^h, before rent);
  * every statistic evolves in stream time; decision cadence only adds a bounded wait.
"""

import math
from typing import Dict, List, Tuple, Any

import numpy as np


class LebreV03:
    def __init__(
        self,
        d: int = 5,
        L: int = 32,
        mu: float = 0.1,                 # NLMS step -> misadjustment ~ mu/(2-mu) ~ 5.3%
        n_sigma: int = 200,              # stream-time memory of the noise-scale estimate
        alpha_add: float = 0.05,         # false-promotion level per test episode (family-wise)
        arl_target: float = 6000.0,      # CUSUM: mean steps to a false eviction >= arl_target
        T_idle: float = 500.0,           # an excited-but-useless atom is shed after ~T_idle steps
        rho: float = 0.25,               # prior variance of a new atom's coefficient
        poles: Tuple[float, ...] = (0.0, 0.5, 0.8, 0.95),
        M_max: int = 4,                  # structural atom budget (resource governance)
        B_probe: int = 2,                # screening probes per step
        H_hot: int = 4,                  # lag candidates under formal test
        screen_w: float = 0.2,           # screening EMA weight (chooses WHAT to test only)
        decide_every: int = 10,          # decision cadence (adds <= 9 steps wait)
        test_every: int = 2,             # hot-test sampling cadence (Ville validity unaffected)
        T_max: int = 200,                # futility horizon of a hot test (type-I unaffected)
        evidence_every: int = 2,         # CUSUM cadence; rent scaled so its stream-time rate is fixed
        latent_test_every: int = 2,      # cadence of latent / drive candidate tests
        pe_fraction: float = 0.1,        # persistent-excitation gate: input power vs long-run power
        n_power: int = 1000,             # stream-time memory of long-run input power
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
        self.p_in = 1.0

        self.lag_cands = [(i, k) for i in range(d) for k in range(1, L + 1)]
        self.p_dict = len(self.lag_cands) + len(poles) + d
        self.thr_add = math.log(self.p_dict / alpha_add)
        self.thr_rem = math.log(arl_target)
        self.rent = self.thr_rem / T_idle

        self.hist = np.zeros((L + 1, d))
        self.t = 0
        self.theta_b = np.zeros(d + 1)
        self.active: List[Dict[str, Any]] = []
        self.s = {p: 0.0 for p in poles}
        self.q: Dict[int, float] = {}
        self.sigma2 = 1.0
        self.screen = {c: 0.0 for c in self.lag_cands}
        self.qptr = 0
        self.hot: Dict[Any, Dict[str, float]] = {("res", p): self._fresh() for p in poles}

        self.fp = {"live": 0.0, "latent_bank": 0.0, "eviction_cusum": 0.0,
                   "search_screen": 0.0, "test_hot": 0.0, "decision": 0.0}
        self.transcendental = 0
        self.n_provisional = 0
        self.n_futility = 0
        self.events: List[Tuple[int, str, str, float]] = []

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _fresh():
        return {"S": 0.0, "V": 0.0, "n": 0}

    def _x_lag(self, i: int, k: int) -> float:
        return float(self.hist[(self.t - k) % (self.L + 1), i])

    def _phi(self, key) -> float:
        if key[0] == "lag":
            return self._x_lag(key[1], key[2])
        if key[0] == "res":
            return self.s[key[1]]
        return self.q[key[1]]

    def latent_atom(self):
        return next((a for a in self.active if a["key"][0] == "res"), None)

    def drive_atom(self):
        return next((a for a in self.active if a["key"][0] == "drv"), None)

    def label(self, key) -> str:
        if key[0] == "lag":
            return f"x{key[1]} atrasado {key[2]} passos"
        if key[0] == "res":
            p = key[1]
            return f"estado latente (tau~{1.0 / (1.0 - p):.0f} passos, polo {p:.2f})"
        lat = self.latent_atom()
        p = lat["key"][1] if lat else float("nan")
        return f"x{key[1]} alimenta o estado latente (polo {p:.2f})"

    def is_active(self, key) -> bool:
        return any(a["key"] == key for a in self.active)

    # ------------------------------------------------------------------ step
    def step(self, x: np.ndarray, y: float) -> float:
        fp = self.fp
        xb = np.append(x, 1.0)

        # 1. prediction
        y_hat = float(self.theta_b @ xb); fp["live"] += 2 * (self.d + 1) - 1
        phis, contribs = [], []
        for a in self.active:
            ph = self._phi(a["key"])
            c = a["theta"] * ph
            phis.append(ph); contribs.append(c)
            y_hat += c; fp["live"] += 2
        e = y - y_hat; fp["live"] += 1

        # 2. NLMS on all active atoms
        p_x = float(x @ x); fp["live"] += 2 * self.d - 1
        norm = p_x + 1.0; fp["live"] += 1
        ph2s = []
        for ph in phis:
            ph2 = ph * ph
            ph2s.append(ph2)
            norm += ph2; fp["live"] += 2
        g = self.mu * e / (1e-6 + norm); fp["live"] += 3
        self.theta_b += g * xb; fp["live"] += 2 * (self.d + 1)
        for a, ph in zip(self.active, phis):
            a["theta"] += g * ph; fp["live"] += 2

        # 3. noise scale
        self.sigma2 += self.beta_s * (e * e - self.sigma2); fp["live"] += 4
        inv2s = 0.5 / self.sigma2
        two_e = 2.0 * e; fp["eviction_cusum"] += 2

        # persistent-excitation gate: no evidence is accumulated while inputs are silent
        excited = p_x >= self.pe_fraction * self.p_in; fp["live"] += 1
        self.p_in += self.beta_p * (p_x - self.p_in); fp["live"] += 3

        # 4. eviction evidence: CUSUM on LLR(without vs with) + excitation-weighted rent
        if excited and self.t % self.evidence_every == 0:
            rent_ev = self.rent * self.evidence_every
            for a, c, ph2 in zip(self.active, contribs, ph2s):
                llr_keep = c * (two_e + c) * inv2s; fp["eviction_cusum"] += 3
                rent = rent_ev * min(1.0, ph2 * a["inv_vref"]); fp["eviction_cusum"] += 2
                a["R"] = max(0.0, a["R"] - llr_keep + rent); fp["eviction_cusum"] += 2
                a["E"] += self.evidence_every * llr_keep; fp["eviction_cusum"] += 2

        # 5. formal tests on PROVISIONAL candidates
        if excited and self.t % self.test_every == 0:
            lat_on = self.latent_atom() is not None
            lat_tick = self.t % self.latent_test_every == 0
            for key, st in self.hot.items():
                if self.is_active(key) or (key[0] == "res" and lat_on):
                    continue
                if key[0] != "lag" and not lat_tick:
                    continue
                ph = self._phi(key)
                st["S"] += e * ph; st["V"] += ph * ph; st["n"] += 1; fp["test_hot"] += 4

        # 6. screening of DORMANT lag atoms (rank-based; chooses what to test)
        for _ in range(self.B_probe):
            c = self.lag_cands[self.qptr]
            self.qptr = (self.qptr + 1) % len(self.lag_cands)
            z = e * self._x_lag(*c); fp["search_screen"] += 1
            self.screen[c] += self.screen_w * (z - self.screen[c]); fp["search_screen"] += 3

        # 7. latent pathway states (predictive for t+1)
        u = e
        lat = self.latent_atom()
        for a, c in zip(self.active, contribs):
            if a["key"][0] in ("res", "drv"):
                u += c; fp["latent_bank"] += 1
        for p in self.poles:
            if p == 0.0:
                self.s[p] = u
            else:
                self.s[p] = p * self.s[p] + (1.0 - p) * u; fp["latent_bank"] += 3
        if lat is not None and self.q:
            p = lat["key"][1]
            for i in self.q:
                self.q[i] = p * self.q[i] + (1.0 - p) * float(x[i]); fp["latent_bank"] += 3

        # 8. lifecycle decisions
        if self.t % self.decide_every == 0:
            self._decide()

        self.hist[self.t % (self.L + 1)] = x
        self.t += 1
        return y_hat

    # ------------------------------------------------------------------ lifecycle
    def _log_mixture(self, st) -> float:
        s2 = self.sigma2
        A = s2 + self.rho * st["V"]
        quad = self.rho * st["S"] ** 2 / (2.0 * s2 * A); self.fp["decision"] += 6
        # exact necessary condition: log(s2/A) <= 0, so quad < thr_add implies no crossing
        if quad < self.thr_add:
            return quad - self.thr_add - 1.0          # below threshold; value unused except for ranking
        self.fp["decision"] += 3; self.transcendental += 1
        return 0.5 * math.log(s2 / A) + quad

    def _evict(self, a, why):
        self.active.remove(a)
        self.events.append((self.t, why, self.label(a["key"]), a["R"]))
        if a["key"][0] == "res":
            self.hot[a["key"]] = self._fresh()
            drv = self.drive_atom()
            if drv is not None:                      # drive is meaningless without its latent state
                self.active.remove(drv)
                self.events.append((self.t, "ACTIVE->EVICTED(coupled)", self.label(drv["key"]), drv["R"]))
            for k in [k for k in self.hot if k[0] == "drv"]:
                del self.hot[k]
            self.q = {}

    def _open_drive_tests(self, p: float):
        # initialise drive filters from the ring buffer (one-off cost), then test which input feeds the state
        for i in range(self.d):
            v = 0.0
            for k in range(self.L, 0, -1):
                v = p * v + (1.0 - p) * self._x_lag(i, k)
            self.q[i] = v
            self.fp["latent_bank"] += 3 * self.L
            self.hot[("drv", i)] = self._fresh()

    def _decide(self):
        # (a) eviction: at most one per decision (the most contradicted atom)
        worst = max(self.active, key=lambda a: a["R"], default=None)
        if worst is not None and worst["R"] > self.thr_rem:
            self._evict(worst, "ACTIVE->EVICTED")

        # (b) promotion: best PROVISIONAL candidate whose test martingale crossed log(p/alpha)
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
                if key[0] == "res":
                    self.hot[key] = self._fresh()
                else:
                    del self.hot[key]
                    if key[0] == "drv" and not any(k[0] == "drv" for k in self.hot) and self.drive_atom() is None:
                        self.q = {}
        if best is not None and len(self.active) >= self.M_max:
            # a drive atom must not displace the latent state it belongs to
            pool = [a for a in self.active if a["R"] >= 0.5 * self.thr_rem
                    and not (best[0] == "drv" and a["key"][0] == "res")]
            if pool:
                self._evict(max(pool, key=lambda a: a["R"]), "ACTIVE->EVICTED(replaced)")
            else:
                best = None
        if best is not None and best in self.hot:
            st = self.hot.pop(best)
            theta0 = st["S"] / (st["V"] + self.sigma2 / self.rho); self.fp["decision"] += 3
            inv_vref = st["n"] / st["V"] if st["V"] > 0 else 0.0; self.fp["decision"] += 1
            self.active.append({"key": best, "theta": theta0, "R": 0.0, "E": best_lm,
                                "t_on": self.t, "inv_vref": inv_vref})
            self.events.append((self.t, "PROVISIONAL->ACTIVE", self.label(best), best_lm))
            if best[0] == "res":
                self.hot[best] = self._fresh()
                self._open_drive_tests(best[1])
            elif best[0] == "drv":
                for k in [k for k in self.hot if k[0] == "drv"]:
                    del self.hot[k]
                self.q = {best[1]: self.q[best[1]]}

        # (c) DORMANT -> PROVISIONAL: refill lag tests from screening ranks (fresh statistics)
        n_lag_hot = sum(1 for k in self.hot if k[0] == "lag")
        if n_lag_hot < self.H_hot:
            taken = {k[1:] for k in self.hot if k[0] == "lag"} | \
                    {a["key"][1:] for a in self.active if a["key"][0] == "lag"}
            ranked = sorted((c for c in self.lag_cands if c not in taken),
                            key=lambda c: -abs(self.screen[c]))
            for c in ranked[: self.H_hot - n_lag_hot]:
                self.hot[("lag",) + c] = self._fresh()
                self.screen[c] = 0.0
                self.n_provisional += 1

    # ------------------------------------------------------------------ explanation
    def explain(self) -> List[str]:
        out = ["base: y ~ " + " ".join(f"{w:+.2f}*x{i}" for i, w in enumerate(self.theta_b[:-1]))
               + f" {self.theta_b[-1]:+.2f}"]
        for a in self.active:
            out.append(f"{self.label(a['key'])}: coef {a['theta']:+.3f}, evidencia {a['E']:.1f} nats, "
                       f"CUSUM {a['R']:.1f}/{self.thr_rem:.1f}, ativo desde t={a['t_on']}")
        out.append(f"ruido residual sigma={math.sqrt(self.sigma2):.3f}")
        return out

    def memory_bytes(self) -> int:
        # float32 convention; screening scores fp16
        return (4 * (self.L + 1) * self.d + 4 * (self.d + 1) + 20 * len(self.active)
                + 4 * len(self.poles) + 4 * len(self.q) + 2 * len(self.lag_cands)
                + 12 * len(self.hot) + 8)
