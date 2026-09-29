# PRA-05 — Protocolo da revisão bibliográfica sistemática (fixado antes das buscas)

**Data:** 27/09/2026 · **Objetivo:** localizar trabalhos que antecipem, total ou parcialmente, as afirmações da LEBRE v0.52 e registrar o que foi e o que não foi encontrado. Isso amplia a auditoria anterior (PRA-04: 25 consultas).

**Afirmações auditadas**
- **A1.** Mudança de estrutura de um previsor online aceita por teste sequencial sempre válido (e-process) de melhora preditiva.
- **A2.** Controle de falsas descobertas online (e-values, LOND/e-LOND) aplicado a seleção de variáveis ou crescimento de modelo em fluxo.
- **A3.** Seleção de entradas e atrasos em modelos com entradas exógenas (ARX, função de transferência) de forma online, com garantia estatística.
- **A4.** Teste hierárquico de atrasos ou refinamento multirresolução da resposta a uma entrada.
- **A5.** Efeito do erro de estimação de um aprendiz online de referência sobre testes de capacidade preditiva.
- **A6.** Previsão online embarcada (TinyML, microcontrolador) com entradas exógenas e orçamento de operações por passo.
- **A7.** Baselines online da mesma classe: filtro de Kalman/ARMAX recursivo, seleção online de modelos por especialistas.

**Fonte.** Mecanismo de busca geral na web (inclui arXiv, periódicos, anais). Até 3 consultas por afirmação, mais 1 de acompanhamento por trabalho muito próximo. Inglês.

**Inclusão.** Método publicado ou pré-print que cubra, na mesma peça, pelo menos dois elementos da afirmação. Os trabalhos incluídos são classificados em quatro níveis:
- *antecipa*: cobre o núcleo da afirmação;
- *parcial*;
- *base*: fornece a ferramenta;
- *distante*.

**Registro.** Cada consulta é registrada em `LIT_REVIEW_LOG.md` com os resultados triados. O relatório vai em `PRA_05_REPORT.md`.

**Limitações declaradas desde já:**
- um mecanismo de busca;
- leitura em geral pelo resumo;
- literatura de 2026 possivelmente não indexada.
