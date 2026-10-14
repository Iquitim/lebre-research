# Auditoria de estresse da v0.54: relatório

**Data:** 13/10/2026. Plano e sinais de alerta em `PLANO_AUDITORIA.md` (commit `b7e7ea5`, antes de rodar); scripts
`auditoria.py` (T1 a T9) e `analise_auditoria.py` neste diretório, e `analises/auditoria_v054_e20.py` no LEBRE Lab (T10).
v0.54 = protótipo no commit `cfe72ce` (M5a + M5b + M4); v0.53 = `lebre==0.2.0`. Resumo numérico em
`analise_resultados.json`; T10 em `analises/AUDITORIA_V054_E20_RESULTADO.md` do Lab. Nada foi ajustado depois de ver os
resultados.

## Veredito

A v0.54 **não tem defeito de correção nem falha catastrófica**, e entrega o que promete no custo médio. A auditoria
encontrou **dois defeitos reais** que a avaliação final não cobria, e um alerta que é artefato:

| Alerta | Natureza | Gravidade |
|---|---|---|
| T5/T6 (intermitência) | **Real, M4:** uma relação que some por mais de ~5.200 passos é removida e precisa ser redetectada quando volta | +10% de erro com blocos de 7.500 passos, +5,5% com 10.000, +4,6% com 15.000; 3,4 eventos por série contra 1,0 |
| T8 (pico de custo) | **Real, M5b:** a atualização do relatório de equivalentes a cada 31 passos coincide periodicamente com a regressão da M1 | pico por passo +3,5% com 10 entradas, +11% com 20, +50% com 50; custo médio menor em todos os casos |
| T2 (alvo constante) | **Artefato:** MSE de ~10⁻³² nos dois modelos (arredondamento da máquina) | nenhuma |

## Resultados, teste por teste

**T1. Identidade e determinismo: passou.** Em 6 casos (sem ciclo, ciclo 24, ciclos 24 e 168, faltas, quarentena,
d = 8 com referência zero): com as mudanças desligadas, a v0.54 é idêntica à v0.53 passo a passo; o modo só-núcleo é
idêntico ao `LebreCore`; duas execuções dão o mesmo resultado; `step` dá o mesmo que `predict` + `observe`.

**T2. Robustez: passou** (fora o artefato). Nenhuma previsão não finita em 39 séries de 12 tipos de estresse.

| Tipo | v0.54 ÷ v0.53 (geo) | máx | custo médio v0.53 → v0.54 |
|---|---|---|---|
| picos de 10⁶ | 1,0000 | 1,0000 | 831 → 738 |
| entrada travada | 1,0000 | 1,0000 | 887 → 591 |
| 30% de alvo faltante | 1,0000 | 1,0000 | 692 → 479 |
| 10% de entradas NaN | 1,0000 | 1,0000 | 885 → 581 |
| escala 10⁻⁸ e 10⁸ | 1,0000 | 1,0000 | 773 → 779; 844 → 555 |
| degrau ×10 | 0,974 | 1,000 | 923 → 634 |
| AR(0,999) | 1,0000 | 1,0000 | 930 → 958 |
| caudas t(1,5) | 1,005 | 1,016 | 869 → 841 |
| d = 1 | 1,0000 | 1,0000 | 537 → 432 |
| d = 50, T = 500 | 1,0000 | 1,0000 | 3.904 → 3.017 |
| T = 200.000 | 1,0000 | 1,0000 | 1.391 → 681 |
| alvo constante | 1,053 (artefato: MSE ~10⁻³²) | | 1.059 → 750 |

**T3. Nulos: passou.** Em 100 séries sem nenhuma relação, nenhuma entrada externa foi aceita, em nenhum momento, pela
v0.54 nem pela v0.53. Razão de erro 0,996.

**T4. Entradas verdadeiras fracas: passou.** Nenhuma remoção da entrada verdadeira em 80 séries (efeitos de 0,05 a 0,4).
A v0.54 ficou igual ou melhor (0,982 a 1,001).

**T5. Intermitência: alerta, defeito real da M4.**

| Bloco ligado/desligado | v0.54 ÷ v0.53 | máx | remoções (10 séries) |
|---|---|---|---|
| 1.000 | 1,016 | 1,110 | 2 |
| 2.500 | 1,000 | 1,000 | 0 |
| 5.000 | 1,000 | 1,000 | 0 |
| 7.500 | **1,100** | 1,146 | 36 |
| 10.000 | **1,055** | 1,094 | 28 |
| 15.000 | 1,046 | 1,088 | 20 |

**Mecanismo, medido nos eventos.** O teste de remoção disparado abre quando a contribuição cai e aceita depois da duração
mínima de 5.000 passos. As remoções caem, em mediana, entre 5.155 e 5.205 passos depois do início do bloco desligado.
Quando a relação volta, a readição leva em mediana 675 a 920 passos, e até 2.250. Esse sinal perdido em cada bloco ligado
é o que custa o erro. Blocos de até 5.000 passos não chegam a disparar a remoção.

**Por que importa.** Relações sazonais reais têm esse formato em dados horários, como o efeito da temperatura no
consumo que só existe numa estação. A avaliação final não mostrou o problema: houve 1 remoção em 93 séries e nenhuma
piora. Mas a reserva não tinha séries longas com relações que somem e voltam.

