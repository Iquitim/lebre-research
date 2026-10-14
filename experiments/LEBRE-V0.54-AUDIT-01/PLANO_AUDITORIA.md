# Auditoria de estresse da v0.54 (pós-promoção): plano e sinais de alerta, escritos e commitados antes de rodar

**Data:** 13/10/2026. **Pedido do responsável pelo projeto:** estressar a v0.54 e verificar se ela está adequada e fiel à
filosofia da LEBRE, com o máximo de critério.

**O que esta auditoria é e o que não é.** A promoção foi decidida pela avaliação final pré-registrada (reserva consumida).
Esta auditoria **não refaz nem substitui** aquela decisão: ela procura defeitos que a avaliação não cobriu. Um sinal de
alerta vira errata declarada da v0.54. Se for grave (defeito de correção, falha catastrófica ou violação de um princípio),
a recomendação é não publicar a v0.54 como está até haver correção, com o processo completo.

**O que se testa.** A v0.54 promovida: protótipo no commit `cfe72ce`, `Lebre054(d, ..., m5a=True, m5b=True, m4=True)`,
contra a v0.53 = `lebre==0.2.0` (`lebre.Lebre`, mesmos argumentos). Ambiente do LEBRE Lab (Python 3.11.9, numpy 2.2.5).

**A filosofia da LEBRE, como critério:**

1. Mudar a estrutura só com evidência sempre válida, a custo conhecido.
2. Não ter falhas catastróficas.
3. Não precisar de ajuste por série.
4. Estrutura interpretável, que reflete o que importa agora.
5. Custo declarado e honesto, médio e de pico.
6. Estado limitado, para caber em microcontrolador.

A v0.54 acrescenta dois pontos: gastar só onde há uso, e a estrutura também sair quando a evidência deixa de sustentá-la.

**Sementes:** toda série sintética vem de `numpy.random.default_rng([2026101300, teste, tipo, k])` (faixa 2026101300 a
2026101499 conferida como livre nos três repositórios). Bootstrap, quando houver: semente 2026101301.

## Testes e sinais de alerta (fixados antes)

| # | Teste | O que verifica | Sinal de alerta |
|---|---|---|---|
| T1 | **Identidade e determinismo**: v0.54 com `m5a=m5b=m4=False` contra `lebre==0.2.0`; `core_only=True` contra `lebre.LebreCore`; duas execuções iguais; `step` contra `predict` + `observe`, em 6 séries variadas (com ciclo, sem ciclo, com faltas, com quarentena) | correção | qualquer diferença |
| T2 | **Robustez** (12 tipos × 3 séries): alvo constante; picos de 10⁶; entrada travada; 30% de alvo faltante em blocos; entradas com NaN; escala 10⁻⁸ e 10⁸; degrau de nível ×10; AR(0,999); caudas t(1,5); d = 1; d = 50 com T = 500; T = 200.000 | falhas catastróficas | previsão não finita em algum passo; razão de MSE v0.54 ÷ v0.53 > 1,05 na média geométrica de um tipo ou > 1,5 em alguma série |
| T3 | **Nulos** (100 séries: alvo AR(0,6), 5 entradas AR independentes, T = 20.000) | estrutura falsa | mais séries com entrada externa na estrutura final na v0.54 que na v0.53 |
| T4 | **Entradas verdadeiras fracas** (efeito b ∈ {0,05; 0,1; 0,2; 0,4}, 20 séries cada, T = 30.000, estacionárias) | remoção falsa (M4) | com b ≥ 0,2, entrada verdadeira removida em mais de 1 de 20 séries; em qualquer b, razão de MSE > 1,02 |
| T5 | **Intermitência** (blocos ligado/desligado de 1.000, 2.500, 5.000, 7.500, 10.000 e 15.000 passos; 10 séries cada; T = 60.000) | o ponto fraco conhecido da M4 | razão de MSE > 1,05 em algum comprimento de bloco |
| T6 | **Oscilação**: eventos aceitos (adições e remoções) por série, em T2 a T5 | churn | média da v0.54 > 2 × a da v0.53 + 1 em algum teste |
| T7 | **Despertar da M1** (M1 inútil por 20.000 ou 40.000 passos e depois útil, abrupto ou gradual; 10 séries cada) | M5a não pode deixar de reagir | razão de MSE no último trecho > 1,02 |
| T8 | **Honestidade do custo**: custo por passo (média, p99 e máximo) e tempo de relógio, em T2 a T5 | custo médio e de pico | pico da v0.54 > 1,10 × o da v0.53 em algum tipo; mediana do tempo de relógio da v0.54 > 1,10 × a da v0.53 |
| T9 | **Crescimento do estado**: tamanho de todas as listas e dicionários do modelo aos 50.000 e aos 200.000 passos (d = 5 e d = 50) | estado limitado | algum contêiner da v0.54 que cresce com T e não cresce na v0.53 |
| T10 | **Banco completo com a combinação**: a v0.54 inteira (M5a + M5b + M4) contra `lebre==0.2.0`, nas 64 famílias do E20 do LEBRE Lab, que só tinham visto cada M separada | interação entre as M | limite superior do IC 95% (bootstrap de blocos pareado, semente 2026101301) > 1,02 em alguma família |

**Regra:** cada sinal de alerta é investigado e relatado com a causa. Nenhum teste, limite ou código é ajustado depois de
ver resultados. O relatório (`RELATORIO_AUDITORIA.md`) traz todos os números, inclusive os que não acenderam alerta.
