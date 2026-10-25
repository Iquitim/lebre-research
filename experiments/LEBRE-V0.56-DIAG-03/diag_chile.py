#!/usr/bin/env python3
"""diag_chile.py — execuções e análise do diagnóstico do Chile (PLANO_DIAG_CHILE.md, §3 e §4).

  python diag_chile.py run       CL-V (20 bacias chilenas da validação): R0, R1, R2, A, C5, C0, com a gravação da M1;
                                 D-A (30 bacias brasileiras, evapotranspiração potencial pet_gleam no lugar da real): A, C5, R0
  python diag_chile.py analise   ->  DIAG_CHILE_RESULTADO.json

Código: ArxGen/run_arx/calib_arx de LEBRE-V0.56-DIAG-01/diag_run.py (conferida bit a bit contra a ArxRls da comparação);
Lebre056 do protótipo congelado (commit ef77728, worktree limpo, LEBRE056_PROTO); C0 = Lebre056 "A" com a M1
precision056.DormantPrecisionParam(every=1, nbands=5, ylags=3, clip=False) (a M5 do DIAG-02).
"""
import importlib.util
import json
import math
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
RAIZ = E.parent
OUT = AQUI / "preds"
COMMIT = "ef77728"
PET = RAIZ / "data" / "external_v056" / "camels_br_pet" / "07_CAMELS_BR_potential_evapotransp.zip"
for p in (E / "LEBRE-V0.56-DATA-01", E / "LEBRE-V0.56-DIAG-01", E / "LEBRE-V0.52-PROTO-01"):
    sys.path.insert(0, str(p))
SEMENTE, BLOCO, INI = 2026102903, 30, 0.30


def proto():
    p = os.environ["LEBRE056_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")
    if p not in sys.path:
        sys.path.insert(0, p)


def serie_cl(gid):
    import dados_v056 as D
    assert ("camels_cl", gid) in set(D.series("validacao")), "só as bacias chilenas da validação"
    s, _ = D.carregar("camels_cl", gid)
    return s


def serie_br_pet(gid):
    """D-A com pet_gleam no lugar de aet_gleam; o resto como data_v052.load_camels"""
    import diag_dados as DD
    import data_v052 as D
    C, pos = DD.conjuntos()
    assert int(gid) in C["A"] and pos[int(gid)] < DD.LIMITE
    import io
    import zipfile
    q = D._camels_file("03_CAMELS_BR_streamflow_selected_catchments.zip", "03_CAMELS_BR_streamflow_selected_catchments", gid, "streamflow")
    p = D._camels_file("05_CAMELS_BR_precipitation.zip", "05_CAMELS_BR_precipitation", gid, "precipitation")
    tt = D._camels_file("09_CAMELS_BR_temperature.zip", "09_CAMELS_BR_temperature", gid, "temperature")
    z = zipfile.ZipFile(PET)
    e = pd.read_csv(io.BytesIO(z.read(f"07_CAMELS_BR_potential_evapotransp/{gid}_potential_evapotransp.txt")), sep=r"\s+")
    e.index = pd.to_datetime(dict(year=e.year, month=e.month, day=e.day))
    idx = q.index
    y = q.streamflow_mm.reindex(idx).to_numpy(float); y[y < 0] = np.nan
    X = np.column_stack([p.p_mswep.reindex(idx), e.pet_gleam.reindex(idx), tt.tmean_era5land.reindex(idx)]).astype(float)
    X, qf = D._ffill_inputs(X)
    return dict(nome=f"camels:{gid}:pet", y=y, X=X, q=np.asarray(qf, bool))


def rodar_lebre(variante, s, gravar=False):
    from lebre056.model056 import Lebre056
    from lebre056.precision056 import DormantPrecisionParam
    m = Lebre056(3, season=None, season2=None, reference="persistence", variant="A" if variante in ("A", "C0") else "C5")
    if variante == "C0":
        m._m1 = DormantPrecisionParam(m.n_inputs, every=1, nbands=5, ylags=3, clip=False)
    y, X, q = s["y"], s["X"], s["q"]
    T = len(y); f = np.full(T, np.nan)
    G = {k: np.full(T, np.nan) for k in ("omega", "dorme", "e_livre", "nucleo")} if gravar else None
    for t in range(T):
        f[t] = m.predict(X[t]).value
        if gravar:
            m1 = m._m1
            G["omega"][t] = m1.weight(); G["dorme"][t] = float(m1.dormant); G["nucleo"][t] = m._L_core
            G["e_livre"][t] = np.nan if m1.e is None else m1.e                  # C5 e C0 não recortam: e = E livre
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]))
    sel = None if m._m1.sel is None else [int(i) for i in m._m1.sel]
    return f, G, dict(custo=m.cost_per_step, m1_entradas_final=sel, estrutura=m.structure)


