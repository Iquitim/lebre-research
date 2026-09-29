# Relatório de revisão — LEBRE v0.3 → v0.3.1 → v0.3.2

**Escopo:** auditoria de código, testes de propriedades, benchmark interno confirmatório, benchmark externo (BENCH-01 com sementes novas,
BENCH-01 com colunas permutadas, 3 datasets reais novos) e revisão de literatura.
**Governança:** exploratório-confirmatório e não canônico. `src/`/`tests/` intactos; M3 `UNOPENED`; nenhuma afirmação de novidade.
Pré-registros com hash: `PREREG_V03_REVIEW_BENCHMARKS.md` (Partes I–III) e `PREREG_ADDENDUM_V032.md` (Partes IV–VI).

## 1. Versões

| Versão | O que é | Hash |
|---|---|---|
| v0.3 (iter4) | versão avaliada originalmente | `FREEZE_ITER4_SHA256.txt` |
| v0.3.1 | correções de validade F1–F5 (teste auto-normalizado, equivariância de escala, piso numérico, rótulo, contabilidade) | `FREEZE_V031_SHA256.txt` |
| v0.3.2 | v0.3.1 + F6 (aquecimento por média amostral; corrige o τ≈1e13 introduzido por F3) | `FREEZE_V032_SHA256.txt` |

**Recomendada:** v0.3.2, a única que passa todas as propriedades de validade e tem o melhor resultado interno.

## 2. Auditoria e propriedades (detalhes em `LEBRE_V03_CODE_AUDIT.md`)

| Propriedade | v0.3 | v0.3.1 | v0.3.2 |
|---|---|---|---|
| Causalidade | ✅ | ✅ | ✅ |
| Alinhamento de atrasos (30/30) | ✅ | ✅ | ✅ |
| Falsas promoções por fluxo: gauss / t₃ / hetero (limite 0,052) | 0,005 / **0,26** / **0,21** | 0 / 0 / 0 | 0 / 0 / 0 |
| Remoções falsas | 4 em 1,14M passos | 4 em 1,14M | 4 em 1,16M |
| MSE latente / Kalman ótimo (mediana; máx) | 1,18; 1,97 | 1,18; 1,91 | 1,17; 1,64 |
| Eventos durante o silêncio | **1,67** | 0 | 0 |
| NMSE com y ×10⁻³ / ×1 / ×10³ | 0,25 / 0,19 / **0,40** | 0,19 / 0,19 / 0,19 | 0,20 / 0,20 / 0,20 |
| Tempo médio até a 1ª promoção (T4) | 1448 | 1531 | 1105 |

## 3. Benchmark interno I1–I14 (confirmatório)

| Parte | Sementes | Versão | NMSE | vs v0.2 A0 | vs ARX | FP | Estrutura exata |
|---|---|---|---|---|---|---|---|
| I | 2116..2145 | v0.3.1 | 0,223 | −0,091 (30/30) | −0,115 (30/30) | 97,8 | 86,5% contra 75,2% |
| V | 2146..2175 | **v0.3.2** | **0,219** | **−0,091 (30/30)** | **−0,118 (30/30)** | **96,9** | **88,6% contra 75,2%** |

Todas as hipóteses pré-registradas (superioridade, gate ≤ 100 FP, valor além do ARX, explicabilidade) **passam com Holm, p < 1e-5**.
Salvaguardas: I13 +20–24 passos de latência (≤ +50 ✅); I11, I12 e I14 muito melhores; reativação da I7 ~60 contra ~96 passos.
A v0.3.2 é melhor que a v0.3.1 em NMSE (−0,0047, p = 0,03) e em estrutura (+2,9 pp, p = 0,001).
**Pontos fracos internos:** a I4 (3 atrasos) ficou pior na v0.3.2 (0,289 contra 0,183 da v0.3.1) e custa 104,5 FP (> 100 nessa tarefa, embora a média respeite o gate).
Na I10 (autorregressão do alvo) o ARX trivial ganha de todas as versões (0,111).

## 4. Benchmark externo

### 4.1 BENCH-01 sintético (A1–A8, H1, H2) — 19–20 modelos, baselines com calibração original

| Cenário | Sementes | 1º | 2º | 3º | Melhor do campo (rank) | Track B (rank) |
|---|---|---|---|---|---|---|
| Parte II, colunas originais | 131..160 | v0.3 (3,1) | v0.3.1 (3,8) | — | S3_RSONN (6,7) | 13,8 |
| **Parte IV, colunas permutadas** | 161..190 | **v0.3 (3,1)** | **v0.3.1 (3,9)** | **v0.3.2 (4,0)** | S3_RSONN (6,9) | 13,5 |

- **Artefato do BENCH-01 confirmado:** as dependências verdadeiras de A2–A4 e H1 estão na coluna 0. Com as colunas permutadas, C4 (só coluna 0)
  cai do rank 7,3 para 16,9 e S1 do 8,4 para 15,5. A v0.3 também perdia parte da vantagem na A3 (0,005 → 0,18), que vinha da ordem do dicionário.
- A família LEBRE v0.3 continua **à frente de todo o campo** com colunas permutadas. A v0.3.2 vence o Track B em 9 de 10 tarefas (30/30 sementes)
  e vence o melhor modelo calibrado de cada tarefa em 8 de 10 (perde na A1 para o RZA-LMS e na A6 para o RSONN).
- **Custo da validade:** a v0.3 original é melhor que a v0.3.2 nas tarefas de quiescência A5/A7 (0,046 contra 0,114) e na A3, porque o teste
  auto-normalizado é mais conservador. É uma troca explícita entre poder e validade.
