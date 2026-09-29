"""Revision 1 of the v0.51 specification text: incorporates Errata 01 (E1–E6) into v051r1_text.py (kept for provenance).
The frozen v051_text.py is not touched."""
import os

H = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(H, "v051r1_text.py")
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# ------------------------------------------------------------------ diagrams (E1, E3, E4)
rep('d1_M2="forma online do modelo airline"', 'd1_M2="memória inspirada no airline"')
rep('d1_M2="online form of the airline model"', 'd1_M2="memory inspired by airline"')
rep('"m: média exponencial do alvo (reversão à média ⇔ suavização exponencial simples com α aprendido)"',
    '"m: média exponencial lenta do alvo, taxa fixa 0,01 (reversão à média: mistura aprendida de y(t−1) e m)"')
rep('"m: exponential mean of the target (mean reversion ⇔ simple exponential smoothing with a learned α)"',
    '"m: slow exponential mean of the target, fixed rate 0.01 (mean reversion: learned mix of y(t−1) and m)"')
rep('"  ⇔ incremento sazonal previsto pelo modelo airline SARIMA(0,1,1)(0,1,1)s ⇔ estado sazonal do Holt-Winters"',
    '"  inspirado no incremento sazonal do airline e no estado sazonal do Holt-Winters (analogia, não equivalência)"')
rep('"  ⇔ seasonal increment forecast by the airline model SARIMA(0,1,1)(0,1,1)s ⇔ Holt-Winters seasonal state"',
    '"  inspired by the airline seasonal increment and the Holt-Winters seasonal state (analogy, not equivalence)"')
rep('d4_sub="Promoção: teste com erro tipo I controlado por episódio. Remoção',
    'd4_sub="Promoção: erro tipo I controlado por episódio sob H₀ (§5.3). Remoção')
rep('d4_sub="Promotion: test with type-I error controlled per episode. Eviction',
    'd4_sub="Promotion: type-I error controlled per episode under H₀ (§5.3). Eviction')

# ------------------------------------------------------------------ §5.2 (E3, E4)
rep(r'''(i) A previsão do modelo airline SARIMA(0,1,1)(0,1,1)<sub>s</sub> para o incremento sazonal é uma média exponencialmente ponderada dos incrementos da mesma fase em ciclos anteriores, com fator Θ; o perfil \\(G\\) com \\(a=0{,}1\\) é exatamente isso com Θ = 0,9, e coincide com o estado sazonal do Holt-Winters e com o "ciclo recorrente aprendível" do CycleNet. (ii) Com peso \\(w_1\\), a feature de reversão à média produz \\(y_{t-1}+w_1(m-y_{t-1})\\), que é a suavização exponencial simples com constante aprendida — ótima para um nível local ruidoso (Muth, 1960).''',
    r'''(i) O perfil \\(G\\) é uma média exponencial (\\(a=0{,}1\\), isto é, fator 0,9 por ciclo) dos incrementos observados na mesma fase em ciclos anteriores. É <em>inspirado</em> na suavização sazonal do Holt-Winters e na componente sazonal do modelo airline SARIMA(0,1,1)(0,1,1)<sub>s</sub>, e cumpre papel análogo ao do "ciclo recorrente aprendível" do CycleNet; <strong>não é equivalente</strong> a nenhum deles. (ii) Com peso \\(w_1\\), a feature de reversão à média produz \\((1-w_1)\\,y_{t-1}+w_1\\,m_{t-1}\\): uma mistura aprendida entre o último valor e uma média exponencial lenta de taxa fixa (0,01). Ela aproxima o efeito de um nível local suavizado, na linha de Muth (1960), mas <strong>não é</strong> a suavização exponencial simples com constante aprendida.''')
rep(r'''(i) The airline model SARIMA(0,1,1)(0,1,1)<sub>s</sub> forecasts the seasonal increment as an exponentially weighted average of the increments at the same phase in previous cycles, with factor Θ; the profile \\(G\\) with \\(a=0.1\\) is exactly that with Θ = 0.9, and coincides with the Holt-Winters seasonal state and with CycleNet\'s "learnable recurrent cycle". (ii) With weight \\(w_1\\), the mean-reversion feature yields \\(y_{t-1}+w_1(m-y_{t-1})\\), i.e. simple exponential smoothing with a learned constant — optimal for a noisy local level (Muth, 1960).''',
    r'''(i) The profile \\(G\\) is an exponential average (\\(a=0.1\\), i.e. factor 0.9 per cycle) of the increments observed at the same phase in previous cycles. It is <em>inspired by</em> Holt-Winters seasonal smoothing and by the seasonal component of the airline model SARIMA(0,1,1)(0,1,1)<sub>s</sub>, and plays a role analogous to CycleNet\'s "learnable recurrent cycle"; it is <strong>not equivalent</strong> to any of them. (ii) With weight \\(w_1\\), the mean-reversion feature yields \\((1-w_1)\\,y_{t-1}+w_1\\,m_{t-1}\\): a learned mix of the last value and a slow exponential mean with a fixed rate (0.01). It approximates the effect of a smoothed local level, in the spirit of Muth (1960), but it is <strong>not</strong> simple exponential smoothing with a learned constant.''')

