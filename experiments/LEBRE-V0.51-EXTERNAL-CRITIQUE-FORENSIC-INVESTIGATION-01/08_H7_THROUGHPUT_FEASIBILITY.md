# 08 — H7: viabilidade da latência ≤ 2000 passos

## Parâmetros do código autoritativo
- **Triagem:** 2 candidatos por passo, entre d·L = 160, então cada candidato é sondado a cada 80 passos. O escore é uma EMA (w = 0,2) de e·x_lag.
- **Testes:** 4 vagas para atrasos, mais 1 candidato por polo latente (enquanto não há latente ativo), mais d candidatos de acionamento (depois do latente). Uma amostra de teste a cada 2 passos; futilidade após T_max = 200 amostras, isto é, 400 passos; decisões a cada 10 passos.
- **Limiar:** log(p/α) = log(169/0,05) = 8,13 nats.

## Limite inferior teórico
Com ranking perfeito, sem candidatos falsos e elegibilidade imediata:
- **Proposta:** até 20 + 80 + 10 ≈ **110 passos**.
- **Teste:** as amostras até cruzar o limiar foram medidas em **90–150** (ledger 06), ou seja, ~180–300 passos.
- **B1** (1 átomo): **≈ 300 passos**.
- **B2** (3 átomos, 3 das 4 vagas em paralelo): **≈ 420 passos**.
- **B3:** o latente (polo 0,8) é testado desde t = 20 (~116 amostras × 2 ≈ 250 passos); o acionamento só abre depois dele (+~300), e o lag(3,12) corre em paralelo. **≈ 560 passos.**

**Conclusão:** o limite de 2.000 passos é viável por construção. `H7_GATE_DESIGN_INVALID` **não** se aplica.
A conta da crítica ("4 vagas × 500 passos, três átomos em fila passam de 2.000") supõe teste serial com duração máxima. Não vale para o código original: 3 átomos cabem em 4 vagas paralelas, e um átomo verdadeiro forte cruza bem antes de T_max.

## O que aconteceu empiricamente (código original)
| Tarefa | Átomo | Proposta (mediana) | Promoção (mediana) | ≤ 2000 passos |
|---|---|---|---|---|
| T1 | lag(1,3) | 1.450 | 1.680 | 6/10 |
| B1 | lag(1,12) | 2.065 | 2.255 | 4/10 |
| B2 | lag(0,3) / lag(2,7) / lag(4,20) | 2.265 / 2.675 / 2.870 | 2.565 / 2.990 / 8.635 | 4 / 2 / 0 de 10 |
| B3 | lag(3,12) / res(0,8) / q(0;0,8) | 2.570 / nunca / nunca | 2.820 / — / — | 5 / 0 / 0 de 10 |

- O tempo entre a abertura do teste e a promoção é de ~200–300 passos, dentro do limite teórico.
- **O atraso está na proposta.** As 4 vagas ficam ocupadas por candidatos sem sinal até a futilidade, 400 passos cada, o que dá ~1 novo candidato a cada 100 passos. Somada ao ruído da triagem (uma sonda por candidato a cada 80 passos), a mediana chega a ~20 propostas antes da verdadeira.

**Classificação:** `H7_FAILURE_SEARCH_THROUGHPUT` para os atrasos. Para o latente/acionamento do B3, a falha não é de vazão: é de elegibilidade (ver 10).
`H7_TEST_THROUGHPUT_LIMIT = MECHANISTICALLY_SUPPORTED`. O mecanismo foi observado no ledger, mas não foi isolado por intervenção, que exigiria alterar a arquitetura e é proibido nesta etapa.
