# PRA-02 — Prior art da LEBRE v0.51 (foco na parte estrutural)

**Data:** 25/09/2026 · **Objeto:** LEBRE v0.51 congelada (`LEBRE-V0.51-FREEZE-01`) · **Antecessor:** PRA-01 (v0.1, 19/09/2026)
**Pergunta:** algum componente da v0.51 — ou a combinação — é distinto da literatura? Em particular, a descoberta estrutural por testes tem espaço para uma afirmação de novidade?

---

## 1. Resposta curta

- **Nenhum componente isolado da v0.51 é novo.** Cada peça tem precedente direto: o teste de promoção (martingales de mistura / t-teste sequencial para coeficientes), os portões previsíveis (continuação opcional, excitação persistente, *sleeping experts*), a remoção por CUSUM, o latente por banco de polos, a memória airline online, a média dinâmica de modelos e o quantil adaptativo.
- **A combinação continua `POSSIBLY_DISTINCT`, mas estreita:** não encontramos um previsor online que descubra atrasos esparsos e um estado latente por **testes sempre válidos**, sob um orçamento de ~100 FP/passo, combinado com uma memória sazonal e com explicação exata. O parente mais próximo em espírito é a família "estrutura governada por limites estatísticos em fluxo" (FIMT-DD, AMRules, alpha-investing), que já faz crescer e podar estrutura online com critérios estatísticos.
- **Num ponto a literatura já está à frente da LEBRE.** Trabalhos de 2025–2026 (SAVA; *dynamic e-closure*) controlam o erro **através** de hipóteses que chegam ao longo do tempo (FDR/FSR simultâneo). A LEBRE controla só **por episódio de teste**. Isso é ao mesmo tempo uma ameaça (a parte estatística não é a fronteira) e uma oportunidade de melhoria com respaldo teórico.
- **Conclusão para governança:** `NOVELTY_CLAIM_READY` continua **NO**. Uma eventual contribuição seria de **integração de engenharia**, e só se sustentaria com evidência em dados reais guiados por entradas, que hoje não existe.

## 2. Afirmações auditadas

| ID | Componente da v0.51 | Veredito | Precedentes mais próximos |
|---|---|---|---|
| C1 | Promoção de átomos (atrasos, latente, acionamento) por martingale de mistura auto-normalizado, com limiar log(p/α) | **KNOWN_TOOL / APPLICATION_POSSIBLY_DISTINCT** | Howard et al. 2021; de la Peña 1999; **Lindon et al. (t-teste e F-teste sequenciais para coeficientes de regressão, JASA 2026)**; alpha-investing (Zhou et al. 2006) |
| C2 | Portões previsíveis de evidência (silêncio, quarentena, dormência) | **KNOWN** | Continuação opcional (Ramdas et al. 2023); excitação persistente / conjuntos de excitação (Leung, Hota & Paré 2024); *sleeping experts* (Freund et al. 1997); hipóteses dormentes (de Heide 2026) |
| C3 | Remoção por CUSUM com aluguel de parcimônia | **KNOWN (variante)** | CUSUM com deriva k (Page 1954); poda por Page-Hinkley (FIMT-DD 2011; AMRules 2016); MDL (Rissanen 1978) |
| C4 | Estado latente por filtro de inovações com banco de polos fixo + acionamento | **KNOWN_COMPONENTS** | Preditor de Kalman em forma de inovações; bases ortonormais Laguerre/Kautz e seleção de polos (ARX-Laguerre online, Int. J. Control 2013; arXiv 2512.21096) |
| C5 | Triagem barata + poucas vagas de teste | **KNOWN (padrão)** | *Screening* seguido de teste (OSFS/SAOLA; Hoeffding trees avaliando poucos candidatos) |
| C6 | Memória M = forma online da função de previsão airline (NLMS sobre diferenças) | **KNOWN** | Box & Jenkins; Holt-Winters; ARIMA online (Liu et al., AAAI 2016); normalização do NLinear |
| C7 | Combinação S/M por média dinâmica de modelos | **KNOWN** | Raftery, Kárný & Ettler 2010; DMA para seleção de preditores (Koop & Korobilis 2012) |
| C8 | Intervalo por rastreamento de quantil com cadência de 8 | **KNOWN (a cadência é variante de custo, com defeito documentado)** | Gibbs & Candès 2021; Angelopoulos et al. 2023 |
| C9 | Integração: ciclo de vida estrutural por testes sempre válidos + memória sazonal + DMA + explicação exata, a ~100–150 FP | **POSSIBLY_DISTINCT (estreito)** | Ver §3; nenhum trabalho encontrado reúne todos os elementos |

## 3. Os dez precedentes mais próximos

