#!/usr/bin/env python3
"""semi_synth6.py — evaluation set #6 (paired-control iteration), declared on 27/09/2026 BEFORE implementing it.
Same REAL inputs (outflows of 5 plants of the development river Grande, 3-h), new structures, new seeds:

  SU0 null                      y = e
  SU1 one input                 y = 0.7 x3(t-5) + e
  SU2 two inputs (one grouped)  y = 0.5 x1(t-2) + 0.5 x2(t-16) + e      ({x0, x1} equivalence group)
  SU3 two-lobed + AR noise      y = 0.6 x4(t-1) + 0.6 x4(t-8) + v,  v = 0.9 v(t-1) + 0.5 e
  SU4 AR target, no inputs      y = v,  v = 0.9 v(t-1) + sqrt(0.19) e   (own past is REAL structure here)

Seeds 6601-6603; pure synthetics 9601-9603.
NULL BATCH (criterion 7): targets with no structure at all, real inputs — 'white' y = e (seeds 6701-6715) and 'heavy'
y = t3/sqrt(3) (seeds 6716-6730). Any accepted change (input, own past or residual state) is a false change there.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401
from semi_synth4 import groups  # noqa: E402,F401

SEEDS = [6601, 6602, 6603]
NULL_SEEDS = {"white": list(range(6701, 6716)), "heavy": list(range(6716, 6731))}
TRUTH = {"SU0": set(), "SU1": {("in", 3)}, "SU2": {("in", 1), ("in", 2)}, "SU3": {("in", 4)}, "SU4": set()}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task in ("SU0", "white"):
        return e
    if task == "heavy":
        return rng.standard_t(3, size=T) / np.sqrt(3.0)
    if task == "SU1":
        return 0.7 * lag(3, 5) + e
    if task == "SU2":
        return 0.5 * lag(1, 2) + 0.5 * lag(2, 16) + e
    v = np.zeros(T)
    if task == "SU3":
        for t in range(1, T):
            v[t] = 0.9 * v[t - 1] + 0.5 * e[t]
        return 0.6 * lag(4, 1) + 0.6 * lag(4, 8) + v
    for t in range(1, T):
        v[t] = 0.9 * v[t - 1] + np.sqrt(0.19) * e[t]
    return v
