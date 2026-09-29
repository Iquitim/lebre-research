#!/usr/bin/env python3
"""semi_synth4.py — evaluation set #4 (cost / equivalence groups / weekly memory iteration), declared on 27/09/2026 BEFORE
implementing it. Same REAL inputs (outflows of 5 plants of the development river Grande, 3-h), new structures, new seeds:

  SQ0 null                      y = e
  SQ1 one input (in a group)    y = 0.7 x1(t-4) + e          (x1 ~ x0, corr 0.98: {x0, x1} is an equivalence group)
  SQ2 two inputs                y = 0.6 x2(t-3) + 0.5 x4(t-14) + e
  SQ3 input + AR noise          y = 0.7 x3(t-7) + v,  v = 0.8 v(t-1) + 0.6 e
  SQ4 null in the mean          y = e * (0.5 + 0.5 |x0(t)|) / c   (x0 changes the VARIANCE only; no gain in the mean)

e ~ N(0, 1); seeds 6401-6403 (not used before). Pure synthetics of the same measurement: seeds 9401-9403.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401

SEEDS = [6401, 6402, 6403]
TRUTH = {"SQ0": set(), "SQ1": {("in", 1)}, "SQ2": {("in", 2), ("in", 4)}, "SQ3": {("in", 3)}, "SQ4": set()}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task == "SQ0":
        return e
    if task == "SQ1":
        return 0.7 * lag(1, 4) + e
    if task == "SQ2":
        return 0.6 * lag(2, 3) + 0.5 * lag(4, 14) + e
    if task == "SQ3":
        v = np.zeros(T)
        for t in range(1, T):
            v[t] = 0.8 * v[t - 1] + 0.6 * e[t]
        return 0.7 * lag(3, 7) + v
    s = e * (0.5 + 0.5 * np.abs(Z[:, 0]))
    return s / s.std()


def groups(X, thr=0.95):
    """equivalence groups of inputs: full-sample |corr| >= thr (used only by the evaluation criteria)"""
    R = np.abs(np.corrcoef(X.T)); d = X.shape[1]
    return {i: {j for j in range(d) if R[i, j] >= thr} for i in range(d)}