# ------------------------------------------------------------------ §5.3 (E1, E2, E5)
rep(r'''<p>{T('Com incrementos condicionalmente simétricos, \\(M_t\\) é supermartingale (de la Peña, 1999; Howard et al., 2021), e pela desigualdade de Ville (1939) a probabilidade de uma promoção falsa em qualquer instante é ≤ α/p por candidato <em>e por episódio de teste</em>. O controle vale por teste, não para o fluxo inteiro: como candidatos podem ser retestados com estatística nova, promoções falsas podem se acumular em fluxos muito longos (a taxa empírica está na §11). ''',
    r'''<p>{T('<strong>Hipótese nula e alcance da garantia.</strong> Seja H₀ a hipótese de que, sem o candidato, o especialista S já fornece a média condicional correta de \\(y_t\\) e o ruído é condicionalmente simétrico. Sob H₀, os incrementos \\(e_k\\varphi_k\\) são condicionalmente simétricos, \\(M_t\\) é supermartingale (de la Peña, 1999; Howard et al., 2021), e pela desigualdade de Ville (1939) a probabilidade de promover o candidato em algum instante do episódio é ≤ α/p. <strong>Fora de H₀</strong> (átomos verdadeiros ainda ausentes, pesos em convergência, estrutura mal especificada) não há garantia: o teste mede a <strong>relevância preditiva do candidato para o resíduo atual de S</strong> e pode promover um átomo apenas correlacionado com a estrutura ausente. Uma promoção significa, portanto, "este termo melhora a previsão dado o modelo atual", e não "este é um termo verdadeiro do processo". Não foi feita uma demonstração formal da propriedade de e-process sob a filtração efetiva do algoritmo; há construções com hipóteses verificáveis na literatura (Pérez-Ortiz et al., 2024; Lindon et al., 2026). A triagem só decide <em>quando</em> um candidato começa a ser testado, e esse instante depende apenas do passado: as estatísticas do teste partem de zero e nenhum dado da triagem entra no martingale. O controle vale por episódio, não para o fluxo inteiro: como candidatos podem ser retestados com estatística nova, o erro acumulado ao longo da vida do sistema não tem limite (a taxa empírica está na §11). Existem métodos que controlam o erro através de hipóteses que chegam e evoluem ao longo do tempo (Foster e Stine, 2008; Xu e Ramdas, 2024; Tavyrikov et al., 2026; de Heide, 2026); a v0.51 não os usa. ''')
rep(r''''With conditionally symmetric increments, \\(M_t\\) is a supermartingale (de la Peña, 1999; Howard et al., 2021), and by Ville\'s inequality (1939) the probability of a false promotion at any time is ≤ α/p per candidate <em>and per test episode</em>. The control holds per test, not for the whole stream: since candidates can be re-tested with fresh statistics, false promotions can accumulate over very long streams (the empirical rate is in §11). ''',
    r''''<strong>Null hypothesis and reach of the guarantee.</strong> Let H₀ be the hypothesis that, without the candidate, expert S already gives the correct conditional mean of \\(y_t\\) and the noise is conditionally symmetric. Under H₀ the increments \\(e_k\\varphi_k\\) are conditionally symmetric, \\(M_t\\) is a supermartingale (de la Peña, 1999; Howard et al., 2021), and by Ville\'s inequality (1939) the probability of promoting the candidate at some time during the episode is ≤ α/p. <strong>Outside H₀</strong> (true atoms still missing, weights still converging, misspecified structure) there is no guarantee: the test measures the <strong>predictive relevance of the candidate for S\'s current residual</strong> and may promote an atom that is merely correlated with the missing structure. A promotion therefore means "this term improves the forecast given the current model", not "this is a true term of the process". No formal proof of the e-process property under the algorithm\'s actual filtration was carried out; constructions with verifiable assumptions exist in the literature (Pérez-Ortiz et al., 2024; Lindon et al., 2026). Screening only decides <em>when</em> a candidate starts being tested, and that time depends only on the past: the test statistics start from zero and no screening data enter the martingale. Control holds per episode, not for the whole stream: since candidates can be re-tested with fresh statistics, the error accumulated over the system\'s lifetime is unbounded (the empirical rate is in §11). Methods exist that control error across hypotheses arriving and evolving over time (Foster and Stine, 2008; Xu and Ramdas, 2024; Tavyrikov et al., 2026; de Heide, 2026); v0.51 does not use them. ''')

