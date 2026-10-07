# PRA-08 — Literatura para acompanhar o melhor previsor quando ele muda (falha do rascunho 2 em séries curtas)

**Data:** 08/10/2026. Lido no texto original (PDF) quando indicado; o resto está marcado.

## 1. O problema

O rascunho 2 da M2 (AdaHedge, FlipFlop) resolveu C05 mas falhou na família de séries curtas por causa de B02: nos
primeiros passos a LEBRE ainda não aprendeu o nível da carga, acumula um déficit enorme de perda quadrática, e pesos que
tratam todo o passado igualmente levam centenas de passos para recuperá-lo. Duas causas juntas:

1. **Memória total:** o arrependimento garantido é contra o melhor previsor **no período inteiro**, não no período
   recente.
2. **Escala:** a perda quadrática varia em ordens de grandeza ao longo da série (erros iniciais de milhares de MW contra
   centenas depois), e o AdaHedge só é invariante a uma escala global.

## 2. Literatura

| Referência | Lido | O que diz | Relação |
|---|---|---|---|
| Adamskiy, Koolen, Chernov e Vovk (2016). A closer look at adaptive regret. *JMLR* 17(23):1–21 | PDF, seções 1–4.1 | Os dois métodos intuitivos de arrependimento adaptativo (especialistas que "acordam" em cada instante; reinícios, Hazan e Seshadhri) **são o Fixed Share** com taxa de troca variável (Lema 2, Lema 3). Arrependimento adaptativo exato do Fixed Share em [t₁, t₂] (Teorema 4). **Corolário 6: com α_t = 1/t, o arrependimento em qualquer intervalo é no máximo ln(N − 1) + ln t₂** (ln N + ln t₂ se t₁ = 1), para a perda de mistura (perda logarítmica), qualquer sequência de dados. Fixed Share é Pareto ótimo para arrependimento adaptativo (seção 4.2). Custo O(N) por passo. | Esquece o déficit inicial ao custo de ln t; sem parâmetro livre; barato. |
| Herbster e Warmuth (1998). Tracking the best expert. *Machine Learning* 32(2):151–178 (PRA-06) | não relido | Fixed Share original, taxa constante. | Origem. |
| Luo e Schapire (2015). Achieving all with no parameters: AdaNormalHedge. *COLT*, PMLR 40 | PDF, seções 1–3 e 5 | AdaNormalHedge sem parâmetros; versão "TV" com especialistas que acordam em cada instante (priori ∝ 1/τ²) dá arrependimento adaptativo ótimo. **Exige perdas em [0, 1]**; custo O(N t) por passo, ou O(N ln t) com cobertura de intervalos. | Alternativa; descartada agora por exigir escala conhecida e pelo custo (~600 FP por passo estimados). |
| Cesa-Bianchi, Gaillard, Lugosi e Stoltz (2012). Mirror descent meets fixed share (and feels no regret). *NeurIPS* 25:989–997 | resumo | Fixed Share para perdas limitadas; arrependimento de deslocamento, adaptativo, descontado. | Mesma família; exige faixa de perdas e ajuste. |
| van Erven, Grünwald e de Rooij (2012), *JRSS-B* (PRA-07) | resumo | Distribuição de troca ("switch distribution") resolve o catch-up phenomenon trocando de modelo cedo. | Versão bayesiana da mesma ideia (mistura sobre sequências de troca). |
| Gokcesu e Kozat (2022). Optimal tracking in prediction with expert advice. arXiv:2208.03708 | resumo | Acompanhamento ótimo sem conhecer horizonte nem faixa das perdas. | **Preprint**, revisão por pares não confirmada; registrado, não usado. |

## 3. O que a literatura indica

1. **Fixed Share com α_t = 1/t sobre perda logarítmica** resolve o ponto 1 com garantia exata, sem parâmetro: em
   qualquer intervalo, a saída perde no máximo ln t₂ (dois previsores) para o melhor previsor daquele intervalo.
2. **O ponto 2 (escala) desaparece na perda logarítmica** se cada previsor for tratado como uma previsão probabilística
   com a sua própria escala: N(previsão, σ²), σ² = média exponencial dos seus próprios erros quadráticos passados (só
   passado, logo previsível). A perda é (y − f)²/(2σ²) + ln σ; é invariante à escala dos dados, e o previsor que erra
   menos, de forma consistente, ganha cerca de ½ ln(MSE_outro ÷ MSE_seu) por passo. É uma escolha de modelagem
   declarada (previsão gaussiana com variância por média exponencial), não um resultado.
3. **Limite honesto:** a garantia é sobre a perda logarítmica da mistura de densidades. A saída pontual é a média da
   mistura (Σ peso × previsão); para ela não há garantia de perda quadrática equivalente. A medição no Lab decide.
