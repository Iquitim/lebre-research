#!/usr/bin/env python3
"""forensic_runs.py — FORENSIC REPRODUCTION of the external critique's H4–H9 tasks with the AUTHORITATIVE, UNMODIFIED
LEBRE v0.51 code (lebre_v051.py / lebre_s051.py, hashes verified at start). Instrumentation is external (wrappers that
observe state); no model behaviour is changed. See FORENSIC_RUN_PLAN.md.

Usage: python forensic_runs.py main | tau | norm | heldout
"""
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V51 = os.path.join(ROOT, "experiments", "LEBRE-V0.51-LEAN-01")
V05 = os.path.join(ROOT, "experiments", "LEBRE-V0.46-STABLE-COMPETITIVE-01")
for p in (V51, V05, ROOT, os.path.join(ROOT, "data", "external_v051"), os.path.join(ROOT, "data", "external_v05"),
          os.path.join(ROOT, "data", "external_bench04")):
    sys.path.insert(0, p)
from lebre_v051 import LebreV051, MemoryExpert  # noqa: E402
from lebre_s051 import StructuralExpert  # noqa: E402

SEEDS = list(range(9101, 9111))
FROZEN = {"lebre_v051.py": "f4dcf460dedfcb583844c54b2cb27d2afe52b44e85f86762305e08ddf226cda3",
          "lebre_s051.py": "3ae285b7ea3c24db00e6ece7f8af6a8ca6ca1baee14849bfe84621757b514613"}


def check_frozen():
    for f, h in FROZEN.items():
        assert hashlib.sha256(open(os.path.join(V51, f), "rb").read()).hexdigest() == h, f


# ------------------------------------------------------------------ task generators (as described in the critique, §"Réplica")
TRUTH = {"T1": {("lag", 1, 3)}, "B1": {("lag", 1, 12)}, "B2": {("lag", 0, 3), ("lag", 2, 7), ("lag", 4, 20)},
         "B3": {("lag", 3, 12), ("res", 0.8), ("drv", 0, 0.8)}, "B4": {("lag", 0, 3), ("lag", 2, 7), ("lag", 4, 20)},
         "N1": set(), "N2": set()}
LENGTH = {"N1": 100_000, "N2": 100_000, "T1": 100_000, "B1": 20_000, "B2": 20_000, "B3": 20_000, "B4": 20_000}


def generate(task, seed, T=None):
    rng = np.random.RandomState(seed); T = T or LENGTH[task]; d = 5
    if task == "N2":
        X = rng.standard_t(3, size=(T, d)) / math.sqrt(3.0); y = rng.standard_t(3, size=T) / math.sqrt(3.0)
        return X, y
    X = rng.normal(size=(T, d))
    lag = lambda i, k: np.r_[np.zeros(k), X[:-k, i]]
    if task == "N1":
        y = rng.normal(size=T)
    elif task == "T1":
        y = 0.8 * lag(1, 3) + rng.normal(size=T)
    elif task == "B1":
        y = 0.8 * lag(1, 12) + rng.normal(size=T)
    elif task in ("B2", "B4"):
        eps = rng.normal(size=T) if task == "B2" else rng.standard_t(3, size=T) / math.sqrt(3.0)
        y = 0.8 * lag(0, 3) + 0.6 * lag(2, 7) + 0.5 * lag(4, 20) + eps
    elif task == "B3":
        z = np.zeros(T); w = rng.normal(size=T)
        for t in range(1, T):
            z[t] = 0.8 * z[t - 1] + X[t, 0] + w[t]
        y = lag(3, 12) + z + rng.normal(size=T)
    return X, y


def key_of(a):
    k = a["key"]
    return (k[0], k[1], k[2]) if k[0] == "lag" else (k[0], round(float(k[1]), 3)) if k[0] == "res" else (k[0], k[1])


def struct_set(S):
    out = set()
    lat = S.latent_atom(); pole = round(float(lat["key"][1]), 3) if lat is not None else None
    for a in S.active:
        k = key_of(a)
        if k[0] == "drv":                                   # a drive is identified by its input AND the latent pole it feeds
            k = ("drv", k[1], pole)
        if k[0] == "lag" and k[2] == 0:
            continue
        out.add(k)
    return out


def hot_key(S, k):
    if k[0] == "lag":
        return (k[0], k[1], k[2])
    if k[0] == "res":
        return (k[0], round(float(k[1]), 3))
    lat = S.latent_atom()
    return ("drv", k[1], round(float(lat["key"][1]), 3) if lat is not None else None)


