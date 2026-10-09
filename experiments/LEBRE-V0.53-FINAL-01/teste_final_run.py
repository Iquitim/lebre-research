"""teste_final_run.py — confere o mecanismo de final_run.py numa série NÃO reservada (B01 do LEBRE Lab, usina 0): o MSE
da v0.53 (avaliação a partir de 20% de T) tem de ser idêntico ao registrado no E20 do Lab (analises/e20_prod_q2/B01.json)
e o custo da v0.52 também. Uso: LEBRE_LAB=<Lab> LEBRE053_PROTO=<worktree>/experiments/LEBRE-V0.53-PROTO-01 python teste_final_run.py
"""
import glob
import json
import os
import sys

import numpy as np

import final_dados as FD
import final_run as FR

LAB = os.environ["LEBRE_LAB"]
sys.path.insert(0, LAB)
from lab import fontes as F  # noqa: E402
from lab.run import load  # noqa: E402

reg = json.load(open(os.path.join(LAB, "analises", "e20_prod_q2", "B01.json"), encoding="utf-8"))["series"][0]
mod = load(os.path.join(LAB, "scenarios", "B", "B01_solar.py"))
u = mod.escolher(mod.TIPO)[0]
assert u["nome"] == reg["serie"]
fn = f"{u['lat']:.4f}_{u['lon']:.4f}_2024-01-01_2025-12-31_{'-'.join(FD.VARS_SOLAR)}_America-Sao_Paulo.json"
ons = sorted(glob.glob(os.path.join(LAB, "dados", "ons", "fator-capacidade-2", "*.csv")))
s = FD.usina("solar", u["nome"], ons, os.path.join(F.CACHE, "open_meteo", fn))
s["zero_baseline"] = False
f53, f52, fr, info = FR._modelos(FR._proto(), s, s["X"], s["y"], None)
ini = int(0.2 * len(s["y"]))
ok = np.isfinite(s["y"]) & np.isfinite(f53)
ok[:ini] = False
mse = float(np.mean((s["y"][ok] - f53[ok]) ** 2))
print(u["nome"], "| MSE v0.53", mse, "registrado", reg["mse"], "| igual:", mse == reg["mse"])
print("custo v0.52", info["custo_v052"], "registrado", reg["custo_v052"], "| igual:", info["custo_v052"] == reg["custo_v052"])
assert mse == reg["mse"] and info["custo_v052"] == reg["custo_v052"]
print("teste passou")
