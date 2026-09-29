# PRA-04 — Prior art da LEBRE v0.52 (versão corrigida)

**Data:** 27/09/2026 · **Objetivo do projeto:** contribuição de pesquisa, sob o princípio *"entregar bem com orçamento mínimo, sem precisar ser o melhor"*.
**Base empírica considerada:** avaliações pré-registradas em dados reservados (125 séries na reserva 1; 40 séries na reserva 2, depois da correção das lacunas do alvo).
**Limite:** 25 consultas num único mecanismo de busca; dois trabalhos lidos em texto completo, os demais pelo resumo (§6).

## 1. O que a v0.52 afirma (e é auditado aqui)

- **A — Previsão com entradas sob orçamento mínimo.** Previsor online, sem treino prévio, com ~400 FP/passo, que na reserva 2 foi o mais preciso da sua classe de custo, empatou com um SARIMAX com entradas ajustado série a série e ficou 16% atrás do Chronos-2 com covariáveis, sem nenhuma falha catastrófica.
- **B — Mudança estrutural certificada.** Cada mudança de estrutura (acrescentar ou remover uma **entrada inteira**, trocar, refinar a resposta por divisão hierárquica de faixas) é aceita por um e-process de melhora preditiva (diferença de perda recortada, nula fraca, forma unilateral), com controle da taxa de mudanças falsas ao longo do fluxo (níveis tipo e-LOND), num orçamento fixo de custo.
- **C1 — Condição de uso (achado).** Se a referência é um aprendiz online com desajuste apreciável (NLMS com passo 0,1), o erro dela fica em parte **previsível pelo passado**. O teste então aceita "estrutura" que só corrige o ruído do aprendiz: no desenvolvimento, 20% dos alvos sem nenhuma estrutura tiveram uma mudança aceita. Com desajuste pequeno (passo 0,05), foram 0/40 no desenvolvimento e 0/30 em avaliação declarada.
- **C2 — Limite de informação (achado).** Em entradas muito suaves (autocorrelação ~0,99), um atraso médio ou longo traz pouca informação além do valor atual. Nem um oráculo online (que conhece o atraso e testa desde o início) descobre a relação em 9–27 mil passos, e às vezes nunca.
- **D — Salvaguardas.** Retenção do último valor observado durante lacunas do alvo (sem malha fechada pela memória), contrato de saída (envelope dos valores observados), controle de pico de custo (escalonamento, triagem espalhada).

## 2. O que já existe, afirmação por afirmação

### A — previsão sob orçamento

| Trabalho | O que faz | Diferença para a v0.52 | Proximidade |
|---|---|---|---|
| SparseTSF (ICML 2024; TPAMI 2026) | Previsão de horizonte longo com < 1k parâmetros | Univariado, **treinado em lote** offline; sem entradas exógenas; sem aprendizado online | Média (orçamento de parâmetros) |
| FITS (ICLR 2024) | ~10k parâmetros, interpolação no domínio da frequência | Idem | Média |
| TTM — Tiny Time Mixers (NeurIPS 2024) | Modelo pré-treinado de ~1M parâmetros; aceita exógenas via decodificador ajustado | 10³–10⁴× mais caro por previsão; pré-treino e ajuste | Média-alta (teto "pequeno" com exógenas) |
| TinyCast (arXiv 2608.15767, 2026) | 146 mil parâmetros, INT8, embarcado, zero-shot, probabilístico | Univariado; sem aprendizado online | Média |
| Reverso (2026) | Modelos de fundação de 0,2–2,6M parâmetros | Teto de referência "pequeno"; univariado | Baixa-média |
| TEDA-forecasting (Computing 2025) | RLS por nuvem de dados, TinyML, incremental | Online e embarcado; **sem** seleção de entradas com garantia; avaliação em outro domínio | Média |
| OneNet, FSNet, DSOF, Proceed | Adaptação online de previsores profundos | Custo 10⁵–10⁸× maior | Baixa |

**Leitura:** existe uma literatura ativa de previsão ultraleve e de fronteira precisão × custo, mas nos trabalhos encontrados ela é **univariada, treinada offline** ou **ordens de grandeza mais cara**. **Não encontramos** avaliação de um previsor **online, guiado por entradas, com ~10² FP/passo**, contra SARIMAX com entradas e Chronos-2 com covariáveis em séries reais nunca vistas. **A contribuição aqui é empírica e de posicionamento**, não um método novo.

