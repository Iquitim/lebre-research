"""change_engine.py — generic engine for evidence-governed structural change (LEBRE v0.52).

Independent of WHAT the structure is (lags, filters, latent states today; multivariate edits later). It manages:
  * persistent hypotheses — one anytime-valid e-process per candidate change (Choe & Ramdas 2024, Thm 3, weak null,
    clipped loss differences minus a margin); pauses between episodes form a predictable subsequence (their Sec. F.1);
  * acceptance levels — LOND-type, fixed when a hypothesis is created, so decisions may be asynchronous (e-LOND,
    Xu & Ramdas 2024): gamma = 1/(2P) for the first P hypotheses, then a summable tail; level = alpha * gamma * (R + 1);
  * experiment slots — at most m concurrent episodes; an episode ends when accepted, when it is not ahead after n_min
    samples (scan rule, Xu, Mei & Moustakides 2021) or after T_max samples.
The model supplies the challengers' outputs, the loss differences and the proposal policy.
"""
import math

import numpy as np


def _gamma_const(n=10 ** 6):
    k = np.arange(1, n + 1, dtype=float)
    s = float(np.sum(1.0 / (k * np.log(k + 1) ** 2)))
    return 1.0 / (s + 1.0 / math.log(n + 1))          # tail bound of the integral


GAMMA_C = _gamma_const()


def gamma_k(k):
    return GAMMA_C / (k * math.log(k + 1) ** 2)


class Hypothesis:
    """Weak null: over the steps at which this change was tested, the challenger did not improve the clipped loss of the
    reference model by more than eps on average (E_{i-1}[d_i] <= 0, d_i = clipped-loss difference minus eps).

    evidence (all anytime-valid e-processes under the weak null; one-sided, the alternative is an improvement):
      "psiE2" — Choe & Ramdas (2024) sub-exponential mixture as stated there: |d_i - gamma_i| <= c, c = 2(1+|eps|)
                (the v0.52 atomic default, kept for the ablation);
      "psiE1" — the same mixture with the ONE-SIDED condition that its proof actually uses (Fan, Grama & Liu 2015 via
                Howard et al. 2021, Sec. A.8: d_i - gamma_i >= -c): d_i >= -(1 + max(eps, 0)) always, so with a
                predictable centring gamma_i <= 0, c = 1 + max(eps, 0) (DEV_LOG, 27/09/2026);
      "bet"   — testing by betting: W_t = prod (1 + lambda_i d_i), lambda_i predictable in [0, 0.5/(1+max(eps,0))]
                (so 1 + lambda_i d_i >= 0.5), plug-in lambda_i = m/(v + m^2) from the past increments (aGRAPA,
                Waudby-Smith & Ramdas 2023); a nonnegative supermartingale under the weak null;
      "mix"   — the average of the "psiE1" and "bet" e-values (an average of e-processes is an e-process).
    """
    LAMBDAS_FRAC = 0.9 * 2.0 ** -np.arange(8)            # lambda grid as fraction of 1/c (uniform mixture)

    def __init__(self, eps, alpha_level, idx, evidence="psiE2"):
        self.eps = eps; self.evidence = evidence
        self.c = 2.0 * (1.0 + abs(eps)) if evidence == "psiE2" else 1.0 + max(eps, 0.0)
        self.alpha = alpha_level; self.log_thr = math.log(1.0 / alpha_level); self.idx = idx
        self.S = 0.0; self.V = 0.0; self.n = 0; self.mean = 0.0
        self.lam = self.LAMBDAS_FRAC / self.c
        self.psi = (-np.log(1 - self.c * self.lam) - self.c * self.lam) / self.c ** 2
        self.logW = 0.0; self.m2 = 0.0; self.lam_max = 0.5 / (1.0 + max(eps, 0.0))

    def observe(self, d):
        if self.evidence == "psiE2":
            gamma = max(-self.c / 2, min(self.c / 2, self.mean))   # predictable centring (past mean)
        else:
            gamma = max(-self.c, min(0.0, self.mean))              # one-sided: gamma <= 0 keeps d - gamma >= -c
        if self.evidence in ("bet", "mix"):
            v = self.m2 / self.n if self.n > 1 else 1.0
            lam = 0.0 if self.n < 10 else max(0.0, min(self.lam_max, self.mean / (v + self.mean ** 2 + 1e-12)))
            self.logW += math.log1p(lam * d)
        self.S += d; self.V += (d - gamma) ** 2; self.n += 1
        dm = d - self.mean; self.mean += dm / self.n; self.m2 += dm * (d - self.mean)

    def _log_mix(self):
        a = self.lam * self.S - self.psi * self.V
        m = a.max()
        return float(m + math.log(np.mean(np.exp(a - m))))

    def log_e(self):
        if self.evidence == "bet":
            return self.logW
        if self.evidence == "mix":
            a, b = self._log_mix(), self.logW
            m = max(a, b)
            return m + math.log(0.5 * (math.exp(a - m) + math.exp(b - m)))
        return self._log_mix()


