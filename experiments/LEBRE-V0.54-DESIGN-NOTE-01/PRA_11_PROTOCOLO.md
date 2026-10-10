# PRA-11 — Protocolo da busca de trabalhos anteriores para a v0.54 (fixado antes das buscas)

**Data:** 10/10/2026 · **Objetivo:** localizar trabalhos que antecipem, total ou parcialmente, as mudanças propostas na
nota de desenho 01 da v0.54, antes do rascunho da especificação. Segue o protocolo da PRA-05 (v0.52).

## Afirmações auditadas

- **B1 (M5a).** Numa combinação online de previsores (especialistas, filtros adaptativos), reduzir a frequência de
  atualização ou o custo de um componente enquanto seu peso é baixo, preservando a capacidade de ele voltar a pesar.
- **B2 (M5b).** Custo proporcional ao uso: candidatos (entradas) nunca aceitos triados com frequência reduzida; aprendizado
  e evidência pausados por regra que só usa o passado (filtragem seletiva de dados, aprendizado disparado por evento).
- **B3 (M4).** Remoção online de estrutura (variáveis, entradas) com garantia sempre válida, ou testes sequenciais de
  remoção; esquecimento de entradas depois de troca de regime.
- **B4 (M3).** Detecção ou prevenção online de relações espúrias em séries não estacionárias (integradas) dentro de
  previsão ou seleção de variáveis online; diferenciar o alvo como hipótese; exigir persistência da melhora.
- **B5 (M6).** Período sazonal tratado como hipótese escolhida online, com evidência sempre válida ou seleção online entre
  memórias sazonais candidatas.
- **B6 (integração).** As mudanças acima governadas por evidência sempre válida, sob um custo computacional declarado, num
  previsor online.

## Consultas (fixadas; inglês; mecanismo de busca geral na web)

| Afirmação | Consultas |
|---|---|
| B1 | (1) convex combination of adaptive filters reduced complexity update only the dominant filter; (2) online expert aggregation computational budget skip updating low-weight experts; (3) sleeping experts lazy update low weight online learning computation |
| B2 | (1) data-selective adaptive filtering set-membership update cessation computational savings; (2) event-triggered learning online regression skip updates; (3) online streaming feature selection reduced screening frequency of inactive features budget |
| B3 | (1) anytime-valid test for removing a variable in online regression e-value; (2) online variable selection regime change recursive least squares variable deletion test; (3) sequential backward elimination streaming time series exogenous inputs |
| B4 | (1) spurious regression online learning nonstationary integrated series detection forecasting; (2) sequential cointegration test online monitoring; (3) automatic differencing decision online time series forecasting unit root streaming |
| B5 | (1) online seasonality detection anytime-valid sequential test of the period; (2) online model selection of the seasonal period exponential smoothing streaming; (3) automatic seasonal period identification streaming time series expert aggregation |
| B6 | (1) compute-adaptive online forecasting anytime-valid structural changes computational budget; (2) e-process online model selection forecasting computational cost |

Até 1 consulta de acompanhamento por trabalho muito próximo (registrada como tal).

## Inclusão, classificação e conferência

- **Inclusão:** método publicado ou pré-print que cubra, na mesma peça, pelo menos dois elementos da afirmação.
- **Níveis:** *antecipa* (cobre o núcleo da afirmação); *parcial*; *base* (fornece a ferramenta); *distante*.
- **Conferência:** os trabalhos classificados como *antecipa* ou *parcial* têm os dados bibliográficos conferidos (arXiv,
  Crossref ou página do editor) e o resumo original lido antes de entrar no relatório.

## Registro

Cada consulta vai em `PRA_11_LOG.md` com os resultados triados; o relatório vai em `PRA_11_RELATORIO.md`.

**Limitações declaradas desde já:** um mecanismo de busca; leitura em geral pelo resumo; literatura de 2026 possivelmente
não indexada; não é uma revisão sistemática no sentido formal. Não encontrar um trabalho não prova originalidade.
