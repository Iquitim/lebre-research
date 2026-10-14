# LEBRE v0.54 — Adendo 01 ao registro de congelamento

**Data:** 14 de outubro de 2026. Os arquivos congelados (`LEBRE_v0.54_SHA256SUMS.txt`) não são editados; correções de
texto ficam neste adendo.

## 1. Número de séries reais da validação 6

Dois arquivos congelados dizem que a validação 6 do LEBRE Lab usou **24** séries reais nunca vistas:

- `experiments/LEBRE-V0.54-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M5a_r2.md`, seção "Aceite na validação 6";
- `experiments/LEBRE-V0.54-DESIGN-NOTE-01/DESIGN_NOTE.md`, atualização de 11/10/2026.

O número certo é **20**: 4 de carga do ONS (2000-2001), 4 de qualidade do ar (estação Dingling), 6 eólicas e 6 de maré,
mais as 50 sintéticas, num total de **70** séries. Isso foi conferido nos arquivos da montagem (`analises/validacao6_montagem.json`)
e do resultado (`analises/m5a_val6/*.json`) do LEBRE Lab. O resultado da validação 6 e a decisão (M5a aceita) não mudam: o
erro era só na contagem citada no texto. A mesma contagem errada aparece numa mensagem de commit do LEBRE Lab, que não é
alterada.
