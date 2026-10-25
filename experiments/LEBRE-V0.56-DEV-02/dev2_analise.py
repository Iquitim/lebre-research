#!/usr/bin/env python3
"""dev2_analise.py — análise da etapa LEBRE-V0.56-DEV-02 (PLANO_DEV_DINAMICO.md, §4 e §5). Escrito e commitado antes de
qualquer execução do banco. Roda no ambiente do Lab (por causa do E20).

- E20: m2_dev.par_bootstrap, 20% inicial, bloco do E20 (como no DEV-01); semente [2026102904, família, série, variante].
- Demais partes: `reps` (LEBRE-V0.55-COMP-01/comp_analise.py), a partir de 30% da série, blocos de 168 (prédios), 30
  (bacias) e 56 (rios); sementes [2026102904 | 2026102905, parte, série, variante].
- Custo do E20: o de A vem de LEBRE-V0.56-DEV-01/preds (a mesma série, a mesma configuração).
Uso: <python do Lab> dev2_analise.py   ->  DEV2_RESULTADO.json
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
OUT = AQUI / "preds"
PARTES = ("P", "DA", "DB", "CLV", "ONSD", "ONSR")
BLOCO = {"P": 168, "DA": 30, "DB": 30, "CLV": 30, "ONSD": 56, "ONSR": 56}
CAND = ("C4", "D1", "D2", "D3", "D4")
SENS = tuple(f"S{i}" for i in range(1, 11))
SA, SB = 2026102904, 2026102905
sys.path.insert(0, str(E / "LEBRE-V0.56-DEV-01"))


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", E / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def carregar():
    S = []
    for f in sorted(OUT.glob("*.json")):
        info = json.loads(f.read_text(encoding="utf-8")); Z = np.load(f.with_suffix(".npz"))
        S.append(dict(info=info, y=Z["y"], P={k: v for k, v in Z.items() if k != "y"}))
    return S


def resumo(logs, rr):
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), log=float(np.mean(logs)), razao=float(np.exp(np.mean(logs))),
                ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))],
                ic95_log=[float(np.quantile(R, 0.025)), float(np.quantile(R, 0.975))])


def par_reps(R_, ss, a, b, L, sem, tag, vi):
    """log(MSE a / MSE b): `reps`, a partir de 30% da série"""
    logs, rr = [], []
    for si, s in enumerate(ss):
        y = s["y"]; ok = np.isfinite(y) & np.isfinite(s["P"][a]) & np.isfinite(s["P"][b]); ok[: int(0.3 * len(y))] = False
        if ok.sum() < 50:
            continue
        p, r = R_.reps((y[ok] - s["P"][a][ok]) ** 2, (y[ok] - s["P"][b][ok]) ** 2, L, np.random.default_rng([sem, tag, si, vi]))
        logs.append(math.log(p)); rr.append(r)
    return resumo(logs, rr)


def main():
    import dev_dados as DD
    E20, M2 = DD.e20()
    R_ = _cmp(); S = carregar()
    por = {p: [s for s in S if s["info"]["_"]["parte"] == p] for p in PARTES}
    e20 = [s for s in S if s["info"]["_"]["parte"] == "e20"]
    res = {"n": {**{p: len(v) for p, v in por.items()}, "e20": len(e20)}}
    # ---------------- Parte A
    fam = {}
    for fi, fm in enumerate(E20.TODAS):
        ss = sorted([s for s in e20 if s["info"]["_"]["ident"][0] == fm], key=lambda s: s["info"]["_"]["ident"][1])
        if not ss:
            continue
        curtas = fm in E20.CURTAS; fam[fm] = {}
        for vi, v in enumerate(CAND, start=1):
            logs, rr = [], []
            for s in ss:
                k = s["info"]["_"]["ident"][1]; y = s["y"]; ini = int(0.2 * len(y))
                L = E20.bloco_curta(s["info"]["_"]["origem"]) if curtas else E20.bloco(fm)
                p, rep = M2.par_bootstrap(y, s["P"][v], s["P"]["A"], ini, L, np.random.default_rng([SA, fi, k, vi]))
                if np.isfinite(p) and p > 0:
                    logs.append(math.log(p)); rr.append(rep)
            fam[fm][v] = resumo(logs, rr) if logs else dict(n=0)
    res["e20"] = fam
    A = {}
    for ti, p in enumerate(PARTES):
        A[p] = {v: par_reps(R_, por[p], v, "A", BLOCO[p], SA, 100 + ti, vi) for vi, v in enumerate(("C3",) + CAND)}
    res["partes_A"] = A
    custo, nan = {}, {}
    a20 = {}
    for s in e20:
        fm, k = s["info"]["_"]["ident"]
        a20[(fm, k)] = json.loads((E / "LEBRE-V0.56-DEV-01" / "preds" / f"e20__{fm}__{k}.json").read_text(encoding="utf-8"))
    for v in CAND:
        r = []
        for s in e20:
            fm, k = s["info"]["_"]["ident"]; ref = a20[(fm, k)]
            r.append((s["info"][v]["custo"] if v in s["info"] else ref[v]["custo"]) / ref["A"]["custo"])
        for p in PARTES:
            r += [s["info"][v]["custo"] / s["info"]["A"]["custo"] for s in por[p]]
        custo[v] = dict(mediana=float(np.median(r)), p95=float(np.quantile(r, 0.95)))
        nan[v] = int(sum(int((np.isfinite(s["y"]) & np.isfinite(s["P"]["A"]) & ~np.isfinite(s["P"][v])).sum()) for s in S if v in s["P"]))
    res["custo"] = custo; res["nan_novas"] = nan
    res["fracao_atualizacoes"] = {v: {p: float(np.median([s["info"][v]["fracao_atualizacoes"] for s in por[p]])) for p in PARTES}
                                  for v in CAND if v.startswith("D")}
    crit = {}
    for v in CAND:
        piores = sorted(((f, d[v]["ic95"][1]) for f, d in fam.items() if d[v].get("n")), key=lambda x: -x[1])
        k1 = all(u <= 1.02 for _, u in piores) and all(A[p][v]["ic95"][1] <= 1.02 for p in ("P", "ONSD", "ONSR"))
        ganho = {p: (-A[p][v]["log"], -A[p][v]["ic95_log"][1], -A[p]["C3"]["log"]) for p in ("DA", "DB", "CLV")}
        k2 = all(g >= 0.8 * g3 and lo > 0 for g, lo, g3 in ganho.values())
        k3 = custo[v]["mediana"] <= 1.25; k4 = nan[v] == 0
        crit[v] = dict(K1=bool(k1), K2=bool(k2), K3=bool(k3), K4=bool(k4), admissivel=bool(k1 and k2 and k3 and k4),
                       pior_e20=piores[:3], fracao_do_ganho_C3={p: g / g3 if g3 else float("nan") for p, (g, lo, g3) in ganho.items()},
                       ganho_minimo=float(min(g for g, lo, g3 in ganho.values())))
    res["criterios_A"] = crit
    adm = [v for v in CAND if crit[v]["admissivel"]]
    if adm:
        cm = min(custo[v]["mediana"] for v in adm)
        emp = [v for v in adm if custo[v]["mediana"] - cm < 0.02]
        res["escolhida"] = max(emp, key=lambda v: crit[v]["ganho_minimo"])
    else:
        res["escolhida"] = None
    # ---------------- Parte B
    B = {}
    for ti, p in enumerate(PARTES):
        B[p] = {v: par_reps(R_, por[p], v, "A", BLOCO[p], SB, 200 + ti, vi) for vi, v in enumerate(SENS)}
    res["partes_B"] = B
    marcas = {}
    for v in SENS:
        melhora = [p for p in PARTES if B[p][v]["ic95"][1] < 0.98]
        piora = [p for p in PARTES if B[p][v]["ic95"][0] > 1.02]
        quase_todas = sum(B[p][v]["ic95"][1] < 1.0 for p in PARTES) >= len(PARTES) - 1
        marcas[v] = dict(melhora=melhora, piora=piora, depende_do_contexto=bool(melhora and piora), mal_calibrado=bool(quase_todas))
    res["marcas_B"] = marcas
    (AQUI / "DEV2_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
    print("séries:", res["n"])
    for v in CAND:
        c = crit[v]
        print(f"{v}: custo {custo[v]['mediana']:.3f} (p95 {custo[v]['p95']:.2f})  ganho/C3 {({p: round(x, 2) for p, x in c['fracao_do_ganho_C3'].items()})}"
              f"  K {c['K1']},{c['K2']},{c['K3']},{c['K4']}  pior E20 {[(f, round(u, 3)) for f, u in c['pior_e20']]}")
    for p in PARTES:
        print(p, {v: round(A[p][v]["razao"], 3) for v in ("C3",) + CAND})
    print("escolhida:", res["escolhida"])
    for v in SENS:
        print(v, {p: round(B[p][v]["razao"], 3) for p in PARTES}, marcas[v])


if __name__ == "__main__":
    main()
