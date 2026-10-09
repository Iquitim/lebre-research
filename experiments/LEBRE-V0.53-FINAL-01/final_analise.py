"""final_analise.py — análise PRÉ-REGISTRADA da avaliação final da v0.53 (PREREG_V053_FINAL.md, seção 5).
Lê preds/ (final_run.py) e chronos/ (final_chronos.py); escreve FINAL_RESULTADO.md e final_resultado.json.

Uso: python final_analise.py
"""
import glob
import json
import math
import os

import numpy as np

import final_dados as FD
import final_regua as R

SEMENTE_CLASSE, SEMENTE = 20261053, 20261054
BLOCO = {"camels": 30, "bdg2": 168, "solar": 168, "eolica": 168, "carga": 168, "fx_ret": 20, "fx_abs": 20, "fx_niv": 20}
BLOCO_CURTA = {f: (24 if b == 168 else 20) for f, b in BLOCO.items()}
LIMITE_CUSTO = 1100.0
RAM_V052, RAM_LIMITE = 74_988, 128 * 1024
NULAS = ["fx_ret"]
CLASSES = ("v0.52 melhor", "referência melhor", "indecidível", "indecidível (choque)")


def _classe(y, f52, fr, ini, L, rng):
    pc, rep = R.par_bootstrap(y, f52, fr, ini, L, rng)
    icc = R.ic(rep)
    c = "v0.52 melhor" if icc[1] < 1 else ("referência melhor" if icc[0] > 1 else "indecidível")
    er = ((fr - y) ** 2)[ini:]
    er = er[np.isfinite(er)]
    choque = float(er.max() / er.sum()) if er.size and er.sum() > 0 else 0.0
    if c in ("referência melhor", "v0.52 melhor") and choque > R.limite_choque(er.size):
        c = "indecidível (choque)"
    return c, pc, icc, choque


def _agregado(reps, pontos):
    if not reps:
        return None
    rr = np.vstack(reps).mean(0)
    return dict(geo=float(np.exp(np.mean(np.log(pontos)))), ic95=R.ic(rr), n=len(reps))


def ram_estimada(d_max):
    """Estimativa analítica (bytes, 8 por número) do estado acrescentado pela v0.53, somada aos 74.988 B medidos da
    v0.52 no STM32F407 (LEBRE-V0.52-EXT-01). M1 (k = 3 + 5 m, m = mín(d, 5)): P k², w, z k; buffers 16 d e 16 m; triagem
    5 d; padronização 2 m + 2; defasagens 2; preenchimento d; AdaHedge 4; Prod 4; escalas 4. M2: histórico da referência
    sazonal (até 168), D e M (8), Prod e normalização (5), porta e e-process (~16), escalas e intervalo (~10)."""
    m = min(d_max, 5)
    k = 3 + 5 * m
    m1 = k * k + 2 * k + 16 * d_max + 16 * m + 5 * d_max + 2 * m + 2 + 2 + d_max + 4 + 4 + 4
    m2 = 168 + 8 + 5 + 16 + 10
    return RAM_V052 + 8 * (m1 + m2), dict(k=k, numeros_m1=m1, numeros_m2=m2)


