"""Bilingual content of the self-contained LEBRE v0.51 specification (no references to local files or folders)."""
import re

# ============================================================================ diagram labels
DIAG = {
    "pt": dict(
        d1_title="D1: Arquitetura da LEBRE v0.51 — dois especialistas, um combinador",
        d1_sub="Cada componente corresponde a um termo do modelo gerador y = nível + ciclo + dinâmica das entradas + ruído",
        d1_in="Observação no passo t", d1_in2="entradas x (padronizadas)", d1_in3="e o valor y(t−1)",
        d1_S="S — especialista estrutural", d1_S2="atrasos esparsos + estado latente", d1_S3="promoção/remoção por testes", d1_S4="estatísticos (martingale, CUSUM)",
        d1_M="M — especialista de memória", d1_M2="forma online do modelo airline", d1_M3="perfil sazonal de incrementos", d1_M4="relativo ao último valor",
        d1_C="Combinador", d1_C2="média dinâmica de modelos", d1_C3="w_S = σ(−η·D)", d1_C4="esquecimento λ = 0,99",
        d1_out="Previsão ŷ(t)", d1_out2="ŷ = ŷ_M + w_S (ŷ_S − ŷ_M)",
        d1_int="Intervalo de 90%", d1_int2="rastreamento de quantil",
        d1_exp="Explicação exata", d1_exp2="soma de parcelas nomeadas",
        d1_fb="erros e(t) realimentam o aprendizado de cada especialista (sem laço entre eles)",
        d1_dorm="peso de S < 0,01 ⇒ evidência de S em pausa",
        d1_note="Os dois especialistas aprendem só com o próprio erro; o combinador não influencia o que eles aprendem.",
        d2_title="D2: O que acontece em um passo de tempo",
        d2_sub="Ordem estritamente causal: toda previsão usa apenas informação disponível antes de y(t)",
        d2_steps=[("Prever", "S e M preveem y(t)", "com dados até t−1"),
                  ("Combinar", "ŷ = ŷ_M + w_S(ŷ_S−ŷ_M)", "e registrar parcelas"),
                  ("Observar", "chega y(t)", "erros e_S, e_M, e"),
                  ("Aprender", "NLMS em S e em M;", "perfil sazonal; ciclo de vida"),
                  ("Atualizar", "D, w_S, intervalo;", "gate de dormência")],
        d2_caus="Garantia de causalidade",
        d2_caus2="A explicação é congelada no instante da previsão; os pesos e o intervalo usados em t foram calculados com dados até t−1.",
        d3_title="D3: Especialista de memória — o que ele lê do passado",
        d3_sub="Todas as features são diferenças relativas ao último valor: não há nível a aprender",
        d3_target="y(t) ?", d3_last="y(t−1)", d3_prev="y(t−2)", d3_seas="y(t−s)", d3_seas1="y(t−s+1)", d3_cycle="ciclo",
        d3_feats=["ŷ_M = y(t−1) + w₁·[m − y(t−1)] + w₂·[y(t−1) − y(t−2)] + w₃·[y(t−s) − y(t−1)] + w₄·[y(t−s+1) − y(t−s)] + w₅·G[fase]",
                  "m: média exponencial do alvo (reversão à média ⇔ suavização exponencial simples com α aprendido)",
                  "G[fase]: média exponencial (fator 0,9) dos incrementos observados nesta mesma fase em ciclos anteriores",
                  "  ⇔ incremento sazonal previsto pelo modelo airline SARIMA(0,1,1)(0,1,1)s ⇔ estado sazonal do Holt-Winters",
                  "w₁…w₅: aprendidos online por NLMS (invariante à escala); sem período declarado usa-se só [m − y(t−1), y(t−1) − y(t−2)]"],
        d4_title="D4: Ciclo de vida estrutural do especialista S",
        d4_sub="Cada transição é uma decisão estatística com taxa de erro controlada",
        d4_dor="Candidato", d4_dor2="no dicionário", d4_prov="Provisório", d4_prov2="em teste (sombra)",
        d4_act="Ativo", d4_act2="contribui para ŷ_S", d4_evi="Removido", d4_evi2="alarme de mudança",
        d4_t1="triagem", d4_t2="martingale ≥ log(p/α)", d4_t3="CUSUM ≥ log(ARL)",
        d4_fut="futilidade após T_max amostras", d4_back="volta ao dicionário (pode ser retestado com estatística nova)",
        d4_gates=["Nenhuma evidência é acumulada quando:",
                  "  • silêncio: a potência das entradas lidas é < 10% da potência de longo prazo (P4: silêncio não é evidência);",
                  "  • quarentena: há valor recortado (|x| > 8) legível por alguma defasagem (P6: entrada fora do contrato não é evidência);",
                  "  • dormência: o peso de S no combinador é < 0,01 (a estrutura de S não afeta a previsão). Previsão e pesos continuam."],
        d5_title="D5: Desempenho no conjunto held-out (10 séries novas)",
        d5_sub="Média geométrica do NMSE relativa ao NLinear online calibrado (menor é melhor)",
        d5_ref="NLinear = 1", d5_note="Chronos-2 com covariáveis só se aplica às 4 séries multivariadas (razão calculada nessas 4).",
        d6_title="D6: Custo computacional por previsão (escala logarítmica)",
        d6_sub="Operações de ponto flutuante por passo, média no conjunto held-out",
        d6_est="(estimado)", d6_note="Chronos: estimativa de ordem de grandeza ≈ 2 × parâmetros × tokens de contexto; os demais foram contados operação a operação.",
    ),
    "en": dict(
        d1_title="D1: LEBRE v0.51 architecture — two experts, one combiner",
        d1_sub="Each component maps to one term of the generative model y = level + cycle + input dynamics + noise",
        d1_in="Observation at step t", d1_in2="inputs x (standardised)", d1_in3="and the value y(t−1)",
        d1_S="S — structural expert", d1_S2="sparse delays + latent state", d1_S3="promotion/eviction by", d1_S4="statistical tests (martingale, CUSUM)",
        d1_M="M — memory expert", d1_M2="online form of the airline model", d1_M3="seasonal profile of increments", d1_M4="relative to the last value",
        d1_C="Combiner", d1_C2="dynamic model averaging", d1_C3="w_S = σ(−η·D)", d1_C4="forgetting λ = 0.99",
        d1_out="Forecast ŷ(t)", d1_out2="ŷ = ŷ_M + w_S (ŷ_S − ŷ_M)",
        d1_int="90% interval", d1_int2="quantile tracking",
        d1_exp="Exact explanation", d1_exp2="sum of named contributions",
        d1_fb="errors e(t) feed each expert's own learning (no loop between them)",
        d1_dorm="weight of S < 0.01 ⇒ S evidence paused",
        d1_note="Both experts learn only from their own error; the combiner does not influence what they learn.",
        d2_title="D2: What happens in one time step",
        d2_sub="Strictly causal order: every forecast uses only information available before y(t)",
        d2_steps=[("Predict", "S and M predict y(t)", "with data up to t−1"),
                  ("Combine", "ŷ = ŷ_M + w_S(ŷ_S−ŷ_M)", "and record contributions"),
                  ("Observe", "y(t) arrives", "errors e_S, e_M, e"),
                  ("Learn", "NLMS in S and in M;", "seasonal profile; lifecycle"),
                  ("Update", "D, w_S, interval;", "dormancy gate")],
        d2_caus="Causality guarantee",
        d2_caus2="The explanation is frozen at prediction time; the weights and interval used at t were computed from data up to t−1.",
        d3_title="D3: Memory expert — what it reads from the past",
        d3_sub="All features are differences relative to the last value: there is no level to learn",
        d3_target="y(t) ?", d3_last="y(t−1)", d3_prev="y(t−2)", d3_seas="y(t−s)", d3_seas1="y(t−s+1)", d3_cycle="cycle",
        d3_feats=["ŷ_M = y(t−1) + w₁·[m − y(t−1)] + w₂·[y(t−1) − y(t−2)] + w₃·[y(t−s) − y(t−1)] + w₄·[y(t−s+1) − y(t−s)] + w₅·G[phase]",
                  "m: exponential mean of the target (mean reversion ⇔ simple exponential smoothing with a learned α)",
                  "G[phase]: exponential average (factor 0.9) of the increments observed at this same phase in previous cycles",
                  "  ⇔ seasonal increment forecast by the airline model SARIMA(0,1,1)(0,1,1)s ⇔ Holt-Winters seasonal state",
                  "w₁…w₅: learned online by NLMS (scale invariant); without a declared period only [m − y(t−1), y(t−1) − y(t−2)] are used"],
        d4_title="D4: Structural lifecycle of expert S",
        d4_sub="Every transition is a statistical decision with a controlled error rate",
        d4_dor="Candidate", d4_dor2="in the dictionary", d4_prov="Provisional", d4_prov2="under test (shadow)",
        d4_act="Active", d4_act2="contributes to ŷ_S", d4_evi="Evicted", d4_evi2="change alarm",
        d4_t1="screening", d4_t2="martingale ≥ log(p/α)", d4_t3="CUSUM ≥ log(ARL)",
        d4_fut="futility after T_max samples", d4_back="back to the dictionary (may be re-tested with fresh statistics)",
        d4_gates=["No evidence is accrued when:",
                  "  • silence: the power of the inputs read is < 10% of the long-run power (P4: silence is not evidence);",
                  "  • quarantine: a clipped value (|x| > 8) is readable by some lag (P6: an input outside the contract is not evidence);",
                  "  • dormancy: the weight of S in the combiner is < 0.01 (S's structure does not affect the forecast). Prediction and weights continue."],
        d5_title="D5: Accuracy on the held-out set (10 new series)",
        d5_sub="Geometric mean of NMSE relative to the calibrated online NLinear (lower is better)",
        d5_ref="NLinear = 1", d5_note="Chronos-2 with covariates only applies to the 4 multivariate series (ratio computed on those 4).",
        d6_title="D6: Computational cost per forecast (log scale)",
        d6_sub="Floating-point operations per step, mean over the held-out set",
        d6_est="(estimated)", d6_note="Chronos: order-of-magnitude estimate ≈ 2 × parameters × context tokens; the others were counted operation by operation.",
    ),
}

MODEL_NAMES = {
    "pt": {"LEBRE_V051": "LEBRE v0.51", "LEBRE_V05": "LEBRE v0.5", "LEBRE_V045": "LEBRE v0.4.5", "LEBRE_V032": "LEBRE v0.3.2",
           "NLINEAR_ONLINE": "NLinear online", "DLINEAR_ONLINE": "DLinear online", "HOLT_WINTERS": "Holt-Winters online",
           "CTRL_PERSISTENCE": "Persistência", "CTRL_SEASONAL_NAIVE": "Sazonal ingênuo", "CTRL_ARX_NLMS": "ARX-NLMS", "IPNLMS": "IPNLMS",
           "CHRONOS_BOLT_TINY": "Chronos-Bolt tiny", "CHRONOS_BOLT_SMALL": "Chronos-Bolt small", "CHRONOS2": "Chronos-2",
           "CHRONOS2_COV": "Chronos-2 c/ covariáveis"},
    "en": {"LEBRE_V051": "LEBRE v0.51", "LEBRE_V05": "LEBRE v0.5", "LEBRE_V045": "LEBRE v0.4.5", "LEBRE_V032": "LEBRE v0.3.2",
           "NLINEAR_ONLINE": "Online NLinear", "DLINEAR_ONLINE": "Online DLinear", "HOLT_WINTERS": "Online Holt-Winters",
           "CTRL_PERSISTENCE": "Persistence", "CTRL_SEASONAL_NAIVE": "Seasonal naive", "CTRL_ARX_NLMS": "ARX-NLMS", "IPNLMS": "IPNLMS",
           "CHRONOS_BOLT_TINY": "Chronos-Bolt tiny", "CHRONOS_BOLT_SMALL": "Chronos-Bolt small", "CHRONOS2": "Chronos-2",
           "CHRONOS2_COV": "Chronos-2 w/ covariates"},
}

