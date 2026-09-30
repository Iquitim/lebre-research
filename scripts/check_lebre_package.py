#!/usr/bin/env python3
"""check_lebre_package.py — checks that the installable package (packages/lebre) reproduces, bit for bit, the published
reserve-3 predictions of the frozen LEBRE v0.52 on real never-seen series, starting from the RAW inputs (the package
standardises them itself). Needs data/external_v052 and experiments/LEBRE-V0.52-HELDOUT-03/preds (out of git).
Usage: python scripts/check_lebre_package.py [N_PER_GROUP]   (default 2)"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
H3 = ROOT / "experiments" / "LEBRE-V0.52-HELDOUT-03"
for p in (ROOT / "packages" / "lebre" / "src", ROOT, ROOT / "experiments" / "LEBRE-V0.52-PROTO-01"):
    sys.path.insert(0, str(p))
import data_v052 as D  # noqa: E402
from lebre import Lebre  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
R = json.load(open(H3 / "RESERVA3.json", encoding="utf-8"))
tasks = [f"camels:{g}" for g in R["camels_br"][:n]] + [f"bdg2:{m}" for m in R["bdg2"][:n]]
bad = 0
for t in tasks:
    d = D.load(t, final=True); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]
    m = Lebre(X.shape[1], season=s, season2=168 if t.startswith("bdg2") else None)
    f = np.array([m.step(X[i], float(y[i]) if np.isfinite(y[i]) else None, quarantine=bool(qu[i])).value for i in range(len(y))])
    ref = np.load(H3 / "preds" / (t.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz"))["V052_PY"]
    same = np.array_equal(f, ref); bad += not same
    print(f"{t}: {len(y)} steps, structure {m.structure}, bit-identical = {same}")
print("RESULT:", "PASS" if not bad else f"FAIL ({bad})"); sys.exit(1 if bad else 0)
