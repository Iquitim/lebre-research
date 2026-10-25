#!/usr/bin/env python3
"""dev_analise.py — análise da etapa LEBRE-V0.56-DEV-01 (PLANO_DEV_M1_BARATA.md, §4 e §5). Escrito e commitado antes de
qualquer execução do banco.

- E20: por série, m2_dev.par_bootstrap(y, variante, A, 20% inicial, bloco do E20), exatamente como no critério de precisão
  das rodadas da v0.55 (LEBRE Lab, analises/d1_v055.py); resumo por família pela média das réplicas em log.
- Prédios e bacias: `reps` de LEBRE-V0.55-COMP-01/comp_analise.py, janela de 30% até o fim, blocos de 168 (prédios) e 30
  (bacias); resumo pela média do log da razão por série e IC pela média das réplicas.
- Sementes: 2026102804 (escolha), 2026102805 (replicação).
Roda no ambiente do Lab (para o E20). Uso: <python do Lab> dev_analise.py escolha | replica <Cx>
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "preds"
VARS = ("C0", "C1", "C2", "C3", "C4", "C5", "C6")
SEMENTE = {"escolha": 2026102804, "replica": 2026102805}
BLOCO = {"P": 168, "R": 168, "DA": 30, "DB": 30}
LIM_K1, FRAC_K2, LIM_K3 = 1.02, 0.7, 1.25


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", AQUI.parent / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def carregar(partes):
    S = []
    for f in sorted(OUT.glob("*.json")):
        info = json.loads(f.read_text(encoding="utf-8"))
        if info["_"]["parte"] not in partes:
            continue
        Z = dict(np.load(f.with_suffix(".npz")))
        S.append(dict(info=info, y=Z["y"], P={k: v for k, v in Z.items() if k != "y"}))
    return S


def resumo(logs, rr):
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), geo=float(np.exp(np.mean(logs))), ic95=[float(np.exp(np.quantile(R, 0.025))),
                                                                       float(np.exp(np.quantile(R, 0.975)))])


def fam_e20(S, variantes, semente):
    sys.path.insert(0, str(AQUI))
    import dev_dados as DD
    E20, M2 = DD.e20()
    out = {}
    for fi, fam in enumerate(E20.TODAS):
        ss = sorted([s for s in S if s["info"]["_"]["parte"] == "e20" and s["info"]["_"]["ident"][0] == fam],
                    key=lambda s: s["info"]["_"]["ident"][1])
        if not ss:
            continue
        curtas = fam in E20.CURTAS
        out[fam] = {}
        for vi, v in enumerate(variantes, start=1):
            logs, rr = [], []
            for s in ss:
                k = s["info"]["_"]["ident"][1]; y = s["y"]; ini = int(0.2 * len(y))
                L = E20.bloco_curta(s["info"]["_"]["origem"]) if curtas else E20.bloco(fam)
                p, rep = M2.par_bootstrap(y, s["P"][v], s["P"]["A"], ini, L, np.random.default_rng([semente, fi, k, vi]))
                if np.isfinite(p) and p > 0:
                    logs.append(math.log(p)); rr.append(rep)
            out[fam][v] = resumo(logs, rr) if logs else dict(n=0, geo=float("nan"), ic95=[float("nan"), float("nan")])
    return out


def par(R_, ss, a, b, L, semente, tag, vi):
    """log(MSE a / MSE b) por série e réplicas; janela de 30% até o fim, finitos nos dois"""
    logs, rr = [], []
    for si, s in enumerate(ss):
        y = s["y"]; ok = np.isfinite(y) & np.isfinite(s["P"][a]) & np.isfinite(s["P"][b]); ok[: int(0.3 * len(y))] = False
        if ok.sum() < 50:
            continue
        p, r = R_.reps((y[ok] - s["P"][a][ok]) ** 2, (y[ok] - s["P"][b][ok]) ** 2, L, np.random.default_rng([semente, tag, si, vi]))
        logs.append(math.log(p)); rr.append(r)
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), log=float(np.mean(logs)), razao=float(np.exp(np.mean(logs))),
                ic95_log=[float(np.quantile(R, 0.025)), float(np.quantile(R, 0.975))],
                ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))])


def custos(S, variantes):
    out = {}
    for v in variantes:
        r = [s["info"][v]["custo"] / s["info"]["A"]["custo"] for s in S]
        por = {}
        for s, x in zip(S, r):
            fam = s["info"]["_"]["ident"][0] if s["info"]["_"]["parte"] == "e20" else s["info"]["_"]["parte"]
            por.setdefault(fam, []).append(x)
        out[v] = dict(mediana=float(np.median(r)), max_mediana_familia=float(max(np.median(x) for x in por.values())),
                      familia_mais_cara=max(por, key=lambda k: np.median(por[k])))
    return out


def escolha():
    R_ = _cmp(); sem = SEMENTE["escolha"]
    S = carregar(("e20", "P", "DA"))
    res = {"n": {p: sum(s["info"]["_"]["parte"] == p for s in S) for p in ("e20", "P", "DA")}}
    res["e20"] = fam_e20(S, VARS, sem)
    P = [s for s in S if s["info"]["_"]["parte"] == "P"]; DA = [s for s in S if s["info"]["_"]["parte"] == "DA"]
    res["predios"] = {v: par(R_, P, v, "A", BLOCO["P"], sem, 100, vi) for vi, v in enumerate(VARS)}
    res["bacias_ganho"] = {v: par(R_, DA, "A", v, BLOCO["DA"], sem, 200, vi) for vi, v in enumerate(VARS)}   # log(A/Cx)
    res["custo"] = custos(S, VARS)
    res["nan"] = {v: int(sum(max(s["info"][v]["nan"] - s["info"]["A"]["nan"], 0) for s in S)) for v in VARS}
    g0 = res["bacias_ganho"]["C0"]["log"]
    crit = {}
    for v in VARS[1:]:
        piores = sorted(((f, d[v]["ic95"][1]) for f, d in res["e20"].items() if d[v]["n"]), key=lambda x: -x[1])
        k1 = all(u <= LIM_K1 for _, u in piores) and res["predios"][v]["ic95"][1] <= LIM_K1
        bg = res["bacias_ganho"][v]
        k2 = bg["log"] >= FRAC_K2 * g0 and bg["ic95_log"][0] > 0
        k3 = res["custo"][v]["mediana"] <= LIM_K3
        k4 = res["nan"][v] == 0
        crit[v] = dict(K1=bool(k1), K2=bool(k2), K3=bool(k3), K4=bool(k4), admissivel=bool(k1 and k2 and k3 and k4),
                       pior_e20=piores[:3], predios_sup=res["predios"][v]["ic95"][1],
                       fracao_do_ganho_C0=float(bg["log"] / g0) if g0 else float("nan"))
    res["criterios"] = crit
    adm = [v for v in VARS[1:] if crit[v]["admissivel"]]
    if adm:
        cm = min(res["custo"][v]["mediana"] for v in adm)
        emp = [v for v in adm if res["custo"][v]["mediana"] - cm < 0.02]
        res["escolhida"] = max(emp, key=lambda v: res["bacias_ganho"][v]["log"])
    else:
        res["escolhida"] = None
    (AQUI / "DEV_M1_RESULTADO_escolha.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                       encoding="utf-8", newline="\n")
    print("séries:", res["n"])
    for v in VARS:
        c = crit.get(v, {}); bg = res["bacias_ganho"][v]
        print(f"{v}: bacias A/Cx {bg['razao']:.3f} [{bg['ic95'][0]:.3f}; {bg['ic95'][1]:.3f}]  prédios Cx/A "
              f"{res['predios'][v]['razao']:.3f} (sup {res['predios'][v]['ic95'][1]:.3f})  custo {res['custo'][v]['mediana']:.3f}"
              f" (máx fam {res['custo'][v]['max_mediana_familia']:.2f} {res['custo'][v]['familia_mais_cara']})  nan {res['nan'][v]}  {c}")
    print("escolhida:", res["escolhida"])


def replica(v):
    R_ = _cmp(); sem = SEMENTE["replica"]
    ref = json.loads((AQUI / "DEV_M1_RESULTADO_escolha.json").read_text(encoding="utf-8"))
    assert ref["escolhida"] == v, (ref["escolhida"], v)
    S = carregar(("DB", "R"))
    DB = [s for s in S if s["info"]["_"]["parte"] == "DB"]; RR = [s for s in S if s["info"]["_"]["parte"] == "R"]
    g = par(R_, DB, "A", v, BLOCO["DB"], sem, 300, 0); pr = par(R_, RR, v, "A", BLOCO["R"], sem, 400, 0)
    gA = ref["bacias_ganho"][v]["log"]
    res = dict(variante=v, bacias_DB_ganho=g, predios_R=pr, custo=custos(S, (v,)),
               replica=bool(g["ic95_log"][0] > 0 and g["log"] >= 0.5 * gA and pr["ic95"][1] <= LIM_K1))
    (AQUI / "DEV_M1_RESULTADO_replica.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                       encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    escolha() if sys.argv[1] == "escolha" else replica(sys.argv[2])
