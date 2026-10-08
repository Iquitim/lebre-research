# LEBRE v0.53 — M1, rascunho 0: especialista de precisão enxuto (F6)

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código. **Decisão do responsável pelo projeto:** M1 enxuta
(atualizações espaçadas), mantendo o critério preliminar de custo da v0.53 (1,25 vez a v0.52) e deixando a M5 como a
mudança que precisa reduzir custo.

## 1. A falha

F6 (LEBRE Lab, B03 qualidade do ar): quando o alvo tem uma relação quase exata com uma entrada no mesmo instante, a v0.52
erra 5,5 vezes mais que uma regressão recursiva (2,1 vezes na média de 4 poluentes). O modelo base da v0.52 já usa todas
as entradas no instante 0, mas por NLMS de passo pequeno, que converge devagar; a RLS converge em poucas dezenas de
observações.

## 2. Literatura

Combinar dois filtros adaptativos de velocidades diferentes é clássico (Arenas-García, Figueiras-Vidal e Sayed, 2006,
PRA-06); a v0.53 não reivindica a combinação. O que muda em relação à nota de desenho: o especialista **não** entra por
um teste (e-process), porque a M2 mostrou que testes são lentos para decidir a saída; entra pelo mesmo mecanismo
validado na M2, o **(A,B)-Prod anytime** (Sani, Neu e Lazaric, 2014), com a v0.52 como referência de confiança: a saída
fica a uma constante da v0.52 e só migra para o especialista quando ele acumula vantagem.

## 3. Definição

- **Especialista E:** regressão recursiva (RLS) com esquecimento sobre z = [1, x_a, x_b, x_c]: as **3 entradas** (no
  instante t) de maior correlação absoluta com o alvo, padronizadas.
- **Triagem:** médias exponenciais de x, x², x·y, y e y² de cada entrada, atualizadas a cada EVERY = 8 passos (constante
  da v0.52). Seleção das 3 entradas depois de N_MIN = 100 alvos observados e refeita a cada T_MAX = 5000 passos
  (constantes da v0.52); se o conjunto mudar, a RLS recomeça (w = 0, P = δI) e a padronização é atualizada.
- **Atualização espaçada (decisão de custo):** a RLS é atualizada a cada EVERY = 8 passos, com o par (z, y) do passo;
  a previsão de E é feita a cada passo. Esquecimento λ = 0,999 por atualização e δ = 100: os mesmos do comparador linear
  online do Lab que define F6 (declarado: não derivados).
- **Combinação:** L' = s × E + (1 − s) × L, com s do (A,B)-Prod anytime (A = E, B = L = v0.52), perdas recortadas da
  v0.52 com a escala do erro recente de L (CLIP_K, LAM, piso da porta). Entradas faltantes: último valor visto (como o
  comparador). Enquanto E não tem seleção, L' = L.
- **Entrada no Prod:** E só participa depois de a RLS ter recebido pelo menos tantas atualizações quanto variáveis (4),
  o mínimo para o sistema estar determinado; se o conjunto de entradas mudar, a RLS e o Prod recomeçam (especialista
  novo). Acrescentado antes do código, na revisão da especificação.
- **Encaixe com a M2:** a M2 (candidata P, congelada) passa a combinar R com L' em vez de R com L.

## 4. Custo (regra de FP da v0.52, contado antes de medir)

Triagem ~d por passo (5 estatísticas por entrada a cada 8 passos); RLS com 4 variáveis ~180 FP por atualização, ~23 por
passo; previsão de E ~13; Prod ~31; mistura 3. **Total ~70 + d FP por passo** (d = número de entradas). Somado à M2
(~130), a v0.53 fica ~200 + d acima da v0.52: o critério de 1,25 vez só é atingido com a M5.

## 5. Critérios no banco de desenvolvimento (da nota de desenho, mais a não regressão da M2)

1. B03: MSE da v0.53 (M1 + M2) no máximo 1,05 vez o do linear online (média geométrica).
2. B01 e B02: limite superior do IC 95% de (M1 + M2) ÷ (M2 sozinha) <= 1,02.
3. Todos os critérios da M2 (régua por decidibilidade) continuam valendo nas 43 famílias, agora com M1; o critério de custo
   passa a valer para as duas juntas: acréscimo sobre a v0.52 <= 150 + 70 + d FP por passo.
4. Custo de M1 medido e reportado (meta: <= 70 + d FP por passo).

## 6. Resultado (E8, E9; 08/10/2026)

- **E8 (desenvolvimento):** a M1 enxuta **não fica**. Critério 1 falha: em B03, M1 + M2 ÷ linear online = 1,899 (v0.52:
  2,076). Critério 3 falha: C05 (1,014, limite superior 1,033) e VB02 (1,010, limite superior 1,020); em várias séries
  horárias e curtas a M1 piora a M2 em 0,1% a 0,7%. Em B01 e B02 o critério 2 passa.
- **E9 (diagnóstico de F6):** a vantagem do comparador linear em B03 vem da estrutura conjunta de defasagens (alvo
  defasado e 8 defasagens de todas as entradas, 75 variáveis), não da relação no mesmo instante; o especialista de 3
  entradas no instante t é o pior desenho para esses dados. O diagnóstico de F6 na nota de desenho estava errado.
- **Consequência:** resolver F6 exigiria uma regressão conjunta com dezenas de variáveis (custo O(k²) com k ~ 75), fora do
  orçamento de custo da v0.53; a decisão sobre a M1 é do responsável pelo projeto.
