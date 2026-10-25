#!/usr/bin/env python3
"""make_split_v056.py — sorteio dos dados de validação e da avaliação final da v0.56 (regras em SPLIT_RULES.md).

Usa só metadados, cobertura (fração de valores não faltantes) e sementes; os valores das séries não são inspecionados.

Mapeamento dos critérios do CAMELS-CL (SPLIT_RULES.md, §3) para as colunas do arquivo de atributos, registrado antes de
calcular a elegibilidade. Escalas lidas do arquivo: as frações de cobertura do solo estão em porcentagem (somam 100);
o grau de intervenção é uma razão (máximo 27,7 no arquivo).
  grande barragem        -> big_dam == 0
  grau de intervenção    -> interv_degree < 0.10
  fração impermeável     -> imp_frac < 5      (%)
  fração de cultivo      -> crop_frac < 20    (%)
  plantação exótica      -> fp_frac < 20      (%)
  fração glaciar         -> lc_glacier < 5    (%)
Requer a fase base de snapshot_v056.py.
"""
import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E = ROOT / "experiments"
D52, D53, D54, D56 = (ROOT / "data" / f"external_v05{k}" for k in (2, 3, 4, 6))
CL = D56 / "camels_cl"
SEED_CL, SEED_EOLICA, SEED_SOLAR, SEED_BDG2 = 5662, 5663, 5664, 5203
MIN_COV = 0.9                                                    # BDG2, como na v0.52
JANELA = pd.date_range("1990-01-01", "2015-12-31", freq="D")
_s = importlib.util.spec_from_file_location("make_split_v054", E / "LEBRE-V0.54-DATA-01" / "make_split_v054.py")
M54 = importlib.util.module_from_spec(_s); _s.loader.exec_module(M54)


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _cl_tabela(arquivo):
    z = zipfile.ZipFile(CL / arquivo)
    t = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), sep="\t", index_col=0, encoding="latin-1", low_memory=False)
    t.index = pd.to_datetime(t.index.astype(str).str.strip().str.strip('"'))
    t.columns = [str(c).strip().strip('"') for c in t.columns]
    return t


def _cobertura(t):
    """fração de dias da janela com valor numérico, por bacia (só presença de valor)"""
    v = t.apply(pd.to_numeric, errors="coerce").reindex(JANELA)
    return v.notna().mean()


def camels_cl():
    z = zipfile.ZipFile(CL / "1_CAMELScl_attributes.zip")
    a = pd.read_csv(io.BytesIO(z.read("1_CAMELScl_attributes.txt")), sep="\t", index_col=0, encoding="latin-1")
    a.columns = [str(c).strip().strip('"') for c in a.columns]
    num = lambda k: pd.to_numeric(a.loc[k], errors="coerce")                                    # noqa: E731
    natural = ((num("big_dam") == 0) & (num("interv_degree") < 0.10) & (num("imp_frac") < 5) & (num("crop_frac") < 20)
               & (num("fp_frac") < 20) & (num("lc_glacier") < 5))
    cob = {"vazao": _cobertura(_cl_tabela("3_CAMELScl_streamflow_mm.zip")),
           "precip_mswep": _cobertura(_cl_tabela("6_CAMELScl_precip_mswep.zip")),
           "tmean_cr2met": _cobertura(_cl_tabela("10_CAMELScl_tmean_cr2met.zip")),
           "pet_hargreaves": _cobertura(_cl_tabela("12_CAMELScl_pet_hargreaves.zip"))}
    ids = [g for g in a.columns if natural.get(g, False)]
    ok = [g for g in ids if cob["vazao"].get(g, 0) >= 0.85 and all(cob[k].get(g, 0) >= 0.99 for k in cob if k != "vazao")]
    pick = [str(x) for x in np.random.default_rng(SEED_CL).permutation(sorted(ok, key=int))]
    final, val = pick[:30], pick[30:50]
    return dict(semente=SEED_CL, n_bacias=a.shape[1], n_quase_naturais=len(ids), n_elegiveis=len(pick),
                janela=["1990-01-01", "2015-12-31"], final_posicoes="0-29", validacao_posicoes="30-49",
                final=final, validacao=val, permutacao=pick,
                cobertura={g: {k: round(float(cob[k].get(g, 0)), 4) for k in cob} for g in final + val})


def bdg2():
    z = zipfile.ZipFile(D52 / "bdg2" / "building-data-genome-project-2-v1.0.zip")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov, nz = m.notna().mean(), (m.fillna(0) != 0).mean()
        meters += [f"{kind}:{b}" for b in cov[(cov >= MIN_COV) & (nz >= 0.5)].index]
    pick = [str(x) for x in np.random.default_rng(SEED_BDG2).permutation(sorted(meters))]
    v55 = _json(E / "LEBRE-V0.55-DATA-02" / "SPLIT_V055.json")["bdg2"]
    assert v55["posicoes"] == "175-204" and set(pick[175:205]) == set(v55["reservadas"]), "reserva v0.55 BDG2 diferente"
    site = lambda m: m.split(":")[1].split("_")[0]                                                      # noqa: E731
    val, fin = pick[205:235], pick[235:265]
    return dict(semente=SEED_BDG2, n_elegiveis=len(pick), validacao_posicoes="205-234", final_posicoes="235-264",
                validacao=sorted(val), final=sorted(fin),
                sites_compartilhados_com_series_ja_usadas=sorted({site(m) for m in val + fin} & {site(m) for m in pick[:205]}))


