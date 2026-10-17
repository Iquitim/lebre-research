#!/usr/bin/env python3
"""make_split_v055.py — reserva da avaliação final da v0.55 (regras em SPLIT_RULES.md).

Usa só metadados, cobertura (fração de valores não faltantes) e sementes; os valores das séries não são inspecionados.
Confere as posições já consumidas (até a validação da v0.55) e as reservas anteriores das usinas. Requer
data/external_v052 (CAMELS-BR, BDG2), os arquivos do ONS já registrados e a fase base de snapshot_v055.py.
"""
import hashlib
import importlib.util
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E = ROOT / "experiments"
D52, D53, D54, D55 = (ROOT / "data" / f"external_v05{k}" for k in (2, 3, 4, 5))
SEED_CAMELS, SEED_BDG2, SEED_EOLICA, SEED_SOLAR = 5202, 5203, 5521, 5522
MIN_COV = 0.9
DIAS = pd.bdate_range("2010-01-01", "2025-12-31")
_s = importlib.util.spec_from_file_location("make_split_v054", E / "LEBRE-V0.54-DATA-01" / "make_split_v054.py")
M54 = importlib.util.module_from_spec(_s); _s.loader.exec_module(M54)
FRED_ALVOS = ["DCPN30", "DCPN2M", "DCPN3M", "DCPF1M", "DCPF2M", "DCPF3M"]
ECB_ALVOS = ["PLN", "CZK", "HUF", "RON", "ISK", "TRY", "IDR", "PHP", "ILS"]


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def camels():
    z = zipfile.ZipFile(D52 / "camels_br" / "01_CAMELS_BR_attributes.zip")
    rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")  # noqa: E731
    a = rd("camels_br_human_intervention.txt").merge(rd("camels_br_quality_check.txt"), on="gauge_id")
    elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
    pick = [int(x) for x in np.random.default_rng(SEED_CAMELS).permutation(sorted(elig.gauge_id.astype(int).tolist()))]
    val = _json(E / "LEBRE-V0.55-DATA-01" / "SPLIT_V055_VAL.json")["camels_br"]
    assert val["posicoes"] == "170-189" and set(pick[170:190]) == set(val["validacao"]), "validação v0.55 CAMELS diferente"
    zq = zipfile.ZipFile(D52 / "camels_br" / "03_CAMELS_BR_streamflow_selected_catchments.zip")
    no_arquivo = {int(Path(n).name.split("_")[0]) for n in zq.namelist() if n.endswith(".txt") and Path(n).name[0].isdigit()}
    res, subst, pos = [], [], 190
    while len(res) < 30 and pos < len(pick):
        g = pick[pos]
        (res if g in no_arquivo else subst).append(g); pos += 1
    return dict(semente=SEED_CAMELS, n_elegiveis=len(pick), posicoes=f"190-{pos - 1}", reservadas=sorted(res),
                substituidas_por_ausencia=subst, conferencia="posições 170-189 = validação da v0.55")


def bdg2():
    z = zipfile.ZipFile(D52 / "bdg2" / "building-data-genome-project-2-v1.0.zip")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov, nz = m.notna().mean(), (m.fillna(0) != 0).mean()
        meters += [f"{kind}:{b}" for b in cov[(cov >= MIN_COV) & (nz >= 0.5)].index]
    pick = [str(x) for x in np.random.default_rng(SEED_BDG2).permutation(sorted(meters))]
    val = _json(E / "LEBRE-V0.55-DATA-01" / "SPLIT_V055_VAL.json")["bdg2"]
    assert val["posicoes"] == "145-174" and set(pick[145:175]) == set(val["validacao"]), "validação v0.55 BDG2 diferente"
    res = pick[175:205]
    site = lambda m: m.split(":")[1].split("_")[0]                                                      # noqa: E731
    return dict(semente=SEED_BDG2, n_elegiveis=len(pick), posicoes="175-204", reservadas=sorted(res),
                sites_compartilhados_com_series_ja_usadas=sorted({site(m) for m in res} & {site(m) for m in pick[:175]}),
                conferencia="posições 145-174 = validação da v0.55")


