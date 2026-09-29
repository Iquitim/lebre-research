"""load05.py — HELD-OUT set for LEBRE v0.5 (never used in any stage). Same conventions as load04:
returns (X, y, split, names, season, j); X[t] = all variables at t-1 (target included), y[t] = target at t."""
import json
import os
import sys

import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "external_bench03")); sys.path.insert(0, os.path.join(D, "..", "external_bench04"))
from tsf import read_tsf  # noqa: E402
from load04 import _frame_to_task  # noqa: E402

D3 = os.path.join(D, "..", "external_bench03")


def _carga(sub):
    df = pd.concat([pd.read_csv(os.path.join(D, f"CURVA_CARGA_{y}.csv"), sep=";") for y in (2021, 2022)])
    df = df[df.id_subsistema == sub].copy(); df["t"] = pd.to_datetime(df.din_instante)
    s = df.set_index("t").val_cargaenergiahomwmed.sort_index(); s = s[~s.index.duplicated()].asfreq("h")
    return s.to_frame("carga")


def _balanco(sub):
    df = pd.concat([pd.read_csv(os.path.join(D, f"BALANCO_{y}.csv"), sep=";") for y in (2021, 2022)])
    df = df[df.id_subsistema == sub].copy(); df["t"] = pd.to_datetime(df.din_instante)
    cols = ["val_gereolica", "val_gersolar", "val_gerhidraulica", "val_gertermica", "val_carga", "val_intercambio"]
    df = df.set_index("t")[cols].sort_index(); df = df[~df.index.duplicated()].asfreq("h")
    df.columns = [c.replace("val_", "") for c in cols]
    return df


def _eur():
    rows = []
    for f in ("bcb_eur_1.json", "bcb_eur_2.json"):
        rows += json.load(open(os.path.join(D, f), encoding="utf-8"))
    s = pd.Series([float(r["valor"]) for r in rows], index=pd.to_datetime([r["data"] for r in rows], dayfirst=True))
    return s[~s.index.duplicated()].sort_index().to_frame("eurbrl")


def _monash(file, idx):
    return pd.DataFrame({"v": read_tsf(os.path.join(D3, file))[idx][1]})


def _elecdemand():
    s = read_tsf(os.path.join(D, "elecdemand_dataset.tsf"))
    return pd.DataFrame({"v": s[0][1]})


TASKS = {
    "N1_ONS_Carga_SECO_2021_22": lambda: _frame_to_task(_carga("SE"), "carga", 24),
    "N2_ONS_Hidro_N_2021_22": lambda: _frame_to_task(_balanco("N"), "gerhidraulica", 24),
    "N3_ONS_Termica_SIN_2021_22": lambda: _frame_to_task(_balanco("SIN"), "gertermica", 24),
    "N4_ONS_Eolica_NE_2021_22": lambda: _frame_to_task(_balanco("NE"), "gereolica", 24),
    "N5_BCB_EURBRL": lambda: _frame_to_task(_eur(), "eurbrl", None),
    "N6_Monash_ElecDemand_VIC": lambda: _frame_to_task(_elecdemand(), "v", 48),
    "N7_Monash_AusElec_S3": lambda: _frame_to_task(_monash("australian_electricity_demand_dataset.tsf", 2), "v", 48),
    "N8_Monash_Pedestrian_S3": lambda: _frame_to_task(_monash("pedestrian_counts_dataset.tsf", 2), "v", 24),
    "N9_Monash_Solar10min_S3": lambda: _frame_to_task(_monash("solar_10_minutes_dataset.tsf", 2), "v", 144),
    "N10_Monash_KDDCup_S3": lambda: _frame_to_task(_monash("kdd_cup_2018_dataset_without_missing_values.tsf", 2), "v", 24),
}
_C = {}


def load(task):
    if task not in _C:
        _C[task] = TASKS[task]()
    return _C[task]


if __name__ == "__main__":
    for t in TASKS:
        X, y, _, n, s, j = load(t)
        print(f"{t:28s} T={len(y):6d} D={X.shape[1]} s={s} nan={int(np.isnan(X).sum())} target={n[j]}")