def job(arg):
    parte, gid = arg
    base = OUT / f"{parte}__{gid}"
    if base.with_suffix(".json").exists():
        return arg, "já feito"
    try:
        t0 = time.time(); proto()
        import comp_dev as CD
        import diag_run as DR
        s = serie_cl(gid) if parte == "CLV" else serie_br_pet(gid)
        y = s["y"]; Xs = CD._scaled_inputs(pd.DataFrame(s["X"]).ffill().fillna(0.0).to_numpy(float)); idx = CD._calib_n(y)
        prev, info = {}, {}
        for cod in (("R0", "R1", "R2") if parte == "CLV" else ("R0",)):
            par = DR.calib_arx(Xs, y, DR.ESCADA[cod], idx)
            prev[cod], fp, ok = DR.run_arx(Xs, y, DR.ESCADA[cod], par); info[cod] = dict(par=par, ok=ok)
        for v in (("A", "C5", "C0") if parte == "CLV" else ("A", "C5")):
            f, G, inf = rodar_lebre(v, s, gravar=(parte == "CLV" and v != "A"))
            prev[v] = f; info[v] = inf
            if G is not None:
                for k, a in G.items():
                    prev[f"{v}_{k}"] = a
        np.savez_compressed(base.with_suffix(".npz"), y=y, **prev)
        info["_"] = dict(parte=parte, gid=str(gid), T=len(y))
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
        return arg, f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg, "ERRO " + traceback.format_exc()[-800:]


def run():
    import dados_v056 as D
    import diag_dados as DD
    C, _ = DD.conjuntos()
    ts = [("CLV", g) for f, g in D.series("validacao") if f == "camels_cl"] + [("DAPET", g) for g in C["A"]]
    OUT.mkdir(exist_ok=True)
    print(len(ts), "tarefas", flush=True)
    with ProcessPoolExecutor(14) as ex:
        for t, st in ex.map(job, ts, chunksize=1):
            print(t, st, flush=True)


# ------------------------------------------------------------------ análise
def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", E / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def contraste(R_, S, a, b, tag, persist=False):
    logs, rr = [], []
    for si, s in enumerate(S):
        y = s["y"]; Pa = s["P"][a]
        Pb = np.r_[np.nan, pd.Series(y).ffill().to_numpy()[:-1]] if persist else s["P"][b]
        ok = np.isfinite(y) & np.isfinite(Pa) & np.isfinite(Pb); ok[: int(INI * len(y))] = False
        if ok.sum() < 50:
            continue
        p, r = R_.reps((y[ok] - Pa[ok]) ** 2, (y[ok] - Pb[ok]) ** 2, BLOCO, np.random.default_rng([SEMENTE, tag, si]))
        logs.append(math.log(p)); rr.append(r)
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), razao=float(np.exp(np.mean(logs))),
                ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))], por_serie=[float(math.exp(v)) for v in logs])


