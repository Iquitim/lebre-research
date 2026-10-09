"""v053_text.py — bilingual content of the LEBRE v0.53 specification and technical report. No local paths; every
empirical number comes from v053_data.py. Claims are scoped to the tests performed. The unchanged v0.52 base is only
summarised; its full description is the v0.52 specification, revision 1."""
import re

REFS = [
    "Adamskiy, D., Koolen, W. M., Chernov, A., Vovk, V. (2016). A closer look at adaptive regret. <em>Journal of Machine Learning Research</em> 17(23), 1–21.",
    "Alquier, P. (2021). Non-exponentially weighted aggregation: regret bounds for unbounded loss functions. <em>ICML</em>.",
    "Ansari, A. F. et al. (2025). Chronos-2: from univariate to universal forecasting. <em>arXiv preprint</em>.",
    "Cesa-Bianchi, N., Gaillard, P., Lugosi, G., Stoltz, G. (2012). Mirror descent meets fixed share (and feels no regret). <em>NeurIPS 25</em>.",
    "Cesa-Bianchi, N., Mansour, Y., Stoltz, G. (2007). Improved second-order bounds for prediction with expert advice. <em>Machine Learning</em> 66, 321–352.",
    "Chagas, V. B. P. et al. (2020). CAMELS-BR: hydrometeorological time series and landscape attributes for 897 catchments in Brazil. <em>Earth System Science Data</em> 12, 2075–2096.",
    "Chen, S. (2017). Beijing Multi-Site Air Quality. <em>UCI Machine Learning Repository</em>, doi:10.24432/C5RK5G.",
    "de Rooij, S., van Erven, T., Grünwald, P. D., Koolen, W. M. (2014). Follow the leader if you can, hedge if you must. <em>Journal of Machine Learning Research</em> 15, 1281–1316.",
    "Even-Dar, E., Kearns, M., Mansour, Y., Wortman, J. (2008). Regret to the best vs. regret to the average. <em>Machine Learning</em> 72, 21–37.",
    "Hazan, E., Kale, S. (2010). Extracting certainty from uncertainty: regret bounded by variation in costs. <em>Machine Learning</em> 80, 165–188.",
    "Koolen, W. M. (2013). The Pareto regret frontier. <em>NeurIPS 26</em>.",
    "Ljung, L. (1999). <em>System Identification: Theory for the User</em>, 2nd ed. Prentice Hall.",
    "Mhammedi, Z., Koolen, W. M., van Erven, T. (2019). Lipschitz adaptivity with multiple learning rates in online learning. <em>COLT</em>.",
    "Miller, C. et al. (2020). The Building Data Genome Project 2. <em>Scientific Data</em> 7, 368.",
    "Moulin, A., Esposito, E., van der Hoeven, D. (2025). When lower-order terms dominate: adaptive expert algorithms for heavy-tailed losses. <em>arXiv:2506.01722</em>.",
    "Orabona, F., Pál, D. (2018). Scale-free online learning. <em>Theoretical Computer Science</em> 716, 50–69.",
    "Sani, A., Neu, G., Lazaric, A. (2014). Exploiting easy data in online optimization. <em>NeurIPS 27</em>.",
    "van Erven, T., Grünwald, P., de Rooij, S. (2012). Catching up faster by switching sooner: a predictive approach to adaptive estimation with an application to the AIC–BIC dilemma. <em>Journal of the Royal Statistical Society B</em> 74(3), 361–417.",
    "V'yugin, V., Trunov, V. (2019). Online aggregation of unbounded losses using shifting experts with confidence. <em>Machine Learning</em>; arXiv:1808.00741.",
    "Wang, H., Ramdas, A. (2023). Catoni-style confidence sequences for heavy-tailed mean estimation. <em>Stochastic Processes and their Applications</em>.",
]

FAM = {
    "pt": {"camels": "Bacias (CAMELS-BR)", "bdg2": "Prédios (BDG2)", "solar": "Usinas solares (ONS)", "eolica": "Usinas eólicas (ONS)",
           "carga": "Carga 2026 (ONS)", "fx_ret": "Câmbio: retornos", "fx_abs": "Câmbio: volatilidade", "fx_niv": "Câmbio: níveis"},
    "en": {"camels": "Basins (CAMELS-BR)", "bdg2": "Buildings (BDG2)", "solar": "Solar plants (ONS)", "eolica": "Wind plants (ONS)",
           "carga": "Load 2026 (ONS)", "fx_ret": "FX: returns", "fx_abs": "FX: volatility", "fx_niv": "FX: levels"},
}
FAMS = ["camels", "bdg2", "solar", "eolica", "carga", "fx_ret", "fx_abs", "fx_niv"]


def _pseudo(T):
    k = lambda s: f'<span class="kw">{s}</span>'
    c = lambda s: f'<span class="cm"># {s}</span>'
    return f"""{k(T("CONSTANTES", "CONSTANTS"))}   M_MAX = 5   BANDS = [0], [1], [2–3], [4–7], [8–15]   λ_RLS = 0.999   δ_RLS = 100   EVERY = 8
              CLIP_K = 2   N_MIN = 100   T_MAX = 5000   LAM = 0.99   ε_gate = 0.002   α_gate = 0.01

{k(T("PASSO", "STEP"))}(x_t, y_{{t−1}}):
  L ← v052.predict(x_t)                                  {c(T("a base congelada, inalterada", "the frozen base, unchanged"))}
  {c(T("M1: especialista de precisão", "M1: precision expert"))}
  z ← [1, ỹ_(t−1), ỹ_(t−2), {T("médias padronizadas das BANDS das m = mín(d, 5) entradas escolhidas", "standardised BAND means of the m = min(d, 5) chosen inputs")}]
  E ← clip(w·z, L ± CLIP_K·max(σ̂<sub>L</sub>, {T("piso", "floor")}))      {k(T("se", "if"))} RLS {T("determinada", "determined")} ({T("k atualizações", "k updates")})
  L' ← L {k(T("se", "if"))} AdaHedge.n < N_MIN {T("senão", "else")} w_L·L + w_E·E      {c(T("sombra na entrada", "shadow entry"))}
  {c(T("M2: ponto de partida na referência trivial", "M2: start from the trivial reference"))}
  R ← 0 | y_last | y_(t−s)                               {c(T("zero, persistência ou sazonal ingênuo", "zero, persistence or seasonal naive"))}
  D ← w_D·[R, L'];   M ← w_M·[R, L'];   s ← η·w_A / (η·w_A + w_B/2)
  ŷ ← L' {k(T("se", "if"))} R {T("indefinida", "undefined")} {T("senão", "else")} s·M + (1 − s)·D
  {k(T("retorna", "return"))} ŷ

{k(T("OBSERVAR", "OBSERVE"))}(y_t):
  v052.observe(y_t);  {T("triagem a cada EVERY; RLS a cada EVERY alvos; nova seleção depois de N_MIN e a cada T_MAX", "screening every EVERY; RLS every EVERY targets; new selection after N_MIN and every T_MAX")}
  AdaHedge.update((y_t − L)², (y_t − E)²)                 {c(T("erro quadrático sem recorte", "squared error, no clipping"))}
  AdaHedge_D.update((y_t − R)², (y_t − L')²)
  Switch_M.update((y_t − R)²/2σ², (y_t − L')²/2σ²)           {c(T("σ² recente; reserva em escala log contra 0/0", "recent σ²; log-scale fallback against 0/0"))}
  N ← max((y_t − D)², (y_t − M)², LAM·N);  Prod.update((y_t − D)²/N, (y_t − M)²/N)"""


