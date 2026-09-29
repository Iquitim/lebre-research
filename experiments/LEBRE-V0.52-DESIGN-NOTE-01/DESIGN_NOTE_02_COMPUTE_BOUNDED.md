# LEBRE v0.52 — Nota de desenho 02: descoberta estrutural sempre válida sob orçamento de computação

**Data:** 25/09/2026 · **Status:** proposta de direção de pesquisa. **Não há código, provas completas nem resultados.**
**Motivação:** o objetivo do projeto é uma contribuição que vá além do estado da arte. A Nota 01 mostrou que a proposta anterior não chega lá.

---

## 1. Por que a Nota 01 não basta

- **G1 (segurança):** composição quase direta de Choe & Ramdas (2024) com e-LOND (Xu & Ramdas, 2024).
- **G2 (convergência por comparação de perdas preditivas):** é o princípio dos mínimos quadrados preditivos (Rissanen, 1986), com consistência forte provada por Hemerly & Davis (Annals of Statistics, 1989) e Wei (Annals of Statistics, 1992).
- O logaritmo de um e-process de razão de verossimilhança preditiva é a vantagem de score acumulada (Choi, 2026; princípio prequencial de Dawid, 1984). **G1 + G2 é, em essência, seleção prequencial de modelo com o limite de Ville.** Resultado correto, mas incremental.

## 2. O que a LEBRE tem de único, e o que os dados mostraram

A LEBRE nasceu como **evolução de estrutura governada por recursos**. O diagnóstico da v0.51 mostrou que o gargalo da descoberta estrutural **não é estatístico, é computacional**:
- o teste de um candidato leva ~200–300 passos, mas a primeira promoção leva 1,5–3 mil;
- o tempo se perde na busca, com poucas vagas de teste e sondagem rara de cada candidato;
- e a evidência de um candidato que não está sendo processado **se perde para sempre**, porque não há memória para guardar o passado.

Isso define um problema que as três literaturas relevantes não cobrem juntas:

| Literatura | O que resolve | O que não resolve |
|---|---|---|
| Testes sempre válidos e múltiplos online (e-processes, e-LOND, e-closure, Choe & Ramdas) | Validade e controle de erro sob parada opcional | Supõe computação ilimitada: toda hipótese é atualizada a cada dado |
| Testes com seleção adaptativa de amostras (Jamieson & Jain, NeurIPS 2018; Sandoval, Waudby-Smith & Jordan, 2026) | Onde **amostrar** sob orçamento de amostras | Cada amostra informa um braço. No nosso caso, cada dado chega de graça e informa **todas** as hipóteses; o que falta é capacidade de processá-lo |
| Inferência com memória limitada (Hellman & Cover, 1970; Berg, Ordentlich & Shayevitz, survey 2024; Steinhardt & Duchi, regressão esparsa com memória limitada; Sharan, Sidford & Valiant, STOC 2019) | Limites inferiores de taxa e de amostras sob memória limitada | Estimação ou teste simples, sem validade sempre válida, testes múltiplos ou descoberta estrutural online |

## 3. O problema proposto

**Descoberta estrutural sempre válida sob orçamento de computação por passo.**
- Um fluxo \((x_t, y_t)\) e um dicionário de \(p\) candidatos estruturais (atrasos, estados latentes, acionamentos).
- A cada passo, o algoritmo pode **atualizar a evidência de no máximo m candidatos** (orçamento de computação), com memória O(m + d·L), e opcionalmente fazer uma **triagem barata** de mais candidatos, com fidelidade menor.
- Evidência não processada no passo t **não pode ser recuperada** depois.
- **Objetivos:**
  - (a) controle da taxa de mudanças falsas ao longo do fluxo, para **qualquer** política de atenção previsível;
  - (b) latência mínima até descobrir a estrutura verdadeira, quando ela existe.

## 4. Resultados-alvo

