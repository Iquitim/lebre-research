# PRA-11 — Registro das consultas (10/10/2026)

Protocolo: `PRA_11_PROTOCOLO.md` (commit `eb2ba79`, antes das buscas). Mecanismo de busca geral na web; 17 consultas, como
fixadas; 1 consulta de acompanhamento por trabalho próximo, feita como leitura do resumo original (arXiv, Crossref).
Níveis: A = antecipa; P = parcial; B = base; D = distante.

| # | Afirmação | Consulta | Resultados triados |
|---|---|---|---|
| 1 | B1 | convex combination of adaptive filters reduced complexity update only the dominant filter | Combinação convexa de filtros (Arenas-García et al. 2006; filtros no domínio da frequência, arXiv:1805.01307; pares de projeção afim): cada componente sempre se adapta; redução de custo por outras vias (B). Nenhum trabalho atualiza só o componente dominante |
| 2 | B1 | online expert aggregation computational budget skip updating low-weight experts | **M-LCB** (Latypov et al., arXiv:2510.22654, 2025): orçamento de atualizações por rodada entre especialistas que aprendem (**P**); BEXP (orçamento de consultas por grupos de custo) (D) |
| 3 | B1 | sleeping experts lazy update low weight online learning computation | Especialistas que "dormem" (Freund et al. 1997; Kanade e Steinke; "dying experts", NeurIPS 2019): o conjunto ativo é dado de fora, não decidido pelo peso (D) |
| 4 | B2 | data-selective adaptive filtering set-membership update cessation computational savings | Filtragem por pertinência a conjunto e seleção de dados: atualiza só quando o erro passa de um limite, com economia de cálculo (B; já na PRA-06) |
| 5 | B2 | event-triggered learning online regression skip updates | Aprendizado disparado por evento (processos gaussianos em controle; Solowjow e Trimpe) (B) |
| 6 | B2 | online streaming feature selection reduced screening frequency of inactive features budget | Seleção de atributos em fluxo (OSFS, 2010/2013; OSFAS, 2019; triagem online com deriva, arXiv:2104.02883): nenhuma reduz a frequência de triagem de candidatos inativos sob orçamento (D) |
| 7 | B3 | anytime-valid test for removing a variable in online regression e-value | Teoria de e-valores e testes fechados online (Fischer e Ramdas, arXiv:2407.15733) (B); nenhum teste sempre válido de remoção de variável em regressão online |
| 8 | B3 | online variable selection regime change recursive least squares variable deletion test | **AdaFSML-RLS** (Souza e Araújo, ETFA 2012): seleção online de variáveis com RLS que acompanha a relevância ao longo do tempo (**P**); seleção online com esquecimento e detecção de mudança (Anagnostopoulos et al.; não conferido) (P, provisório); testes de remoção em lote (FSDA) (D) |
| 9 | B3 | sequential backward elimination streaming time series exogenous inputs | Eliminação para trás em lote para entradas de séries temporais (SISAL; Tikka e Hollmén) (D) |
| 10 | B4 | spurious regression online learning nonstationary integrated series detection forecasting | Literatura clássica de regressão espúria e previsões espúrias, em lote (B) |
| 11 | B4 | sequential cointegration test online monitoring | **Trapani e Whitehouse** (arXiv:2003.12182, 2020): monitoramento sequencial de quebras e de perda de cointegração numa regressão (B); monitoramento CUSUM não paramétrico (D) |
| 12 | B4 | automatic differencing decision online time series forecasting unit root streaming | Decisão de diferenciação por testes de raiz unitária em lote (Koehler e Franses 1998; `ndiffs`) (B); diferenciação aprendida (AdaRDiff, arXiv:2608.28134) (D) |
| 13 | B5 | online seasonality detection anytime-valid sequential test of the period | Teoria para tornar testes sempre válidos (Koning e van Meer, arXiv:2501.03982; Holmes e Walker, arXiv:2602.13872) (B); detecção de sazonalidade em lote (D) |
| 14 | B5 | online model selection of the seasonal period exponential smoothing streaming | Suavização exponencial online com período fixo; seleção do modelo sazonal em lote (AIC; estimador neural, arXiv:2606.27711) (D) |
| 15 | B5 | automatic seasonal period identification streaming time series expert aggregation | Patentes de identificação de período (ACF e densidade espectral), em lote ou com reverificação; algoritmo de agregação para séries (Jamil et al.) (D) |
| 16 | B6 | compute-adaptive online forecasting anytime-valid structural changes computational budget | **ADOWIP** (Wang, arXiv:2606.25068, 2026): previsor online que só se adapta quando a perda passa de um quantil calibrado e há orçamento, com contabilidade exata do custo (**P**); previsão adaptativa a mudanças estruturais (Giraitis et al. 2013) (D) |
| 17 | B6 | e-process online model selection forecasting computational cost | Seleção de modelos de previsão por e-valores em tempo real (Backhaus et al., arXiv:2410.17800; já na PRA-04) (B) |

## Acompanhamento (resumos originais lidos)

| Trabalho | Fonte conferida | Conferência |
|---|---|---|
| Latypov, Suvorikova, Kroshnin, Gasnikov, Dorn (2025), *Managing Self-Learning Experts under Per-Round Budget Constraints*, arXiv:2510.22654 | arXiv (resumo) | Escolhe um especialista para decidir e no máximo M de K para aprender por rodada, por limites de confiança; arrependimento sempre válido no tempo. Ambiente estocástico de bandidos/RL, não combinação de previsores por pesos |
| Wang (2026), *Adapt Only When It Pays: Budgeted Decision-Loss Priority for Delayed Online Time-Series Adaptation*, arXiv:2606.25068 | arXiv (resumo) | Atualiza um adaptador residual só quando a perda de decisão passa de um quantil calibrado e há orçamento; viabilidade do orçamento e arrependimento para um subproblema convexo; sem evidência sempre válida; mudanças de parâmetros, não de estrutura |
| Souza e Araújo (2012), *An online variable selection method using recursive least squares*, ETFA 2012, doi:10.1109/ETFA.2012.6489623 | Crossref (dados bibliográficos); descrição pelo trecho de busca | Seleção online de variáveis com RLS para sensores virtuais; a descrição do método não foi lida no texto completo |
| Trapani e Whitehouse (2020), *Sequential monitoring for cointegrating regressions*, arXiv:2003.12182 | arXiv (resumo) | Monitoramento por CUSUM de mudança de inclinação ou de passagem a não cointegração, após amostra de calibração |
| Backhaus, Brucke, Ruckdeschel, Schlüters (2024), arXiv:2410.17800 | arXiv (resumo) | Seleção de modelos de previsão por e-valores em tempo real; "persistência" aqui é combinar previsões persistindo no modelo indicado pelos e-valores, não exigir que uma melhora dure |
