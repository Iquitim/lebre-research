"""v053_diagrams.py — architecture diagrams of the self-contained LEBRE v0.53 documents (inline SVG), same primitives as
the earlier documents (v032_diagrams, imported, not changed). The diagrams of the structural core are drawn by
v052_diagrams (imported, not changed) with labels retitled here for this document. Labels in PT-BR and EN."""
import copy

import v052_diagrams as D52
from v032_diagrams import C, _esc, arrow, box, svg

L = {
    "pt": dict(
        a_t="D1 — Arquitetura completa da LEBRE: núcleo estrutural + M1 + M2",
        a_s="O núcleo calcula a previsão L e é o único dono das mudanças de estrutura; M1 e M2 só mudam como a previsão final é formada",
        in1="Observação em t", in2="entradas x(t), alvo y(t−1)",
        b1="Núcleo estrutural (D2)", b2="memória + estrutura + plano", b3="de mudanças → previsão L",
        e1="M1 — especialista E", e2="AR2 + bandas de defasagem", e3="de até 5 entradas (RLS)",
        h1="M1 — combinação", h2="AdaHedge no erro quadrático", h3="L' = (1−ω)·L + ω·E",
        r1="Referência trivial R", r2="zero, persistência", r3="ou sazonal ingênuo",
        d1="H", d2="AdaHedge R × L'", m1="W", m2="troca única R → L'",
        p1="M2 — (A,B)-Prod", p2="H (confiança), W (oportunista)", p3="perdas ÷ máx. com esquecimento",
        y1="Previsão ŷ(t)", y2="+ intervalo de 90%",
        sh="sombra: E só pesa depois de 100 atualizações",
    ),
    "en": dict(
        a_t="D1 — Complete LEBRE architecture: structural core + M1 + M2",
        a_s="The core computes the forecast L and is the only owner of structural changes; M1 and M2 only change how the final forecast is formed",
        in1="Observation at t", in2="inputs x(t), target y(t−1)",
        b1="Structural core (D2)", b2="memory + structure + change", b3="plane → forecast L",
        e1="M1 — expert E", e2="AR2 + lag bands", e3="of up to 5 inputs (RLS)",
        h1="M1 — combination", h2="AdaHedge on squared error", h3="L' = (1−ω)·L + ω·E",
        r1="Trivial reference R", r2="zero, persistence", r3="or seasonal naive",
        d1="H", d2="AdaHedge R vs L'", m1="W", m2="one-way switch R → L'",
        p1="M2 — (A,B)-Prod", p2="H (confidence), W (opportunist)", p3="losses ÷ forgetting max",
        y1="Forecast ŷ(t)", y2="+ 90% interval",
        sh="shadow: E weighs only after 100 updates",
    ),
}

P = {
    "pt": dict(
        t="D7 — Como se chegou a M1 e M2: desenhos, falhas e o que cada uma ensinou",
        s="Cada caixa é um desenho medido com plano registrado antes; vermelho = reprovado, verde = aprovado e confirmado",
        m2=[("P", "Prod com perda recortada", "aprovada no desenv. e na val. 3"),
            ("Val. 4", "P falha em câmbio e maré", "choques dominam o MSE"),
            ("Q", "perda ÷ maior erro já visto", "Prod congela após recorde"),
            ("Q2", "maior erro com esquecimento", "aprovada; confirmada na val. 5")],
        m1=[("r2", "AR2 + bandas, Prod recortado", "cego ao erro grande (val. 4)"),
            ("r3", "AR2 + entradas atuais", "perde B03; Prod congela"),
            ("r4", "r2 + Prod normalizado", "Prod ignora o especialista"),
            ("r5", "r2 + AdaHedge no erro²", "aprovado; confirmado na val. 5")],
        l2="M2", l1="M1",
        lesson="Lição comum: o Prod exige perdas em [0, 1]; as três formas de pôr o erro quadrático nesse intervalo distorceram o que ele otimizava. A M1 passou a combinar direto no erro quadrático.",
    ),
    "en": dict(
        t="D7 — How M1 and M2 were reached: designs, failures and what each one taught",
        s="Each box is a design measured with a plan registered beforehand; red = rejected, green = approved and confirmed",
        m2=[("P", "Prod on clipped loss", "passed dev. and val. 3"),
            ("Val. 4", "P fails on FX and tides", "shocks dominate the MSE"),
            ("Q", "loss ÷ running max error", "Prod freezes after a record"),
            ("Q2", "forgetting running max", "approved; confirmed in val. 5")],
        m1=[("r2", "AR2 + bands, clipped Prod", "blind to large errors (val. 4)"),
            ("r3", "AR2 + current inputs", "loses B03; Prod freezes"),
            ("r4", "r2 + normalised Prod", "Prod ignores the expert"),
            ("r5", "r2 + AdaHedge on error²", "approved; confirmed in val. 5")],
        l2="M2", l1="M1",
        lesson="Common lesson: Prod needs losses in [0, 1]; the three ways of putting the squared error there distorted what it optimised. M1 now combines directly on the squared error.",
    ),
}