### B — mudança estrutural certificada

| Trabalho | O que faz | Diferença para a v0.52 | Proximidade |
|---|---|---|---|
| **Amoukou, Mishra & Veloso**, *Correcting split selection in online decision trees via anytime-valid inference*, arXiv 2605.31239 (**maio/2026**) | Aceita uma divisão de árvore online quando um e-process (**apostas** ou Bernstein empírico) sobre a **diferença de perda prequencial** entre incumbente (folha) e desafiante (divisão) rejeita a nula fraca ou forte de Choe & Ramdas. **Controle global** (probabilidade ≥ 1−α de nenhuma substituição falsa no fluxo inteiro) por alocação de níveis | Árvores em dados tabulares, não séries com entradas; controle **FWER** (não FDR); **sem remoção** de estrutura; sem orçamento de custo; **não discute** o ruído do aprendiz de referência | **ALTA — é o núcleo do mecanismo da v0.52 em outro domínio** |
| Choe & Ramdas (2024); Henzi & Ziegel (2022) | E-process para comparar dois previsores sequenciais pela diferença média de score | Dois previsores, sem crescimento de modelo | Alta (base teórica) |
| e-LOND; online e-BH; e-GAI | FDR online com e-valores sob dependência arbitrária | Hipóteses fixas; decisões irrevogáveis | Alta (base de multiplicidade) |
| Testes hierárquicos (Yekutieli 2008; Benjamini & Bogomolov; TreeBH) | FDR em árvores de hipóteses, "pai antes do filho" | Offline, p-valores | Média (base das divisões) |
| OGFS; group-SAOLA; alpha-investing | Seleção de **grupos** de atributos em fluxo | Sem e-valores, sem garantia sempre válida, sem séries temporais | Média |
| RAVAS (Yang & Yao, arXiv 2606.00478) | Regressão esparsa online com atributos que surgem com o tempo; garantias de seleção | Garantia assintótica/probabilística, não sempre válida; sem orçamento de FLOPs | Média |
| Frazier & Poskitt (2505.09090); Backhaus et al. (2410.17800) | Escolha sequencial entre métodos de previsão por e-valores | Conjunto fixo de métodos | Média |
| "Bet on Features" (Antonov, Mukherjee, Pibernik & Choe, arXiv 2607.11653) | Apostas contextuais sobre um dicionário de atributos para **auditar** a calibração de previsores quantílicos | Auditoria; não altera o previsor | Baixa-média |

**Correção de uma conclusão anterior.** A PRA-03 (25/09/2026) registrou que nenhum trabalho reunia (1) candidatos gerados adaptativamente com desafiantes aprendidos online, (2) referência que evolui com as aceitações, (3) controle de erro ao longo do fluxo, (4) remoção e substituição, (5) orçamento fixo. **Amoukou et al. (maio/2026), anterior àquela auditoria mas não encontrado nela, cobre (1), (2) e (3), este último na forma FWER.** Continuam em aberto: (4) testes de remoção e substituição, (5) orçamento de custo, controle de **FDR** (em vez de FWER) nesse contexto e a aplicação a **séries temporais com entradas por unidade de entrada**.

**Leitura:** o núcleo do mecanismo (aceitar mudanças estruturais por e-process de melhora preditiva, com controle de erro no fluxo) **não é original**. O que a v0.52 acrescenta é **integração e extensão**: unidades por entrada, refinamento hierárquico, testes de remoção e troca, FDR e orçamento de custo, num previsor de série temporal. Isso é contribuição de **sistemas/integração**, como já se previa.

### C1 — desajuste da referência como condição de uso

