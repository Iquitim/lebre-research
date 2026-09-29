# LEBRE v0.51 — Errata 01

**Documento corrigido:** Especificação da Arquitetura LEBRE v0.51 (PDF PT-BR/EN) e `ARQUITETURA_V051.md`, congelados em `LEBRE-V0.51-FREEZE-01`.
**Data:** 25 de setembro de 2026
**Natureza:** correções e esclarecimentos **só de texto**. O código, os parâmetros e os resultados da v0.51 **não mudam**. Os arquivos congelados não foram editados, e esta errata prevalece sobre os trechos indicados.

| ID | Tipo | Onde | Resumo |
|---|---|---|---|
| E1 | **Correção** | §5.3, §8, §11.1, D4 | A garantia de promoção vale sob uma hipótese nula mais forte do que o texto sugere |
| E2 | Esclarecimento | §5.3 | Por que a triagem não invalida o teste |
| E3 | **Correção** | §5.2, D1, D3, §10.1, §15; `ARQUITETURA_V051.md` §4 | Relação da memória M com o modelo airline e o Holt-Winters: analogia, não equivalência |
| E4 | **Correção** | §5.2 (ii), D3; `ARQUITETURA_V051.md` §4 | A feature de reversão à média não reproduz a suavização exponencial simples |
| E5 | Esclarecimento | §5.3, §11.1, §14 | Controle de erro por episódio, e não ao longo do fluxo; a literatura oferece controle global |
| E6 | Esclarecimento | §12 | Posicionamento da parte estrutural em relação à literatura |

---

## E1 — Alcance da garantia de promoção (correção)

**Texto atual (§5.3):** "Com incrementos condicionalmente simétricos, \(M_t\) é supermartingale (de la Peña, 1999; Howard et al., 2021), e pela desigualdade de Ville (1939) a probabilidade de uma promoção falsa em qualquer instante é ≤ α/p por candidato *e por episódio de teste*."
Formulações derivadas: §8 ("Promoções têm erro tipo I controlado por episódio de teste"), D4 ("Promoção: teste com erro tipo I controlado por episódio") e §11.1 ("nenhuma promoção falsa em 2 milhões de passos nulos").

**O que o texto deixa implícito.** Seja \(z_t = e_t\,\varphi_t\), com \(e_t = y_t - \hat y^S_t\) o erro do especialista S **sem** o candidato e \(\varphi_t\) o regressor do candidato, previsível. A mistura gaussiana de \(\exp(\lambda S_t - \lambda^2 Q_t/2)\) só é supermartingale se, sob a hipótese nula, a distribuição condicional de \(z_t\) dado o passado for simétrica em torno de zero (de la Peña, 1999). Em particular, é preciso que \(\mathbb E[z_t \mid \mathcal F_{t-1}] = 0\). Como \(\mathbb E[z_t \mid \mathcal F_{t-1}] = \varphi_t\,(\mu_t - \hat y^S_t)\), onde \(\mu_t\) é a média condicional verdadeira de \(y_t\), a condição exige que **S já seja o preditor correto sem o candidato** (e que o ruído seja condicionalmente simétrico). A escolha de τ não é o problema: τ é fixado no início de cada episódio e fica constante durante ele.

**Texto corrigido (§5.3):**
> "Seja H₀ a hipótese de que, sem o candidato, o especialista S já fornece a média condicional correta de \(y_t\) e o ruído é condicionalmente simétrico. Sob H₀, \(M_t\) é supermartingale (de la Peña, 1999; Howard et al., 2021), e pela desigualdade de Ville a probabilidade de promover o candidato em algum instante do episódio é ≤ α/p. **Fora de H₀** (átomos verdadeiros ainda ausentes, pesos em convergência, estrutura mal especificada), não há garantia. Nesse caso o teste mede **relevância preditiva do candidato para o resíduo atual de S**, e pode promover um átomo apenas correlacionado com a estrutura ausente."

**Consequências para a leitura dos resultados:**
- A taxa empírica de 0 promoções falsas (§11.1; 0/17 686 episódios no diagnóstico da §11.2) foi medida em nulos com **entradas independentes do alvo**, que é a situação em que H₀ vale aproximadamente. Ela não cobre o caso mal especificado.
- A promoção de um polo errado no processo com latente e de atrasos aproximados (§11.2) é o comportamento esperado de um teste de relevância preditiva fora de H₀, e não uma violação da garantia.
- Uma promoção deve ser lida como "este termo melhora a previsão dado o modelo atual", não como "este termo é estrutura verdadeira do processo". Isso vale para o registro do ciclo de vida e para as explicações nomeadas.
- Uma demonstração formal da propriedade de e-process sob a filtração efetiva do código (portões previsíveis, pesos NLMS em adaptação, σ̂² estimado) **não foi feita**. Construções com hipóteses verificáveis para coeficientes de regressão existem na literatura (Lindon et al., JASA 2026; Pérez-Ortiz et al., Annals of Statistics 2024).