def sections(lang, N, Dg, G):
    P = lang == "pt"
    T = lambda pt, en: pt if P else en
    F = N["final"]; fam = F["fam"]; f6 = N["f6"]; dev = N["dev"]; val = N["val"]; sh = N["shocks"]
    FN = FAM[lang]

    def n(x, d=3):
        s = f"{x:,.{d}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".") if P else s

    def ci(a):
        return "-" if not a else f"{n(a['geo'])} [{n(a['ic95'][0])}; {n(a['ic95'][1])}]"

    def tbl(head, rows, cls="compact"):
        h = "".join(f"<th>{c}</th>" for c in head)
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<table class="no-break {cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'

    def fig(s, cap):
        return f'<div class="diagram-container no-break">{s}<div class="diagram-caption">{cap}</div></div>'

    ov = F["overall"]; inc_all = F["inc_all"]
    import numpy as np
    inc_med, inc_max = float(np.median(inc_all)), float(max(inc_all))
    toc = [T("Sumário executivo", "Executive summary"), T("Ponto de partida: a v0.52 e dois modos de falha", "Starting point: v0.52 and two failure modes"),
           T("Visão geral da arquitetura", "Architecture overview"), T("M1: especialista de precisão", "M1: precision expert"),
           T("M2: ponto de partida na referência trivial", "M2: starting from the trivial reference"), T("Custo computacional", "Computational cost"),
           T("Metodologia de avaliação", "Evaluation methodology"), T("Desenvolvimento: desenhos e falhas", "Development: designs and failures"),
           T("Validações em dados novos", "Validations on new data"), T("Avaliação final pré-registrada", "Pre-registered final evaluation"),
           T("Limites e afirmações que não fazemos", "Limits and claims we do not make"), T("Posição na literatura", "Position in the literature"),
           T("Parâmetros", "Parameters"), T("Pseudocódigo e reprodutibilidade", "Pseudocode and reproducibility"),
           T("Referências", "References"), T("Histórico de revisões", "Revision history")]
    tl = "".join(f'<li class="toc-item"><span class="toc-title">{i + 1}. {t}</span><span class="toc-page">§{i + 1}</span></li>' for i, t in enumerate(toc))
    out = [f"""<div class="page-break"></div><h1>{T("Sumário", "Contents")}</h1><ul class="toc-list">{tl}</ul>"""]

    # ------------------------------------------------------------ 1
    gains = ", ".join(f"{FN[k]} {n(fam[k]['ratio'])}" for k in ("camels", "fx_niv", "fx_ret", "bdg2"))
    out.append(f"""<div class="page-break"></div><h1>1. {toc[0]}</h1>
<p>{T("A <strong>LEBRE v0.53</strong> é a v0.52 <strong>inalterada</strong> com dois componentes novos por cima. A <strong>M1</strong> combina a previsão da v0.52 com um especialista de precisão (uma regressão recursiva sobre o passado do alvo e médias de defasagem das entradas), para os casos em que a v0.52 fica abaixo da fronteira precisão × custo. A <strong>M2</strong> faz a previsão partir de uma referência trivial declarada (zero, persistência ou sazonal ingênuo) e só confiar na parte adaptativa quando ela se mostra melhor, para os casos em que a v0.52 perde para essa referência.",
"<strong>LEBRE v0.53</strong> is the <strong>unchanged</strong> v0.52 with two new components on top. <strong>M1</strong> combines the v0.52 forecast with a precision expert (a recursive regression on the target's past and on lag-band means of the inputs), for the cases where v0.52 lies below the accuracy × cost frontier. <strong>M2</strong> makes the forecast start from a declared trivial reference (zero, persistence or seasonal naive) and trust the adaptive part only when it proves better, for the cases where v0.52 loses to that reference.")}</p>
<div class="alert alert-info"><strong>{T("Resultado da avaliação final pré-registrada", "Result of the pre-registered final evaluation")}</strong> ({F['n']} {T("séries reservadas antes de qualquer código da v0.53", "series reserved before any v0.53 code")}):
<ul style="margin-top:4px">
<li>{T("<strong>promovida</strong> pela regra fixada antes: nenhuma piora em nenhuma família e melhora clara no conjunto;", "<strong>promoted</strong> by the rule fixed beforehand: no harm in any family and a clear overall improvement;")}</li>
<li>{T("erro quadrático médio v0.53 ÷ v0.52 de", "mean squared error v0.53 ÷ v0.52 of")} <strong>{n(ov['geo'])}</strong> [IC 95% {n(ov['ic95'][0])}; {n(ov['ic95'][1])}] {T("nas", "over the")} {ov['n']} {T("séries", "series")};</li>
<li>{T("o ganho vem de", "the gain comes from")} {gains}; {T("em solar, eólica e carga a v0.53 é idêntica à v0.52;", "in solar, wind and load v0.53 is identical to v0.52;")}</li>
<li>{T("custo: acréscimo mediano de", "cost: median increment of")} {n(inc_med, 0)} {T("operações por passo sobre a v0.52 (máximo", "operations per step over v0.52 (maximum")} {n(inc_max, 0)}{T("; limite pré-registrado de 1.100); memória estimada de", "; pre-registered limit 1,100); estimated memory")} {n(F['ram'] / 1024, 1)} KB.</li></ul></div>
<div class="alert alert-warning"><strong>{T("Premissa", "Premise")}:</strong> {T("como na v0.52, a LEBRE não pretende ser o previsor mais preciso; pretende entregar bem sob orçamento mínimo e sem falhas graves. A v0.53 custa mais que a v0.52 em todas as séries e só ganha em parte dos domínios; esse é o principal limite desta versão (§11).", "as in v0.52, LEBRE does not aim to be the most accurate forecaster; it aims to deliver well under a minimal budget and without severe failures. v0.53 costs more than v0.52 on every series and only gains in part of the domains; that is the main limit of this version (§11).")}</div>""")

    # ------------------------------------------------------------ 2
    e14 = f6["e14"]
    rows14 = [(k, n(v["v052"]), n(v["best_same_cost"]), n(v["cost"], 0), T("<strong>abaixo</strong>", "<strong>below</strong>") if v["below"] else T("na fronteira", "on the frontier"))
              for k, v in sorted(e14.items(), key=lambda kv: -kv[1]["v052"] / kv[1]["best_same_cost"])]
    f8 = [(FN[k], fam[k]["classes"]["referência melhor"], fam[k]["n"]) for k in ("fx_ret", "fx_niv")]
    out.append(f"""<div class="page-break"></div><h1>2. {toc[1]}</h1>
<p>{T("A v0.52 (especificação, revisão 1) é um previsor online com um modelo vivo simples (memória do próprio alvo, regressão nas entradas e média dinâmica dos dois) e um plano de mudanças de estrutura testadas por e-process. Ela foi congelada sem promoção em 27/09/2026. O LEBRE Lab, banco de testes público, levantou falhas da v0.52 em domínios novos; a v0.53 trata duas delas, sem ampliar o espaço de hipóteses (as demais ficaram para a v0.54).",
"v0.52 (specification, revision 1) is an online forecaster with a simple live model (memory of the target itself, regression on the inputs and dynamic averaging of the two) and a plane of structural changes tested by e-processes. It was frozen without promotion on 2026-09-27. The LEBRE Lab, a public test bench, surfaced failures of v0.52 in new domains; v0.53 addresses two of them without widening the hypothesis space (the others were left for v0.54).")}</p>
<h2>{T("F8: perder para a referência trivial", "F8: losing to the trivial reference")}</h2>
<p>{T("Em séries quase imprevisíveis (retornos e níveis de câmbio), a parte adaptativa da v0.52 erra mais que prever zero ou repetir o último valor. Na própria reserva final, a referência foi melhor que a v0.52, com intervalo de confiança inteiro acima de 1, em", "In nearly unpredictable series (FX returns and levels), the adaptive part of v0.52 errs more than predicting zero or repeating the last value. In the final reserve itself, the reference beat v0.52, with the whole confidence interval above 1, in")} {f8[0][1]} {T("de", "of")} {f8[0][2]} {T("séries de retornos e", "return series and")} {f8[1][1]} {T("de", "of")} {f8[1][2]} {T("de níveis.", "level series.")}</p>
<h2>{T("F6: abaixo da fronteira precisão × custo", "F6: below the accuracy × cost frontier")}</h2>
<p>{T("Em 8 famílias do desenvolvimento um comparador linear completo (todas as entradas e defasagens estimadas juntas, de alguns milhares a dezenas de milhares de operações por passo) vence a v0.52 por mais de 5%. O que importa sob orçamento é se a v0.52 perde para algo <em>do mesmo custo</em>. O diagnóstico mediu 8 regressões de custos variados em cada família: a v0.52 está abaixo da fronteira (uma regressão de custo menor ou igual erra 5% menos) em 4 delas, todas com a mesma causa, a falta de estimação conjunta da dinâmica do alvo e do efeito das entradas.",
"In 8 development families a full linear comparator (all inputs and lags estimated jointly, from a few thousand to tens of thousands of operations per step) beats v0.52 by more than 5%. What matters under a budget is whether v0.52 loses to something <em>of the same cost</em>. The diagnostic measured 8 regressions of varied cost in each family: v0.52 is below the frontier (a regression of equal or lower cost errs 5% less) in 4 of them, all with the same cause, the lack of joint estimation of the target dynamics and of the input effect.")}</p>
{tbl([T("Família", "Family"), T("v0.52 ÷ completo", "v0.52 ÷ full"), T("melhor com custo ≤ v0.52", "best with cost ≤ v0.52"), T("custo v0.52 (FP)", "v0.52 cost (FP)"), T("situação", "status")], rows14)}
<p class="small">{T("Erro = MSE ÷ MSE do comparador linear online completo (média geométrica da família). B03: qualidade do ar; B07, VB07, XB07: maré meteorológica (três conjuntos independentes); VC05: inflação; YB03: qualidade do ar de Pequim; YB06: eólica; A05: sintético.",
"Error = MSE ÷ MSE of the full online linear comparator (family geometric mean). B03: air quality; B07, VB07, XB07: storm surge (three independent sets); VC05: inflation; YB03: Beijing air quality; YB06: wind; A05: synthetic.")}</p>""")

    # ------------------------------------------------------------ 3
    out.append(f"""<div class="page-break"></div><h1>3. {toc[2]}</h1>
{fig(Dg['arch'], T("A v0.52 roda como antes e é a única dona das mudanças de estrutura; a v0.53 só muda como a previsão final é formada.", "v0.52 runs as before and is the only owner of structural changes; v0.53 only changes how the final forecast is formed."))}
<ul>
<li>{T("<strong>Nada da v0.52 muda.</strong> Os quatro arquivos da base são cópias byte a byte de <code>lebre==0.1.0</code>; a estrutura que a v0.52 aceita dentro da v0.53 é a mesma de quando ela roda sozinha (verificado em todas as séries avaliadas).", "<strong>Nothing in v0.52 changes.</strong> The four base files are byte-for-byte copies of <code>lebre==0.1.0</code>; the structure v0.52 accepts inside v0.53 is the same as when it runs alone (verified on every evaluated series).")}</li>
<li>{T("<strong>M1</strong> produz L' a partir de L e do especialista E. Onde E não ajuda, o peso dele vai a zero e L' = L.", "<strong>M1</strong> produces L' from L and the expert E. Where E does not help, its weight goes to zero and L' = L.")}</li>
<li>{T("<strong>M2</strong> mistura R e L' por dois caminhos (D, conservador; M, que troca de R para L' uma vez) e combina os dois por um (A,B)-Prod, que garante não ficar muito atrás de D.", "<strong>M2</strong> mixes R and L' through two paths (D, conservative; M, which switches from R to L' once) and combines both with an (A,B)-Prod, which guarantees not falling far behind D.")}</li>
<li>{T("Todo o custo novo é fixo por passo, dado o número de entradas; nada cresce com o tempo.", "All new cost is fixed per step, given the number of inputs; nothing grows with time.")}</li></ul>""")

    # ------------------------------------------------------------ 4
    out.append(f"""<div class="page-break"></div><h1>4. {toc[3]}</h1>
<h2>{T("O especialista", "The expert")}</h2>
<p>{T("Variáveis: o próprio alvo nas defasagens 1 e 2 e, para cada uma das m = mín(d, 5) entradas de maior correlação absoluta com o alvo, as médias padronizadas nas bandas de defasagem [0], [1], [2–3], [4–7] e [8–15]:", "Variables: the target itself at lags 1 and 2 and, for each of the m = min(d, 5) inputs with the largest absolute correlation with the target, the standardised means over the lag bands [0], [1], [2–3], [4–7] and [8–15]:")}</p>
<div class="math-box">$$z_t = \\big[1,\\ \\tilde y_{{t-1}},\\ \\tilde y_{{t-2}},\\ \\bar x_{{i,b}}(t)\\big]_{{i \\le m,\\ b \\le 5}}, \\qquad k = 3 + 5m, \\qquad E_t = w_t^\\top z_t$$</div>
<p>{T("Os pesos vêm de mínimos quadrados recursivos com esquecimento λ = 0,999 e P₀ = 100·I, atualizados a cada 8 alvos observados. A escolha das entradas usa médias exponenciais (só passado), é feita depois de 100 alvos e refeita a cada 5.000; se o conjunto muda, a regressão e a combinação recomeçam. A previsão é recortada em L ± 2·máx(σ̂<sub>L</sub>, piso), σ̂<sub>L</sub> o erro recente da v0.52, o que limita o estrago de uma regressão mal condicionada.",
"Weights come from recursive least squares with forgetting λ = 0.999 and P₀ = 100·I, updated every 8 observed targets. Input selection uses exponential means (past only), is made after 100 targets and redone every 5,000; if the set changes, the regression and the combination restart. The forecast is clipped to L ± 2·max(σ̂<sub>L</sub>, floor), σ̂<sub>L</sub> being the recent v0.52 error, which bounds the damage of an ill-conditioned regression.")}</p>
<h2>{T("A combinação com a v0.52", "The combination with v0.52")}</h2>
<p>{T("AdaHedge (de Rooij et al., 2014) com dois especialistas, v0.52 e E, sobre o <strong>erro quadrático sem recorte nem normalização</strong>: os pesos seguem o erro quadrático acumulado, que é o que o MSE mede, e a taxa de aprendizado se ajusta sozinha à escala. Entrada em sombra: até 100 atualizações, L' = L.", "AdaHedge (de Rooij et al., 2014) with two experts, v0.52 and E, on the <strong>squared error without clipping or normalisation</strong>: the weights follow the accumulated squared error, which is what the MSE measures, and the learning rate adapts to the scale by itself. Shadow entry: until 100 updates, L' = L.")}</p>
<div class="math-box">$$L'_t = (1 - \\omega_t)\\,L_t + \\omega_t\\,E_t, \\qquad \\omega_t = \\frac{{e^{{-\\eta_t S^E_{{t-1}}}}}}{{e^{{-\\eta_t S^L_{{t-1}}}} + e^{{-\\eta_t S^E_{{t-1}}}}}}, \\qquad S^\\bullet_{{t-1}} = \\sum_{{\\tau \\lt t}} (y_\\tau - \\bullet_\\tau)^2$$</div>
<p>{T("<strong>Por que não um (A,B)-Prod, como na M2:</strong> o Prod exige perdas em [0, 1]. Três formas de pôr o erro quadrático nesse intervalo foram medidas e falharam por razões diferentes (§8): recortar em 2σ deixa o Prod cego aos erros grandes; dividir pelo maior erro já visto o congela depois de um recorde; dividir pelo maior erro recente dá peso pequeno aos passos de erro grande, justamente onde o especialista ganha. Trocar a garantia constante do Prod pela do AdaHedge (arrependimento que, relativo ao MSE total, some com o tamanho da série) foi o que funcionou.",
"<strong>Why not an (A,B)-Prod, as in M2:</strong> Prod needs losses in [0, 1]. Three ways of putting the squared error into that interval were measured and failed for different reasons (§8): clipping at 2σ leaves Prod blind to large errors; dividing by the largest error ever seen freezes it after a record; dividing by the largest recent error gives small weight to the large-error steps, exactly where the expert gains. Trading Prod's constant guarantee for AdaHedge's (a regret that, relative to the total MSE, vanishes with series length) is what worked.")}</p>""")

    # ------------------------------------------------------------ 5
    top = sh["top"]
    out.append(f"""<div class="page-break"></div><h1>5. {toc[4]}</h1>
<p>{T("A referência R é declarada com os dados: zero para retornos financeiros, sazonal ingênuo quando há ciclo, persistência nos demais casos. Enquanto R não está definida (antes de um ciclo completo), a saída é L'.", "The reference R is declared with the data: zero for financial returns, seasonal naive when there is a cycle, persistence otherwise. While R is undefined (before a full cycle), the output is L'.")}</p>
<ul>
<li>{T("<strong>D</strong> — AdaHedge entre R e L' sobre o erro quadrático (só nos passos com R definida): confiança, sem trocas.", "<strong>D</strong> — AdaHedge between R and L' on the squared error (only on steps with R defined): confidence, no switches.")}</li>
<li>{T("<strong>M</strong> — troca num só sentido (switch distribution, van Erven et al., 2012): posterior sobre “sempre R”, “sempre L'” e “R até um instante, L' depois”, com risco de troca 1/t, sobre perdas gaussianas na escala recente; um caminho em escala logarítmica evita 0/0 quando toda a massa está de um lado.", "<strong>M</strong> — one-way switch (switch distribution, van Erven et al., 2012): posterior over “always R”, “always L'” and “R until some time, L' after”, with switch hazard 1/t, on Gaussian losses at the recent scale; a log-scale path avoids 0/0 when all the mass is on one side.")}</li>
<li>{T("<strong>Combinação</strong> — (A,B)-Prod anytime (Sani et al., 2014) com B = D (confiança) e A = M (oportunista); perdas (y − ·)²/N(t), com N(t) = máx(perdas do passo, 0,99·N(t−1)).", "<strong>Combination</strong> — anytime (A,B)-Prod (Sani et al., 2014) with B = D (confidence) and A = M (opportunist); losses (y − ·)²/N(t), with N(t) = max(step losses, 0.99·N(t−1)).")}</li></ul>
<div class="math-box">$$\\hat y_t = s_t\\,M_t + (1 - s_t)\\,D_t, \\qquad s_t = \\frac{{\\eta_t w^A_t}}{{\\eta_t w^A_t + w^B/2}}, \\qquad \\eta_t = \\min\\Big(\\tfrac12,\\ \\sqrt{{1/(1 + \\textstyle\\sum_{{\\tau \\lt t}} \\delta_\\tau^2)}}\\Big)$$</div>
<h2>{T("Garantias e o limite dos choques", "Guarantees and the limit of shocks")}</h2>
<p>{T("Para as perdas normalizadas, o Prod garante arrependimento constante contra D e da ordem de √(T log log T) contra M; na escala original não há limite formal limpo, porque a normalização muda com o tempo. Há um limite que nenhum combinador online contorna: as garantias para perdas sem limite valem em unidades da maior perda de um passo, e em séries financeiras um único dia pode responder por boa parte de todo o erro (nas", "For the normalised losses, Prod guarantees constant regret against D and of order √(T log log T) against M; in the original scale there is no clean formal bound, because the normalisation changes over time. There is a limit no online combiner escapes: guarantees for unbounded losses hold in units of the largest single-step loss, and in financial series one day can account for much of the whole error (in the")} {sh['n']} {T("séries medidas,", "measured series,")} {sh['over5']} {T("têm o maior passo acima de 5% do erro total da referência; o maior,", "have the largest step above 5% of the reference's total error; the largest,")} {top[0][1]}, {n(100 * top[0][2], 1)}%). {T("Por isso a régua de avaliação trata essas séries como indecidíveis (§7).", "That is why the evaluation ruler treats those series as undecidable (§7).")}</p>""")

    # ------------------------------------------------------------ 6
    bd = dev["breakdown"]
    G_cost = G["cost_gain"]
    out.append(f"""<div class="page-break"></div><h1>6. {toc[5]}</h1>
<p>{T("Contagem pela regra da v0.52 (uma operação elementar = 1 FP), auditada: a implementação faz exatamente as contas declaradas (cada par da matriz da RLS simetrizado uma vez; só a linha nova das entradas padronizada), com as previsões idênticas às validadas em", "Count by the v0.52 rule (one elementary operation = 1 FP), audited: the implementation performs exactly the declared operations (each pair of the RLS matrix symmetrised once; only the new input row standardised), with forecasts identical to the validated ones in")} {dev['identity'][0]} {T("de", "of")} {dev['identity'][1]} {T("séries; a auditoria elevou a contagem em", "series; the audit raised the count by")} {n(100 * (dev['audit_median'] - 1), 1)}% ({T("mediana", "median")}).</p>
{tbl([T("Parte", "Part"), T("FP por passo (mediana, uma série por família, antes da auditoria)", "FP per step (median, one series per family, before the audit)")],
     [("v0.52", n(bd['v052'], 0)), ("M2", n(bd['m2'], 0)), (T("M1: atualização da RLS", "M1: RLS update"), n(bd['m1_rls'], 0)), (T("M1: resto", "M1: rest"), n(bd['m1_rest'], 0)), ("<strong>Total</strong>", f"<strong>{n(bd['total'], 0)}</strong>")])}
<p>{T("RLS: 6k² + 5k por atualização (a cada 8 alvos); previsão do especialista: 2k + 18m + 4; AdaHedge: 48; M2: ~132 a 137. No desenvolvimento e na validação 5 (", "RLS: 6k² + 5k per update (every 8 targets); expert prediction: 2k + 18m + 4; AdaHedge: 48; M2: ~132 to 137. In development and validation 5 (")}{dev['identity'][1]} {T("séries), o acréscimo sobre a v0.52 teve mediana de", "series), the increment over v0.52 had a median of")} {n(dev['inc_median'], 0)} {T("e máximo de", "and a maximum of")} {n(dev['inc_max'], 0)} FP; {T("a razão v0.53 ÷ v0.52, mediana de", "the ratio v0.53 ÷ v0.52, a median of")} {n(dev['ratio_median'], 2)} {T("e máximo de", "and a maximum of")} {n(dev['ratio_max'], 2)}.</p>
<p>{T("A meta preliminar da nota de desenho (custo ≤ 1,25 vez o da v0.52) é incompatível com M1 + M2: com a v0.52 em ~450 FP, o acréscimo máximo seria ~110 FP, menos que a M2 sozinha. Antes da avaliação final, o responsável pelo projeto a substituiu por um teto de <strong>acréscimo absoluto de 1.100 FP por passo</strong> em cada série (o custo novo é quase fixo; uma razão pune as séries em que a v0.52 é barata), mais 2,5 vezes nas famílias do tipo F6.",
"The preliminary target of the design note (cost ≤ 1.25 times that of v0.52) is incompatible with M1 + M2: with v0.52 at ~450 FP, the maximum increment would be ~110 FP, less than M2 alone. Before the final evaluation, the project owner replaced it with a ceiling of an <strong>absolute increment of 1,100 FP per step</strong> on every series (the new cost is nearly fixed; a ratio penalises the series where v0.52 is cheap), plus 2.5 times on F6-type families.")}</p>
{fig(G_cost, T("Avaliação final: acréscimo de custo e razão de erro por série. O custo é pago em todas as séries; o ganho aparece em bacias e câmbio.", "Final evaluation: cost increment and error ratio per series. The cost is paid on every series; the gain appears in basins and FX."))}""")

    # ------------------------------------------------------------ 7
    out.append(f"""<div class="page-break"></div><h1>7. {toc[6]}</h1>
<h2>{T("Disciplina", "Discipline")}</h2>
<ul>
<li>{T("Os dados da avaliação final foram reservados em 05/10/2026, antes de qualquer código da v0.53, com hashes e travas nos dois repositórios.", "The final-evaluation data were reserved on 2026-10-05, before any v0.53 code, with hashes and locks in both repositories.")}</li>
<li>{T("Cada medição tem plano e critérios commitados antes; nada é ajustado depois; as falhas ficam declaradas.", "Every measurement has its plan and criteria committed beforehand; nothing is adjusted afterwards; failures stay declared.")}</li>
<li>{T("Cada conjunto de validação é escolhido só por metadados, congelado com SHA-256 e usado uma única vez.", "Each validation set is chosen from metadata only, frozen with SHA-256 and used once.")}</li></ul>
<h2>{T("Régua por decidibilidade", "Decidability ruler")}</h2>
<p>{T("Cada série é classificada pelo IC 95% de v0.52 ÷ R (bootstrap de blocos pareado, 2.000 réplicas): “v0.52 melhor”, “referência melhor” ou “indecidível”. Critérios: (1) nas “referência melhor”, v0.53 ÷ R com limite superior ≤ 1,01; (2) nas “v0.52 melhor”, v0.53 ÷ v0.52 com limite superior ≤ 1,02; (4) nos testes negativos, nenhuma entrada falsa a mais que a v0.52; (6) a estrutura da v0.52 preservada; (7) nas séries curtas (360 passos), ≤ 1,05 do melhor de v0.52 e R. Três adendos, decididos durante o desenvolvimento e antes da validação 5: uma série em que o maior passo isolado passa de máx(5%, 5·2 ln(n)/n) do erro de R fica indecidível nos critérios 1 e 2 (n = passos avaliados).",
"Each series is classified by the 95% CI of v0.52 ÷ R (paired block bootstrap, 2,000 replicates): “v0.52 better”, “reference better” or “undecidable”. Criteria: (1) on “reference better”, v0.53 ÷ R with upper limit ≤ 1.01; (2) on “v0.52 better”, v0.53 ÷ v0.52 with upper limit ≤ 1.02; (4) on negative tests, no more false inputs than v0.52; (6) v0.52's structure preserved; (7) on short series (360 steps), ≤ 1.05 of the best of v0.52 and R. Three addenda, decided during development and before validation 5: a series whose largest single step exceeds max(5%, 5·2 ln(n)/n) of R's error is undecidable on criteria 1 and 2 (n = evaluated steps).")}</p>
<h2>{T("F6 e promoção", "F6 and promotion")}</h2>
<p>{T("F6, nas famílias abaixo da fronteira: custo ≤ 2,5 vezes o da v0.52 e erro ≤ 1,05 vez o menor erro entre as 8 regressões do diagnóstico com custo ≤ o da v0.53. Promoção (pré-registro, decisões do responsável pelo projeto): (A) nenhuma piora por família, (B) v0.53 ÷ v0.52 em todas as séries com limite superior do IC 95% abaixo de 1 e (C) memória estimada ≤ 128 KB.",
"F6, on the families below the frontier: cost ≤ 2.5 times that of v0.52 and error ≤ 1.05 times the lowest error among the diagnostic's 8 regressions with cost ≤ that of v0.53. Promotion (pre-registration, project-owner decisions): (A) no harm per family, (B) v0.53 ÷ v0.52 over all series with the upper limit of the 95% CI below 1 and (C) estimated memory ≤ 128 KB.")}</p>""")

    # ------------------------------------------------------------ 8
    devrows = [(r["name"], n(r["v052"]), n(r["v053"]), n(r["meta"]), n(r["cost_ratio"], 2)) for r in f6["rows"] if r["src"] == "dev"]
    out.append(f"""<div class="page-break"></div><h1>8. {toc[7]}</h1>
{fig(Dg['path'], T("Os desenhos que importaram para a decisão; a lista completa (6 desenhos da M1, 14 configurações da M2) está no LEBRE Lab.", "The designs that mattered for the decision; the full list (6 M1 designs, 14 M2 configurations) is in the LEBRE Lab."))}
<p>{T("O banco de desenvolvimento cresceu até", "The development bench grew to")} {dev['families']} {T("famílias e", "families and")} {dev['series']} {T("séries (desenvolvimento original e as validações 1 a 4, já gastas, mais as famílias curtas). Nele, a combinação final (M1 rascunho 5 + M2 Q2) atendeu a todos os critérios da M2 e a F6 nas quatro famílias abaixo da fronteira:", "series (original development and validations 1 to 4, already spent, plus the short families). On it, the final combination (M1 draft 5 + M2 Q2) met all M2 criteria and F6 on the four families below the frontier:")}</p>
{tbl([T("Família", "Family"), T("v0.52 ÷ completo", "v0.52 ÷ full"), T("v0.53 ÷ completo", "v0.53 ÷ full"), T("meta", "target"), T("custo ÷ v0.52", "cost ÷ v0.52")], devrows)}
<p>{T("Achados de processo, todos registrados: um defeito numérico no componente M (0/0 por underflow) foi achado num teste, corrigido e auditado (nunca disparou em medição registrada; desde então uma previsão não finita conta como falha); um erro de construção nas validações 4 e 5 (ciclo de 30 h em vez de 24 h em solar, eólica e carga) restringiu o alcance da validação 5 (§9).",
"Process findings, all recorded: a numerical defect in component M (0/0 by underflow) was found in a test, fixed and audited (it never fired in a recorded measurement; since then a non-finite forecast counts as a failure); a construction error in validations 4 and 5 (30 h cycle instead of 24 h in solar, wind and load) restricted the scope of validation 5 (§9).")}</p>""")

    # ------------------------------------------------------------ 9
    v5rows = [(r["name"], n(r["v052"]), n(r["v053"]), n(r["meta"]), n(r["cost_ratio"], 2)) for r in f6["rows"] if r["src"] == "val5"]
    v4 = val["v4_fails"]
    out.append(f"""<div class="page-break"></div><h1>9. {toc[8]}</h1>
<p>{T("As validações 1 e 2 serviram a desenhos anteriores da M2; a validação 3 confirmou a candidata P. A <strong>validação 4</strong> reprovou a M1 rascunho 2 com a P: critério 1 em", "Validations 1 and 2 served earlier M2 designs; validation 3 confirmed candidate P. <strong>Validation 4</strong> rejected M1 draft 2 with P: criterion 1 on")} {v4['1']} {T("e critério 2 em", "and criterion 2 on")} {v4['2']}. {T("O diagnóstico separou as causas (a falha da solar era da M1; as do câmbio e da maré, da M2) e levou aos desenhos do §8.", "The diagnostic separated the causes (the solar failure came from M1; the FX and tide ones from M2) and led to the designs of §8.")}</p>
<p>{T("A <strong>validação 5</strong> (", "<strong>Validation 5</strong> (")}{val['v5_series']} {T("séries novas, medição única) confirmou a M1 rascunho 5 com a M2 Q2: F6 atendida em qualidade do ar de Pequim (Chen, 2017) e em seis estações de maré novas, e todos os critérios da M2 em todas as famílias.", "new series, single measurement) confirmed M1 draft 5 with M2 Q2: F6 met on Beijing air quality (Chen, 2017) and on six new tide stations, and all M2 criteria on every family.")}</p>
{tbl([T("Família", "Family"), T("v0.52 ÷ completo", "v0.52 ÷ full"), T("v0.53 ÷ completo", "v0.53 ÷ full"), T("meta", "target"), T("custo ÷ v0.52", "cost ÷ v0.52")], v5rows)}
<div class="alert alert-warning"><strong>Errata:</strong> {T("nas validações 4 e 5, as famílias solar, eólica e carga foram montadas com ciclo de 30 h em vez de 24 h. As comparações entre v0.52 e v0.53 nessas famílias valem para a tarefa como montada, não para a análoga declarada; a evidência fresca da v0.53 com o ciclo certo nesses domínios é a avaliação final (§10).", "in validations 4 and 5, the solar, wind and load families were built with a 30 h cycle instead of 24 h. The v0.52 vs v0.53 comparisons in those families hold for the task as built, not for the declared analogue; the fresh evidence for v0.53 with the right cycle in those domains is the final evaluation (§10).")}</div>""")

    # ------------------------------------------------------------ 10
    frows = []
    for k in FAMS:
        f = fam[k]; c = f["classes"]
        frows.append((FN[k], f["n"], f"{c['v0.52 melhor']}/{c['referência melhor']}/{c['indecidível']}/{c['indecidível (choque)']}",
                      n(f["ratio"]), ci(f["c1"]), ci(f["c2"]), n(f["inc_max"], 0)))
    refrows = [(FN[k], n(fam[k]["chronos53"]), n(fam[k]["chronos52"]),
                n(fam[k].get("sarimax_addendum", fam[k]["sarimax"])) + ("*" if k.startswith("fx") else "")) for k in FAMS]
    reh = F["rehearsal"]
    out.append(f"""<div class="page-break"></div><h1>10. {toc[9]}</h1>
<p>{T("Execução única em", "Single run on")} {F['n']} {T("séries reservadas (30 bacias do CAMELS-BR, Chagas et al., 2020; 30 medidores do BDG2, Miller et al., 2020; 8 usinas solares, 8 eólicas, a carga de 2026 dos 4 subsistemas e 8 pares de câmbio em 3 tarefas). O pré-registro foi aprovado depois de um ensaio em", "reserved series (30 CAMELS-BR basins, Chagas et al., 2020; 30 BDG2 meters, Miller et al., 2020; 8 solar plants, 8 wind plants, the 2026 load of the 4 subsystems and 8 FX pairs in 3 tasks). The pre-registration was approved after a rehearsal on")} {reh['n']} {T("séries já gastas de bacias e prédios (", "already spent basin and building series (")}{reh['errors']} {T("erros).", "errors).")}</p>
{fig(G['fam_ratio'], T("v0.53 ÷ v0.52 por série (pontos) e média geométrica da família (traço).", "v0.53 ÷ v0.52 per series (dots) and family geometric mean (bar)."))}
{tbl([T("Família", "Family"), T("séries", "series"), T("v0.52 melhor / ref. / indec. / choque", "v0.52 better / ref. / undec. / shock"), T("v0.53 ÷ v0.52", "v0.53 ÷ v0.52"), T("crit. 1", "crit. 1"), T("crit. 2", "crit. 2"), T("+custo máx. (FP)", "max +cost (FP)")], frows)}
<ul>
<li>{T("Melhora geral:", "Overall improvement:")} <strong>{ci(ov)}</strong>; {T("séries curtas contra o melhor de v0.52 e R:", "short series against the best of v0.52 and R:")} {ci(F['short'])}.</li>
<li>{T("Nenhuma previsão não finita; entradas falsas nos retornos iguais às da v0.52; estrutura preservada em todas as séries; memória estimada de", "No non-finite forecast; false inputs on returns equal to v0.52's; structure preserved on every series; estimated memory")} {n(F['ram'], 0)} B.</li>
<li>{T("Em solar, eólica e carga, a M1 terminou com peso zero em todas as", "In solar, wind and load, M1 ended with zero weight on all")} {fam['solar']['n'] + fam['eolica']['n'] + fam['carga']['n']} {T("séries e a v0.53 ficou idêntica à v0.52.", "series and v0.53 was identical to v0.52.")}</li>
<li>{T("Duas correções durante a execução, sem efeito em modelo ou critério: a leitura da carga de 2026 pelo código do subsistema (o ONS renomeou o Sudeste) e o tratamento de uma série curta degenerada (empate exato com erro zero).", "Two fixes during the run, with no effect on model or criterion: reading the 2026 load by subsystem code (ONS renamed the Southeast) and handling a degenerate short series (exact tie with zero error).")}</li></ul>
<h2>{T("Tetos de referência (só reportados)", "Reference ceilings (reported only)")}</h2>
<p>{T("Modelos fora da classe de orçamento, só como referência: Chronos-2 com covariáveis (Ansari et al., 2025), modelo de fundação de ~10⁹ operações por previsão, nos 1.000 pontos do protocolo da v0.52; e SARIMAX com entradas.", "Models outside the budget class, as reference only: Chronos-2 with covariates (Ansari et al., 2025), a foundation model of ~10⁹ operations per forecast, on the 1,000 points of the v0.52 protocol; and SARIMAX with inputs.")}</p>
{tbl([T("Família", "Family"), T("v0.53 ÷ Chronos-2 (1.000 pontos)", "v0.53 ÷ Chronos-2 (1,000 points)"), T("v0.52 ÷ Chronos-2", "v0.52 ÷ Chronos-2"), T("SARIMAX-X ÷ v0.53", "SARIMAX-X ÷ v0.53")], refrows)}
<p class="small">{T("* Câmbio: o SARIMAX com entradas não rodou na execução (entradas com feriados faltantes); valores do adendo com as entradas preenchidas pela regra da v0.52, feito depois do resultado.", "* FX: SARIMAX with inputs did not run in the execution (inputs with missing holidays); values from the addendum with inputs filled by the v0.52 rule, made after the result.")}</p>""")

    # ------------------------------------------------------------ 11
    lim = [T("<strong>Custo sem ganho em parte dos domínios:</strong> a v0.53 custa mais em todas as séries; em solar, eólica e carga é idêntica à v0.52.", "<strong>Cost without gain in part of the domains:</strong> v0.53 costs more on every series; in solar, wind and load it is identical to v0.52."),
           T("<strong>F6 sem família na reserva final:</strong> a evidência de F6 em dados novos é só a validação 5; uma família do desenvolvimento passou com margem pequena (VB07).", "<strong>F6 without a family in the final reserve:</strong> the evidence for F6 on new data is validation 5 only; one development family passed by a small margin (VB07)."),
           T("<strong>Régua decidida durante o desenvolvimento:</strong> os adendos do choque foram decididos depois de ver dados de desenvolvimento, antes da validação 5 e da avaliação final.", "<strong>Ruler decided during development:</strong> the shock addenda were decided after seeing development data, before validation 5 and the final evaluation."),
           T("<strong>Sem garantia formal na escala original:</strong> o Prod garante em perdas normalizadas; o AdaHedge da M1 não dá arrependimento constante contra a v0.52.", "<strong>No formal guarantee in the original scale:</strong> Prod guarantees on normalised losses; M1's AdaHedge gives no constant regret against v0.52."),
           T("<strong>Memória estimada, não medida;</strong> sem porte para C nem medição em microcontrolador.", "<strong>Memory estimated, not measured;</strong> no C port nor microcontroller measurement."),
           T("<strong>Incerteza:</strong> o IC do conjunto trata as séries como independentes; a carga tem 4 séries.", "<strong>Uncertainty:</strong> the overall CI treats series as independent; load has 4 series."),
           T("<strong>Erratas</strong> nas validações 4 e 5 e duas correções na execução final, todas declaradas.", "<strong>Errata</strong> in validations 4 and 5 and two fixes in the final run, all declared."),
           T("<strong>Originalidade:</strong> nenhum componente é novo; a contribuição é a integração sob orçamento declarado e a evidência pré-registrada.", "<strong>Originality:</strong> no component is new; the contribution is the integration under a declared budget and the pre-registered evidence."),
           T("<strong>Fora desta versão:</strong> remoções que acontecem, custo proporcional ao uso e ciclo como hipótese (v0.54).", "<strong>Outside this version:</strong> removals that happen, cost proportional to use and cycle as hypothesis (v0.54).")]
    out.append(f"""<div class="page-break"></div><h1>11. {toc[10]}</h1><ul>{''.join(f'<li>{x}</li>' for x in lim)}</ul>""")

    # ------------------------------------------------------------ 12
    out.append(f"""<h1>12. {toc[11]}</h1>
<p>{T("Cada peça tem antecedente direto: AdaHedge e FlipFlop (de Rooij et al., 2014); (A,B)-Prod e o arrependimento constante contra um especialista de confiança (Sani et al., 2014; Even-Dar et al., 2008; Koolen, 2013); switch distribution (van Erven et al., 2012) e Fixed Share (Adamskiy et al., 2016; Cesa-Bianchi et al., 2012); regressão recursiva com defasagens (Ljung, 1999). Os limites de garantia em perdas sem limite e caudas pesadas estão em Cesa-Bianchi et al. (2007), Hazan e Kale (2010), Orabona e Pál (2018), Mhammedi et al. (2019), V'yugin e Trunov (2019), Alquier (2021) e Moulin et al. (2025); sequências de confiança robustas a caudas pesadas, em Wang e Ramdas (2023), ficaram como direção para a M2. A contribuição desta versão é a <strong>integração</strong> desses componentes sob um orçamento declarado e a avaliação pré-registrada.",
"Every part has a direct antecedent: AdaHedge and FlipFlop (de Rooij et al., 2014); (A,B)-Prod and constant regret against a trusted expert (Sani et al., 2014; Even-Dar et al., 2008; Koolen, 2013); switch distribution (van Erven et al., 2012) and Fixed Share (Adamskiy et al., 2016; Cesa-Bianchi et al., 2012); recursive regression with lags (Ljung, 1999). Guarantee limits for unbounded and heavy-tailed losses are in Cesa-Bianchi et al. (2007), Hazan and Kale (2010), Orabona and Pál (2018), Mhammedi et al. (2019), V'yugin and Trunov (2019), Alquier (2021) and Moulin et al. (2025); heavy-tail-robust confidence sequences, in Wang and Ramdas (2023), remained a direction for M2. The contribution of this version is the <strong>integration</strong> of these components under a declared budget and the pre-registered evaluation.")}</p>""")

    # ------------------------------------------------------------ 13
    par = [("M1", T("entradas", "inputs"), "m = mín(d, 5)" if P else "m = min(d, 5)", T("maior correlação absoluta (médias exponenciais, só passado)", "largest absolute correlation (exponential means, past only)")),
           ("M1", T("bandas", "bands"), "[0], [1], [2–3], [4–7], [8–15]", T("médias padronizadas", "standardised means")),
           ("M1", "RLS", "λ = 0,999; δ = 100" if P else "λ = 0.999; δ = 100", T("a cada 8 alvos observados", "every 8 observed targets")),
           ("M1", T("seleção", "selection"), T("após 100; a cada 5.000", "after 100; every 5,000"), T("recomeça regressão e combinação", "restarts regression and combination")),
           ("M1", T("recorte", "clip"), "L ± 2·máx(σ̂<sub>L</sub>, piso)" if P else "L ± 2·max(σ̂<sub>L</sub>, floor)", T("σ̂<sub>L</sub>: erro recente da v0.52", "σ̂<sub>L</sub>: recent v0.52 error")),
           ("M1", T("combinação", "combination"), "AdaHedge", T("erro quadrático; sombra de 100 atualizações", "squared error; 100-update shadow")),
           ("M2", "R", T("zero / sazonal / persistência", "zero / seasonal / persistence"), T("declarada com os dados", "declared with the data")),
           ("M2", "D", "AdaHedge", T("erro quadrático, só com R definida", "squared error, only with R defined")),
           ("M2", "M", T("troca única, risco 1/t", "one-way switch, hazard 1/t"), T("perdas gaussianas na escala recente", "Gaussian losses at the recent scale")),
           ("M2", "Prod", "η ≤ ½; w_B = ½", T("perdas ÷ máx(perdas, 0,99·N)", "losses ÷ max(losses, 0.99·N)")),
           ("M2", T("porta", "gate"), "ε = 0,002; α = 0,01" if P else "ε = 0.002; α = 0.01", T("auditoria das decisões; recriada a cada decisão", "decision audit; recreated after each decision"))]
    out.append(f"""<div class="page-break"></div><h1>13. {toc[12]}</h1>
{tbl([T("Parte", "Part"), T("Parâmetro", "Parameter"), T("Valor", "Value"), T("Observação", "Note")], par)}
<p class="small">{T("Os parâmetros da base v0.52 são os da especificação v0.52, revisão 1, §20. Nada é ajustado por série.", "The parameters of the v0.52 base are those of the v0.52 specification, revision 1, §20. Nothing is tuned per series.")}</p>""")

    # ------------------------------------------------------------ 14
    rep = [T("<strong>Código promovido:</strong> repositório de pesquisa (lebre-research), commit 4a2620e, pasta do protótipo da v0.53; configuração canônica no registro de congelamento da v0.53.", "<strong>Promoted code:</strong> research repository (lebre-research), commit 4a2620e, v0.53 prototype folder; canonical configuration in the v0.53 freeze record."),
           T("<strong>Integridade:</strong> o manifesto SHA-256 da v0.53 cobre 177 arquivos; o verificador de integridade do repositório confere todas as versões congeladas.", "<strong>Integrity:</strong> the v0.53 SHA-256 manifest covers 177 files; the repository integrity verifier checks every frozen version."),
           T("<strong>Avaliação final:</strong> pasta da avaliação final da v0.53 no repositório de pesquisa (pré-registro, scripts, notas da execução, resultados).", "<strong>Final evaluation:</strong> the v0.53 final-evaluation folder of the research repository (pre-registration, scripts, run notes, results)."),
           T("<strong>Desenvolvimento e validações:</strong> LEBRE Lab, github.com/Iquitim/lebre-lab (planos antes de cada medição, resultados, diagnósticos, erratas); este documento leu os resultados do Lab no commit", "<strong>Development and validations:</strong> LEBRE Lab, github.com/Iquitim/lebre-lab (plans before each measurement, results, diagnostics, errata); this document read the Lab results at commit") + f" {N['lab_commit']}.",
           T("<strong>Ambiente:</strong> Python 3.11, numpy 2.2.5, pandas 2.2.3, statsmodels 0.15.0; Chronos-2 com o pacote chronos 2.3.2.", "<strong>Environment:</strong> Python 3.11, numpy 2.2.5, pandas 2.2.3, statsmodels 0.15.0; Chronos-2 with the chronos 2.3.2 package."),
           T("<strong>Determinismo:</strong> sem números aleatórios no modelo; a mesma sequência de entradas dá a mesma saída.", "<strong>Determinism:</strong> no random numbers in the model; the same input sequence gives the same output.")]
    out.append(f"""<div class="page-break"></div><h1>14. {toc[13]}</h1>
<pre class="pseudo">{_pseudo(T)}</pre>
<ul>{''.join(f'<li>{x}</li>' for x in rep)}</ul>""")

    # ------------------------------------------------------------ 15, 16
    out.append(f"""<h1>15. {toc[14]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>""")
    out.append(f"""<h1>16. {toc[15]}</h1><ul><li>{T("<strong>Revisão 0</strong> (09/10/2026): primeira edição, depois da promoção.", "<strong>Revision 0</strong> (2026-10-09): first edition, after the promotion.")}</li></ul>""")
    if P:
        fix = lambda mm: re.sub(r"(?<=\d)\.(?=\d)", "{,}", mm.group(0))
        out = [re.sub(r"\$\$.*?\$\$", fix, o, flags=re.S) for o in out]
    return out


