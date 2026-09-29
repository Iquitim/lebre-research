# 16 — O que a "estabilidade" mede

Protocolo: a mesma janela final de teste, com 0, 50, …, 450 passos iniciais descartados.

- **Mede:** sensibilidade do resultado à inicialização e ao período de aquecimento (*burn-in*). Ou seja, se o modelo converge para o mesmo desempenho independentemente de como começou.
- **Não mede:** estabilidade entre trechos diferentes da série (regimes, estações, anos), nem variância entre janelas independentes. Nenhuma janela independente foi avaliada.
- **Nome adequado:** "sensibilidade à inicialização (burn-in)". A frase "estável" na especificação deve ser restrita a esse sentido. Não se pode afirmar robustez temporal.