| Trabalho | Relação com o achado |
|---|---|
| Giacomini & White (2006) | Mostram que testes de capacidade preditiva comparam **métodos** (modelo + procedimento de estimação), não modelos. O achado C1 é um caso concreto dessa distinção: "melhora sobre a referência" inclui "estimar melhor", não só "estrutura nova" |
| Clark & West (2007); West (1996) | Em comparações aninhadas, o erro de estimação **penaliza o modelo maior** sob a nula. O nosso efeito vai no **sentido oposto**: o ruído de um aprendiz online de referência, previsível pelo passado, **favorece** o desafiante maior |
| Literatura de LMS/NLMS (Widrow) | O desajuste (~μ/2 do ruído) e a correlação do ruído dos pesos com as entradas recentes são conhecidos |
| **Han & Qu**, arXiv 2608.30502 (ago/2026) | Monitores sempre válidos (martingais conformais) disparam em 135/135 séries reais porque a premissa de permutabilidade falha em dados dependentes. Recomendam "controles de calibração sob a nula e rastros do mecanismo". **Causa diferente** (premissa do teste), mas o mesmo tema: garantias válidas no papel falham na prática sem controles nulos |
| Amoukou et al. (2026) | Usa a mesma comparação incumbente × desafiante aprendidos online e **não discute** o efeito do ruído do incumbente |

**Leitura:** os ingredientes são conhecidos (métodos × modelos; desajuste do LMS), mas **não encontramos** a observação explícita e medida de que, num e-process **válido** (sem premissa de permutabilidade), a aceitação de "estrutura" pode ser dirigida pelo ruído previsível de uma referência adaptativa, nem a condição de uso correspondente. É um **achado metodológico modesto e útil**, com dois vizinhos claros para citar (Giacomini & White; Han & Qu). Para virar contribuição publicável, precisa de formalização: uma condição sobre o desajuste sob a qual a nula estrutural implica diferença média de perda ≤ 0.

### C2 — limite de informação em entradas suaves

A perda de poder com regressores muito persistentes é **conhecida** em econometria (Stambaugh 1999; Campbell & Yogo 2006; IVX), assim como o pré-branqueamento na identificação de funções de transferência (Box & Jenkins). O oráculo online é uma **quantificação ilustrativa** para o nosso regime (teste sempre válido, comprimento finito), **não uma contribuição nova**.

### D — salvaguardas

Retenção do último valor observado, filtros de Kalman com observações faltantes, saturação da saída e limites de custo por passo são **práticas padrão**. O registro útil é o **modo de falha** encontrado: memória em malha aberta durante lacunas, instável e explosiva. É uma lição de engenharia a documentar, não uma contribuição.

## 3. Declaração honesta de contribuição

| Item | Classificação |
|---|---|
| Mecanismo de mudança estrutural por e-process de melhora preditiva com controle no fluxo | **Não original** (Choe & Ramdas; Amoukou et al. 2026; e-LOND) |
| Extensão a séries com entradas: unidades por entrada, refinamento hierárquico, remoção e troca testadas, controle FDR, orçamento fixo | **Integração/extensão** — original na combinação, não nas peças |
| Achado C1 (desajuste da referência; condição de uso) | **Metodológico modesto**, não encontrado explicitamente; precisa de formalização |
| Achado C2 (limite de informação) | **Conhecido** em princípio; quantificação ilustrativa |
| Resultado empírico sob orçamento (1º na classe de ~10² FP; empate com SARIMAX-X; erro 16% acima do Chronos-2 com covariáveis, ~68% da redução de erro dele sobre o NLinear, a ~10⁻⁷ do custo; zero falhas catastróficas) | **Empírico**, com pré-registro e dados nunca vistos; é o argumento mais forte hoje |
| Salvaguardas | Engenharia padrão |

**Síntese:** a v0.52 é uma **contribuição de sistemas e empírica**: um previsor online de custo mínimo, com mudanças estruturais certificadas e explicáveis, avaliado honestamente contra tetos de referência. Não há ruptura teórica. O trabalho de Amoukou et al. (2026) precisa ser citado como o vizinho mais próximo do mecanismo, e o posicionamento deve enfatizar **orçamento, robustez e séries com entradas**.

## 4. Ameaças à validade da contribuição

1. **Comparadores de orçamento ausentes:** SparseTSF, FITS e TinyCast (univariados) e TTM (com exógenas) não foram avaliados no nosso protocolo online. Um revisor pedirá pelo menos um modelo ultraleve e um TTM ajustado.
2. **Domínio:** hidrologia e prédios com poucas entradas; sem ONS na reserva 2; 40 séries.
3. **Custo:** a contagem de FP é analítica, feita pelo código, e ainda não foi medida em microcontrolador.
4. **Contrato de custo:** a média e o pico ficaram ~2% acima do contrato na reserva 2.

## 5. Recomendações