def usinas():
    import glob
    a2425 = sorted(glob.glob(str(D53 / "ons_fator" / "*.csv"))); a26 = sorted(glob.glob(str(D54 / "ons_fator_2026" / "*.csv")))
    assert len(a2425) == 24 and len(a26) == 9
    m25 = M54._ons(a2425, "2024-01-01 00:00", "2025-12-31 23:00")
    m26 = M54._ons(a26, "2026-01-01 00:00", "2026-09-30 23:00")
    v53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json"); v54 = _json(E / "LEBRE-V0.54-DATA-01" / "SPLIT_V054.json")
    out = {}
    base = m25[(m25.tipo == "Eólica") & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95)]
    r53 = {u["nome"] for u in v53["eolica"]["reservadas"]}; r54 = {u["nome"] for u in v54["eolica"]["reservadas"]}
    lab = list(base[~base.index.isin(r53)].sort_values("cap", ascending=False).head(M54.N_LAB_POR_TIPO).index)
    assert lab == v54["eolica"]["excluidas_lab"], "lista das eólicas do Lab diferente da v0.54"
    m = base[(base.cap >= 100) & ~base.index.isin(r53) & ~base.index.isin(lab) & ~base.index.isin(r54)]
    nomes = list(np.random.default_rng(SEED_EOLICA).permutation(sorted(m.index)))[:8]
    out["eolica"] = dict(semente=SEED_EOLICA, periodo=["2024-01-01", "2025-12-31"], n_elegiveis=len(m),
                         excluidas=dict(lab=len(lab), reserva_v053=len(r53), reserva_v054=len(r54)),
                         reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                          lon=float(m.loc[k, "lon"]), completude=round(float(m.loc[k, "completude"]), 4)) for k in nomes])
    base = m25[(m25.tipo == "Solar") & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95) & (m25.cap >= 100)]
    c26 = m26["completude"].reindex(base.index).fillna(0)
    s54 = {u["nome"] for u in v54["solar"]["reservadas"]}
    m = base[(c26 >= 0.95) & ~base.index.isin(s54)]
    nomes = list(np.random.default_rng(SEED_SOLAR).permutation(sorted(m.index)))[:8]
    out["solar"] = dict(semente=SEED_SOLAR, periodo=["2026-01-01", "2026-09-30"], n_elegiveis=len(m),
                        excluidas=dict(reserva_v054=len(s54)), observacao="separação no tempo, como na v0.54",
                        reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                         lon=float(m.loc[k, "lon"]), completude_2026=round(float(c26[k]), 4)) for k in nomes])
    return out


def _cob(s):
    s = s[(s.index >= DIAS[0]) & (s.index <= DIAS[-1])]
    return round(float(s.reindex(DIAS).notna().mean()), 4)


def fred_serie(cod):
    df = pd.read_csv(D55 / "fred" / f"{cod}.csv")
    return pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(), index=pd.to_datetime(df.iloc[:, 0]))


def ecb_serie(cur):
    df = pd.read_csv(D55 / "ecb" / f"EUR_{cur}.csv")
    return pd.Series(pd.to_numeric(df["OBS_VALUE"], errors="coerce").to_numpy(), index=pd.to_datetime(df["TIME_PERIOD"]))


def niveis():
    cp = {c: _cob(fred_serie(c)) for c in FRED_ALVOS}
    ec = {c: _cob(ecb_serie(c)) for c in ECB_ALVOS}
    return dict(niveis_cp=dict(cobertura=cp, reservadas=[c for c in FRED_ALVOS if cp[c] >= MIN_COV], entradas=["DFF", "DTB3"]),
                niveis_ecb=dict(cobertura=ec, reservadas=[c for c in ECB_ALVOS if ec[c] >= MIN_COV],
                                entradas=["USD", "GBP", "JPY", "CHF"]),
                periodo=["2010-01-01", "2025-12-31"], cobertura_minima=MIN_COV)


def main():
    base_sums = HERE / "SNAPSHOT_BASE_SHA256SUMS.txt"
    split = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"),
                 snapshot_base_sha256=hashlib.sha256(base_sums.read_bytes()).hexdigest(),
                 camels_br=camels(), bdg2=bdg2(), **usinas(), **niveis())
    p = HERE / "SPLIT_V055.json"
    p.write_text(json.dumps(split, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V055_SHA256.txt").write_text(f"{h} *SPLIT_V055.json\n", encoding="utf-8", newline="\n")
    print("CAMELS", split["camels_br"]["posicoes"], len(split["camels_br"]["reservadas"]), "subst", split["camels_br"]["substituidas_por_ausencia"],
          "| BDG2", len(split["bdg2"]["reservadas"]), "| eólica elegíveis", split["eolica"]["n_elegiveis"],
          "| solar elegíveis", split["solar"]["n_elegiveis"], "| cp", split["niveis_cp"]["reservadas"],
          "| ecb", split["niveis_ecb"]["reservadas"], "| SHA-256", h)


if __name__ == "__main__":
    main()
