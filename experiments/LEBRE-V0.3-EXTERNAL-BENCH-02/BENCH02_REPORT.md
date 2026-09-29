# BENCH-02 — Relatório (benchmark externo extenso da LEBRE v0.3.2)

**Pré-registro:** `PREREG_BENCH02.md` (SHA-256 em `PREREG_BENCH02_SHA256.txt`), escrito antes da execução. Modelo: `lebre_v032.py` congelado e sem calibração.
**Escala:** 25 tarefas em 4 trilhas, 24 modelos, 3.425 execuções, 69 minutos em 16 processos. Resultados: `BENCH02_RESULTS.csv`; análise: `analyze_bench02.py`.

## 1. Decisão pré-registrada

| Critério | Resultado |
|---|---|
| E1: posição global da LEBRE v0.3.2 pelo rank médio | **6ª de 24** (rank médio 8,44) |
| Top-3 em alguma trilha | **nenhuma** (A: 6ª, B: 5ª, C: 6ª, D: 12ª) |
| E3: skill > 0 contra a persistência **e** top-3 | 4/25 = **0,16** |
| **Decisão** | **`NOT_JUSTIFIED_EXTERNALLY`** |

## 2. Ranking global (rank médio pelo NMSE mediano por tarefa)

| Posição | Modelo | Rank médio | Nº de vitórias | Top-3 | Divergências |
|---|---|---|---|---|---|
| 1 | IPNLMS (Benesty & Gay 2002) | 3,40 | 6 | 16 | 0 |
| 2 | CTRL_ARX_NLMS | 7,20 | 3 | 8 | 0 |
| 3 | River SGD LinReg | 7,80 | 0 | 8 | 6 |
| 4 | B2_CCN | 8,12 | 0 | 4 | 19 |
| 5 | River HATR | 8,24 | 2 | 5 | 0 |
| **6** | **LEBRE v0.3.2** | **8,44** | **2** | **4** | **0** |
| 7 | River ARF-Reg | 9,36 | 3 | 5 | 4 |
| 10 | Persistência | 10,20 | 8 | 12 | 0 |
| 11 | Track B (LEBRE v0.1) | 10,36 | 0 | 0 | 3 |

## 3. Por trilha

**A — previsão online (ETT, Exchange, Jena, ECL, Traffic).** A persistência e o ARX dominam, como é esperado em séries horárias próximas de raiz unitária.
A LEBRE vence no **ECL** (0,086 contra 0,097 da persistência). Nas outras 7 tarefas fica atrás da persistência, até 40× no ETTm2 (0,048 contra 0,0012).
O NLMS simples sobre as mesmas entradas padronizadas é ainda pior (0,25–0,36). **Hipótese** (não verificada): o passo fixo μ = 0,1 e a representação padronizada do termo
autorregressivo tornam a adaptação lenta; IPNLMS (μ = 0,5 calibrado) e ARX (`y_{t−1}` bruto) não têm esse problema.

**B — regressão em fluxo com deriva.** Nas tarefas sintéticas não lineares (Friedman, Mv, Planes2D) as árvores do River (HATR, ARF) vencem, porque a LEBRE é linear.
Mesmo assim, a LEBRE fica em 2º na Friedman GRA e GSG, com skill ≈ 0,85 contra a persistência. Nos dados reais pequenos (TrumpApproval, WaterFlow) a persistência domina, e a LEBRE falha no WaterFlow (NMSE 4,98).

**C — identificação não linear.** A LEBRE é **1ª no Wiener–Hammerstein, com NMSE 0,0032 contra 0,0177 do 2º (CCN)**, 5,5× melhor e a 3/3 sementes.
No EMPS e no Cascaded Tanks a amostragem fina torna `y_{t−1}` quase perfeito e a persistência vence.

**D — sistemas FIR esparsos.** **O IPNLMS vence as 6 condições** (NMSE ≈ 0,02). A LEBRE com linha de atrasos fica entre ≈ 0,05 e 0,07 (rank 11–14).
Na representação nativa (D = 1, usando o dicionário de atrasos) ela melhora para K = 1 (0,043 e 0,055), mas piora para K = 8 (0,22 e 0,27) porque o orçamento M_max = 4 não comporta 8 taps.
**A LEBRE perde, no seu próprio terreno de atrasos esparsos, para um algoritmo clássico de 2002.**

## 4. Pontos a favor

- **0 divergências em 152 execuções.** Entre os 6 primeiros, só IPNLMS, ARX e HATR também têm 0; CCN (19), SGD (6) e ARF (4) divergem.
- Maior skill mediano contra a persistência entre os 12 primeiros (+0,506), ou seja, raramente é pior que "não fazer nada" por grande margem, exceto em séries de raiz unitária.
- Melhor resultado absoluto do benchmark num sistema não linear clássico (Wiener–Hammerstein).
- Em 5 tarefas fica na fronteira de Pareto NMSE × FLOPs.

## 5. Interpretação

1. A **arquitetura** é válida e se comporta como especificado: decisões estatisticamente controladas e zero divergências.
2. Mas **a competitividade externa não se sustenta**. Os mecanismos de ciclo de vida não compensam três lacunas da v0.3.2:
   (a) ausência de átomos autorregressivos do alvo em unidades próprias, que domina a trilha A e os dados reais;
   (b) passo fixo do NLMS, sem proporcionalidade por coeficiente — o IPNLMS mostra que um *ganho proporcional à magnitude do coeficiente* basta para vencer em sistemas esparsos;
   (c) classe linear, que perde para árvores em regressão não linear com deriva.
3. As evidências internas positivas (I1–I14, BENCH-01) vêm de benchmarks cujo desenho favorece a decomposição base + atraso + latente. O BENCH-02, mais amplo, mostra essa limitação.

## 6. O que isso sugere para a v0.4 (hipóteses, cada uma exigindo nova avaliação held-out)

1. Átomo AR do alvo em unidades próprias (`y_{t−k}` bruto e diferenças), o que recupera persistência e ARX como casos particulares.
2. Ganho proporcional (tipo IPNLMS) dentro do NLMS dos átomos ativos, uma troca local e fundamentada (Benesty & Gay 2002).
3. Orçamento estrutural adaptativo, ou M_max derivado do custo, para sistemas com muitos taps.
4. Átomos não lineares baratos (termos quadráticos ou por partes), testados pelo mesmo ciclo de vida.

## 7. Ressalvas de protocolo

- Os baselines do BENCH-01B foram calibrados em min(15% T, 5000) passos. IPNLMS teve grid de μ; LEBRE, ARX e os modelos do River rodaram sem calibração (padrões).
- Os resultados de identificação (trilha C) são de predição de 1 passo e **não são comparáveis** aos números publicados de simulação livre.
- A trilha A usa h = 1 com informação em t−1. Os artigos FSNet/OneNet usam janelas e horizontes maiores com MSE normalizado, então não há comparação direta de números.
- O Mv tinha atributos categóricos, tratados com one-hot determinístico (esclarecimento de protocolo registrado aqui, porque o pré-registro não especificava).
- Semente CED não disponível por falha de rede, e ParWH não incluído (múltiplos experimentos). Registrado.