# Core diagrams (v052_diagrams), retitled for this document: the core forecast is L, not the final output.
CORE = {
    "pt": dict(a_t="D2 — Núcleo estrutural: previsão viva + experimentos em sombra",
               a_s="O caminho da previsão (em cima) é barato e sempre ativo; o plano de mudanças (embaixo) propõe, testa e decide mudanças de estrutura",
               a_Y="Previsão L", a_Y2="(segue para M1)", a_C3="L = ŷ_M + w_S(ŷ_S − ŷ_M)",
               f_t="D3 — O que acontece em um passo de tempo",
               f_steps=[("Ler", "x(t) e própria", "defasagem; contrato"), ("Prever", "núcleo → L; M1 → L';", "M2 → ŷ e intervalo"),
                        ("Observar", "chega y(t)", "(ou lacuna)"), ("Aprender", "núcleo: NLMS, RLS,", "evidência; M1 e M2"),
                        ("Decidir", "a cada 10 passos:", "aceitar, encerrar, abrir")],
               u_t="D4 — Unidade de mudança: uma entrada inteira, refinada por divisões",
               l_t="D5 — Ciclo de vida de uma hipótese de mudança",
               m_t="D6 — Cadeia de medição do núcleo em microcontrolador simulado",
               m_s="O núcleo, portado para C99 em precisão simples, conferido contra o Python e executado num Cortex-M4F simulado"),
    "en": dict(a_t="D2 — Structural core: live forecast + shadow experiments",
               a_s="The forecast path (top) is cheap and always active; the change plane (bottom) proposes, tests and decides structural changes",
               a_Y="Forecast L", a_Y2="(goes to M1)", a_C3="L = ŷ_M + w_S(ŷ_S − ŷ_M)",
               f_t="D3 — What happens in one time step",
               f_steps=[("Read", "x(t) and own", "lag; contract"), ("Predict", "core → L; M1 → L';", "M2 → ŷ and interval"),
                        ("Observe", "y(t) arrives", "(or a gap)"), ("Learn", "core: NLMS, RLS,", "evidence; M1 and M2"),
                        ("Decide", "every 10 steps:", "accept, close, open")],
               u_t="D4 — Unit of change: a whole input, refined by splits",
               l_t="D5 — Lifecycle of a change hypothesis",
               m_t="D6 — Measurement chain of the core on a simulated microcontroller",
               m_s="The core, ported to C99 in single precision, checked against Python and run on a simulated Cortex-M4F"),
}


def d_arch(l):
    b = []
    b.append(box(20, 150, 140, 70, l["in1"], [l["in2"]], C["blue"], C["blue_bg"], 11.5, 9.4))
    b.append(box(195, 75, 190, 84, l["b1"], [l["b2"], l["b3"]], C["violet"], C["violet_bg"], 11.5, 9.4))
    b.append(box(195, 205, 190, 84, l["e1"], [l["e2"], l["e3"]], C["violet"], C["violet_bg"], 11.5, 9.4))
    b.append(box(420, 140, 180, 84, l["h1"], [l["h2"], l["h3"]], C["amber"], C["amber_bg"], 11.5, 9.4))
    b.append(box(420, 285, 180, 76, l["r1"], [l["r2"], l["r3"]], C["green"], C["green_bg"], 11.5, 9.4))
    b.append(box(640, 135, 110, 60, l["d1"], [l["d2"]], C["red"], C["red_bg"], 11.5, 8.6))
    b.append(box(640, 230, 110, 60, l["m1"], [l["m2"]], C["red"], C["red_bg"], 11.5, 8.6))
    b.append(box(780, 168, 160, 84, l["p1"], [l["p2"], l["p3"]], C["amber"], C["amber_bg"], 11.5, 8.6))
    b.append(box(800, 290, 120, 60, l["y1"], [l["y2"]], C["blue"], C["blue_bg"], 11.5, 9.4))
    b.append(arrow(160, 175, 193, 120)); b.append(arrow(160, 195, 193, 245))
    b.append(arrow(385, 125, 418, 168)); b.append(arrow(385, 245, 418, 200))
    b.append(arrow(600, 175, 638, 165)); b.append(arrow(600, 195, 638, 255))
    b.append(arrow(600, 318, 638, 280)); b.append(arrow(600, 312, 638, 185))
    b.append(arrow(750, 165, 778, 195)); b.append(arrow(750, 260, 778, 225))
    b.append(arrow(860, 252, 860, 288))
    b.append(f'<text x="290" y="312" font-size="9.6" fill="{C["muted"]}" text-anchor="middle">{_esc(l["sh"])}</text>')
    return svg(965, 380, l["a_t"], l["a_s"], "".join(b))


def d_path(l):
    b = []
    w, h, gap = 192, 74, 28
    for row, (key, y0, lab_) in enumerate((("m2", 92, l["l2"]), ("m1", 222, l["l1"]))):
        b.append(f'<text x="22" y="{y0 + 42}" font-size="14" font-weight="700" fill="{C["ink"]}">{_esc(lab_)}</text>')
        for i, (t, s1, s2) in enumerate(l[key]):
            x = 60 + i * (w + gap)
            ok = i == 3
            b.append(box(x, y0, w, h, t, [s1, s2], C["green"] if ok else C["red"], C["green_bg"] if ok else C["red_bg"], 11.5, 9.2))
            if i < 3:
                b.append(arrow(x + w, y0 + h / 2, x + w + gap - 2, y0 + h / 2))
    b.append(f'<rect x="22" y="320" width="921" height="44" rx="6" fill="{C["grey_bg"]}" stroke="{C["grey"]}"/>')
    words = l["lesson"].split(" ")
    half = len(words) // 2
    for k, part in enumerate((" ".join(words[:half]), " ".join(words[half:]))):
        b.append(f'<text x="482" y="{338 + 15 * k}" font-size="9.8" fill="{C["ink"]}" text-anchor="middle">{_esc(part)}</text>')
    return svg(965, 380, l["t"], l["s"], "".join(b))


def all_diagrams(lang):
    core = copy.deepcopy(D52.L[lang]); core.update(CORE[lang])
    return {"arch": d_arch(L[lang]), "path": d_path(P[lang]), "core": D52.d_arch(core), "step": D52.d_step(core),
            "unit": D52.d_unit(core), "life": D52.d_life(core), "mcu": D52.d_mcu(core)}
