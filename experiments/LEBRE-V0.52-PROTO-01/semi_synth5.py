#!/usr/bin/env python3
"""semi_synth5.py — evaluation set #5 (replication under the revised cost contract), declared on 27/09/2026 BEFORE the
measurement; the model is the frozen code of measurement #4, unchanged. Same REAL inputs (outflows of 5 plants of the
development river Grande, 3-h), new structures, new seeds:

  SR0 null                      y = e
  SR1 one input, mid lag        y = 0.6 x2(t-9) + e
  SR2 two inputs (one grouped)  y = 0.5 x0(t-1) + 0.5 x3(t-25) + e      ({x0, x1} equivalence group)
  SR3 two-lobed response        y = 0.8 x4(t-2) + 0.4 x4(t-12) + e
  SR4 null, heavy tails         y = t3 / sqrt(3)

e ~ N(0, 1); seeds 6501-6503 (not used before). Pure synthetics of the same measurement: seeds 9501-9503.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401
from semi_synth4 import groups  # noqa: E402,F401

SEEDS = [6501, 6502, 6503]
TRUTH = {"SR0": set(), "SR1": {("in", 2)}, "SR2": {("in", 0), ("in", 3)}, "SR3": {("in", 4)}, "SR4": set()}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task == "SR0":
        return e
    if task == "SR1":
        return 0.6 * lag(2, 9) + e
    if task == "SR2":
        return 0.5 * lag(0, 1) + 0.5 * lag(3, 25) + e
    if task == "SR3":
        return 0.8 * lag(4, 2) + 0.4 * lag(4, 12) + e
    return rng.standard_t(3, size=T) / np.sqrt(3.0)
