"""dev_lean.py — DEV (previously used data only): cheap target-memory experts and lean aggregation vs the dense window."""
import math, os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "LEBRE-V0.46-STABLE-COMPETITIVE-01")); sys.path.insert(0, HERE)
import dev_arch as A                      # DEV loaders, NLinear window, v0.5 prototype
G = A.G
from experiments.bench01.streams import CausalStandardScaler
from lebre_v045 import LebreV045

def lagset(s, kind):
    if kind == "K6":
        return [2, 3, s - 1, s, s + 1, 2 * s] if s else [2, 3, 4, 8, 16, 24]
    if kind == "K10":
        return [2, 3, 4, s - 2, s - 1, s, s + 1, s + 2, 2 * s - 1, 2 * s] if s else [2, 3, 4, 5, 6, 8, 12, 16, 24, 48]
    if kind == "K4":
        return [2, s, s + 1, 2 * s] if s else [2, 3, 8, 24]

class SparseMem:
    """y_hat = y_{t-1} + sd * sum_k w_k (y_{t-k} - y_{t-1}) / sd, k in a sparse seasonal lag set; NLMS; ring buffer."""
    def __init__(self, lags, mu=0.05):
        self.K = np.array(lags); self.Lb = int(self.K.max()); self.mu = mu
        self.buf = np.zeros(self.Lb); self.n = 0; self.m = 0.0; self.s2 = 0.0; self.w = np.zeros(len(lags)); self.phi = None
        self.fp = 0.0
    def predict(self):
        if self.n < self.Lb:
            self.phi = None; return self.buf[(self.n - 1) % self.Lb] if self.n else 0.0
        sd = math.sqrt(self.s2 / self.n) if self.s2 > 0 else 1.0
        last = self.buf[(self.n - 1) % self.Lb]
        self.phi = (self.buf[(self.n - self.K) % self.Lb] - last) / sd; self.sd = sd; self.last = last
        self.fp += 3 * len(self.K) + 4
        return last + sd * float(self.w @ self.phi)
    def update(self, y, yh):
        if self.phi is not None:
            e = (y - yh) / self.sd
            self.w += self.mu * e * self.phi / (1e-6 + float(self.phi @ self.phi)); self.fp += 4 * len(self.K) + 4
        self.buf[self.n % self.Lb] = y; self.n += 1; d = y - self.m; self.m += d / self.n; self.s2 += d * (y - self.m); self.fp += 6
    def step(self, x, y):
        p = self.predict(); self.update(y, p); return p

class ProfMem:
    """rich cheap memory: y_hat = y_{t-1} + sd * w . phi, phi (relative to y_{t-1}, scaled by causal sd):
       f_mean = (m - y_{t-1}), f_d1 = (y_{t-1} - y_{t-2}), f_sn = (y_{t-s} - y_{t-1}), f_si = (y_{t-s+1} - y_{t-s}),
       f_prof = G[phase] (EW mean of the increment at this phase over past cycles, Holt-Winters-type seasonal state).
       Without season: f_mean, f_d1, (y_{t-2}-y_{t-1}) ... lags {2,4,8}."""
    def __init__(self, s, mu=0.05, a_prof=0.1, a_mean=0.01, feats="all"):
        self.s = s; self.mu = mu; self.ap = a_prof; self.am = a_mean; self.feats = feats
        self.Lb = 2 * s + 2 if s else 9
        self.buf = np.zeros(self.Lb); self.n = 0; self.mv = 0.0; self.s2 = 0.0; self.mew = None
        self.G = np.zeros(s) if s else None
        nf = {"all": 5, "noprof": 4, "nomean": 4}[feats] if s else 4
        self.w = np.zeros(nf); self.phi = None; self.fp = 0.0
    def _b(self, k):  # y_{t-k}, k>=1 (buffer holds values up to y_{t-1})
        return self.buf[(self.n - k) % self.Lb]
    def predict(self):
        if self.n < self.Lb:
            self.phi = None; return self._b(1) if self.n else 0.0
        sd = math.sqrt(self.s2 / self.n) if self.s2 > 0 else 1.0; last = self._b(1); inv = 1.0 / sd
        if self.s:
            s = self.s; f = [self.mew - last, last - self._b(2), self._b(s) - last, self._b(s - 1) - self._b(s), self.G[self.n % s]]
            if self.feats == "noprof": f = f[:4]
            if self.feats == "nomean": f = f[1:]
        else:
            f = [self.mew - last, last - self._b(2), self._b(4) - last, self._b(8) - last]
        self.phi = np.array(f) * inv; self.sd = sd; self.last = last
        self.fp += 3 * len(f) + 4
        return last + sd * float(self.w @ self.phi)
    def update(self, y, yh):
        if self.phi is not None:
            e = (y - yh) / self.sd
            self.w += self.mu * e * self.phi / (1e-6 + float(self.phi @ self.phi)); self.fp += 4 * len(self.w) + 4
        if self.s and self.n >= 1:
            ph = self.n % self.s; self.G[ph] += self.ap * ((y - self._b(1)) - self.G[ph]); self.fp += 4
        self.mew = y if self.mew is None else self.mew + self.am * (y - self.mew); self.fp += 3
        self.buf[self.n % self.Lb] = y; self.n += 1; d = y - self.mv; self.mv += d / self.n; self.s2 += d * (y - self.mv); self.fp += 6
    def step(self, x, y):
        p = self.predict(); self.update(y, p); return p