**Leitura pela filosofia.** Remover o que a evidência deixou de sustentar é exatamente o princípio da M4, e cada
remoção é estatisticamente válida para o episódio testado. O problema é de custo de oportunidade, não de validade: a
LEBRE não tem memória de que aquela relação já existiu, então trata a volta como uma descoberta nova.

**T6. Oscilação: alerta, mesma causa do T5.** Nos demais testes, os eventos por série da v0.54 são praticamente os da
v0.53 (T2: 2,49 contra 2,33; T3: 0 e 0; T4: 0,31 e 0,31; T7: 3,18 contra 3,15).

**T7. Despertar da M1: passou.** Nas 4 variantes (troca abrupta ou gradual, depois de 20.000 ou 40.000 passos), a razão
de erro no trecho depois da troca ficou entre 0,997 e 1,003 (máximo de uma série: 1,031). A M1 dormiu em 40 de 40 séries.

**T8. Honestidade do custo: alerta no pico, defeito real da M5b.**

- **Custo médio:** menor em quase todos os grupos (por exemplo, de 1.391 para 681 em T = 200.000). As exceções são
  pequenas: +3% em AR(0,999) e +1% em escala 10⁻⁸.
- **Tempo de relógio:** a mediana da razão v0.54 ÷ v0.53 foi 0,845, ou seja, a economia contada aparece também no tempo
  real.
- **Pico por passo:** igual ao da v0.53 em todos os grupos, exceto com muitas entradas. Medido à parte (3.000 passos,
  sem e com a M5b):

| Entradas | pico v0.53 | pico v0.54 | pico v0.54 sem a M5b |
|---|---|---|---|
| 5 | 6.009 | 5.897 | 5.972 |
| 10 | 6.265 | 6.485 | 6.280 |
| 20 | 6.583 | 7.333 | 6.598 |
| 50 | 7.837 | 11.724 | 7.852 |

**Causa.** No núcleo da v0.53, a atualização da matriz de covariâncias a cada 4 passos tem fase fixa, escalonada para
nunca coincidir com a regressão da M1, que roda a cada 8 passos. O escalonamento foi introduzido na v0.52 justamente para
cortar picos. Com o passo 31 da M5b, a fase percorre todos os restos e coincide com a regressão da M1 uma vez a cada 248
passos. A M5b não muda previsões, mas quebra esse escalonamento. Para um microcontrolador, o pico importa tanto quanto a
média.

**T9. Crescimento do estado: passou.** Nenhum contêiner cresce só na v0.54; os que crescem são os mesmos nas duas versões.
Há uma observação **anterior à v0.54**, não introduzida por ela: a lista de eventos (`events`) cresce sem limite nas duas,
de 80 para 315 entradas com d = 5 e de 176 para 713 com d = 50, entre 50.000 e 200.000 passos. Num dispositivo
embarcado, ela precisaria ser limitada ou descartável.

**T10. A combinação inteira no banco do E20: passou.** Nas 64 famílias, nenhum limite superior acima de 1,02 e nenhuma
previsão não finita. Pior caso: YB03, 1,0000 (IC 0,9929 a 1,0072). A07: 1,0051 (IC até 1,0061), o efeito do T5 no
gerador com blocos de 5.000. A05: 0,9946.

## O que isto diz sobre a v0.54 e a filosofia da LEBRE

| Princípio | Situação na v0.54 |
|---|---|
| Mudar só com evidência sempre válida | Mantido: nenhuma entrada falsa em 100 nulos; nenhuma remoção falsa em 80 séries com efeitos fracos |
| Sem falhas catastróficas | Mantido: nenhuma previsão não finita em nenhum estresse; pior piora encontrada: +14,6% numa série intermitente |
| Sem ajuste por série | Mantido: as mesmas constantes em tudo |
| Estrutura que reflete o presente | Mantido, com custo: a M4 remove o que sumiu, mas não tem memória do que costuma voltar |
| Custo declarado e honesto | **Parcial:** a média cai e o tempo real acompanha, mas o pico sobe com muitas entradas (M5b) |
| Gastar só onde há uso (v0.54) | Mantido: onde a M1 é útil, o custo fica igual; onde não é, cai |

## Recomendações (decisão do responsável pelo projeto)

1. **M5b, pico de custo.** A correção é pequena e não muda previsões: pular, ou adiar um passo, a atualização da matriz
   quando ela coincidir com a regressão da M1. Ainda exige o processo: rascunho, teste de identidade, medição do pico e
   errata da v0.54.
2. **M4, relações que voltam.** Não há correção trivial. Os caminhos possíveis são:
   - readição rápida de uma unidade removida há pouco, partindo dos pesos que ela tinha;
   - duração mínima de remoção ligada ao histórico da unidade;
   - ou declarar a limitação.

   Qualquer mudança aqui altera previsões e precisa do processo completo, provavelmente na v0.55.
3. **Publicação.** Publicar a v0.54 como está exige declarar os dois defeitos na spec e nas notas de versão. A
   alternativa é publicar uma v0.54 revisada com a correção da M5b, que é neutra para as previsões, e a limitação da M4
   declarada.
