# LEBRE v0.53 — M1, rascunho 1: especialista de defasagens conjuntas (F6), especificação antes do código

**Data:** 08/10/2026. **Decisões do responsável pelo projeto:** a v0.53 não fecha com débito técnico (F6 é resolvida
nela); a meta de F6 é de fronteira precisão × custo, com teto de **2,5 vezes** o custo da v0.52 em B03.
**Base:** rascunho 0 (não fica: E8) e diagnósticos E9 e E10 (LEBRE Lab, `diagnosticos/F6_E9_*`, `F6_E10_*`): a vantagem do
comparador linear em B03 vem da estrutura conjunta de defasagens; com custo comparável ao da v0.52, um RLS sobre o alvo
defasado e as bandas de defasagem das entradas já a supera com folga.

## 1. Critério de F6 (fixado antes de medir; substitui o "1,05 do linear online" da nota de desenho)

- **Comparadores fixos:** as 8 variantes de RLS do E10, com erro (média geométrica ÷ comparador completo) e custo medidos:
  AR2+0 (1,711 a cada passo, 872 FP; 2,198 a cada 8, 198 FP), AR2+B3 (1,359, 2.082 FP; 1,574, 318 FP), AR2+B8 (1,101,
  11.432 FP; 1,302, 1.574 FP), completo (1,000, 34.200 FP; 1,239, 4.406 FP).
- **Teto:** custo médio por passo da v0.53 em B03 (v0.52 + M2 + M1) <= 2,5 vezes o da v0.52 em B03 (medidos na mesma
  execução, por série).
- **Meta:** com c = custo médio da v0.53 em B03, erro da v0.53 (média geométrica das 4 séries, ÷ comparador completo)
  <= 1,05 × o menor erro entre as variantes com custo <= c.

## 2. O especialista E (rascunho 1)

- **Variáveis:** z = [1, y_{t−1}, y_{t−2}, bandas de m entradas], bandas da v0.52 por entrada: instante t, defasagem 1,
  média de 2-3, média de 4-7, média de 8-15 (k = 3 + 5m variáveis).
- **m = mín(d, 8)**: as m entradas de maior correlação absoluta com o alvo (triagem do rascunho 0). O limite 8 vem do
  teto de custo: é o maior m cujo especialista (~1.574 FP com m = 8 no E10) cabe no orçamento de 2,5 vezes em B03.
- **RLS** com λ = 0,999 e δ = 100, atualizada a cada EVERY = 8 passos (como no rascunho 0); seleção depois de N_MIN alvos,
  refeita a cada T_MAX, com recomeço da RLS e do Prod se o conjunto mudar.
- **Entrada no Prod:** só depois de k atualizações da RLS (sistema determinado), como no rascunho 0.
- **Combinação e encaixe:** (A,B)-Prod anytime com a v0.52 como referência de confiança; a M2 (candidata P) combina R com
  L' = s E + (1 − s) L. Alvo faltante: as defasagens do alvo usam o último valor observado.

## 3. Critérios no banco de desenvolvimento

1. F6 em B03, como na seção 1.
2. B01 e B02: limite superior do IC 95% de (M1 + M2) ÷ (M2 sozinha) <= 1,02.
3. Critérios da M2 (régua por decidibilidade) nas 43 famílias com M1 ligada, **C05 incluída**; custo combinado reportado
   (o teto de custo da v0.53 como um todo é decidido no pré-registro final; tensão já declarada na nota de desenho).

## 4. Custo

Especialista: (6k² + 4k)/8 + 2k + 10m FP por passo (k = 3 + 5m): ~1.574 com m = 8; Prod ~31; triagem ~d.