| # | Resultado | Dificuldade esperada | Situação na literatura (até onde buscamos) |
|---|---|---|---|
| T1 | **Validade sob atenção arbitrária.** Qualquer política que escolha, de forma previsível, quais hipóteses atualizar preserva as garantias de e-process e de FCR (Choe & Ramdas §F.1; e-LOND) | baixa (lema) | Consequência de resultados conhecidos |
| T2 | **Limite inferior de latência** para detectar um termo de ganho g entre p candidatos, com orçamento m: algo como \(\Omega\big(\tfrac{p}{m}\cdot\tfrac{\log(1/\alpha)}{g^2}\big)\) sem triagem, e um limite mais fino com triagem de custo menor | **alta**: é o núcleo novo | Não encontrado para descoberta sempre válida sob orçamento de computação |
| T3 | **Algoritmo "triar e testar"** com atenção adaptativa (tipo bandit sobre o crescimento da evidência) que atinge T2 a menos de fatores logarítmicos, com a triagem sem contaminar a validade (dados de triagem nunca reutilizados no teste) | média-alta | Parcialmente análogo a Jamieson & Jain, mas com observações compartilhadas e evidência perdida |
| T4 | **Estrutura aninhada e dependente do caminho** (crescimento, remoção, troca) dentro do mesmo arcabouço, incluindo a saída de estruturas erradas (polo errado, atrasos aproximados) | média | Não encontrado |
| T5 | **Instância embarcada**: a LEBRE como realização do algoritmo em microcontrolador, com medição de ciclos e energia, em dados reais guiados por entradas, confrontando latência medida e limite teórico | média (engenharia) | Não encontrado |

**Afirmação-alvo, se T2–T5 se confirmarem:**
> "Formulamos e resolvemos a descoberta estrutural sempre válida sob orçamento de computação por passo. Provamos um limite inferior de latência em função do orçamento, damos um algoritmo que o atinge com controle de mudanças falsas ao longo do fluxo inteiro, e mostramos a realização em um microcontrolador, com dados reais."

Essa afirmação liga três áreas que hoje não conversam: inferência sempre válida, limites de memória e computação, e aprendizado embarcado. Ela também transforma o gargalo empírico que medimos na v0.51 em teoria.

## 5. Por que isso pode ir além do estado da arte

- Coloca a **computação como recurso estatístico de primeira classe** em inferência sequencial. Hoje, os trabalhos de inferência sempre válida tratam amostras como o recurso escasso; em dispositivos embarcados e fluxos de alta dimensão, o escasso é computação e memória.
- Dá uma resposta quantitativa a uma pergunta prática sem resposta: *quanta computação é necessária para descobrir estrutura com garantia, e quanto se perde por economizá-la?*
- Mantém o DNA original da LEBRE (estrutura governada por recursos e evidência) e dá a ele uma base teórica que antes não tinha.

## 6. Riscos e como falsificar cedo

- **T2 pode ser difícil ou trivial.** Trivial: se o limite sair diretamente de "cada candidato recebe no máximo uma fração m/p da atenção". Nesse caso, o conteúdo novo precisa estar no caso **com triagem**, a troca entre triagem barata e teste caro, que não é trivial. Difícil: argumentos de memória limitada são tecnicamente pesados (Steinhardt & Duchi; Sharan et al.). **Teste rápido:** tentar primeiro o caso sem triagem e com candidatos independentes, e depois o caso com triagem.
- **Pode existir trabalho não encontrado** em "testes múltiplos com computação limitada" ou "testes sequenciais em fluxos com esboços (sketches)". É preciso uma busca dirigida antes de investir.
- **Alcance empírico:** mesmo com teoria, a demonstração precisa de dados reais guiados por entradas, que continuam sendo o pré-requisito pendente.

## 7. Próximos passos (em ordem)

