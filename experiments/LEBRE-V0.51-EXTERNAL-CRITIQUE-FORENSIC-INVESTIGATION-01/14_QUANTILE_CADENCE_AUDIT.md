# 14 — Cadência do intervalo (8 passos)

## Implementação real (código)
A cada 8 passos (t ≡ 0 mod 8): q ← max(0, q + 8·γ·σ̂·(1{|e_t| > q} − α)). Só o indicador **do passo de atualização** entra, multiplicado por 8 (operador A).
O operador alternativo B soma os 8 indicadores do bloco: q ← q + γ·σ̂·Σ(1{|e|>q} − α). O operador C atualiza a cada passo.
Em séries periódicas, **A e B não são equivalentes**: se 8 divide s, A só observa s/gcd(8,s) fases. Por exemplo, 3 de 24 com s = 24 e 18 de 144 com s = 144.

## Resíduos periódicos sintéticos (σ_t periódico, amplitude 0,8)
|   s | operator                    |   coverage |   phase_cov_min |   phase_cov_max |   phases_observed_by_refresh |
|----:|:----------------------------|-----------:|----------------:|----------------:|-----------------------------:|
|  24 | A_code_current_indicator_x8 |     0.9138 |          0.7438 |               1 |                            3 |
|  24 | B_accumulated_8_indicators  |     0.9021 |          0.725  |               1 |                            3 |
|  24 | C_every_step                |     0.901  |          0.725  |               1 |                            3 |
|  48 | A_code_current_indicator_x8 |     0.9005 |          0.7188 |               1 |                            6 |
|  48 | B_accumulated_8_indicators  |     0.9018 |          0.675  |               1 |                            6 |
|  48 | C_every_step                |     0.9003 |          0.6688 |               1 |                            6 |
| 144 | A_code_current_indicator_x8 |     0.9127 |          0.7    |               1 |                           18 |
| 144 | B_accumulated_8_indicators  |     0.9013 |          0.65   |               1 |                           18 |
| 144 | C_every_step                |     0.8999 |          0.6688 |               1 |                           18 |
|  25 | A_code_current_indicator_x8 |     0.8965 |          0.7125 |               1 |                           25 |
|  25 | B_accumulated_8_indicators  |     0.9022 |          0.725  |               1 |                           25 |
|  25 | C_every_step                |     0.9018 |          0.7125 |               1 |                           25 |

## Resíduos reais do próprio modelo (held-out; o operador só altera o intervalo, não a previsão)
| src    | task                       |   s |   cov_A |   cov_B |   cov_C |
|:-------|:---------------------------|----:|--------:|--------:|--------:|
| held   | Q1_ONS_Carga_SIN_2019_20   |  24 |   0.965 |   0.901 |   0.9   |
| held   | Q2_ONS_Hidro_SE_2019_20    |  24 |   0.937 |   0.901 |   0.9   |
| held   | Q3_ONS_Hidro_S_2019_20     |  24 |   0.928 |   0.901 |   0.901 |
| held   | Q4_ONS_Eolica_SIN_2019_20  |  24 |   0.922 |   0.901 |   0.9   |
| held   | Q6_Monash_AusElec_S4       |  48 |   0.851 |   0.902 |   0.9   |
| held   | Q7_Monash_Pedestrian_S4    |  24 |   0.92  |   0.902 |   0.901 |
| held   | Q8_Monash_Solar10min_S4    | 144 |   0.906 |   0.906 |   0.901 |
| held   | Q9_Monash_KDDCup_S4        |  24 |   0.893 |   0.9   |   0.898 |
| held   | Q10_Monash_AusElec_S5      |  48 |   0.89  |   0.903 |   0.901 |
| held05 | N1_ONS_Carga_SECO_2021_22  |  24 |   0.971 |   0.901 |   0.9   |
| held05 | N2_ONS_Hidro_N_2021_22     |  24 |   0.916 |   0.9   |   0.9   |
| held05 | N3_ONS_Termica_SIN_2021_22 |  24 |   0.927 |   0.903 |   0.902 |
| held05 | N4_ONS_Eolica_NE_2021_22   |  24 |   0.923 |   0.901 |   0.9   |
| held05 | N6_Monash_ElecDemand_VIC   |  48 |   0.877 |   0.904 |   0.901 |
| held05 | N7_Monash_AusElec_S3       |  48 |   0.862 |   0.903 |   0.9   |
| held05 | N8_Monash_Pedestrian_S3    |  24 |   0.913 |   0.901 |   0.9   |
| held05 | N9_Monash_Solar10min_S3    | 144 |   0.891 |   0.906 |   0.901 |
| held05 | N10_Monash_KDDCup_S3       |  24 |   0.912 |   0.902 |   0.901 |

- Com o operador A, a cobertura real varia entre 0,85 e 0,97 conforme a série. Com B ou C, todas ficam em 0,900–0,906.
- O Q1 (0,965, a única série fora da faixa no pré-registro) vai para 0,901 com B.
- A cobertura por fase é ruim em todos os operadores (mínimos de 0,3–0,8), porque a cobertura é marginal, não condicional, como a especificação já declarava.

**Classificação:** `QUANTILE_CADENCE_PHASE_ALIASING = SUPPORTED`. O operador B é o candidato natural de correção, mas **não** foi adotado nesta etapa.