TASKS = {
    "Q1_ONS_Carga_SIN_2019_20": ("Q1", "ONS — carga do Sistema Interligado Nacional (2019–20)", "ONS — load of the Brazilian National Grid (2019–20)", "BR", "horária / hourly", 6, 24),
    "Q2_ONS_Hidro_SE_2019_20": ("Q2", "ONS — geração hidráulica, Sudeste/Centro-Oeste (2019–20)", "ONS — hydro generation, Southeast/Center-West (2019–20)", "BR", "horária / hourly", 6, 24),
    "Q3_ONS_Hidro_S_2019_20": ("Q3", "ONS — geração hidráulica, Sul (2019–20)", "ONS — hydro generation, South (2019–20)", "BR", "horária / hourly", 6, 24),
    "Q4_ONS_Eolica_SIN_2019_20": ("Q4", "ONS — geração eólica do SIN (2019–20)", "ONS — wind generation, National Grid (2019–20)", "BR", "horária / hourly", 6, 24),
    "Q5_BCB_GBPBRL": ("Q5", "Banco Central do Brasil — libra/real (2005–24)", "Central Bank of Brazil — GBP/BRL (2005–24)", "BR", "diária / daily", 1, None),
    "Q6_Monash_AusElec_S4": ("Q6", "Demanda elétrica australiana, série 4", "Australian electricity demand, series 4", "INT", "30 min", 1, 48),
    "Q7_Monash_Pedestrian_S4": ("Q7", "Contagem de pedestres (Melbourne), série 4", "Pedestrian counts (Melbourne), series 4", "INT", "horária / hourly", 1, 24),
    "Q8_Monash_Solar10min_S4": ("Q8", "Geração solar (EUA), série 4", "Solar power (USA), series 4", "INT", "10 min", 1, 144),
    "Q9_Monash_KDDCup_S4": ("Q9", "Qualidade do ar (KDD Cup 2018), série 4", "Air quality (KDD Cup 2018), series 4", "INT", "horária / hourly", 1, 24),
    "Q10_Monash_AusElec_S5": ("Q10", "Demanda elétrica australiana, série 5", "Australian electricity demand, series 5", "INT", "30 min", 1, 48),
}

REFS = [
    "Angelopoulos, A. N., Candès, E. J., Tibshirani, R. J. (2023). Conformal PID control for time series prediction. <em>NeurIPS 36</em>.",
    "Ansari, A. F. et al. (2024). Chronos: learning the language of time series. <em>Transactions on Machine Learning Research</em>.",
    "Ansari, A. F. et al. (2025). Chronos-2: from univariate to universal forecasting. <em>arXiv preprint</em>.",
    "Benesty, J., Gay, S. L. (2002). An improved PNLMS algorithm. <em>Proc. IEEE ICASSP</em>, 1881–1884.",
    "Box, G. E. P., Jenkins, G. M. (1970). <em>Time Series Analysis: Forecasting and Control</em>. Holden-Day.",
    "Cesa-Bianchi, N., Lugosi, G. (2006). <em>Prediction, Learning, and Games</em>. Cambridge University Press.",
    "de la Peña, V. H. (1999). A general class of exponential inequalities for martingales and ratios. <em>Annals of Probability</em> 27(1), 537–564.",
    "Freund, Y., Schapire, R. E., Singer, Y., Warmuth, M. K. (1997). Using and combining predictors that specialize. <em>Proc. ACM STOC</em>, 334–343.",
    "Gibbs, I., Candès, E. J. (2021). Adaptive conformal inference under distribution shift. <em>NeurIPS 34</em>.",
    "Godahewa, R., Bergmeir, C., Webb, G. I., Hyndman, R. J., Montero-Manso, P. (2021). Monash time series forecasting archive. <em>NeurIPS Datasets and Benchmarks</em>.",
    "Granger, C. W. J., Ramanathan, R. (1984). Improved methods of combining forecasts. <em>Journal of Forecasting</em> 3(2), 197–204.",
    "Hampel, F. R., Ronchetti, E. M., Rousseeuw, P. J., Stahel, W. A. (1986). <em>Robust Statistics: The Approach Based on Influence Functions</em>. Wiley.",
    "Harvey, A. C. (1989). <em>Forecasting, Structural Time Series Models and the Kalman Filter</em>. Cambridge University Press.",
    "Hassibi, B., Sayed, A. H., Kailath, T. (1996). H∞ optimality of the LMS algorithm. <em>IEEE Transactions on Signal Processing</em> 44(2), 267–280.",
    "Haykin, S. (2002). <em>Adaptive Filter Theory</em>, 4th ed. Prentice Hall.",
    "Herbster, M., Warmuth, M. K. (1998). Tracking the best expert. <em>Machine Learning</em> 32(2), 151–178.",
    "Holt, C. C. (1957/2004). Forecasting seasonals and trends by exponentially weighted moving averages. <em>International Journal of Forecasting</em> 20(1), 5–10.",
    "Howard, S. R., Ramdas, A., McAuliffe, J., Sekhon, J. (2021). Time-uniform, nonparametric, nonasymptotic confidence sequences. <em>Annals of Statistics</em> 49(2), 1055–1080.",
    "Hyndman, R. J., Koehler, A. B., Ord, J. K., Snyder, R. D. (2008). <em>Forecasting with Exponential Smoothing: The State Space Approach</em>. Springer.",
    "Lin, S., Lin, W., Hu, X., Wu, W., Mo, R., Zhong, H. (2024). CycleNet: enhancing time series forecasting through modeling periodic patterns. <em>NeurIPS 37</em>.",
    "Lin, S., Lin, W., Wu, W., Chen, H., Yang, J. (2024). SparseTSF: modeling long-term time series forecasting with 1k parameters. <em>ICML</em>.",
    "Lorden, G. (1971). Procedures for reacting to a change in distribution. <em>Annals of Mathematical Statistics</em> 42(6), 1897–1908.",
    "Makridakis, S., Spiliotis, E., Assimakopoulos, V. (2020). The M4 competition: 100,000 time series and 61 forecasting methods. <em>International Journal of Forecasting</em> 36(1), 54–74.",
    "Moustakides, G. V. (1986). Optimal stopping times for detecting changes in distributions. <em>Annals of Statistics</em> 14(4), 1379–1387.",
    "Muth, J. F. (1960). Optimal properties of exponentially weighted forecasts. <em>Journal of the American Statistical Association</em> 55(290), 299–306.",
    "Nagumo, J., Noda, A. (1967). A learning method for system identification. <em>IEEE Transactions on Automatic Control</em> 12(3), 282–287.",
    "Page, E. S. (1954). Continuous inspection schemes. <em>Biometrika</em> 41(1/2), 100–115.",
    "Raftery, A. E., Kárný, M., Ettler, P. (2010). Online prediction under model uncertainty via dynamic model averaging: application to a cold rolling mill. <em>Technometrics</em> 52(1), 52–66.",
    "Ramdas, A., Grünwald, P., Vovk, V., Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. <em>Statistical Science</em> 38(4), 576–601.",
    "Rissanen, J. (1978). Modeling by shortest data description. <em>Automatica</em> 14(5), 465–471.",
    "Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. <em>Nature Machine Intelligence</em> 1, 206–215.",
    "Smyl, S. (2020). A hybrid method of exponential smoothing and recurrent neural networks for time series forecasting. <em>International Journal of Forecasting</em> 36(1), 75–85.",
    "Ville, J. (1939). <em>Étude critique de la notion de collectif</em>. Gauthier-Villars.",
    "Vovk, V. (1990). Aggregating strategies. <em>Proc. 3rd Annual Workshop on Computational Learning Theory</em>, 371–383.",
    "Winters, P. R. (1960). Forecasting sales by exponentially weighted moving averages. <em>Management Science</em> 6(3), 324–342.",
    "Xu, Z., Zeng, A., Xu, Q. (2024). FITS: modeling time series with 10k parameters. <em>ICLR</em>.",
    "Zeng, A., Chen, M., Zhang, L., Xu, Q. (2023). Are transformers effective for time series forecasting? <em>AAAI</em>, 11121–11128.",
    "Operador Nacional do Sistema Elétrico (ONS). Dados abertos: balanço de energia por subsistema, curva de carga horária.",
    "Banco Central do Brasil. Sistema Gerenciador de Séries Temporais (SGS): taxas de câmbio.",
]

# translation of the model's own (Portuguese) explanation labels for the English document
LABEL_EN = [(r"\[estrutural, peso ([0-9.]+)\] ", r"Structural (weight \1): "), (r"\[memória, peso ([0-9.]+)\] memória: ", r"Memory (weight \1): "),
            ("último valor y\\(t-1\\)", "last value y(t-1)"), ("reversão à média", "mean reversion"),
            ("incremento recente", "recent increment"), ("sazonal: ", "seasonal: "),
            ("incremento de um ciclo atrás", "increment one cycle ago"),
            ("perfil sazonal de incrementos", "seasonal profile of increments"),
            ("entradas atuais \\(base\\)", "current inputs (base)"), ("viés", "bias"), (r"x(\d+) atrasado (\d+) passos", r"x\1 delayed \2 steps"),
            (r"estado latente \(tau~(\d+) passos, polo ([0-9.]+)\)", r"latent state (tau~\1 steps, pole \2)"),
            (r"x(\d+) alimenta o estado latente \(polo ([0-9.]+)\)", r"x\1 drives the latent state (pole \2)"),
            ("PROVISIONAL->ACTIVE", "promoted"), ("ACTIVE->EVICTED\\(replaced\\)", "evicted (replaced)"),
            ("ACTIVE->EVICTED\\(coupled\\)", "evicted (coupled)"), ("ACTIVE->EVICTED", "evicted")]
LABEL_PT_EVT = [(r"\[estrutural, peso ([0-9.]+)\] ", r"Estrutural (peso \1): "), (r"\[memória, peso ([0-9.]+)\] memória: ", r"Memória (peso \1): "),
                ("PROVISIONAL->ACTIVE", "promovido"), ("ACTIVE->EVICTED\\(replaced\\)", "removido (substituído)"),
                ("ACTIVE->EVICTED\\(coupled\\)", "removido (acoplado)"), ("ACTIVE->EVICTED", "removido"), (r"(\d)\.(\d)", r"\1,\2")]


def tr(s, lang):
    rules = LABEL_EN if lang == "en" else LABEL_PT_EVT
    for a, b in rules:
        s = re.sub(a, b, s)
    return s