- **Recursos:** com D de 10 a 50, a família v0.3 gasta cerca de 209 FLOPs e ~5 KB. **Nenhuma tarefa atende o envelope do BENCH-01 (≤ 100 FLOPs, ≤ 1 KB).**

### 4.2 Dados reais nunca usados (UCI: Appliances, Beijing PM2.5, Metro Traffic)

| Dataset | Persistência | ARX | v0.3 | v0.3.1 | v0.3.2* | Melhor baseline calibrado |
|---|---|---|---|---|---|---|
| X1 Appliances | **0,520** | 0,821 | 1,079 | 0,676 | 0,698 | C2_NLMS 0,611 |
| X2 PM2.5 | **0,066** | 0,085 | 0,224 | 0,133 | 0,121 | Track B 0,225 |
| X3 Metro | **0,170** | 1,564 | 19,2 | 10,1 | 5,40 | S3_RSONN 0,977 |

\* A v0.3.2 é semi-held-out (a correção F6 veio da A3 sintética; os resultados da v0.3.1 nesses dados já tinham sido vistos).

- **A persistência trivial (`ŷ = y_{t-1}`) vence todos os modelos nos três datasets.** Em séries reais horárias ou de 10 minutos o alvo é dominado
  pela autocorrelação, e nenhum modelo do campo usa `y_{t-k}` diretamente como regressor.
- A v0.3.2 fica em 2º–3º no X2 e ganha de todos os baselines calibrados ali. No X1 fica no meio do campo.
- **O X3 revelou uma falha de robustez:** um único registro errado do dataset (`rain_1h = 9831,3` mm/h) vira uma entrada de milhares de σ e
  produz um erro de 1,1×10⁶ num passo. Isso domina o NMSE (os demais decis ficam em 0,23–0,42). Todos os modelos lineares sofrem com isso;
  a v0.3.x não tem proteção contra outliers de entrada.

## 5. Literatura (detalhes em `LEBRE_V03_LITERATURE_REVIEW.md`)

Os mecanismos da v0.3.2 estão bem ancorados: forma de inovações de Kalman (Ljung 1999); promoção por martingale auto-normalizado, com a desigualdade de Ville e
de la Peña (1999), conferida no texto de Howard et al. (2020, Lema 3(d)); CUSUM (Page; Lorden 1971; Moustakides 1986); NLMS (Slock 1993);
excitação persistente (Ioannou & Sun 1996). A arte anterior mais próxima da seleção estrutural em fluxo é o **alpha-investing**
(Zhou, Foster, Stine & Ungar, KDD 2005 / JMLR 2006). O **DMA** (Raftery et al. 2010) é o comparador bayesiano natural. **Nenhum dos dois foi comparado ainda.**
As garantias valem sob hipóteses idealizadas; no laço adaptativo são aproximadas e foram checadas empiricamente (Seção 2).

## 6. Veredito

1. **Interno (I1–I14):** a v0.3.2 é uma evolução clara e confirmada da v0.2. Tem NMSE 29% menor, custo menor (96,9 contra 111,2 FP),
   explicabilidade melhor (88,6% contra 75,2%) e decisões estruturais estatisticamente válidas e invariantes à escala.
2. **Externo sintético:** a família v0.3 lidera um campo de 15 baselines calibrados, mesmo depois de remover o artefato de colunas do BENCH-01.
3. **Externo real:** **a existência ainda não se justifica em dados reais.** A persistência trivial vence em todos, e há uma falha de robustez a outliers.
4. **Recursos:** o orçamento de 100 FP vale para D=5. Para D alto o custo é O(D) e a memória passa de 1 KB.

## 7. Prioridades para a v0.4 (em ordem de impacto esperado; cada item exige nova avaliação held-out)

1. **Átomos autorregressivos do alvo `y_{t-k}`** no dicionário, com o mesmo teste e o mesmo CUSUM. Isso ataca de uma vez a I10, A5/A7, H1 e os três
   datasets reais, onde a persistência e o ARX vencem. Deveria recuperar a persistência como caso particular.
2. **Robustez a outliers de entrada:** recorte das entradas padronizadas ou perda de Huber na predição e na evidência. É preciso decidir com base
   em princípio, não ajustar ao X3.
3. **Busca sublinear em D:** a triagem por varredura rotativa leva cerca de D·32/2 passos por ciclo. Com D=20 a descoberta demora centenas a milhares de passos.
   Alternativa fundamentada: triagem por correlação agregada por feature antes de escolher o atraso.
4. **Mais poder sem perder validade:** trocar Bonferroni por alpha-investing ou e-values com controle de FDR/FWER. Isso deve recuperar o
   que se perdeu em A3, A5 e A7 em relação à v0.3.
5. **Polos fundamentados** (critério de bases ortonormais) e **latente de 2ª ordem** (H1).
6. **Comparadores ausentes:** DMA, alpha-investing + ARX e ARX com seleção por RIC.
7. **Memória/fp16:** validar numericamente o armazenamento em fp16 e reduzir o histórico para caber em 1 KB.

## 8. Desvios e ressalvas

- O pré-registro diz "(26)" features para o X1, mas a lista explícita tem 25. Vale a lista (erro de contagem).
- A v0.3.2 nasceu de uma falha vista na Parte II. Por isso foi avaliada em sementes novas (Partes IV e V), e nos dados reais é semi-held-out.
- O modelo V03 (iter4) passou por 4 iterações de DEV nas sementes 3301..3310. Todas as avaliações acima usam sementes diferentes dessas.
