# PRA-04 — Log de buscas (prior art da LEBRE v0.52 corrigida)

**Data:** 27/09/2026
**Ferramenta:** busca web (um único mecanismo, resultados em inglês) + leitura de páginas de resumo no arXiv e, para dois trabalhos, do texto completo em HTML (leitura mediada por ferramenta de resumo).
**Escopo:** as afirmações atuais da v0.52 que as auditorias anteriores (PRA-02, PRA-03, Nota de desenho 02 §8–§10) não cobriram:
- (A) previsão com entradas sob orçamento mínimo;
- (B) mudança estrutural certificada por unidade de entrada, com refinamento hierárquico;
- (C) os achados metodológicos (desajuste da referência; limite de informação em entradas suaves);
- (D) as salvaguardas de engenharia.

**Não repetido aqui:** Choe & Ramdas (2024), Henzi & Ziegel (2022), e-LOND, SMCS, seleção prequencial/PLS, limites de memória × amostras, detecção de mudança com controle de amostragem (lidos antes).

| # | Família | Consulta | Achados relevantes | Leitura | Disposição |
|---|---|---|---|---|---|
| 1 | A | SparseTSF ultra-lightweight time series forecasting 1k parameters | SparseTSF (Lin et al., ICML 2024; TPAMI 2026) | resumo | INCLUÍDO — orçamento comparável em parâmetros; univariado, treino em lote, horizonte longo |
| 2 | A | FITS modeling time series with 10k parameters | FITS (Xu et al., ICLR 2024) | resumo | INCLUÍDO — idem; ~10k parâmetros |
| 3 | A | Tiny Time Mixers TTM exogenous variables | TTM (Ekambaram et al., NeurIPS 2024) | resumo | INCLUÍDO — ~1M parâmetros, aceita exógenas via decodificador ajustado |
| 4 | A | forecasting accuracy versus computational cost FLOPs trade-off 2025 | CAPS (2026), FreqFlow (2025), trabalhos de clima | resultados | Contexto — fronteira precisão × custo reportada em modelos profundos (10⁵–10⁹ FLOPs) |
| 5 | A | TinyML online time series forecasting microcontroller exogenous 2025 2026 | TinyCast (arXiv 2608.15767), TEDA-forecasting (Computing 2025), survey TinyML | resumo | INCLUÍDOS |
| 6 | A | TinyCast (abstract) | 146 mil parâmetros, INT8, zero-shot, univariado, probabilístico | resumo | INCLUÍDO — sem exógenas, sem aprendizado online |
| 7 | A | TEDA-forecasting abstract | nuvens de dados + RLS por nuvem, TinyML, correção de outliers | resumo (via busca) | INCLUÍDO — online e embarcado; sem seleção de entradas certificada |
| 8 | A | Reverso efficient time series foundation model 2026 | Reverso (arXiv 2602.17634), 0,2–2,6M parâmetros | resumo | Contexto — teto "pequeno" de modelos de fundação |
| 9 | B | online group feature selection OGFS group SAOLA | OGFS; group-SAOLA (Yu et al.) | resumos | INCLUÍDO — seleção de grupos em fluxo, sem e-valores nem garantia sempre válida |
| 10 | B | online time series forecasting concept drift OneNet FSNet | OneNet (NeurIPS 2023), FSNet (ICLR 2023), DSOF, Proceed | resumos | Contexto — adaptação online profunda, custo alto, sem estrutura certificada |
| 11 | B | recursive estimation transfer function online input selection ARMAX RPEM | RPEM/RARMAX; identificação regularizada online (arXiv 2401.00097) | resultados | Contexto — seleção de entradas por critérios clássicos, não sempre válidos |
| 12 | B | anytime-valid sequential Granger causality e-values 2025 2026 | Distributional Granger (arXiv 2606.22230, já na PRA-02); inferência para previsões de inflação (2608.23064) | resultados | Baixa proximidade |
| 13 | B | online FDR hierarchical tree-structured hypotheses e-values | Yekutieli 2008; Benjamini & Bogomolov; TreeBH; e-valores com resolução adaptativa | resultados | INCLUÍDO — testes hierárquicos existem (offline); versão online com e-values não encontrada |
| 14 | B | sequential model selection e-process online regression add variable 2026 | Backhaus et al. 2410.17800 (já na PRA-03); Frazier & Poskitt 2505.09090; RAVAS (Yang & Yao, arXiv 2606.00478) | resumos | INCLUÍDOS |
| 15 | B | anytime-valid inference online learning adaptive filter misspecified learners | **Amoukou, Mishra & Veloso, arXiv 2605.31239** (maio/2026) | **texto completo** | **INCLUÍDO — AMEAÇA ALTA ao núcleo do mecanismo** |
| 16 | C | Clark West 2007 nested models estimation noise | Clark & West (J. Econometrics 2007); West (1996) | resultados | INCLUÍDO — efeito do erro de estimação (sentido oposto ao nosso) |
| 17 | C | Giacomini White conditional predictive ability forecasting methods | Giacomini & White (Econometrica 2006) | resultados | INCLUÍDO — "método" = modelo + procedimento de estimação |
| 18 | C | LMS weight noise misadjustment correlated with past inputs | Widrow et al.; literatura de filtros adaptativos | resultados | INCLUÍDO — desajuste do LMS é conhecido |
| 19 | C | predictive regression persistent regressors Stambaugh Campbell Yogo | Stambaugh (1999); Campbell & Yogo (2006); IVX | resultados | INCLUÍDO — perda de poder com regressores persistentes é conhecida |
| 20 | D | missing output data recursive identification free-run hold last value | Kalman com observações faltantes; LOCF; imputação em identificação | resultados | INCLUÍDO — prática padrão |
| 21 | B | budgeted online learning computational budget model selection streaming | seleção de modelos com orçamento (arXiv 2401.10478, 2510.22654); kernels com orçamento | resultados | Contexto — orçamento de memória/treino, não de FLOPs por passo com testes sempre válidos |
| 22 | B | online forecaster exogenous structural change e-values FDR input selection embedded | e-BH, online e-BH (2407.20683), e-GAI | resultados | Nenhum trabalho com a combinação completa |
| 23 | B | "testing by betting" online feature selection model growth e-LOND forecasting 2026 | "Bet on Features" (Antonov et al., arXiv 2607.11653); Amoukou et al. | resumo | INCLUÍDO — auditoria de calibração, não modifica o previsor |
| 24 | B | anytime-valid lag selection online system identification ARX certified structure | rARX-DIPCA (arXiv 2606.00652); seleção de ordem por AIC/BIC | resultados | Contexto — sem garantia sempre válida |
| 25 | B/C | online model growth add remove regressors sequential test lifetime error control 2025 2026 | **Han & Qu, arXiv 2608.30502** (ago/2026); adaptação online de modelos de fundação | resumo completo | **INCLUÍDO — relevante para o achado (C1)** |

**Leituras de texto completo nesta auditoria:** Amoukou et al. (2605.31239), via HTML; Han & Qu (2608.30502), resumo integral. **Demais:** página de resumo ou resultados de busca. É a principal limitação (ver relatório §6).
