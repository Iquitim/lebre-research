#!/usr/bin/env python3
"""snapshot_v054.py — cópia dos dados brutos da reserva da v0.54 em data/external_v054/ (fora do git), com SHA-256.

Duas fases, nesta ordem (regras em SPLIT_RULES.md):
  python snapshot_v054.py base    ONS Fator de Capacidade jan-set/2026, preços à vista diários da EIA e curvas diárias
                                  do Tesouro dos EUA (nominal e real), 2010-2025
  python snapshot_v054.py tempo   Open-Meteo nos locais das usinas reservadas (depende de SPLIT_V054.json)
Os arquivos são gravados como baixados, sem abrir os valores. A fase base do ONS de 2024-2025 (eólica) reutiliza os
arquivos já registrados em data/external_v053/ons_fator (SHA-256 em LEBRE-V0.53-DATA-01/SNAPSHOT_SHA256SUMS.txt).
Licenças: ONS CC-BY; Open-Meteo CC BY 4.0 (uso não comercial do API gratuito); EIA e Tesouro dos EUA, domínio público
(obras do governo federal americano).
"""
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data" / "external_v054"
SUMS = HERE / "SNAPSHOT_SHA256SUMS.txt"
UA = {"User-Agent": "Mozilla/5.0 (lebre-research; pesquisa sem fins comerciais; github.com/Iquitim/lebre-research)"}
MESES_SOLAR = [f"2026-{m:02d}" for m in range(1, 10)]
# Preços à vista diários da EIA (fora o WTI, alvo no desenvolvimento do LEBRE Lab, e o Brent, quase idêntico a ele).
EIA = {"RNGWHHD": "ng", "EER_EPMRU_PF4_Y35NY_DPG": "pet", "EER_EPMRU_PF4_RGC_DPG": "pet", "EER_EPD2F_PF4_Y35NY_DPG": "pet",
       "EER_EPD2DXL0_PF4_Y35NY_DPG": "pet", "EER_EPD2DXL0_PF4_RGC_DPG": "pet", "EER_EPD2DC_PF4_Y05LA_DPG": "pet",
       "EER_EPJK_PF4_RGC_DPG": "pet", "EER_EPLLPA_PF4_Y44MB_DPG": "pet", "EER_EPMRR_PF4_Y05LA_DPG": "pet"}
# Entradas (não alvos): WTI e Brent, para as tarefas de energia.
EIA_ENTRADAS = {"RWTC": "pet", "RBRTE": "pet"}
ANOS = range(2010, 2026)
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


def tesouro(ano, tipo):
    q = dict(type=tipo, field_tdr_date_value=str(ano), page="", _format="csv")
    return (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{ano}/all?"
            + urllib.parse.urlencode(q))


def fase_base():
    feitos = set()
    for r in ons_recursos("fator-capacidade-2"):
        if r["format"].upper() == "CSV" and any(r["name"].endswith(m) for m in MESES_SOLAR):
            fn = r["url"].rsplit("/", 1)[-1]
            if fn not in feitos:
                baixar(r["url"], OUT / "ons_fator_2026" / fn); feitos.add(fn)
    assert len(feitos) == 9, f"esperados 9 arquivos mensais de jan-set/2026, achados {sorted(feitos)}"
    for cod, grupo in {**EIA, **EIA_ENTRADAS}.items():
        baixar(f"https://www.eia.gov/dnav/{grupo}/hist_xls/{cod}d.xls", OUT / "eia" / f"{cod}d.xls")
    for ano in ANOS:
        baixar(tesouro(ano, "daily_treasury_yield_curve"), OUT / "tesouro" / f"nominal_{ano}.csv")
        baixar(tesouro(ano, "daily_treasury_real_yield_curve"), OUT / "tesouro" / f"real_{ano}.csv")


def open_meteo(lat, lon, ini, fim, variaveis, dest):
    q = dict(latitude=f"{lat:.4f}", longitude=f"{lon:.4f}", start_date=ini, end_date=fim, hourly=",".join(variaveis),
             timezone="America/Sao_Paulo")
    baixar("https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(q), dest)


def fase_tempo():
    split = json.loads((HERE / "SPLIT_V054.json").read_text(encoding="utf-8"))
    for tipo, vars_, (ini, fim) in (("solar", VARS_SOLAR, ("2026-01-01", "2026-09-30")),
                                    ("eolica", VARS_EOLICA, ("2024-01-01", "2025-12-31"))):
        for u in split[tipo]["reservadas"]:
            safe = "".join(c if c.isalnum() else "_" for c in u["nome"])
            open_meteo(u["lat"], u["lon"], ini, fim, vars_, OUT / "open_meteo" / f"{tipo}_{safe}.json")


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
