"""load04.py — loaders for BENCH-04 (real data only; Brazilian + international).

Every task returns (X, y, split, names, season, j):
  X[t] = information available before y[t] (all variables at t-1, target included), raw units;
  y[t] = target at t; split = None (test starts at 0.30 T); names = column names of X; season = period or None; j = column of X holding the target (y[t-1]).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "external_bench03"))
from tsf import read_tsf  # noqa: E402

CAP = 50000


def _frame_to_task(df, target, season):
    df = df.astype(float).ffill().bfill()
    V = df.to_numpy()[:CAP + 1]
    j = list(df.columns).index(target)
    return V[:-1], V[1:, j], None, list(df.columns), season, j


def _ons_carga(sub):
    frames = [pd.read_csv(os.path.join(D, f"CURVA_CARGA_{y}.csv"), sep=";") for y in (2023, 2024)]
    df = pd.concat(frames)
    df = df[df.id_subsistema == sub].copy()
    df["t"] = pd.to_datetime(df.din_instante)
    s = df.set_index("t").val_cargaenergiahomwmed.sort_index()
    s = s[~s.index.duplicated()].asfreq("h")
    return s.to_frame("carga")


def _ons_balanco(sub):
    frames = [pd.read_csv(os.path.join(D, f"BALANCO_{y}.csv"), sep=";") for y in (2023, 2024)]
    df = pd.concat(frames)
    df = df[df.id_subsistema == sub].copy()
    df["t"] = pd.to_datetime(df.din_instante)
    cols = ["val_gereolica", "val_gersolar", "val_gerhidraulica", "val_gertermica", "val_carga", "val_intercambio"]
    df = df.set_index("t")[cols].sort_index()
    df = df[~df.index.duplicated()].asfreq("h")
    df.columns = [c.replace("val_", "") for c in cols]
    return df


def _bcb_usd():
    rows = []
    for f in ("bcb_usd_1.json", "bcb_usd_2.json"):
        rows += json.load(open(os.path.join(D, f), encoding="utf-8"))
    s = pd.Series([float(r["valor"]) for r in rows], index=pd.to_datetime([r["data"] for r in rows], dayfirst=True))
    s = s[~s.index.duplicated()].sort_index()
    return s.to_frame("usdbrl")


def _airq():
    df = pd.read_csv(os.path.join(D, "airquality", "AirQualityUCI.csv"), sep=";", decimal=",")
    df = df.dropna(how="all", axis=1).dropna(subset=["Date"])
    df = df.drop(columns=["Date", "Time", "NMHC(GT)"])       # NMHC(GT) is ~90 % missing
    return df.replace(-200, np.nan)


def _tetouan():
    df = pd.read_csv(os.path.join(D, "tetouan", "Tetuan City power consumption.csv"))
    return df.drop(columns=["DateTime"])


def _bike():
    df = pd.read_csv(os.path.join(D, "bike", "hour.csv"))
    return df[["hr", "workingday", "weathersit", "temp", "atemp", "hum", "windspeed", "cnt"]]


def _oiko():
    s = read_tsf(os.path.join(D, "oikolab", "oikolab_weather_dataset.tsf"))
    names = ["temperature", "dewpoint", "wind_speed", "pressure", "humidity", "solar_rad", "thermal_rad", "cloud"]
    return pd.DataFrame({n: v for n, (_, v) in zip(names, s)})


TASKS = {
    # Brazilian data (ONS = Operador Nacional do Sistema Eletrico; BCB = Banco Central do Brasil)
    "BR1_ONS_Carga_SECO": lambda: _frame_to_task(_ons_carga("SE"), "carga", 24),
    "BR2_ONS_Carga_N": lambda: _frame_to_task(_ons_carga("N"), "carga", 24),
    "BR3_ONS_Eolica_NE": lambda: _frame_to_task(_ons_balanco("NE"), "gereolica", 24),
    "BR4_ONS_Solar_NE": lambda: _frame_to_task(_ons_balanco("NE"), "gersolar", 24),
    "BR5_BCB_USDBRL": lambda: _frame_to_task(_bcb_usd(), "usdbrl", None),
    # international real data
    "R1_UCI_AirQuality_CO": lambda: _frame_to_task(_airq(), "CO(GT)", 24),
    "R2_UCI_Tetouan_Z1": lambda: _frame_to_task(_tetouan(), "Zone 1 Power Consumption", 144),
    "R3_UCI_BikeSharing": lambda: _frame_to_task(_bike(), "cnt", 24),
    "R4_Oikolab_Temp": lambda: _frame_to_task(_oiko(), "temperature", 24),
    "R5_Oikolab_Wind": lambda: _frame_to_task(_oiko()[["wind_speed"]], "wind_speed", 24),
}

_CACHE = {}


def load(task):
    if task not in _CACHE:
        _CACHE[task] = TASKS[task]()
    return _CACHE[task]


if __name__ == "__main__":
    for t in TASKS:
        X, y, _, n, s, j = load(t)
        print(f"{t:24s} T={len(y):6d} D={X.shape[1]:2d} s={s} nan={int(np.isnan(X).sum())} "
              f"y[mean={y.mean():.3g} sd={y.std():.3g}] lag1-corr={np.corrcoef(y[1:], y[:-1])[0, 1]:.4f} cols={n}")
