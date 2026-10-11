"""final_analise.py — análise PRÉ-REGISTRADA da avaliação final da v0.54 (PREREG_V054_FINAL.md, seção 5).
Lê preds/ (final_run.py) e chronos/ (final_chronos.py); escreve FINAL_RESULTADO.md e final_resultado.json.
Régua por decidibilidade como na avaliação da v0.53 (peças em LEBRE-V0.53-FINAL-01/final_regua.py, sem alteração),
agora com a v0.53 no lugar da v0.52.

Uso: python final_analise.py [pasta_base]
"""
import glob
import importlib.util
import json
import math
import os
import sys

import numpy as np

import final_dados as FD

# RUN_NOTAS.md, item 1: carregar por caminho, sem pôr a pasta da v0.53 no sys.path (os processos filhos herdavam esse
# sys.path e importavam o final_dados da v0.53 no lugar deste)
_sr = importlib.util.spec_from_file_location("final_regua_v053",
                                             os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.53-FINAL-01", "final_regua.py"))
R = importlib.util.module_from_spec(_sr); _sr.loader.exec_module(R)
sys.modules.setdefault("final_regua", R)                            # o final_analise da v0.53 importa final_regua

_spec = importlib.util.spec_from_file_location("final_analise_v053",
                                               os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.53-FINAL-01", "final_analise.py"))
A53 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A53)

SEMENTE_CLASSE, SEMENTE, SEMENTE_CUSTO = 2026101291, 2026101292, 2026101293
BLOCO = {"camels": 30, "bdg2": 168, "solar": 168, "eolica": 168, "niveis": 20}
BLOCO_CURTA = {f: (24 if b == 168 else 20) for f, b in BLOCO.items()}
RAM_LIMITE = 128 * 1024
NULAS = ["niveis"]
CLASSES = ("v0.53 melhor", "referência melhor", "indecidível", "indecidível (choque)")


def _classe(y, f53, fr, ini, L, rng):
    pc, rep = R.par_bootstrap(y, f53, fr, ini, L, rng)
    icc = R.ic(rep)
    c = "v0.53 melhor" if icc[1] < 1 else ("referência melhor" if icc[0] > 1 else "indecidível")
    er = ((fr - y) ** 2)[ini:]
    er = er[np.isfinite(er)]
    choque = float(er.max() / er.sum()) if er.size and er.sum() > 0 else 0.0
    if c in ("referência melhor", "v0.53 melhor") and choque > R.limite_choque(er.size):
        c = "indecidível (choque)"
    return c, pc, icc, choque


def ram_estimada(d_max):
    """Estimativa da v0.53 (LEBRE-V0.53-FINAL-01/final_analise.ram_estimada, sem alteração) mais o estado acrescentado
    pela v0.54, 8 bytes por número: M5a (estado do sono e do despertar: ~12 números); M4 (referência e último teste
    disparado por unidade ativa, até 4 unidades, e 2 contadores: 10 números); M5b (nenhum estado novo)."""
    r53, info = A53.ram_estimada(d_max)
    return r53 + 8 * (12 + 10), dict(info, numeros_v054=22)


def mediana_ic(razoes, rng, B=2000):
    v = np.asarray(razoes, float)
    boots = np.median(v[rng.integers(0, len(v), size=(B, len(v)))], axis=1)
    return float(np.median(v)), [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def main(base=FD.AQUI, lista=None):
    lista = FD.tarefas() if lista is None else lista
    S = []
    for p in sorted(glob.glob(os.path.join(base, "preds", "*.json"))):
        meta = json.load(open(p, encoding="utf-8"))
        a = np.load(p[:-5] + ".npz")
        ch = os.path.join(base, "chronos", os.path.basename(p)[:-5] + ".npz")
        S.append((meta, a, np.load(ch) if os.path.exists(ch) else None))
    ordem = {(f, str(i)): j for j, (f, i) in enumerate(lista)}
    S = [x for x in S if (x[0]["familia"], x[0]["ident"]) in ordem]
    S.sort(key=lambda x: ordem[(x[0]["familia"], x[0]["ident"])])
    faltam = [t for t in lista if not any((m["familia"], m["ident"]) == (t[0], str(t[1])) for m, _, _ in S)]

    por_fam = {f: dict(series=[], reps={"ref": [], "v053": []}, pontos={"ref": [], "v053": []}) for f in FD.FAMILIAS}
    curtas = dict(reps=[], pontos=[], series=[])
    linhas, razoes_custo = [], []
    for k, (meta, a, ch) in enumerate(S):
        fam = meta["familia"]
        y, f54, f53, fr, fs = a["y"], a["v054"], a["v053"], a["ref"], a["sarimax"]
        T = len(y); ini = int(0.2 * T); L = BLOCO[fam]
        nan = int((np.isfinite(y) & ~np.isfinite(f54))[ini:].sum())
        c, pc, icc, choque = _classe(y, f53, fr, ini, L, np.random.default_rng([SEMENTE_CLASSE, k]))
        rng = np.random.default_rng([SEMENTE, k])
        p_ref, rep_ref = R.par_bootstrap(y, f54, fr, ini, L, rng)
        p_53, rep_53 = R.par_bootstrap(y, f54, f53, ini, L, rng)
        F = por_fam[fam]
        if c == "referência melhor":
            F["reps"]["ref"].append(rep_ref); F["pontos"]["ref"].append(p_ref)
        if c == "v0.53 melhor":
            F["reps"]["v053"].append(rep_53); F["pontos"]["v053"].append(p_53)
        mse = lambda f: float(np.nanmean(((y - f) ** 2)[ini:][np.isfinite(f[ini:]) & np.isfinite(y[ini:])]))  # noqa: E731
        info = meta["info"]
        rc = info["custo_v054"] / info["custo_v053"]; razoes_custo.append(rc)
        r = dict(familia=fam, serie=meta["nome"], T=T, classe=c, v053_sobre_ref=pc, v053_sobre_ref_ic95=icc, choque=choque,
                 v054_sobre_ref=p_ref, v054_sobre_v053=p_53, v054_sobre_v053_ic95=R.ic(rep_53), nan=nan,
                 custo_v054=info["custo_v054"], custo_v053=info["custo_v053"], razao_custo=rc,
                 externas_v054=info["externas_v054"], externas_v053=info["externas_v053"], remocoes=info["remocoes"],
                 m1=info["m1"], identica=info["identica"],
                 sarimax_sobre_v054=mse(fs) / mse(f54) if meta["sarimax_ok"] else None)
        if ch is not None:
            idx = ch["idx"]
            e = lambda f: float(np.mean((y[idx] - f) ** 2))  # noqa: E731
            r["v054_sobre_chronos_1000"] = e(f54[idx]) / e(ch["CHRONOS2_COV"])
            r["v053_sobre_chronos_1000"] = e(f53[idx]) / e(ch["CHRONOS2_COV"])
        F["series"].append(r); linhas.append(r)
        cy, c54, c53, cr = a["curta_y"], a["curta_v054"], a["curta_v053"], a["curta_ref"]
        n = len(cy); ci = int(0.2 * n)
        if np.isfinite(cy[ci:]).sum() >= (n - ci) / 2:
            ok = np.isfinite(cy) & np.isfinite(c53) & np.isfinite(cr); ok[:ci] = False
            melhor = c53 if np.sum((cy[ok] - c53[ok]) ** 2) <= np.sum((cy[ok] - cr[ok]) ** 2) else cr
            ok54 = ok & np.isfinite(c54)
            if np.sum((cy[ok54] - melhor[ok54]) ** 2) == 0:
                if np.sum((cy[ok54] - c54[ok54]) ** 2) == 0:
                    curtas.setdefault("empates_exatos", []).append(meta["nome"])
                else:
                    curtas.setdefault("falhas_comparador_perfeito", []).append(meta["nome"])
                continue
            pcm, repc = R.par_bootstrap(cy, c54, melhor, ci, BLOCO_CURTA[fam], np.random.default_rng([SEMENTE, 10_000 + k]))
            curtas["reps"].append(repc); curtas["pontos"].append(pcm)
            curtas["series"].append(dict(familia=fam, serie=meta["nome"], v054_sobre_melhor=pcm,
                                         nan=int((np.isfinite(cy) & ~np.isfinite(c54))[ci:].sum())))

    falhas = {"A1": [], "A2": [], "A3": [], "A4": [], "A5 NaN": []}
    resumo = {}
    for fam, F in por_fam.items():
        if not F["series"]:
            continue
        c1 = A53._agregado(F["reps"]["ref"], F["pontos"]["ref"])
        c2 = A53._agregado(F["reps"]["v053"], F["pontos"]["v053"])
        resumo[fam] = dict(c1=c1, c2=c2, classes={c: sum(s["classe"] == c for s in F["series"]) for c in CLASSES},
                           todas_v054_sobre_v053=float(np.exp(np.mean([math.log(s["v054_sobre_v053"]) for s in F["series"]]))),
                           razao_custo_mediana=float(np.median([s["razao_custo"] for s in F["series"]])),
                           remocoes=sum(len(s["remocoes"]) for s in F["series"]),
                           externas=(sum(s["externas_v054"] > 0 for s in F["series"]),
                                     sum(s["externas_v053"] > 0 for s in F["series"])))
        if c1 and c1["ic95"][1] > 1.01:
            falhas["A1"].append(fam)
        if c2 and c2["ic95"][1] > 1.02:
            falhas["A2"].append(fam)
        if fam in NULAS and resumo[fam]["externas"][0] > resumo[fam]["externas"][1]:
            falhas["A3"].append(fam)
        if any(s["nan"] for s in F["series"]):
            falhas["A5 NaN"].append(fam)
    c4 = A53._agregado(curtas["reps"], curtas["pontos"])
    if c4 and c4["ic95"][1] > 1.05:
        falhas["A4"].append("CURTAS")
    falhas["A4"] += [f"comparador perfeito e v0.54 pior: {n}" for n in curtas.get("falhas_comparador_perfeito", [])]
    if any(s["nan"] for s in curtas["series"]):
        falhas["A5 NaN"].append("CURTAS")
    med, med_ic = mediana_ic(razoes_custo, np.random.default_rng(SEMENTE_CUSTO))
    custo_ok = med_ic[1] < 1
    d_max = max(int(m["d"]) for m, _, _ in S)
    ram, ram_info = ram_estimada(d_max)
    sem_piora = not faltam and not any(falhas.values())
    promovida = sem_piora and custo_ok and ram <= RAM_LIMITE
    out = dict(faltam=faltam, falhas=falhas, resumo=resumo, curtas=c4, curtas_empates_exatos=curtas.get("empates_exatos", []),
               custo_razao_mediana=med, custo_razao_mediana_ic95=med_ic, custo_ok=custo_ok, ram_estimada_bytes=ram,
               ram_info=ram_info, sem_piora=sem_piora, promovida=promovida, series=linhas, series_curtas=curtas["series"])
    json.dump(out, open(os.path.join(base, "final_resultado.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False, default=str)

    fmt = lambda a: "-" if not a else f"{a['geo']:.3f} ({a['ic95'][0]:.3f}–{a['ic95'][1]:.3f}; n = {a['n']})"  # noqa: E731
    T = ["# Avaliação final da v0.54 na reserva: resultado", "", "Pré-registro `PREREG_V054_FINAL.md`.", "",
         f"Séries: {len(S)} de {len(lista)}; faltam: {', '.join(map(str, faltam)) or 'nenhuma'}.", "",
         f"**B. Custo (razão mediana v0.54 ÷ v0.53 por série): {med:.3f} (IC 95% {med_ic[0]:.3f}–{med_ic[1]:.3f}) → "
         f"{'atende' if custo_ok else 'não atende'} (limite superior < 1).**", "",
         "| Critério A | Falhas |", "|---|---|"] + [f"| {k} | {', '.join(v) or '-'} |" for k, v in falhas.items()] + [
         "", f"A4 (curtas, contra o melhor de v0.53 e referência): {fmt(c4)}. Empates exatos fora do agregado: "
         f"{', '.join(curtas.get('empates_exatos', [])) or 'nenhum'}.",
         f"C. Memória estimada (não medida): {ram:,} B de {RAM_LIMITE:,} B ({'cabe' if ram <= RAM_LIMITE else 'não cabe'}).", "",
         f"**Decisão: {'v0.54 PROMOVIDA' if promovida else 'v0.54 NÃO promovida'}** (sem piora: {sem_piora}; custo: "
         f"{custo_ok}; memória: {ram <= RAM_LIMITE}).", "",
         "| Família | séries (v0.53 melhor / ref. melhor / indecidível / choque) | A1 | A2 | v0.54 ÷ v0.53 (todas) | "
         "custo v0.54 ÷ v0.53 (mediana) | remoções | externas v0.54 (v0.53) |", "|---|---|---|---|---|---|---|---|"]
    for fam, r in resumo.items():
        c = r["classes"]
        T.append(f"| {fam} | {c[CLASSES[0]]} / {c[CLASSES[1]]} / {c[CLASSES[2]]} / {c[CLASSES[3]]} | {fmt(r['c1'])} | "
                 f"{fmt(r['c2'])} | {r['todas_v054_sobre_v053']:.3f} | {r['razao_custo_mediana']:.3f} | {r['remocoes']} | "
                 f"{r['externas'][0]} ({r['externas'][1]}) |")
    T += ["", "## Referências fora da classe de orçamento (só reportadas)", "",
          "| Família | SARIMAX-X ÷ v0.54 (geo) | v0.54 ÷ Chronos-2 nos 1.000 pontos (geo) | v0.53 ÷ Chronos-2 (geo) |",
          "|---|---|---|---|"]
    for fam, F in por_fam.items():
        g = lambda key: [s[key] for s in F["series"] if s.get(key)]  # noqa: E731
        gm = lambda v: f"{math.exp(np.mean(np.log(v))):.3f}" if v else "-"  # noqa: E731
        T.append(f"| {fam} | {gm(g('sarimax_sobre_v054'))} | {gm(g('v054_sobre_chronos_1000'))} | "
                 f"{gm(g('v053_sobre_chronos_1000'))} |")
    open(os.path.join(base, "FINAL_RESULTADO.md"), "w", encoding="utf-8", newline="\n").write("\n".join(T) + "\n")
    print("\n".join(T[:22]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else FD.AQUI)
