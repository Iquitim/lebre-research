#!/usr/bin/env python3
"""make_split_v054.py — reserva da avaliação final da v0.54 (regras em SPLIT_RULES.md).

Usa só metadados, cobertura (fração de valores não faltantes) e sementes; os valores das séries não são inspecionados.
Recalcula as permutações da v0.52 e confere as posições já consumidas (v0.52, reservas 2 e 3, reserva da v0.53).
Requer: data/external_v052 (CAMELS-BR, BDG2), data/external_v053/ons_fator (2024-2025, já registrado) e a fase "base" de
snapshot_v054.py. Pacotes: pandas 2.2.3, numpy, xlrd (leitura das planilhas .xls da EIA).
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
D52, D53, D54 = ROOT / "data" / "external_v052", ROOT / "data" / "external_v053", ROOT / "data" / "external_v054"
E = ROOT / "experiments"
SEED_CAMELS, SEED_BDG2, SEED_EOLICA, SEED_SOLAR = 5202, 5203, 5421, 5422
MIN_COV, MIN_COV_NIVEIS = 0.9, 0.9
N_LAB_POR_TIPO = 36            # o LEBRE Lab usou as 36 maiores usinas de cada tipo (cenários B e validações V a Z)
EIA_NOMES = {"RNGWHHD": "gás natural Henry Hub (US$/MMBtu)",
             "EER_EPMRU_PF4_Y35NY_DPG": "gasolina convencional, porto de Nova York (US$/galão)",
             "EER_EPMRU_PF4_RGC_DPG": "gasolina convencional, Costa do Golfo (US$/galão)",
             "EER_EPD2F_PF4_Y35NY_DPG": "óleo de aquecimento nº 2, porto de Nova York (US$/galão)",
             "EER_EPD2DXL0_PF4_Y35NY_DPG": "diesel de ultrabaixo enxofre, porto de Nova York (US$/galão)",
             "EER_EPD2DXL0_PF4_RGC_DPG": "diesel de ultrabaixo enxofre, Costa do Golfo (US$/galão)",
             "EER_EPD2DC_PF4_Y05LA_DPG": "diesel CARB de ultrabaixo enxofre, Los Angeles (US$/galão)",
             "EER_EPJK_PF4_RGC_DPG": "querosene de aviação, Costa do Golfo (US$/galão)",
             "EER_EPLLPA_PF4_Y44MB_DPG": "propano, Mont Belvieu (US$/galão)",
             "EER_EPMRR_PF4_Y05LA_DPG": "gasolina RBOB, Los Angeles (US$/galão)"}
TESOURO = {("nominal", "1 Mo"): "Tesouro nominal 1 mês", ("nominal", "6 Mo"): "Tesouro nominal 6 meses",
           ("real", "5 YR"): "Tesouro real 5 anos", ("real", "7 YR"): "Tesouro real 7 anos",
           ("real", "10 YR"): "Tesouro real 10 anos", ("real", "20 YR"): "Tesouro real 20 anos",
           ("real", "30 YR"): "Tesouro real 30 anos"}
DIAS = pd.bdate_range("2010-01-01", "2025-12-31")


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
    v53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json")["camels_br"]
    assert sorted(pick[:10]) == s52["development"] and sorted(pick[10:60]) == s52["held_out"], "permutação CAMELS diferente"
    assert set(pick[60:80]) == set(r2) and set(pick[80:110]) == set(r3), "reservas 2/3 CAMELS diferentes"
    assert v53["posicoes"] == "110-139" and set(pick[110:140]) == set(v53["reservadas"]), "reserva v0.53 CAMELS diferente"
    zq = zipfile.ZipFile(D52 / "camels_br" / "03_CAMELS_BR_streamflow_selected_catchments.zip")
    no_arquivo = {int(Path(n).name.split("_")[0]) for n in zq.namelist() if n.endswith(".txt") and Path(n).name[0].isdigit()}
    res, subst, pos = [], [], 140
    while len(res) < 30:
        g = pick[pos]
        (res if g in no_arquivo else subst).append(g); pos += 1
    return dict(semente=SEED_CAMELS, n_elegiveis=len(pick), posicoes=f"140-{pos - 1}", reservadas=sorted(res),
                substituidas_por_ausencia=subst,
                conferencia="posições 0-139 = SPLIT_V052 + RESERVA2 + RESERVA3 + reserva da v0.53")


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
    v53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json")["bdg2"]
    assert sorted(pick[:5]) == s52["development"] and sorted(pick[5:35]) == s52["held_out"], "permutação BDG2 diferente"
    assert set(pick[35:55]) == set(r2) and set(pick[55:85]) == set(r3), "reservas 2/3 BDG2 diferentes"
    assert v53["posicoes"] == "85-114" and set(pick[85:115]) == set(v53["reservadas"]), "reserva v0.53 BDG2 diferente"
    res = pick[115:145]
    site = lambda m: m.split(":")[1].split("_")[0]                                                      # noqa: E731
    usados = {site(m) for m in pick[:115]}
    return dict(semente=SEED_BDG2, n_elegiveis=len(pick), posicoes="115-144", reservadas=sorted(res),
                sites_compartilhados_com_series_ja_usadas=sorted({site(m) for m in res} & usados),
                conferencia="posições 0-114 = SPLIT_V052 + RESERVA2 + RESERVA3 + reserva da v0.53")


def _ons(arqs, ini, fim):
    df = pd.concat([pd.read_csv(a, sep=";") for a in arqs], ignore_index=True)
    df["din_instante"] = pd.to_datetime(df["din_instante"])
    horas = pd.date_range(ini, fim, freq="h")
    df = df[(df.din_instante >= horas[0]) & (df.din_instante <= horas[-1])]
    n = df.dropna(subset=["val_geracaoverificada"]).groupby("nom_usina_conjunto")["din_instante"].nunique() / len(horas)
    meta = df.groupby("nom_usina_conjunto").agg(tipo=("nom_tipousina", "first"), cap=("val_capacidadeinstalada", "max"),
                                                lat=("val_latitudesecoletora", "first"), lon=("val_longitudesecoletora", "first"))
    meta["completude"] = n.reindex(meta.index).fillna(0)
    return meta


def usinas():
    a2425 = sorted(glob.glob(str(D53 / "ons_fator" / "*.csv")))
    assert len(a2425) == 24, f"esperados 24 arquivos mensais de 2024-2025, achados {len(a2425)}"
    a26 = sorted(glob.glob(str(D54 / "ons_fator_2026" / "*.csv")))
    assert len(a26) == 9, f"esperados 9 arquivos mensais de jan-set/2026, achados {len(a26)}"
    m25 = _ons(a2425, "2024-01-01 00:00", "2025-12-31 23:00")
    m26 = _ons(a26, "2026-01-01 00:00", "2026-09-30 23:00")
    v53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json")
    out = {}
    # Eólica: usinas inéditas, 2024-2025. Exclui as do Lab (reproduz lab/usinas.escolher: completude >= 0,95,
    # coordenadas, fora da reserva da v0.53, 36 maiores por capacidade) e as da reserva da v0.53.
    tipo = "Eólica"
    base = m25[(m25.tipo == tipo) & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95)]
    r53 = {u["nome"] for u in v53["eolica"]["reservadas"]}
    lab = list(base[~base.index.isin(r53)].sort_values("cap", ascending=False).head(N_LAB_POR_TIPO).index)
    m = base[(base.cap >= 100) & ~base.index.isin(r53) & ~base.index.isin(lab)]
    nomes = list(np.random.default_rng(SEED_EOLICA).permutation(sorted(m.index)))[:8]
    out["eolica"] = dict(semente=SEED_EOLICA, periodo=["2024-01-01", "2025-12-31"], n_elegiveis=len(m),
                         excluidas_lab=lab, excluidas_reserva_v053=sorted(r53),
                         elegibilidade="coordenadas; geração verificada em >= 95% das horas de 2024-2025; capacidade >= 100 MW",
                         reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                          lon=float(m.loc[k, "lon"]), completude=round(float(m.loc[k, "completude"]), 4))
                                     for k in nomes])
    # Solar: separação no tempo (jan-set/2026, período que o Lab não carrega e que nenhuma avaliação usou).
    tipo = "Solar"
    base = m25[(m25.tipo == tipo) & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95) & (m25.cap >= 100)]
    c26 = m26["completude"].reindex(base.index).fillna(0)
    m = base[c26 >= 0.95]
    nomes = list(np.random.default_rng(SEED_SOLAR).permutation(sorted(m.index)))[:8]
    out["solar"] = dict(semente=SEED_SOLAR, periodo=["2026-01-01", "2026-09-30"], n_elegiveis=len(m),
                        elegibilidade="coordenadas; geração verificada em >= 95% das horas de 2024-2025 e de jan-set/2026; capacidade >= 100 MW",
                        observacao="separação no tempo: as usinas solares elegíveis de 2024-2025 foram todas usadas (Lab e reserva da v0.53)",
                        reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                         lon=float(m.loc[k, "lon"]), completude_2026=round(float(c26[k]), 4)) for k in nomes])
    return out


def _cobertura(s):
    s = s[(s.index >= DIAS[0]) & (s.index <= DIAS[-1])]
    return float(s.reindex(DIAS).notna().mean())


def niveis():
    alvos = {}
    for cod, nome in EIA_NOMES.items():
        x = pd.read_excel(D54 / "eia" / f"{cod}d.xls", sheet_name="Data 1", skiprows=2, engine="xlrd")
        s = pd.Series(pd.to_numeric(x.iloc[:, 1], errors="coerce").to_numpy(), index=pd.to_datetime(x.iloc[:, 0]))
        alvos[f"eia:{cod}"] = dict(nome=nome, cobertura=round(_cobertura(s), 4))
    tab = {}
    for tipo in ("nominal", "real"):
        df = pd.concat([pd.read_csv(p) for p in sorted((D54 / "tesouro").glob(f"{tipo}_*.csv"))], ignore_index=True)
        df.index = pd.to_datetime(df["Date"], format="%m/%d/%Y")
        tab[tipo] = df
    for (tipo, col), nome in TESOURO.items():
        s = pd.to_numeric(tab[tipo][col], errors="coerce") if col in tab[tipo] else pd.Series(dtype=float)
        alvos[f"tesouro:{tipo}:{col}"] = dict(nome=nome, cobertura=round(_cobertura(s), 4))
    res = {k: v for k, v in alvos.items() if v["cobertura"] >= MIN_COV_NIVEIS}
    return dict(periodo=["2010-01-01", "2025-12-31"], cobertura_minima=MIN_COV_NIVEIS, reservadas=res,
                fora_por_cobertura={k: v for k, v in alvos.items() if k not in res},
                excluidas=dict(eia_RWTC="WTI: alvo no desenvolvimento do LEBRE Lab (C01-C03)",
                               eia_RBRTE="Brent: quase idêntico ao WTI",
                               tesouro_nominal="1, 2, 3, 5, 7, 10, 20 e 30 anos e 3 meses: usados no LEBRE Lab (C04 e validações 2 a 5)"),
                entradas_disponiveis=["eia:RWTC", "eia:RBRTE"],
                fonte="EIA (preços à vista diários) e Departamento do Tesouro dos EUA (curvas diárias); domínio público")


def main():
    snap = HERE / "SNAPSHOT_SHA256SUMS.txt"
    split = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"),
                 snapshot_base_sha256=hashlib.sha256(snap.read_bytes()).hexdigest(),
                 camels_br=camels(), bdg2=bdg2(), **usinas(), niveis=niveis(),
                 fora_da_reserva=dict(carga="decisão do responsável pelo projeto (10/10/2026): a carga de 2026 até setembro foi usada na v0.53",
                                      cambio="moedas flutuantes do H.10 praticamente esgotadas"))
    p = HERE / "SPLIT_V054.json"
    p.write_text(json.dumps(split, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V054_SHA256.txt").write_text(f"{h} *SPLIT_V054.json\n", encoding="utf-8", newline="\n")
    print("CAMELS", split["camels_br"]["posicoes"], "substituídas", split["camels_br"]["substituidas_por_ausencia"],
          "| BDG2 sites compartilhados", len(split["bdg2"]["sites_compartilhados_com_series_ja_usadas"]),
          "| eólica elegíveis", split["eolica"]["n_elegiveis"], "| solar elegíveis", split["solar"]["n_elegiveis"],
          "| níveis", len(split["niveis"]["reservadas"]), "fora por cobertura", list(split["niveis"]["fora_por_cobertura"]),
          "| SHA-256", h)


if __name__ == "__main__":
    main()
