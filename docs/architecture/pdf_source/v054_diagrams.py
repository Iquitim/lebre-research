"""v054_diagrams.py — diagrams of the self-contained LEBRE v0.54 documents: the v0.53 diagrams (v053_diagrams, imported,
not changed), with the architecture diagram relabelled to show the v0.54 mechanisms (M1 dormancy, triggered removal and
cheap equivalence report in the core)."""
import copy

import v053_diagrams as D53

EXTRA = {
    "pt": dict(a_s="O núcleo calcula L e é o único dono das mudanças de estrutura (inclusive a remoção disparada); M1 dorme sem uso; M1 e M2 só mudam como a saída é formada",
               b2="memória + estrutura + plano", b3="de mudanças (+ remoção) → L",
               e2="AR2 + bandas de defasagem", e3="(RLS); dorme sem uso"),
    "en": dict(a_s="The core computes L and is the only owner of structural changes (triggered removal included); M1 sleeps when unused; M1 and M2 only change how the output is formed",
               b2="memory + structure + change", b3="plane (+ removal) → L",
               e2="AR2 + lag bands of up to", e3="5 inputs (RLS); sleeps if unused"),
}


def all_diagrams(lang):
    out = D53.all_diagrams(lang)
    lab = copy.deepcopy(D53.L[lang]); lab.update(EXTRA[lang])
    out["arch"] = D53.d_arch(lab)
    return out