1. **Ler na íntegra** Steinhardt & Duchi (regressão esparsa com memória limitada), o survey de Berg, Ordentlich & Shayevitz (2024) e Jamieson & Jain (2018). Pergunta: algum deles já dá T2 ou algo equivalente?
2. **Busca dirigida** por "multiple testing under computational constraints", "sequential testing with sketches" e "attention-limited inference".
3. **Formalizar o modelo de computação** (o que conta como "processar" um candidato; triagem versus teste) e **tentar T2** no caso mais simples: p candidatos independentes, um verdadeiro, ruído gaussiano.
4. Em paralelo: escolher os conjuntos de dados reais guiados por entradas.

## 8. Reavaliação após leitura integral (25/09/2026)

**Lido:**
- Steinhardt & Duchi (COLT 2015): limite inferior Ω(kd/(Bε)) de amostras para estimação esparsa com B bits.
- Survey de Berg, Ordentlich & Shayevitz (2024).
- Garg, Hastings, Pabbaraju & Sharan, *A unified approach to memory-sample tradeoffs for detecting planted structures* (arXiv 2603.00770, fev/2026), Teorema 1.8.
- Por resumo: Dagan & Shamir (COLT 2018), detecção de correlações com pouca memória.

**Consequência para T2.** Garg et al. provam, para **detectar** médias gaussianas esparsas (o nosso caso simples, "um entre p candidatos tem sinal"), que qualquer algoritmo com s bits de memória precisa de n amostras com s·n ≥ Ω(d^{0,99}/(α ℓ q)²). Com memória proporcional a m candidatos, isso dá latência ≳ p/(m·g²). Identificar é mais difícil que detectar, então o limite se transfere. Somado ao limite sequencial clássico (≈ log(1/α)/g², tipo Wald), o limite inferior de T2 **sai essencialmente como corolário**: T2 não é o núcleo novo.

**O que sobra de genuíno:**
1. **Achievability com validade sempre válida.** Um algoritmo de triagem e teste com latência ≈ p/(m g²) + log(1/α)/g² (aditivo), que atinge os limites a menos de fatores logarítmicos **e** controla a taxa de mudanças falsas ao longo do fluxo. Os algoritmos com memória limitada da literatura garantem erro com amostra fixa; os de e-process ignoram memória. A ponte é nova, mas cada metade é conhecida.
2. **Mudança estrutural (não estacionariedade).** Se a estrutura verdadeira pode mudar num instante desconhecido, a pergunta vira **detecção rápida de mudança sob orçamento de computação**: o limite de Lorden (log ARL / KL) com um termo de varredura p/m. Não verificado na literatura; é o candidato mais promissor a um resultado menos óbvio. **Ainda precisa de busca dirigida.**
3. **Estruturas aninhadas e dependentes do caminho** (troca, remoção) e a **realização embarcada** com dados reais.

**Avaliação honesta.** Em três rodadas, cada candidato a "teorema central novo" caiu numa literatura madura:
- predição sequencial e seleção prequencial;
- testes múltiplos com e-valores;
- trocas entre memória e amostras.

A contribuição realista é uma **ponte bem feita** entre essas áreas, com:
- (i) algoritmo quase ótimo em computação e sempre válido;
- (ii) extensão a mudanças estruturais;
- (iii) realização em microcontrolador com dados reais.

É uma contribuição adequada e publicável se bem executada. Mas o grau de "ruptura" depende sobretudo do item 2, que ainda não foi verificado.

## 9. Busca dirigida do item 2 (mudança estrutural sob orçamento)

**Resultado: já existe.** Processar só m de p candidatos por passo, quando a evidência não processada se perde, é matematicamente equivalente a **observar** só m de p fluxos. Esse é o problema de detecção rápida de mudança em vários fluxos com controle de amostragem:
- Xu, Mei & Moustakides, *Optimum multi-stream sequential change-point detection with sampling control*, IEEE Transactions on Information Theory 67(11), 2021. Prova otimalidade assintótica de uma regra de **varredura**: amostrar um fluxo até o CUSUM zerar ou cruzar o limiar e então passar ao próximo, que é essencialmente o que a LEBRE faz.
- Gopalan, Lakshminarayanan & Saligrama, *Bandit quickest changepoint detection*, NeurIPS 2021. Dá limite inferior de atraso e um esquema de sensoriamento que equilibra exploração e aproveitamento.
- Survey *Multi-stream quickest change detection: foundations and recent advances* (Entropy, 2026; arXiv 2604.18008).

