# PRA-02 — Log de buscas (prior art da LEBRE v0.51)

**Data:** 25/09/2026
**Ferramenta:** busca web (um único mecanismo, resultados em inglês) + leitura de resumos no arXiv.
**Escopo:** componentes da v0.51 que a PRA-01 (19/09/2026, focada na v0.1) não cobriu.
**Limite declarado:** para a maioria dos trabalhos, a leitura foi de **resumo/página de abstract**, não de texto completo.

| # | Família | Consulta | Achados relevantes | Disposição |
|---|---|---|---|---|
| 1 | Testes sempre válidos para regressão | anytime-valid linear models regression coefficients sequential test Lindon | Lindon et al., arXiv 2210.08589 → JASA 2026; pacote R `avlm` | INCLUÍDO (ameaça alta ao teste de promoção) |
| 2 | Seleção de variáveis em fluxo com e-valores | online streaming feature selection e-values anytime-valid | OSFS (ICML 2010), SAOLA, OFS; nenhum com e-valores | INCLUÍDO como família; baixa proximidade |
| 3 | Alpha-investing | alpha-investing streaming feature selection Zhou Foster Stine Ungar | Zhou et al., KDD 2005 / JMLR 2006 | INCLUÍDO (ameaça alta conceitual) |
| 4 | Identificação esparsa online | online sparse identification of nonlinear dynamics recursive SINDy | R-SINDy (IEEE, 2024); SINDy streaming | INCLUÍDO (média) |
| 5 | Estrutura governada por testes em fluxo | FIMT-DD Hoeffding bound regression tree Page-Hinkley | FIMT-DD (Ikonomovska et al., 2011) | INCLUÍDO (alta, conceito de ciclo de vida) |
| 6 | Granger online | online Granger causality lag selection sequential test | arXiv 2303.17916 (2023); arXiv 2606.22230 (2026) | LIDO; baixa proximidade (offline / canais distribucionais) |
| 7 | E-processos e defasagens | e-process testing by betting time series regression lag selection | nenhum trabalho de seleção de defasagem com e-processos | Lacuna registrada |
| 8 | Estimação adaptativa de atraso | adaptive time delay estimation LMS Etter | Etter & Stearns (1981); So, Ching & Chan (1994) | INCLUÍDO (baixa-média) |
| 9 | Ordem/atraso ARX online | online model structure selection ARX recursive order and delay | ferramentas offline (arxstruc/delayest); testes pós-estimação | Contexto |
| 10 | Bancos de polos | Laguerre Kautz orthonormal basis pole selection online recursive | ARX-Laguerre online (Int. J. Control 86(3), 2013); seleção de polos (arXiv 2512.21096) | INCLUÍDO (média, estado latente) |
| 11 | CUSUM + MDL | CUSUM minimum description length online pruning parsimony | MDL online (Shamir 2015); FOCuS; nenhuma combinação CUSUM+aluguel | Lacuna estreita registrada |
| 12 | E-valores recentes | sequential hypothesis testing online regression feature e-value 2024–2026 | online closed testing (2407.15733); SAVA (2512.12244) | INCLUÍDO |
| 13 | DMA com seleção de preditores | Koop Korobilis dynamic model averaging inflation | Koop & Korobilis (IER 2012) | INCLUÍDO (média, combinador) |
| 14 | Seleção online de defasagens em previsão | online lag selection streaming forecasting sparse lags 2024–2025 | estudos offline/deep learning; VAR online (CSDA 2026) | Contexto |
| 15 | Sistemas evolutivos | evolving systems rule addition significance pruning eTS FLEXFIS | eTS, FLEXFIS, SAFIS (significância de regra) | Coberto pela PRA-01; contexto |
| 16 | Previsão embarcada | TinyML on-device online learning time series forecasting microcontroller | TinyCast (arXiv 2608.15767, 2026); fuzzy linguístico adaptativo em TinyML (MDPI AI 2025); TinyOL | INCLUÍDO (concorrência de produto) |
| 17 | Martingales de mistura | online variable selection mixture martingale confidence sequence sparse | Kaufmann & Koolen (JMLR 2021) | Contexto teórico |
| 18 | RLS esparso com suporte | recursive least squares sparse support detection active set delays | arXiv 2601.10379 (2026); 2406.10349 (2024); 2505.00323 (2025) | INCLUÍDOS (média-alta) |
| 19 | ARIMA online | Online ARIMA algorithms Liu Hoi Zhao AAAI 2016 | Liu et al. (AAAI 2016) | INCLUÍDO (memória M) |
| 20 | Regras adaptativas | AMRules Hoeffding Page-Hinkley | AMRules (Duarte, Gama & Bifet, TKDD 2016) | INCLUÍDO (alta, ciclo de vida) |
| 21 | Estados latentes online | online latent state discovery sequential test streaming pole | HMM em fluxo (predictive-first); nada com banco de polos + teste | Lacuna registrada |
| 22 | Pulos previsíveis / dormência | sleeping experts dormancy predictable skipping e-process optional continuation | de Heide, arXiv 2608.09927 (2026) | INCLUÍDO (média; também oportunidade) |

**Trabalhos lidos na página de abstract:** 2512.12244, 2303.17916, 2606.22230, 2601.10379, 2406.10349, 2505.00323, 2608.15767, 2608.09927.
**Não lidos em texto completo:** todos os acima. É a principal limitação desta auditoria (ver relatório, §6).
