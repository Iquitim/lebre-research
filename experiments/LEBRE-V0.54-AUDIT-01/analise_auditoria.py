"""analise_auditoria.py — aplica os sinais de alerta de PLANO_AUDITORIA.md aos resultados de auditoria.py (T1 a T9).
Uso: python analise_auditoria.py <pasta_resultados>
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np


def geo(v):
    v = [x for x in v if x is not None and np.isfinite(x) and x > 0]
    return float(np.exp(np.mean(np.log(v)))) if v else float("nan")


def aceitos(evs):
    return sum(1 for e in evs if e["outcome"] == "accepted" and e["change"] != "gate")


def main(p):
    L = load = lambda n: json.load(open(os.path.join(p, f"{n}.json")))   # noqa: E731
    out, alertas = {}, []
    t1 = load("T1"); out["T1"] = t1
    if not all(all(v for k, v in c.items() if k != "caso") for c in t1):
        alertas.append("T1: diferença de identidade ou determinismo")
    todos = []
    for n in ("T2", "T3", "T4", "T5", "T7"):
        R = load(n); todos += R
        erros = [r for r in R if "erro" in r]
        if erros:
            alertas.append(f"{n}: {len(erros)} execuções com erro")
    # T2
    por = defaultdict(list)
    for r in (x for x in todos if x["teste"] == "T2" and "erro" not in x):
        tipo = "escala" if r["chave"].startswith("escala") else r["chave"]
        por[tipo].append(r)
    t2 = {}
    for tipo, rs in por.items():
        razoes = [r["mse54"] / r["mse53"] if r["mse53"] else float("nan") for r in rs]
        t2[tipo] = dict(geo=geo(razoes), max=max(x for x in razoes if np.isfinite(x)) if any(np.isfinite(razoes)) else None,
                        nao_finitas54=sum(r["nao_finitas54_total"] for r in rs), nao_finitas53=sum(r["nao_finitas53_total"] for r in rs),
                        n=len(rs))
        if t2[tipo]["nao_finitas54"]:
            alertas.append(f"T2 {tipo}: {t2[tipo]['nao_finitas54']} previsões não finitas na v0.54 (v0.53: {t2[tipo]['nao_finitas53']})")
        if t2[tipo]["geo"] > 1.05 or (t2[tipo]["max"] or 0) > 1.5:
            alertas.append(f"T2 {tipo}: razão de MSE geo {t2[tipo]['geo']:.4f}, máx {t2[tipo]['max']:.4f}")
    out["T2"] = t2
    # T3
    R3 = [r for r in todos if r["teste"] == "T3" and "erro" not in r]
    ext = lambda est: any(n.startswith("x") for n in est)            # noqa: E731
    t3 = dict(n=len(R3), com_externa_v053=sum(ext(r["estrutura53"]) for r in R3),
              com_externa_v054=sum(ext(r["estrutura54"]) for r in R3),
              aceitas_alguma_vez_v053=sum(any(e["added"] and e["added"].startswith("x") and e["outcome"] == "accepted" for e in r["eventos53"]) for r in R3),
              aceitas_alguma_vez_v054=sum(any(e["added"] and e["added"].startswith("x") and e["outcome"] == "accepted" for e in r["eventos54"]) for r in R3),
              geo=geo([r["mse54"] / r["mse53"] for r in R3]))
    out["T3"] = t3
    if t3["com_externa_v054"] > t3["com_externa_v053"]:
        alertas.append(f"T3: {t3['com_externa_v054']} séries com entrada externa na v0.54 contra {t3['com_externa_v053']} na v0.53")
    # T4
    t4 = {}
    for b in sorted({r["chave"] for r in todos if r["teste"] == "T4"}):
        rs = [r for r in todos if r["teste"] == "T4" and r["chave"] == b and "erro" not in r]
        rem = sum(any("('in', 0)" in s for _, s in r["remocoes54"]) for r in rs)
        aceita53 = sum("x0" in r["estrutura53"] or any(e["added"] == "x0" and e["outcome"] == "accepted" for e in r["eventos53"]) for r in rs)
        t4[str(b)] = dict(n=len(rs), x0_removida=rem, x0_aceita_v053=aceita53, geo=geo([r["mse54"] / r["mse53"] for r in rs]),
                          max=max(r["mse54"] / r["mse53"] for r in rs))
        if (b >= 0.2 and rem > 1) or t4[str(b)]["geo"] > 1.02:
            alertas.append(f"T4 b={b}: x0 removida em {rem} de {len(rs)}; razão {t4[str(b)]['geo']:.4f}")
    out["T4"] = t4
    # T5
    t5 = {}
    for Lb in sorted({r["chave"] for r in todos if r["teste"] == "T5"}):
        rs = [r for r in todos if r["teste"] == "T5" and r["chave"] == Lb and "erro" not in r]
        t5[str(Lb)] = dict(n=len(rs), geo=geo([r["mse54"] / r["mse53"] for r in rs]), max=max(r["mse54"] / r["mse53"] for r in rs),
                           remocoes=sum(len(r["remocoes54"]) for r in rs))
        if t5[str(Lb)]["geo"] > 1.05:
            alertas.append(f"T5 bloco {Lb}: razão {t5[str(Lb)]['geo']:.4f}")
    out["T5"] = t5
    # T6
    t6 = {}
    for n in ("T2", "T3", "T4", "T5", "T7"):
        rs = [r for r in todos if r["teste"] == n and "erro" not in r]
        m53, m54 = float(np.mean([aceitos(r["eventos53"]) for r in rs])), float(np.mean([aceitos(r["eventos54"]) for r in rs]))
        t6[n] = dict(eventos_v053=m53, eventos_v054=m54)
        if m54 > 2 * m53 + 1:
            alertas.append(f"T6 {n}: {m54:.2f} eventos por série na v0.54 contra {m53:.2f}")
    out["T6"] = t6
    # T7
    t7 = {}
    for v in sorted({tuple(r["chave"]) for r in todos if r["teste"] == "T7"}):
        rs = [r for r in todos if r["teste"] == "T7" and tuple(r["chave"]) == v and "erro" not in r]
        t7["_".join(map(str, v))] = dict(n=len(rs), geo_ultimo=geo([r["mse54_seg"] / r["mse53_seg"] for r in rs]),
                                        max=max(r["mse54_seg"] / r["mse53_seg"] for r in rs),
                                        dormiram=sum(r["m1"]["sleeps"] > 0 for r in rs), despertaram=sum(r["m1"]["wakes"] > 0 for r in rs))
        if t7["_".join(map(str, v))]["geo_ultimo"] > 1.02:
            alertas.append(f"T7 {v}: razão no último trecho {t7['_'.join(map(str, v))]['geo_ultimo']:.4f}")
    out["T7"] = t7
    # T8
    t8 = {}
    grupos = defaultdict(list)
    for r in todos:
        if "erro" in r:
            continue
        g = r["teste"] + (":" + str(r["chave"]) if r["teste"] in ("T2", "T4", "T5") else "")
        grupos[g].append(r)
    for g, rs in grupos.items():
        pico53, pico54 = max(r["custo53"]["max"] for r in rs), max(r["custo54"]["max"] for r in rs)
        t8[g] = dict(media53=float(np.mean([r["custo53"]["media"] for r in rs])), media54=float(np.mean([r["custo54"]["media"] for r in rs])),
                     p99_53=float(np.mean([r["custo53"]["p99"] for r in rs])), p99_54=float(np.mean([r["custo54"]["p99"] for r in rs])),
                     pico53=pico53, pico54=pico54, tempo=float(np.median([r["tempo54"] / r["tempo53"] for r in rs])))
        if pico54 > 1.10 * pico53:
            alertas.append(f"T8 {g}: pico {pico54:.0f} contra {pico53:.0f}")
    tempo = float(np.median([r["tempo54"] / r["tempo53"] for r in todos if "erro" not in r]))
    out["T8"] = dict(grupos=t8, tempo_mediana_razao=tempo)
    if tempo > 1.10:
        alertas.append(f"T8: tempo de relógio mediano {tempo:.3f} × o da v0.53")
    # T9
    if os.path.exists(os.path.join(p, "T9.json")):
        t9 = load("T9"); out["T9"] = t9
        for d in (5, 50):
            c53 = {k for r in t9 if r["d"] == d and r["modelo"] == "v053" for k in r["cresce"]}
            c54 = {k for r in t9 if r["d"] == d and r["modelo"] == "v054" for k in r["cresce"]}
            novos = sorted(c54 - c53)
            out.setdefault("T9_novos", {})[d] = novos
            if novos:
                alertas.append(f"T9 d={d}: contêineres que crescem só na v0.54: {novos}")
    out["alertas"] = alertas
    json.dump(out, open(os.path.join(p, "analise.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k not in ("T1", "T9")}, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
