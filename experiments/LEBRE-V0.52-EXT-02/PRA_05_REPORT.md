# PRA-05 — Revisão bibliográfica sistemática da LEBRE v0.52 (relatório)

**Data:** 27/09/2026 · Protocolo em `LIT_REVIEW_PROTOCOL.md`, fixado antes das buscas; diário em `LIT_REVIEW_LOG.md` (22 consultas e 8 resumos, somados às 25 consultas da PRA-04).

## 1. Resultado por afirmação

| Afirmação | Trabalhos mais próximos encontrados | Conclusão |
|---|---|---|
| **A1** Mudança de estrutura aceita por e-process de melhora preditiva | Amoukou, Mishra & Veloso 2026 (árvores online; já na PRA-04); **Choi 2026, arXiv 2608.08174** (evidência sempre válida de que uma *correção pré-especificada* de uma distribuição preditiva a melhora; razão de verossimilhança preditiva como e-value); Jha 2026, arXiv 2606.22230 (Granger distribucional com teste sequencial adaptativo e controle de FWER) | **Continua não original.** Choi 2026 é mais um vizinho próximo: lá a correção é pré-especificada e a evidência é de verossimilhança, enquanto a LEBRE aprende o desafiante no episódio e usa diferença de perda recortada. |
| **A2** Controle de falsas descobertas online sobre o fluxo de mudanças | Xu & Ramdas 2024 (e-LOND); **de Heide 2026, arXiv 2608.09927** (e-closure dinâmica para hipóteses cuja evidência continua a acumular, "setwise persistent", com FDR); Yao, Gang & Sun 2025, arXiv 2512.12244 (alpha-investing sempre válido no cenário duplamente sequencial); arXiv 2603.24792 (e-closure online, mais poder que o e-LOND) | **Base existente e ativa.** O caso das hipóteses persistentes da LEBRE está coberto em teoria por trabalhos de 2025–2026, que também oferecem procedimentos com mais poder que o e-LOND. |
| **A3** Seleção online de entradas/atrasos em modelos com entradas exógenas | Identificação esparsa recursiva de ARMAX com garantias assintóticas (arXiv 2505.00323); Jha 2026 (Granger); SINDy + Kalman online (arXiv 2511.11178) | **Parcial.** Há seleção online com garantia **assintótica** ou sem garantia. Não encontramos seleção de entradas por unidade com garantia **a qualquer tempo** e controle de FDR em fluxo. |
| **A4** Refinamento hierárquico/multirresolução da resposta a uma entrada | Testes hierárquicos (Yekutieli; Meinshausen); seleção bayesiana de defasagens (offline) | Peças conhecidas; nenhuma combinação online encontrada. |
| **A5** Erro de estimação da referência e significado estrutural do teste | Giacomini & White 2006; Clark & West 2007; Han & Qu 2026; estudo de Monte Carlo sobre testes preditivos na seleção de modelos (IJF 2020); **Fernández-Barrios et al. 2026, arXiv 2609.04388** (viés do incumbente na promoção de desafiantes; empírico, detecção de intrusão) | **Observação modesta, com vizinhos claros.** Não encontramos a forma explícita da Proposição 1 aplicada a e-processes que decidem estrutura. O tema geral (comparar métodos, não modelos; viés do incumbente) é conhecido. |
| **A6** Previsão online embarcada com entradas exógenas | TinyOL (aprendizado online em MCU); **Lara Pinal, Das & Schlüter 2026, arXiv 2608.14698** (ESP32, rede de 3.011 parâmetros, aprendizado incremental com sensores exógenos, previsão solar, 115 dias em campo); TinyCast | **Existe** previsão embarcada com aprendizado online e entradas exógenas. A diferença da LEBRE é a seleção de estrutura com evidência e o orçamento de ~10² operações por passo, não o fato de ser embarcada. |
| **A7** Comparadores online da mesma classe | ARMAX com filtro de Kalman em vazão (literatura clássica de hidrologia) | Comparador clássico relevante **não avaliado** na LEBRE; registrar como limitação. |

## 2. Consequências para o texto

1. **Posição na literatura:**
   - acrescentar Choi (2026) e Jha (2026) como vizinhos de A1;
   - acrescentar de Heide (2026) e Yao, Gang & Sun (2025) como base de A2 para hipóteses persistentes (e como caminho de melhora de poder);
   - acrescentar a identificação esparsa recursiva de ARMAX (A3), Lara Pinal et al. (2026) (A6) e Fernández-Barrios et al. (2026) (A5).
2. **A contribuição continua de integração e empírica.** A combinação é: unidades por entrada; desafiantes aprendidos no episódio; remoção e troca testadas; refinamento hierárquico; níveis online; orçamento fixo de ~10² operações por passo; execução em Cortex-M4F simulado. Nada encontrado a antecipa inteira; cada peça tem precedente.
3. **Nova limitação a declarar:** falta um comparador ARMAX/Kalman online.

## 3. Limitações desta revisão

- Um mecanismo de busca, com limitação de taxa em 5 consultas.
- Leitura por resumo (8 resumos), sem texto integral.
- Buscas só em inglês.
- A literatura de 2026 é muito ativa; trabalhos recentes podem não estar indexados.
- Não é uma revisão sistemática no sentido formal (sem bases bibliográficas fechadas nem dupla triagem).

## Referências novas

- Choi, S. (2026). Anytime-valid evidence for prespecified predictive corrections. arXiv:2608.08174.
- de Heide, R. (2026). Dynamic e-closure for online hypotheses with any-time-valid evidence. arXiv:2608.09927.
- Fernández-Barrios, R., Pastor-López, I., Pikatza-Huerga, A., García Bringas, P. (2026). Candidate comparability before promotion. arXiv:2609.04388.
- Jha, A. (2026). Distributional Granger causality: identification, sequential inference, and adaptive testing. arXiv:2606.22230.
- Lara Pinal, E. M., Das, A., Schlüter, S. (2026). A low-cost IoT device for environmental monitoring and embedded solar forecasting with on-device incremental learning. arXiv:2608.14698.
- Yao, Z., Gang, B., Sun, W. (2025). Safe, always-valid alpha-investing rules for doubly sequential online inference. arXiv:2512.12244.
- Recursive sparse parameter identification of multivariate ARMAX systems with non-stationary observations and colored noise (2025). arXiv:2505.00323.