# ------------------------------------------------------------------ §8 (E1)
rep("Promoções têm erro tipo I controlado por episódio de teste; remoções",
    "Promoções têm erro tipo I controlado por episódio sob H₀ e, fora dela, indicam relevância preditiva dado o modelo atual; remoções")
rep("Promotions have type-I error controlled per test episode; evictions",
    "Promotions have type-I error controlled per episode under H₀ and, outside it, indicate predictive relevance given the current model; evictions")

# ------------------------------------------------------------------ §10.1 (E3)
rep("que é uma forma online do modelo airline / Holt-Winters com pesos aprendidos por NLMS.",
    "uma memória linear com features inspiradas no modelo airline e no Holt-Winters e pesos aprendidos por NLMS.")
rep("which is an online form of the airline / Holt-Winters model with weights learned by NLMS.",
    "a linear memory with features inspired by the airline and Holt-Winters models and weights learned by NLMS.")

# ------------------------------------------------------------------ §11.1 (E1)
rep("nenhuma promoção falsa em 2 milhões de passos nulos. O controle é formalmente por episódio,",
    "nenhuma promoção falsa em 2 milhões de passos nulos com entradas independentes do alvo, situação em que H₀ (§5.3) vale aproximadamente. O controle é formalmente por episódio,")
rep("no false promotion in 2 million null steps. The control is formally per episode,",
    "no false promotion in 2 million null steps with inputs independent of the target, a situation in which H₀ (§5.3) approximately holds. The control is formally per episode,")

# ------------------------------------------------------------------ §12 (E6)
rep("É a parte mais interessante do ponto de vista científico e conecta-se com a área de inferência sempre válida (Ramdas et al., 2023).",
    "É a parte mais interessante do ponto de vista científico e conecta-se com a área de inferência sempre válida (Ramdas et al., 2023). Seus componentes têm precedentes diretos: seleção estatística de variáveis em fluxo com controle de falsas descobertas (Zhou et al., 2006; Ungar et al., 2005); estruturas criadas, testadas em paralelo e substituídas ou podadas em fluxo (Hulten et al., 2001; Ikonomovska et al., 2011; Almeida et al., 2013); testes sempre válidos para coeficientes de regressão (Lindon et al., 2026); bancos de modelos dinâmicos ponderados por inovações (Magill, 1965). O que a v0.51 reúne é uma combinação específica desses elementos sob orçamento de custo, sem afirmação de novidade.")
rep("It is the most interesting part scientifically and connects to the area of anytime-valid inference (Ramdas et al., 2023).",
    "It is the most interesting part scientifically and connects to the area of anytime-valid inference (Ramdas et al., 2023). Its components have direct precedents: statistical feature selection in streams with false-discovery control (Zhou et al., 2006; Ungar et al., 2005); structures created, tested in parallel and replaced or pruned in streams (Hulten et al., 2001; Ikonomovska et al., 2011; Almeida et al., 2013); anytime-valid tests for regression coefficients (Lindon et al., 2026); banks of dynamic models weighted by innovations (Magill, 1965). What v0.51 brings together is a specific combination of these elements under a cost budget, with no novelty claim.")

# ------------------------------------------------------------------ §14 limits (E1, E5)
rep('               T("O controle de erro das promoções vale por episódio de teste; as remoções não têm taxa de alarme falso garantida.", "Promotion error control holds per test episode; evictions have no guaranteed false-alarm rate."),',
    '               T("O controle de erro das promoções vale por episódio e só sob H₀ (S já correto sem o candidato); fora dela, uma promoção indica relevância preditiva, não estrutura verdadeira. O erro acumulado com retestes não é limitado. As remoções não têm taxa de alarme falso garantida.", "Promotion error control holds per episode and only under H₀ (S already correct without the candidate); outside it a promotion indicates predictive relevance, not true structure. Error accumulated through re-testing is unbounded. Evictions have no guaranteed false-alarm rate."),')

# ------------------------------------------------------------------ §15 (E3)
rep('T("perfil sazonal (Θ = 0,9 no modelo airline)", "seasonal profile (Θ = 0.9 in the airline model)")',
    'T("perfil sazonal (fator 0,9 por ciclo; análogo, não igual, ao Θ do airline)", "seasonal profile (factor 0.9 per cycle; analogous, not equal, to the airline Θ)")')

