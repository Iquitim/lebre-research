"""dados_v056.py — carregador das séries da validação e da avaliação final da v0.56 (SPLIT_V056.json), com trava: só
carrega séries do sorteio, conferindo o SHA-256 do sorteio. Só para as execuções pré-registradas.

- camels_cl: vazão (mm) e entradas do mesmo dia (precipitação MSWEP, evapotranspiração potencial de Hargreaves,
  temperatura média CR2MET), janela 1990-01-01 a 2014-12-31 (correção 01); vazão negativa = ausente; entradas ausentes
  mantidas no último valor com o passo em quarentena (data_v052._ffill_inputs, a regra do CAMELS-BR).
- bdg2 e camels_br: data_v052 (a construção das avaliações anteriores).
- eolica e solar: LEBRE-V0.54-FINAL-01/final_dados.usina (a construção da v0.55), com o tempo do Open-Meteo gravado em
  data/external_v056/open_meteo."""
import functools
import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
E = RAIZ / "experiments"
SNAP53, SNAP54, SNAP56 = (RAIZ / "data" / f"external_v05{k}" for k in (3, 4, 6))
SPLIT_SHA = "ec9bb01ea6dcb8bc177a55e7729081746b22fbcd86ca35297674e640d10604e3"
JANELA = pd.date_range("1990-01-01", "2014-12-31", freq="D")
ESPERADO = {"camels_cl": (None, None, 3, "persistence"), "bdg2": (24, 168, 2, "seasonal"), "eolica": (24, None, 5, "seasonal"),
            "solar": (24, None, 4, "seasonal"), "camels_br": (None, None, 3, "persistence")}


@functools.lru_cache(maxsize=1)
def split():
    p = AQUI / "SPLIT_V056.json"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == SPLIT_SHA, "SPLIT_V056.json alterado"
    return json.loads(p.read_text(encoding="utf-8"))


def series(uso):
    """[(família, id)] da validação ("validacao") ou da avaliação final ("final")"""
    S = split()
    if uso == "validacao":
        return [("camels_cl", g) for g in S["camels_cl"]["validacao"]] + [("bdg2", m) for m in S["bdg2"]["validacao"]]
    assert uso == "final"
    return ([("camels_cl", g) for g in S["camels_cl"]["final"]] + [("bdg2", m) for m in S["bdg2"]["final"]]
            + [("eolica", u["nome"]) for u in S["eolica"]["reservadas"]] + [("solar", u["nome"]) for u in S["solar"]["reservadas"]]
            + [("camels_br", str(g)) for g in S["camels_br"]["reservadas"]])


def _permitida(familia, ident):
    return (familia, ident) in set(series("validacao")) | set(series("final"))


@functools.lru_cache(maxsize=4)
def _cl(arquivo):
    z = zipfile.ZipFile(SNAP56 / "camels_cl" / arquivo)
    t = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), sep="\t", index_col=0, encoding="latin-1", low_memory=False)
    t.index = pd.to_datetime(t.index.astype(str).str.strip().str.strip('"'))
    t.columns = [str(c).strip().strip('"') for c in t.columns]
    return t.apply(pd.to_numeric, errors="coerce").reindex(JANELA)


def _f54():
    sp = importlib.util.spec_from_file_location("final_dados_v054", E / "LEBRE-V0.54-FINAL-01" / "final_dados.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def _d52():
    p = str(E / "LEBRE-V0.52-PROTO-01")
    if p not in sys.path:
        sys.path.insert(0, p)
    import data_v052
    return data_v052


def carregar(familia, ident):
    assert _permitida(familia, ident), f"{familia}:{ident} fora do sorteio da v0.56"
    if familia == "camels_cl":
        D = _d52()
        y = _cl("3_CAMELScl_streamflow_mm.zip")[ident].to_numpy(float)
        y[y < 0] = np.nan
        X = np.column_stack([_cl(f)[ident].to_numpy(float) for f in ("6_CAMELScl_precip_mswep.zip", "12_CAMELScl_pet_hargreaves.zip",
                                                                      "10_CAMELScl_tmean_cr2met.zip")])
        X, q = D._ffill_inputs(X)
        s = dict(nome=f"camels_cl:{ident}", y=y, X=X, q=np.asarray(q, bool), season=None, season2=None)
    elif familia in ("bdg2", "camels_br"):
        D = _d52()
        d = D.load(f"{'camels' if familia == 'camels_br' else 'bdg2'}:{ident}", final=True)   # sorteio da v0.56
        s = dict(nome=d["task"], y=np.asarray(d["y"], float), X=np.asarray(d["X"], float), q=np.asarray(d["quarantine"], bool),
                 season=d["season"], season2=168 if familia == "bdg2" else None)
    else:
        F = _f54()
        pasta = SNAP54 / "ons_fator_2026" if familia == "solar" else SNAP53 / "ons_fator"
        ons = sorted(str(p) for p in pasta.iterdir())
        horas = F.HORAS_SOLAR if familia == "solar" else F.HORAS_EOLICA
        safe = "".join(c if c.isalnum() else "_" for c in ident)
        r = F.usina(familia, ident, ons, str(SNAP56 / "open_meteo" / f"{familia}_{safe}.json"), horas)
        s = dict(nome=r["nome"], y=r["y"], X=r["X"], q=None, season=r["season"], season2=r["season2"])
    season, season2, d, ref = ESPERADO[familia]
    assert s["season"] == season and s["season2"] == season2 and s["X"].shape[1] == d, (familia, ident, s["X"].shape)
    assert len(s["y"]) == s["X"].shape[0] and np.isfinite(s["y"]).mean() > 0.5, (familia, ident)
    return s, ref


if __name__ == "__main__":                                      # só estrutura: formas e frações, nenhum valor
    for uso in ("validacao", "final"):
        print(uso, len(series(uso)))
    for fam, i in [series("validacao")[0], series("validacao")[-1]]:
        s, ref = carregar(fam, i)
        print(fam, i, len(s["y"]), s["X"].shape, ref, "fração de alvos presentes", round(float(np.isfinite(s["y"]).mean()), 3))
    try:
        carregar("camels_cl", "1001001"); print("FALHOU A TRAVA")
    except AssertionError as ex:
        print("trava ok:", ex)
