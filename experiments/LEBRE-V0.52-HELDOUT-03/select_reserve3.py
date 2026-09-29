#!/usr/bin/env python3
"""select_reserve3.py — RESERVA 3 (27/09/2026): the NEXT positions of the same seeded permutations that built SPLIT_V052
(CAMELS-BR seed 5202: positions 80-109; BDG2 seed 5203: positions 55-84). The script recomputes the eligibility and the
permutation exactly as make_split_v052.py, asserts that the first positions reproduce the development and held-out sets
of SPLIT_V052.json, and checks (by file NAMES only, no values read) that the drawn series exist in the archives.
Nothing about the series' values is inspected here."""
import io
import json
import os
import sys
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.52-DATA-01"))
import make_split_v052 as MS  # noqa: E402

S = json.load(open(os.path.join(ROOT, "experiments", "LEBRE-V0.52-DATA-01", "SPLIT_V052.json"), encoding="utf-8"))
D = MS.D

# CAMELS-BR: same eligibility and permutation
z = zipfile.ZipFile(os.path.join(D, "camels_br", "01_CAMELS_BR_attributes.zip"))
rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")
a = rd("camels_br_human_intervention.txt").merge(rd("camels_br_quality_check.txt"), on="gauge_id")
elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
ids = sorted(elig.gauge_id.astype(int).tolist())
pc = np.random.default_rng(MS.SEED_CAMELS).permutation(ids)
assert sorted(int(x) for x in pc[:10]) == S["camels_br"]["development"]
assert sorted(int(x) for x in pc[10:60]) == S["camels_br"]["held_out"]
cam = [int(x) for x in pc[80:110]]

# BDG2: same eligibility and permutation (reads only coverage/non-zero shares, as the original split did)
zb = zipfile.ZipFile(os.path.join(D, "bdg2", "building-data-genome-project-2-v1.0.zip"))
base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
meters = []
for kind in ("chilledwater", "hotwater", "steam"):
    m = pd.read_csv(io.BytesIO(zb.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
    cov = m.notna().mean(); nz = (m.fillna(0) != 0).mean()
    meters += [f"{kind}:{b}" for b in cov[(cov >= MS.MIN_COV) & (nz >= 0.5)].index]
meters = sorted(meters)
pb = np.random.default_rng(MS.SEED_BDG2).permutation(meters)
assert sorted(pb[:5].tolist()) == S["bdg2"]["development"]
assert sorted(pb[5:35].tolist()) == S["bdg2"]["held_out"]
bdg = [str(x) for x in pb[55:85]]
R2 = json.load(open(os.path.join(ROOT, "experiments", "LEBRE-V0.52-HELDOUT-02", "RESERVA2.json"), encoding="utf-8"))
assert [int(x) for x in pc[60:80]] == R2["camels_br"] and [str(x) for x in pb[35:55]] == R2["bdg2"]
used = set(S["camels_br"]["development"]) | set(S["camels_br"]["held_out"]) | set(R2["camels_br"])
assert not (set(cam) & used)
usedb = set(S["bdg2"]["development"]) | set(S["bdg2"]["held_out"]) | set(R2["bdg2"])
assert not (set(bdg) & usedb)

# existence (names only)
names = set(zipfile.ZipFile(os.path.join(D, "camels_br", "03_CAMELS_BR_streamflow_selected_catchments.zip")).namelist())
missing = [g for g in cam if not any(str(g) in n for n in names)]
out = {"created": "2026-09-27", "rule": "next positions of the SPLIT_V052 permutations after reserve 2 (CAMELS-BR seed 5202: 80-109; BDG2 seed 5203: 55-84)",
       "camels_br": cam, "bdg2": bdg, "camels_missing_in_archive": missing,
       "bdg2_sites_shared_with_development": sorted({b.split(":")[1].split("_")[0] for b in bdg} &
                                                    {b.split(":")[1].split("_")[0] for b in S["bdg2"]["development"]})}
json.dump(out, open(os.path.join(HERE, "RESERVA3.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
