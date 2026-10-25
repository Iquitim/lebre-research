#!/usr/bin/env python3
"""diag_m1_analise.py — análise do diagnóstico da M1 (PLANO_DIAG_M1.md, §4 e §5). Escrito e commitado antes de qualquer
execução das variantes.

Mesma estatística do DIAG-01 (reps de LEBRE-V0.55-COMP-01/comp_analise.py, blocos de 30 dias, média do log da razão por
série, IC pelos percentis da média das réplicas, p bilateral, Holm). R0 vem das previsões do DIAG-01. As previsões
internas (E livre) só existem em parte dos passos: os contrastes com elas usam a máscara comum restrita aos passos em que
existem, e isso é dito no resultado.
Uso: python diag_m1_analise.py {A|B}   ->  DIAG_M1_RESULTADO_<conjunto>.json
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
D1 = AQUI.parent / "LEBRE-V0.56-DIAG-01"
CMP = AQUI.parent / "LEBRE-V0.55-COMP-01" / "comp_analise.py"
SEMENTE = {"A": 2026102802, "B": 2026102803}
BLOCO, TEST_FRAC = 30, 0.30
VAR = ("M1", "M2", "M3", "M4", "M5")


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", CMP)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def carregar(conj):
    sys.path.insert(0, str(D1))
    import diag_dados as DD
    C, pos = DD.conjuntos()
    S = []
    for gid in C[conj]:
        Z = dict(np.load(AQUI / "preds" / f"{conj}__{gid}.npz"))
        Z1 = np.load(D1 / "preds" / f"{conj}__{gid}.npz")
        info = json.loads((AQUI / "preds" / f"{conj}__{gid}.json").read_text(encoding="utf-8"))
        assert info["M0_igual_L0_diag01"] and np.array_equal(Z["y"], Z1["y"], equal_nan=True)
        P = {k: v for k, v in Z.items() if k != "y"}; P["R0"] = Z1["R0"]
        s = DD.carregar(gid, C, pos)
        S.append(dict(gid=gid, y=Z["y"], P=P, info=info, chuva=s["X"][:, 0]))
    return S


def base(s, modelos):
    y = s["y"]; ok = np.isfinite(y); ok[: int(TEST_FRAC * len(y))] = False
    for k in modelos:
        ok &= np.isfinite(s["P"][k])
    return ok


def contraste(S, a, b, principais, conj, ci, R_):
    logs, rr, frac = [], [], []
    for si, s in enumerate(S):
        ok0 = base(s, principais); ok = ok0 & np.isfinite(s["P"][a]) & np.isfinite(s["P"][b])
        y = s["y"][ok]
        if len(y) < 50:
            continue
        frac.append(ok.sum() / max(ok0.sum(), 1))
        rng = np.random.default_rng([SEMENTE[conj], ci, si])
        p, r = R_.reps((y - s["P"][a][ok]) ** 2, (y - s["P"][b][ok]) ** 2, BLOCO, rng)
        logs.append(math.log(p)); rr.append(r)
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), log=float(np.mean(logs)), razao=float(np.exp(np.mean(logs))),
                ic95_log=[float(np.quantile(R, 0.025)), float(np.quantile(R, 0.975))],
                p=float(min(1.0, 2 * min((R <= 0).mean(), (R >= 0).mean()))),
                fracao_dos_passos=float(np.median(frac)), por_serie=[float(math.exp(v)) for v in logs])


def chuva_mask(s, ok):
    p = s["chuva"]; molhado = p[np.isfinite(p) & (p > 0)]
    lim = np.quantile(molhado, 0.9) if len(molhado) else np.inf
    ch = np.zeros(len(p), bool); ch[0] = p[0] > lim; ch[1:] = (p[1:] > lim) | (p[:-1] > lim)
    return ok & ch


def main(conj):
    R_ = _cmp(); S = carregar(conj)
    presentes = set.intersection(*[set(s["P"]) for s in S])
    principais = sorted(k for k in presentes if k in ("R0", "M0") + VAR)
    res = {"conjunto": conj, "n_series": len(S), "modelos": principais}
    con = {}
    con["G"] = contraste(S, "M0", "R0", principais, conj, 0, R_)
    fam = [v for v in VAR if v in presentes]
    for i, v in enumerate(fam):
        con[f"M0_vs_{v}"] = contraste(S, "M0", v, principais, conj, 1 + i, R_)
        con[f"{v}_vs_R0"] = contraste(S, v, "R0", principais, conj, 20 + i, R_)
    for c, sg in zip(fam, R_.holm([con[f"M0_vs_{v}"]["p"] for v in fam])):
        con[f"M0_vs_{c}"]["holm"] = bool(sg)
    desc = [("Elivre_M0_vs_R0", "M0_e_raw", "R0"), ("Lp_vs_nucleo", "M0_Lp", "M0_nucleo"), ("saida_vs_Lp", "M0", "M0_Lp")]
    if "M5_e_raw" in presentes:
        desc.append(("Elivre_M5_vs_R0", "M5_e_raw", "R0"))
    for i, (rot, a, b) in enumerate(desc):
        con[rot] = contraste(S, a, b, principais, conj, 40 + i, R_)
    res["contrastes"] = con
    G = con["G"]["log"]
    res["regra1"] = {v: bool(con[f"M0_vs_{v}"]["holm"] and con[f"M0_vs_{v}"]["log"] >= 0.5 * G and con[f"M0_vs_{v}"]["log"] > 0)
                     for v in fam}
    rec, rec_ch, dorm = [], [], []
    for s in S:
        ok = base(s, principais); e, er = s["P"]["M0_e"], s["P"]["M0_e_raw"]
        tem = ok & np.isfinite(er) & np.isfinite(e)
        if tem.sum():
            rec.append(float(np.mean(e[tem] != er[tem])))
            tc = chuva_mask(s, tem)
            if tc.sum():
                rec_ch.append(float(np.mean(e[tc] != er[tc])))
        dorm.append(float(np.mean(s["P"]["M0_dorme"][ok] > 0)))
    res["recorte"] = dict(fracao_mediana=float(np.median(rec)), fracao_mediana_chuva=float(np.median(rec_ch)),
                          series_com_E=len(rec))
    res["dormencia"] = dict(fracao_mediana=float(np.median(dorm)), series_que_dormem=int(sum(d > 0 for d in dorm)))
    res["custo_mediano_razao_M0"] = {v: float(np.median([s["info"][v]["custo"] / s["info"]["M0"]["custo"] for s in S]))
                                     for v in fam}
    res["custo_mediano_M0"] = float(np.median([s["info"]["M0"]["custo"] for s in S]))
    (AQUI / f"DIAG_M1_RESULTADO_{conj}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                        encoding="utf-8", newline="\n")
    for rot, c in con.items():
        print(f"{rot:16s} razão {c['razao']:.3f}  IC log [{c['ic95_log'][0]:+.3f}; {c['ic95_log'][1]:+.3f}]  p {c['p']:.4f}"
              f"  holm {c.get('holm', '-')}  passos {c['fracao_dos_passos']:.2f}")
    print("regra 1:", res["regra1"]); print("recorte:", res["recorte"]); print("dormência:", res["dormencia"])
    print("custo:", res["custo_mediano_M0"], res["custo_mediano_razao_M0"])


if __name__ == "__main__":
    main(sys.argv[1])
