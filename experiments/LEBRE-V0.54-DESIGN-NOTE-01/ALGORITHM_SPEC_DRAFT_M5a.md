# LEBRE v0.54 — Rascunho 0 da especificação da M5a: a M1 dormente enquanto não pesa

**Data:** 10/10/2026 · **Status:** rascunho para revisão do responsável pelo projeto; sem código, sem medição.
**Base:** nota de desenho 01 da v0.54 (prioridade 1); linha de base E23 do LEBRE Lab; PRA-11.
**Ponto de partida do código:** `lebre==0.2.0` (idêntica, bit a bit, ao protótipo promovido da v0.53).

## 1. O problema, em números

A M1 combina a previsão do núcleo L com o especialista E por AdaHedge: L' = (1 − ω) L + ω E. Ela paga todo passo, pese ou
não. Contagem analítica por passo (a mesma regra de toda a LEBRE), com k = 3 + 5m variáveis e m = mín(d, 5) entradas:

| d | previsão de E e recorte | AdaHedge | regressão (RLS a cada 8 alvos) | triagem | total |
|---|---|---|---|---|---|
| 1 | 42 | 48 | 53 | 1 | 144 |
| 3 | 98 | 48 | 254 | 2 | 403 |
| 5 ou mais | 154 | 48 | 606 | 4 a 32 | 811 a 839 |

Na avaliação final da v0.53, ω terminou em zero em 70 de 104 séries; no E23, em 95 de 95. **Três quartos do custo da M1
são a atualização da regressão**, feita mesmo quando E não entra na previsão.

## 2. A regra proposta

A M1 passa a ter dois modos. Tudo usa só o passado.

**Modo ativo** — exatamente a v0.53: E previsto e AdaHedge atualizado a cada alvo observado; regressão a cada 8 alvos
aprendidos.

**Entrada no modo dormente.** Depois da sombra (AdaHedge com pelo menos N_MIN = 100 atualizações) e com E definido, se
ω < ω_min = 10⁻³ em D = 2.000 alvos aprendidos seguidos, a M1 dorme.

**Modo dormente** — a M1 continua aprendendo, mais devagar, e continua sendo avaliada:
- a saída é L' = L (ω < 10⁻³ já fazia L' diferir de L em menos de 0,1% de (E − L));
- E é calculado só nos passos de amostra: um a cada J = 8 alvos aprendidos (passo escolhido pelo contador de alvos
  aprendidos, conhecido antes da previsão);
- a regressão é atualizada a cada 8 passos de amostra (a cada 64 alvos aprendidos), com o z daquele passo;
- a triagem das entradas e a nova seleção a cada T_MAX continuam como na v0.53;
- o AdaHedge fica congelado (não recebe as perdas da amostra; ver 4.2).

**Despertar.** Nos passos de amostra, acompanha-se uma média exponencial (taxa 0,01) da melhora relativa de E sobre L,
g = ((y − L)² − (y − E)²), normalizada pela média exponencial (mesma taxa) de (y − L)². Se, com pelo menos 100 amostras desde
a entrada no modo dormente, a média normalizada passar de g_min = 0,05 (E pelo menos 5% melhor que L nas amostras
recentes), a M1 desperta: volta ao modo ativo com **AdaHedge reiniciado e nova sombra de N_MIN atualizações**, como já
acontece na v0.53 quando as entradas escolhidas mudam.

**Propriedade que decorre da regra:** enquanto a M1 nunca dorme, a v0.54 é **idêntica, bit a bit,** à v0.53. Onde a M1
pesa (as bacias e as famílias abaixo da fronteira), nada muda.

## 3. Custo

Por passo dormente: (previsão de E + recorte + perdas) ÷ 8 + regressão ÷ 64 + triagem + estatística de despertar
(~5 FP por amostra). Estimativa: 24 FP com d = 1, 57 com d = 3, 110 a 138 com d ≥ 5, isto é, **83% a 86% menos** que a M1
ativa. A contagem da implementação será auditada como na v0.53 (E21/E22).

## 4. Escolhas e justificativas

1. **Constantes declaradas, não ajustadas:** ω_min = 10⁻³, D = 2.000, J = 8, regressão dormente a cada 64, taxa 0,01,
   g_min = 0,05, 100 amostras. Ficam fixas antes de qualquer medição; se o desenvolvimento reprovar a regra, a mudança de
   constantes é um novo rascunho, registrado como tal.
