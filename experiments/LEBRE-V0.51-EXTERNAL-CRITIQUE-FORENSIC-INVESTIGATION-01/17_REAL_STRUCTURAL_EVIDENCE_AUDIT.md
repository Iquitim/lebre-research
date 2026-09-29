# 17 — Evidência estrutural em dados reais

Telemetria do S dentro da v0.51 nos dois conjuntos held-out (código original, harness original):

| src    | task                       |   d |   s |   mean_wS |   max_wS |   frac_wS_gt_0.5 |   S_structural_promotions |   S_removals |   S_contribution_rms_rel |
|:-------|:---------------------------|----:|----:|----------:|---------:|-----------------:|--------------------------:|-------------:|-------------------------:|
| held   | Q1_ONS_Carga_SIN_2019_20   |   6 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q2_ONS_Hidro_SE_2019_20    |   6 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q3_ONS_Hidro_S_2019_20     |   6 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q4_ONS_Eolica_SIN_2019_20  |   6 |  24 |     0     |    0.053 |            0     |                         0 |            0 |                    0     |
| held   | Q5_BCB_GBPBRL              |   1 | nan |     0.443 |    1     |            0.429 |                         4 |            2 |                    0.008 |
| held   | Q6_Monash_AusElec_S4       |   1 |  48 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q7_Monash_Pedestrian_S4    |   1 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q8_Monash_Solar10min_S4    |   1 | 144 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held   | Q9_Monash_KDDCup_S4        |   1 |  24 |     0.556 |    1     |            0.542 |                         5 |            5 |                    0.209 |
| held   | Q10_Monash_AusElec_S5      |   1 |  48 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N1_ONS_Carga_SECO_2021_22  |   1 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N2_ONS_Hidro_N_2021_22     |   6 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N3_ONS_Termica_SIN_2021_22 |   6 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N4_ONS_Eolica_NE_2021_22   |   6 |  24 |     0     |    0.002 |            0     |                         0 |            0 |                    0     |
| held05 | N5_BCB_EURBRL              |   1 | nan |     0.27  |    1     |            0.267 |                         2 |            0 |                    0.012 |
| held05 | N6_Monash_ElecDemand_VIC   |   1 |  48 |     0     |    0     |            0     |                         1 |            0 |                    0     |
| held05 | N7_Monash_AusElec_S3       |   1 |  48 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N8_Monash_Pedestrian_S3    |   1 |  24 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N9_Monash_Solar10min_S3    |   1 | 144 |     0     |    0     |            0     |                         0 |            0 |                    0     |
| held05 | N10_Monash_KDDCup_S3       |   1 |  24 |     0.157 |    1     |            0.135 |                         2 |            1 |                    0.046 |

**Classificação por série:**
- **MEMORY_DOMINATED:** 16/20, com w_S ≈ 0. 15 delas não têm nenhuma promoção estrutural; a N6 tem 1 promoção sem peso no combinador. Inclui as 7 séries do ONS com 6 entradas.
- **MIXED:** Q5 e N5 (câmbio): w_S médio de 0,27–0,44, contribuição < 1,2% do desvio do alvo; e N10 (KDD S3): w_S 0,16, contribuição de 4,6%.
- **STRUCTURAL_DOMINATED:** Q9 (qualidade do ar KDD S4): w_S médio de 0,56, contribuição de 21% do desvio do alvo; o ganho sobre M é real (NMSE 0,101 contra 0,138 da M sozinha).
- Nenhuma dessas séries é um sistema guiado por entradas no sentido pretendido. Nas séries com d = 1, as "entradas" são apenas o próprio passado do alvo.

`REAL_STRUCTURAL_DISCOVERY = INSUFFICIENT_EVIDENCE` (status: **OPEN**). A recuperação sintética não autoriza nenhuma inferência sobre dados reais.
