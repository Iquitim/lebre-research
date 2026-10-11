# LEBRE v0.54 — Rascunho 2 da especificação da M5a

**Data:** 10/10/2026 · **Status:** aprovado pelo responsável pelo projeto para medição (M5A_E3); sem resultado ainda.
**Antecedentes:** rascunho 0, revisão a (M5A_E1: não aceito; critério 1 em A01 e C03) e rascunho 1 (M5A_E2, LEBRE Lab
`analises/M5A_E2_RESULTADO.md`, commit `3f9e6f3`: não aceito; critério 1 em A01, 0,264, e critério 2 em YB03, limite
superior 1,0216). Contagem: este é o 3º desenho da M5a.

## A tensão que os dois desenhos revelaram

Despertar a M1 quando a seleção de entradas muda durante o sono (protótipo do rascunho 0) custou caro em A01, onde as
entradas escolhidas mudam a cada nova seleção sem ganho; não despertar (rascunho 1) custou precisão em YB03 (série NO2:
+5,0%), onde o especialista novo era útil, mas com vantagem pequena demais para a estatística de despertar (limiar de 5%,
1 amostra a cada 8).

## O que muda em relação ao rascunho 1

**Teste curto do especialista novo.** Se a seleção de entradas muda enquanto a M1 dorme, a M1 desperta em **teste**: modo
ativo, AdaHedge reiniciado com sombra de N_MIN = 100 atualizações (como na v0.53 para um especialista novo). Durante o
teste, ela volta a dormir depois de **D_TESTE = 500** alvos aprendidos seguidos com ω < 10⁻³ (em vez de D = 2.000). Se,
depois da sombra, ω chegar a 10⁻³ ou mais em algum passo, o teste termina e valem as regras normais (D = 2.000). O teste
também termina quando a M1 volta a dormir.

Tudo o mais do rascunho 1 vale: constantes (ω_min = 10⁻³, D = 2.000, J = 8, regressão dormente a cada 64, taxa 0,01,
g_min = 0,05, 100 amostras), modo ativo idêntico à v0.53, saída L' = L no sono, despertar pela estatística com AdaHedge
reiniciado e sombra. A constante nova, D_TESTE = 500, é declarada aqui, antes de medir.

## Critérios (fixados antes da medição M5A_E3; os mesmos do rascunho 1)

1. **Custo:** A01 e A05: custo médio da M1 na v0.54 ≤ 0,25 × o da v0.53, em cada cenário; C03 só reportado.
2. **Sem piora:** 64 famílias do E20, limite superior do IC 95% ≤ 1,01; nenhuma previsão não finita.
3. **3a:** sementes 20261152 a 20261171; MSE depois da troca ≤ 1,02 × v0.53.
4. **3b:** sementes 20261172 a 20261191; despertar condicional em ≥ 90% das séries na condição (inconclusivo com menos
   de 5); MSE do último trecho ≤ 1,02 × v0.53.
5. **Identidade:** onde a M1 nunca dormiu, previsões idênticas às da v0.53.

Bootstrap: semente 20261062. Sementes conferidas como não usadas no código e nos documentos dos três repositórios.

## Decisão depois da medição M5A_E3 (10/10/2026)

Resultado (LEBRE Lab, `analises/M5A_E3_RESULTADO.md`, commit `d4f6cac`): o rascunho 2 reprovou só no critério 1, em A01
(razão 0,373; meta ≤ 0,25), e atendeu a todos os critérios de precisão e identidade (pior família: YB03, limite superior
1,0043), ao 3a e ao 3b. **Decisão do responsável pelo projeto:** a meta de 75% de corte foi uma estimativa feita antes de
se conhecer o custo dos períodos ativos (sombra, 2.000 alvos antes de dormir e testes curtos na reseleção); ela passa a
ser **corte de pelo menos 60% do custo da M1 (razão ≤ 0,40) em A01 e A05**. Esta revisão foi decidida **depois** de três
medições no banco de desenvolvimento e por isso não serve como evidência de aprovação: o rascunho 2 vira **candidato**, e
a aceitação depende de uma validação em dados novos, com plano e critérios fixados antes, usada uma única vez.