2. **Por que congelar o AdaHedge no sono.** Depois de muito tempo com E pior, a diferença acumulada de perdas é tão grande
   que o AdaHedge levaria muito tempo para devolver peso a E mesmo que E passasse a ser melhor; alimentá-lo com as amostras
   não resolveria isso. O despertar usa uma estatística recente e reinicia o AdaHedge com sombra, que é o mecanismo de
   entrada que a v0.53 já validou. **Consequência a medir:** a v0.54 pode reagir mais rápido que a v0.53 a uma M1 que
   volta a ser útil (a v0.53 também carrega a diferença acumulada).
3. **Por que a saída é L e não (1 − ω) L + ω E no sono.** Com ω < 10⁻³ a diferença é desprezível, e calcular E todo passo
   é justamente o custo que se quer evitar.
4. **Risco declarado:** um despertar falso custa só o modo ativo por um tempo (a sombra protege a saída); um despertar
   tardio custa precisão nos trechos em que E já seria útil. O cenário de reativação (5.3) mede isso.

## 5. Critérios no desenvolvimento (fixados aqui, antes de medir)

1. **Custo:** onde a M1 termina com peso zero (A01, A05 e C03 do E23), custo da M1 reduzido em pelo menos 75% em relação à
   v0.53; custo total por passo reportado.
2. **Sem piora:** nas 64 famílias de desenvolvimento do E20 (as mesmas da v0.53), razão de MSE v0.54 ÷ v0.53 por família
   com limite superior do IC 95% (bootstrap de blocos pareado) ≤ 1,01; nenhuma previsão não finita.
3. **Reativação** (cenário sintético novo, sementes 5600 a 5619, conferidas como não usadas no código e nos documentos
   dos três repositórios): alvo sem dinâmica conjunta até t = 15.000
   e com dinâmica do tipo de `joint_dynamics` (AR2 + bandas de entradas) depois; no trecho depois da troca, MSE da v0.54 no
   máximo 1,02 vez o da v0.53 (média geométrica de 20 séries), e a M1 desperta em pelo menos 18 de 20 séries.
4. **Identidade:** em séries em que a M1 nunca dorme, previsões idênticas às da `lebre==0.2.0` (teste automático).

## 6. Medição

Plano no LEBRE Lab (`analises/M5A_E1_PLANO.md`), commitado antes de rodar: protótipo da v0.54 contra a `lebre==0.2.0`
nos itens 1 a 4. Protótipo em `experiments/LEBRE-V0.54-PROTO-01/` (lebre-research), partindo dos arquivos da biblioteca
0.2.0 (hashes registrados); os arquivos do núcleo continuam intocados.

## 7. Achado no protótipo, antes da medição (10/10/2026)

O protótipo (`experiments/LEBRE-V0.54-PROTO-01/`) passou nos testes de identidade (onde a M1 nunca dorme, previsões
idênticas às da `lebre==0.2.0`), de `m5a=False` e de economia de custo. Um teste de sanidade de despertar, montado como o
cenário do critério 3 (sem dinâmica conjunta até t = 12.000, com ela depois; semente 5603), falhou: a M1 dormiu e não
despertou. O diagnóstico mostrou que **o cenário não cria utilidade para a M1 nem na v0.53**:

- depois da troca, o especialista E da v0.53, **ativo**, errou 2,6, 2,8 e 2,0 vezes mais que o núcleo nas janelas de
  2, 3 e 3 mil passos seguintes; o peso da M1 na v0.53 terminou em 6·10⁻¹⁴⁷; partindo do zero no mesmo regime, E erra
  0,52 a 0,80 vez o núcleo;
- a v0.54 e a v0.53 tiveram o mesmo erro depois da troca (razão 1,000).

Causa provável: a regressão do especialista tem memória longa (esquecimento 0,999 por atualização, uma atualização a cada
8 alvos) e fica presa ao regime anterior; o conjunto de entradas escolhidas não muda, então nada reinicia a M1. Isso é uma
**limitação da v0.53**, ligada à prioridade 2 (trocas de regime), não da M5a.

**Revisão proposta do critério 3 (pendente de decisão do responsável pelo projeto; a medição não foi feita):**
- (3a) **sem piora:** no cenário de troca de regime acima (20 séries), MSE da v0.54 no trecho depois da troca no máximo
  1,02 vez o da v0.53;
- (3b) **despertar condicional:** num segundo cenário, em que a M1 é útil, deixa de ser e volta a ser (regime A, depois B,
  depois A de novo, com a mesma relação), nas séries em que a M1 da v0.53 volta a pesar (ω > 0,5 em algum ponto do último
  trecho), a M1 da v0.54 desperta em pelo menos 90% delas; o MSE do último trecho fica no máximo 1,02 vez o da v0.53.

O teste de sanidade foi trocado por um teste do mecanismo de despertar isolado (`tests/test_m5a.py`).