1. **Congelar a v0.52 corrigida** como versão de pesquisa, com esta declaração de contribuição e as limitações.
2. Antes de qualquer publicação:
   - (a) incluir um comparador ultraleve (SparseTSF ou FITS em modo online) e o TTM com exógenas;
   - (b) formalizar C1;
   - (c) medir em microcontrolador;
   - (d) nova avaliação em dados nunca vistos, incluindo outro domínio hidrológico.

## 6. Limitações desta auditoria

- **Busca:** um mecanismo e 25 consultas, só em inglês. Bases com acesso restrito (Springer, IEEE) foram lidas por resumo ou busca.
- **Profundidade de leitura:** texto completo só em Amoukou et al. e no resumo integral de Han & Qu, ambos mediados por ferramenta de resumo. Os demais trabalhos foram lidos por resumo.
- **Recorte temporal:** a literatura de 2026 é muito ativa. Pode haver trabalhos recentes relevantes não indexados.

## Referências

- Amoukou, S. I., Mishra, S., Veloso, M. (2026). *Correcting split selection in online decision trees via anytime-valid inference.* [arXiv:2605.31239](https://arxiv.org/abs/2605.31239)
- Han, W., Qu, L. (2026). *When the martingale never stops firing: anytime-valid gating on real forecast streams.* [arXiv:2608.30502](https://arxiv.org/abs/2608.30502)
- Antonov, I., Mukherjee, S., Pibernik, R., Choe, Y. J. (2026). *Bet on features: anytime-valid and feature-aware auditing of conditional quantile forecasters.* [arXiv:2607.11653](https://arxiv.org/abs/2607.11653)
- Yang, Y., Yao, F. (2026). *Online sparse regression with expanding observables.* [arXiv:2606.00478](https://arxiv.org/abs/2606.00478)
- Frazier, D. T., Poskitt, D. S. (2025). *Sequential scoring rule evaluation for forecast method selection.* [arXiv:2505.09090](https://arxiv.org/abs/2505.09090)
- Lin, S. et al. (2024). *SparseTSF: modeling long-term time series forecasting with 1k parameters.* ICML. [arXiv:2405.00946](https://arxiv.org/abs/2405.00946)
- Xu, Z., Zeng, A., Xu, Q. (2024). *FITS: modeling time series with 10k parameters.* ICLR. [arXiv:2307.03756](https://arxiv.org/abs/2307.03756)
- Ekambaram, V. et al. (2024). *Tiny Time Mixers (TTMs).* NeurIPS. [arXiv:2401.03955](https://arxiv.org/abs/2401.03955)
- Steinhauser, A. (2026). *TinyCast: probabilistic zero-shot forecasting with computed periodicity.* [arXiv:2608.15767](https://arxiv.org/abs/2608.15767)
- *Reverso: efficient time series foundation models for zero-shot forecasting* (2026). [arXiv:2602.17634](https://arxiv.org/abs/2602.17634)
- *TEDA-forecasting: an unsupervised tinyML incremental learning approach for outlier processing and forecasting.* Computing 107(8), 2025. [DOI 10.1007/s00607-025-01490-3](https://link.springer.com/article/10.1007/s00607-025-01490-3)
- Zhang, Y. et al. (2023). *OneNet.* NeurIPS. [arXiv:2309.12659](https://arxiv.org/abs/2309.12659)
- Yu, K. et al. *Scalable and accurate online feature selection for big data* (SAOLA, group-SAOLA). [arXiv:1511.09263](https://arxiv.org/pdf/1511.09263)
- Giacomini, R., White, H. (2006). Tests of conditional predictive ability. *Econometrica* 74(6).
- Clark, T. E., West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *J. Econometrics* 138(1), 291–311.
- Campbell, J. Y., Yogo, M. (2006). Efficient tests of stock return predictability. *J. Financial Economics* 81(1).
- Stambaugh, R. F. (1999). Predictive regressions. *J. Financial Economics* 54(3).
- Yekutieli, D. (2008). Hierarchical false discovery rate-controlling methodology. *JASA* 103(481).
- Choe, Y. J., Ramdas, A. (2024). Comparing sequential forecasters. *Operations Research*. [arXiv:2110.00115](https://arxiv.org/abs/2110.00115)
- Xu, Z., Ramdas, A. (2024). Online multiple testing with e-values (e-LOND). *AISTATS*.