| # | Trabalho | O que faz | Proximidade | Diferença para a LEBRE |
|---|---|---|---|---|
| 1 | **Lindon, Ham, Tingley & Bojinov** — Anytime-valid linear models (arXiv 2022; JASA 2026) | t-teste e F-teste sequenciais e sequências de confiança para coeficientes de regressão, em forma fechada | **ALTA para C1** | Voltado a experimentos A/B, sem descoberta de atrasos nem ciclo de vida; trata a variância de forma invariante (a LEBRE usa σ̂² plug-in) |
| 2 | **Zhou, Foster, Stine & Ungar** — Streamwise feature selection / alpha-investing (KDD 2005; JMLR 2006) | Considera variáveis candidatas em sequência e ajusta o limiar de entrada com garantia do tipo FDR | **ALTA (conceito)** | Cada variável é avaliada uma vez, com p-valor em amostra fixa; não há remoção nem dinâmica temporal |
| 3 | **Ikonomovska, Gama & Džeroski** — FIMT-DD (2011) | Árvore de regressão online: cresce por limite de Hoeffding e poda/substitui por Page-Hinkley | **ALTA (ciclo de vida)** | Estrutura de partições, não atrasos/latentes; sem controle sempre válido; sem memória sazonal |
| 4 | **Duarte, Gama & Bifet** — AMRules (TKDD 2016) | Regras de regressão em fluxo: expande por Hoeffding, poda por Page-Hinkley, detecta outliers | **ALTA (ciclo de vida)** | Idem; a detecção de outliers é análoga à quarentena |
| 5 | **Ren et al.** — Online sparse Bayesian identification of nonlinear time-varying systems (arXiv 2601.10379, 2026) | Identificação esparsa online com suporte ativo revisável por evidência posterior | **MÉDIA-ALTA** | Bayesiano, sem garantia de erro tipo I; identificação, não previsão; custo não reportado |
| 6 | **Fu & Zhao** — Recursive sparse parameter identification (arXiv 2505.00323, 2025) | Algoritmo recursivo com convergência do conjunto esparso sob excitação não persistente | **MÉDIA** | Garantia assintótica de conjunto, sem controle por teste; sem latente; sem previsão sazonal |
| 7 | **Yao, Gang & Sun** — SAVA (arXiv 2512.12244, 2025–26) | Alpha-investing seguro e sempre válido para fluxos "duplamente sequenciais" (tarefas novas chegando, cada uma com dados em fluxo) | **MÉDIA (estatística)** | Genérico; é exatamente a garantia de família que falta à LEBRE |
| 8 | **de Heide** — Dynamic e-closure (arXiv 2608.09927, 2026) | FDR simultâneo sob parada, com hipóteses que chegam ao longo do tempo; hipóteses dormentes | **MÉDIA (estatística)** | Teoria sem algoritmo de custo fixo; oportunidade de melhoria |
| 9 | **Koop & Korobilis** — Forecasting inflation using DMA (IER 2012) | DMA/DMS com esquecimento sobre subconjuntos de preditores | **MÉDIA (C7)** | Combina modelos, sem testar estrutura; custo exponencial no número de preditores |
| 10 | **Liu, Hoi, Zhao & Sun** — Online ARIMA (AAAI 2016) | Parâmetros ARIMA aprendidos online com garantia de arrependimento | **MÉDIA (C6)** | Sem estrutura por entradas; a memória M da LEBRE é um caso particular dessa ideia |

**Outros relevantes:** R-SINDy (IEEE, 2024), sobre descoberta de equações online com LASSO recursivo; Etter & Stearns (1981), sobre estimação adaptativa de atraso; ARX-Laguerre online (2013), sobre bancos de polos. No produto: **TinyCast** (arXiv 2608.15767, 2026), um previsor zero-shot de 146 mil parâmetros em INT8 para dispositivos embarcados, sem ajuste por sinal (não aprende online); e sistemas fuzzy linguísticos com adaptação online em TinyML (MDPI AI, 2025), que são explicáveis e embarcados.

## 4. Onde a LEBRE fica, honestamente

1. **Estatística.** O teste de promoção é uma aplicação correta de ferramentas conhecidas. A literatura atual (Lindon; SAVA; e-closure) é mais sofisticada: trata a variância incômoda de forma exata e controla o erro através de hipóteses que chegam ao longo do tempo. Não há contribuição estatística a reivindicar.
2. **Ciclo de vida estrutural em fluxo.** A ideia de "crescer por teste e podar por detector de mudança" existe desde FIMT-DD/AMRules (limites de Hoeffding + Page-Hinkley). O que a LEBRE acrescenta é o **tipo de estrutura** (atrasos e estado latente com significado físico), o **teste sempre válido** no lugar do Hoeffding e o **orçamento explícito**. Essa distinção é real, mas estreita, e a evidência empírica dela é hoje sintética e parcial (falha com latente acionado).
3. **Previsão.** A memória M e o combinador são clássicos. O valor está em engenharia: sem ajuste por série, ~120 FP, intervalo e explicação.
4. **Produto embarcado.** Há concorrência recente em previsão embarcada (TinyCast) e em modelos explicáveis adaptativos embarcados (fuzzy em TinyML). O diferencial da LEBRE seria aprender online a ~100 FP com explicação estrutural; nenhum dos dois faz exatamente isso, mas a comparação precisaria ser feita.

