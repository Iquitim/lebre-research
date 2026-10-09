# LEBRE v0.53 — M1, rascunho 3: regressão conjunta do alvo e das entradas atuais, especificação antes do código

**Data:** 09/10/2026. **Quarto desenho da M1.** Base: validação 4 (rascunho 2 não confirmado: nenhuma contribuição em Y-B03;
estrago em Y-B01 Horizonte) e diagnósticos do LEBRE Lab:
- **E13:** em Horizonte, o especialista dominava (s ~ 0,94) porque o Prod decide por perda recortada em 2σ e não via o erro
  grande e sistemático no nascer e no pôr do sol (+22% de MSE só às 16-17 h).
- **E14:** a v0.52 está abaixo da fronteira precisão × custo em **B03 e nas três famílias de maré** (B07, VB07, XB07). Nas
  marés, a regressão conjunta de y_{t−1}, y_{t−2} e das entradas no instante t, atualizada **a cada passo** (~280 FP,
  mais barata que a v0.52), empata com o comparador completo. Em B03, essa mesma regressão (com todas as entradas) já
  melhora muito a v0.52 (1,711 contra 2,076 do comparador; E10).

## 1. O especialista E (rascunho 3)

- **Variáveis:** z = [1, y_{t−1}, y_{t−2}, x_t das m entradas escolhidas], padronizadas pela triagem do rascunho 1
  (k = 3 + m). **Sem bandas de defasagem.**
- **m = mín(d, 5)**, as de maior correlação absoluta com o alvo (triagem e reseleção do rascunho 1).
- **RLS a cada passo** com alvo observado (λ = 0,999, δ = 100); entra no Prod depois de k atualizações.
- **Recorte da previsão:** [L − B, L + B], B = CLIP_K × máx(σ̂_L, piso), como no rascunho 2 (mantém o erro do especialista
  amarrado à escala dos dados, o que protege a normalização do item seguinte).
- **Combinação com a v0.52:** (A,B)-Prod anytime (A = E, B = v0.52), com as perdas normalizadas pelo maior erro já visto,
  **a mesma mudança da candidata Q da M2**: f_t(x) = (y_t − x)² / N_t, N_t = máx_{τ <= t} máx((y_τ − L_τ)², (y_τ − E_τ)²).
- **Encaixe:** a M2 (candidata Q) combina R com L' = s E + (1 − s) L.
- **Custo:** RLS (6k² + 4k) + previsão 2k + triagem/padronização 10m, por passo: ~482 FP com m = 5 (k = 8); ~282 com d = 3.
  Mais Prod (~31) e recorte (~4).

## 2. Critérios no banco de desenvolvimento ampliado (E16; fixados antes)

1. **F6 nas famílias em que a v0.52 está abaixo da fronteira (E14):** B03, B07, VB07, XB07. Em cada uma: custo médio da
   v0.53 (v0.52 + M1 + M2) <= 2,5 vezes o da v0.52 e erro (média geométrica ÷ comparador linear online completo) <= 1,05 ×
   o menor erro entre as 8 variantes do E14 com custo <= o da v0.53. É a regra do rascunho 1 (decidida pelo responsável
   pelo projeto para B03), aplicada às famílias em que o E14 mostrou o mesmo defeito.
2. **Critérios da M2 (régua por decidibilidade com o adendo de 09/10) com M1 + M2 em todas as famílias**, C05 incluída.
3. **Custo** reportado; teto da v0.53 como um todo no pré-registro final.

Se atender, a M1 r3 e a M2 Q vão juntas para a validação 5.
