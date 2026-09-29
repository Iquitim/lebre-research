#!/usr/bin/env python3
"""semi_synth3.py — evaluation set #3 for the v0.52 evidence/peak iteration, declared on 27/09/2026 BEFORE implementing it
(semi_synth.py was used to design; semi_synth2.py was consumed by the measurement of the hierarchical version).
Same REAL inputs (outflows of 5 plants of the development river Grande, 3-h), new declared structures, new seeds:

  SP0 null              y = e
  SP1 one input         y = 0.7 x4(t-6) + e
  SP2 two inputs        y = 0.6 x0(t-2) + 0.6 x3(t-20) + e
  SP3 storage + lag     z = 0.85 z(t-1) + x1(t) (rescaled to unit variance);  y = 0.6 z + 0.6 x2(t-11) + e
  SP4 null, AR target   y = v,  v = 0.95 v(t-1) + sqrt(1 - 0.95^2) e

e ~ N(0, 1); seeds 6301-6303 (not used before). Pure synthetics of the same measurement: seeds 9301-9303.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401

SEEDS = [6301, 6302, 6303]
TRUTH = {"SP0": set(), "SP1": {("in", 4)}, "SP2": {("in", 0), ("in", 3)}, "SP3": {("in", 1), ("in", 2)}, "SP4": set()}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task == "SP0":
        return e
    if task == "SP1":
        return 0.7 * lag(4, 6) + e
    if task == "SP2":
        return 0.6 * lag(0, 2) + 0.6 * lag(3, 20) + e
    if task == "SP3":
        z = np.zeros(T)
        for t in range(1, T):
            z[t] = 0.85 * z[t - 1] + Z[t, 1]
        z = (z - z.mean()) / z.std()
        return 0.6 * z + 0.6 * lag(2, 11) + e
    v = np.zeros(T)
    for t in range(1, T):
        v[t] = 0.95 * v[t - 1] + np.sqrt(1 - 0.95 ** 2) * e[t]
    return v
