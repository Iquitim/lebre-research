"""dev_guard.py — DEV diagnosis for v0.4.5 on previously used real data only (BENCH-02, BENCH-03 series 1, external_v03).
Arms: V032, V042 (plain clip), V042_NOCLIP, V045 (leverage-normalised guard). 10 start offsets; fixed test window."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"),
          os.path.join(ROOT, "data", "external_bench03"), HERE, ROOT):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from lebre_v045 import LebreV045  # noqa: E402
from tsf import read_tsf  # noqa: E402

D03 = os.path.join(ROOT, "data", "external_bench03"); DV3 = os.path.join(ROOT, "data", "external_v03")
MONASH = {"M_AusElectricity": "australian_electricity_demand_dataset", "M_Pedestrian": "pedestrian_counts_dataset",
          "M_KDDCup2018": "kdd_cup_2018_dataset_without_missing_values", "M_Solar10min": "solar_10_minutes_dataset",
          "M_USBirths": "us_births_dataset"}
B02 = ["A_ETTh1", "A_ETTm1", "A_ECL", "A_Traffic", "A_Exchange", "A_JenaWeather"]
XT = ["X1_Appliances", "X2_BeijingPM25", "X3_MetroTraffic"]
TASKS = B02 + list(MONASH) + XT
OFFSETS = list(range(0, 500, 50))
ARMS = {"V032": lambda d: B.LebreStep(d).m, "V042": lambda d: LebreV042(d=d),
        "V042_NOCLIP": lambda d: LebreV042(d=d, clip=False), "V045_EVONLY": lambda d: LebreV045(d=d, quarantine_learn="none"),
        "V045_CUR": lambda d: LebreV045(d=d, quarantine_learn="current"), "V045_WIN": lambda d: LebreV045(d=d, quarantine_learn="window")}


def load(task):
    if task in MONASH:
        v = read_tsf(os.path.join(D03, MONASH[task] + ".tsf"))[0][1][:50000]
        return v[:-1, None], v[1:]
    if task.startswith("X"):
        if task == "X1_Appliances":
            df = pd.read_csv(os.path.join(DV3, "energydata_complete.csv"))
            f = ["lights"] + [f"T{i}" for i in range(1, 10)] + [f"RH_{i}" for i in range(1, 10)] + \
                ["T_out", "Press_mm_hg", "RH_out", "Windspeed", "Visibility", "Tdewpoint"]
            return df[f].values.astype(float), df["Appliances"].values.astype(float)
        if task == "X2_BeijingPM25":
            df = pd.read_csv(os.path.join(DV3, "PRSA_data_2010.1.1-2014.12.31.csv")); df = df[df["pm2.5"].notna()]
            return df[["DEWP", "TEMP", "PRES", "Iws", "Is", "Ir", "hour"]].values.astype(float), df["pm2.5"].values.astype(float)
        df = pd.read_csv(os.path.join(DV3, "Metro_Interstate_Traffic_Volume.csv.gz"))
        df["hour"] = pd.to_datetime(df["date_time"]).dt.hour
        return df[["temp", "rain_1h", "snow_1h", "clouds_all", "hour"]].values.astype(float), df["traffic_volume"].values.astype(float)
    X, y, _ = B.load(task, 0)
    return X[:50000], y[:50000]


def run(args):
    task, arm, off = args
    X, y = load(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1]); m = ARMS[arm](X.shape[1]); e = []
    for i in range(off, T):
        p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i])
        if i >= ts:
            e.append((y[i] - p) ** 2)
    ok = bool(np.all(np.isfinite(e)))
    return {"task_id": task, "arm": arm, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if ok else np.inf}


if __name__ == "__main__":
    jobs = [(t, a, o) for t in TASKS for a in ARMS for o in OFFSETS]
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(run, jobs, chunksize=2)))
    df.to_csv(os.path.join(HERE, "DEV_GUARD.csv"), index=False)
    med = df.groupby(["task_id", "arm"]).nmse.median().unstack()
    spread = df.groupby(["task_id", "arm"]).nmse.agg(lambda s: s.quantile(.9) / s.quantile(.1)).unstack()
    w = df.pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
    pd.set_option("display.width", 220)
    print("mediana (10 offsets):\n" + med.round(4).to_string())
    print("\ninstabilidade p90/p10:\n" + spread.round(2).to_string())
    for a in [k for k in ARMS if k != "V032"]:
        r = np.log(w[a] / w.V032)
        print(f"{a}/V032 geo pareado: {np.exp(r.mean()):.3f}; pior tarefa (mediana): {np.exp(r.groupby(level=0).median().max()):.3f}")