class Probe:
    """external observer of the structural expert: logs hot-set entries, evidence at decisions, active set, blocking."""
    def __init__(self, S, truth, log_timeline=False):
        self.S = S; self.truth = truth; self.first_hot = {}; self.hot_entries = {}; self.blocked = []
        self.evidence = {}; self.timeline = [] if log_timeline else None; self.n_episodes = 0
        self.cand_types = {}; self._last_lm = {}
        orig = S._decide
        orig_lm = S._log_mixture
        probe = self

        def lm_wrap(st):
            v = orig_lm(st)
            probe._last_lm[id(st)] = v
            return v

        def decide_wrap():
            before_hot = set(S.hot.keys()); probe._last_lm = {}
            hot_items = {k: st for k, st in S.hot.items()}
            n_struct_before = S.n_struct(); active_before = struct_set(S)
            orig()
            t = S.t
            after_hot = set(S.hot.keys())
            for k in after_hot - before_hot:                       # new test episodes opened in this decision
                kk = hot_key(S, k)
                probe.n_episodes += 1; probe.cand_types[k[0]] = probe.cand_types.get(k[0], 0) + 1
                probe.hot_entries.setdefault(kk, []).append(t)
                probe.first_hot.setdefault(kk, t)
            # evidence of true candidates currently under test
            for k, st in hot_items.items():
                kk = hot_key(S, k)
                if kk in probe.truth and id(st) in probe._last_lm:
                    probe.evidence.setdefault(kk, []).append((t, st["n"], float(probe._last_lm[id(st)])))
                    # blocked: crossed the threshold but did not become active and the budget was full
                    if probe._last_lm[id(st)] >= S.thr_add and kk not in struct_set(S) and n_struct_before >= S.M_max:
                        probe.blocked.append((t, kk, sorted(map(str, active_before))))
            if probe.timeline is not None:
                probe.timeline.append((t, "|".join(sorted(map(str, struct_set(S)))), S.n_struct(),
                                       "|".join(sorted(str(k) for k in S.hot))))
        S._decide = decide_wrap
        S._log_mixture = lm_wrap


def run_task(args):
    task, seed, arm, rho, norm, timeline = args
    check_frozen()
    X, y = generate(task, seed)
    T = len(y); truth = TRUTH[task]
    kw = {"rho": rho} if rho is not None else {}
    if arm == "V051":
        m = LebreV051(d=X.shape[1], season=None, **kw); S = m.S
    else:
        m = StructuralExpert(d=X.shape[1], ipnlms=False, intervals=False, **kw); S = m
    pr = Probe(S, truth, log_timeline=timeline)
    Mo = MemoryExpert(None)                                          # M alone on the same stream (critique's "M" column)
    if norm == "ema100":                                             # replica-like normaliser (diagnostic only)
        mu_e = np.zeros(X.shape[1]); v_e = np.ones(X.shape[1]); a = 0.01
    elif norm == "causal":
        from experiments.bench01.streams import CausalStandardScaler
        sc = CausalStandardScaler(d=X.shape[1])
    err, errS, errM, fps, checks, exact = np.empty(T), np.empty(T), np.empty(T), np.empty(T), 0, 0
    first_promo = {}
    for t in range(T):
        x = X[t]
        if norm == "ema100":
            xn = (x - mu_e) / np.sqrt(v_e); d0 = x - mu_e; mu_e += a * d0; v_e += a * (d0 * d0 - v_e)
        elif norm == "causal":
            xn = sc.transform(x); sc.update(x)
        else:
            xn = x
        b = sum(m.fp.values()) if arm == "V051" else sum(S.fp.values())
        p = m.step(xn, float(y[t])); err[t] = y[t] - p
        fps[t] = (sum(m.fp.values()) if arm == "V051" else sum(S.fp.values())) - b
        if arm == "V051":
            errS[t] = y[t] - sum(c for _, c in m._last[2])
        pm = Mo.predict(); Mo.update(float(y[t]), pm); errM[t] = y[t] - pm
        ss = struct_set(S)
        for k in truth:
            if k in ss and k not in first_promo:
                first_promo[k] = t
        if truth and t >= 1000 and t % 100 == 0:
            checks += 1; exact += int(ss == truth)
    if arm != "V051":
        errS = err
    ev = S.events
    promos = [e for e in ev if e[1] == "PROVISIONAL->ACTIVE" and e[0] >= 20]
    rems = [e for e in ev if e[1].startswith("ACTIVE->EVICTED")]
    vy = np.var(y)
    out = {"task": task, "seed": seed, "arm": arm, "rho": rho if rho is not None else 1.0, "norm": norm, "T": T,
           "nmse": float(np.mean(err ** 2) / vy), "nmse_S": float(np.mean(errS ** 2) / vy), "nmse_M": float(np.mean(errM ** 2) / vy),
           "fp_mean": float(fps.mean()), "fp_peak": float(fps.max()), "promotions": len(promos), "removals": len(rems),
           "exact_frac": exact / checks if checks else np.nan, "checks": checks, "episodes": pr.n_episodes,
           "episodes_by_type": json.dumps(pr.cand_types), "blocked_events": len(pr.blocked),
           "coverage": (m.cover_hits / m.cover_n) if arm == "V051" else np.nan}
    ledger = []
    for k in sorted(truth, key=str):
        prom_t = [e[0] for e in promos if key_label(S, k) == e[2]]
        rem_t = [(e[0], e[1]) for e in rems if key_label(S, k) == e[2]]
        evd = pr.evidence.get(k, [])
        ledger.append({"task": task, "seed": seed, "arm": arm, "rho": out["rho"], "norm": norm, "atom": str(k),
                       "first_proposed_t": pr.first_hot.get(k, np.nan), "n_test_episodes": len(pr.hot_entries.get(k, [])),
                       "first_promoted_t": first_promo.get(k, np.nan), "n_promotions": len(prom_t),
                       "n_removals": len(rem_t), "removal_times": json.dumps([r[0] for r in rem_t][:20]),
                       "removal_kinds": json.dumps(sorted({r[1] for r in rem_t})),
                       "max_log_evidence": max((e[2] for e in evd), default=np.nan),
                       "evidence_samples_at_first_cross": next((e[1] for e in evd if e[2] >= S.thr_add), np.nan),
                       "blocked_crossings": sum(1 for b in pr.blocked if b[1] == k),
                       "final_active": k in struct_set(S)})
    comp = {}
    for e in promos:
        if e[2] not in {key_label(S, k) for k in truth}:
            comp[e[2]] = comp.get(e[2], 0) + 1
    out["competing_promotions"] = json.dumps(dict(sorted(comp.items(), key=lambda z: -z[1])[:6]), ensure_ascii=False)
    return out, ledger, (pr.timeline if timeline else None), pr.blocked


