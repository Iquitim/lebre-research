"""load051.py — HELD-OUT set for LEBRE v0.51 (series never evaluated by any stage). Conventions of load04/load05:
returns (X, y, split, names, season, j); X[t] = all variables at t-1 (target included), y[t] = target at t."""
import json
import os
import sys

import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "external_bench03")); sys.path.insert(0, os.path.join(D, "..", "external_bench04"))
from tsf import read_tsf  # noqa: E402
from load04 import _frame_to_task  # noqa: E402

D3 = os.path.join(D, "..", "external_bench03")


def _balanco(sub):
    df = pd.concat([pd.read_csv(os.path.join(D, f"BALANCO_{y}.csv"), sep=";") for y in (2019, 2020)])
    df = df[df.id_subsistema == sub].copy(); df["t"] = pd.to_datetime(df.din_instante)
    cols = ["val_gereolica", "val_gersolar", "val_gerhidraulica", "val_gertermica", "val_carga", "val_intercambio"]
    df = df.set_index("t")[cols].sort_index(); df = df[~df.index.duplicated()].asfreq("h")
    df.columns = [c.replace("val_", "") for c in cols]
    return df


def _gbp():
    rows = []
    for f in ("bcb_gbp_1.json", "bcb_gbp_2.json"):
        rows += json.load(open(os.path.join(D, f), encoding="utf-8"))
    s = pd.Series([float(r["valor"]) for r in rows], index=pd.to_datetime([r["data"] for r in rows], dayfirst=True))
    return s[~s.index.duplicated()].sort_index().to_frame("gbpbrl")


def _monash(file, idx):
    return pd.DataFrame({"v": read_tsf(os.path.join(D3, file))[idx][1]})


TASKS = {
    "Q1_ONS_Carga_SIN_2019_20": lambda: _frame_to_task(_balanco("SIN"), "carga", 24),
    "Q2_ONS_Hidro_SE_2019_20": lambda: _frame_to_task(_balanco("SE"), "gerhidraulica", 24),
    "Q3_ONS_Hidro_S_2019_20": lambda: _frame_to_task(_balanco("S"), "gerhidraulica", 24),
    "Q4_ONS_Eolica_SIN_2019_20": lambda: _frame_to_task(_balanco("SIN"), "gereolica", 24),
    "Q5_BCB_GBPBRL": lambda: _frame_to_task(_gbp(), "gbpbrl", None),
    "Q6_Monash_AusElec_S4": lambda: _frame_to_task(_monash("australian_electricity_demand_dataset.tsf", 3), "v", 48),
    "Q7_Monash_Pedestrian_S4": lambda: _frame_to_task(_monash("pedestrian_counts_dataset.tsf", 3), "v", 24),
    "Q8_Monash_Solar10min_S4": lambda: _frame_to_task(_monash("solar_10_minutes_dataset.tsf", 3), "v", 144),
    "Q9_Monash_KDDCup_S4": lambda: _frame_to_task(_monash("kdd_cup_2018_dataset_without_missing_values.tsf", 3), "v", 24),
    "Q10_Monash_AusElec_S5": lambda: _frame_to_task(_monash("australian_electricity_demand_dataset.tsf", 4), "v", 48),
}
_C = {}


def load(task):
    if task not in _C:
        _C[task] = TASKS[task]()
    return _C[task]


if __name__ == "__main__":
    import numpy as np
    for t in TASKS:
        X, y, _, n, s, j = load(t)
        print(f"{t:28s} T={len(y):6d} D={X.shape[1]} s={s} nan={int(np.isnan(X).sum())} target={n[j]}")
