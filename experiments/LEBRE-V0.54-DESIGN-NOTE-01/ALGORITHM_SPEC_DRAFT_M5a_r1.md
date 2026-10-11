# LEBRE v0.54 — Rascunho 1 da especificação da M5a

**Data:** 10/10/2026 · **Status:** aprovado pelo responsável pelo projeto para medição (M5A_E2); sem resultado ainda.
**Antecedente:** rascunho 0, revisão a (`ALGORITHM_SPEC_DRAFT_M5a.md`), medido em M5A_E1 (LEBRE Lab, resultado
`analises/M5A_E1_RESULTADO.md`, commit `642afd1`): **não aceito** (critério 1 reprovado em A01 e C03; 2, 3a, 3b e 5
atendidos). Contagem: este é o 2º desenho da M5a.

## O que muda em relação ao rascunho 0 (e por quê)

1. **Troca da seleção de entradas durante o sono não desperta a M1.** O protótipo do rascunho 0 despertava a M1 nessa
   troca, regra que **não estava no texto do rascunho 0** (desvio declarado no resultado do M5A_E1) e que causou os
   despertares em A01 (3 de 3 por série) e em A12 (36 de 39). Agora, se a seleção muda enquanto a M1 dorme, o AdaHedge
   recomeça (como na v0.53, para o especialista novo) e a estatística de despertar também recomeça; a M1 continua dormindo
   e só desperta pela estatística. No modo ativo nada muda (a troca reinicia o AdaHedge, com sombra, como na v0.53).
2. **Critério 1 restrito a séries com pelo menos 10.000 passos.** Em séries curtas, a regra (sombra de 100 atualizações e
   2.000 alvos com peso baixo antes de dormir) deixa pouco tempo de sono (C03: ~1.100 passos em ~4.000). A regra **não**
   muda para passar no critério; o custo nas séries curtas passa a ser só reportado. Decisão do responsável pelo projeto.

Todo o resto do rascunho 0 vale sem alteração: constantes (ω_min = 10⁻³, D = 2.000, J = 8, regressão dormente a cada 64,
taxa 0,01, g_min = 0,05, 100 amostras), modo ativo idêntico à v0.53, saída L' = L no sono, despertar com AdaHedge
reiniciado e sombra.

## Critérios (fixados antes da medição M5A_E2)

1. **Custo:** em A01 (30 séries, 20.000 passos) e A05 (20 séries, 30.000 passos), custo médio da M1 na v0.54 ≤ 0,25 × o
   da v0.53, em cada cenário; C03 e as demais séries curtas, só reportadas.
2. **Sem piora:** 64 famílias do E20, limite superior do IC 95% da razão v0.54 ÷ v0.53 ≤ 1,01; nenhuma previsão não
   finita.
3. **3a:** troca de regime (mesmo gerador do M5A_E1), sementes novas 20261111 a 20261130; MSE depois da troca ≤ 1,02 × v0.53.
4. **3b:** útil → inútil → útil (mesmo gerador), sementes novas 20261131 a 20261150; despertar condicional em ≥ 90% das
   séries na condição (inconclusivo com menos de 5); MSE do último trecho ≤ 1,02 × v0.53.
5. **Identidade:** onde a M1 nunca dormiu, previsões idênticas às da v0.53.

Bootstrap: semente 20261061. Todas as sementes conferidas como não usadas no código e nos documentos dos três repositórios.