## 10. Conclusão das quatro rodadas

| Candidato a núcleo novo | Onde já existe |
|---|---|
| Promoção por melhora preditiva | Choe & Ramdas (2024); Henzi & Ziegel (2022); seleção prequencial (Dawid; Rissanen; Wei) |
| Controle de erro ao longo do fluxo | e-LOND (2024); e-closure (2026); SAVA (2025) |
| Convergência da estrutura | Mínimos quadrados preditivos (Hemerly & Davis, 1989; Wei, 1992); Fu & Zhao (2025) |
| Limite inferior sob orçamento de memória/computação | Steinhardt & Duchi (2015); Dagan & Shamir (2018); Garg et al. (2026) |
| Mudança estrutural sob orçamento | Xu, Mei & Moustakides (2021); Gopalan et al. (2021) |

**Leitura:** a descoberta estrutural online da LEBRE está numa **interseção densa** de áreas maduras. Não há um teorema central novo à espera nessas direções. O que existe é:
- (i) a **unificação**: mostrar que a descoberta estrutural online em previsores embarcados se reduz a detecção com controle de amostragem, somada a testes múltiplos sempre válidos e a trocas entre memória e amostras;
- (ii) um **algoritmo integrado quase ótimo** que herda as garantias das três áreas ao mesmo tempo;
- (iii) a **demonstração** em dados reais e em microcontrolador.

É uma contribuição **adequada, de integração e de sistemas**, não uma ruptura teórica.

## Referências novas desta nota

- Rissanen, J. (1986). Stochastic complexity and modeling. *Annals of Statistics* 14(3).
- Hemerly, E. M., Davis, M. H. A. (1989). Strong consistency of the PLS criterion for order determination of autoregressive processes. *Annals of Statistics* 17, 941–946.
- Wei, C. Z. (1992). On predictive least squares principles. *Annals of Statistics* 20(1), 1–42.
- Dawid, A. P. (1984). Statistical theory: the prequential approach. *JRSS A* 147(2), 278–290.
- Jamieson, K., Jain, L. (2018). A bandit approach to sequential experimental design with false discovery control. *NeurIPS*.
- Sandoval, R. J., Waudby-Smith, I., Jordan, M. I. (2026). Multi-armed sequential hypothesis testing by betting. arXiv:2603.17925.
- Hellman, M. E., Cover, T. M. (1970). Learning with finite memory. *Annals of Mathematical Statistics* 41(3).
- Berg, T., Ordentlich, O., Shayevitz, O. (2024). Statistical inference with limited memory: a survey. *IEEE JSAIT*. arXiv:2312.15225.
- Steinhardt, J., Duchi, J. Minimax rates for memory-bounded sparse linear regression. *COLT* (2015).
- Sharan, V., Sidford, A., Valiant, G. (2019). Memory-sample tradeoffs for linear regression with small error. *STOC*.
- Garg, S., Hastings, J., Pabbaraju, C., Sharan, V. (2026). A unified approach to memory-sample tradeoffs for detecting planted structures. arXiv:2603.00770.
- Dagan, Y., Shamir, O. (2018). Detecting correlations with little memory and communication. *COLT*, PMLR 75.
- Xu, Q., Mei, Y., Moustakides, G. V. (2021). Optimum multi-stream sequential change-point detection with sampling control. *IEEE Transactions on Information Theory* 67(11), 7627–7636.
- Gopalan, A., Lakshminarayanan, B., Saligrama, V. (2021). Bandit quickest changepoint detection. *NeurIPS*. arXiv:2107.10492.
- *Multi-stream quickest change detection: foundations and recent advances* (2026). *Entropy* 28(5):566; arXiv:2604.18008.