**Formulações derivadas corrigidas:**
- §8 e D4: "Promoções têm erro tipo I controlado por episódio **sob H₀ (§5.3)**; fora dela, indicam relevância preditiva."
- §11.1: "nenhuma promoção falsa em 2 milhões de passos nulos **com entradas independentes do alvo**."

## E2 — Triagem e validade do teste (esclarecimento)

A §5.3 não explica por que selecionar candidatos pela triagem não enviesa o teste. Acrescentar:
> "A triagem só decide **quando** um candidato começa a ser testado. Esse instante depende apenas do passado (é um tempo de parada). Ao começar, as estatísticas do teste (S, Q e o contador de amostras) partem de zero, o escore de triagem do candidato é zerado, e nenhum dado usado na triagem entra no martingale. Portanto, a validade de cada episódio depende apenas de E1, e não do processo de seleção."

## E3 — Memória M, modelo airline e Holt-Winters (correção)

**Textos atuais:**
- D1: "forma online do modelo airline".
- D3: "⇔ incremento sazonal previsto pelo modelo airline SARIMA(0,1,1)(0,1,1)s ⇔ estado sazonal do Holt-Winters".
- §5.2 (i): "o perfil \(G\) com \(a=0{,}1\) é exatamente isso com Θ = 0,9, e coincide com o estado sazonal do Holt-Winters".
- §10.1: "uma forma online do modelo airline / Holt-Winters".
- §15: "perfil sazonal (Θ = 0,9 no modelo airline)".
- `ARQUITETURA_V051.md` §4: "forma online e linear nos parâmetros da função de previsão do modelo airline"; "é também o estado sazonal do Holt-Winters".

**Problema.** Nenhuma equivalência foi demonstrada entre as features de M e a função de previsão do airline SARIMA(0,1,1)(0,1,1)ₛ. Também não há equivalência genérica entre o airline e o Holt-Winters aditivo: o Holt-Winters aditivo corresponde a um ARIMA restrito, do tipo (0,1,s+1)(0,1,0)ₛ, e só coincide com o airline sob condições especiais.

**Texto corrigido:**
> "O perfil \(G\) é uma média exponencial (fator 0,9 por ciclo) dos incrementos observados na mesma fase em ciclos anteriores. É **inspirado** na suavização sazonal do Holt-Winters e na componente sazonal do modelo airline, e cumpre papel análogo ao do 'ciclo recorrente' do CycleNet. **Não é equivalente** a nenhum desses modelos. M é uma memória linear nos parâmetros, com features inspiradas nesses modelos clássicos e pesos aprendidos por NLMS."

- D1: "memória sazonal inspirada no airline / Holt-Winters".
- D3: "inspirado no incremento sazonal do airline e no estado sazonal do Holt-Winters (analogia, não equivalência)".
- §15: "perfil sazonal (fator 0,9 por ciclo; análogo, não igual, ao Θ do airline)".

A comparação empírica com o airline ajustado por máxima verossimilhança (§10.2) permanece válida: ela compara desempenho, não depende da equivalência.

## E4 — Reversão à média e suavização exponencial simples (correção)

**Textos atuais:**
- §5.2 (ii): "a feature de reversão à média produz \(y_{t-1}+w_1(m-y_{t-1})\), que é a suavização exponencial simples com constante aprendida".
- D3: "reversão à média ⇔ suavização exponencial simples com α aprendido".
- `ARQUITETURA_V051.md`: "reproduz a suavização exponencial simples com α aprendido".

**Problema.** A previsão resultante é \((1-w_1)\,y_{t-1} + w_1\,m_{t-1}\), em que \(m\) é uma média exponencial com taxa **fixa** 0,01. Isso é uma mistura aprendida entre o último valor e uma média lenta de taxa fixa. Na suavização exponencial simples, a própria taxa de suavização é aprendida. As duas famílias só coincidem nos extremos (w₁ = 0: persistência).

**Texto corrigido:**
> "A feature de reversão à média produz \((1-w_1)\,y_{t-1}+w_1\,m_{t-1}\): uma mistura aprendida entre o último valor e uma média exponencial lenta (taxa fixa 0,01). Ela aproxima o efeito de um nível local suavizado, na linha de Muth (1960), mas **não é** a suavização exponencial simples com constante aprendida."

## E5 — Controle de erro ao longo do fluxo (esclarecimento)

A especificação já declara que o controle é "por teste, não para o fluxo inteiro" (§5.3, §14). Acrescentar:
> "Como um candidato pode voltar ao dicionário e ser retestado com o mesmo nível α/p, o número de oportunidades de promoção falsa cresce com o tempo, e não há limite para a taxa de erro acumulada ao longo da vida do sistema. Existem métodos que controlam o erro **através** de hipóteses que chegam e evoluem ao longo do tempo: alpha-investing (Foster & Stine, 2008), e-LOND (Xu & Ramdas, 2024), testes múltiplos com e-processes (Tavyrikov, Goeman & de Heide, 2026) e *dynamic e-closure* (de Heide, 2026). A v0.51 não os usa."