def main(base=FD.AQUI, lista=None):
    """base: pasta com preds/ e chronos/; lista: tarefas esperadas (padrão: as da reserva). Os dois só mudam no teste."""
    lista = FD.tarefas() if lista is None else lista
    S = []
    for p in sorted(glob.glob(os.path.join(base, "preds", "*.json"))):
        meta = json.load(open(p, encoding="utf-8"))
        a = np.load(p[:-5] + ".npz")
        ch = os.path.join(base, "chronos", os.path.basename(p)[:-5] + ".npz")
        S.append((meta, a, np.load(ch) if os.path.exists(ch) else None))
    ordem = {(f, str(i)): j for j, (f, i) in enumerate(lista)}
    S.sort(key=lambda x: ordem[(x[0]["familia"], x[0]["ident"])])
    faltam = [t for t in lista if not any((m["familia"], m["ident"]) == (t[0], str(t[1])) for m, _, _ in S)]

    por_fam = {f: dict(series=[], reps={"ref": [], "v052": []}, pontos={"ref": [], "v052": []}) for f in FD.FAMILIAS}
    curtas = dict(reps=[], pontos=[], series=[])
    tot_reps, tot_pontos, linhas = [], [], []
    for k, (meta, a, ch) in enumerate(S):
        fam = meta["familia"]
        y, f53, f52, fr, fs = a["y"], a["v053"], a["v052"], a["ref"], a["sarimax"]
        T = len(y)
        ini = int(0.2 * T)
        L = BLOCO[fam]
        nan = int((np.isfinite(y) & ~np.isfinite(f53))[ini:].sum())
        c, pc, icc, choque = _classe(y, f52, fr, ini, L, np.random.default_rng([SEMENTE_CLASSE, k]))
        rng = np.random.default_rng([SEMENTE, k])
        p_ref, rep_ref = R.par_bootstrap(y, f53, fr, ini, L, rng)
        p_52, rep_52 = R.par_bootstrap(y, f53, f52, ini, L, rng)
        tot_reps.append(rep_52); tot_pontos.append(p_52)
        F = por_fam[fam]
        if c == "referência melhor":
            F["reps"]["ref"].append(rep_ref); F["pontos"]["ref"].append(p_ref)
        if c == "v0.52 melhor":
            F["reps"]["v052"].append(rep_52); F["pontos"]["v052"].append(p_52)
        mse = lambda f: float(np.nanmean(((y - f) ** 2)[ini:][np.isfinite(f[ini:]) & np.isfinite(y[ini:])]))
        info = meta["info"]
        r = dict(familia=fam, serie=meta["nome"], T=T, classe=c, v052_sobre_ref=pc, v052_sobre_ref_ic95=icc, choque=choque,
                 v053_sobre_ref=p_ref, v053_sobre_v052=p_52, v053_sobre_v052_ic95=R.ic(rep_52), nan=nan,
                 acrescimo_custo=info["custo_v053"] - info["custo_v052"], custo_v053=info["custo_v053"],
                 custo_v052=info["custo_v052"], externas_v053=info["externas_v053"], externas_v052=info["externas_v052"],
                 estrutura_identica=info["estrutura_identica"], peso_m1_final=info["peso_m1_final"],
                 sarimax_sobre_v053=mse(fs) / mse(f53) if meta["sarimax_ok"] else None)
        if ch is not None:
            idx = ch["idx"]
            e = lambda f: float(np.mean((y[idx] - f) ** 2))
            r["v053_sobre_chronos_1000"] = e(f53[idx]) / e(ch["CHRONOS2_COV"])
            r["v052_sobre_chronos_1000"] = e(f52[idx]) / e(ch["CHRONOS2_COV"])
        F["series"].append(r)
        linhas.append(r)
        # curtas (critério 7: contra o melhor de v0.52 e referência)
        cy, c53, c52, cr = a["curta_y"], a["curta_v053"], a["curta_v052"], a["curta_ref"]
        n = len(cy)
        ci = int(0.2 * n)
        if np.isfinite(cy[ci:]).sum() >= (n - ci) / 2:
            ok = np.isfinite(cy) & np.isfinite(c52) & np.isfinite(cr)
            ok[:ci] = False
            melhor = c52 if np.sum((cy[ok] - c52[ok]) ** 2) <= np.sum((cy[ok] - cr[ok]) ** 2) else cr
            pcm, repc = R.par_bootstrap(cy, c53, melhor, ci, BLOCO_CURTA[fam], np.random.default_rng([SEMENTE, 10_000 + k]))
            curtas["reps"].append(repc); curtas["pontos"].append(pcm)
            curtas["series"].append(dict(familia=fam, serie=meta["nome"], v053_sobre_melhor=pcm,
                                         nan=int((np.isfinite(cy) & ~np.isfinite(c53))[ci:].sum())))

    # critérios
    falhas = {"1": [], "2": [], "4": [], "6": [], "7": [], "NaN": [], "custo": []}
    resumo = {}
    for fam, F in por_fam.items():
        if not F["series"]:
            continue
        c1 = _agregado(F["reps"]["ref"], F["pontos"]["ref"])
        c2 = _agregado(F["reps"]["v052"], F["pontos"]["v052"])
        resumo[fam] = dict(c1=c1, c2=c2, classes={c: sum(s["classe"] == c for s in F["series"]) for c in CLASSES},
                           todas_v053_sobre_v052=float(np.exp(np.mean([math.log(s["v053_sobre_v052"]) for s in F["series"]]))),
                           acrescimo_custo_max=max(s["acrescimo_custo"] for s in F["series"]),
                           externas=(sum(s["externas_v053"] > 0 for s in F["series"]),
                                     sum(s["externas_v052"] > 0 for s in F["series"])))
        if c1 and c1["ic95"][1] > 1.01:
            falhas["1"].append(fam)
        if c2 and c2["ic95"][1] > 1.02:
            falhas["2"].append(fam)
        if fam in NULAS and resumo[fam]["externas"][0] > resumo[fam]["externas"][1]:
            falhas["4"].append(fam)
        if not all(s["estrutura_identica"] for s in F["series"]):
            falhas["6"].append(fam)
        if any(s["nan"] for s in F["series"]):
            falhas["NaN"].append(fam)
        if any(s["acrescimo_custo"] > LIMITE_CUSTO for s in F["series"]):
            falhas["custo"].append(fam)
    c7 = _agregado(curtas["reps"], curtas["pontos"])
    if c7 and c7["ic95"][1] > 1.05:
        falhas["7"].append("CURTAS")
    if any(s["nan"] for s in curtas["series"]):
        falhas["NaN"].append("CURTAS")
    geral = _agregado(tot_reps, tot_pontos)
    melhora = bool(geral and geral["ic95"][1] < 1)
    d_max = max(int(m["d"]) for m, _, _ in S)
    ram, ram_info = ram_estimada(d_max)
    sem_piora = not faltam and not any(falhas.values())
    promovida = sem_piora and melhora and ram <= RAM_LIMITE
    out = dict(faltam=faltam, falhas=falhas, resumo=resumo, curtas=c7, geral_v053_sobre_v052=geral, melhora_clara=melhora,
               ram_estimada_bytes=ram, ram_info=ram_info, sem_piora=sem_piora, promovida=promovida, series=linhas,
               series_curtas=curtas["series"])
    json.dump(out, open(os.path.join(base, "final_resultado.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, default=str)

    fmt = lambda a: "-" if not a else f"{a['geo']:.3f} ({a['ic95'][0]:.3f}–{a['ic95'][1]:.3f}; n = {a['n']})"
    T = ["# Avaliação final da v0.53 na reserva: resultado", "", "Pré-registro `PREREG_V053_FINAL.md`.", "",
         f"Séries: {len(S)} de {len(lista)}; faltam: {', '.join(map(str, faltam)) or 'nenhuma'}.", "",
         f"**Melhora geral (v0.53 ÷ v0.52, todas as séries): {fmt(geral)} → {'atende' if melhora else 'não atende'} "
         f"(limite superior < 1).**", "",
         "| Critério | Falhas |", "|---|---|"] + [f"| {k} | {', '.join(v) or '-'} |" for k, v in falhas.items()] + [
         "", f"Critério 7 (curtas, contra o melhor): {fmt(c7)}.",
         f"Memória estimada (não medida): {ram:,} B de {RAM_LIMITE:,} B ({'cabe' if ram <= RAM_LIMITE else 'não cabe'}).", "",
         f"**Decisão: {'v0.53 PROMOVIDA' if promovida else 'v0.53 NÃO promovida'}** (sem piora: {sem_piora}; melhora clara: "
         f"{melhora}; memória: {ram <= RAM_LIMITE}).", "",
         "| Família | séries (v0.52 melhor / ref. melhor / indecidível / choque) | 1 | 2 | v0.53 ÷ v0.52 (todas) | "
         "+custo máx | externas v0.53 (v0.52) |", "|---|---|---|---|---|---|---|"]
    for fam, r in resumo.items():
        c = r["classes"]
        T.append(f"| {fam} | {c[CLASSES[0]]} / {c[CLASSES[1]]} / {c[CLASSES[2]]} / {c[CLASSES[3]]} | {fmt(r['c1'])} | "
                 f"{fmt(r['c2'])} | {r['todas_v053_sobre_v052']:.3f} | {r['acrescimo_custo_max']:.0f} | "
                 f"{r['externas'][0]} ({r['externas'][1]}) |")
    T += ["", "## Referências fora da classe de orçamento (só reportadas)", "",
          "| Família | SARIMAX-X ÷ v0.53 (geo) | v0.53 ÷ Chronos-2 nos 1.000 pontos (geo) | v0.52 ÷ Chronos-2 (geo) |",
          "|---|---|---|---|"]
    for fam, F in por_fam.items():
        g = lambda key: [s[key] for s in F["series"] if s.get(key)]
        gm = lambda v: f"{math.exp(np.mean(np.log(v))):.3f}" if v else "-"
        T.append(f"| {fam} | {gm(g('sarimax_sobre_v053'))} | {gm(g('v053_sobre_chronos_1000'))} | "
                 f"{gm(g('v052_sobre_chronos_1000'))} |")
    open(os.path.join(base, "FINAL_RESULTADO.md"), "w", encoding="utf-8", newline="\n").write("\n".join(T) + "\n")
    print("\n".join(T[:24]))


if __name__ == "__main__":
    main()
