#!/usr/bin/env python3
"""snapshot_v053.py — cópia dos dados brutos da reserva da v0.53 em data/external_v053/ (fora do git), com SHA-256.

Duas fases, nesta ordem:
  python snapshot_v053.py base    ONS Fator de Capacidade 2024-2025, ONS Curva de Carga 2026, câmbio e juros (FRED)
  python snapshot_v053.py tempo   Open-Meteo nos locais reservados (depende de SPLIT_V053.json)
Os arquivos são gravados como baixados, sem abrir os valores. Licenças: SPLIT_RULES.md e dados/FONTES.md do LEBRE Lab.
"""
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data" / "external_v053"
SUMS = HERE / "SNAPSHOT_SHA256SUMS.txt"
# Opcional: pasta com os arquivos mensais já baixados pelo LEBRE Lab em 04/10/2026 (evita baixar de novo).
LAB_CACHE = Path(os.environ["LEBRE_LAB_ONS_CACHE"]) if os.environ.get("LEBRE_LAB_ONS_CACHE") else None
UA = {"User-Agent": "lebre-research (pesquisa sem fins comerciais; github.com/Iquitim/lebre-research)"}
FX = ["DEXUSUK", "DEXSZUS", "DEXCAUS", "DEXUSAL", "DEXMXUS", "DEXKOUS", "DEXSDUS", "DEXNOUS"]
JUROS = ["DGS2", "DGS10"]
CAPITAIS = {"SUDESTE": (-23.55, -46.63), "SUL": (-30.03, -51.23), "NORDESTE": (-8.05, -34.90), "NORTE": (-1.46, -48.50)}
VARS_CARGA = ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "shortwave_radiation", "precipitation"]
VARS_SOLAR = ["shortwave_radiation", "direct_normal_irradiance", "cloud_cover", "temperature_2m"]
VARS_EOLICA = ["wind_speed_100m", "wind_direction_100m", "wind_speed_10m", "temperature_2m"]


def baixar(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                dest.write_bytes(r.read())
            return
        except Exception as ex:                                   # noqa: BLE001
            if k == 3:
                raise RuntimeError(f"falhou: {url}: {ex}") from ex
            time.sleep(5 * (k + 1))


def ons_recursos(dataset):
    url = f"https://dados.ons.org.br/api/3/action/package_show?id={dataset}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return json.load(r)["result"]["resources"]


def fase_base():
    for r in ons_recursos("fator-capacidade-2"):
        nome = r["name"]
        if r["format"].upper() == "CSV" and any(f"-{a}-" in nome for a in ("2024", "2025")):
            fn = r["url"].rsplit("/", 1)[-1]; dest = OUT / "ons_fator" / fn
            if not dest.exists() and LAB_CACHE and (LAB_CACHE / fn).exists():
                dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(LAB_CACHE / fn, dest)
            baixar(r["url"], dest)
    for r in ons_recursos("curva-carga"):
        if r["format"].upper() == "CSV" and r["name"].endswith("2026"):
            baixar(r["url"], OUT / "ons_carga" / r["url"].rsplit("/", 1)[-1])
    for s in FX + JUROS:
        baixar(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}", OUT / "fred" / f"{s}.csv")


def open_meteo(lat, lon, ini, fim, variaveis, dest):
    q = dict(latitude=f"{lat:.4f}", longitude=f"{lon:.4f}", start_date=ini, end_date=fim, hourly=",".join(variaveis),
             timezone="America/Sao_Paulo")
    baixar("https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(q), dest)


def fase_tempo():
    split = json.loads((HERE / "SPLIT_V053.json").read_text(encoding="utf-8"))
    for sub, (lat, lon) in CAPITAIS.items():
        open_meteo(lat, lon, "2026-01-01", "2026-09-30", VARS_CARGA, OUT / "open_meteo" / f"carga_{sub}.json")
    for tipo, vars_ in (("solar", VARS_SOLAR), ("eolica", VARS_EOLICA)):
        for u in split[tipo]["reservadas"]:
            safe = "".join(c if c.isalnum() else "_" for c in u["nome"])
            open_meteo(u["lat"], u["lon"], "2024-01-01", "2025-12-31", vars_, OUT / "open_meteo" / f"{tipo}_{safe}.json")


def gravar_somas():
    linhas = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            linhas.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.relative_to(ROOT).as_posix()}")
    SUMS.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(len(linhas), "arquivos em", SUMS.name)


if __name__ == "__main__":
    {"base": fase_base, "tempo": fase_tempo}[sys.argv[1]]()
    gravar_somas()
