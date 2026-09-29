# Análise pós-hoc — resposta à revisão externa da v0.51

Fora do pré-registro. Script: `posthoc_feedback.py`. Resultados: `POSTHOC_FEEDBACK_METRICS.csv`, `POSTHOC_FEEDBACK_WS.csv` e `POSTHOC_FEEDBACK_NULL.csv`.
Dados: held-out da v0.51 (Q1–Q10) e held-out da v0.5 (N1–N10).

| Ponto da crítica | Veredito | Evidência |
|---|---|---|
| O resultado principal vem do M | **Procede** | "Só M" / v0.51 = 1,034 (Q) e 1,006 (N); resultado idêntico em 8/10 séries |
| w_S nas séries do ONS com d = 6 | **Procede** (S não ganha peso) | máximo de 0,053; S só pesa em câmbio (Q5, N5) e KDD (Q9, N10) |
| Holt-Winters fraco; faltam airline/ETS fortes | **Procede**, e é mais forte do que a crítica previa | Airline por MLE / v0.51 = 0,948 (9 séries) e 0,896 (9); ETS por MLE ruim (1,65×, com uma divergência) |
| HW pior que persistência em Q6 e Q10 | **Parcial** | Q6 sim (0,0452 contra 0,0321); Q10 não (0,0371 contra 0,0385) |
| Falta RLS nas 5 features | **Procede** | 0,93× quando estável, mas diverge em 7/20 séries longas |
| "3º de 15" inflado | **Procede** | Sem as versões antigas, a v0.51 é 4ª geral e 1ª entre os modelos online leves |
| NMSE favorece séries com tendência | **Não procede para as razões** | As razões por série cancelam o denominador; skill e MAE relativos foram reportados mesmo assim |
| Controle de erro por teste, não por fluxo | **Procede** (formalmente) | Empiricamente: 0 promoções falsas em 2M passos nulos |
| O aluguel quebra a garantia de ARL | **Procede** | 7 remoções do átomo verdadeiro em 1M passos estacionários; remoções = "perda de utilidade" |
| "Roda em microcontroladores" não verificado | **Procede** | Texto trocado por "dimensionado para / não verificado" |
| Explicação exata é trivial | **Procede** | Documentado; o diferencial é a seleção nomeada por evidência |

As especificações PDF (PT-BR e EN) foram revisadas com a premissa explícita, as §10–§12 novas e as versões anteriores tratadas como ablações nomeadas.
