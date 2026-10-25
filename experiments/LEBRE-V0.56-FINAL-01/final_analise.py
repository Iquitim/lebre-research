#!/usr/bin/env python3
"""final_analise.py — regra de promoção da v0.56 (PREREG_V056_FINAL.md, §3), a partir de preds/. Escrito e commitado antes
da validação e da execução. Grava FINAL_RESULTADO.json.

Estatística (a mesma da validação): por série, razão de MSE C5 ÷ A a partir de 20% da série e réplicas em log por blocos
móveis pareados (`reps` de LEBRE-V0.55-COMP-01/comp_analise.py); por família, média geométrica e IC pela média das
réplicas; 2.000 réplicas, semente [2026102901, família, série]. Janela curta: passos 200 a 2.000.

R5: a estimativa da v0.55 (86.180 B, LEBRE-V0.55-FINAL-01/FINAL_RESULTADO.json) mais a variação do estado da M1 com cinco
entradas escolhidas, 8 bytes por número. Na M1, o estado que muda é a matriz P (k²), os pesos w (k) e o histórico de
alvos (ylags): v0.55, k = 1 + 2 + 5·5 = 28 e 2 alvos; v0.56, k = 1 + 3 + 3·5 = 19 e 3 alvos.
"""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FAMILIAS = ["camels_cl", "bdg2", "eolica", "solar", "camels_br"]
BLOCO = {"camels_cl": 30, "bdg2": 168, "eolica": 168, "solar": 168, "camels_br": 30}
SEMENTE, INI = 2026102901, 0.20
RAM_LIMITE = 128 * 1024


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", RAIZ / "experiments" / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def cp_sup(x, n, a=0.05):
    """limite superior de Clopper-Pearson bilateral (a função da avaliação final da v0.55)"""
    if x >= n:
        return 1.0
    lo, hi = x / n, 1.0
    for _ in range(80):
        p = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))
        lo, hi = (p, hi) if cdf > a / 2 else (lo, p)
    return (lo + hi) / 2


def ram():
    r55 = json.loads((RAIZ / "experiments" / "LEBRE-V0.55-FINAL-01" / "FINAL_RESULTADO.json").read_text(encoding="utf-8"))
    base = r55["criterios"]["R5_bytes"]
    k55, k56 = 1 + 2 + 5 * 5, 1 + 3 + 3 * 5
    delta = (k56 * k56 + k56 + 3) - (k55 * k55 + k55 + 2)
    return base + 8 * delta, dict(base_v055=base, k_v055=k55, k_v056=k56, delta_numeros=delta)


def main():
    R_ = _cmp()
    res = {"familias": {}, "series": []}
    nan, custos, pl = 0, [], {"A": 0, "C5": 0}
    estrutura_diferente = []
    for fi, fam in enumerate(FAMILIAS):
        arqs = sorted((AQUI / "preds").glob(f"{fam}__*.json"))
        logs, rr, logs_c, rr_c = [], [], [], []
        for si, arq in enumerate(arqs):
            meta = json.loads(arq.read_text(encoding="utf-8")); Z = np.load(arq.with_suffix(".npz")); I = meta["info"]
            y = Z["y"]; t = np.arange(len(y))
            for a_, b_ in (("A", "C5"), ("A_pl", "C5_pl")):
                nan += int((np.isfinite(y) & np.isfinite(Z[a_]) & ~np.isfinite(Z[b_])).sum())
            ok = np.isfinite(y) & np.isfinite(Z["A"]) & np.isfinite(Z["C5"]); okj = ok.copy(); okj[: int(INI * len(y))] = False
            rng = np.random.default_rng([SEMENTE, fi, si])
            p, r = R_.reps((y[okj] - Z["C5"][okj]) ** 2, (y[okj] - Z["A"][okj]) ** 2, BLOCO[fam], rng)
            okc = ok & (t >= 200) & (t < 2000)
            pc, rc = R_.reps((y[okc] - Z["C5"][okc]) ** 2, (y[okc] - Z["A"][okc]) ** 2, 24 if BLOCO[fam] == 168 else 20, rng)
            logs.append(math.log(p)); rr.append(r); logs_c.append(math.log(pc)); rr_c.append(rc)
            cr = I["C5"]["custo"] / I["A"]["custo"]; custos.append(cr)
            plv = {v: any(u in meta["placebo"] for u in I[v + "_pl"]["externas_final"]) for v in ("A", "C5")}
            for v in pl:
                pl[v] += plv[v]
            igual = all(I["A" + s]["estrutura"] == I["C5" + s]["estrutura"] and I["A" + s]["assinatura_nucleo"] == I["C5" + s]["assinatura_nucleo"]
                        for s in ("", "_pl"))
            if not igual:
                estrutura_diferente.append(f"{fam}:{meta['ident']}")
            res["series"].append(dict(familia=fam, ident=meta["ident"], razao=p, razao_curta=pc, custo_razao=cr,
                                      placebo_A=plv["A"], placebo_C5=plv["C5"], portao_A=I["A"]["portao"], portao_C5=I["C5"]["portao"],
                                      estrutura_e_nucleo_iguais=igual))
        R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]; Rc = np.vstack(rr_c).mean(0); Rc = Rc[np.isfinite(Rc)]
        ss = [s for s in res["series"] if s["familia"] == fam]
        res["familias"][fam] = dict(n=len(arqs), geo=float(np.exp(np.mean(logs))),
                                    ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))],
                                    curta_geo=float(np.exp(np.mean(logs_c))),
                                    curta_ic95=[float(np.exp(np.quantile(Rc, 0.025))), float(np.exp(np.quantile(Rc, 0.975)))],
                                    custo_mediana=float(np.median([s["custo_razao"] for s in ss])),
                                    placebo_A=sum(s["placebo_A"] for s in ss), placebo_C5=sum(s["placebo_C5"] for s in ss))
    n_tot = len(res["series"]); F = res["familias"]
    ram_b, ram_info = ram()
    cr = {"R1": all(f["ic95"][1] <= 1.02 for f in F.values()),
          "R2": cp_sup(pl["C5"], n_tot) <= 0.10 and pl["C5"] <= pl["A"],
          "R2_placebo": dict(A=pl["A"], C5=pl["C5"], n=n_tot, C5_sup=cp_sup(pl["C5"], n_tot), A_sup=cp_sup(pl["A"], n_tot)),
          "R3": nan == 0, "R3_nan": nan,
          "R4": float(np.median(custos)) <= 1.25, "R4_mediana": float(np.median(custos)),
          "R5": ram_b <= RAM_LIMITE, "R5_bytes": ram_b, "R5_info": ram_info,
          "R6": F["camels_cl"]["ic95"][1] < 1.00}
    cr["PROMOVIDA"] = all(cr[k] for k in ("R1", "R2", "R3", "R4", "R5", "R6"))
    res["criterios"] = cr
    res["estrutura_ou_nucleo_diferente"] = estrutura_diferente
    res["piores"] = sorted(res["series"], key=lambda x: -x["razao"])[:5]
    (AQUI / "FINAL_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n",
                                               encoding="utf-8", newline="\n")
    for fam, d in F.items():
        print(f"{fam}: C5/A {d['geo']:.3f} [{d['ic95'][0]:.3f}; {d['ic95'][1]:.3f}]  curta {d['curta_geo']:.3f}  custo {d['custo_mediana']:.3f}"
              f"  placebo A/C5 {d['placebo_A']}/{d['placebo_C5']}")
    print(json.dumps(cr, ensure_ascii=False, default=str)); print("estrutura ou núcleo diferente:", estrutura_diferente)


if __name__ == "__main__":
    main()
