# Relatório — LEBRE v0.4.5 (guarda de contrato de entrada, C5′)

Pré-registro: `PREREG_V045.md` (SHA-256 no arquivo `PREREG_V045_SHA256.txt`). Objeto: `lebre_v045.py` (SHA-256 `97af0482…`).
Correção de montagem, sem efeito nos resultados: `internal_v045.py` apontava para o hash do pré-registro antigo e falhou antes de rodar. A verificação foi corrigida (`HARNESS_FIX_NOTE.txt`).

## Decisão pré-registrada: **NÃO PROMOVIDA**

A regra exigia todas as salvaguardas internas. Duas falharam:
- atraso de detecção de 1,30× a v0.3.2 (limite 1,25×);
- ΔNMSE na I5 de +0,018 (limite +0,010).

**Essas falhas não vêm da mudança.** No interno a v0.4.5 é idêntica à v0.4.2, porque nada é recortado. São propriedades da própria v0.4.2 que
não se replicaram nas sementes novas (2401..2430): nas sementes da promoção (2236..2265), o atraso tinha sido de 228 contra 226.
Portanto, **a salvaguarda de detecção da v0.4.2 também falha em sementes novas**. Esse é um achado sobre a v0.4.2, não sobre a C5′.

## Resultados

| Parte | Critério | Resultado |
|---|---|---|
| 1. Interno | G1–G6 | ✅ todos (NMSE 0,2146; estrutura 92,6%; cobertura 0,901; fidelidade exata; 99,5 FP) |
| 1. Interno | salvaguardas | ❌ detecção 1,30×; ❌ I5 +0,018; ✅ latências; ✅ I7; ✅ não degrada contra a v0.4.2 |
| 2. Propriedades | T3, T9, T10 | ✅ 0 promoções falsas; fidelidade exata; cobertura 0,901 |
| 3. BENCH-04 refeito (semi-held-out) | rótulo | **`COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` (5/5)**, contra 3/5 da v0.4.2 |
| 3. BENCH-04 | contra v0.3.2 / contra v0.4.2 | **0,91×** / **0,78×**; 7º de 35 (a v0.4.2 era 9º) |
| 4. Held-out BR (ONS carga S/NE, eólica S, solar SE) | H1: V045/V042 ≤ 1 | ✅ 0,926 |
| 4. Held-out BR | H2: V045/V032 ≤ 1,10 | ✅ 0,974 |
| 4. Held-out BR | H3: instabilidade p90/p10 | ❌ V045 3,56; V042 3,23; **V032 1,07** |
| 5. X3 (outliers) | ≤ 1,10 × V042 | ✅ 0,262 contra 0,273 (a v0.3.2 fica em 4,24) |

Contra os modelos modernos, a v0.4.5 continua longe: 2,1× o NLinear e 3,2× o melhor Chronos no BENCH-04.

## Estabilidade — a pergunta principal

- **A C5′ resolveu a instabilidade de aquecimento.** Tetouan passa de p90/p10 3,1 para 1,6; BR1 de 3,1 para 1,5; BR2 de 2,5 para 1,8.
- **Existe uma segunda instabilidade na linha v0.4, independente do recorte.** O resultado fica bimodal conforme o ponto de partida.
  Na carga Sul, por exemplo, dá ~0,05 em 7 de 10 partidas (melhor que os 0,065 da v0.3.2) e 0,21–0,34 nas outras 3.
  A v0.3.2 fica entre 0,060 e 0,069 em todas. O mesmo padrão aparece em solar SE/CO, eólica NE e solar NE.
- A v0.3.2 continua sendo a versão **mais estável** (p90/p10 ≈ 1,0–1,2 em quase tudo), mas é **frágil a outliers de entrada** (X3: 4,24).
- **Hipótese para a próxima etapa (não testada):** o aprendizado proporcional (IPNLMS) concentra a adaptação nos coeficientes
  grandes e pode travar em soluções ruins dependendo da história inicial. O mesmo pode explicar o aumento do atraso de detecção.
  A ablação sem IPNLMS (§7 do BENCH-04) é o ponto de partida.

## Conclusão

A C5′ é uma correção correta e fundamentada. Remove o dano do aquecimento, mantém a proteção contra outliers e melhora
todas as métricas externas (5/5 no BENCH-04, melhor que a v0.4.2 e a v0.3.2 no held-out). Pela regra pré-registrada, porém, **não há promoção**.
As salvaguardas internas que falharam são herdadas da v0.4.2, e a meta de estabilidade não foi atingida.
Estado: a v0.4.2 continua como referência formal da linha v0.4, com a ressalva registrada de que ela também falha a salvaguarda de detecção em sementes novas.

## Decisão posterior (pós-hoc, 2026-09-23)

O responsável pelo projeto aceitou a recomendação: **a v0.4.5 substitui a v0.4.2 como implementação da linha v0.4**. É uma correção,
não uma promoção plena, e vem com ressalvas vinculadas. O registro está em `DECISAO_V045_SUBSTITUI_V042.md`. A decisão pré-registrada (`NAO_PROMOVIDA`) permanece registrada.