# ------------------------------------------------------------------ revision note in §1
rep('<div class="alert alert-warning"><strong>{T("Premissa", "Premise")}:</strong>',
    '''<div class="alert alert-info"><strong>{T("Revisão 1", "Revision 1")}:</strong> {T("a arquitetura, o código, os parâmetros e os resultados são os mesmos da revisão original. Mudam apenas descrições: (1) o alcance da garantia de promoção (§5.3, §8, §11, §14); (2) a relação da memória com os modelos airline e Holt-Winters e da reversão à média com a suavização exponencial (§5.2, D1, D3, §10, §15); (3) o controle de erro ao longo do fluxo (§5.3); (4) o posicionamento frente a trabalhos relacionados (§12).", "the architecture, code, parameters and results are the same as in the original revision. Only descriptions change: (1) the reach of the promotion guarantee (§5.3, §8, §11, §14); (2) the relation of the memory to the airline and Holt-Winters models and of mean reversion to exponential smoothing (§5.2, D1, D3, §10, §15); (3) error control along the stream (§5.3); (4) positioning relative to related work (§12).")}</div>
<div class="alert alert-warning"><strong>{T("Premissa", "Premise")}:</strong>''')

# ------------------------------------------------------------------ references
rep('    "Operador Nacional do Sistema Elétrico (ONS). Dados abertos: balanço de energia por subsistema, curva de carga horária.",',
    '''    "Almeida, E., Ferreira, C., Gama, J. (2013). Adaptive model rules from data streams. <em>Proc. ECML PKDD</em>, LNCS 8188, 480–492.",
    "de Heide, R. (2026). Dynamic e-closure for online hypotheses with any-time-valid evidence. <em>arXiv preprint</em> 2608.09927.",
    "Foster, D. P., Stine, R. A. (2008). α-investing: a procedure for sequential control of expected false discoveries. <em>Journal of the Royal Statistical Society B</em> 70(2), 429–444.",
    "Hulten, G., Spencer, L., Domingos, P. (2001). Mining time-changing data streams. <em>Proc. ACM KDD</em>, 97–106.",
    "Ikonomovska, E., Gama, J., Džeroski, S. (2011). Learning model trees from evolving data streams. <em>Data Mining and Knowledge Discovery</em> 23(1), 128–168.",
    "Lindon, M., Ham, D. W., Tingley, M., Bojinov, I. (2026). Anytime-valid inference in linear models and regression-adjusted causal inference. <em>Journal of the American Statistical Association</em>.",
    "Magill, D. T. (1965). Optimal adaptive estimation of sampled stochastic processes. <em>IEEE Transactions on Automatic Control</em> 10(4), 434–439.",
    "Pérez-Ortiz, M. F., Lardy, T., de Heide, R., Grünwald, P. (2024). E-statistics, group invariance and anytime-valid testing. <em>Annals of Statistics</em> 52(4), 1410–1432.",
    "Tavyrikov, Y., Goeman, J. J., de Heide, R. (2026). Carefree multiple testing with e-processes. <em>Electronic Journal of Statistics</em>.",
    "Ungar, L. H., Zhou, J., Foster, D. P., Stine, R. A. (2005). Streaming feature selection using IIC. <em>Proc. AISTATS</em>, PMLR R5, 357–364.",
    "Xu, Z., Ramdas, A. (2024). Online multiple testing with e-values. <em>Proc. AISTATS</em>, PMLR 238.",
    "Zhou, J., Foster, D. P., Stine, R. A., Ungar, L. H. (2006). Streamwise feature selection. <em>Journal of Machine Learning Research</em> 7, 1861–1885.",
    "Operador Nacional do Sistema Elétrico (ONS). Dados abertos: balanço de energia por subsistema, curva de carga horária.",''')
rep('\n# translation of the model',
    '\nREFS = sorted(REFS[:-2], key=lambda r: r.lower().replace("de heide", "heide").replace("de la peña", "pena")) + REFS[-2:]\n\n# translation of the model')

# ------------------------------------------------------------------ cover / running header
rep('badge="Especificação v0.51",', 'badge="Especificação v0.51 · Revisão 1",')
rep('badge="Specification v0.51",', 'badge="Specification v0.51 · Revision 1",')
rep('footer_r="Setembro de 2026 • Documento v0.51",', 'footer_r="Setembro de 2026 • Documento v0.51, revisão 1",')
rep('footer_r="September 2026 • Document v0.51",', 'footer_r="September 2026 • Document v0.51, revision 1",')
rep('page_status="Status: versão de pesquisa"', 'page_status="Status: versão de pesquisa · rev. 1"')
rep('page_status="Status: research version"', 'page_status="Status: research version · rev. 1"')

open(p, "w", encoding="utf-8").write(s)
print("ok")
