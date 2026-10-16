#!/usr/bin/env python3
"""check_inequalities.py — numerical sanity check (not a proof) of the two inequalities used in NOTA_FORMAL_F1.md, on
the exact ranges of the frozen v0.54 code (experiments/LEBRE-V0.54-PROTO-01/lebre054/_engine.py):

  (L1) Fan's inequality, scaled by c:  exp(lam*y - psi(lam)*y^2) <= 1 + lam*y  for y >= -c, 0 <= lam < 1/c,
       psi(lam) = (-log(1 - c*lam) - c*lam) / c^2;
  (L2) exp(-a) * (1 + a) <= 1 for every real a.

It also reads the constants of the frozen engine (lambda grid, c for eps = +-0.002) and checks that the increments of
the test lie in [-c, inf) and that sum of g_j <= 1 for the level sequences. Prints PASS/FAIL per check."""
import importlib.util
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("eng", ROOT / "experiments/LEBRE-V0.54-PROTO-01/lebre054/_engine.py")
eng = importlib.util.module_from_spec(spec); spec.loader.exec_module(eng)

ok_all = True


def report(name, ok, detail=""):
    global ok_all
    ok_all &= bool(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


for eps in (0.002, -0.002):
    h = eng.Hypothesis(eps, 0.05, 1)
    c = h.c
    report(f"lambda grid inside [0, 1/c) for eps={eps}", bool(np.all((h.lam >= 0) & (h.lam < 1 / c))),
           f"max lam*c = {float(h.lam.max() * c):.3f}")
    y = np.concatenate([np.linspace(-c, 0, 20001), np.linspace(0, 5, 20001), np.logspace(0, 3, 2001)])
    worst = -math.inf
    for lam in np.concatenate([h.lam, np.linspace(0, 0.999 / c, 400)]):
        psi = (-math.log(1 - c * lam) - c * lam) / c ** 2
        gap = np.exp(lam * y - psi * y * y) - (1 + lam * y)
        worst = max(worst, float(gap.max()))
    report(f"(L1) Fan inequality, eps={eps}", worst <= 1e-12, f"max of lhs - rhs = {worst:.3e}")
    # increments d = l_ref - l_chal - eps with clipped losses in [0, 1]; gamma = min(past mean, 0) >= -c
    dmin = 0.0 - 1.0 - eps
    report(f"increment lower bound d >= -c, eps={eps}", dmin >= -c - 1e-15, f"min d = {dmin}, -c = {-c}")

a = np.linspace(-50, 50, 200001)
report("(L2) exp(-a)(1+a) <= 1", float((np.exp(-a) * (1 + a)).max()) <= 1 + 1e-15,
       f"max = {float((np.exp(-a) * (1 + a)).max()):.15f}")

k = np.arange(1, 2_000_001, dtype=float)
s = float(np.sum(eng.GAMMA_C / (k * np.log(k + 1) ** 2)))
report("sum of gamma_k (2e6 terms) < 1", s < 1, f"partial sum = {s:.6f} (tail bound is in GAMMA_C)")
for d in (1, 4, 50):
    P = 2 * (d + 2)
    report(f"main engine: sum of g_j <= 1 (d={d})", P * (1 / (2 * P)) + 0.5 * s <= 1, "first P at 1/(2P), then 0.5*gamma")
print("RESULT:", "PASS" if ok_all else "FAIL")
