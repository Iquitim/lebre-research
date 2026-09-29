# LEBRE v0.3 — Evolução fundamentada da LEBRE (nota de design + resultados exploratórios)

**Estágio:** `LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01` · **Status:** `EXPLORATORY_DEV_NON_CANONICAL`
`src/` e `tests/` canônicos intocados. M3 `UNOPENED`. `NOVELTY_CLAIM_READY = NO`. Nada aqui é confirmatório.

## 1. Objetivo

Evoluir a LEBRE, e não substituí-la, segundo quatro princípios: (1) eficiência sob orçamento restrito,
(2) explicabilidade, (3) adaptabilidade, (4) fundamentação matemática. A exigência adicional é ter desempenho competitivo que
justifique a existência da arquitetura.

## 2. O que é mantido da LEBRE

- caminho-base linear sem memória, sempre ativo;
- caminho de atrasos discretos esparsos (átomos `x_{t-k,i}`, k ≤ 32 como na v0.2);
- **um** caminho de estado latente recorrente;
- ciclo de vida `DORMANT → PROVISIONAL → ACTIVE → EVICTED`;
- busca por fronteira rotativa esparsa (triagem de 2 candidatos por passo);
- orçamento explícito de átomos estruturais (`M_max = 4`).

## 3. O que muda: heurística → princípio

| Função | v0.2 (heurístico) | v0.3 (fundamentado) | Garantia / base |
|---|---|---|---|
| Estado latente | unidade escalar com RTRL (~20 FP) | forma de inovações (Kalman estacionário): `s_t = p s_{t-1} + (1-p) u_{t-1}` com banco de polos τ ∈ {1, 2, 5, 20}, mais o átomo de **acionamento** `q_t = p q_{t-1} + (1-p) x_{t-1,i}` | preditor ótimo para estado oculto linear de 1ª ordem (resultado estabelecido); o banco de polos é uma aproximação |
| PROVISIONAL→ACTIVE | EMA 0,95 + `obs≥15` + limiares 0,02/0,015 | martingale de mistura gaussiana sobre o escore do resíduo: promove se `log M ≥ log(p/α)` | desigualdade de Ville + Bonferroni: P(promoção falsa por episódio) ≤ α, *anytime* (idealizado: σ conhecido, modelo fixo) |
| ACTIVE→EVICTED | EMAs de ganho por evento + limiares 0,005/0,008 | CUSUM de Page sobre a razão de log-verossimilhança "sem vs. com" o átomo, com limiar `h = log(ARL)` | Lorden: tempo médio até remoção falsa ≥ e^h (antes do aluguel) |
| Parcimônia / recursos | aluguel de shadow (heurístico) | aluguel MDL `r = h/T_idle` nats por passo, ponderado pela excitação do átomo | um átomo precisa "pagar" ≥ r nats/passo para ficar; um átomo ocioso sai em ~T_idle passos |
| Quiescência | retenção em duas escalas de tempo | evidência congelada sem **excitação persistente** (potência de entrada < 10% da potência de longo prazo) | princípio clássico de controle adaptativo: sem excitação não há identificação |
| Escalas de tempo | EMAs por evento (causa do ARB10) | toda evidência em tempo de fluxo; cadências só adicionam espera limitada | invariância ao "decimar" decisões, por construção |
| Inicialização | peso do candidato | média posterior `S/(V + σ²/ρ)` | Bayes gaussiano; evita o "gargalo do recém-nascido" |

Os limiares derivam de α, do ARL e de T_idle, e não de ajuste empírico: `log(p/α)` ≈ 8,2 nats; `h = log 6000` ≈ 8,7 nats.

**Explicabilidade.** Cada átomo tem significado físico ("x1 atrasado 6 passos", "estado latente τ≈5 alimentado por x0"),
evidência em nats, CUSUM contrário e registro de eventos do ciclo de vida. Veja `LebreV03.explain()`.

## 4. Resultados exploratórios

### 4.1 Benchmark interno I1–I14 (DEV, sementes 3301..3310, 4 iterações)

| | NMSE | FP/passo | estrutura exata |
|---|---|---|---|
| v0.2 A0 (K1, K_arb=5) | 0,316 | 110,9 | 159/220 |
| v0.2 B1 (K2) | 0,321 | 100,4 | 154/220 |
| **v0.3 iter4** | **0,215** | **99,3** | **167/220** |

v0.3 − v0.2 A0: Δ = −0,102, com 10/10 sementes a favor. **Ressalva:** quatro iterações de design foram feitas nas mesmas sementes. O resultado é DEV, não confirmatório.

### 4.2 BENCH-01 externo (uma única execução, v0.3 congelada, SHA-256 em `FREEZE_ITER4_SHA256.txt`)

