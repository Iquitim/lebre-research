#!/usr/bin/env python3
"""semi_synth2.py — NEW semi-synthetic tasks for the evaluation of the hierarchical input-level v0.52, declared on 27/09/2026
BEFORE implementing it (the tasks of semi_synth.py were used to design it and can no longer judge it).
Same REAL inputs (outflows of 5 plants of the development river Grande, 3-h), new declared structures, new seeds:

  SN0 null            y = e
  SN1 distributed     y = 0.5 x2(t-2) + 0.5 x2(t-5) + e
  SN2 two inputs      y = 0.8 x3(t-9) + 0.6 x1(t-1) + e
  SN3 storage + lag   z = 0.9 z(t-1) + 0.1 x4(t) (rescaled to unit variance);  y = z + 0.5 x0(t-15) + e
  SN4 null, AR target y = v,  v = 0.9 v(t-1) + sqrt(1 - 0.81) e      (no input relation; autocorrelated target)

Inputs standardised with full-sample mean/sd for GENERATION only; models get raw inputs through the causal scaler.
e ~ N(0, 1); seeds 6201-6203 (not used before). Truth at the input level (x index = column; self = index 5).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401  (same real inputs)

SEEDS = [6201, 6202, 6203]
TRUTH = {"SN0": set(), "SN1": {("in", 2)}, "SN2": {("in", 3), ("in", 1)}, "SN3": {("in", 4), ("in", 0)}, "SN4": set()}
# atom-level truth (lags / low-pass), for reporting the recovered response
TRUTH_LAGS = {"SN1": {(2, 2), (2, 5)}, "SN2": {(3, 9), (1, 1)}, "SN3": {(0, 15)}}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task == "SN0":
        return e
    if task == "SN1":
        return 0.5 * lag(2, 2) + 0.5 * lag(2, 5) + e
    if task == "SN2":
        return 0.8 * lag(3, 9) + 0.6 * lag(1, 1) + e
    if task == "SN3":
        z = np.zeros(T)
        for t in range(1, T):
            z[t] = 0.9 * z[t - 1] + 0.1 * Z[t, 4]
        z = (z - z.mean()) / z.std()
        return z + 0.5 * lag(0, 15) + e
    v = np.zeros(T)
    for t in range(1, T):
        v[t] = 0.9 * v[t - 1] + np.sqrt(1 - 0.81) * e[t]
    return v