TEXT = {
    "pt": dict(html_lang="pt-BR", badge="Especificação v0.53 · revisão 0",
               title="LEBRE v0.53 — Especificação e Relatório Técnico",
               subtitle="Consolidação da v0.52: especialista de precisão e ponto de partida na referência trivial, sob orçamento declarado",
               expansion="<strong>LEBRE:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>v0.53:</strong> v0.52 inalterada + M1 (especialista de precisão) + M2 (referência trivial)",
               footer_l="Projeto de Pesquisa Codinome Lebre", footer_r="Outubro de 2026 • Documento v0.53, revisão 0",
               page_header="LEBRE v0.53 — Especificação e Relatório Técnico", page_status="Status: versão de pesquisa promovida · rev. 0",
               page_word='"Página "', page_footer="Projeto de Pesquisa Codinome Lebre • Especificação v0.53"),
    "en": dict(html_lang="en", badge="Specification v0.53 · revision 0",
               title="LEBRE v0.53 — Specification and Technical Report",
               subtitle="Consolidation of v0.52: precision expert and starting point at the trivial reference, under a declared budget",
               expansion="<strong>LEBRE:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>v0.53:</strong> unchanged v0.52 + M1 (precision expert) + M2 (trivial reference)",
               footer_l="Codinome Lebre Research Project", footer_r="October 2026 • Document v0.53, revision 0",
               page_header="LEBRE v0.53 — Specification and Technical Report", page_status="Status: promoted research version · rev. 0",
               page_word='"Page "', page_footer="Codinome Lebre Research Project • Specification v0.53"),
}
for _k in TEXT:
    TEXT[_k].update(v01_header="Especificação da Arquitetura LEBRE v0.1 — Documento de Referência", v01_status="Status: FROZEN_WITH_SCOPE_LIMITS",
                    v01_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1")
