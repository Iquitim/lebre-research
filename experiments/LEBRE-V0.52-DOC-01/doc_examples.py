"""doc_examples.py — illustrative runs of the FROZEN LEBRE v0.52 (canonical configuration, imported, never edited) for the
documentation figures. DEVELOPMENT data only (ons:ITUTINGA) and one declared synthetic process (seed 5290):
  y_t = 0.8 x0_{t-12} + 0.3 mean(x1_{t-4..t-7}) + e_t,  x_i AR(1) with coefficient 0.5 (unit variance), e ~ N(0, 0.5^2),
  x2 irrelevant, T = 20000.
Output: DOC_EXAMPLES.npz / DOC_EXAMPLES.json (forecast window, evidence traces at decision steps, events, recovered
response, analytic cost by component)."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EXT = os.path.join(ROOT, "experiments", "LEBRE-V0.52-EXT-01"); PROTO = os.path.join(ROOT, "experiments", "LEBRE-V0.52-PROTO-01")
for p in (ROOT, PROTO, EXT):
    sys.path.insert(0, p)
import heldout2_cfg as CFG  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
from lebre_v052h import LebreV052H  # noqa: E402


def run(X, y, qu, s, s2=None, win=None):
    Xs = C._scaled_inputs(X)
    m = LebreV052H(d=X.shape[1], season=s, **dict(CFG.CANONICAL, season2=s2))
    T = len(y); f = np.empty(T); q = np.full(T, np.nan); ws = np.empty(T); ev = []
    comp = {}
    for t in range(T):
        f[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        q[t] = m.qhat if m.qhat is not None else np.nan; ws[t] = m.wS
        if t % 10 == 0:
            for ex in m.engine.slots:
                ev.append((t, str(ex.kind), str(ex.add_key), str(ex.rem_key), float(ex.hyp.log_e()), float(ex.hyp.log_thr), int(ex.n)))
    comp = dict(m.fp); comp["memory"] += m.M.fp; comp["control"] += m.engine.fp
    comp = {k: v / T for k, v in comp.items()}
    events = [(int(e[0]), e[1], e[2], str(e[3]), str(e[4]), e[5], e[6]) for e in m.events]
    resp = {str(u): m.response(u) for u in m.active if u[0] == "in"}
    groups = {str(u): sorted(m.equivalents(u)) for u in m.active if u[0] == "in"}
    return m, f, q, ws, ev, comp, events, resp, groups


out = {}
# (A) development river
d = D.load("ons:ITUTINGA")
m, f, q, ws, ev, comp, events, resp, groups = run(d["X"], d["y"], d["quarantine"], d["season"])
y = d["y"]; ts = int(0.3 * len(y)); msk = np.isfinite(y); msk[:ts] = False
out["A"] = {"task": "ons:ITUTINGA", "names": list(d.get("names", [])), "T": len(y), "d": int(d["X"].shape[1]), "season": d["season"],
            "events": events, "comp": comp, "resp": {k: [[list(a), b] for a, b in v] for k, v in resp.items()}, "groups": groups,
            "coverage": m.coverage(), "nmse": float(np.mean((y[msk] - f[msk]) ** 2) / np.var(y[msk]))}
np.savez_compressed(os.path.join(HERE, "DOC_EXAMPLE_A.npz"), y=y, f=f, q=q, ws=ws,
                    ev=np.array([(e[0], e[4], e[5], e[6]) for e in ev]), ev_key=np.array([e[1] + "|" + e[2] + "|" + e[3] for e in ev]))
print("A", out["A"]["events"], out["A"]["resp"], out["A"]["groups"], round(out["A"]["nmse"], 4), {k: round(v, 1) for k, v in comp.items()})
# (B) declared synthetic process
rng = np.random.default_rng(5290); T = 20000; X = np.zeros((T, 3)); e = rng.standard_normal((T, 3)) * np.sqrt(1 - 0.25)
for t in range(1, T):
    X[t] = 0.5 * X[t - 1] + e[t]
y = np.zeros(T)
for t in range(12, T):
    y[t] = 0.8 * X[t - 12, 0] + 0.3 * X[t - 7:t - 3, 1].mean()
y += 0.5 * rng.standard_normal(T)
m, f, q, ws, ev, comp, events, resp, groups = run(X, y, np.zeros(T, bool), None)
out["B"] = {"events": events, "comp": comp, "resp": {k: [[list(a), b] for a, b in v] for k, v in resp.items()}, "groups": groups,
            "coverage": m.coverage()}
np.savez_compressed(os.path.join(HERE, "DOC_EXAMPLE_B.npz"), y=y, f=f,
                    ev=np.array([(e[0], e[4], e[5], e[6]) for e in ev]), ev_key=np.array([e[1] + "|" + e[2] + "|" + e[3] for e in ev]))
print("B", events, out["B"]["resp"], {k: round(v, 1) for k, v in comp.items()})
json.dump(out, open(os.path.join(HERE, "DOC_EXAMPLES.json"), "w", encoding="utf-8"), indent=1, default=str)
