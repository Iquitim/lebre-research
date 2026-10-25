# LEBRE v0.56 — Por que o ganho da C5 caiu nas bacias do Chile: plano (commitado antes de qualquer medição)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-03` · **Natureza:** diagnóstico **exploratório**. Nenhuma mudança de
desenho; a reserva final da v0.56 (30 bacias do CAMELS-CL, posições 0–29, e as demais famílias) continua lacrada.

## 1. Pergunta

Nas bacias brasileiras do desenvolvimento, a C5 (a M1 corrigida) errava de 5% a 7% menos que a v0.55. Nas 20 bacias
chilenas da validação, a diferença foi de 1,2%, com IC incluindo 1 (`LEBRE-V0.56-VAL-01`). **Por quê?**

Hipóteses, fixadas antes de medir:
- **H1, não havia o que ganhar:** no Chile, a v0.55 já fica perto de um ARX com RLS. O ganho da C5 nas bacias
  brasileiras era o de fechar a diferença para esse ARX; se a diferença não existe no Chile, a C5 não tem o que fechar.
- **H2, as entradas informam menos:** no Chile, as entradas do mesmo dia e de até 3 dias (o que a C5 usa) explicam menos
  da vazão. Isso valeria, por exemplo, com neve e degelo, onde a vazão responde a temperaturas acumuladas e a
  precipitações antigas.
- **H3, a evapotranspiração potencial:** o Chile entra com evapotranspiração potencial (Hargreaves); o Brasil, com a real
  (GLEAM). Se a C5 tirava proveito da real, trocar a real pela potencial nas bacias brasileiras deveria reduzir o ganho.
- **H4, a M1 não entra:** no Chile, a M1 da C5 ganha pouco peso, fica dormente ou escolhe outras entradas.

## 2. Dados

| Conjunto | Uso | Situação |
|---|---|---|
| **CL-V**: as 20 bacias chilenas da validação (posições 30–49 do sorteio da v0.56) | H1, H2, H4 e descritivo | gastas pela validação; a trava aceita só essas 20 |
| **D-A**: as 30 bacias brasileiras das posições 140–169 | H3 | consumidas (diagnósticos anteriores) |
| **Lacradas** | **não tocadas** | as 30 bacias chilenas da final, os prédios, as usinas e as 17 bacias brasileiras da final |

**Arquivo novo, para H3:** `07_CAMELS_BR_potential_evapotransp.zip` do CAMELS-BR 1.2 (Zenodo 15025488, CC-BY-4.0, o
mesmo depósito dos arquivos já usados), em `data/external_v052/camels_br/`, com SHA-256 registrado. A coluna será escolhida
pelo cabeçalho, antes de rodar: um produto de evapotranspiração **potencial**, preferindo o mais próximo de uma fórmula de
temperatura (como a de Hargreaves); a escolha fica registrada em `RUN_NOTAS.md` antes da execução.

## 3. Medições (execução única)

**CL-V:**
- R0 (ARX-RLS da comparação, `ArxGen` em R0), R1 (sem entradas) e R2 (só precipitação), como no `DIAG-01`;
- A (v0.55), C5 e C0 (a correção completa, a M5 do `DIAG-02`), com a gravação das previsões internas da M1: peso ω,
  fração do tempo dormente, entradas escolhidas, E livre;
- desempenho de A, C5 e R0 relativo à persistência, para situar as séries.

**D-A, com a evapotranspiração potencial no lugar da real** (a outra entrada e a precipitação inalteradas): A, C5 e R0.

## 4. Leitura (fixada antes; tudo descritivo, com IC pelo bootstrap da comparação: blocos de 30 dias, a partir de 30%
da série, semente 2026102903, conferida como não usada)

- **H1:** G_CL = v0.55 ÷ R0 em CL-V. Se o IC de G_CL contém 1 ou fica abaixo de 1, H1 é **sustentada**: não havia diferença
  para fechar. Comparado com G em D-A (1,124) e D-B (1,053).
- **H2:** R1 ÷ R0 em CL-V (quanto as entradas ajudam o ARX), comparado com D-A (1,281) e D-B (1,262). Um valor muito menor
  sustenta H2.
- **H3:** em D-A, a razão v0.55 ÷ C5 com a potencial, comparada com a mesma razão com a real (1,072 no `DEV-01`). Se o
  ganho cair para menos da metade, H3 é sustentada.
- **H4:** peso mediano da M1 e fração do tempo dormente em CL-V, comparados com D-A (`DIAG-02`); entradas escolhidas.
- **Descritivo por bacia em CL-V:** Spearman de log(v0.55 ÷ C5) e de log(v0.55 ÷ R0) com a fração de neve (MSWEP), a
  aridez, o índice de escoamento de base, a sazonalidade da precipitação e a área. Com n = 20, só indicação.

O relatório diz quais hipóteses são sustentadas, quais não são, e o que isso implica para uma próxima candidata.

## 5. Registro de um deslize anterior

Ao conferir a estrutura do arquivo de evapotranspiração real do CAMELS-BR para este plano, imprimi os 5 primeiros valores
de entrada (evapotranspiração, 1980) da bacia 10500000. Ela está na posição 79 da permutação (reserva 2 da v0.52,
consumida em 2026-09). Nenhum alvo, nenhuma série lacrada.