class Cascade:
    """memory M first, LEBRE (v0.4.5) on M's residual; no aggregation."""
    def __init__(self, d, s, feats, ip=True):
        self.M = ProfMem(s, feats=feats); self.A = LebreV045(d=d, ipnlms=ip); self.fp = 0.0
    def step(self, x, y):
        a0 = sum(self.A.fp.values()); pm = self.M.predict(); r = self.A.step(x, y - pm); self.M.update(y, pm)
        self.fp += sum(self.A.fp.values()) - a0 + 2; return pm + r
    @property
    def fptot(self): return self.fp + self.M.fp


class Res:
    """LEBRE (v0.4.5) first; memory M models LEBRE's residual (error-correction). No aggregator, no feedback loop."""
    def __init__(self, d, s, feats, ip=True):
        self.M = ProfMem(s, feats=feats); self.A = LebreV045(d=d, ipnlms=ip); self.fp = 0.0
    def step(self, x, y):
        a0 = sum(self.A.fp.values())
        rm = self.M.predict(); pa = self.A.step(x, y); self.M.update(y - pa, rm)
        self.fp += sum(self.A.fp.values()) - a0 + 2; return pa + rm
    @property
    def fptot(self): return self.fp + self.M.fp


class Lean:
    """EWA of A = LEBRE v0.4.5 and M = sparse target memory."""
    def __init__(self, d, s, kind, eta=1.0, lam=0.99):
        ip = not kind.endswith("_NOIP"); kind = kind.replace("_NOIP", "")
        self.A = LebreV045(d=d, ipnlms=ip)
        self.M = ProfMem(s, feats=kind[1:].lower() if kind.startswith("P") else "all") if kind.startswith("P") else SparseMem(lagset(s, kind)); self.L = np.zeros(2); self.mm = None
        self.eta, self.lam = eta, lam; self.fp = 0.0
    def step(self, x, y):
        a0 = sum(self.A.fp.values())
        pm = self.M.predict(); pa = self.A.step(x, y)
        w = np.exp(-self.eta * (self.L - self.L.min())); w /= w.sum(); p = w[0] * pa + w[1] * pm
        self.M.update(y, pm)
        l = np.array([(y - pa) ** 2, (y - pm) ** 2]); self.mm = l.mean() if self.mm is None else self.mm + (1 - self.lam) * (l.mean() - self.mm)
        self.L = self.lam * self.L + l / (self.mm + 1e-300)
        self.fp += sum(self.A.fp.values()) - a0 + 25
        return p
    @property
    def fptot(self): return self.fp + self.M.fp

class Stack:
    """regression combination (Granger-Ramanathan 1984 / stacking): the structural forecast is one more feature of M."""
    def __init__(self, d, s):
        from lebre_v051 import MemoryExpert
        self.S = LebreV045(d=d, ipnlms=False, intervals=False)
        feats = ("mean", "d1", "sn", "si", "prof") if s else ("mean", "d1")
        self.M = MemoryExpert(s, feats=feats + ("struct",)); self.fp = 0.0; self.peak = 0.0
    def step(self, x, y):
        a0 = sum(self.S.fp.values()); m0 = self.M.fp
        ps = self.S.step(x, y); self.M.struct = ps
        p = self.M.predict(); self.M.update(y, p)
        f = sum(self.S.fp.values()) - a0 + self.M.fp - m0; self.fp += f; self.peak = max(self.peak, f)
        return p
    @property
    def fptot(self): return self.fp

class V051W:
    def __init__(self, d, s, **kw):
        from lebre_v051 import LebreV051
        self.m = LebreV051(d=d, season=s, **kw)
    def step(self, x, y): return self.m.step(x, y)
    @property
    def fptot(self): return sum(self.m.fp.values())

