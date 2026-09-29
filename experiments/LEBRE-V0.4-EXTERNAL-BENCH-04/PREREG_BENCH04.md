# Pré-registro — BENCH-04: benchmark externo da LEBRE v0.4 com dados reais variados, modelos novos e dados brasileiros

**Escrito e com hash registrado antes de qualquer execução em dados do benchmark.** Os testes de mecânica usaram só séries sintéticas.
Objeto: LEBRE v0.4, `experiments/LEBRE-V0.4-PROMOTION-01/lebre_v042.py`
(SHA-256 `5c9ac0f7952dd42c593ad117a712d3ae4f44356fb56bfc36fa08a2de94986506`), congelada e **sem calibração**.
Este estágio **não promove nem altera** a arquitetura. O resultado caracteriza a v0.4. M3 continua `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## 1. Dados (todos reais e nunca usados em estágios anteriores)

| Tarefa | Fonte | Frequência | T | D | s | Alvo |
|---|---|---|---|---|---|---|
| BR1_ONS_Carga_SECO | ONS, curva de carga horária 2023–2024, subsistema SE/CO | horária | 17 543 | 1 | 24 | carga (MWmed) |
| BR2_ONS_Carga_N | ONS, curva de carga horária 2023–2024, subsistema Norte | horária | 17 543 | 1 | 24 | carga |
| BR3_ONS_Eolica_NE | ONS, balanço de energia por subsistema 2023–2024, Nordeste | horária | 17 543 | 6 | 24 | geração eólica |
| BR4_ONS_Solar_NE | idem | horária | 17 543 | 6 | 24 | geração solar |
| BR5_BCB_USDBRL | Banco Central do Brasil, SGS série 1 (dólar comercial, venda), 2005–2024 | diária (úteis) | 5 020 | 1 | — | taxa de câmbio |
| R1_UCI_AirQuality_CO | UCI Air Quality (Itália, 2004–2005) | horária | 9 356 | 12 | 24 | CO(GT) |
| R2_UCI_Tetouan_Z1 | UCI Power consumption of Tetouan city (Marrocos, 2017) | 10 min | 50 000 | 8 | 144 | consumo da zona 1 |
| R3_UCI_BikeSharing | UCI Bike sharing (Washington, 2011–2012) | horária | 17 378 | 8 | 24 | contagem de aluguéis |
| R4_Oikolab_Temp | Monash/OikoLab weather (Austrália, 2010–) | horária | 50 000 | 8 | 24 | temperatura |
| R5_Oikolab_Wind | idem, só a série de vento | horária | 50 000 | 1 | 24 | velocidade do vento |

Conjunto de informação idêntico ao BENCH-03: `X[t]` contém **todas** as variáveis em t−1 (alvo incluído), em unidades brutas; `y[t]` é o alvo em t.
Faltantes: preenchimento para frente (AirQuality: −200 = faltante; a coluna NMHC(GT), ~90 % faltante, é removida).
Séries limitadas a 50 000 pontos. Teste a partir de 0,30 T, prequencial, escalonador causal nas entradas (harness `bench01/runner.py`).
Os períodos sazonais s vêm da frequência de amostragem (diária para dados horários ou de 10 min). Nenhum período foi escolhido olhando os dados.

## 2. Modelos (≈ 37 por tarefa)

- **Objeto:** LEBRE_V042. **Referência:** LEBRE_V032.
- **Controles e filtros clássicos:** persistência, sazonal ingênuo (se houver s), ARX-NLMS, IPNLMS, C1–C4 do BENCH-01B (NLMS, RLS, defasagem fixa, só entrada atual).
- **BENCH-01B:** RZA-LMS, CCN, MUSE-RNN, GRU mínima, ESN online, VT-LMS, LRU, RSONN, ACESN, backprop contínuo.
- **River:** regressão linear SGD, HATR, ARF (só T ≤ 25 000, por custo), **AMRules** (novo) e **Passive-Aggressive** (novo).
- **Modelos novos online:** DLinear e NLinear online (Zeng et al. 2023; janela de L = max(96, 2s) do alvo, treinados online por NLMS),
  QKLMS (Chen et al. 2012; kernel gaussiano, orçamento de 500 centros), RFF-NLMS (256 features de Fourier aleatórias) e Holt-Winters aditivo online.
- **Modelos de fundação pré-treinados (zero-shot, previsão rolante de um passo, mesmo conjunto de informação):**
  Chronos-Bolt tiny (9M parâmetros) e small (48M), contexto 512; Chronos-2 (120M, out/2025), contexto 512, só com o histórico do alvo;
  **Chronos-2 com covariáveis** (todas as outras variáveis como covariáveis passadas), contexto 256 por orçamento de CPU, só em tarefas multivariadas.
  Ponto = mediana. Intervalo: [q0,05; q0,95] (90 %) no Chronos-2; [q0,1; q0,9] (80 % nominal) no Bolt, que só foi treinado nesses quantis.
  Rodam uma vez (são determinísticos). **Risco de contaminação declarado:** não é possível excluir que dados públicos (UCI, Monash)
  estejam no corpus de pré-treino; isso favoreceria os modelos Chronos.
- **Calibração dos comparadores:** grades do BENCH-01B, IPNLMS μ ∈ {0,1; 0,5} e grades próprias dos modelos novos, escolhidas pelo MSE nos
  primeiros min(15 % T, 5000) passos (dentro da parte de treino), sementes de calibração 42..44. **A LEBRE não é calibrada.**
- **Sementes de avaliação:** 7611, 7612, 7613 (varredura no repositório: livres). Métrica por tarefa: mediana das três.

## 3. Critérios primários (idênticos ao BENCH-03 e ao BENCH-03b)

| Critério | Definição | Limiar |
|---|---|---|
| K-a | NMSE < persistência | ≥ 70 % das tarefas |
| K-b | NMSE ≤ 1,25 × melhor clássico (IPNLMS, ARX-NLMS, NLMS, RLS, persistência, sazonal ingênuo) | ≥ 60 % |
| K-c | zero divergências | 100 % das execuções |
| K-d | NMSE ≤ 1,25 × LEBRE v0.3.2 | ≥ 90 % |
| K-e | cobertura do intervalo de 90 % ∈ [0,85; 0,95] | ≥ 80 % |

Rótulo: `COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` se K-a a K-e passarem; `PARTIALLY_COMPETITIVE` se ≥ 3 passarem; senão `NOT_COMPETITIVE`.

## 4. Análises secundárias (registradas, sem limiar de decisão)

- **S1 — posição geral:** rank médio da LEBRE v0.4 entre todos os modelos (online + fundação). O braço _SL fica fora do ranking.
- **S2 — contra modelos modernos:** razão de NMSE contra o melhor Chronos e contra o melhor entre DLinear, NLinear e Holt-Winters; fração de tarefas com razão ≤ 1,25.
- **S3 — K-b ampliado:** K-b com o conjunto clássico acrescido de Holt-Winters, DLinear e NLinear.
- **S4 — subconjunto brasileiro:** K-a a K-e e o rank só nas tarefas BR1–BR5.
- **S5 — intervalos:** cobertura e largura relativa (largura média / desvio-padrão do teste) da LEBRE contra os Chronos.
- **S6 — custo:** FP/passo e memória (modelos instrumentados); ms/passo de parede para todos, incluindo Chronos (CPU, 16 threads). FP não é energia.
- **S7 — braço exploratório `_SL`:** LEBRE_V042_SL e IPNLMS_SL recebem, **pelo ambiente**, a defasagem sazonal y[t−s] como entrada extra
  (tarefas com s). Pergunta: a lacuna para os modelos de janela é falta de memória sazonal na entrada? Serve só para orientar a próxima versão.
  O resultado não altera a v0.4.
- **S8 — explicabilidade:** número de átomos estruturais ativos ao fim e número de eventos de ciclo de vida.

## 5. Expectativas declaradas antes da execução

Em séries sazonais de alta frequência, modelos com janela longa (sazonal ingênuo, Holt-Winters, DLinear, Chronos) devem ter vantagem, porque
os filtros adaptativos veem só t−1 e os átomos de defasagem da LEBRE cobrem até 32 passos (alcançam s = 24, mas não s = 144),
precisando de evidência estatística para entrar. O câmbio (BR5) é quase um passeio aleatório; ali ninguém
deve superar a persistência com folga. Se a LEBRE ficar atrás dos modelos modernos, isso será reportado como está.
