"""v052_diagrams.py — architecture diagrams of the LEBRE v0.52 documents (inline SVG, same visual set as the earlier
documents). Labels in PT-BR and EN."""
from v032_diagrams import C, _esc, arrow, box, lab, svg

L = {
    "pt": dict(
        a_t="D1 — Arquitetura da LEBRE: previsão viva + experimentos em sombra",
        a_s="O caminho da previsão (em cima) custa pouco e é sempre ativo; o plano de mudanças (embaixo) propõe, testa e decide mudanças de estrutura",
        a_in="Observação em t", a_in2="entradas x(t) padronizadas", a_in3="+ próprio passado do alvo",
        a_M="M — memória", a_M2="nível, ciclo(s), perfil sazonal", a_M3="NLMS com pisos de escala",
        a_S="S — especialista estrutural", a_S2="base: viés + valor atual das entradas", a_S3="+ blocos das unidades aceitas",
        a_C="Combinação", a_C2="média dinâmica de modelos", a_C3="ŷ = ŷ_M + w_S(ŷ_S − ŷ_M)",
        a_O="Contrato de saída", a_O2="envelope dos valores", a_O3="já observados",
        a_Y="Previsão ŷ(t)", a_Y2="+ intervalo de 90%",
        a_plane="Plano de mudanças (experimentos com evidência sempre válida)",
        a_scr="Triagem", a_scr2="correlação pré-branqueada", a_scr3="por entrada, a cada 4 passos",
        a_slot="2 vagas de experimento", a_slot2="desafiante G = S + g em sombra", a_slot3="(mínimos quadrados no episódio)",
        a_ev="E-process", a_ev2="melhora da perda recortada", a_ev3="unilateral, sempre válido",
        a_dec="Decisão", a_dec2="níveis tipo e-LOND", a_dec3="controle de mudanças falsas",
        a_fb="aceita: S muda", a_obs="registro: eventos, grupos, respostas",
        f_t="D2 — O que acontece em um passo de tempo",
        f_s="Ordem estritamente causal: tudo o que decide a previsão em t usa apenas dados até t−1",
        f_steps=[("Ler", "x(t) e própria", "defasagem; contrato"), ("Prever", "M, S e desafiantes;", "combinar; limitar"),
                 ("Observar", "chega y(t)", "(ou lacuna)"), ("Aprender", "NLMS em M e S; RLS", "e evidência nos desafiantes"),
                 ("Decidir", "a cada 10 passos:", "aceitar, encerrar, abrir")],
        f_gap="Lacuna do alvo: nada aprende; a memória recebe o último valor observado (retenção), nunca a própria previsão.",
        u_t="D3 — Unidade de mudança: uma entrada inteira, refinada por divisões",
        u_s="O desafiante de uma entrada usa médias do passado em faixas de oitava; divisões hierárquicas (tipo Haar) refinam a resposta depois da aceitação",
        u_lags="atrasos da entrada x_i", u_now="x_i(t)", u_peak="atraso de pico k*", u_peak2="(escolhido pelo próprio desafiante)",
        u_split="divisão: faixa → duas metades (nova hipótese, testada só se o \"pai\" foi aceito)",
        u_eq="Desafiante da unidade: ŷ_G = ŷ_S + Σ_b θ_b · média(x_i, faixa b) + θ_k · x_i(t−k*) + θ_0 · x_i(t)",
        l_t="D4 — Ciclo de vida de uma hipótese de mudança",
        l_s="Hipóteses persistentes: a evidência de uma mudança se acumula entre episódios; cada decisão usa um nível fixado na criação",
        l_c="Candidata", l_c2="triagem acima do", l_c3="quantil 99% (χ²)",
        l_w="Aquecimento", l_w2="250 amostras: só treina", l_w3="o desafiante; escolhe k*",
        l_e="Evidência", l_e2="e-process acumula", l_e3="log E vs log(1/α_k)",
        l_a="Aceita", l_a2="S passa a incluir", l_a3="a mudança",
        l_p="Pausa", l_p2="varredura: soma ≤ 0 após 100", l_p3="ou 5.000 amostras; espera 2.000",
        l_r="Teste de remoção periódico", l_r2="(ε = −0,002: basta não piorar)",
        l_kinds="Tipos: acrescentar (ε = 0,002) · remover (ε = −0,002) · trocar (com 4 unidades ativas) · dividir (ε = 0,002)",
        m_t="D5 — Cadeia de medição em microcontrolador simulado",
        m_s="O mesmo algoritmo, portado para C99 em precisão simples, conferido contra o Python e executado num Cortex-M4F simulado",
        m_py="Python congelado", m_py2="referência (float64)",
        m_c="Porte C99", m_c2="float64 e float32", m_c3="capacidade fixa",
        m_eq="Equivalência", m_eq2="decisões e NMSE", m_eq3="(PC, float32)",
        m_gcc="arm-none-eabi-gcc 15.2", m_gcc2="-O2, FPU fpv4-sp-d16", m_gcc3="sem contração FMA",
        m_ren="Renode 1.17", m_ren2="STM32F4 (Cortex-M4F)", m_ren3="contador DWT",
        m_out="Medidas por passo", m_out2="instruções (DWT)", m_out3="ciclos: rastreio + manual",
        m_note="O simulador conta instruções executadas, mas não modela o pipeline; os ciclos vêm do rastreio de execução com os tempos publicados do Cortex-M4.",
    ),
    "en": dict(
        a_t="D1 — LEBRE architecture: live forecast + shadow experiments",
        a_s="The forecast path (top) is cheap and always active; the change plane (bottom) proposes, tests and decides structural changes",
        a_in="Observation at t", a_in2="standardised inputs x(t)", a_in3="+ the target's own past",
        a_M="M — memory", a_M2="level, cycle(s), seasonal profile", a_M3="NLMS with scale floors",
        a_S="S — structural expert", a_S2="base: bias + current input values", a_S3="+ blocks of accepted units",
        a_C="Combination", a_C2="dynamic model averaging", a_C3="ŷ = ŷ_M + w_S(ŷ_S − ŷ_M)",
        a_O="Output contract", a_O2="envelope of the values", a_O3="already observed",
        a_Y="Forecast ŷ(t)", a_Y2="+ 90% interval",
        a_plane="Change plane (experiments with anytime-valid evidence)",
        a_scr="Screening", a_scr2="prewhitened correlation", a_scr3="per input, every 4 steps",
        a_slot="2 experiment slots", a_slot2="challenger G = S + g in shadow", a_slot3="(least squares within episode)",
        a_ev="E-process", a_ev2="improvement of clipped loss", a_ev3="one-sided, anytime-valid",
        a_dec="Decision", a_dec2="e-LOND-type levels", a_dec3="false-change control",
        a_fb="accepted: S changes", a_obs="log: events, groups, responses",
        f_t="D2 — What happens in one time step",
        f_s="Strictly causal order: everything that decides the forecast at t uses only data up to t−1",
        f_steps=[("Read", "x(t) and own", "lag; contract"), ("Predict", "M, S, challengers;", "combine; bound"),
                 ("Observe", "y(t) arrives", "(or a gap)"), ("Learn", "NLMS in M and S; RLS", "and evidence in challengers"),
                 ("Decide", "every 10 steps:", "accept, close, open")],
        f_gap="Target gap: nothing learns; the memory receives the last observed value (hold), never its own forecast.",
        u_t="D3 — Unit of change: a whole input, refined by splits",
        u_s="An input challenger uses means of the past over octave bands; hierarchical (Haar-like) splits refine the response after acceptance",
        u_lags="lags of input x_i", u_now="x_i(t)", u_peak="peak lag k*", u_peak2="(chosen by the challenger itself)",
        u_split="split: band → two halves (a new hypothesis, tested only if the \"parent\" was accepted)",
        u_eq="Unit challenger: ŷ_G = ŷ_S + Σ_b θ_b · mean(x_i, band b) + θ_k · x_i(t−k*) + θ_0 · x_i(t)",
        l_t="D4 — Lifecycle of a change hypothesis",
        l_s="Persistent hypotheses: the evidence for a change accumulates across episodes; each decision uses a level fixed at creation",
        l_c="Candidate", l_c2="screen above the", l_c3="99% quantile (χ²)",
        l_w="Warm-up", l_w2="250 samples: only trains", l_w3="the challenger; picks k*",
        l_e="Evidence", l_e2="e-process accrues", l_e3="log E vs log(1/α_k)",
        l_a="Accepted", l_a2="S now includes", l_a3="the change",
        l_p="Pause", l_p2="scan: sum ≤ 0 after 100", l_p3="or 5,000 samples; wait 2,000",
        l_r="Periodic removal test", l_r2="(ε = −0.002: not worse suffices)",
        l_kinds="Kinds: add (ε = 0.002) · remove (ε = −0.002) · swap (with 4 active units) · split (ε = 0.002)",
        m_t="D5 — Measurement chain on a simulated microcontroller",
        m_s="The same algorithm, ported to C99 in single precision, checked against Python and run on a simulated Cortex-M4F",
        m_py="Frozen Python", m_py2="reference (float64)",
        m_c="C99 port", m_c2="float64 and float32", m_c3="fixed capacity",
        m_eq="Equivalence", m_eq2="decisions and NMSE", m_eq3="(PC, float32)",
        m_gcc="arm-none-eabi-gcc 15.2", m_gcc2="-O2, FPU fpv4-sp-d16", m_gcc3="no FMA contraction",
        m_ren="Renode 1.17", m_ren2="STM32F4 (Cortex-M4F)", m_ren3="DWT counter",
        m_out="Per-step measures", m_out2="instructions (DWT)", m_out3="cycles: trace + manual",
        m_note="The simulator counts executed instructions but does not model the pipeline; cycles come from the execution trace with the published Cortex-M4 timings.",
    ),
}


