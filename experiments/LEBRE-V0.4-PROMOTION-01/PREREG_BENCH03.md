# Pré-registro — Promoção LEBRE v0.4: confirmação interna + BENCH-03 held-out

**Escrito e com hash registrado ANTES de qualquer execução destas avaliações.**
Objeto: `lebre_v04.py` congelado (SHA-256 `f542bf7c…5cc4912`), configuração padrão C2 + C4 + C5 + C6
(C1 e C3 desligados; ver `V04_DEV_REPORT.md`). Sem calibração. Comparador principal: `lebre_v032.py` (congelado).

## Parte 1 — Confirmação interna (I1–I14), não degradação

- Sementes **2176..2205** (N = 30, livres). Braços: V02_A0, V032, V04 e CTRL_ARX.
- Unidade: semente, com a média das 14 tarefas feita dentro de cada semente.

| Hipótese | Regra |
|---|---|
| G1 NMSE, não inferioridade contra v0.3.2 | limite unilateral de 95% de (V04 − V032) < +0,010 |
| G2 custo | média de FP da V04 ≤ 100,000 |
| G3 estrutura, não inferioridade contra v0.3.2 | limite unilateral inferior de 95% de (V04 − V032) na fração exata > −0,02 |
| G4 superioridade contra v0.2 A0 | limite unilateral superior de 95% de (V04 − V02_A0) < 0 |
| G5 intervalos | cobertura média ∈ [0,88; 0,92] (alvo 0,90) |
| G6 fidelidade | máx \|ŷ − Σ contribuições\| = 0 (tolerância de ponto flutuante 1e-9) |

Salvaguardas reportadas: latência de chaveamento I11–I14 (V04 − V032 ≤ +50 passos), reativação da I7 e ΔNMSE por tarefa ≤ +0,010.

**Desfechos de explicabilidade e transparência operacional** (declaração de benefício):
recuperação de estrutura; esparsidade (átomos ativos em média); estabilidade (eventos do ciclo de vida por 1000 passos em I1, I3, I4, I6 e I9 depois de t = 2000);
atraso de detecção de mudança (primeiro evento do ciclo de vida depois do ponto de mudança em I5, I11, I12, I13 e I14); cobertura; fidelidade.

## Parte 2 — BENCH-03 externo held-out (nenhum dado usado antes no projeto)

**Trilha A — previsão univariada (arquivo Monash, Godahewa et al. 2021), informação X_t = [y_{t−1}].** Primeira série de cada arquivo,
limitada aos primeiros 50 000 pontos: australian_electricity_demand (sazonal ingênuo s = 48), sunspot, saugeenday, us_births (s = 7),
solar_10_minutes (s = 144), pedestrian_counts (s = 24), kdd_cup_2018 (s = 24).
**Trilha B — regressão em fluxo (River), sementes 7301..7310, T = 16 000:** FriedmanDrift LEA (4000/8000/12000), GRA (6000/12000),
GSG (6000/12000, janela 800), Planes2D e Mv.
**Trilha C — identificação (nonlinearbenchmark.org), X_t = [u_t, y_{t−1}], teste na partição de validação:** F16 (treino FullMSine_Level3 →
teste FullMSine_Level4_Validation) e ParWH (treino Est-phase-0-amp-2 → teste Val-amp-2).
**Trilha D — FIR esparso, sementes 7401..7410:** comprimento 32; K ∈ {2, 6}; entrada branca ou AR(1) com 0,8; **SNR de 10 dB**; troca de sistema em T/2.

**Modelos:** LEBRE_V04, LEBRE_V032, CTRL_PERSISTENCE, CTRL_SEASONAL_NAIVE (quando s estiver definido), CTRL_ARX_NLMS, IPNLMS (μ calibrado),
os 15 do BENCH-01B (calibrados em min(15%, 5000) passos), RIVER_SGD_LINREG, RIVER_HATR e RIVER_ARF (este **somente em fluxos ≤ 25 000 passos**,
por custo computacional). Sementes dos modelos estocásticos nos dados reais: 7501..7503. Harness: `run_full_stream`, teste a partir de 0,30T
(trilhas A, B e D) ou na partição oficial (trilha C).

## Critério de decisão (faixa de competitividade; fixado antes dos dados)

| # | Critério | Limiar |
|---|---|---|
| K-a | skill > 0 contra a persistência (NMSE mediano) | ≥ 70% das tarefas |
| K-b | NMSE ≤ 1,25× o do melhor clássico (IPNLMS, ARX, NLMS, RLS, persistência, sazonal) | ≥ 60% das tarefas |
| K-c | zero divergências | 100% das execuções |
| K-d | não degradação contra a v0.3.2: NMSE_V04 ≤ 1,25 × NMSE_V032 | ≥ 90% das tarefas |
| K-e | cobertura do intervalo de 90% ∈ [0,85; 0,95] | ≥ 80% das tarefas |

`COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` se K-a a K-e passarem; `PARTIALLY_COMPETITIVE` se ≥ 3 passarem; caso contrário `NOT_COMPETITIVE`.
**Nota de honestidade:** os limiares K-a e K-b foram escolhidos perto do desempenho de DEV (18/25 e 15/25), portanto este é um teste de replicação em dados novos, não de superação.

## Regra de promoção a v0.4

A LEBRE é promovida a **v0.4 (especificação de pesquisa)** se a Parte 1 passar em G1–G6 **e** a Parte 2 der `COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` ou `PARTIALLY_COMPETITIVE`.
Em qualquer outro caso, a v0.3.2 permanece como a versão de pesquisa vigente.
