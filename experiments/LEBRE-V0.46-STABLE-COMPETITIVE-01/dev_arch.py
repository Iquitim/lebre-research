"""dev_arch.py — DEV: architectures that remove level learning / add long target memory (previously used data only)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "LEBRE-V0.45-ROBUST-GUARD-01"))
sys.path.insert(0, os.path.join(HERE, "..", "LEBRE-V0.4-EXTERNAL-BENCH-04")); sys.path.insert(0, HERE)
import dev_guard as G  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v045 import LebreV045  # noqa: E402
from newmodels import OnlineLTSF, lookback  # noqa: E402

SEASON = {"A_ETTh1": 24, "A_ETTm1": 96, "A_ECL": 24, "A_Traffic": 24, "A_JenaWeather": 144, "A_Exchange": None,
          "M_AusElectricity": 48, "M_Pedestrian": 24, "M_KDDCup2018": 24, "M_Solar10min": 144,
          "X1_Appliances": 144, "X2_BeijingPM25": 24, "X3_MetroTraffic": 24}
TASKS = list(SEASON)
OFFSETS = [0, 100, 200, 300, 400]


class JointLin:
    """one NLMS on [NLinear window features (target, relative to last value), current standardised inputs x]."""
    def __init__(self, L, d, mu, use_x=True, lebre=False):
        self.win = OnlineLTSF(L, "nlinear", mu=mu); self.mu = mu; self.use_x = use_x
        self.wx = np.zeros(d + 1); self.leb = LebreV045(d=d) if lebre else None

    def step(self, x, y):
        w = self.win
        if len(w.buf) < w.L:
            p = w.buf[-1] if len(w.buf) else 0.0
            w.buf = np.append(w.buf, y); w.z.upd(y); return p
        phi, off, sd = w._feat()
        xx = np.append(x, 1.0) if self.use_x else np.zeros(0)
        f = np.concatenate([phi, xx])
        wv = np.concatenate([w.w, self.wx if self.use_x else np.zeros(0)])
        p = off + sd * float(wv @ f)
        r = 0.0
        if self.leb is not None:                       # LEBRE structural layer on the joint residual (scaled)
            r = sd * self.leb.step(x, (y - p) / sd)
        e = (y - p - r) / sd
        g = self.mu * e / (1e-6 + float(f @ f))
        w.w += g * phi
        if self.use_x:
            self.wx += g * xx
        w.buf = np.append(w.buf[1:], y); w.z.upd(y)
        return p + r


class Mix:
    """exponentially weighted aggregation of expert A (LEBRE v0.4.5) and expert B (target-memory window + pruned LEBRE
    on its residual). Loss: squared error normalised by the running mean expert loss; discounted (lambda) cumulative loss."""
    def __init__(self, d, s, mu_w=0.05, eta=1.0, lam=0.999, three=False):
        self.three = three
        self.A = LebreV045(d=d)
        self.win = OnlineLTSF(lookback(s), "nlinear", mu=mu_w); self.R = LebreV045(d=d, prune_base=True)
        self.L = np.zeros(3 if three else 2); self.m = None; self.eta, self.lam = eta, lam; self.wlog = []

    def _peek(self):
        w = self.win
        if len(w.buf) < w.L:
            return w.buf[-1] if len(w.buf) else 0.0
        phi, off, sd = w._feat()
        return off + sd * float(w.w @ phi)

    def step(self, x, y):
        pa = self.A.step(x, y)
        pw = self._peek(); pb = pw + self.R.step(x, y - pw); self.win.step(x, y)
        z = -self.eta * (self.L - self.L.min()); w = np.exp(z); w /= w.sum()
        P = np.array([pa, pb, pw] if self.three else [pa, pb])
        p = float(w @ P)
        l = (y - P) ** 2
        self.m = l.mean() if self.m is None else self.m + (1 - self.lam) * (l.mean() - self.m)
        self.L = self.lam * self.L + l / (self.m + 1e-12)
        return p


class Model:
    def __init__(self, kind, d, s, mu_w=0.2):
        self.kind = kind; self.yp = None
        if kind.startswith("MIX"):
            eta, lam = {"MIX": (1.0, 0.999), "MIX_E03": (0.3, 0.999), "MIX_L99": (1.0, 0.99), "MIX3_L99": (1.0, 0.99), "MIX3_L995": (1.0, 0.995)}[kind]
            self.mx = Mix(d, s, 0.05, eta, lam, three=kind.startswith("MIX3"))
        if kind.startswith("JOINT"):
            self.j = JointLin(lookback(s), d, 0.1, use_x=True, lebre=(kind == "JOINT_LEBRE"))
        self.leb = (LebreV045(d=d, prune_base=True) if kind.startswith("CPRUNE") else LebreV045(d=d)) if kind in ("V045", "DIFF", "CASCADE", "CASCADE_W01", "CPRUNE_W01", "CPRUNE_W005") else None
        self.win = OnlineLTSF(lookback(s), "nlinear", mu=mu_w) if kind in ("NLIN", "NLIN_W01", "NLIN_W005", "CASCADE", "CASCADE_W01", "CPRUNE_W01", "CPRUNE_W005") else None

    def step(self, x, y):
        k = self.kind
        if k.startswith("MIX"):
            return self.mx.step(x, y)
        if k.startswith("JOINT"):
            return self.j.step(x, y)
        if k == "V045":
            return self.leb.step(x, y)
        if k == "DIFF":
            base = self.yp if self.yp is not None else 0.0
            p = base + self.leb.step(x, y - base); self.yp = y; return p
        if k in ("NLIN", "NLIN_W01", "NLIN_W005"):
            return self.win.step(x, y)[0]
        # cascade: window base (relative to last value) + LEBRE on its residual
        pw = self._peek()
        r = self.leb.step(x, y - pw)
        self.win.step(x, y)
        return pw + r

    def _peek(self):
        w = self.win
        if len(w.buf) < w.L:
            return w.buf[-1] if len(w.buf) else 0.0
        phi, off, sd = w._feat()
        return off + sd * float(w.w @ phi)


def run(a):
    task, kind, off = a
    X, y = G.load(task); T = len(X); ts = int(.3 * T)
    sc = CausalStandardScaler(d=X.shape[1]); m = Model(kind, X.shape[1], SEASON[task], {"CASCADE_W01": .1, "NLIN_W01": .1, "CPRUNE_W01": .1, "NLIN_W005": .05, "CPRUNE_W005": .05}.get(kind, .2))
    e = []
    for i in range(off, T):
        p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i])
        if i >= ts:
            e.append((y[i] - p) ** 2)
    return {"task_id": task, "arm": kind, "offset": off,
            "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if np.all(np.isfinite(e)) else np.inf}


if __name__ == "__main__":
    arms = sys.argv[1].split(",") if len(sys.argv) > 1 else ["V045", "DIFF", "NLIN", "CASCADE", "CASCADE_W01"]
    jobs = [(t, a, o) for t in TASKS for a in arms for o in OFFSETS]
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(run, jobs, chunksize=1)))
    out = os.path.join(HERE, "DEV_ARCH.csv")
    if os.path.exists(out):
        old = pd.read_csv(out); df = pd.concat([old[~old.arm.isin(arms)], df])
    df.to_csv(out, index=False)
    g = df.groupby(["task_id", "arm"]).nmse
    pd.set_option("display.width", 220)
    print("mediana\n" + g.median().unstack().round(4).to_string())
    ins = (g.max() / g.min()).unstack()
    w = df.pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
    ref = "NLIN"
    for a in w.columns:
        print(f"{a:14s} geo/NLIN {np.exp(np.log(w[a]/w[ref]).mean()):.3f}  geo/V045 {np.exp(np.log(w[a]/w.V045).mean()):.3f}"
              f"  instab(max/min) mediana {ins[a].median():.2f} max {ins[a].max():.2f}")
