# M2 da v0.53: candidata M (switch distribution num só sentido), especificação antes do código

**Data:** 08/10/2026. **Nona configuração da M2.** Base: E3 (`M2_E3_RESULTADO.md`, LEBRE Lab): a candidata D (AdaHedge
acumulado) é robusta a erros isolados mas não escapa de uma fase de aprendizado longa (Abaiara); a candidata S (switch
distribution) escapa dessa fase mas, por trocar nos dois sentidos, volta para a referência a cada erro isolado grande da
LEBRE e perde 2-7% em quase todas as famílias.

## 1. A ideia

Há uma informação conhecida de antemão que nenhuma tentativa usou: **a LEBRE aprende e a referência não.** A competência
relativa da LEBRE tende a melhorar com os dados (é a dificuldade D1, o "catch-up phenomenon" de van Erven et al., 2012,
que motivou a switch distribution: modelos simples primeiro, complexos depois). A definição geral do artigo (eq. 10)
permite restringir os previsores para os quais se pode trocar (conjuntos 𝒦 e ℒ). A candidata M restringe as trocas a
**um só sentido, da referência para a LEBRE**.

## 2. Definição

- **Hipóteses:** "sempre R"; "sempre L"; "R até o instante t, L a partir de t" (t >= 2).
- **Prioridade:** a do artigo (eq. 11: μ(m) = 2^{−m}, τ(t) = 1/(t(t − 1)), escolhas uniformes) restrita a essas
  sequências e renormalizada: μ(1) = ½ repartido entre "sempre R" e "sempre L" (¼ cada) e μ(2) = ¼ para "R e depois L";
  renormalizando por ¾, **⅓ para cada forma**, e o instante da troca com τ(t) = 1/(t(t − 1)) (soma 1 em t >= 2).
- **Cálculo exato (forward):** pesos w_R (sempre R), w_L (sempre L), w_P (R, troca pendente), w_T (já trocou para L).
  Início ⅓, ⅓, ⅓, 0. A cada rodada: multiplicar pelas verossimilhanças (R para w_R e w_P; L para w_L e w_T); depois mover
  a fração 1/(n + 1) de w_P para w_T (chance de a troca ocorrer no próximo instante, dado que não ocorreu: τ(t)/Σ_{u>=t} τ(u)
  = 1/t). Peso de R na previsão: w_R + w_P; de L: w_L + w_T.
- **Perdas, escala e regras:** iguais às da candidata S (gaussianas de variância comum σ̂² = máx(mín(σ²_R, σ²_L), piso²),
  comparação só com a referência definida, primeira rodada só inicializa as escalas). Saída: média ponderada.

## 3. Garantias e limites

- Mistura bayesiana: perda logarítmica acumulada no máximo a da melhor hipótese mais −ln(prioridade): ln 3 contra
  "sempre R" ou "sempre L"; ln 3 + ln(t(t − 1)) contra "trocar em t".
- **Limite declarado:** se a LEBRE piorar de forma duradoura depois de ter sido melhor (o contrário de aprender), M só
  volta à referência pela hipótese "sempre R", que pode ter ficado muito atrás: comporta-se como a candidata D nesse caso.
- Custo estimado: ~40 FP por passo, mais ~18 da auditoria.

## 4. Medição

E4 (desenvolvimento) nas 43 famílias, com a régua por decidibilidade e plano commitado antes; se atender a tudo,
validação 3 nova, congelada, usada uma vez; depois a reserva (v0.53 completa).