def analise():
    R_ = _cmp()
    S = {}
    for f in sorted(OUT.glob("*.json")):
        info = json.loads(f.read_text(encoding="utf-8")); Z = np.load(f.with_suffix(".npz"))
        S.setdefault(info["_"]["parte"], []).append(dict(info=info, y=Z["y"], P={k: v for k, v in Z.items() if k != "y"}))
    CLV, DAP = S["CLV"], S["DAPET"]
    res = {"n": {k: len(v) for k, v in S.items()}}
    res["H1_G_CL_v055_sobre_R0"] = contraste(R_, CLV, "A", "R0", 1)
    res["H2_CL_R1_sobre_R0"] = contraste(R_, CLV, "R1", "R0", 2)
    res["CL_R2_sobre_R0"] = contraste(R_, CLV, "R2", "R0", 3)
    res["CL_v055_sobre_C5"] = contraste(R_, CLV, "A", "C5", 4)
    res["CL_v055_sobre_C0"] = contraste(R_, CLV, "A", "C0", 5)
    res["CL_C5_sobre_R0"] = contraste(R_, CLV, "C5", "R0", 6)
    res["CL_Elivre_C0_sobre_R0"] = contraste(R_, CLV, "C0_e_livre", "R0", 7)
    res["CL_v055_sobre_persistencia"] = contraste(R_, CLV, "A", None, 8, persist=True)
    res["CL_R0_sobre_persistencia"] = contraste(R_, CLV, "R0", None, 9, persist=True)
    res["H3_DA_pet_v055_sobre_C5"] = contraste(R_, DAP, "A", "C5", 10)
    res["H3_DA_pet_G_v055_sobre_R0"] = contraste(R_, DAP, "A", "R0", 11)
    om, dm, ent = [], [], []
    for s in CLV:
        y = s["y"]; ok = np.isfinite(y); ok[: int(INI * len(y))] = False
        om.append(float(np.nanmedian(s["P"]["C5_omega"][ok]))); dm.append(float(np.mean(s["P"]["C5_dorme"][ok] > 0)))
        ent.append(s["info"]["C5"]["m1_entradas_final"])
    res["H4_CL_C5"] = dict(omega_mediano_por_serie=om, omega_mediana=float(np.median(om)), fracao_dormente_mediana=float(np.median(dm)),
                           series_que_dormem=int(sum(d > 0 for d in dm)), entradas_finais=ent)
    D2 = E / "LEBRE-V0.56-DIAG-02" / "preds"                         # referência brasileira (D-A) para H4
    om_br, dm_br = [], []
    for f in sorted(D2.glob("A__*.npz")):
        Z = np.load(f); y = Z["y"]; ok = np.isfinite(y); ok[: int(INI * len(y))] = False
        om_br.append(float(np.nanmedian(Z["M5_omega"][ok]))) if "M5_omega" in Z else None
        dm_br.append(float(np.mean(Z["M0_dorme"][ok] > 0)))
    res["H4_DA_referencia"] = dict(omega_mediana_M5=float(np.median(om_br)) if om_br else None, fracao_dormente_mediana_M0=float(np.median(dm_br)))
    # descritivo por bacia
    import io
    import zipfile
    from scipy.stats import spearmanr
    z = zipfile.ZipFile(RAIZ / "data" / "external_v056" / "camels_cl" / "1_CAMELScl_attributes.zip")
    a = pd.read_csv(io.BytesIO(z.read("1_CAMELScl_attributes.txt")), sep="\t", index_col=0, encoding="latin-1")
    a.columns = [str(c).strip().strip('"') for c in a.columns]
    g5 = [math.log(1 / x) for x in res["CL_v055_sobre_C5"]["por_serie"]]
    gR = [math.log(x) for x in res["H1_G_CL_v055_sobre_R0"]["por_serie"]]
    ids = [s["info"]["_"]["gid"] for s in CLV]
    desc = {}
    for att in ("frac_snow_mswep", "aridity_mswep", "baseflow_index", "p_seasonality_mswep", "area", "high_prec_freq_mswep"):
        v = [float(pd.to_numeric(a.loc[att, g], errors="coerce")) for g in ids]
        r1 = spearmanr(g5, v); r2 = spearmanr(gR, v)
        desc[att] = dict(ganho_C5_rho=float(r1[0]), ganho_C5_p=float(r1[1]), G_rho=float(r2[0]), G_p=float(r2[1]),
                         mediana=float(np.median(v)))
    res["descritivo_CL"] = desc
    (AQUI / "DIAG_CHILE_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for k, v in res.items():
        if isinstance(v, dict) and "razao" in v:
            print(f"{k:32s} {v['razao']:.3f} [{v['ic95'][0]:.3f}; {v['ic95'][1]:.3f}] n={v['n']}")
    print("H4:", {k: v for k, v in res["H4_CL_C5"].items() if k != "omega_mediano_por_serie"}); print("H4 ref:", res["H4_DA_referencia"])
    for att, d in desc.items():
        print(f"{att:22s} ganho C5 rho {d['ganho_C5_rho']:+.2f} (p {d['ganho_C5_p']:.2f})  G rho {d['G_rho']:+.2f} (p {d['G_p']:.2f})  mediana {d['mediana']:.3g}")


if __name__ == "__main__":
    {"run": run, "analise": analise}[sys.argv[1]]()
