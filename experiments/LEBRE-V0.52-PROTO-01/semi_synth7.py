#!/usr/bin/env python3
"""semi_synth7.py — evaluation set #7 (smooth-input discovery and cost peaks), declared on 27/09/2026 BEFORE implementing.
Same REAL inputs (outflows of 5 plants of the development river Grande, 3-h), new structures focused on SMOOTH inputs
with MID/LONG lags (the failure of SU2/SR1), new seeds:

  SW0 null                          y = e
  SW1 smooth, mid lag               y = 0.6 x2(t-12) + e
  SW2 smooth, long lag (grouped)    y = 0.6 x1(t-20) + e                  ({x0, x1} equivalence group)
  SW3 two smooth inputs             y = 0.5 x2(t-6) + 0.5 x4(t-18) + e
  SW4 input + AR noise              y = 0.6 x3(t-10) + v,  v = 0.8 v(t-1) + 0.6 e

Seeds 6801-6803; pure synthetics 9701-9703; NULL BATCH (criterion 7): white 6901-6915, heavy-tailed 6916-6930.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from semi_synth import inputs  # noqa: E402,F401
from semi_synth4 import groups  # noqa: E402,F401

SEEDS = [6801, 6802, 6803]
NULL_SEEDS = {"white": list(range(6901, 6916)), "heavy": list(range(6916, 6931))}
TRUTH = {"SW0": set(), "SW1": {("in", 2)}, "SW2": {("in", 1)}, "SW3": {("in", 2), ("in", 4)}, "SW4": {("in", 3)}}


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task in ("SW0", "white"):
        return e
    if task == "heavy":
        return rng.standard_t(3, size=T) / np.sqrt(3.0)
    if task == "SW1":
        return 0.6 * lag(2, 12) + e
    if task == "SW2":
        return 0.6 * lag(1, 20) + e
    if task == "SW3":
        return 0.5 * lag(2, 6) + 0.5 * lag(4, 18) + e
    v = np.zeros(T)
    for t in range(1, T):
        v[t] = 0.8 * v[t - 1] + 0.6 * e[t]
    return 0.6 * lag(3, 10) + v