## 5. Implicações para o próximo passo

**Governança:** `NOVELTY_CLAIM_READY = NO` (mantido). A formulação mais forte hoje defensável é:
> "Integração, sob orçamento de ~100–150 FP/passo, de um ciclo de vida estrutural governado por testes sempre válidos (atrasos esparsos e estado latente) com uma memória sazonal clássica e média dinâmica de modelos; contribuição de engenharia, com evidência estrutural apenas sintética."

**Para uma v0.52 com respaldo na literatura**, candidatos ordenados por respaldo × impacto:
1. **Controle de erro através de hipóteses que chegam ao longo do tempo** (e-BH online / SAVA / e-closure), no lugar de α/p por episódio. Tem respaldo teórico direto, custo provavelmente baixo e resolve uma limitação declarada.
2. **Teste de coeficiente com variância tratada de forma invariante** (Lindon et al.). Substitui o σ̂² plug-in e pode melhorar o poder no caso de vários atrasos.
3. **Latente**: revisão/troca do polo, ou base de Laguerre com polo adaptativo (literatura ARX-Laguerre), atacando a falha do latente acionado.
4. **Higiene** (sem questão de novidade): quantil acumulado e ε na memória.

**Comparadores que faltam na avaliação**, se a parte estrutural for defendida: alpha-investing, FIMT-DD/AMRules (disponíveis em bibliotecas de fluxo como a River), RLS/LMS esparso com suporte e o teste de Lindon como substituto direto do teste da LEBRE. E, antes de tudo, **dados reais guiados por entradas**.

## 6. Limitações desta auditoria

- Busca em **um único mecanismo web**, só em inglês; não cobre literatura chinesa de identificação esparsa, patentes nem bases pagas (IEEE Xplore/Scopus) de forma sistemática.
- **Leitura de resumos**, não de textos completos. Os vereditos sobre os trabalhos 1, 3, 4, 7 e 8 devem ser confirmados com leitura integral antes de qualquer afirmação pública.
- Busca adversarial feita por quem projetou o sistema: existe viés de confirmação possível. Recomenda-se uma revisão independente dos cinco mais próximos.
- A PRA-01 continua valendo para as partes herdadas da v0.1 (redes evolutivas, RAN/MRAN, filtragem esparsa).

## Referências (URLs verificadas nesta sessão)

- Lindon et al. — [arXiv 2210.08589](https://arxiv.org/abs/2210.08589) · [JASA 2026](https://www.tandfonline.com/doi/full/10.1080/01621459.2026.2692052) · [avlm (CRAN)](https://cran.r-project.org/web/packages/avlm/avlm.pdf)
- Zhou, Foster, Stine & Ungar — [JMLR 7 (2006)](https://www.jmlr.org/papers/volume7/zhou06a/zhou06a.pdf) · [KDD 2005](https://dl.acm.org/doi/10.1145/1081870.1081914)
- FIMT-DD — [Regression Trees from Data Streams with Drift Detection](https://www.researchgate.net/publication/221612862_Regression_Trees_from_Data_Streams_with_Drift_Detection)
- AMRules — [TKDD 2016](https://dl.acm.org/doi/10.1145/2829955)
- Ren et al. 2026 — [arXiv 2601.10379](https://arxiv.org/abs/2601.10379)
- Fu & Zhao 2025 — [arXiv 2505.00323](https://arxiv.org/abs/2505.00323)
- Leung, Hota & Paré 2024 — [arXiv 2406.10349](https://arxiv.org/abs/2406.10349)
- SAVA (Yao, Gang & Sun) — [arXiv 2512.12244](https://arxiv.org/abs/2512.12244)
- de Heide 2026 — [arXiv 2608.09927](https://arxiv.org/abs/2608.09927)
- Online closed testing with e-values — [arXiv 2407.15733](https://arxiv.org/html/2407.15733v1)
- Koop & Korobilis 2012 — [Forecasting Inflation Using DMA](http://eprints.gla.ac.uk/59746/1/59746.pdf)
- Liu et al. 2016 — [Online ARIMA (AAAI)](https://ojs.aaai.org/index.php/AAAI/article/view/10257)
- R-SINDy — [IEEE 10753612](https://ieeexplore.ieee.org/document/10753612/)
- ARX-Laguerre online — [Int. J. Control 86(3)](https://www.tandfonline.com/doi/full/10.1080/00207179.2012.732710) · seleção de polos: [arXiv 2512.21096](https://arxiv.org/pdf/2512.21096)
- Etter & Stearns / estimação de atraso — [visão geral (Springer)](https://link.springer.com/chapter/10.1007/1-4020-7769-6_8)
- Granger sequencial — [arXiv 2303.17916](https://arxiv.org/abs/2303.17916) · [arXiv 2606.22230](https://arxiv.org/abs/2606.22230)
- TinyCast — [arXiv 2608.15767](https://arxiv.org/abs/2608.15767) · fuzzy em TinyML — [MDPI AI 6(12):325](https://www.mdpi.com/2673-2688/6/12/325)