V051_VARIANTS = {"V051": {}, "V051_NOSI": {"mem_feats": ("mean", "d1", "sn", "prof")},
                 "V051_NOSI_NOMEAN": {"mem_feats": ("d1", "sn", "prof")}, "V051_E1": {"every": 1}, "V051_NODORM": {"eps_dormant": 0.0}, "V051_ETA05": {"eta": 0.5}, "V051_ETA05_NODORM": {"eta": 0.5, "eps_dormant": 0.0}, "V051_H2B1": {"H_hot": 2, "B_probe": 1}, "V051_H3": {"H_hot": 3},
                 "V051_IP": {"ipnlms": True}, "V051_H2B1_P3": {"H_hot": 2, "B_probe": 1, "poles": (0.0, 0.5, 0.9)}}

def make(kind, d, s):
    if kind in V051_VARIANTS: return V051W(d, s, **V051_VARIANTS[kind])
    if kind == "STACK": return Stack(d, s)
    if kind.startswith("PMEM_"): return ProfMem(s, feats=kind[5:].lower())
    if kind.startswith("RES_"): return Res(d, s, kind[4:].replace("_NOIP", "").lower(), ip=not kind.endswith("_NOIP"))
    if kind.startswith("CAS_"): return Cascade(d, s, kind[4:].replace("_NOIP", "").lower(), ip=not kind.endswith("_NOIP"))
    if kind.startswith("MEM_"): return SparseMem(lagset(s, kind[4:]))
    if kind.startswith("LEAN_"): return Lean(d, s, kind[5:])
    return A.Model(kind, d, s, {"NLIN_W005": .05}.get(kind, .2))

def run(a):
    task, kind, off = a
    X, y = G.load(task); T = len(X); ts = int(.3 * T); s = A.SEASON[task]
    sc = CausalStandardScaler(d=X.shape[1]); m = make(kind, X.shape[1], s); e = []
    for i in range(off, T):
        p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i]); p = p[0] if isinstance(p, tuple) else p
        if i >= ts: e.append((y[i] - p) ** 2)
    fp = m.fptot / (T - off) if hasattr(m, "fptot") else (m.fp / (T - off) if hasattr(m, "fp") and isinstance(m.fp, float) else np.nan)
    return {"task_id": task, "arm": kind, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if np.all(np.isfinite(e)) else np.inf, "fp": fp}

def internal(a):
    from scratch.bench_v02_integration import generate_v02_stream
    task, seed, kind = a
    X, y, _ = generate_v02_stream(task, seed=seed, total_steps=6000); m = make(kind, 5, None); e = []
    for t in range(6000):
        p = m.step(X[t], float(y[t])); p = p[0] if isinstance(p, tuple) else p; e.append((y[t] - p) ** 2)
    fp = m.fptot / 6000 if hasattr(m, "fptot") else np.nan
    return {"task_id": task, "seed": seed, "arm": kind, "nmse": float(np.mean(e) / np.var(y)), "fp": fp}

if __name__ == "__main__":
    arms = sys.argv[1].split(","); mode = sys.argv[2] if len(sys.argv) > 2 else "ext"
    if mode == "ext":
        jobs = [(t, a, o) for t in A.TASKS for a in arms for o in (0, 200, 400)]
        with ProcessPoolExecutor(16) as ex: df = pd.DataFrame(list(ex.map(run, jobs, chunksize=1)))
        out = os.path.join(HERE, "DEV_LEAN_EXT.csv")
        if os.path.exists(out): old = pd.read_csv(out); df = pd.concat([old[~old.arm.isin(arms)], df])
        df.to_csv(out, index=False)
        w = df.pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
        pd.set_option("display.width", 250)
        print(df.groupby(["task_id", "arm"]).nmse.median().unstack().round(4).to_string())
        g = df.groupby(["task_id", "arm"]).nmse; ins = (g.max() / g.min()).unstack()
        for a in w.columns:
            print(f"{a:14s} geo/NLIN_W005 {np.exp(np.log(w[a] / w.NLIN_W005).mean()):.3f}  instab max {ins[a].max():.2f}  fp {df[df.arm == a].fp.mean():.0f}")
    else:
        from scratch.bench_v02_integration import BENCHMARK_TASKS
        jobs = [(t, s, a) for s in range(2176, 2186) for t in BENCHMARK_TASKS for a in arms]
        with ProcessPoolExecutor(16) as ex: df = pd.DataFrame(list(ex.map(internal, jobs)))
        print(df.groupby("arm")[["nmse", "fp"]].mean().round(4))
