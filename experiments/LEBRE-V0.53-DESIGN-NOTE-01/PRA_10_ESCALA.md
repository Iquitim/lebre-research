# PRA-10: combinação com garantia na escala do erro quadrático (perdas sem limite, caudas pesadas)

**Data:** 09/10/2026. **Motivo:** a validação 4 (LEBRE Lab, `analises/M1_VAL4_RESULTADO.md`) e os diagnósticos E13 a E15
mostraram uma assinatura comum às falhas da M1 e da M2: o (A,B)-Prod decide e garante em **perda recortada** em [0, 1],
enquanto o critério é o **MSE**; poucos passos extremos dominam o MSE (choques de câmbio; nascer e pôr do sol na solar).
**Nível de verificação:** resumos e páginas dos artigos lidos; os teoremas não foram conferidos no texto completo, exceto
onde dito.

## 1. O que a literatura oferece

| Referência | O que interessa aqui |
|---|---|
| de Rooij, van Erven, Grünwald, Koolen (2014), AdaHedge (já usado na M2, candidata D) | Primeiro limite de arrependimento **sem escala** para especialistas: não precisa conhecer a faixa das perdas; o limite tem um termo de ordem menor proporcional à maior perda observada. |
| Cesa-Bianchi, Mansour, Stoltz (2007), *Improved second-order bounds for prediction with expert advice* | Limites de segunda ordem, da forma O(√(V log K) + M log K), com V a variância das perdas e M a maior perda; adaptam à escala sem conhecê-la. |
| Hazan, Kale (COLT 2008; Machine Learning 2010), *Extracting certainty from uncertainty* | Arrependimento limitado pela **variação** das perdas, em vez do número de passos. |
| Moulin, Esposito, van der Hoeven (arXiv 2506.01722, 2025-2026; preprint, sem revisão por pares indicada), *When lower-order terms dominate: adaptive expert algorithms for heavy-tailed losses* | Exatamente o nosso caso: com caudas pesadas, o termo de ordem menor (ligado à maior perda) dos métodos adaptativos **domina** o arrependimento. Propõem algoritmos com O(√(θ T log K)), θ = limite do segundo momento das perdas, sem conhecer faixa nem θ; citam melhora para perda quadrática. Comparação contra o melhor especialista, não contra uma referência fixa. |
| V'yugin, Trunov (arXiv 1808.00741; Machine Learning), *Online aggregation of unbounded losses using shifting experts with confidence* | AdaHedge + Fixed Share com perdas com sinal e **sem limite**; teste em consumo de eletricidade. |
| Alquier (ICML 2021), *Non-exponentially weighted aggregation* | Pesos não exponenciais (FTRL com φ-divergência) para perdas sem limite, às vezes com limite pior. |
| Mhammedi, Koolen, van Erven (COLT 2019), *Lipschitz adaptivity with multiple learning rates* | Squint e MetaGrad que aprendem a escala sozinhos (escala subestimada faz o método falhar; superestimada piora muito). |
| Orabona, Pál (ALT 2015; TCS), *Scale-free online learning* | Algoritmos sem escala para otimização linear online; limites inferiores no pior caso. |
| Wang, Ramdas (Stoch. Proc. Appl.; arXiv 2202.01250), *Catoni-style confidence sequences for heavy-tailed mean estimation* | Sequências de confiança **válidas a qualquer tempo** para a média com só a variância limitada (sem recorte), via função de influência de Catoni; extensão a momentos p em (1, 2]. Ferramenta natural para um e-process sobre a diferença de erro quadrático sem recortar. |
| Sani, Neu, Lazaric (2014), (A,B)-Prod; Even-Dar et al. (2008); Koolen (2013) (PRA-09) | Arrependimento constante contra um especialista fixo custa √(T log T) contra o melhor; a constante vale **na escala das perdas limitadas**. |

## 2. O que os dados dizem (E15, LEBRE Lab `diagnosticos/E15_RESULTADO.md`)

Fração do erro quadrático total da referência que vem do **maior passo isolado**: até 25,9% (baht 1990-1999), 23,9%
(petróleo em nível), 17,4% (rúpia do Sri Lanka), 10-12% (vários índices de inflação); 0,2-0,9% nas marés, exceto Point
Reyes (3%). Em 32 séries o maior passo passa de 5% do total.

## 3. Consequência (argumento elementar, nosso, não citado)

Uma garantia contra a referência R do tipo "arrependimento <= c × maior diferença de perda de um passo" é o que a
literatura entrega para perdas sem limite (o termo de ordem menor). Na escala relativa do critério, isso vira
"excesso <= c × fração do maior passo". Se um único passo é 26% do total, **nenhum combinador online que se afaste de R
antes desse passo tem garantia de excesso <= 1%**: num passo de choque, a diferença de perda entre a previsão e R é da ordem
de |previsão − R| × |y − R|, e o choque não é previsível. Há duas saídas honestas: (a) só se afastar de R com evidência
robusta a caudas pesadas, sabendo que isso reduz o ganho nas séries em que L é melhor; (b) reconhecer que a meta de 1% não
é garantível nessas séries e defini-la a partir do que é atingível (como foi feito com a régua por decidibilidade).

## 4. Direções para os próximos rascunhos

1. **M1 (combinação do especialista com a v0.52):** trocar o Prod com perda recortada por agregação na **própria escala do
   erro quadrático** (AdaHedge já é sem escala; candidatos mais robustos: segunda ordem, ou o de Moulin et al.). Em
   Horizonte o erro do especialista é sistemático (todo dia, no nascer e pôr do sol), não raro: qualquer agregação no erro
   quadrático sem recorte o detectaria. Especialista: a regressão conjunta do E14 (alvo defasado de 1 e 2 passos e as
   entradas no instante t, a cada passo; nas marés empata com o comparador completo a ~280 FP).
2. **M2:** afastar-se de R só com evidência na escala do erro quadrático, robusta a caudas pesadas (sequências de confiança
   tipo Catoni, Wang e Ramdas), em vez do recorte. Prever no desenho o custo dessa robustez nas séries em que L é melhor.
3. **Critério 1 da M2 nas séries dominadas por choques:** decisão do responsável pelo projeto, **antes** de qualquer nova
   medição (ver seção 3).

## 5. Decisão (09/10/2026)

O responsável pelo projeto escolheu a saída por decidibilidade para o critério 1: séries em que o maior passo isolado é
mais de 5% do erro total da referência ficam "indecidíveis" no critério 1, só em medições futuras (adendo em
`M2_CANDIDATA_D.md`). As direções 1 e 2 da seção 4 continuam necessárias: Portland (maior passo 0,26%) falhou sem choque
nenhum.
