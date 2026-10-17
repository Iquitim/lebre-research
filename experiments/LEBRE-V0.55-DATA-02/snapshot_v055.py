#!/usr/bin/env python3
"""snapshot_v055.py — cópia dos dados brutos da reserva final da v0.55 em data/external_v055/ (fora do git), com SHA-256.

Duas fases, nesta ordem (regras em SPLIT_RULES.md):
  python snapshot_v055.py base    FRED (6 taxas de commercial paper do H.15; entradas DFF e DTB3) e BCE (9 alvos e 4
                                  entradas), dez/2009 a dez/2025; confere os arquivos do ONS já registrados
  python snapshot_v055.py tempo   Open-Meteo nos locais das usinas sorteadas (depende de SPLIT_V055.json)
Os arquivos são gravados como baixados, sem abrir os valores. As funções de download (baixar, open_meteo) são as de
LEBRE-V0.54-DATA-01/snapshot_v054.py, importadas sem alteração.
Licenças: FRED/Board of Governors, domínio público com citação; BCE, reuso livre com citação ("Source: ECB statistics");
Open-Meteo CC BY 4.0; ONS CC BY.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data" / "external_v055"
SUMS = HERE / "SNAPSHOT_SHA256SUMS.txt"
_s = importlib.util.spec_from_file_location("snapshot_v054", ROOT / "experiments" / "LEBRE-V0.54-DATA-01" / "snapshot_v054.py")
S54 = importlib.util.module_from_spec(_s); _s.loader.exec_module(S54)

FRED_ALVOS = ["DCPN30", "DCPN2M", "DCPN3M", "DCPF1M", "DCPF2M", "DCPF3M"]
FRED_ENTRADAS = ["DFF", "DTB3"]
ECB_ALVOS = ["PLN", "CZK", "HUF", "RON", "ISK", "TRY", "IDR", "PHP", "ILS"]
ECB_ENTRADAS = ["USD", "GBP", "JPY", "CHF"]
INI, FIM = "2009-12-01", "2025-12-31"


def fase_base():
    for cod in FRED_ALVOS + FRED_ENTRADAS:
        S54.baixar(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={cod}&cosd={INI}&coed={FIM}", OUT / "fred" / f"{cod}.csv")
    for cur in ECB_ALVOS + ECB_ENTRADAS:
        S54.baixar(f"https://data-api.ecb.europa.eu/service/data/EXR/D.{cur}.EUR.SP00.A?format=csvdata"
                   f"&startPeriod={INI}&endPeriod={FIM}", OUT / "ecb" / f"EUR_{cur}.csv")
    # ONS: os arquivos já registrados (2024-2025 na v0.53; jan-set/2026 na v0.54) são reutilizados; conferência dos hashes
    for pasta, sums in (("data/external_v053/ons_fator", "LEBRE-V0.53-DATA-01"), ("data/external_v054/ons_fator_2026", "LEBRE-V0.54-DATA-01")):
        reg = {ln.split(" *")[1]: ln.split(" *")[0] for ln in (ROOT / "experiments" / sums / "SNAPSHOT_SHA256SUMS.txt").read_text().splitlines() if pasta in ln}
        assert reg, pasta
        for rel, h in reg.items():
            assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, f"arquivo do ONS alterado: {rel}"
        print("ONS conferido:", pasta, len(reg), "arquivos")


def fase_tempo():
    split = json.loads((HERE / "SPLIT_V055.json").read_text(encoding="utf-8"))
    for tipo, vars_, (ini, fim) in (("solar", S54.VARS_SOLAR, ("2026-01-01", "2026-09-30")),
                                    ("eolica", S54.VARS_EOLICA, ("2024-01-01", "2025-12-31"))):
        for u in split[tipo]["reservadas"]:
            safe = "".join(c if c.isalnum() else "_" for c in u["nome"])
            S54.open_meteo(u["lat"], u["lon"], ini, fim, vars_, OUT / "open_meteo" / f"{tipo}_{safe}.json")


def gravar_somas(nome):
    linhas = [f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.relative_to(ROOT).as_posix()}"
              for p in sorted(OUT.rglob("*")) if p.is_file()]
    (HERE / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(len(linhas), "arquivos em", nome)


if __name__ == "__main__":
    fase = sys.argv[1]
    {"base": fase_base, "tempo": fase_tempo}[fase]()
    gravar_somas("SNAPSHOT_BASE_SHA256SUMS.txt" if fase == "base" else "SNAPSHOT_SHA256SUMS.txt")