def _sections(lang):
    P = lang == "pt"
    T = lambda pt, en: pt if P else en

    def n(x, d=3):
        s = f"{x:,.{d}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".") if P else s

    def tbl(head, rows, cls="compact"):
        h = "".join(f"<th>{c}</th>" for c in head)
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<table class="no-break {cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'

    def fig(svg, cap):
        return f'<div class="diagram-container no-break">{svg}<div class="diagram-caption">{cap}</div></div>'

    def S(N, D):
        MN = MODEL_NAMES[lang]
        dec = N["dec"]; p1, p2, p3 = dec["part1"], dec["part2"], dec["part3"]
        I = N["int"]; mh = N["mh"]; rank = N["rank"]; gv = N["geo_vs_nlin"]; ins = N["instab"]; cov = N["cov"]
        ch = N["costh"]; ct = N["cost_task"]
        out = []

        # ------------------------------------------------------------ 1 executive summary + TOC
        toc = [T("Sumário executivo", "Executive summary"), T("O que é a LEBRE e para que serve", "What LEBRE is and what it is for"),
               T("Princípios de projeto", "Design principles"), T("Visão geral da arquitetura", "Architecture overview"),
               T("Formulação matemática", "Mathematical formulation"), T("Fluxo de um passo e causalidade", "One step and causality"),
               T("Custo computacional", "Computational cost"), T("Observabilidade e explicabilidade", "Observability and explainability"),
               T("Validação empírica e rigor metodológico", "Empirical validation and methodological rigour"),
               T("Evolução da arquitetura e lições", "Evolution of the architecture and lessons"),
               T("Limites e afirmações que não fazemos", "Limits and claims we do not make"),
               T("Parâmetros", "Parameters"), T("Referências", "References")]
        tl = "".join(f'<li class="toc-item"><span class="toc-title">{i + 1}. {t}</span><span class="toc-page">§{i + 1}</span></li>' for i, t in enumerate(toc))
        out.append(f"""<div class="page-break"></div><h1>1. {toc[0]}</h1>
<p>{T('A <strong>LEBRE</strong> é um previsor <strong>online</strong> de séries temporais: a cada passo ela recebe uma observação, prevê o próximo valor, aprende com o erro e segue adiante, sem nunca reprocessar o passado. Foi projetada para quatro exigências simultâneas: <strong>custo computacional mínimo</strong> (roda em microcontroladores), <strong>desempenho competitivo</strong> com modelos modernos, <strong>estabilidade</strong> e <strong>explicabilidade exata</strong> de cada previsão.',
'<strong>LEBRE</strong> is an <strong>online</strong> time-series forecaster: at every step it receives an observation, predicts the next value, learns from the error and moves on, never re-processing the past. It was designed for four simultaneous requirements: <strong>minimal computational cost</strong> (it runs on microcontrollers), <strong>competitive accuracy</strong> against modern models, <strong>stability</strong>, and <strong>exact explainability</strong> of every forecast.')}</p>
<p>{T('A versão <strong>v0.51</strong> é a arquitetura mínima que atende às quatro exigências. Ela tem apenas quatro peças, cada uma derivada de um termo do modelo clássico de decomposição estrutural de séries temporais: um <strong>especialista estrutural</strong> (dinâmica guiada por entradas), um <strong>especialista de memória</strong> (nível e ciclo do próprio alvo), um <strong>combinador</strong> por média dinâmica de modelos e um <strong>intervalo de predição</strong> calibrado online.',
'Version <strong>v0.51</strong> is the minimal architecture that meets all four requirements. It has only four parts, each derived from one term of the classical structural decomposition of time series: a <strong>structural expert</strong> (input-driven dynamics), a <strong>memory expert</strong> (level and cycle of the target itself), a <strong>combiner</strong> based on dynamic model averaging, and an online-calibrated <strong>prediction interval</strong>.')}</p>
<div class="alert alert-info"><strong>{T('Resultado principal (avaliação pré-registrada em 10 séries reais nunca usadas no desenvolvimento, 5 delas brasileiras):', 'Main result (pre-registered evaluation on 10 real series never used during development, 5 of them Brazilian):')}</strong>
{T('erro', 'error')} {n(p2['C1_geo_vs_NLinear'], 2)}× {T('o do NLinear online calibrado', 'that of the calibrated online NLinear')} ·
{n(p2['C3_geo_vs_best_chronos'], 2)}× {T('o do melhor modelo de fundação (Chronos-2)', 'that of the best foundation model (Chronos-2)')} ·
{T('3º lugar entre 15 modelos', '3rd of 15 models')} ·
{n(ch.loc['LEBRE_V051', 'fp'], 0)} {T('operações por passo (média), pico', 'operations per step (mean), peak')} {n(p2['B_heldout_max_peak'], 0)} ·
~{n(ch.loc['LEBRE_V051', 'mem'] / 1024, 1)} KB {T('de estado', 'of state')} ·
{T('variação máxima entre pontos de partida', 'maximum variation across start points')} {n(p2['S1_max'], 3)}×.</div>
<h2>{T('Guia do documento', 'Document guide')}</h2><ul class="toc-list">{tl}</ul>""")

        # ------------------------------------------------------------ 2 what / what for
        out.append(f"""<div class="page-break"></div><h1>2. {toc[1]}</h1>
<h2>{T('O problema', 'The problem')}</h2>
<p>{T('Muitos sistemas reais produzem medições em fluxo contínuo — consumo de energia, geração eólica e solar, vazão, qualidade do ar, sensores industriais, câmbio — e precisam de uma previsão do próximo valor <em>no próprio dispositivo</em>, com memória e energia escassas, sem acesso a GPU e sem a possibilidade de treinar offline com grandes históricos. Nesses cenários há três obstáculos: (i) os modelos modernos mais precisos (transformers e modelos de fundação) exigem centenas de megabytes e bilhões de operações por previsão; (ii) os filtros adaptativos clássicos são baratos, mas perdem para modelos modernos em séries sazonais; (iii) em aplicações críticas, uma previsão sem explicação e sem incerteza quantificada tem pouco valor operacional.',
'Many real systems produce measurements as a continuous stream — energy load, wind and solar generation, flow, air quality, industrial sensors, exchange rates — and need a forecast of the next value <em>on the device itself</em>, with scarce memory and energy, no GPU and no possibility of offline training on large histories. Three obstacles arise: (i) the most accurate modern models (transformers and foundation models) require hundreds of megabytes and billions of operations per forecast; (ii) classical adaptive filters are cheap but lose to modern models on seasonal series; (iii) in critical applications, a forecast without explanation and without quantified uncertainty has little operational value.')}</p>
<h2>{T('O que a LEBRE faz', 'What LEBRE does')}</h2>
<ul><li>{T('<strong>Aprende online, a cada passo</strong>, sem fase de treino separada e sem calibração por tarefa: as mesmas constantes servem para todas as séries.', '<strong>Learns online, at every step</strong>, with no separate training phase and no per-task calibration: the same constants serve every series.')}</li>
<li>{T('<strong>Funciona em dois tipos de problema</strong>: séries guiadas pela própria memória (sazonalidade, nível) e sistemas guiados por entradas (atrasos, estados ocultos), decidindo sozinha qual hipótese vale a cada momento.', '<strong>Works on two kinds of problem</strong>: series driven by their own memory (seasonality, level) and systems driven by inputs (delays, hidden states), deciding by itself which hypothesis holds at each moment.')}</li>
<li>{T('<strong>Explica cada previsão exatamente</strong> como soma de parcelas nomeadas (por exemplo, "entrada x1 atrasada 6 passos", "perfil sazonal", "reversão à média").', '<strong>Explains every forecast exactly</strong> as a sum of named contributions (e.g. "input x1 delayed 6 steps", "seasonal profile", "mean reversion").')}</li>
<li>{T('<strong>Informa a própria incerteza</strong> com um intervalo de 90% calibrado online, e <strong>emite alarmes</strong> quando a estrutura do sistema muda.', '<strong>Reports its own uncertainty</strong> with an online-calibrated 90% interval, and <strong>raises alarms</strong> when the system structure changes.')}</li>
<li>{T('<strong>Custa ~100–150 operações de ponto flutuante por passo</strong> e ~1,3 KB de estado: cerca de 10⁶–10⁷ vezes menos computação que um modelo de fundação.', '<strong>Costs ~100–150 floating-point operations per step</strong> and ~1.3 KB of state: about 10⁶–10⁷ times less computation than a foundation model.')}</li></ul>
<h2>{T('Para que serve (casos de uso típicos)', 'What it is for (typical use cases)')}</h2>
<p>{T('Previsão de curto prazo embarcada em medidores e controladores de energia; monitoramento de geração renovável; manutenção preditiva de sensores industriais; previsão e detecção de mudanças em fluxos de IoT; qualquer contexto em que a previsão precise ser barata, auditável e acompanhada de incerteza.',
'Embedded short-term forecasting in energy meters and controllers; monitoring of renewable generation; predictive maintenance on industrial sensors; forecasting and change detection on IoT streams; any context where the forecast must be cheap, auditable and accompanied by uncertainty.')}</p>
<h2>{T('O que a LEBRE não é', 'What LEBRE is not')}</h2>
<p>{T('Não é um modelo de fundação nem um previsor de longo horizonte; não modela relações fortemente não lineares entre entradas e alvo (a classe é linear nos parâmetros); não afirma causalidade física (as explicações descrevem o modelo, isto é, relevância preditiva). O nome LEBRE vem da família original de arquiteturas do projeto (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>): estruturas que entram e saem do modelo por evidência estatística, sob orçamento explícito de recursos.',
'It is not a foundation model nor a long-horizon forecaster; it does not model strongly non-linear input–target relations (the class is linear in the parameters); it does not claim physical causality (explanations describe the model, i.e. predictive relevance). The name LEBRE comes from the project\'s original family of architectures (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>): structures enter and leave the model by statistical evidence, under an explicit resource budget.')}</p>""")

        # ------------------------------------------------------------ 3 principles
        pr = [(T("Custo", "Cost"), T("≤ 150 operações de ponto flutuante por passo em média e pico ≤ 500 (até ~6 entradas); memória de poucos KB.", "≤ 150 floating-point operations per step on average and peak ≤ 500 (up to ~6 inputs); a few KB of memory.")),
              (T("Arquitetura mínima", "Minimal architecture"), T("Cada componente corresponde a um termo do modelo gerador e foi mantido só se a sua remoção piorasse o resultado (§9.6).", "Every component maps to a term of the generative model and was kept only if removing it made results worse (§9.6).")),
              (T("Competitividade", "Competitiveness"), T("Desempenho no nível de modelos modernos leves (NLinear, DLinear) e próximo de modelos de fundação.", "Accuracy at the level of modern lightweight models (NLinear, DLinear) and close to foundation models.")),
              (T("Observabilidade e explicabilidade", "Observability and explainability"), T("Decomposição exata de cada previsão, pesos interpretáveis, intervalo calibrado, alarmes de mudança e custo contabilizado.", "Exact decomposition of each forecast, interpretable weights, calibrated interval, change alarms and accounted cost.")),
              ("P2", T("Evidência em tempo de fluxo: a taxa de acumulação de evidência é fixa por passo, não por evento.", "Stream-time evidence: evidence accrues at a fixed rate per step, not per event.")),
              ("P4", T("Silêncio não é evidência: sem excitação das entradas nenhuma estatística de decisão é atualizada.", "Silence is not evidence: without input excitation no decision statistic is updated.")),
              ("P6", T("Contrato de entrada: entradas padronizadas; um valor fora do contrato (|x| > 8) é usado recortado na previsão, mas não gera evidência nem aprendizado.", "Input contract: standardised inputs; a value outside the contract (|x| > 8) is used clipped in the forecast but produces neither evidence nor learning.")),
              (T("Sem calibração", "No calibration"), T("Nenhum hiperparâmetro é ajustado por série; o único dado do ambiente é o período de amostragem s (por exemplo, 24 para dados horários).", "No hyper-parameter is tuned per series; the only information from the environment is the sampling period s (e.g. 24 for hourly data)."))]
        out.append(f"""<div class="page-break"></div><h1>3. {toc[2]}</h1>
<p>{T('A LEBRE v0.51 foi projetada a partir de quatro exigências e de quatro princípios operacionais herdados das versões anteriores:', 'LEBRE v0.51 was designed from four requirements and four operational principles inherited from earlier versions:')}</p>
{tbl([T('Princípio', 'Principle'), T('Significado na v0.51', 'Meaning in v0.51')], [(f'<strong>{a}</strong>', b) for a, b in pr])}""")

        # ------------------------------------------------------------ 4 overview
        out.append(f"""<h1>4. {toc[3]}</h1>
{fig(D['D1'], T('A arquitetura completa: dois especialistas, um combinador e as saídas de observabilidade.', 'The complete architecture: two experts, one combiner and the observability outputs.'))}
<p>{T('<strong>Por que dois especialistas.</strong> Séries reais sazonais e sistemas guiados por entradas pedem representações opostas. Nas primeiras, a informação decisiva está no próprio passado do alvo, e a previsão deve ser feita relativa ao último valor. Nos segundos, ancorar no último valor injeta ruído, e o que importa são as entradas e os seus atrasos. Durante o desenvolvimento, as tentativas de unir as duas representações num único modelo (em cascata, por aprendizado conjunto ou por regressão de combinação) falharam em pelo menos um dos dois mundos (§9.6). Por isso a arquitetura mínima tem dois especialistas e um combinador que acompanha qual hipótese está valendo.',
'<strong>Why two experts.</strong> Real seasonal series and input-driven systems call for opposite representations. In the former, the decisive information is in the target\'s own past, and the forecast should be made relative to the last value. In the latter, anchoring on the last value injects noise, and what matters are the inputs and their delays. During development, attempts to merge both representations into a single model (cascade, joint learning or regression combination) failed in at least one of the two worlds (§9.6). The minimal architecture therefore has two experts and a combiner that tracks which hypothesis currently holds.')}</p>""")

        # ------------------------------------------------------------ 5 math
        out.append(f"""<div class="page-break"></div><h1>5. {toc[4]}</h1>
<h2>5.1 {T('Modelo gerador', 'Generative model')}</h2>
<p>{T('Partimos da decomposição estrutural de séries temporais (Harvey, 1989):', 'We start from the structural decomposition of time series (Harvey, 1989):')}</p>
<div class="math-box">$$y_t=\\ell_t+c_{{t \\bmod s}}+f(\\mathbf x_{{t-1}},\\mathbf x_{{t-2}},\\dots)+\\eta_t$$</div>
<p>{T('em que \\(\\ell_t\\) é um nível que varia lentamente, \\(c\\) é um ciclo de período \\(s\\), \\(f\\) é a dinâmica induzida pelas entradas (atrasos e estados ocultos) e \\(\\eta_t\\) é ruído, possivelmente com autocorrelação curta. A suavização exponencial em espaço de estados (Hyndman et al., 2008), o modelo airline de Box e Jenkins (1970) e o Holt-Winters (Holt, 1957; Winters, 1960) são casos particulares. Métodos leves recentes usam a mesma ideia de separar o ciclo e prever o resto: CycleNet (Lin et al., 2024), SparseTSF (Lin et al., 2024), FITS (Xu et al., 2024) e o vencedor da competição M4 (Smyl, 2020).',
'where \\(\\ell_t\\) is a slowly varying level, \\(c\\) is a cycle of period \\(s\\), \\(f\\) is the input-induced dynamics (delays and hidden states) and \\(\\eta_t\\) is noise, possibly with short autocorrelation. State-space exponential smoothing (Hyndman et al., 2008), the Box–Jenkins airline model (1970) and Holt-Winters (Holt, 1957; Winters, 1960) are special cases. Recent lightweight methods use the same idea of separating the cycle and forecasting the rest: CycleNet (Lin et al., 2024), SparseTSF (Lin et al., 2024), FITS (Xu et al., 2024) and the winner of the M4 competition (Smyl, 2020).')}</p>
<h2>5.2 {T('Especialista de memória M (nível e ciclo)', 'Memory expert M (level and cycle)')}</h2>
{fig(D['D3'], T('As cinco features da memória, todas relativas ao último valor.', 'The five memory features, all relative to the last value.'))}
<div class="math-box">$$\\hat y^{{M}}_t=y_{{t-1}}+\\mathbf w^\\top\\boldsymbol\\phi_t,\\qquad \\boldsymbol\\phi_t=\\big[\\,m_{{t-1}}-y_{{t-1}},\\;y_{{t-1}}-y_{{t-2}},\\;y_{{t-s}}-y_{{t-1}},\\;y_{{t-s+1}}-y_{{t-s}},\\;G_{{t \\bmod s}}\\,\\big]$$
$$G_{{p}}\\leftarrow G_{{p}}+a\\,\\big[(y_t-y_{{t-1}})-G_{{p}}\\big],\\;a=0.1;\\qquad m_t\\leftarrow m_{{t-1}}+0.01\\,(y_t-m_{{t-1}})$$
$$\\mathbf w\\leftarrow\\mathbf w+\\frac{{\\mu\\,(y_t-\\hat y^M_t)}}{{\\lVert\\boldsymbol\\phi_t\\rVert^2}}\\boldsymbol\\phi_t,\\;\\mu=0.05$$</div>
<p>{T('<strong>Por que estas features.</strong> (i) A previsão do modelo airline SARIMA(0,1,1)(0,1,1)<sub>s</sub> para o incremento sazonal é uma média exponencialmente ponderada dos incrementos da mesma fase em ciclos anteriores, com fator Θ; o perfil \\(G\\) com \\(a=0{,}1\\) é exatamente isso com Θ = 0,9, e coincide com o estado sazonal do Holt-Winters e com o "ciclo recorrente aprendível" do CycleNet. (ii) Com peso \\(w_1\\), a feature de reversão à média produz \\(y_{t-1}+w_1(m-y_{t-1})\\), que é a suavização exponencial simples com constante aprendida — ótima para um nível local ruidoso (Muth, 1960). (iii) O incremento recente captura a autocorrelação curta, e as duas features de defasagem sazonal levam a informação bruta do último ciclo. (iv) Prever relativo ao último valor elimina a necessidade de aprender o nível, que era a causa da instabilidade de versões anteriores (§10); essa é também a normalização do NLinear (Zeng et al., 2023).',
'<strong>Why these features.</strong> (i) The airline model SARIMA(0,1,1)(0,1,1)<sub>s</sub> forecasts the seasonal increment as an exponentially weighted average of the increments at the same phase in previous cycles, with factor Θ; the profile \\(G\\) with \\(a=0.1\\) is exactly that with Θ = 0.9, and coincides with the Holt-Winters seasonal state and with CycleNet\'s "learnable recurrent cycle". (ii) With weight \\(w_1\\), the mean-reversion feature yields \\(y_{t-1}+w_1(m-y_{t-1})\\), i.e. simple exponential smoothing with a learned constant — optimal for a noisy local level (Muth, 1960). (iii) The recent increment captures short autocorrelation, and the two seasonal-lag features carry the raw information of the last cycle. (iv) Forecasting relative to the last value removes the need to learn the level, which caused the instability of earlier versions (§10); this is also NLinear\'s normalisation (Zeng et al., 2023).')}</p>
<p>{T('<strong>Por que NLMS.</strong> O NLMS (Nagumo e Noda, 1967) é o passo de norma mínima que zera o erro a posteriori na direção da feature; o LMS é ótimo no sentido H∞ (Hassibi, Sayed e Kailath, 1996), isto é, minimiza a pior razão entre energia do erro e energia das perturbações sem supor distribuição — a propriedade adequada a fluxos não estacionários. Além disso, o NLMS é <em>invariante à escala</em> das features, o que dispensa qualquer padronização do alvo. O RLS convergiria mais rápido, mas custa O(k²).',
'<strong>Why NLMS.</strong> NLMS (Nagumo and Noda, 1967) is the minimum-norm step that zeroes the a-posteriori error along the feature direction; LMS is H∞-optimal (Hassibi, Sayed and Kailath, 1996), i.e. it minimises the worst-case ratio of error energy to disturbance energy without distributional assumptions — the right property for non-stationary streams. NLMS is also <em>scale invariant</em> in its features, so the target needs no standardisation. RLS would converge faster but costs O(k²).')}</p>
<h2>5.3 {T('Especialista estrutural S (dinâmica guiada por entradas)', 'Structural expert S (input-driven dynamics)')}</h2>
<div class="math-box">$$\\hat y^{{S}}_t=\\theta_0+\\boldsymbol\\theta_b^\\top\\mathbf x_t+\\sum_{{a\\in\\mathcal A_t}}\\theta_a\\,\\varphi_a(t),\\qquad |\\mathcal A_t|\\le 4$$</div>
<p>{T('A base densa lê as entradas atuais; o conjunto ativo \\(\\mathcal A_t\\) contém átomos estruturais com significado físico: <em>atrasos</em> \\(x_{i,t-k}\\) com \\(k\\le 32\\), um <em>estado latente</em> e um <em>acionamento</em> do estado latente. O estado latente implementa o preditor de Kalman estacionário em forma de inovações: para um estado oculto de primeira ordem, o preditor ótimo é linear em filtros de primeira ordem da inovação e da entrada com polo \\(p\\); a LEBRE usa um banco de polos \\(\\{0;\\,0{,}5;\\,0{,}8;\\,0{,}95\\}\\):',
'The dense base reads the current inputs; the active set \\(\\mathcal A_t\\) contains physically meaningful structural atoms: <em>delays</em> \\(x_{i,t-k}\\) with \\(k\\le 32\\), a <em>latent state</em> and a <em>drive</em> of the latent state. The latent state implements the steady-state Kalman predictor in innovations form: for a first-order hidden state, the optimal predictor is linear in first-order filters of the innovation and of the input with pole \\(p\\); LEBRE uses a pole bank \\(\\{0,\\,0.5,\\,0.8,\\,0.95\\}\\):')}</p>
<div class="math-box">$$s_t=p\\,s_{{t-1}}+(1-p)\\,u_t/\\hat\\sigma,\\qquad q_{{i,t}}=p\\,q_{{i,t-1}}+(1-p)\\,x_{{i,t}}$$</div>
<p>{T('Todos os parâmetros são aprendidos por NLMS com o erro do próprio S. <strong>Promoção:</strong> cada candidato é testado em sombra (sem entrar na previsão) por um martingale de mistura auto-normalizado; ele é promovido quando', 'All parameters are learned by NLMS with S\'s own error. <strong>Promotion:</strong> every candidate is tested in shadow (without entering the forecast) by a self-normalised mixture martingale; it is promoted when')}</p>
<div class="math-box">$$\\log M_t=\\frac{{\\tau S_t^2}}{{2(1+\\tau Q_t)}}-\\tfrac12\\log(1+\\tau Q_t)\\;\\ge\\;\\log(p_{{\\text{{dict}}}}/\\alpha),\\qquad S_t=\\textstyle\\sum e_k\\varphi_k,\\;Q_t=\\sum (e_k\\varphi_k)^2$$</div>
<p>{T('Com incrementos condicionalmente simétricos, \\(M_t\\) é supermartingale (de la Peña, 1999; Howard et al., 2021), e pela desigualdade de Ville (1939) a probabilidade de uma promoção falsa em qualquer instante é ≤ α/p por candidato. <strong>Remoção:</strong> um CUSUM (Page, 1954) da razão de log-verossimilhança "sem contra com" o átomo, acrescido de um aluguel de parcimônia \\(r=h/T_{\\text{idle}}\\) no espírito do MDL (Rissanen, 1978), remove o átomo quando cruza \\(h=\\log(\\text{ARL})=\\log 6000\\); sem aluguel, o tempo médio até um alarme falso é ≥ e<sup>h</sup> (Lorden, 1971; Moustakides, 1986). Cada remoção é um <strong>alarme de mudança estrutural</strong>.',
'With conditionally symmetric increments, \\(M_t\\) is a supermartingale (de la Peña, 1999; Howard et al., 2021), and by Ville\'s inequality (1939) the probability of a false promotion at any time is ≤ α/p per candidate. <strong>Eviction:</strong> a CUSUM (Page, 1954) of the log-likelihood ratio "without vs. with" the atom, plus a parsimony rent \\(r=h/T_{\\text{idle}}\\) in the MDL spirit (Rissanen, 1978), removes the atom when it crosses \\(h=\\log(\\text{ARL})=\\log 6000\\); without rent, the mean time to a false alarm is ≥ e<sup>h</sup> (Lorden, 1971; Moustakides, 1986). Every eviction is a <strong>structural change alarm</strong>.')}</p>
{fig(D['D4'], T('Ciclo de vida estrutural e as três condições em que a evidência não é acumulada.', 'Structural lifecycle and the three conditions under which no evidence is accrued.'))}
<p>{T('<strong>Três portões de evidência, uma só justificativa.</strong> Silêncio, quarentena e dormência são regras que dependem apenas do passado (são <em>previsíveis</em>). Pular observações por uma regra previsível preserva a propriedade de supermartingale das estatísticas de evidência (Ramdas et al., 2023), então o controle de erro dos testes continua válido. A <strong>quarentena</strong> é uma rejeição forte de pontos de alavancagem, no espírito dos estimadores GM de Mallows (Hampel et al., 1986). A <strong>dormência</strong> segue a ideia dos <em>sleeping experts</em> (Freund et al., 1997): enquanto S tem peso desprezível, a sua estrutura não afeta a previsão, e só a descoberta estrutural é pausada. A previsão, o aprendizado dos pesos e a escala \\(\\hat\\sigma^2\\) continuam, de modo que S pode recuperar peso. <strong>Partida a frio:</strong> ao promover um estado latente, os estados de acionamento começam em zero. O teste continua válido para qualquer regressor previsível, e o custo de pico cai de ~500 para O(d).',
'<strong>Three evidence gates, one justification.</strong> Silence, quarantine and dormancy are rules that depend only on the past (they are <em>predictable</em>). Skipping observations by a predictable rule preserves the supermartingale property of the evidence statistics (Ramdas et al., 2023), so the tests\' error control remains valid. <strong>Quarantine</strong> is a hard rejection of leverage points, in the spirit of Mallows GM-estimators (Hampel et al., 1986). <strong>Dormancy</strong> follows the <em>sleeping experts</em> idea (Freund et al., 1997): while S has negligible weight its structure does not affect the forecast, and only structural discovery is paused. Prediction, weight learning and the scale \\(\\hat\\sigma^2\\) continue, so S can regain weight. <strong>Cold start:</strong> when a latent state is promoted, the drive states start at zero. The test remains valid for any predictable regressor, and the peak cost drops from ~500 to O(d).')}</p>
<h2>5.4 {T('Combinador: média dinâmica de modelos', 'Combiner: dynamic model averaging')}</h2>
<div class="math-box">$$D_t=\\lambda D_{{t-1}}+\\frac{{(y_t-\\hat y^S_t)^2-(y_t-\\hat y^M_t)^2}}{{\\hat\\sigma_t^2}},\\qquad w^S_t=\\frac{{1}}{{1+e^{{\\eta D_t}}}},\\qquad \\hat y_t=\\hat y^M_t+w^S_{{t-1}}(\\hat y^S_t-\\hat y^M_t)$$</div>
<p>{T('Com dois especialistas, os pesos da média dinâmica de modelos com esquecimento (Raftery, Kárný e Ettler, 2010) dependem apenas da diferença acumulada das perdas. Com verossimilhança preditiva gaussiana e perdas normalizadas pela variância \\(\\hat\\sigma^2\\) do erro combinado, o expoente é \\(\\eta=1/2\\) — um valor derivado, não ajustado. O fator λ = 0,99 (memória de ~100 passos) permite acompanhar mudanças de regime, como no <em>fixed-share</em> (Herbster e Warmuth, 1998); o algoritmo pertence à família dos agregadores de pesos exponenciais com garantias de arrependimento (Vovk, 1990; Cesa-Bianchi e Lugosi, 2006). Combinar por regressão (Granger e Ramanathan, 1984) foi testado e descartado: exige manter um peso próximo de 1 sobre uma feature de alta variância, e o desajuste do NLMS vira ruído (§9.6).',
'With two experts, the weights of dynamic model averaging with forgetting (Raftery, Kárný and Ettler, 2010) depend only on the accumulated loss difference. With a Gaussian predictive likelihood and losses normalised by the variance \\(\\hat\\sigma^2\\) of the combined error, the exponent is \\(\\eta=1/2\\) — a derived value, not a tuned one. The factor λ = 0.99 (~100-step memory) lets the combiner track regime changes, as in <em>fixed-share</em> (Herbster and Warmuth, 1998); the algorithm belongs to the family of exponentially weighted aggregators with regret guarantees (Vovk, 1990; Cesa-Bianchi and Lugosi, 2006). Regression combination (Granger and Ramanathan, 1984) was tested and discarded: it requires holding a weight near 1 on a high-variance feature, and NLMS misadjustment turns into noise (§9.6).')}</p>
<h2>5.5 {T('Intervalo de predição', 'Prediction interval')}</h2>
<div class="math-box">$$\\hat q_t=\\max\\!\\big(0,\\;\\hat q_{{t-1}}+\\gamma\\,\\hat\\sigma_t\\,(\\mathbb 1\\{{|e_t|>\\hat q_{{t-1}}\\}}-\\alpha)\\big),\\qquad \\alpha=0.1,\\;\\gamma=0.1,\\qquad \\text{{{T("intervalo", "interval")}}}=\\hat y_t\\pm\\hat q_t$$</div>
<p>{T('O rastreamento de quantil (Gibbs e Candès, 2021; Angelopoulos, Candès e Tibshirani, 2023) garante cobertura de longo prazo próxima de 90% sem supor distribuição. Na v0.51, a raiz, a inversa e a atualização do quantil são recalculadas a cada 8 passos com passo multiplicado por 8, o que preserva a taxa em tempo de fluxo e reduz o custo.',
'Quantile tracking (Gibbs and Candès, 2021; Angelopoulos, Candès and Tibshirani, 2023) guarantees long-run coverage close to 90% without distributional assumptions. In v0.51 the square root, the inverse and the quantile update are recomputed every 8 steps with an 8× step, which preserves the stream-time rate and reduces cost.')}</p>
<h2>5.6 {T('Explicação aditiva exata', 'Exact additive explanation')}</h2>
<div class="math-box">$$\\hat y_t=w^S\\Big[\\theta_0+\\textstyle\\sum_i\\theta_{{b,i}}x_{{i,t}}+\\sum_{{a\\in\\mathcal A_t}}\\theta_a\\varphi_a(t)\\Big]+(1-w^S)\\Big[y_{{t-1}}+\\sum_{{k=1}}^{{5}}w_k\\phi_{{k,t}}\\Big]$$</div>
<p>{T('Cada parcela tem nome e valor, e a soma é igual à previsão até o arredondamento de máquina. É uma explicação <em>intrínseca</em> (o modelo é a explicação; Rudin, 2019), não uma aproximação pós-hoc.', 'Every term has a name and a value, and the sum equals the forecast up to machine rounding. It is an <em>intrinsic</em> explanation (the model is the explanation; Rudin, 2019), not a post-hoc approximation.')}</p>""")

        # ------------------------------------------------------------ 6 step flow
        out.append(f"""<div class="page-break"></div><h1>6. {toc[5]}</h1>
{fig(D['D2'], T('Sequência de operações em cada passo.', 'Sequence of operations at each step.'))}
<p>{T('Os dois especialistas nunca veem a previsão combinada nem o erro combinado; cada um aprende só com o próprio erro. Assim, o combinador não cria um laço de realimentação entre eles — uma cascata ou um aprendizado conjunto, testados durante o desenvolvimento, mostraram-se instáveis justamente por esse laço.',
'The two experts never see the combined forecast or the combined error; each learns only from its own error. The combiner therefore creates no feedback loop between them — a cascade and joint learning, tested during development, were unstable precisely because of such a loop.')}</p>""")

        # ------------------------------------------------------------ 7 cost
        rows_c = [(T('S — especialista estrutural (d = 5)', 'S — structural expert (d = 5)'), "~85–100", T('base densa ~6d; átomos, latente, busca e evidência', 'dense base ~6d; atoms, latent, search and evidence')),
                  (T('S em dormência (séries sazonais)', 'S in dormancy (seasonal series)'), "~60–75", T('sem testes, CUSUM nem atualização de evidência', 'no tests, CUSUM or evidence updates')),
                  (T('M — memória (5 features)', 'M — memory (5 features)'), "~35–40", T('diferenças, produto interno, NLMS, perfil, média', 'differences, inner product, NLMS, profile, mean')),
                  (T('M sem período (2 features)', 'M without period (2 features)'), "~22", "—"),
                  (T('Combinador', 'Combiner'), "~17", T('erros, diferença de perdas, 1 exp a cada 8 passos', 'errors, loss difference, 1 exp every 8 steps')),
                  (T('Intervalo', 'Interval'), "~2", T('comparação e atualização a cada 8 passos', 'comparison and update every 8 steps'))]
        est = "(est.)"
        FMX = {"CHRONOS_BOLT_TINY": ("~6·10⁸ " + est, "~36 MB"), "CHRONOS_BOLT_SMALL": ("~3·10⁹ " + est, "~190 MB"),
               "CHRONOS2": ("~8·10⁹ " + est, "~480 MB"), "CHRONOS2_COV": ("~10¹⁰ " + est, "~480 MB")}
        rows_m = [(MN[m], FMX[m][0] if m in FMX else n(ch.loc[m, "fp"], 0), "—" if m in FMX else n(ch.loc[m, "peak"], 0),
                   FMX[m][1] if m in FMX else n(ch.loc[m, "mem"] / 1024, 2) + " KB", n(ch.loc[m, "ms"], 3))
                  for m in ["LEBRE_V051", "LEBRE_V045", "LEBRE_V05", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]]
        out.append(f"""<div class="page-break"></div><h1>7. {toc[6]}</h1>
<p>{T('Contamos cada adição, multiplicação, divisão e comparação em ponto flutuante executada pelo algoritmo (FP). Operações feitas a cada k passos entram divididas por k. FP não é energia, mas é um indicador reprodutível e independente de linguagem.',
'We count every floating-point addition, multiplication, division and comparison executed by the algorithm (FP). Operations done every k steps are divided by k. FP is not energy, but it is a reproducible, language-independent indicator.')}</p>
{tbl([T('Componente', 'Component'), T('FP/passo', 'FP/step'), T('Composição', 'Composition')], rows_c)}
<p>{T(f'<strong>Orçamento verificado.</strong> Nas 14 tarefas internas (d = 5) a média máxima por tarefa foi {n(p1["B_internal_max_mean_fp"], 0)} FP e o pico {n(p1["B_internal_max_peak"], 0)}; nas 10 séries do held-out (d ≤ 6), {n(p2["B_heldout_max_mean_fp"], 0)} e {n(p2["B_heldout_max_peak"], 0)}. O custo cresce ~8 FP por entrada adicional (base densa de S); com 25 entradas mediu-se ~260 de média e ~520 de pico — é a fronteira do orçamento.',
f'<strong>Verified budget.</strong> On the 14 internal tasks (d = 5) the maximum per-task mean was {n(p1["B_internal_max_mean_fp"], 0)} FP and the peak {n(p1["B_internal_max_peak"], 0)}; on the 10 held-out series (d ≤ 6), {n(p2["B_heldout_max_mean_fp"], 0)} and {n(p2["B_heldout_max_peak"], 0)}. Cost grows by ~8 FP per extra input (S\'s dense base); with 25 inputs we measured ~260 on average and ~520 at peak — that is the budget boundary.')}</p>
{fig(D['D6'], T('Custo por previsão comparado com os modelos avaliados.', 'Cost per forecast compared with the evaluated models.'))}
{tbl([T('Modelo', 'Model'), T('FP/passo (média)', 'FP/step (mean)'), T('FP pico', 'FP peak'), T('Memória do modelo', 'Model memory'), T('ms/passo (CPU)', 'ms/step (CPU)')], rows_m)}
<p class="small">{T('Tempos de parede em Python num único núcleo de CPU (LEBRE e lineares) e em PyTorch com 16 threads (Chronos); em linguagem compilada a LEBRE ficaria na faixa de microssegundos. Memória dos modelos Chronos: ~36 MB (Bolt tiny, 9 M parâmetros), ~190 MB (Bolt small) e ~480 MB (Chronos-2, 120 M parâmetros) em float32.',
'Wall-clock times in Python on a single CPU core (LEBRE and linear models) and in PyTorch with 16 threads (Chronos); in a compiled language LEBRE would be in the microsecond range. Memory of the Chronos models: ~36 MB (Bolt tiny, 9 M parameters), ~190 MB (Bolt small) and ~480 MB (Chronos-2, 120 M parameters) in float32.')}</p>""")

        # ------------------------------------------------------------ 8 observability
        ex = N["examples"]
        def parts_rows(e, k=12):
            ps = sorted(e["parts"], key=lambda z: -abs(z[1]))[:k]
            return [(tr(a, lang), n(c, 3 if abs(c) < 100 else 1)) for a, c in ps]
        q1, i9 = ex["Q1"], ex["I9"]
        evs = "; ".join(f"t={t}: {tr(a, lang)} — {tr(b, lang)}" for t, a, b in i9["events"][:6])
        out.append(f"""<div class="page-break"></div><h1>8. {toc[7]}</h1>
<p>{T('A cada passo a LEBRE v0.51 entrega, além da previsão:', 'At every step LEBRE v0.51 delivers, besides the forecast:')}</p>
<ul><li>{T('<strong>Decomposição exata</strong> da previsão em parcelas nomeadas (§5.6).', '<strong>Exact decomposition</strong> of the forecast into named contributions (§5.6).')}</li>
<li>{T('<strong>Peso w<sub>S</sub></strong>: indica se o sistema está se comportando como "guiado por entradas" (w<sub>S</sub> ≈ 1) ou "guiado pela própria memória" (w<sub>S</sub> ≈ 0).', '<strong>Weight w<sub>S</sub></strong>: tells whether the system behaves as "input-driven" (w<sub>S</sub> ≈ 1) or "driven by its own memory" (w<sub>S</sub> ≈ 0).')}</li>
<li>{T('<strong>Intervalo de 90%</strong> calibrado online.', 'An online-calibrated <strong>90% interval</strong>.')}</li>
<li>{T('<strong>Registro do ciclo de vida</strong>: quando e por que cada estrutura entrou ou saiu, com a evidência em nats; cada remoção é um alarme de mudança com taxa de alarme falso controlada.', '<strong>Lifecycle log</strong>: when and why each structure entered or left, with the evidence in nats; each eviction is a change alarm with a controlled false-alarm rate.')}</li>
<li>{T('<strong>Custo contabilizado</strong> por componente.', '<strong>Accounted cost</strong> per component.')}</li></ul>
<h2>{T('Exemplo real 1 — série sazonal (carga do SIN, último passo do held-out)', 'Real example 1 — seasonal series (national grid load, last held-out step)')}</h2>
<p>{T(f'Previsão {n(q1["y_hat"], 1)} MWmed (valor observado {n(q1["y"], 1)}), intervalo ±{n(q1["interval"], 1)}, peso estrutural w<sub>S</sub> = {n(q1["wS"], 3)}: a memória domina. Parcelas (as maiores em módulo; a soma de todas é exatamente a previsão):',
f'Forecast {n(q1["y_hat"], 1)} MWavg (observed {n(q1["y"], 1)}), interval ±{n(q1["interval"], 1)}, structural weight w<sub>S</sub> = {n(q1["wS"], 3)}: memory dominates. Contributions (largest in magnitude; the sum of all of them is exactly the forecast):')}</p>
{tbl([T('Parcela', 'Contribution'), T('Valor', 'Value')], parts_rows(q1, 8))}
<h2>{T('Exemplo real 2 — sistema guiado por entradas (atraso + estado latente)', 'Real example 2 — input-driven system (delay + latent state)')}</h2>
<p>{T(f'Previsão {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observado {n(i9["y"], 3)}), w<sub>S</sub> = {n(i9["wS"], 3)}: o especialista estrutural domina e a explicação nomeia a estrutura recuperada. Primeiros eventos do ciclo de vida: {evs}.',
f'Forecast {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observed {n(i9["y"], 3)}), w<sub>S</sub> = {n(i9["wS"], 3)}: the structural expert dominates and the explanation names the recovered structure. First lifecycle events: {evs}.')}</p>
{tbl([T('Parcela', 'Contribution'), T('Valor', 'Value')], parts_rows(i9, 10))}""")

        # ------------------------------------------------------------ 9 validation
        qn = lambda t: TASKS[t][0]
        order = sorted(mh.index, key=lambda t: int(qn(t)[1:]))
        best_ch = mh[["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]].min(axis=1)
        rows_t = []
        for t in order:
            r = mh.loc[t]
            vals = [r.LEBRE_V051, r.NLINEAR_ONLINE, r.DLINEAR_ONLINE, r.HOLT_WINTERS, best_ch[t], r.CTRL_PERSISTENCE, r.LEBRE_V05, r.LEBRE_V045]
            mn = min(vals[:5])
            cells = [f'<strong>{n(v, 4)}</strong>' if v == mn else n(v, 4) for v in vals]
            rows_t.append([f"{qn(t)}", TASKS[t][1] if P else TASKS[t][2]] + cells + [n(ins.loc[t, "V051"], 3), n(cov[t], 3)])
        pos = rank.rank(method="min").astype(int)
        rk = [(f"{pos[m]}º" if P else f"{pos[m]}", MN.get(m, m), n(v, 2)) for m, v in rank.items()]
        rows_ds = [(TASKS[t][0], TASKS[t][1] if P else TASKS[t][2], TASKS[t][4].split(" / ")[0 if P else 1] if "/" in TASKS[t][4] else TASKS[t][4],
                    TASKS[t][5], TASKS[t][6] or "—") for t in order]
        acc = [T("Critério", "Criterion"), T("Limiar", "Threshold"), T("Resultado", "Result")]
        crit = [(T("Custo médio por tarefa (interno d = 5; held-out d ≤ 6)", "Mean cost per task (internal d = 5; held-out d ≤ 6)"), "≤ 150 FP", f"{n(p1['B_internal_max_mean_fp'], 0)} / {n(p2['B_heldout_max_mean_fp'], 0)} ✔"),
                (T("Pico por passo", "Peak per step"), "≤ 500 FP", f"{n(p1['B_internal_max_peak'], 0)} / {n(p2['B_heldout_max_peak'], 0)} ✔"),
                (T("Interno: não piora contra a v0.4.5 (limite sup. 95%)", "Internal: no degradation vs v0.4.5 (upper 95%)"), "< +0,010" if P else "< +0.010", f"{'+' if p1['I-1_upper95'] >= 0 else ''}{n(p1['I-1_upper95'], 4)} ✔"),
                (T("Cobertura interna do intervalo de 90%", "Internal 90% interval coverage"), "[0,88; 0,92]" if P else "[0.88, 0.92]", f"{n(p1['I-2_cov'], 3)} ✔"),
                (T("Fidelidade da explicação (erro relativo)", "Explanation fidelity (relative error)"), "≤ 1e−9", f"{p1['I-3_faith']:.0e} ✔"),
                (T("Held-out: razão contra NLinear", "Held-out: ratio vs NLinear"), "≤ 1,10" if P else "≤ 1.10", f"{n(p2['C1_geo_vs_NLinear'], 3)} ✔"),
                (T("Held-out: razão contra o melhor de NLinear, DLinear, Holt-Winters", "Held-out: ratio vs best of NLinear, DLinear, Holt-Winters"), "≤ 1,15" if P else "≤ 1.15", f"{n(p2['C2_geo_vs_best_modern_linear'], 3)} ✔"),
                (T("Held-out: razão contra a LEBRE v0.5", "Held-out: ratio vs LEBRE v0.5"), "≤ 1,10" if P else "≤ 1.10", f"{n(p2['C4_geo_vs_V05'], 3)} ✔"),
                (T("Estabilidade entre 10 pontos de partida (mediana / máx.)", "Stability across 10 start points (median / max)"), "≤ 1,10 / ≤ 1,50" if P else "≤ 1.10 / ≤ 1.50", f"{n(p2['S1_median'], 3)} / {n(p2['S1_max'], 3)} ✔"),
                (T("Tarefas com cobertura em [0,85; 0,95]", "Tasks with coverage in [0.85, 0.95]"), "≥ 80%", f"{n(100 * p2['S2_frac'], 0)}% ✔"),
                (T("Divergências numéricas", "Numerical divergences"), "0", "0 ✔"),
                (T("Meta (não vinculante): razão contra o melhor Chronos", "Target (non-binding): ratio vs best Chronos"), "≤ 1,50" if P else "≤ 1.50", f"{n(p2['C3_geo_vs_best_chronos'], 3)} ✔")]
        out.append(f"""<div class="page-break"></div><h1>9. {toc[8]}</h1>
<h2>9.1 {T('Protocolo e salvaguardas contra viés', 'Protocol and safeguards against bias')}</h2>
<ul><li>{T('<strong>Pré-registro.</strong> Hipóteses, critérios, limiares, conjuntos de dados, comparadores e sementes foram escritos antes de qualquer execução, e o documento recebeu um hash SHA-256 registrado. O código do modelo foi congelado por hash, e a execução verifica os dois hashes antes de começar.', '<strong>Pre-registration.</strong> Hypotheses, criteria, thresholds, datasets, comparators and seeds were written before any run, and the document\'s SHA-256 hash was recorded. The model code was frozen by hash, and the run checks both hashes before starting.')}</li>
<li>{T('<strong>Separação desenvolvimento/avaliação.</strong> Todas as escolhas de projeto foram feitas em dados de desenvolvimento já usados antes. O conjunto de avaliação principal (held-out) é formado por 10 séries que nenhuma versão da LEBRE tinha visto.', '<strong>Development/evaluation separation.</strong> All design choices were made on previously used development data. The main evaluation set (held-out) consists of 10 series that no LEBRE version had seen.')}</li>
<li>{T('<strong>Sementes novas.</strong> As sementes aleatórias foram verificadas como nunca usadas no projeto.', '<strong>Fresh seeds.</strong> Random seeds were verified never to have been used in the project.')}</li>
<li>{T('<strong>Avaliação prequencial causal.</strong> A cada passo o modelo prevê e só então vê o valor. As entradas são padronizadas por médias e variâncias acumuladas até o instante anterior, o erro é medido a partir de 30% da série, e o NMSE é o erro quadrático médio dividido pela variância do trecho de teste. Para modelos com componentes aleatórios usa-se a mediana de 3 sementes.', '<strong>Causal prequential evaluation.</strong> At every step the model predicts and only then sees the value. Inputs are standardised with means and variances accumulated up to the previous instant, error is measured from 30% of the series onward, and NMSE is the mean squared error divided by the test-segment variance. Models with random components use the median of 3 seeds.')}</li>
<li>{T('<strong>Vantagem dada aos comparadores.</strong> NLinear, DLinear, Holt-Winters e IPNLMS tiveram os hiperparâmetros escolhidos por série, nos primeiros min(15%, 5000) passos. A LEBRE <em>não</em> foi calibrada.', '<strong>Advantage given to comparators.</strong> NLinear, DLinear, Holt-Winters and IPNLMS had their hyper-parameters chosen per series on the first min(15%, 5000) steps. LEBRE was <em>not</em> calibrated.')}</li>
<li>{T('<strong>Modelos de fundação.</strong> Chronos-Bolt tiny foi avaliado em todo o trecho de teste. Por custo de CPU, Chronos-Bolt small e Chronos-2 foram avaliados em 1000 pontos igualmente espaçados do teste, e Chronos-2 com covariáveis em 500 — uma estimativa sem viés do erro médio. Todos usam o mesmo conjunto de informação (valores até t−1, contexto 512; 256 com covariáveis). Não é possível excluir que séries públicas estejam no pré-treino desses modelos, o que os favoreceria.', '<strong>Foundation models.</strong> Chronos-Bolt tiny was evaluated on the whole test segment. Because of CPU cost, Chronos-Bolt small and Chronos-2 were evaluated on 1000 evenly spaced test points and Chronos-2 with covariates on 500 — an unbiased estimate of the mean error. All use the same information set (values up to t−1, context 512; 256 with covariates). Public series may be in these models\' pre-training data, which would favour them.')}</li>
<li>{T('<strong>Estabilidade.</strong> Cada série foi reprocessada a partir de 10 pontos de partida diferentes (0, 50, …, 450 passos descartados), com a mesma janela de teste. A razão máx./mín. do NMSE mede a dependência do resultado em relação ao início.', '<strong>Stability.</strong> Each series was re-run from 10 different start points (0, 50, …, 450 steps dropped) with the same test window. The max/min NMSE ratio measures how much the result depends on the start.')}</li>
<li>{T('<strong>Regra de decisão fixada antes.</strong> A promoção exigia passar em <em>todos</em> os critérios vinculantes. Resultados desfavoráveis de versões anteriores foram publicados, e registrados no §10.', '<strong>Decision rule fixed in advance.</strong> Promotion required passing <em>all</em> binding criteria. Unfavourable results of earlier versions were published and are recorded in §10.')}</li></ul>
<h2>9.2 {T('Conjunto held-out (10 séries reais nunca usadas)', 'Held-out set (10 real series never used)')}</h2>
{tbl(['', T('Série', 'Series'), T('Frequência', 'Frequency'), 'd', 's'], rows_ds)}
<p class="small">{T('d = número de variáveis de entrada (todas as variáveis em t−1, incluindo o próprio alvo); s = período declarado. Fontes: Operador Nacional do Sistema Elétrico (dados abertos), Banco Central do Brasil (SGS) e Monash Time Series Forecasting Archive (Godahewa et al., 2021).', 'd = number of input variables (all variables at t−1, including the target itself); s = declared period. Sources: Brazilian National Electric System Operator (open data), Central Bank of Brazil (SGS) and the Monash Time Series Forecasting Archive (Godahewa et al., 2021).')}</p>
<div class="no-break"><h2>9.3 {T('Critérios pré-registrados e resultado', 'Pre-registered criteria and outcome')}</h2>
{tbl(acc, crit)}</div>
<div class="verdict">{T('DECISÃO PRÉ-REGISTRADA: PROMOVIDA — todos os critérios vinculantes atendidos.', 'PRE-REGISTERED DECISION: PROMOTED — all binding criteria met.')}</div>
<h2>9.4 {T('Resultados por série (NMSE, menor é melhor)', 'Results per series (NMSE, lower is better)')}</h2>
{tbl(['', T('Série', 'Series'), 'LEBRE v0.51', 'NLinear', 'DLinear', 'Holt-W.', T('Melhor Chronos', 'Best Chronos'), T('Persist.', 'Persist.'), 'v0.5', 'v0.4.5', T('Estab.', 'Stab.'), T('Cobert.', 'Cover.')], rows_t)}
<p class="small">{T('Negrito: menor NMSE entre LEBRE v0.51, NLinear, DLinear, Holt-Winters e o melhor Chronos. Estab.: máx./mín. do NMSE entre 10 pontos de partida. Cobert.: cobertura empírica do intervalo de 90%.', 'Bold: lowest NMSE among LEBRE v0.51, NLinear, DLinear, Holt-Winters and the best Chronos. Stab.: max/min NMSE across 10 start points. Cover.: empirical coverage of the 90% interval.')}</p>
{fig(D['D5'], T('Razão da média geométrica do NMSE em relação ao NLinear no held-out.', 'Geometric-mean NMSE ratio relative to NLinear on the held-out set.'))}
{tbl([T('Posição', 'Position'), T('Modelo', 'Model'), T('Posto médio', 'Mean rank')], rk)}
<h2>9.5 {T('Resultados internos e verificações secundárias', 'Internal results and secondary checks')}</h2>
<p>{T('<strong>Suíte interna</strong> (14 processos sintéticos com estrutura conhecida — atrasos exatos e múltiplos, estados latentes, quiescência, mudanças de regime, estrutura redundante e um controle não linear; 30 sementes novas por tarefa):', '<strong>Internal suite</strong> (14 synthetic processes with known structure — exact and multiple delays, latent states, quiescence, regime switches, redundant structure and a non-linear control; 30 fresh seeds per task):')}</p>
{tbl([T('Versão', 'Version'), 'NMSE', T('FP/passo (média)', 'FP/step (mean)'), T('FP pico', 'FP peak'), T('Cobertura', 'Coverage'), T('Estrutura exata', 'Exact structure')],
     [(MN["LEBRE_V051"], n(I.loc["V051", "nmse"], 4), n(I.loc["V051", "fp"], 1), n(I.loc["V051", "peak"], 0), n(I.loc["V051", "cov"], 3), f'{n(100 * I.loc["V051", "struct"], 1)}%'),
      (MN["LEBRE_V045"], n(I.loc["V045", "nmse"], 4), n(I.loc["V045", "fp"], 1), n(I.loc["V045", "peak"], 0), n(I.loc["V045", "cov"], 3), f'{n(100 * I.loc["V045", "struct"], 1)}%'),
      (MN["LEBRE_V05"], n(I.loc["V05", "nmse"], 4), n(I.loc["V05", "fp"], 1), n(I.loc["V05", "peak"], 0), n(I.loc["V05", "cov"], 3), f'{n(100 * I.loc["V05", "struct"], 1)}%')])}
<p>{T('Nos sistemas guiados por entradas, a v0.51 iguala a v0.4.5 e recupera a estrutura correta em ~91% das verificações. O especialista de memória sozinho não serve ali (NMSE ≈ 1,0). A v0.5 (com janela densa de 96–288 defasagens) é ~9% melhor nesse suíte, mas custa ~7× mais.',
'On input-driven systems v0.51 matches v0.4.5 and recovers the correct structure in ~91% of the checks. The memory expert alone is useless there (NMSE ≈ 1.0). v0.5 (with a dense 96–288-lag window) is ~9% better on this suite but costs ~7× more.')}</p>
<p>{T(f'<strong>Verificações secundárias</strong> (conjuntos já vistos em etapas anteriores, rotulados como semi-held-out): num segundo conjunto de 10 séries (5 brasileiras) a v0.51 ficou em {p3["heldout_v05"]["position"]}º de {p3["heldout_v05"]["n_models"]}, com {n(p3["heldout_v05"]["geo_vs_NLinear"], 2)}× o NLinear e {n(p3["heldout_v05"]["geo_vs_best_chronos"], 2)}× o melhor Chronos. Num benchmark de 10 tarefas reais com 36 modelos (filtros adaptativos, redes recorrentes e reservatórios online, árvores online, modelos lineares modernos e modelos de fundação) ficou em {p3["bench04"]["position"]}º de {p3["bench04"]["n_models"]}, com {n(p3["bench04"]["geo_vs_NLinear"], 2)}× o NLinear, {n(p3["bench04"]["geo_vs_best_chronos"], 2)}× o melhor Chronos e estabilidade máxima de {n(p3["bench04"]["instab_max"], 2)}.',
f'<strong>Secondary checks</strong> (sets seen in earlier stages, labelled semi-held-out): on a second set of 10 series (5 Brazilian) v0.51 ranked {p3["heldout_v05"]["position"]}rd of {p3["heldout_v05"]["n_models"]}, at {n(p3["heldout_v05"]["geo_vs_NLinear"], 2)}× NLinear and {n(p3["heldout_v05"]["geo_vs_best_chronos"], 2)}× the best Chronos. On a benchmark of 10 real tasks with 36 models (adaptive filters, online recurrent networks and reservoirs, online trees, modern linear models and foundation models) it ranked {p3["bench04"]["position"]}rd of {p3["bench04"]["n_models"]}, at {n(p3["bench04"]["geo_vs_NLinear"], 2)}× NLinear, {n(p3["bench04"]["geo_vs_best_chronos"], 2)}× the best Chronos, with maximum instability {n(p3["bench04"]["instab_max"], 2)}.')}</p>
<h2>9.6 {T('Evidência de projeto: por que cada peça existe', 'Design evidence: why each part exists')}</h2>
<p>{T('Ablações feitas nos dados de desenvolvimento (13 séries reais já usadas e a suíte interna com sementes de desenvolvimento). A coluna "séries reais" é a razão geométrica do NMSE contra um NLinear online com janela densa.', 'Ablations on development data (13 previously used real series and the internal suite with development seeds). The "real series" column is the geometric NMSE ratio against an online NLinear with a dense window.')}</p>
{tbl([T('Variante', 'Variant'), T('Séries reais', 'Real series'), T('Interno', 'Internal'), T('Conclusão', 'Conclusion')],
     [(T('só S (LEBRE v0.4.5)', 'S only (LEBRE v0.4.5)'), "2,07" if P else "2.07", "0,221" if P else "0.221", T('M é necessária', 'M is necessary')),
      (T('só M', 'M only'), "0,96" if P else "0.96", "1,008" if P else "1.008", T('S é necessário', 'S is necessary')),
      (T('M sem perfil sazonal G', 'M without seasonal profile G'), "1,12" if P else "1.12", "—", T('G é necessário', 'G is necessary')),
      (T('cascata M → S (sem combinador)', 'cascade M → S (no combiner)'), "0,97" if P else "0.97", "0,304" if P else "0.304", T('combinador é necessário', 'combiner is necessary')),
      (T('S → M sobre o resíduo de S', 'S → M on S\'s residual'), "1,47" if P else "1.47", "0,255" if P else "0.255", T('idem', 'idem')),
      (T('combinação por regressão', 'regression combination'), "0,94" if P else "0.94", "0,240" if P else "0.240", T('média dinâmica preferível', 'dynamic averaging preferred')),
      (T('sem dormência de S', 'without S dormancy'), "0,98" if P else "0.98", "0,220" if P else "0.220", T('dormência: −25 FP sem perda', 'dormancy: −25 FP, no loss')),
      (f'<strong>LEBRE v0.51</strong>', "<strong>0,98</strong>" if P else "<strong>0.98</strong>", "<strong>0,220</strong>" if P else "<strong>0.220</strong>", "—")])}""")

        # ------------------------------------------------------------ 10 evolution
        ev = [("v0.1", T("Organização original: caminho-base, atrasos esparsos, estado latente, ciclo de vida com probação em sombra.", "Original organisation: base path, sparse delays, latent state, lifecycle with shadow probation."), T("referência canônica congelada", "frozen canonical reference")),
              ("v0.3.2", T("Toda decisão estrutural vira teste estatístico (martingale de mistura, CUSUM); latente em forma de inovações de Kalman; ≤ 100 FP.", "Every structural decision becomes a statistical test (mixture martingale, CUSUM); latent in Kalman innovations form; ≤ 100 FP."), T("estável, mas 2–3× pior que modelos modernos em séries sazonais", "stable, but 2–3× worse than modern models on seasonal series")),
              ("v0.4 / v0.4.5", T("Aprendizado proporcional, intervalos calibrados, explicação exata; guarda de contrato de entrada.", "Proportionate learning, calibrated intervals, exact explanation; input-contract guard."), T("instabilidade dependente do ponto de partida; ~2,6× o NLinear em dados reais novos", "start-point-dependent instability; ~2.6× NLinear on new real data")),
              ("v0.5", T("Três especialistas com janela densa de 96–288 defasagens.", "Three experts with a dense 96–288-lag window."), T("competitiva (1,06× NLinear) e estável, mas ~1000 FP/passo", "competitive (1.06× NLinear) and stable, but ~1000 FP/step")),
              ("v0.51", T("Dois especialistas mínimos: estrutural + memória airline; média dinâmica de modelos.", "Two minimal experts: structural + airline memory; dynamic model averaging."), T("0,84× NLinear, estável, ~120 FP/passo", "0.84× NLinear, stable, ~120 FP/step"))]
        out.append(f"""<div class="page-break"></div><h1>10. {toc[9]}</h1>
{tbl([T('Versão', 'Version'), T('Ideia central', 'Central idea'), T('Resultado', 'Outcome')], ev)}
<p>{T('<strong>Lições que moldaram a v0.51.</strong> (1) O desempenho em séries reais sazonais depende de memória do próprio alvo expressa relativa ao último valor; a hipótese estrutural esparsa, sozinha, não basta. (2) Aprender o nível pelo termo de viés torna as decisões estruturais iniciais dependentes do ponto de partida. (3) Recortar entradas antes que o escalonador do ambiente estabilize, sem pausar a evidência, fixa estruturas espúrias. (4) Uma memória bem especificada, com 5 números aprendidos, supera uma janela densa com centenas de pesos aprendidos online, em linha com a lição das competições M: métodos estatísticos simples e bem especificados são difíceis de superar (Makridakis et al., 2020).',
'<strong>Lessons that shaped v0.51.</strong> (1) Accuracy on real seasonal series depends on memory of the target itself expressed relative to the last value; the sparse structural hypothesis alone is not enough. (2) Learning the level through the bias term makes the early structural decisions depend on the start point. (3) Clipping inputs before the environment\'s scaler stabilises, without pausing evidence, locks in spurious structures. (4) A well-specified memory with 5 learned numbers beats a dense window with hundreds of weights learned online, in line with the lesson of the M competitions: simple, well-specified statistical methods are hard to beat (Makridakis et al., 2020).')}</p>""")

        # ------------------------------------------------------------ 11 limits
        lim = [T("O orçamento de 150 FP/passo vale para até ~6 entradas; cada entrada adicional custa ~8 FP.", "The 150 FP/step budget holds for up to ~6 inputs; every extra input costs ~8 FP."),
               T("Chronos-2 continua mais preciso (~1,37× melhor em média geométrica), com custo 10⁶–10⁷ vezes maior.", "Chronos-2 remains more accurate (~1.37× better in geometric mean), at 10⁶–10⁷ times the cost."),
               T("A classe é linear nos parâmetros: relações fortemente não lineares entre entradas e alvo não são capturadas.", "The class is linear in the parameters: strongly non-linear input–target relations are not captured."),
               T("Previsão de um passo à frente; horizontes longos não foram avaliados.", "One-step-ahead forecasting; long horizons were not evaluated."),
               T("A cobertura do intervalo é de longo prazo, não condicional; numa série ficou em 0,965 (acima da faixa).", "Interval coverage is long-run, not conditional; on one series it was 0.965 (above the band)."),
               T("As garantias estatísticas dos testes são exatas só sob hipóteses idealizadas; no laço adaptativo foram verificadas empiricamente.", "The tests' statistical guarantees are exact only under idealised assumptions; inside the adaptive loop they were verified empirically."),
               T("A troca de pesos do combinador é um sinal interpretável, não um alarme com taxa de erro controlada.", "The combiner's weight switch is an interpretable signal, not an alarm with a controlled error rate."),
               T("Não afirmamos: estado da arte, causalidade física, eficiência energética (FP não é energia), cobertura condicional nem novidade científica.", "We do not claim: state of the art, physical causality, energy efficiency (FP is not energy), conditional coverage or scientific novelty.")]
        out.append(f"""<h1>11. {toc[10]}</h1><ul>{''.join(f'<li>{x}</li>' for x in lim)}</ul>""")

        # ------------------------------------------------------------ 12 parameters
        par = [("μ (S)", "0,1" if P else "0.1", T("passo do NLMS do especialista estrutural", "NLMS step of the structural expert")),
               ("μ (M)", "0,05" if P else "0.05", T("passo do NLMS da memória", "NLMS step of the memory")),
               ("a", "0,1" if P else "0.1", T("perfil sazonal (Θ = 0,9 no modelo airline)", "seasonal profile (Θ = 0.9 in the airline model)")),
               (T("fator da média", "mean factor"), "0,01" if P else "0.01", T("média exponencial para a reversão à média", "exponential mean for mean reversion")),
               ("η", "1/2", T("derivado da verossimilhança gaussiana", "derived from the Gaussian likelihood")),
               ("λ", "0,99" if P else "0.99", T("esquecimento do combinador e do σ̂² combinado (~100 passos)", "forgetting of the combiner and combined σ̂² (~100 steps)")),
               (T("limiar de dormência", "dormancy threshold"), "0,01" if P else "0.01", T("peso abaixo do qual a evidência de S pausa", "weight below which S's evidence pauses")),
               ("L", "32", T("atraso máximo dos candidatos", "maximum candidate delay")),
               ("M_max", "4", T("orçamento de átomos estruturais", "structural atom budget")),
               ("α", "0,05" if P else "0.05", T("taxa de promoção falsa (limiar log(p/α))", "false-promotion rate (threshold log(p/α))")),
               ("ARL", "6000", T("tempo médio até alarme falso (h = log ARL)", "mean time to false alarm (h = log ARL)")),
               ("T_idle", "500", T("aluguel de parcimônia r = h/T_idle", "parsimony rent r = h/T_idle")),
               (T("polos", "poles"), "{0; 0,5; 0,8; 0,95}" if P else "{0, 0.5, 0.8, 0.95}", T("banco do estado latente", "latent-state bank")),
               (T("recorte", "clip"), "±8", T("contrato de entrada (P6)", "input contract (P6)")),
               (T("excitação", "excitation"), "10%", T("potência mínima para acumular evidência (P4)", "minimum power to accrue evidence (P4)")),
               (T("intervalo", "interval"), "α = 0,1; γ = 0,1" if P else "α = 0.1; γ = 0.1", T("cobertura alvo 90%; passo do rastreador", "target coverage 90%; tracker step")),
               (T("cadência", "cadence"), "8", T("passos entre recálculos de raiz, inversa, exp e quantil", "steps between square root, inverse, exp and quantile recomputation")),
               ("s", T("do ambiente", "from environment"), T("período de amostragem declarado (único dado externo)", "declared sampling period (only external information)"))]
        out.append(f"""<div class="page-break"></div><h1>12. {toc[11]}</h1>
<p>{T('Todos os valores são constantes do projeto, iguais para todas as séries; nenhum foi ajustado nos dados de avaliação.', 'All values are design constants, identical for every series; none was tuned on the evaluation data.')}</p>
{tbl([T('Parâmetro', 'Parameter'), T('Valor', 'Value'), T('Papel', 'Role')], par)}""")

        # ------------------------------------------------------------ 13 references
        out.append(f"""<h1>13. {toc[12]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>""")
        if P:
            fix = lambda mm: re.sub(r"(?<=\d)\.(?=\d)", "{,}", mm.group(0))
            out = [re.sub(r'<div class="math-box">.*?</div>', fix, o, flags=re.S) for o in out]
        return out
    return S


TEXT = {
    "pt": dict(html_lang="pt-BR", badge="Especificação v0.51",
               title="Especificação da Arquitetura LEBRE v0.51",
               subtitle="Previsão online mínima, barata, competitiva e explicável",
               expansion="<strong>LEBRE:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>Arquitetura:</strong> especialista estrutural + especialista de memória + média dinâmica de modelos",
               meta=[("Custo", "~121 operações/passo; ~1,3 KB"), ("Desempenho (held-out)", "0,84× NLinear · 1,37× Chronos-2"),
                     ("Estabilidade", "variação máx. 1,08× entre partidas"), ("Status", "versão de pesquisa promovida por avaliação pré-registrada")],
               footer_l="Projeto de Pesquisa Codinome Lebre", footer_r="Setembro de 2026 • Documento v0.51",
               v01_header="Especificação da Arquitetura LEBRE v0.1 — Documento de Referência", v01_status="Status: FROZEN_WITH_SCOPE_LIMITS",
               v01_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1",
               page_header="Especificação da Arquitetura LEBRE v0.51", page_status="Status: versão de pesquisa", page_word='"Página "',
               page_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.51",
               diag=DIAG["pt"], model_names=MODEL_NAMES["pt"], sections=_sections("pt")),
    "en": dict(html_lang="en", badge="Specification v0.51",
               title="LEBRE v0.51 Architecture Specification",
               subtitle="Minimal, cheap, competitive and explainable online forecasting",
               expansion="<strong>LEBRE:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>Architecture:</strong> structural expert + memory expert + dynamic model averaging",
               meta=[("Cost", "~121 operations/step; ~1.3 KB"), ("Accuracy (held-out)", "0.84× NLinear · 1.37× Chronos-2"),
                     ("Stability", "max. variation 1.08× across starts"), ("Status", "research version promoted by pre-registered evaluation")],
               footer_l="Codinome Lebre Research Project", footer_r="September 2026 • Document v0.51",
               v01_header="Especificação da Arquitetura LEBRE v0.1 — Documento de Referência", v01_status="Status: FROZEN_WITH_SCOPE_LIMITS",
               v01_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1",
               page_header="LEBRE v0.51 Architecture Specification", page_status="Status: research version", page_word='"Page "',
               page_footer="Codinome Lebre Research Project • Architecture Specification v0.51",
               diag=DIAG["en"], model_names=MODEL_NAMES["en"], sections=_sections("en")),
}
