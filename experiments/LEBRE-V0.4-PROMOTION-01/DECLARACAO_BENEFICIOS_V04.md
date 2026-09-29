# Declaração de benefícios — explicabilidade e transparência operacional da LEBRE v0.4

**Escopo:** esta declaração afirma apenas o que foi **medido** nas avaliações pré-registradas da v0.4 (`lebre_v042.py`). Cada afirmação traz a evidência e o limite.
**Terminologia:** "explicabilidade" significa responder *por que* o modelo previu ou decidiu algo. "Transparência operacional" significa
mostrar *o que está acontecendo* com o sistema agora. Evitamos o termo "observabilidade" para não colidir com a propriedade formal da teoria de controle (Kalman).

## A. Explicabilidade intrínseca

| # | Benefício | Evidência medida | Limite |
|---|---|---|---|
| E1 | **Cada previsão é a soma exata de contribuições nomeadas** (viés, entradas atuais, "x1 atrasado 6 passos", "estado latente τ≈5 alimentado por x0") | T9: diferença máxima entre ŷ e Σ contribuições **= 0** em 260 fluxos e em 420 execuções internas | fidelidade ao **modelo**, não causalidade física (relevância preditiva no sentido de Granger) |
| E2 | **A estrutura recuperada corresponde à verdade** em processos conhecidos | 91,7% dos checkpoints exatos (v0.3.2: 89,6%; v0.2: 72,0%); 100% em I1, I2, I3, I6 e I7 | pior em estrutura intermitente (I14: 71,7%); estruturas redundantes (I10) não têm explicação única |
| E3 | **Toda decisão estrutural tem justificativa estatística citável** (evidência em nats, taxa de erro controlada) | 0 promoções falsas em 400 fluxos nulos (gaussiano, t₃, heterocedástico); 5 remoções falsas em 1,16M passos | garantias exatas só sob hipóteses idealizadas; no laço adaptativo são aproximadas e foram verificadas empiricamente |
| E4 | **Explicações parcimoniosas** | ~1,2 átomos estruturais ativos em média, além da base | quando a informação chega como entrada atual (linha de atrasos, Friedman), a explicação fica nos pesos da base |
| E5 | **Explicações estáveis** | 0,20 eventos de ciclo de vida por 1000 passos em regime estacionário (mediana 0) | — |
| E6 | **Invariância de escala**: a explicação não muda com a unidade do alvo | T7: NMSE e estrutura idênticos com y ×10⁻³, ×1 e ×10³ | pressupõe entradas padronizadas pelo ambiente (P6) |

## B. Transparência operacional

| # | Benefício | Evidência medida | Limite |
|---|---|---|---|
| O1 | **Intervalos de predição de 90% calibrados online**, sem supor distribuição | cobertura interna 0,900 (0,867–0,926 por execução); 0,894–0,904 sob t₃, heterocedasticidade e mudança de regime; externo: 14 de 15 tarefas em [0,85; 0,95] | cobertura de longo prazo, não condicional; em séries fortemente não estacionárias pode ficar abaixo (AusElectricity S2: 0,81) |
| O2 | **Alarmes de mudança estrutural** (cada remoção por CUSUM tem taxa de alarme falso controlada) | atraso de detecção mediano de 40 passos (média 228), igual ao da v0.3.2 | alarma mudanças *estruturais*; mudanças absorvidas pelos pesos não geram alarme |
| O3 | **Log completo do ciclo de vida** (quando e por que cada estrutura entrou ou saiu) | presente em todas as execuções | volume de eventos cresce em dados muito não estacionários (F16: ~400 eventos) |
| O4 | **Custo computacional contabilizado e previsível** | 99,9 FP/passo no interno (d = 5); relatado por componente | cresce com d (média de 177 FP no BENCH-03b); FP não é energia |
| O5 | **Zero divergências numéricas** | 0 em todas as execuções internas e externas (BENCH-03 e BENCH-03b) | — |

## C. O que os comparadores não oferecem (verificado nos benchmarks)

Nenhum dos 21 comparadores externos do BENCH-03b (excluída a própria LEBRE v0.3.2) (filtros adaptativos clássicos, redes recorrentes e reservatórios do BENCH-01B, árvores e modelos lineares do River)
entrega **ao mesmo tempo** decomposição exata da previsão, estrutura temporal nomeada, intervalos calibrados e alarmes de mudança com erro controlado.
Modelos lineares (NLMS, IPNLMS, RLS) permitem ler pesos, mas não oferecem estrutura temporal selecionada nem alarmes. As árvores do River não
oferecem decomposição aditiva exata. As redes recorrentes e os reservatórios não oferecem nenhum dos quatro.

## D. Declaração

> A LEBRE v0.4 oferece previsões **competitivas** (1ª de 24 modelos no benchmark held-out BENCH-03b, dentro de 1,25× do melhor filtro clássico
> em 93% das tarefas, com zero divergências), **junto com** explicações exatas e estatisticamente fundamentadas, intervalos de predição calibrados e
> alarmes de mudança estrutural. Tudo isso com custo contabilizado de ~100 FP/passo para d = 5.

## E. Reivindicações proibidas

Estado da arte; causalidade física; garantias exatas no laço adaptativo; cobertura condicional; eficiência energética a partir de FP;
explicação única em estruturas redundantes; aplicabilidade a relações não lineares fortes.

## F. Atualização (2026-09-23)

- A linha v0.4 passa a ser implementada por `lebre_v045.py`. A C5′ não altera E1–E6 nem O1–O5 no interno: os resultados internos são idênticos aos da v0.4.2.
- **A afirmação "competitiva" da seção D deve ser lida com os limites do BENCH-04:**
  - com a v0.4.5: 5/5 nos critérios, 7º de 35 modelos;
  - porém 2,1× o NLinear online e 3,2× o melhor Chronos em séries sazonais reais;
  - a O2 (atraso de detecção) é ~1,3× o da v0.3.2 em sementes novas.
