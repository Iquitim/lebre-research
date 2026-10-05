#!/usr/bin/env python3
"""make_split_v053.py — reserva da avaliação final da v0.53 (regras em SPLIT_RULES.md).

Usa só metadados, cobertura e sementes. Recalcula as permutações da v0.52 e confere as posições já consumidas.
Requer: data/external_v052 (CAMELS-BR, BDG2) e a fase "base" de snapshot_v053.py (ONS Fator de Capacidade 2024-2025).
"""
import glob
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
D52 = ROOT / "data" / "external_v052"
E = ROOT / "experiments"
SEED_CAMELS, SEED_BDG2, SEED_SOLAR, SEED_EOLICA = 5202, 5203, 5311, 5312
MIN_COV = 0.9
USADAS_NO_LAB = {"Solar": ["Conj. Janaúba", "Conj. Arinos 2 500 kV", "Conj. Futura", "Conj. Sol do Cerrado",
                           "Conj. Helio Valgas", "Conj. Lar do Sol"],
                 "Eólica": ["Conj. São Roque", "Conj. Lagoa dos Ventos", "Conj. Caju", "Conj. Monte Verde",
                            "Conj. Serra do Mel A", "Conj. Santa Vitória do Palmar"]}
FX = {"DEXUSUK": "libra (US$ por libra)", "DEXSZUS": "franco suíço por US$", "DEXCAUS": "dólar canadense por US$",
      "DEXUSAL": "US$ por dólar australiano", "DEXMXUS": "peso mexicano por US$", "DEXKOUS": "won por US$",
      "DEXSDUS": "coroa sueca por US$", "DEXNOUS": "coroa norueguesa por US$"}


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def camels():
    z = zipfile.ZipFile(D52 / "camels_br" / "01_CAMELS_BR_attributes.zip")
    rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")  # noqa: E731
    a = rd("camels_br_human_intervention.txt").merge(rd("camels_br_quality_check.txt"), on="gauge_id")
    elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
    pick = [int(x) for x in np.random.default_rng(SEED_CAMELS).permutation(sorted(elig.gauge_id.astype(int).tolist()))]
    s52 = _json(E / "LEBRE-V0.52-DATA-01" / "SPLIT_V052.json")["camels_br"]
    r2 = _json(E / "LEBRE-V0.52-HELDOUT-02" / "RESERVA2.json")["camels_br"]
    r3 = _json(E / "LEBRE-V0.52-HELDOUT-03" / "RESERVA3.json")["camels_br"]
    assert sorted(pick[:10]) == s52["development"] and sorted(pick[10:60]) == s52["held_out"], "permutação CAMELS diferente"
    assert set(pick[60:80]) == set(r2) and set(pick[80:110]) == set(r3), "reservas 2/3 CAMELS diferentes"
    zq = zipfile.ZipFile(D52 / "camels_br" / "03_CAMELS_BR_streamflow_selected_catchments.zip")
    no_arquivo = {int(Path(n).name.split("_")[0]) for n in zq.namelist() if n.endswith(".txt") and Path(n).name[0].isdigit()}
    res, subst, pos = [], [], 110
    while len(res) < 30:
        g = pick[pos]
        (res if g in no_arquivo else subst).append(g); pos += 1
    return dict(semente=SEED_CAMELS, n_elegiveis=len(pick), posicoes=f"110-{pos - 1}", reservadas=sorted(res),
                substituidas_por_ausencia=subst, conferencia="posições 0-109 = SPLIT_V052 + RESERVA2 + RESERVA3")