def d_arch(l):
    b = []
    b.append(box(20, 120, 150, 80, l["a_in"], [l["a_in2"], l["a_in3"]], C["blue"], C["blue_bg"]))
    b.append(box(215, 68, 200, 78, l["a_M"], [l["a_M2"], l["a_M3"]], C["green"], C["green_bg"]))
    b.append(box(215, 168, 200, 78, l["a_S"], [l["a_S2"], l["a_S3"]], C["violet"], C["violet_bg"]))
    b.append(box(460, 112, 170, 88, l["a_C"], [l["a_C2"], l["a_C3"]], C["amber"], C["amber_bg"], lsize=9.8))
    b.append(box(655, 112, 160, 84, l["a_O"], [l["a_O2"], l["a_O3"]], C["red"], C["red_bg"], lsize=9.4))
    b.append(box(840, 118, 110, 70, l["a_Y"], [l["a_Y2"]], C["blue"], C["blue_bg"]))
    b.append(arrow(170, 150, 213, 110)); b.append(arrow(170, 170, 213, 205))
    b.append(arrow(415, 107, 458, 145)); b.append(arrow(415, 207, 458, 170))
    b.append(arrow(630, 155, 653, 155)); b.append(arrow(815, 153, 838, 153))
    b.append(f'<rect x="20" y="276" width="925" height="170" rx="8" fill="{C["grey_bg"]}" stroke="{C["grey"]}" stroke-dasharray="6,4"/>')
    b.append(f'<text x="34" y="436" font-size="11" font-weight="700" fill="{C["muted"]}">{_esc(l["a_plane"])}</text>')
    b.append(box(40, 310, 185, 88, l["a_scr"], [l["a_scr2"], l["a_scr3"]], C["violet"], C["violet_bg"], 11.5, 9.6))
    b.append(box(260, 310, 215, 88, l["a_slot"], [l["a_slot2"], l["a_slot3"]], C["violet"], C["violet_bg"], 11.5, 9.6))
    b.append(box(510, 310, 200, 88, l["a_ev"], [l["a_ev2"], l["a_ev3"]], C["red"], C["red_bg"], 11.5, 9.6))
    b.append(box(745, 310, 180, 88, l["a_dec"], [l["a_dec2"], l["a_dec3"]], C["amber"], C["amber_bg"], 11.5, 9.6))
    b.append(arrow(225, 354, 258, 354)); b.append(arrow(475, 354, 508, 354)); b.append(arrow(710, 354, 743, 354))
    b.append(arrow(835, 308, 380, 250, "green", True, l["a_fb"], 640, 268, C["green"]))
    b.append(arrow(315, 248, 330, 308, "line", True))
    b.append(f'<text x="930" y="436" font-size="10" fill="{C["muted"]}" text-anchor="end">{_esc(l["a_obs"])}</text>')
    return svg(965, 460, l["a_t"], l["a_s"], "".join(b))