Mesmo harness, 30 sementes de avaliação, 15 tarefas (8 mecanísticas, 2 holdouts, 5 com dados reais), sem calibração
(os baselines tiveram grid search por tarefa). 450/450 execuções bem-sucedidas, 0 divergências.

| Modelo | NMSE médio | FLOPs médios | rank médio (de 16) | tarefas na fronteira de Pareto |
|---|---|---|---|---|
| **LEBRE v0.3 (congelada)** | **0,215** | 178,8 | **2,0** | **10** |
| S3_RSONN | 0,599 | 498,4 | 5,6 | 1 |
| Track B (M2 congelado) | 0,702 | 90,4 | 8,4 | 6 |

A v0.3 vence o Track B em 13 das 15 tarefas (30/30 sementes em cada uma). Ela perde na A1 e na B3.

### 4.3 Controle cético: autorregressão do alvo (decisivo para a interpretação)

| Controle (sem calibração) | NMSE médio |
|---|---|
| Persistência `ŷ = y_{t-1}` | 0,930 |
| **ARX-NLMS** `[x_t, 1, y_{t-1}]`, μ = 0,1 | **0,426** |
| LEBRE v0.3 | **0,215** |

- **O ARX-NLMS trivial já supera todo o campo do BENCH-01B.** Parte grande da vantagem aparente da v0.3 sobre o campo é
  autorregressão do alvo, permitida pelo protocolo prequencial mas não explorada pelos baselines. Essa é uma lacuna do BENCH-01B.
- **O valor próprio da v0.3 sobre o ARX** (0,215 contra 0,426) vem da descoberta estrutural e da adaptação a regimes: ela vence em 9 de 15 tarefas.
  Os maiores ganhos são em atrasos esparsos (A2–A4: 0,005 contra 1,06), transições (A8, H2) e dados reais B1/B2.
- **A v0.3 perde para o ARX** em A5/A7 (quiescência, 0,044 contra 0,022), H1 (ressonador de 2ª ordem, 0,206 contra 0,134), B3, B4 e B5
  (B5 por margem ínfima). Diagnóstico provável: o latente usa o resíduo `u` e só uma ordem de dinâmica, enquanto o ARX usa `y_{t-1}`
  diretamente e o tempo todo.

## 5. Limitações honestas

1. **Envelope de micro-recursos do BENCH-01 não atendido.** Com D grande, o custo escala como O(D): 355 FLOPs com D=50, média de 179.
   Só 3 das 15 tarefas ficam ≤ 100 FLOPs. A memória (histórico de 33×D + escores de triagem) passa de 1 KB em quase todas.
   No I1–I14 (D=5) o orçamento de 100 FP é atendido, mas com folga mínima.
2. **As garantias são idealizadas.** Ville e Lorden valem com modelo fixo e σ conhecido. No laço adaptativo são aproximações.
3. **Redundância (I10 / Gate 6)** continua produzindo co-ocupação, porque a evidência condicional não reajusta os outros pesos.
4. **Achados informados pelo BENCH-01 não podem ser revalidados no próprio BENCH-01** (os dados reais são determinísticos).
5. As contagens de FLOPs dos baselines são autodeclaradas por implementação. A comparação é aproximada.

## 6. Próximos passos recomendados

1. **v0.3.1 (hipóteses já contaminadas pelo BENCH-01; exigem avaliação nova):**
   - átomos autorregressivos do alvo `y_{t-k}` no dicionário, o que dá ordem 2 para H1 e retenção em A5/A7;
   - histórico em fp16 e triagem com poucos bytes, para caber em 1 KB;
   - custo sublinear em D (NLMS esparso na base).
2. **Pré-registro confirmatório** da v0.3 contra a v0.2 A0 no I1–I14, com coorte nova (por exemplo 2086..2115, após varredura), N=30.
3. **Adicionar o ARX-NLMS como controle obrigatório** a qualquer benchmark futuro da LEBRE.
4. **Holdout externo novo:** outros datasets reais que não sejam do BENCH-01, escolhidos antes de rodar.

## 7. Artefatos

`lebre_v03.py` (modelo), `run_dev_eval.py` + `DEV_*_iter{1..4}.csv` (I1–I14), `FREEZE_ITER4_SHA256.txt`,
`run_bench01_external.py` + `BENCH01_LEBRE_V03_RESULTS.csv`, `compare_bench01.py` + `BENCH01_V03_VS_FIELD.csv`,
`BENCH01_OVERALL_WITH_V03.csv`, `run_bench01_controls.py` + `BENCH01_CONTROLS_RESULTS.csv`.
