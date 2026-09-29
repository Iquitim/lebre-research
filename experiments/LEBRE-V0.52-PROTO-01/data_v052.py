"""data_v052.py — loaders for the v0.52 real input-driven tasks.

Guard: only DEVELOPMENT tasks of SPLIT_V052.json can be loaded unless final=True (reserved for the pre-registered run).
Pre-declared choices (SPLIT_RULES.md and this header, fixed before modelling):
  ONS      target = inflow (val_vazaoafluente) of the downstream plant; inputs = outflow (val_vazaodefluente) of the direct
           upstream plant(s); 3-hour means (>= 2 of 3 hours present, else missing); 2015-2025; season s = 8 (daily cycle).
  CAMELS   target = streamflow_mm; inputs = p_mswep, aet_gleam, tmean_era5land; daily; season None.
  BDG2     target = cleaned heating/cooling meter; inputs = airTemperature, dewTemperature of the site; hourly; season 24.
  Silverbox, Cascaded Tanks (dev only): single input/output, season None.
Missing values are returned as NaN (target) or forward-filled causally with a quarantine flag (inputs); negative flows -> NaN.
"""
import io
import json
import os
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "data", "external_v052")
SPLIT = json.load(open(os.path.join(ROOT, "experiments", "LEBRE-V0.52-DATA-01", "SPLIT_V052.json"), encoding="utf-8"))


def dev_tasks():
    t = [f"ons:{x['target']}" for x in SPLIT["ons"]["development"]]
    t += [f"camels:{g}" for g in SPLIT["camels_br"]["development"]]
    t += [f"bdg2:{m}" for m in SPLIT["bdg2"]["development"]]
    return t + ["silverbox", "tanks:est", "tanks:val"]


def _guard(task, final):
    if final or task in dev_tasks():
        return
    raise PermissionError(f"{task} is not a development task; held-out data may only be loaded in the final pre-registered run")