def d_step(l):
    b = []; x, w, h = 25, 162, 90
    cols = [(C["blue"], C["blue_bg"]), (C["violet"], C["violet_bg"]), (C["amber"], C["amber_bg"]), (C["green"], C["green_bg"]), (C["red"], C["red_bg"])]
    for i, (t, s1, s2) in enumerate(l["f_steps"]):
        xx = x + i * 188
        b.append(box(xx, 78, w, h, f"{i + 1}. {t}", [s1, s2], cols[i][0], cols[i][1], tsize=11.5, lsize=9.6))
        if i < 4:
            b.append(arrow(xx + w, 123, xx + 186, 123))
    b.append(f'<rect x="25" y="190" width="914" height="40" rx="6" fill="{C["grey_bg"]}" stroke="{C["grey"]}"/>')
    b.append(f'<text x="482" y="215" font-size="10.2" fill="{C["ink"]}" text-anchor="middle">{_esc(l["f_gap"])}</text>')
    return svg(965, 245, l["f_t"], l["f_s"], "".join(b))


def d_unit(l):
    b = []
    x0, x1, y0 = 70, 880, 150
    n = 32
    xs = lambda k: x1 - (x1 - x0) * k / n          # lag k to the left; k = 0 (now) on the right
    bands = [(1, 1), (2, 3), (4, 7), (8, 15), (16, 31)]
    colb = ["#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6"]
    for (lo, hi), c in zip(bands, colb):
        b.append(f'<rect x="{xs(hi + 0.5):.1f}" y="{y0 - 38}" width="{xs(lo - 0.5) - xs(hi + 0.5):.1f}" height="34" fill="{c}" stroke="#FFFFFF" stroke-width="2" rx="3"/>')
        b.append(f'<text x="{(xs(hi + 0.5) + xs(lo - 0.5)) / 2:.1f}" y="{y0 - 16}" font-size="10.5" font-weight="700" fill="{C["ink"]}" text-anchor="middle">[{lo}–{hi}]' if lo != hi else
                 f'<text x="{(xs(hi + 0.5) + xs(lo - 0.5)) / 2:.1f}" y="{y0 - 16}" font-size="10.5" font-weight="700" fill="{C["ink"]}" text-anchor="middle">[1]')
        b.append("</text>")
    b.append(f'<rect x="{xs(0.5):.1f}" y="{y0 - 38}" width="{xs(-0.5) - xs(0.5):.1f}" height="34" fill="{C["green_bg"]}" stroke="{C["green"]}" rx="3"/>')
    b.append(f'<text x="{xs(0):.1f}" y="{y0 + 14}" font-size="10" fill="{C["green"]}" text-anchor="middle">{_esc(l["u_now"])}</text>')
    for k in (1, 2, 4, 8, 16, 31):
        b.append(f'<text x="{xs(k):.1f}" y="{y0 + 14}" font-size="9" fill="{C["muted"]}" text-anchor="middle">t−{k}</text>')
    b.append(f'<text x="{x0}" y="{y0 - 48}" font-size="10.5" fill="{C["muted"]}">{_esc(l["u_lags"])} →</text>')
    k = 12
    b.append(f'<line x1="{xs(k):.1f}" y1="{y0 - 44}" x2="{xs(k):.1f}" y2="{y0 + 2}" stroke="{C["red"]}" stroke-width="2.4"/>')
    b.append(f'<text x="{xs(k):.1f}" y="{y0 + 30}" font-size="10" font-weight="700" fill="{C["red"]}" text-anchor="middle">{_esc(l["u_peak"])}</text>')
    b.append(f'<text x="{xs(k):.1f}" y="{y0 + 43}" font-size="9" fill="{C["red"]}" text-anchor="middle">{_esc(l["u_peak2"])}</text>')
    # split tree of band [8-15]
    yy = 230
    par = (8, 15); halves = [(8, 11), (12, 15)]; quarters = [(12, 13), (14, 15)]
    def seg(lo, hi, y, c):
        return (f'<rect x="{xs(hi + 0.5):.1f}" y="{y}" width="{xs(lo - 0.5) - xs(hi + 0.5):.1f}" height="24" fill="{c}" stroke="#FFFFFF" stroke-width="2" rx="3"/>'
                f'<text x="{(xs(hi + 0.5) + xs(lo - 0.5)) / 2:.1f}" y="{y + 16}" font-size="9.6" fill="{C["ink"]}" text-anchor="middle">[{lo}–{hi}]</text>')
    b.append(seg(*par, yy, "#60A5FA"))
    for h in halves:
        b.append(seg(*h, yy + 36, "#93C5FD"))
    for q in quarters:
        b.append(seg(*q, yy + 72, "#BFDBFE"))
    cx = lambda lo, hi: (xs(hi + 0.5) + xs(lo - 0.5)) / 2
    for h in halves:
        b.append(f'<line x1="{cx(*par):.1f}" y1="{yy + 24}" x2="{cx(*h):.1f}" y2="{yy + 36}" stroke="{C["line"]}" stroke-width="1"/>')
    for q in quarters:
        b.append(f'<line x1="{cx(12, 15):.1f}" y1="{yy + 60}" x2="{cx(*q):.1f}" y2="{yy + 72}" stroke="{C["line"]}" stroke-width="1"/>')
    b.append(f'<text x="{xs(17):.1f}" y="{yy + 52}" font-size="10" fill="{C["ink"]}" text-anchor="end">{_esc(l["u_split"])}</text>')
    b.append(f'<rect x="40" y="345" width="885" height="34" rx="6" fill="{C["violet_bg"]}" stroke="{C["violet"]}"/>')
    b.append(f'<text x="482" y="367" font-size="11" fill="{C["ink"]}" text-anchor="middle">{_esc(l["u_eq"])}</text>')
    return svg(965, 392, l["u_t"], l["u_s"], "".join(b))