## E6 — Posicionamento da parte estrutural (esclarecimento)

**Texto atual (§12):** "É a parte mais interessante do ponto de vista científico e conecta-se com a área de inferência sempre válida (Ramdas et al., 2023)."

**Acrescentar:**
> "Seus componentes têm precedentes diretos. Seleção estatística de variáveis em fluxo, com controle de falsas descobertas: alpha-investing e IIC (Zhou et al., 2005; Ungar et al., 2005). Estruturas criadas, testadas em paralelo e substituídas ou podadas em fluxo: CVFDT (Hulten et al., 2001), FIMT-DD e AMRules (Ikonomovska et al., 2011; Almeida, Ferreira & Gama, 2013). Testes sempre válidos para coeficientes de regressão: Lindon et al. (2026). Bancos de modelos dinâmicos ponderados por inovações: Magill (1965). O que a v0.51 reúne é uma combinação específica desses elementos sob orçamento de custo, sem afirmação de novidade."

---

## Referências acrescentadas por esta errata

- de la Peña, V. H. (1999). A general class of exponential inequalities for martingales and ratios. *Annals of Probability* 27(1), 537–564.
- Lindon, M., Ham, D. W., Tingley, M., Bojinov, I. (2026). Anytime-valid inference in linear models and regression-adjusted causal inference. *Journal of the American Statistical Association*. arXiv:2210.08589.
- Pérez-Ortiz, M. F., Lardy, T., de Heide, R., Grünwald, P. (2024). E-statistics, group invariance and anytime-valid testing. *Annals of Statistics* 52(4), 1410–1432.
- Foster, D. P., Stine, R. A. (2008). α-investing: a procedure for sequential control of expected false discoveries. *JRSS B* 70(2), 429–444.
- Xu, Z., Ramdas, A. (2024). Online multiple testing with e-values. *AISTATS*, PMLR 238.
- Tavyrikov, Y., Goeman, J. J., de Heide, R. (2026). Carefree multiple testing with e-processes. *Electronic Journal of Statistics*. arXiv:2501.19360.
- de Heide, R. (2026). Dynamic e-closure for online hypotheses with any-time-valid evidence. arXiv:2608.09927.
- Zhou, J., Foster, D. P., Stine, R. A., Ungar, L. H. (2005/2006). Streaming feature selection using alpha-investing. *KDD 2005*; Streamwise feature selection, *JMLR* 7.
- Ungar, L. H., Zhou, J., Foster, D. P., Stine, R. A. (2005). Streaming feature selection using IIC. *AISTATS*, PMLR R5, 357–364.
- Hulten, G., Spencer, L., Domingos, P. (2001). Mining time-changing data streams. *KDD*, 97–106.
- Ikonomovska, E., Gama, J., Džeroski, S. (2011). Learning model trees from evolving data streams. *Data Mining and Knowledge Discovery* 23(1), 128–168.
- Almeida, E., Ferreira, C., Gama, J. (2013). Adaptive model rules from data streams. *ECML PKDD*, LNCS 8188, 480–492.
- Magill, D. T. (1965). Optimal adaptive estimation of sampled stochastic processes. *IEEE Transactions on Automatic Control* 10(4), 434–439.

---

## English summary (for readers of the EN specification)

- **E1 (correction):** the promotion guarantee (≤ α/p per candidate and test episode) holds under H₀ = "without the candidate, expert S already gives the correct conditional mean and the noise is conditionally symmetric". Outside H₀ there is no guarantee, and a promotion means *predictive relevance for S's current residual*, not true structure. The empirical 0 false promotions were measured on nulls with inputs independent of the target. A formal proof under the code's actual filtration was not done.
- **E2 (clarification):** screening only decides when a test starts (a stopping time); test statistics start from zero and screening data never enter the martingale.
- **E3 (correction):** memory M and its profile G are *inspired by* (not equivalent to) the airline SARIMA(0,1,1)(0,1,1)ₛ and Holt-Winters models; additive Holt-Winters is not generically the airline model.
- **E4 (correction):** the mean-reversion feature gives \((1-w_1)y_{t-1}+w_1 m_{t-1}\) with a fixed-rate mean (0.01); it is not simple exponential smoothing with a learned constant.
- **E5 (clarification):** error control is per episode; with re-testing, lifetime error is unbounded. Global online multiple-testing methods exist (alpha-investing, e-LOND, e-processes, dynamic e-closure) and are not used in v0.51.
- **E6 (clarification):** the structural components have direct precedents (alpha-investing/IIC, CVFDT, FIMT-DD/AMRules, anytime-valid regression tests, multiple-model estimation); v0.51 is a specific, cost-bounded combination with no novelty claim.