def bdg2():
    z = zipfile.ZipFile(D52 / "bdg2" / "building-data-genome-project-2-v1.0.zip")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov, nz = m.notna().mean(), (m.fillna(0) != 0).mean()
        meters += [f"{kind}:{b}" for b in cov[(cov >= MIN_COV) & (nz >= 0.5)].index]
    pick = [str(x) for x in np.random.default_rng(SEED_BDG2).permutation(sorted(meters))]
    s52 = _json(E / "LEBRE-V0.52-DATA-01" / "SPLIT_V052.json")["bdg2"]
    r2 = _json(E / "LEBRE-V0.52-HELDOUT-02" / "RESERVA2.json")["bdg2"]
    r3 = _json(E / "LEBRE-V0.52-HELDOUT-03" / "RESERVA3.json")["bdg2"]
    assert sorted(pick[:5]) == s52["development"] and sorted(pick[5:35]) == s52["held_out"], "permutação BDG2 diferente"
    assert set(pick[35:55]) == set(r2) and set(pick[55:85]) == set(r3), "reservas 2/3 BDG2 diferentes"
    res = pick[85:115]
    site = lambda m: m.split(":")[1].split("_")[0]                                                      # noqa: E731
    usados = {site(m) for m in pick[:85]}
    return dict(semente=SEED_BDG2, n_elegiveis=len(pick), posicoes="85-114", reservadas=sorted(res),
                sites_compartilhados_com_series_ja_usadas=sorted({site(m) for m in res} & usados),
                conferencia="posições 0-84 = SPLIT_V052 + RESERVA2 + RESERVA3")


def usinas():
    arqs = sorted(glob.glob(str(ROOT / "data" / "external_v053" / "ons_fator" / "*.csv")))
    assert len(arqs) == 24, f"esperados 24 arquivos mensais de 2024-2025, achados {len(arqs)}"
    df = pd.concat([pd.read_csv(a, sep=";") for a in arqs], ignore_index=True)
    df["din_instante"] = pd.to_datetime(df["din_instante"])
    horas = pd.date_range("2024-01-01 00:00", "2025-12-31 23:00", freq="h")
    df = df[(df.din_instante >= horas[0]) & (df.din_instante <= horas[-1])]
    n = df.dropna(subset=["val_geracaoverificada"]).groupby("nom_usina_conjunto")["din_instante"].nunique() / len(horas)
    meta = df.groupby("nom_usina_conjunto").agg(tipo=("nom_tipousina", "first"), cap=("val_capacidadeinstalada", "max"),
                                                lat=("val_latitudesecoletora", "first"), lon=("val_longitudesecoletora", "first"))
    meta["completude"] = n.reindex(meta.index).fillna(0)
    out = {}
    for tipo, chave, seed in (("Solar", "solar", SEED_SOLAR), ("Eólica", "eolica", SEED_EOLICA)):
        m = meta[(meta.tipo == tipo) & meta.lat.notna() & meta.lon.notna() & (meta.completude >= 0.95) & (meta.cap >= 100)]
        m = m.drop(index=[u for u in USADAS_NO_LAB[tipo] if u in m.index])
        nomes = list(np.random.default_rng(seed).permutation(sorted(m.index)))[:8]
        out[chave] = dict(semente=seed, n_elegiveis_sem_as_do_lab=len(m), excluidas_usadas_no_lab=USADAS_NO_LAB[tipo],
                          elegibilidade="coordenadas; geração verificada em >= 95% das horas de 2024-2025; capacidade >= 100 MW",
                          reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                           lon=float(m.loc[k, "lon"]), completude=round(float(m.loc[k, "completude"]), 4))
                                      for k in nomes])
    return out


def main():
    snap = HERE / "SNAPSHOT_SHA256SUMS.txt"
    split = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"),
                 snapshot_base_sha256=hashlib.sha256(snap.read_bytes()).hexdigest(),
                 camels_br=camels(), bdg2=bdg2(), **usinas(),
                 carga=dict(subsistemas=["SUDESTE", "SUL", "NORDESTE", "NORTE"], periodo=["2026-01-01", "2026-09-30"],
                            observacao="separação no tempo: o LEBRE Lab usou 2022-2025 dos mesmos subsistemas"),
                 cambio=dict(pares=FX, periodo=["2010-01-01", "2025-12-31"], fonte="Fed H.10 via FRED, domínio público"))
    p = HERE / "SPLIT_V053.json"
    p.write_text(json.dumps(split, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V053_SHA256.txt").write_text(f"{h} *SPLIT_V053.json\n", encoding="utf-8", newline="\n")
    print("CAMELS", split["camels_br"]["posicoes"], "substituídas", split["camels_br"]["substituidas_por_ausencia"],
          "| BDG2 sites compartilhados", len(split["bdg2"]["sites_compartilhados_com_series_ja_usadas"]),
          "| solar elegíveis", split["solar"]["n_elegiveis_sem_as_do_lab"], "| eólica elegíveis",
          split["eolica"]["n_elegiveis_sem_as_do_lab"], "| SHA-256", h)


if __name__ == "__main__":
    main()
