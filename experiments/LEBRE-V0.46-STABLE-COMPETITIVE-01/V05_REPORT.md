# Relatório — LEBRE v0.5 (três especialistas online com agregação exponencial)

Pré-registro: `PREREG_V05.md` (hash em `PREREG_V05_SHA256.txt`). Objeto: `lebre_v05.py` (hash em `FREEZE_V05_SHA256.txt`).
**Decisão pré-registrada: `PROMOVIDA_v0.5`** (versão de pesquisa; passa a ser a referência da linha). A LEBRE v0.1 continua canônica;
M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## 1. Investigação (DEV, só dados já usados)

1. **O IPNLMS não causa a instabilidade** (`dev_instab.py`): sem ele, a instabilidade é igual e o erro piora.
2. **A causa é a representação.** Em séries reais sazonais, o que importa é memória **densa e longa** do alvo, relativa ao último valor (NLinear).
   A hipótese estrutural esparsa (≤ 4 átomos até a defasagem 32) e o nível aprendido pelo viés tornam as decisões iniciais dependentes do ponto de partida.
3. **Nenhuma representação vence nos dois mundos.** A janela é essencial em séries reais e inútil ou prejudicial nos sistemas guiados por entradas (I1–I14).
   A cascata piorou o interno em 30%; o aprendizado conjunto divergiu.
4. **Agregação online de três especialistas** resolve os dois casos, com garantia de arrependimento:
   - A: a LEBRE estrutural;
   - W: memória do alvo;
   - B: W mais a LEBRE sujeita a evidência sobre o resíduo.

## 2. Resultados pré-registrados

| Critério | Limiar | Resultado |
|---|---|---|
| I-1 interno: não degrada contra a v0.4.5 | limite superior < +0,010 | ✅ −0,015. **Melhora:** NMSE 0,198 contra 0,215 |
| I-2 cobertura interna | [0,88; 0,92] | ✅ 0,902 |
| I-3 fidelidade da explicação | ≤ 1e−9 | ✅ 3e−15 |
| **C1** held-out: V05 / NLinear | ≤ 1,10 | ✅ **1,058** |
| **C2** held-out: V05 / melhor de NLinear, DLinear e Holt-Winters | ≤ 1,15 | ✅ **1,058** |
| **S1** estabilidade (10 partidas), mediana / máximo | ≤ 1,10 / ≤ 1,50 | ✅ **1,010 / 1,121** (v0.4.5: 1,76 / 8,58) |
| S2 cobertura ∈ [0,85; 0,95] | ≥ 80% das tarefas | ✅ 100% (0,893–0,902) |
| K-c divergências | 0 | ✅ |
| C3 (meta, não vinculante): V05 / melhor Chronos | ≤ 1,50 | ✅ por pouco: **1,487** |

**Held-out** (10 séries novas, 5 brasileiras, 14 modelos): **5º lugar**, atrás de Chronos-2, Chronos-2 com covariáveis, NLinear e Chronos-Bolt small.
Fica à frente do Chronos-Bolt tiny, do DLinear e do Holt-Winters. Tem 0,38× o erro da v0.4.5 e 0,50× o da persistência.

**BENCH-04** (semi-held-out, 36 modelos): **4º lugar** (a v0.4.5 era 7º). K-a a K-e: 90%, 100%, ✅, 100%, 100%. Razões: 1,04× o NLinear e 1,62× o melhor Chronos.
Estabilidade: máximo de 1,03.

## 3. Leitura honesta

- **Competitiva, não superior.** A v0.5 fica ~5% atrás do NLinear online calibrado nas séries reais e ~1,5× atrás do melhor Chronos.
  O ganho de desempenho vem principalmente do especialista de memória (NLinear embutido).
  A contribuição própria da LEBRE aparece:
  - nos sistemas guiados por entradas, onde o NLinear não serve e a v0.5 melhora a própria v0.4.5;
  - nas covariáveis com outliers (guarda C5′);
  - nos intervalos calibrados (o NLinear não tem);
  - na explicação exata.
- **Estável:** a instabilidade dependente do ponto de partida desapareceu (máximo de 1,12 contra 8,58 da v0.4.5).
- **Custo:** ~1000 FP/passo e 0,17 ms/passo em Python. É ~10× a v0.4 e ~6× o NLinear, mas ~90× mais barata que o Chronos-2 e ~300× mais que o Chronos-2 com covariáveis na CPU.
- **Explicabilidade:** continua exata e aditiva, mas mudou de natureza.
  - A memória do alvo é densa e aparece agregada: último valor, defasagens recentes e ciclo.
  - A estrutura esparsa nomeada vale para o especialista estrutural e para as covariáveis, ponderadas pelos pesos.
  - Os pesos são interpretáveis (que "modo" o modelo está usando). No interno, o peso do especialista estrutural termina em média em 0,93, e ele recupera a estrutura correta em 92,4% dos casos.
- **Limites:**
  - C3 passou por margem mínima;
  - Chronos pode ter visto séries do Monash no pré-treino;
  - N1 e N4 são held-out temporal de séries do BENCH-04;
  - a troca de pesos não tem teste estatístico de alarme.

## 4. Artefatos

`lebre_v05.py`, `PREREG_V05.md`, `eval_v05.py`, `chronos_v05.py`, `analyze_v05.py`, `V05_DECISION.json`,
`INTERNAL_V05_RESULTS.csv`, `HELDOUT_V05_RESULTS.csv`, `HELDOUT_V05_OFFSETS.csv`, `HELDOUT_CHRONOS_RESULTS.csv`, `BENCH04_V05_*.csv`,
DEV: `dev_instab.py`, `dev_arch.py`, `dev_internal.py`, `DEV_*.csv`.