def _spike_filter(v, window, ratio=20.0):
    """causal validity rule (added 26/09/2026 after dev inspection, before any held-out access): a value is invalid if it
    exceeds `ratio` x the 90th percentile of the series' own valid values in the previous `window` steps."""
    s = pd.Series(v, dtype=float)
    q90 = s.rolling(window, min_periods=max(4, window // 4)).quantile(0.9).shift(1)
    bad = (q90 > 0) & (s > ratio * q90)
    out = s.to_numpy().copy(); out[bad.to_numpy()] = np.nan
    return out


def _jump_filter(v, ratio=10.0, med_ratio=5.0, window=56):
    """causal validity rule for ONS flows (added 26/09/2026 after dev inspection, before any held-out access): a 3-h value
    is a recording error if it exceeds BOTH `ratio` x the last valid value AND `med_ratio` x the median of the previous
    `window` blocks (a large reservoir's flow does not jump tenfold in 3 h; the median condition prevents a single low
    value from locking the series)."""
    s_ = pd.Series(v, dtype=float)
    med = s_.rolling(window, min_periods=max(4, window // 4)).median().shift(1).to_numpy()
    out = s_.to_numpy().copy(); last = np.nan
    for t in range(len(out)):
        x = out[t]
        if not np.isfinite(x):
            continue
        if np.isfinite(last) and last > 0 and np.isfinite(med[t]) and med[t] > 0 and x > ratio * last and x > med_ratio * med[t]:
            out[t] = np.nan
        else:
            last = x
    return out


def _ffill_inputs(X):
    """causal forward fill; returns filled X and a boolean 'quarantine' flag where any input was missing."""
    miss = np.isnan(X).any(axis=1)
    Xf = pd.DataFrame(X).ffill().fillna(0.0).to_numpy()
    return Xf, miss


# ------------------------------------------------------------------ ONS
_ONS_CACHE = {}


def _ons_hourly(names):
    key = tuple(sorted(names))
    if key in _ONS_CACHE:
        return _ONS_CACHE[key]
    cols = ["nom_reservatorio", "din_instante", "val_vazaoafluente", "val_vazaodefluente"]
    parts = []
    for y in range(2015, 2026):
        for m in range(1, 13):
            p = os.path.join(D, "ons_hourly", f"DADOS_HIDROLOGICOS_HO_{y}_{m:02d}.parquet")
            if os.path.exists(p):
                d = pd.read_parquet(p, columns=cols)
                parts.append(d[d.nom_reservatorio.isin(names)])
    df = pd.concat(parts, ignore_index=True)
    df = df[(df.din_instante >= "2015-01-01") & (df.din_instante <= "2025-12-31 23:00")]
    _ONS_CACHE[key] = df
    return df


def _agg3h(s, idx):
    s = s.reindex(idx)
    s[s < 0] = np.nan
    g = s.groupby(np.arange(len(s)) // 3)
    m = g.mean(); n = g.count()
    m[n < 2] = np.nan
    return m.to_numpy()


def load_ons(target, final=False):
    _guard(f"ons:{target}", final)
    rec = next(x for x in SPLIT["ons"]["development"] + SPLIT["ons"]["held_out"] if x["target"] == target)
    names = [target] + rec["inputs"]
    df = _ons_hourly(names)
    idx = pd.date_range("2015-01-01", "2025-12-31 23:00", freq="h")
    piv_a = df.pivot_table(index="din_instante", columns="nom_reservatorio", values="val_vazaoafluente")
    piv_d = df.pivot_table(index="din_instante", columns="nom_reservatorio", values="val_vazaodefluente")
    y = _jump_filter(_spike_filter(_agg3h(piv_a[target], idx), 56))
    X = np.column_stack([_jump_filter(_spike_filter(_agg3h(piv_d[u], idx), 56)) for u in rec["inputs"]])
    X, q = _ffill_inputs(X)
    return {"X": X, "y": y, "quarantine": q, "season": 8, "names": [f"defluente {u}" for u in rec["inputs"]],
            "task": f"ons:{target}", "inputs_upstream": rec["inputs"], "river": rec["river"]}


# ------------------------------------------------------------------ CAMELS-BR
def _camels_file(zipname, folder, gid, kind):
    z = zipfile.ZipFile(os.path.join(D, "camels_br", zipname))
    t = pd.read_csv(io.BytesIO(z.read(f"{folder}/{gid}_{kind}.txt")), sep=r"\s+")
    t.index = pd.to_datetime(dict(year=t.year, month=t.month, day=t.day))
    return t


def load_camels(gid, final=False):
    _guard(f"camels:{gid}", final)
    q = _camels_file("03_CAMELS_BR_streamflow_selected_catchments.zip", "03_CAMELS_BR_streamflow_selected_catchments", gid, "streamflow")
    p = _camels_file("05_CAMELS_BR_precipitation.zip", "05_CAMELS_BR_precipitation", gid, "precipitation")
    e = _camels_file("06_CAMELS_BR_actual_evapotransp.zip", "06_CAMELS_BR_actual_evapotransp", gid, "actual_evapotransp")
    tt = _camels_file("09_CAMELS_BR_temperature.zip", "09_CAMELS_BR_temperature", gid, "temperature")
    idx = q.index
    y = q.streamflow_mm.reindex(idx).to_numpy(float)
    y[y < 0] = np.nan
    X = np.column_stack([p.p_mswep.reindex(idx), e.aet_gleam.reindex(idx), tt.tmean_era5land.reindex(idx)]).astype(float)
    X, qf = _ffill_inputs(X)
    return {"X": X, "y": y, "quarantine": qf, "season": None, "names": ["precipitação", "evapotranspiração", "temperatura"],
            "task": f"camels:{gid}"}


# ------------------------------------------------------------------ BDG2
_BDG2 = {}


def _bdg2_zip():
    return zipfile.ZipFile(os.path.join(D, "bdg2", "building-data-genome-project-2-v1.0.zip"))


def load_bdg2(meter, final=False):
    _guard(f"bdg2:{meter}", final)
    kind, bid = meter.split(":")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    z = _bdg2_zip()
    if kind not in _BDG2:
        _BDG2[kind] = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0, parse_dates=True)
    if "weather" not in _BDG2:
        _BDG2["weather"] = pd.read_csv(io.BytesIO(z.read(base + "weather/weather.csv")), parse_dates=["timestamp"])
    s = _BDG2[kind][bid]
    site = bid.split("_")[0]
    w = _BDG2["weather"]
    w = w[w.site_id == site].drop_duplicates("timestamp", keep="first").set_index("timestamp").reindex(s.index)  # weather has repeated stamps
    y = s.to_numpy(float)
    y[y < 0] = np.nan
    y = _spike_filter(y, 168)
    X = w[["airTemperature", "dewTemperature"]].to_numpy(float)
    X, qf = _ffill_inputs(X)
    return {"X": X, "y": y, "quarantine": qf, "season": 24, "names": ["temperatura do ar", "ponto de orvalho"], "task": f"bdg2:{meter}"}


# ------------------------------------------------------------------ dev benchmarks
def load_silverbox():
    d = pd.read_csv(os.path.join(ROOT, "data", "external", "silverbox_eval_sn.csv"))
    return {"X": d[["V_in"]].to_numpy(float), "y": d.V_out.to_numpy(float), "quarantine": np.zeros(len(d), bool),
            "season": None, "names": ["V_in"], "task": "silverbox"}


def load_tanks(which):
    z = zipfile.ZipFile(os.path.join(D, "cascaded_tanks", "CascadedTanksFiles.zip"))
    d = pd.read_csv(io.BytesIO(z.read("CascadedTanksFiles/dataBenchmark.csv")))
    u, y = ("uEst", "yEst") if which == "est" else ("uVal", "yVal")
    return {"X": d[[u]].to_numpy(float), "y": d[y].to_numpy(float), "quarantine": np.zeros(len(d), bool),
            "season": None, "names": ["tensão da bomba"], "task": f"tanks:{which}"}


def load(task, final=False):
    if task.startswith("ons:"):
        return load_ons(task[4:], final)
    if task.startswith("camels:"):
        return load_camels(int(task[7:]), final)
    if task.startswith("bdg2:"):
        return load_bdg2(task[5:], final)
    if task == "silverbox":
        return load_silverbox()
    if task.startswith("tanks:"):
        return load_tanks(task[6:])
    raise KeyError(task)
