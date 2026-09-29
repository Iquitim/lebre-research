# 00 — Resumo executivo forense

**Objeto:** a especificação da LEBRE v0.51 contra o relatório externo "LEBRE – achados e validações" (réplica independente).
**Modo:** forense, sem reparo. O código congelado da v0.51 foi executado sem modificação; os hashes foram verificados em cada processo.

## Divulgações de processo
- A rodada principal (`forensic_runs.py main`) foi executada **antes** de este plano ser redigido. O hash do script foi registrado depois (`FORENSIC_RUNS_SCRIPT_SHA256_AT_MAIN_RUN.txt`). Portanto, nenhum resultado desta investigação é pré-registrado: todos são **análises pós-hoc de diagnóstico**.
- `ARTIFACT_MISSING`: o código e os resultados brutos da réplica (`edubraqd/lebre-prototipo`, `results/lebre051/run_hypotheses.txt`) e o gerador do A8. Todas as conclusões que dependem deles foram rebaixadas.
- As tarefas N1/N2/T1/B1–B4 foram regeneradas a partir da **descrição** da réplica, com 10 sementes e o comprimento de fluxo **escolhido aqui**. O comprimento e o esquema de checagens da réplica são desconhecidos, então as diferenças numéricas finas não são interpretáveis.

## Resultados principais
1. **Garantias estatísticas (H4, H5):** reproduzidas.
   - 0 promoções falsas em 17.686 episódios nulos (limite superior CP95 1,7·10⁻⁴ < α/p = 3,0·10⁻⁴).
   - Remoção de átomo útil a ~3·10⁻⁶ por passo ativo, sempre com redescoberta.
2. **Descoberta estrutural (H6):**
   - **Atraso único:** suportada (B1 0,93; T1 0,98).
   - **Múltiplos atrasos:** falha (B2 0,57), sensível a τ.
   - **Latente:** falha total (B3 0,00), robusta a τ e ao normalizador.
   - **Caudas pesadas:** falha (B4 0,27).
3. **Mecanismo do B3 (novo):** a hipótese da crítica, *saturação do conjunto ativo*, **não** se sustenta no código original. O orçamento só fica cheio em 3,5% do tempo e não houve bloqueios.
   - A causa é o **limite de um único latente**: o primeiro polo a cruzar o limiar (0,0 ou 0,5, em 10/10 sementes) ocupa a vaga, e o acionamento correto (polo 0,8) nunca fica elegível.
   - A estrutura é representável, mas inalcançável.
4. **Latência (H7):** o gate de 2.000 passos é viável (limite inferior de 300–600 passos). A falha vem da **vazão da busca e da triagem** (primeira proposta a ~1.500–2.900 passos), e não do poder do teste. A aritmética serial da crítica está errada, mas o mecanismo de vazão existe.
5. **H8:** **NOT_SUPPORTED**. O critério vinculante (≤ 1,01 em todas as tarefas) falha no B3 (1,020); nas demais tarefas a razão fica ≤ 1,001, mas isso é só descritivo. **H9:** suportado quando comparado com a variante densa do próprio projeto, nas 3 convenções de contagem (razão de FP de 0,15–0,20). O resultado de 0,32–0,35 da réplica depende da contabilidade dela.
6. **Pontos da crítica que procedem:**
   - A especificação é **insuficiente para reprodução**: τ, T_max, triagem, vagas, política com o conjunto cheio, limite de latentes e ε não são documentados, e a normalização está descrita de forma errada.
   - O ε do NLMS falta; a memória sem ε **diverge** no caso "plano seguido de degrau".
   - O "~1,3 KB" depende de d e s juntos (≈ 196d + 12s + ~190 B): vale até s = 78 com d = 1, s = 13 com d = 5 e nunca com d = 6.
   - A cadência de 8 do quantil causa **aliasing de fase**: cobertura real de 0,85–0,97, contra 0,90 no operador acumulado.
   - "Estabilidade" mede só sensibilidade ao *burn-in*.
   - "Melhor não-fundação" não é defensável: o airline por MLE pós-hoc é 5% melhor.
   - Não há evidência estrutural em dados reais: 16/20 séries são dominadas por M (w_S ≈ 0), e 15/20 não têm nenhuma promoção estrutural.
7. **Veredicto da v0.51:** as garantias estatísticas e o desempenho de previsão (com escopo) se mantêm. A afirmação de descoberta estrutural tem de ser restrita a atrasos únicos, e a especificação precisa de correção.
   - **Nenhum reparo foi feito.** Os ramos E (quantil em lote) e F (contrato numérico do NLMS) são isoláveis e autorizáveis.
   - O ramo que realmente importa, a seleção do polo latente e a vazão da busca, **não** está na lista pré-definida e depende de revisão humana.
