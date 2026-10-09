"""ensaio_arquivos.py — presença dos arquivos e das séries da reserva, só por nomes (ENSAIO_PLANO.md, item 1)."""
import io
import os
import zipfile

import pandas as pd

import final_dados as FD

S = FD.SPLIT
falta = []
om = os.path.join(FD.SNAP, "open_meteo")
for tipo in ("solar", "eolica"):
    for u in S[tipo]["reservadas"]:
        if not os.path.exists(os.path.join(om, f"{tipo}_{FD._seguro(u['nome'])}.json")):
            falta.append(f"tempo {tipo} {u['nome']}")
for sub in S["carga"]["subsistemas"]:
    if not os.path.exists(os.path.join(om, f"carga_{sub}.json")):
        falta.append(f"tempo carga {sub}")
if not os.path.exists(os.path.join(FD.SNAP, "ons_carga", "CURVA_CARGA_2026.csv")):
    falta.append("carga 2026")
ons = sorted(os.listdir(os.path.join(FD.SNAP, "ons_fator")))
esperados = [f"FATOR_CAPACIDADE-2_{a}_{m:02d}.csv" for a in (2024, 2025) for m in range(1, 13)]
falta += [f"ONS {f}" for f in esperados if f not in ons]
for s in FD.FX + ["DGS2", "DGS10"]:
    if not os.path.exists(os.path.join(FD.SNAP, "fred", f"{s}.csv")):
        falta.append(f"FRED {s}")
nomes = set()
for f in esperados:
    nomes |= set(pd.read_csv(os.path.join(FD.SNAP, "ons_fator", f), sep=";", usecols=["nom_usina_conjunto"])["nom_usina_conjunto"])
falta += [f"usina sem nome nos arquivos do ONS: {u['nome']}" for t in ("solar", "eolica") for u in S[t]["reservadas"]
          if u["nome"] not in nomes]
D52 = os.path.join(FD.RAIZ, "data", "external_v052")
zips = {k: zipfile.ZipFile(os.path.join(D52, "camels_br", z)).namelist() for k, z in
        (("streamflow", "03_CAMELS_BR_streamflow_selected_catchments.zip"), ("precipitation", "05_CAMELS_BR_precipitation.zip"),
         ("actual_evapotransp", "06_CAMELS_BR_actual_evapotransp.zip"), ("temperature", "09_CAMELS_BR_temperature.zip"))}
for g in S["camels_br"]["reservadas"]:
    for k, lst in zips.items():
        if not any(n.endswith(f"/{g}_{k}.txt") for n in lst):
            falta.append(f"CAMELS {g} {k}")
z = zipfile.ZipFile(os.path.join(D52, "bdg2", "building-data-genome-project-2-v1.0.zip"))
base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/meters/cleaned/"
cab = {}
for m in S["bdg2"]["reservadas"]:
    kind, bid = m.split(":")
    if kind not in cab:
        with z.open(base + f"{kind}_cleaned.csv") as fh:
            cab[kind] = set(io.TextIOWrapper(fh, encoding="utf-8").readline().strip().split(","))
    if bid not in cab[kind]:
        falta.append(f"BDG2 {m}")
n = 16 + 4 + 1 + 24 + 10 + 16 + 30 * 4 + 30
print(f"itens conferidos: {n}; faltando: {len(falta)}")
for f in falta:
    print(" -", f)
