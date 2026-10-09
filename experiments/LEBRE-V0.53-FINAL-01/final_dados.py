"""final_dados.py — tarefas da avaliação final da v0.53 na reserva (PREREG_V053_FINAL.md, seção 3).

Cada família reproduz a construção usada no desenvolvimento:
  camels, bdg2        como na avaliação da v0.52 (LEBRE-V0.52-PROTO-01/data_v052.py, com quarentena das entradas
                      preenchidas); bdg2 com season 24 e season2 168
  solar, eolica       como B01 e B06 do LEBRE Lab: geração verificada do ONS (Fator de Capacidade 2024-2025), tempo
                      ERA5 do Open-Meteo no local da usina; eólica com vento a 100 m em componentes u e v; season 24
  carga               como B02: carga horária por subsistema, tempo na capital; season 24 e season2 168; 2026-01 a 2026-09
  fx_ret, fx_abs,     como C01, C02 e C03: dias úteis 2010-2025; entradas com 1 dia útil de atraso: os outros 3 pares do
  fx_niv              grupo (grupos de 4 na ordem do SPLIT_V053.json) e os juros de 2 e 10 anos (variações ou níveis);
                      fx_ret com referência zero

Os leitores recebem os caminhos dos arquivos, para que o código possa ser testado em séries não reservadas no mesmo
formato antes da execução final (teste_final_dados.py). `conferir` verifica a construção de cada série.
"""
import io
import json
import os
import sys
import zipfile  # noqa: F401  (data_v052 usa)

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
SNAP = os.path.join(RAIZ, "data", "external_v053")
SPLIT = json.load(open(os.path.join(RAIZ, "experiments", "LEBRE-V0.53-DATA-01", "SPLIT_V053.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(RAIZ, "experiments", "LEBRE-V0.52-PROTO-01"))

HORAS_USINAS = pd.date_range("2024-01-01 00:00", "2025-12-31 23:00", freq="h")
HORAS_CARGA = pd.date_range("2026-01-01 00:00", "2026-09-30 23:00", freq="h")
DIAS_FX = pd.bdate_range("2010-01-01", "2025-12-31")
VARS_SOLAR = ["shortwave_radiation", "direct_normal_irradiance", "cloud_cover", "temperature_2m"]
VARS_EOLICA = ["wind_speed_100m", "wind_direction_100m", "wind_speed_10m", "temperature_2m"]
VARS_CARGA = ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "shortwave_radiation", "precipitation"]
FX = list(SPLIT["cambio"]["pares"])
GRUPOS_FX = [FX[:4], FX[4:]]
FAMILIAS = ["camels", "bdg2", "solar", "eolica", "carga", "fx_ret", "fx_abs", "fx_niv"]


def _seguro(nome):
    return "".join(c if c.isalnum() else "_" for c in nome)


def serie(nome, alvo, entradas, season=None, season2=None, freq="h"):
    """Como lab.real.serie (LEBRE Lab): alinha alvo e entradas na grade comum; lacunas viram NaN."""
    ini, fim = max(alvo.index.min(), entradas.index.min()), min(alvo.index.max(), entradas.index.max())
    idx = alvo.index[(alvo.index >= ini) & (alvo.index <= fim)] if freq is None else pd.date_range(ini, fim, freq=freq)
    a = alvo[~alvo.index.duplicated()].reindex(idx)
    e = entradas[~entradas.index.duplicated()].reindex(idx)
    return dict(nome=nome, y=a.to_numpy(float), X=e.to_numpy(float), season=season, season2=season2,
                entradas=list(e.columns), inicio=str(idx[0]), fim=str(idx[-1]), quarantine=None)


def tempo(arq, variaveis):
    """Como lab.fontes.open_meteo: DataFrame horário das variáveis de um arquivo JSON do Open-Meteo."""
    d = json.load(open(arq, encoding="utf-8"))["hourly"]
    return pd.DataFrame({k: d[k] for k in variaveis}, index=pd.to_datetime(d["time"])).astype(float)


def vento_uv(vel, dire):
    r = np.deg2rad(dire)
    return -vel * np.sin(r), -vel * np.cos(r)


# ------------------------------------------------------------------ ONS: usinas
_GER = {}


def geracao_ons(arquivos):
    """Como lab.usinas._tabela: geração verificada horária por usina/conjunto, na grade 2024-2025."""
    chave = tuple(arquivos)
    if chave not in _GER:
        df = pd.concat([pd.read_csv(a, sep=";", decimal=".") for a in arquivos], ignore_index=True)
        df["din_instante"] = pd.to_datetime(df["din_instante"])
        df = df[(df["din_instante"] >= HORAS_USINAS[0]) & (df["din_instante"] <= HORAS_USINAS[-1])]
        _GER[chave] = df.pivot_table(index="din_instante", columns="nom_usina_conjunto",
                                     values="val_geracaoverificada").reindex(HORAS_USINAS)
    return _GER[chave]


def usina(tipo, nome, arquivos_ons, arq_tempo):
    ger = geracao_ons(arquivos_ons)[nome]
    if tipo == "solar":
        t = tempo(arq_tempo, VARS_SOLAR)
    else:
        t = tempo(arq_tempo, VARS_EOLICA)
        uu, vv = vento_uv(t["wind_speed_100m"], t["wind_direction_100m"])
        t = t.assign(vento100_u=uu, vento100_v=vv).drop(columns=["wind_direction_100m"])
    return serie(nome, ger, t, season=24)


# ------------------------------------------------------------------ ONS: carga
def carga(sub, arq_carga, arq_tempo, horas=HORAS_CARGA):
    df = pd.read_csv(arq_carga, sep=";", decimal=".")
    df["din_instante"] = pd.to_datetime(df["din_instante"])
    c = df.pivot_table(index="din_instante", columns="nom_subsistema", values="val_cargaenergiahomwmed")[sub]
    c = c[(c.index >= horas[0]) & (c.index <= horas[-1])]
    return serie(f"{sub}_{horas[0].year}", c, tempo(arq_tempo, VARS_CARGA), season=24, season2=168)


# ------------------------------------------------------------------ câmbio (FRED)
def fred_csv(arq):
    df = pd.read_csv(arq)
    return pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(), index=pd.to_datetime(df.iloc[:, 0])).sort_index()


def _cal(s, dias):
    return s[~s.index.duplicated()].reindex(dias)


def _retorno(p):
    r = 100 * np.log(p.ffill()).diff()
    r[p.isna()] = np.nan
    return r


def _variacao(p):
    d = p.ffill().diff()
    d[p.isna()] = np.nan
    return d


def cambio(tipo, alvo, grupo, arqs, dias=DIAS_FX):
    """tipo: fx_ret | fx_abs | fx_niv; grupo: os 4 pares; arqs: {série FRED: caminho}, com DGS2 e DGS10."""
    n = pd.DataFrame({s: _cal(fred_csv(arqs[s]), dias) for s in grupo} |
                     {"juro_2a": _cal(fred_csv(arqs["DGS2"]), dias), "juro_10a": _cal(fred_csv(arqs["DGS10"]), dias)})
    outros = [a for a in grupo if a != alvo]
    if tipo == "fx_niv":
        ent = n[outros + ["juro_2a", "juro_10a"]].shift(1)
        s = serie(f"nivel_{alvo}", n[alvo], ent, freq=None)
    else:
        r = pd.DataFrame({a: _retorno(n[a]) for a in grupo} | {f"d_{j}": _variacao(n[j]) for j in ("juro_2a", "juro_10a")})
        if tipo == "fx_abs":
            r = r.abs()
        ent = r[outros + ["d_juro_2a", "d_juro_10a"]].shift(1)
        s = serie(("abs_" if tipo == "fx_abs" else "") + alvo, r[alvo], ent, freq=None)
    s["zero_baseline"] = tipo == "fx_ret"
    return s


# ------------------------------------------------------------------ CAMELS-BR e BDG2 (data_v052)
def v052(tarefa, final):
    import data_v052 as D
    d = D.load(tarefa, final=final)
    return dict(nome=tarefa, y=np.asarray(d["y"], float), X=np.asarray(d["X"], float), season=d["season"],
                season2=168 if tarefa.startswith("bdg2:") else None, entradas=list(d["names"]),
                quarantine=np.asarray(d["quarantine"], bool), zero_baseline=False)


# ------------------------------------------------------------------ tarefas da reserva
def tarefas():
    t = [("camels", str(g)) for g in SPLIT["camels_br"]["reservadas"]]
    t += [("bdg2", m) for m in SPLIT["bdg2"]["reservadas"]]
    t += [("solar", u["nome"]) for u in SPLIT["solar"]["reservadas"]]
    t += [("eolica", u["nome"]) for u in SPLIT["eolica"]["reservadas"]]
    t += [("carga", s) for s in SPLIT["carga"]["subsistemas"]]
    t += [(f, p) for f in ("fx_ret", "fx_abs", "fx_niv") for p in FX]
    return t


def carregar(familia, ident):
    """Só na execução final pré-registrada (final=True nos leitores do v0.52)."""
    if familia == "camels":
        s = v052(f"camels:{ident}", final=True)
    elif familia == "bdg2":
        s = v052(f"bdg2:{ident}", final=True)
    elif familia in ("solar", "eolica"):
        u = next(x for x in SPLIT[familia]["reservadas"] if x["nome"] == ident)
        ons = sorted(os.path.join(SNAP, "ons_fator", f) for f in os.listdir(os.path.join(SNAP, "ons_fator")))
        s = usina(familia, u["nome"], ons, os.path.join(SNAP, "open_meteo", f"{familia}_{_seguro(u['nome'])}.json"))
        s["zero_baseline"] = False
    elif familia == "carga":
        s = carga(ident, os.path.join(SNAP, "ons_carga", "CURVA_CARGA_2026.csv"),
                  os.path.join(SNAP, "open_meteo", f"carga_{ident}.json"))
        s["zero_baseline"] = False
    else:
        grupo = next(g for g in GRUPOS_FX if ident in g)
        arqs = {x: os.path.join(SNAP, "fred", f"{x}.csv") for x in grupo + ["DGS2", "DGS10"]}
        s = cambio(familia, ident, grupo, arqs)
    s["familia"] = familia
    conferir(s, familia)
    return s


ESPERADO = {  # season, season2, d, passos (None = não fixo), referência
    "camels": (None, None, 3, None, "persistencia"),
    "bdg2": (24, 168, 2, None, "sazonal"),
    "solar": (24, None, 4, len(HORAS_USINAS), "sazonal"),
    "eolica": (24, None, 5, len(HORAS_USINAS), "sazonal"),
    "carga": (24, 168, 5, len(HORAS_CARGA), "sazonal"),
    "fx_ret": (None, None, 5, len(DIAS_FX), "zero"),
    "fx_abs": (None, None, 5, len(DIAS_FX), "persistencia"),
    "fx_niv": (None, None, 5, len(DIAS_FX), "persistencia"),
}


def referencia(s):
    return "zero" if s.get("zero_baseline") else ("sazonal" if s.get("season") else "persistencia")


def conferir(s, familia, passos=True):
    """Conferência da construção (motivo: errata do ciclo nas validações 4 e 5 do LEBRE Lab)."""
    season, season2, d, T, ref = ESPERADO[familia]
    assert s["season"] == season, (familia, "season", s["season"])
    assert s["season2"] == season2, (familia, "season2", s["season2"])
    assert s["X"].shape[1] == d, (familia, "d", s["X"].shape)
    assert len(s["y"]) == s["X"].shape[0], (familia, "tamanhos")
    if passos and T is not None:
        assert len(s["y"]) == T, (familia, "passos", len(s["y"]), T)
    assert referencia(s) == ref, (familia, "referência", referencia(s))
    assert np.isfinite(s["y"]).mean() > 0.5, (familia, "alvo quase todo faltante")
