# Decisão — a v0.4.5 substitui a v0.4.2 como implementação da linha v0.4 (correção, não promoção plena)

**Data:** 2026-09-23. **Tomada por:** o responsável pelo projeto, com base na recomendação registrada em `V045_REPORT.md`.
**Natureza:** decisão **pós-hoc**, tomada depois de ver os resultados do `PREREG_V045.md`. A decisão pré-registrada (`NAO_PROMOVIDA`) permanece
registrada e não é apagada. Esta decisão não a reescreve; ela a complementa.

## Por que a regra pré-registrada não se aplica como escrita

A regra dizia: "se a v0.4.5 falhar, a v0.4.2 permanece". Ela partia da premissa de que a v0.4.2 passava nas próprias salvaguardas.
Nas sementes novas (2401..2430), a v0.4.2 **falha exatamente as mesmas duas salvaguardas** (detecção 1,30× a v0.3.2; ΔNMSE na I5 +0,018),
porque no interno a v0.4.5 é idêntica a ela. Manter a v0.4.2 significaria escolher a versão pior com a mesma falha.

## Base da decisão (dominância, sem nenhuma métrica pior)

| | v0.4.2 | v0.4.5 |
|---|---|---|
| Interno G1–G6, custo, cobertura, fidelidade | igual | igual |
| Salvaguardas contra a v0.3.2 | falha | falha (idêntica) |
| BENCH-04 (semi-held-out) | 3/5; 1,18× a v0.3.2 | **5/5; 0,91×** |
| Held-out BR novo | 1,05× a v0.3.2 | **0,97×** |
| X3 (outliers) | 0,273 | **0,262** |
| Instabilidade ligada ao aquecimento (BENCH-04, p90/p10) | 1,61 | **1,51** |

## Estado resultante

- **Linha v0.4 (versão de pesquisa):** implementada por `lebre_v045.py` (SHA-256 `97af0482…`). A `lebre_v042.py` fica arquivada como histórico.
- **Ressalvas vinculadas à linha v0.4** (valem para a v0.4.5):
  1. o atraso de detecção fica ~1,3× o da v0.3.2 em sementes novas;
  2. o ΔNMSE na I5 é de +0,018 contra a v0.3.2;
  3. há instabilidade bimodal conforme o ponto de partida (held-out p90/p10 de 3,6, contra 1,07 da v0.3.2);
  4. continua longe dos modelos modernos (2,1× o NLinear e 3,2× o Chronos no BENCH-04).
- **v0.3.2** continua sendo a referência de estabilidade (é frágil a outliers de entrada: X3 = 4,24).
- LEBRE v0.1 continua canônica e congelada; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.
- **Próxima etapa:** v0.4.6, para investigar o aprendizado proporcional (IPNLMS) como causa da instabilidade e do atraso de detecção,
  com o mesmo protocolo (DEV → pré-registro → interno + held-out + BENCH-04 + X3).
