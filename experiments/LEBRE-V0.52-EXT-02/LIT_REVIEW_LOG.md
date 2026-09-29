# PRA-05 — Diário de buscas (27/09/2026)

**Mecanismo:** busca web geral. Houve limitação de taxa ("too_many_requests") em 5 consultas; nelas o mecanismo devolveu resultados parciais, que foram triados assim mesmo.

**Classificação dos resultados:**
- "antecipa": cobre o núcleo da afirmação;
- "parcial";
- "base": fornece a ferramenta;
- "distante";
- "—": nada relevante.

**Consultas:**

| # | Afirmação | Consulta | Triados / relevantes |
|---|---|---|---|
| 1 | A1 | anytime-valid e-process accept structural change online forecaster model growth | 2608.08174 (Choi 2026, correções preditivas pré-especificadas por e-process; **parcial**); 2410.17800 (e-valores para seleção de modelo de previsão; base, já citado); 2502.14173 (monitoramento de inadequação por erros; distante); 2505.09090 (SSRE; base, já citado) |
| 2 | A2 | sequential test predictive improvement add feature online learning e-values false discovery rate | 2603.24792 (e-closure online, melhora o e-LOND; base); 2407.15733 (closed testing online com e-values; base); 2506.01452 (e-GAI; base) |
| 3 | A1/A2 | online model selection anytime-valid comparing forecasters e-values streaming variable selection | 2501.10930 (seleção bayesiana online em logística; distante); 2608.23064 (inferência sequencial de previsões de inflação; distante) |
| 4 | A2 | streaming feature selection e-LOND online FDR regression sequential e-values adding variables | OSFS (ICML 2010; parcial para A2 sem e-values, já na PRA-04 via SAOLA); "Feature selection using e-values" (NSF PAR; offline, distante) |
| 5 | A2/A4 | online FDR control model selection lag selection time series anytime-valid hierarchical hypotheses | 2502.08539 (stopped e-BH; base); 1612.04467 (FDR hierárquico; base) |
| 6 | A3 | recursive ARX input selection online statistical test system identification transfer function delay estimation | recursiveARX, identificação recursiva (sem seleção com garantia; distante) |
| 7 | A3 | online sparse system identification exogenous inputs recursive least squares variable selection guarantees 2025 | **2505.00323** (identificação esparsa recursiva de ARMAX com garantias assintóticas; **parcial** para A3) |
| 8 | A4 | hierarchical testing lags distributed lag model multiresolution Haar coefficient selection time series | 2508.10055 (seleção bayesiana conjunta de atributos e defasagens; distante, offline); nada sobre Haar/multirresolução em defasagens |
| 9 | A5 | estimation error online learner benchmark predictive ability test adaptive reference misadjustment LMS | falha (limite de taxa) |
| 10 | A5 | "comparing sequential forecasters" learned forecasters estimation noise… | só Choe & Ramdas (base, já citado) |
| 11 | A6 | TinyML on-device online learning time series forecasting exogenous inputs microcontroller | TinyOL (2103.08295; aprendizado online em MCU, rede neural; parcial para A6); 2405.07601 (idem); TinyCast (já citado) |
| 12 | A6 | microcontroller energy load forecasting on-device adaptive filter Cortex-M4 cycles per prediction | **2608.14698** (ESP32, rede de 3.011 parâmetros, aprendizado incremental no dispositivo com sensores exógenos, previsão solar; **parcial** para A6, sem seleção de entradas nem medição de energia) |
| 13 | A7 | online Kalman filter ARMAX recursive forecasting benchmark hydrology streamflow (limite parcial) | ARMAX/Kalman em vazão (Haltiner 1988; literatura clássica; base para comparador ausente) |
| 14 | A7 | online learning forecasting expert aggregation building energy load one-step-ahead BDG2 (limite parcial) | só o artigo do BDG2 e benchmarks gerais; — |
| 15 | A1 | Amoukou Mishra Veloso follow-up citations (limite) | — |
| 16 | A1 | evidence-based architecture growth online learning shadow challenger champion anytime-valid promotion | **2609.04388** (comparabilidade de candidatos antes da promoção em detecção de intrusão; viés do incumbente; **parcial** para A5, empírico) |
| 17 | A3 | online Granger causality detection anytime-valid sequential test streaming time series exogenous variable | **2606.22230** (Granger distribucional com teste sequencial e alpha-investing, FWER; **parcial** para A1/A3); 2303.17916 (Granger por teste sequencial; parcial, sem garantia a qualquer tempo explícita) |
| 18 | A2 | e-LOND persistent hypotheses asynchronous decisions dependence simulation FDR e-values time series | **2608.09927** (de Heide 2026, e-closure dinâmica para hipóteses online com evidência que continua a acumular, "setwise persistent"; **base** diretamente pertinente às hipóteses persistentes); JMLR 2021 (testes assíncronos; base) |
| 19 | A3 | online structure learning ARX model order selection sequential likelihood ratio adaptive filtering tap selection | 2511.11178 (SINDy + Kalman online; parcial, sem garantia de seleção); 2607.16106 (LRT online de ponto de mudança; distante) |
| 20 | A1/A3 | anytime-valid test online Granger causality e-process predictive improvement 2026 (limite parcial) | 2209.12637 (testes a qualquer tempo de independência condicional, model-X; base) |
| 21 | A5 | testing predictive improvement over adaptively estimated benchmark estimation error favors larger model | Monte Carlo de testes de capacidade preditiva na seleção de modelos (IJF 2020; parcial, lote); testes com modelos sobrepostos (J. Econometrics 2024; base) |
| 22 | A2 | online e-process variable screening streaming regression anytime-valid feature inclusion | **2512.12244** (SAVA: alpha-investing sempre válido em cenário duplamente sequencial; **base** para A2); modelos lineares sempre válidos (Netflix; base); 2608.30502 (Han & Qu; já citado) |

**Leituras de resumo:** 2608.08174, 2606.22230, 2608.09927, 2609.04388, 2608.14698, 2511.11178, 2303.17916, 2512.12244.

**Total:** 22 consultas e 8 resumos lidos. Somando as 25 consultas da PRA-04, a auditoria chega a 47 consultas.