def key_label(S, k):
    if k[0] == "lag":
        return S.label(("lag", k[1], k[2]))
    if k[0] == "res":
        return S.label(("res", k[1]))
    return f"x{k[1]} alimenta o estado latente (polo {k[2]:.2f})"   # same format as the model's own label


def main(mode):
    check_frozen()
    t0 = time.time()
    if mode == "main":
        jobs = [(t, s, a, None, "raw", t == "B3") for t in ("N1", "N2", "T1", "B1", "B2", "B3", "B4") for s in SEEDS for a in ("V051", "S_ONLY")]
    elif mode == "tau":
        jobs = [(t, s, "V051", r, "raw", False) for t in ("N1", "B2", "B3") for s in SEEDS for r in (1 / 50, 1 / 200, 1 / 1000)]
    elif mode == "norm":
        jobs = [(t, s, "V051", None, n, False) for t in ("B1", "B2", "B3") for s in SEEDS for n in ("causal", "ema100")]
    with ProcessPoolExecutor(16) as ex:
        res = list(ex.map(run_task, jobs, chunksize=1))
    out = pd.DataFrame([r[0] for r in res]); led = pd.DataFrame([row for r in res for row in r[1]])
    out.to_csv(os.path.join(HERE, f"RUN_{mode.upper()}_SUMMARY.csv"), index=False)
    led.to_csv(os.path.join(HERE, f"RUN_{mode.upper()}_LEDGER.csv"), index=False)
    if mode == "main":
        tl = [(j[0], j[1], j[2], *row) for j, r in zip(jobs, res) if r[2] for row in r[2]]
        pd.DataFrame(tl, columns=["task", "seed", "arm", "t", "active_struct", "n_struct", "hot"]).to_csv(os.path.join(HERE, "RUN_MAIN_B3_TIMELINE.csv"), index=False)
        bl = [(j[0], j[1], j[2], *b) for j, r in zip(jobs, res) for b in r[3]]
        pd.DataFrame(bl, columns=["task", "seed", "arm", "t", "atom", "active_before"]).to_csv(os.path.join(HERE, "RUN_MAIN_BLOCKED.csv"), index=False)
    print(f"{mode}: {len(out)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1])
