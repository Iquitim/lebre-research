#!/usr/bin/env python3
"""reproduce_smoke.py — fast end-to-end check that the v0.52-r1 results can still be regenerated from this repository.

Stages (each reports PASS / FAIL / SKIP; SKIP means a required artifact outside git is absent — see docs/research/ARTIFACTS_MANIFEST.tsv):
  1 config    configs/lebre_v052_canonical.json equals the frozen canonical configuration.
  2 model     the frozen LEBRE v0.52 re-run on reserve-3 series reproduces the saved predictions BIT FOR BIT
              (needs data/external_v052 and experiments/LEBRE-V0.52-HELDOUT-03/preds/*.npz).
  3 analysis  the pre-registered reserve-3 analysis, re-run in a temporary copy, reproduces RESERVA3_TABLE.csv
              (needs the preds/fm/mcu outputs of reserve 3).
  4 cport     the C99 port (float64 build, rebuilt with zig cc if available) reproduces the Python decisions on one
              development series (needs ziglang and data/external_v052).
Usage: python scripts/reproduce_smoke.py [--series N]   (default N = 2: first CAMELS-BR and first BDG2 series of reserve 3)"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "experiments"
PROTO, EXT1, H3 = E / "LEBRE-V0.52-PROTO-01", E / "LEBRE-V0.52-EXT-01", E / "LEBRE-V0.52-HELDOUT-03"
for p in (ROOT, PROTO, EXT1, H3):
    sys.path.insert(0, str(p))
RESULTS = {}


def report(stage, status, msg=""):
    RESULTS[stage] = status
    print(f"[{status:4s}] {stage}: {msg}", flush=True)


def stage_config():
    import heldout2_cfg as CFG                      # asserts equality with the frozen definition on import
    cfg = json.load(open(ROOT / "configs" / "lebre_v052_canonical.json", encoding="utf-8"))["config"]
    report("1 config", "PASS" if cfg == CFG.CANONICAL else "FAIL", "canonical configuration")


def stage_model(n):
    R = json.load(open(H3 / "RESERVA3.json", encoding="utf-8"))
    tasks = [f"camels:{g}" for g in R["camels_br"][:(n + 1) // 2]] + [f"bdg2:{m}" for m in R["bdg2"][:n // 2]]
    try:
        import comp_dev as C
        import data_v052 as D
        import heldout2_cfg as CFG
        from lebre_v052h import LebreV052H
    except Exception as ex:                          # noqa: BLE001
        return report("2 model", "SKIP", f"import failed: {ex}")
    for t in tasks:
        f = H3 / "preds" / (t.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")
        if not f.exists():
            return report("2 model", "SKIP", f"missing artifact {f.relative_to(ROOT)}")
        try:
            d = D.load(t, final=True)
        except Exception as ex:                      # noqa: BLE001
            return report("2 model", "SKIP", f"data for {t} unavailable: {ex}")
        X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
        m = LebreV052H(d=X.shape[1], season=s, **dict(CFG.CANONICAL, season2=168 if t.startswith("bdg2") else None))
        p = np.array([m.step(Xs[i], float(y[i]) if np.isfinite(y[i]) else None, quarantine=bool(qu[i])) for i in range(len(y))])
        ref = np.load(f)["V052_PY"]
        same = np.array_equal(np.nan_to_num(p, nan=-1e300), np.nan_to_num(ref, nan=-1e300))
        print(f"       {t}: {len(y)} steps, bit-identical = {same}", flush=True)
        if not same:
            return report("2 model", "FAIL", f"{t} differs (max |diff| {np.nanmax(np.abs(p - ref)):.3g})")
    report("2 model", "PASS", f"{len(tasks)} reserve-3 series reproduced bit for bit")


def stage_analysis():
    need = [H3 / "preds", H3 / "fm", H3 / "mcu"]
    if not all(p.exists() and any(p.iterdir()) for p in need):
        return report("3 analysis", "SKIP", "reserve-3 outputs (preds/fm/mcu) not present")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for p in need:
            shutil.copytree(p, tmp / p.name)
        shutil.copy(H3 / "heldout3_analysis.py", tmp)
        r = subprocess.run([sys.executable, str(tmp / "heldout3_analysis.py")], capture_output=True, text=True,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if r.returncode:
            return report("3 analysis", "FAIL", r.stderr[-400:])
        import pandas as pd
        a = pd.read_csv(tmp / "RESERVA3_TABLE.csv"); b = pd.read_csv(H3 / "RESERVA3_TABLE.csv")
        num = a.select_dtypes("number").columns
        ok = a.drop(columns=num).equals(b.drop(columns=num)) and np.allclose(a[num].values, b[num].values, equal_nan=True, rtol=0, atol=1e-12)
    report("3 analysis", "PASS" if ok else "FAIL", "RESERVA3_TABLE.csv regenerated" + ("" if ok else " with differences"))


def stage_cport():
    try:
        import ziglang  # noqa: F401
    except ImportError:
        return report("4 cport", "SKIP", "ziglang not installed (pip install ziglang==0.16.0)")
    try:
        import comp_dev as C
        import data_v052 as D
        import heldout2_cfg as CFG
        from lebre_v052h import LebreV052H
        d = D.load("ons:ITUTINGA")
    except Exception as ex:                          # noqa: BLE001
        return report("4 cport", "SKIP", f"development data unavailable: {ex}")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:     # the loaded DLL cannot be deleted on Windows
        src = EXT1 / "lebre_c"
        dll = Path(tmp) / "lebre052_f64.dll"
        r = subprocess.run([sys.executable, "-m", "ziglang", "cc", "-O2", "-std=c99", "-shared", "-o", str(dll),
                            str(src / "lebre052.c"), str(src / "api.c")], capture_output=True, text=True)
        if r.returncode:
            return report("4 cport", "FAIL", r.stderr[-400:])
        import equiv_test as EQ
        X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
        m = LebreV052H(d=X.shape[1], season=s, **dict(CFG.CANONICAL, season2=None))
        for t in range(len(y)):
            m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        ev_py = [(e[0], EQ.KIND[e[2]], EQ.key_c(e[3]), (EQ.key_c(e[4])[0], EQ.key_c(e[4])[1], 0, 0) if e[4] else (0, 0, 0, 0))
                 for e in m.events if e[1] == "accepted"]
        _, ev_c, ov = EQ.run_c(str(dll), Xs, np.where(np.isfinite(y), y, np.nan), qu.astype(int), s, None)
    ok = ev_c == ev_py and not ov
    report("4 cport", "PASS" if ok else "FAIL", f"float64 C build: {len(ev_py)} accepted changes, identical = {ev_c == ev_py}")


if __name__ == "__main__":
    n = int(sys.argv[sys.argv.index("--series") + 1]) if "--series" in sys.argv else 2
    stage_config(); stage_model(n); stage_analysis(); stage_cport()
    fails = [k for k, v in RESULTS.items() if v == "FAIL"]
    print("RESULT:", "FAIL " + ", ".join(fails) if fails else "PASS (" + ", ".join(f"{k.split()[1]}={v}" for k, v in RESULTS.items()) + ")")
    sys.exit(1 if fails else 0)