class Experiment:
    """One episode on a slot; evidence goes to the persistent hypothesis. `theta`/`pow` are the challenger's own
    parameters, owned and updated by the model."""

    def __init__(self, kind, add_key, rem_key, hyp, t0):
        self.kind, self.add_key, self.rem_key, self.hyp, self.t0 = kind, add_key, rem_key, hyp, t0
        self.theta = 0.0; self.pow = None; self.S = 0.0; self.n = 0
        self.eps = hyp.eps

    def observe(self, d):
        self.hyp.observe(d); self.S += d; self.n += 1


class ChangeEngine:
    def __init__(self, alpha, family_size, m_slots, n_min, T_max, evidence="psiE2"):
        self.alpha, self.P, self.m_slots, self.n_min, self.T_max = alpha, family_size, m_slots, n_min, T_max
        self.evidence = evidence
        self.hyps = {}; self.n_hyp = 0; self.n_accepted = 0; self.k_started = 0
        self.slots = []; self.fp = 0.0

    def hypothesis(self, hkey, eps):
        if hkey not in self.hyps:
            self.n_hyp += 1
            g = 1.0 / (2 * self.P) if self.n_hyp <= self.P else 0.5 * gamma_k(self.n_hyp - self.P)   # sum <= 1
            self.hyps[hkey] = Hypothesis(eps, min(self.alpha * g * (self.n_accepted + 1), 0.5), self.n_hyp, self.evidence)
        return self.hyps[hkey]

    def open(self, kind, add_key, rem_key, hkey, eps, t):
        self.k_started += 1
        ex = Experiment(kind, add_key, rem_key, self.hypothesis(hkey, eps), t)
        self.slots.append(ex)
        return ex

    def free_slots(self):
        return self.m_slots - len(self.slots)

    def review(self):
        """returns [(decision, experiment, log_e)] with decision in {'accepted', 'closed'}; keeps the others running."""
        out, keep = [], []
        for ex in self.slots:
            le = ex.hyp.log_e(); self.fp += 3 * len(ex.hyp.lam)
            if le >= ex.hyp.log_thr:
                out.append(("accepted", ex, le))
            elif ex.n >= self.T_max or (ex.n >= self.n_min and ex.S <= 0.0):   # scan rule: not ahead -> free the slot
                out.append(("closed", ex, le))
            else:
                keep.append(ex)
        self.slots = keep
        return out

    def consume(self, ex):
        """an accepted change: count the discovery and retire its hypothesis (a new instance if ever retested)."""
        self.n_accepted += 1
        self.hyps = {k: h for k, h in self.hyps.items() if h is not ex.hyp}

    def busy_keys(self):
        return {k for ex in self.slots for k in (ex.add_key, ex.rem_key) if k}
