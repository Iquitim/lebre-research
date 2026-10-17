"""v055_diagrams.py — diagrams of the self-contained LEBRE v0.55 documents: the v0.54 diagrams (v054_diagrams, imported,
not changed), with the architecture diagram relabelled for v0.55, plus one new diagram of the anchored core (nested
combination with the innovation structure and the reference of each kind of test). Built with the v0.53 SVG helpers."""
import copy

import v053_diagrams as D53
import v054_diagrams as D54

box, arrow, svg, C, _esc = D53.box, D53.arrow, D53.svg, D53.C, D53._esc

EXTRA = {
    "pt": dict(a_s="O núcleo calcula L (memória, estrutura de nível e estrutura de inovação) e é o único dono das mudanças de estrutura; M1 dorme sem uso; M1 e M2 só mudam como a saída é formada",
               b2="memória + estruturas de nível", b3="e de inovação + plano → L",
               e2="AR2 + bandas de defasagem", e3="(RLS); dorme sem uso"),
    "en": dict(a_s="The core computes L (memory, level structure and innovation structure) and is the only owner of structural changes; M1 sleeps when unused; M1 and M2 only change how the output is formed",
               b2="memory + level and innovation", b3="structures + plane → L",
               e2="AR2 + lag bands of up to", e3="5 inputs (RLS); sleeps if unused"),
}

ANCHOR = {
    "pt": dict(t="Núcleo ancorado (v0.55)", s="Duas combinações aninhadas formam L; cada tipo de unidade é testado contra a previsão que ela pode melhorar",
               m=("Memória", "m: passado do alvo", "(parte de y(t−1))"), sl=("Estrutura de nível", "s: base + blocos", "das unidades aceitas"),
               si=("Estrutura de inovação", "ŝΔ: prevê y − m", "mesmas unidades, pesos próprios"),
               l1=("L₁ = m + wS·(s − m)", "média dinâmica", "(o núcleo anterior)"), l=("L = L₁ + wI·(m + ŝΔ − L₁)", "média dinâmica", "(mesmas constantes)"),
               te=("Unidades externas", "testadas contra L;", "remoção desconta a contribuição em L"),
               ti=("Unidades internas", "testadas contra s", "(passado do alvo, resíduo)"),
               tr=("Triagem (portão suave)", "internas triadas pelo", "resíduo y − L")),
    "en": dict(t="Anchored core (v0.55)", s="Two nested combinations form L; each kind of unit is tested against the forecast it can improve",
               m=("Memory", "m: target's past", "(starts from y(t−1))"), sl=("Level structure", "s: base + blocks", "of accepted units"),
               si=("Innovation structure", "ŝΔ: predicts y − m", "same units, own weights"),
               l1=("L₁ = m + wS·(s − m)", "dynamic averaging", "(the previous core)"), l=("L = L₁ + wI·(m + ŝΔ − L₁)", "dynamic averaging", "(same constants)"),
               te=("External units", "tested against L;", "removal discounts the contribution in L"),
               ti=("Internal units", "tested against s", "(target's past, residual)"),
               tr=("Screening (soft gate)", "internal units screened", "by the residual y − L")),
}


def d_anchor(l):
    b = []
    b.append(box(20, 60, 200, 62, l["m"][0], list(l["m"][1:]), C["blue"], C["blue_bg"], 11.5, 9.2))
    b.append(box(20, 150, 200, 62, l["sl"][0], list(l["sl"][1:]), C["violet"], C["violet_bg"], 11.5, 9.2))
    b.append(box(20, 240, 200, 62, l["si"][0], list(l["si"][1:]), C["violet"], C["violet_bg"], 11.5, 9.2))
    b.append(box(280, 100, 220, 62, l["l1"][0], list(l["l1"][1:]), C["amber"], C["amber_bg"], 11, 9.2))
    b.append(box(560, 170, 230, 62, l["l"][0], list(l["l"][1:]), C["amber"], C["amber_bg"], 11, 9.2))
    b.append(box(280, 300, 230, 62, l["ti"][0], list(l["ti"][1:]), C["green"], C["green_bg"], 11, 9.0))
    b.append(box(560, 300, 230, 62, l["te"][0], list(l["te"][1:]), C["green"], C["green_bg"], 11, 9.0))
    b.append(box(820, 230, 140, 72, l["tr"][0], list(l["tr"][1:]), C["red"], C["red_bg"], 10.5, 8.6))
    b.append(arrow(220, 91, 278, 120)); b.append(arrow(220, 181, 278, 140))
    b.append(arrow(500, 131, 558, 190)); b.append(arrow(220, 271, 558, 210)); b.append(arrow(220, 91, 558, 180))
    b.append(arrow(120, 212, 300, 298)); b.append(arrow(675, 232, 675, 298)); b.append(arrow(790, 201, 840, 228))
    return svg(965, 380, l["t"], l["s"], "".join(b))


def all_diagrams(lang):
    out = D54.all_diagrams(lang)
    lab = copy.deepcopy(D53.L[lang]); lab.update(D54.EXTRA[lang]); lab.update(EXTRA[lang])
    out["arch"] = D53.d_arch(lab)
    out["anchor"] = d_anchor(ANCHOR[lang])
    return out