def d_life(l):
    b = []
    b.append(box(25, 90, 160, 84, l["l_c"], [l["l_c2"], l["l_c3"]], C["grey"], C["grey_bg"]))
    b.append(box(225, 90, 170, 84, l["l_w"], [l["l_w2"], l["l_w3"]], C["amber"], C["amber_bg"]))
    b.append(box(435, 90, 170, 84, l["l_e"], [l["l_e2"], l["l_e3"]], C["violet"], C["violet_bg"]))
    b.append(box(770, 90, 170, 84, l["l_a"], [l["l_a2"], l["l_a3"]], C["green"], C["green_bg"]))
    b.append(box(435, 214, 170, 74, l["l_p"], [l["l_p2"], l["l_p3"]], C["red"], C["red_bg"], lsize=9.4))
    b.append(arrow(185, 132, 223, 132)); b.append(arrow(395, 132, 433, 132))
    b.append(arrow(605, 132, 768, 132, "green", False, "log E ≥ log(1/α_k)", 686, 122, C["green"]))
    b.append(arrow(520, 174, 520, 212, "red"))
    b.append(f'<path d="M 435 252 L 105 252 L 105 176" fill="none" stroke="{C["line"]}" stroke-width="1.3" stroke-dasharray="5,4" marker-end="url(#a)"/>')
    b.append(box(770, 214, 170, 74, l["l_r"], [l["l_r2"]], C["blue"], C["blue_bg"], 10.5, 9.2))
    b.append(arrow(855, 174, 855, 212, "blue", True))
    b.append(f'<text x="482" y="318" font-size="10.3" fill="{C["ink"]}" text-anchor="middle">{_esc(l["l_kinds"])}</text>')
    return svg(965, 332, l["l_t"], l["l_s"], "".join(b))


