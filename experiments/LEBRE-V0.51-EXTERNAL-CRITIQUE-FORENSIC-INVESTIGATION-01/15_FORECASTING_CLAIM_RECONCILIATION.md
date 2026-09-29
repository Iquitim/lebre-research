# 15 — Reconciliação das afirmações de previsão

Razão = NMSE da LEBRE / NMSE do modelo. Valores < 1 indicam a LEBRE melhor. "Válidas" são as séries em que o modelo concluiu sem falha.

| group             | model               |   valid_series |   geo_ratio_LEBRE_over_model |   median_ratio |   LEBRE_wins |
|:------------------|:--------------------|---------------:|-----------------------------:|---------------:|-------------:|
| prereg_online     | NLINEAR_ONLINE      |             10 |                        0.839 |          0.808 |            8 |
| prereg_online     | DLINEAR_ONLINE      |             10 |                        0.736 |          0.735 |           10 |
| prereg_online     | HOLT_WINTERS        |             10 |                        0.407 |          0.457 |           10 |
| prereg_online     | IPNLMS              |             10 |                        0.281 |          0.26  |           10 |
| prereg_online     | CTRL_ARX_NLMS       |             10 |                        0.338 |          0.266 |            9 |
| prereg_online     | CTRL_PERSISTENCE    |             10 |                        0.356 |          0.288 |            8 |
| prereg_online     | CTRL_SEASONAL_NAIVE |              9 |                        0.045 |          0.04  |            9 |
| posthoc_classical | M_ONLY              |             10 |                        0.967 |          1     |            2 |
| posthoc_classical | AIRLINE             |              9 |                        1.054 |          1.078 |            3 |
| posthoc_classical | ETS                 |              9 |                        0.606 |          0.555 |            8 |
| posthoc_classical | RLS5                |              6 |                        1.068 |          1.049 |            0 |
| foundation        | CHRONOS_BOLT_TINY   |             10 |                        0.772 |          0.867 |            7 |
| foundation        | CHRONOS_BOLT_SMALL  |             10 |                        0.999 |          1.086 |            4 |
| foundation        | CHRONOS2            |             10 |                        1.357 |          1.121 |            2 |
| foundation        | CHRONOS2_COV        |              4 |                        1.552 |          1.486 |            0 |

- **Comparadores online pré-registrados** (protocolo comum de 10 séries): a LEBRE é a melhor. Razão 0,84 contra o NLinear, 8/10 vitórias; contra DLinear, Holt-Winters e IPNLMS, vence em 10/10.
- **Clássicos pós-hoc:**
  - **airline por MLE**, 9 séries (falha de memória na implementação de espaço de estados com s = 144): **1,054**; a LEBRE vence 3/9.
  - **Só M:** 0,967.
  - **RLS:** 6 séries válidas, com 4 divergências.
  - Modelos com coberturas diferentes (10, 9, 6 ou 4 séries) não devem entrar num único ranking ordinal.
- **Modelos de fundação:** Chronos-2 é melhor (LEBRE/Chronos-2 = 1,357). O Chronos-2 com covariáveis só cobre 4 séries.

**Frase mais forte defensável:**
"Melhor modelo entre os comparadores online pré-registrados, no protocolo comum de 10 séries (0,84× o NLinear calibrado). Um modelo airline ajustado por máxima verossimilhança, avaliado depois (pós-hoc), é ~5% mais preciso nas 9 séries em que rodou, e o Chronos-2 é ~1,36× mais preciso, com custo 10⁶–10⁷ vezes maior."

**Não é defensável:** "melhor modelo não-fundação", porque existe um clássico pós-hoc mais forte. Também não se deve pôr num único ranking ordinal modelos com coberturas diferentes.

**Terminologia "held-out":**
- O conjunto principal (Q1–Q10) nunca foi usado por nenhuma versão: held-out genuíno.
- O segundo conjunto (N1–N10) já havia sido usado para avaliar a v0.5, e N1/N4 são séries do BENCH-04 em outro período. Deve ser chamado de **semi-held-out**. A §9.6 da especificação o chama de "já visto", mas a §10 o conta como held-out: a inconsistência procede.