def usinas():
    import glob
    a2425 = sorted(glob.glob(str(D53 / "ons_fator" / "*.csv"))); a26 = sorted(glob.glob(str(D54 / "ons_fator_2026" / "*.csv")))
    assert len(a2425) == 24 and len(a26) == 9
    m25 = M54._ons(a2425, "2024-01-01 00:00", "2025-12-31 23:00")
    m26 = M54._ons(a26, "2026-01-01 00:00", "2026-09-30 23:00")
    v53, v54, v55 = (_json(E / f"LEBRE-V0.5{k}-DATA-0{j}" / f"SPLIT_V05{k}.json") for k, j in ((3, 1), (4, 1), (5, 2)))
    out = {}
    base = m25[(m25.tipo == "Eólica") & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95)]
    r53, r54, r55 = ({u["nome"] for u in v["eolica"]["reservadas"]} for v in (v53, v54, v55))
    lab = list(base[~base.index.isin(r53)].sort_values("cap", ascending=False).head(M54.N_LAB_POR_TIPO).index)
    assert lab == v54["eolica"]["excluidas_lab"], "lista das eólicas do Lab diferente da v0.54"
    m = base[(base.cap >= 100) & ~base.index.isin(r53) & ~base.index.isin(lab) & ~base.index.isin(r54)]
    assert len(m) == v55["eolica"]["n_elegiveis"], "elegíveis eólicas diferentes da v0.55"
    m = m[~m.index.isin(r55)]
    nomes = list(np.random.default_rng(SEED_EOLICA).permutation(sorted(m.index)))[:8]
    out["eolica"] = dict(semente=SEED_EOLICA, periodo=["2024-01-01", "2025-12-31"], n_elegiveis=len(m),
                         excluidas=dict(lab=len(lab), reserva_v053=len(r53), reserva_v054=len(r54), reserva_v055=len(r55)),
                         reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                          lon=float(m.loc[k, "lon"]), completude=round(float(m.loc[k, "completude"]), 4)) for k in nomes])
    base = m25[(m25.tipo == "Solar") & m25.lat.notna() & m25.lon.notna() & (m25.completude >= 0.95) & (m25.cap >= 100)]
    c26 = m26["completude"].reindex(base.index).fillna(0)
    s54, s55 = ({u["nome"] for u in v["solar"]["reservadas"]} for v in (v54, v55))
    m = base[(c26 >= 0.95) & ~base.index.isin(s54)]
    assert len(m) == v55["solar"]["n_elegiveis"], "elegíveis solares diferentes da v0.55"
    m = m[~m.index.isin(s55)]
    nomes = list(np.random.default_rng(SEED_SOLAR).permutation(sorted(m.index)))[:8]
    out["solar"] = dict(semente=SEED_SOLAR, periodo=["2026-01-01", "2026-09-30"], n_elegiveis=len(m),
                        excluidas=dict(reserva_v054=len(s54), reserva_v055=len(s55)), observacao="separação no tempo",
                        reservadas=[dict(nome=k, cap=round(float(m.loc[k, "cap"]), 1), lat=float(m.loc[k, "lat"]),
                                         lon=float(m.loc[k, "lon"]), completude_2026=round(float(c26[k]), 4)) for k in nomes])
    return out


def camels_br():
    sys.path.insert(0, str(E / "LEBRE-V0.56-DIAG-01"))
    import diag_dados as DD
    pick = DD.permutacao()
    v55 = _json(E / "LEBRE-V0.55-DATA-02" / "SPLIT_V055.json")["camels_br"]
    assert v55["posicoes"] == "190-219" and set(pick[190:220]) == set(v55["reservadas"])
    zq = zipfile.ZipFile(D52 / "camels_br" / "03_CAMELS_BR_streamflow_selected_catchments.zip")
    no_arquivo = {int(Path(n).name.split("_")[0]) for n in zq.namelist() if n.endswith(".txt") and Path(n).name[0].isdigit()}
    res = [g for g in pick[220:] if g in no_arquivo]
    return dict(semente=5202, posicoes="220-236", reservadas=sorted(res), ausentes_do_arquivo=[g for g in pick[220:] if g not in no_arquivo])


def main():
    base_sums = HERE / "SNAPSHOT_BASE_SHA256SUMS.txt"
    split = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"),
                 snapshot_base_sha256=hashlib.sha256(base_sums.read_bytes()).hexdigest(),
                 camels_cl=camels_cl(), bdg2=bdg2(), **usinas(), camels_br=camels_br())
    p = HERE / "SPLIT_V056.json"
    p.write_text(json.dumps(split, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V056_SHA256.txt").write_text(f"{h} *SPLIT_V056.json\n", encoding="utf-8", newline="\n")
    c = split["camels_cl"]
    print("CAMELS-CL: bacias", c["n_bacias"], "quase naturais", c["n_quase_naturais"], "elegíveis", c["n_elegiveis"],
          "final", len(c["final"]), "validação", len(c["validacao"]), "| BDG2", len(split["bdg2"]["validacao"]), len(split["bdg2"]["final"]),
          "| eólica", split["eolica"]["n_elegiveis"], "| solar", split["solar"]["n_elegiveis"],
          "| CAMELS-BR", len(split["camels_br"]["reservadas"]), "| SHA-256", h)


if __name__ == "__main__":
    main()