def d_mcu(l):
    b = []
    specs = [(l["m_py"], [l["m_py2"]], C["blue"], C["blue_bg"]), (l["m_c"], [l["m_c2"], l["m_c3"]], C["violet"], C["violet_bg"]),
             (l["m_eq"], [l["m_eq2"], l["m_eq3"]], C["green"], C["green_bg"]), (l["m_gcc"], [l["m_gcc2"], l["m_gcc3"]], C["amber"], C["amber_bg"]),
             (l["m_ren"], [l["m_ren2"], l["m_ren3"]], C["red"], C["red_bg"]), (l["m_out"], [l["m_out2"], l["m_out3"]], C["blue"], C["blue_bg"])]
    x, w = 20, 140
    for i, (t, ls, c, f) in enumerate(specs):
        xx = x + i * 157
        b.append(box(xx, 78, w, 84, t, ls, c, f, tsize=10.8, lsize=9.2))
        if i < 5:
            b.append(arrow(xx + w, 120, xx + 155, 120))
    b.append(f'<text x="482" y="190" font-size="9.8" fill="{C["muted"]}" text-anchor="middle">{_esc(l["m_note"])}</text>')
    return svg(965, 205, l["m_t"], l["m_s"], "".join(b))


def all_diagrams(lang):
    l = L[lang]
    return {"arch": d_arch(l), "step": d_step(l), "unit": d_unit(l), "life": d_life(l), "mcu": d_mcu(l)}
