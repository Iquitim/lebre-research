#!/usr/bin/env python3
"""val_analise.py — análise da validação da v0.56 (PREREG_V056_VAL.md, §2 e §3). Escrito e commitado antes da execução.
Estatística da avaliação final da v0.55: por série, razão de MSE C5 ÷ A a partir de 20% da série e réplicas em log por
blocos móveis pareados (`reps` de LEBRE-V0.55-COMP-01/comp_analise.py); por família, média geométrica e IC pela média
das réplicas; 2.000 réplicas, semente [2026102902, família, série].
Uso: python val_analise.py   ->  VAL_RESULTADO.json
"""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
FAM = ("camels_cl", "bdg2")
BLOCO = {"camels_cl": 30, "bdg2": 168}
SEMENTE, INI = 2026102902, 0.20


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", AQUI.parent / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def main():
    R_ = _cmp()
    S = []
    for f in sorted((AQUI / "preds").glob("*.json")):
        info = json.loads(f.read_text(encoding="utf-8")); Z = np.load(f.with_suffix(".npz"))
        S.append(dict(info=info, y=Z["y"], A=Z["A"], C5=Z["C5"]))
    res = {"n": len(S), "familias": {}, "series": []}
    nan_novas = 0
    for fi, fam in enumerate(FAM):
        ss = [s for s in S if s["info"]["_"]["familia"] == fam]
        logs, rr, curta, custo = [], [], [], []
        for si, s in enumerate(ss):
            y = s["y"]; ok = np.isfinite(y) & np.isfinite(s["A"]) & np.isfinite(s["C5"]); ok[: int(INI * len(y))] = False
            nan_novas += int((np.isfinite(y) & np.isfinite(s["A"]) & ~np.isfinite(s["C5"])).sum())
            p, r = R_.reps((y[ok] - s["C5"][ok]) ** 2, (y[ok] - s["A"][ok]) ** 2, BLOCO[fam], np.random.default_rng([SEMENTE, fi, si]))
            logs.append(math.log(p)); rr.append(r)
            t = np.arange(len(y)); c = np.isfinite(y) & np.isfinite(s["A"]) & np.isfinite(s["C5"]) & (t >= 200) & (t < 2000)
            curta.append(float(((y[c] - s["C5"][c]) ** 2).sum() / ((y[c] - s["A"][c]) ** 2).sum()))
            custo.append(s["info"]["C5"]["custo"] / s["info"]["A"]["custo"])
            res["series"].append(dict(familia=fam, ident=s["info"]["_"]["ident"], razao=p, razao_curta=curta[-1], custo_razao=custo[-1],
                                      estrutura_igual=s["info"]["A"]["estrutura"] == s["info"]["C5"]["estrutura"]))
        R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
        res["familias"][fam] = dict(n=len(ss), geo=float(np.exp(np.mean(logs))),
                                    ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))],
                                    curta_geo=float(np.exp(np.mean(np.log(curta)))), custo_mediana=float(np.median(custo)))
    F = res["familias"]
    custo_med = float(np.median([s["custo_razao"] for s in res["series"]]))
    res["criterios"] = dict(V1=bool(F["camels_cl"]["ic95"][1] < 1.00), V2=bool(F["bdg2"]["ic95"][1] <= 1.02),
                            sem_nan_novas=nan_novas == 0, custo_mediana=custo_med, custo_ok=custo_med <= 1.25)
    res["criterios"]["PASSA"] = bool(all(res["criterios"][k] for k in ("V1", "V2", "sem_nan_novas", "custo_ok")))
    res["piores"] = sorted(res["series"], key=lambda x: -x["razao"])[:5]
    res["estrutura_igual_em_todas"] = all(s["estrutura_igual"] for s in res["series"])
    (AQUI / "VAL_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for fam, d in F.items():
        print(f"{fam}: C5/A {d['geo']:.3f} [{d['ic95'][0]:.3f}; {d['ic95'][1]:.3f}]  curta {d['curta_geo']:.3f}  custo {d['custo_mediana']:.3f}")
    print("critérios:", res["criterios"]); print("estrutura igual em todas:", res["estrutura_igual_em_todas"])
    print("piores:", [(p["familia"], p["ident"], round(p["razao"], 3)) for p in res["piores"]])


if __name__ == "__main__":
    main()
