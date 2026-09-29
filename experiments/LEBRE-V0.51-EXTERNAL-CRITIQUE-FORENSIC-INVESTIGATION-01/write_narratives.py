#!/usr/bin/env python3
"""write_narratives.py — writes the narrative forensic artifacts (01, 08–17, 19, 21) from fixed text + run outputs."""
import os

import pandas as pd

H = os.path.dirname(os.path.abspath(__file__))
W = lambda name, txt: open(os.path.join(H, name), "w", encoding="utf-8").write(txt.strip() + "\n")
tau = pd.read_csv(os.path.join(H, "RUN_TAU_SUMMARY.csv")); main = pd.read_csv(os.path.join(H, "RUN_MAIN_SUMMARY.csv"))
h5 = pd.read_csv(os.path.join(H, "AUDIT_H5_EXPOSURE.csv")); nl = pd.read_csv(os.path.join(H, "AUDIT_NLMS_EPSILON.csv"))
mm = pd.read_csv(os.path.join(H, "AUDIT_MEMORY_SCALING.csv")); qc = pd.read_csv(os.path.join(H, "AUDIT_QUANTILE_CADENCE.csv"))
tel = pd.read_csv(os.path.join(H, "AUDIT_HELDOUT_TELEMETRY.csv")); fr = pd.read_csv(os.path.join(H, "AUDIT_FORECASTING_RECONCILIATION.csv"))
md = lambda df: df.to_markdown(index=False)

W("01_ARTIFACT_AUTHORITY_MAP.md", f"""
# 01 — Mapa de autoridade dos artefatos

| Nível | Artefato | Disponível | Observação |
|---|---|---|---|
| 1 — resultados brutos | `INTERNAL_V051_RESULTS.csv`, `HELDOUT_V051_*.csv`, `V051_DECISION.json` (v0.51) e `RUN_*.csv` / `AUDIT_*.csv` (este estudo) | sim | gerados pelo código abaixo |
| 1 — resultados brutos da réplica | `results/lebre051/run_hypotheses.txt` | **ARTIFACT_MISSING** | só existem os números transcritos no relatório PDF |
| 2 — código executável | `lebre_v051.py`, `lebre_s051.py` (hashes congelados conferem) e `experiments/bench01/streams.py` (escalonador) | sim | autoridade para o comportamento |
| 2 — código da réplica | `edubraqd/lebre-prototipo/src/lebre051/` | **ARTIFACT_MISSING** | repositório privado |
| 3 — configuração congelada | `FREEZE_V051_SHA256.txt`, `FREEZE_S051_SHA256.txt`, `CODE_DATA_SHA256_AT_PREREG.txt` | sim | todos conferem |
| 4 — pré-registro | `PREREG_V051.md` + `PREREG_V051_SHA256.txt` | sim (local) | não publicado com o documento |
| 5 — especificação | `LEBRE_ARCHITECTURE_v0.51_SPEC_{{PTBR,EN}}.pdf` | sim | omite parâmetros (ver 03) |
| 6 — relatório da réplica | `LEBRE-achados-e-validacoes(-2).pdf` | sim | fonte das hipóteses H4–H9 |
| 7 — narrativa | relatórios `V051_REPORT.md` e `POSTHOC_FEEDBACK_REPORT.md` | sim | subordinados aos níveis 1–4 |

**Divergências entre níveis documentadas neste estudo:**
- A especificação diz que as entradas são padronizadas "por médias e variâncias acumuladas até o instante anterior". O código (nível 2) usa uma **média exponencial com α = 10⁻⁴**, iniciada em média 0 e variância 1. Prevalece o código.
- A especificação não diz o que fazer quando o conjunto ativo está cheio. O código **substitui** a vítima de maior CUSUM se R ≥ h/2. Prevalece o código; a lacuna fica registrada.
- A especificação não limita o número de estados latentes. O código admite **um só** e deixa de testar os demais polos enquanto ele está ativo. Esse fato decide o B3.
""")

W("08_H7_THROUGHPUT_FEASIBILITY.md", f"""
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
""")

W("09_A8_NORMALIZATION_AUDIT.md", f"""
# 09 — A8 e a normalização

1. **Normalização autoritativa da v0.51.**
   - Nos benchmarks externos, o ambiente usa `CausalStandardScaler`: EMA com α = 10⁻⁴ (constante de tempo ~10.000 passos), início em média 0 e variância 1, piso de variância 10⁻⁴.
   - Na suíte interna (onde se mediram os ~91% de estrutura), as entradas entram **sem** normalização (já são ~N(0,1)).
   - A réplica usou o normalizador da sua própria v0.1 (EMA de ~100 passos), que **não** é o da v0.51.
2. **Tarefa A8.** É uma tarefa da v0.1 do replicador; o gerador não está disponível (`ARTIFACT_MISSING`), então o A8 não pôde ser executado.
3. **Diagnóstico possível sem o A8.** B1–B3 com entrada bruta, com o escalonador do projeto e com um EMA de 100 passos no estilo da réplica (tabela de `RUN_NORM_SUMMARY.csv`):

{md(pd.concat([main[(main.arm == 'V051') & main.task.isin(['B1', 'B2', 'B3'])].assign(norm='raw'), pd.read_csv(os.path.join(H, 'RUN_NORM_SUMMARY.csv'))]).groupby(['task', 'norm']).agg(exact=('exact_frac', 'mean'), nmse=('nmse', 'mean')).round(3).reset_index())}

   Com entradas estacionárias, o normalizador não altera a estrutura recuperada. O efeito descrito pela crítica depende de entradas não estacionárias, como os regimes do A8.
4. **Classificação** (três afirmações separadas):
   - `A8_REPRODUCTION_STATUS = NOT_EXECUTABLE`: faltam o gerador e os resultados brutos da réplica.
   - `A8_NORMALIZATION_IMPLEMENTATION_DIFF = CONFIRMED`: pela descrição da própria réplica, ela usou um EMA de ~100 passos, e não o escalonador da v0.51 (EMA com α = 10⁻⁴).
   - `A8_NORMALIZATION_CAUSAL_ROOT_CAUSE = INSUFFICIENT_EVIDENCE`: a diferença existe, mas não há como demonstrar que ela explica o resultado do A8. Nas tarefas estacionárias B1–B3 o normalizador não tem efeito, e isso não diz nada sobre entradas não estacionárias.
   - O efeito do escalonador autoritativo em entradas não estacionárias continua **sem teste**. Não se generaliza do A8 para as demais tarefas.
""")

W("10_B3_ACTIVE_SET_SATURATION_AUDIT.md", f"""
# 10 — B3: o conjunto ativo saturou?

## Mecânica (código autoritativo)
1. **Capacidade:** M_max = 4 átomos estruturais. O latente e o acionamento contam; as entradas atuais da base não contam.
2. **Átomos verdadeiros do B3:** lag(3,12), latente com polo 0,8 e acionamento x0 → latente(0,8).
3. **Dependência de elegibilidade:** o acionamento só é testado depois que um latente é promovido, e herda o polo **desse** latente.
4. **Latente único:** enquanto um latente está ativo, nenhum outro polo é testado.
5. **Conjunto cheio:** existe substituição, mas só de vítimas com R ≥ h/2.

## Linha do tempo por semente (`10_B3_ACTIVE_SET_TIMELINES.png`, `RUN_MAIN_B3_TIMELINE.csv`)
- Em **10 de 10 sementes** o primeiro latente promovido tem polo **0,0 ou 0,5**. O polo 0,8 **nunca** fica ativo: tempo ativo com polo 0,0 = 46,6%, polo 0,5 = 50,2%, nenhum = 3,1%.
- O orçamento fica cheio (4 átomos) em só **3,5%** dos instantes de decisão. Houve **0** cruzamentos de limiar bloqueados por orçamento cheio.
- O lag(3,12) verdadeiro é encontrado em 10/10 sementes. Aparecem atrasos aproximados de x0 (1 e 2 passos), mas raramente, em 1–2 sementes.
- **Sensibilidade a τ:** o res(0,8) chega a ser promovido quando o prior é conservador (ρ = 1/1000: 5/10 sementes). Mesmo assim, a estrutura exata continua 0, porque os outros átomos deixam de ser encontrados.

## Resposta
**A estrutura verdadeira é representável, mas inalcançável pela política atual de busca e seleção.**
- O latente de polo 0,8 com acionamento x0 reproduz o processo z exatamente, então não falta representação.
- O que falta é um caminho até essa estrutura: o polo que primeiro acumula evidência (o mais simples) ocupa a única vaga de latente, e o acionamento correto nunca fica elegível.

A hipótese da crítica ("atrasos aproximados enchem as vagas") **não** é o mecanismo no código original. A ausência de troca é uma escolha da réplica, porque o código tem troca.

- `B3_ACTIVE_SET_SATURATION = NOT_SUPPORTED` (como mecanismo no código original).
- `B3_FAILURE_EXPOSES_SPECIFICATION_GAP = YES`: nem a regra de troca nem o limite de um latente estão na especificação.
- Mecanismo real: `WRONG_ATOM_PROMOTION + ELIGIBILITY_DEPENDENCY` (latente único, polo definido pelo primeiro que cruza o limiar).
""")

tt = pd.concat([main[(main.arm == 'V051') & main.task.isin(['N1', 'B2', 'B3'])].assign(rho=1.0), tau]).groupby(['task', 'rho']).agg(exact=('exact_frac', 'mean'), promotions=('promotions', 'sum'), nmse=('nmse', 'mean')).round(3).reset_index()
W("11_TAU_SENSITIVITY_AUDIT.md", f"""
# 11 — Sensibilidade ao τ do martingale (ANÁLISE DE SENSIBILIDADE, não otimização)

**Derivação no código:** τ = ρ / (σ̂² · m_φ), com ρ = 1. É um prior de informação unitária: a mistura gaussiana sobre λ tem variância igual à de uma observação, e m_φ é a potência de projeto do regressor. A especificação mostra τ só dentro da fórmula, sem valor nem unidade.

**Correspondência com a réplica:** a réplica usa m ∈ {{50, 200, 1000}}, no estilo de Howard et al. (fronteira ajustada para um tempo intrínseco m). Isso corresponde aproximadamente a ρ = 1/m. A grade pré-definida usou exatamente esses valores; nenhum outro foi testado.

{md(tt)}

- **N1:** nenhuma promoção falsa para nenhum τ.
- **B2:** limítrofe. ρ = 1 e 1/50 dão ~0,58, abaixo do alvo de 0,80 da réplica. Com ρ mais conservador a estrutura some (1/200 → 0,28; 1/1000 → 0,00). A crítica relatou o efeito oposto (m = 1000 elevaria o B2 para 0,841); com o código original isso **não** se reproduz.
- **B3:** exato = 0 em toda a grade.

**Classificação:** `TAU_SENSITIVITY = SPEC_UNDERSPECIFIED`. O parâmetro não está na especificação, e o resultado de múltiplos atrasos depende dele (**BOUNDARY_SENSITIVE** para o B2). A falha do B3 é **ROBUST** a τ.
""")

W("12_NLMS_EPSILON_AUDIT.md", f"""
# 12 — ε do NLMS

1. **O código autoritativo usa ε?**
   - **S:** sim, ε = 10⁻⁶ absoluto no denominador.
   - **M:** não. A atualização só é pulada quando ‖φ‖² = 0 exatamente.
2. **Documentado?** Não.
3. **Invariância de escala.** Com w ← w + μ e φ/(‖φ‖² + ε), um ε absoluto fixo quebra a invariância: o passo efetivo em escala c é μ c² ‖φ‖²/(c² ‖φ‖² + ε), que depende de c. Na M (sem ε), a invariância é **exata**: NMSE idêntico de ×10⁻⁶ a ×10⁶. Em compensação, **não há proteção** quando ‖φ‖ é pequeno e o erro é grande.

{md(nl.round(6))}

- **O caso "plano seguido de degrau" diverge** (NMSE ~8·10²⁰; |w| ~4,5·10¹¹): os incrementos recentes são ~0 enquanto o erro é grande. Esse é o mecanismo que a crítica observou no R1m sem período.
- Séries quantizadas com platôs e alvos quase constantes não divergiram neste teste.
- **Efeito nos resultados reportados:** nenhuma divergência no held-out (0 divergências registradas). O risco é real em séries com platôs longos seguidos de saltos.

**Classificação:** `NLMS_EPSILON_SPEC = CODE_ONLY` para S (ε absoluto não documentado) e **MISSING/UNSTABLE** para M. `NLMS_NUMERIC_CONTRACT = UNSTABLE`.
""")

W("13_MEMORY_SCALING_AUDIT.md", f"""
# 13 — Escala de memória

**Estado persistente pela fórmula do código** (contabilidade em float32; Python guarda float64, ou seja, o dobro):
- **S:** 4(L+1)d + 8 + 28|A| + 4|polos| + 4|q| + 2·dL + 12|hot| + 24 bytes. Com d = 5 dá ≈ 1,08 KB, **independente de s**.
- **M:** buffer de **2s+2** valores + perfil de **s** valores + pesos, o que dá 4·(3s + k + 8) bytes ≈ **12s bytes**. A crítica estimou ~2s floats; o código guarda ~3s, porque o buffer tem o dobro do necessário para as defasagens usadas (s e s−1).

{md(mm[['d', 's', 'S_bytes', 'M_bytes', 'total_bytes_code_formula', 'python_float64_equivalent_bytes']])}

- Separação: parâmetros do modelo (pesos de S e M: < 100 floats), buffer de fluxo (histórico de defasagens de S: (L+1)·d; buffer de M: 2s+2), estado sazonal (s) e memória de trabalho (vetores temporários O(d + k)).
- **MEMORY_COMPLEXITY** = 4·[(L+1)d + 2dL/4 + 3s + O(|A| + |hot| + k)] bytes ≈ **196d + 12s + ~190 bytes** (float32; conferido contra `memory_bytes()` para d = 1–6 e s ∈ {24, 144}). Sem sazonalidade: ≈ 196d + 180.
- **Envelope do "~1,3 KB"** (≤ 1.331 B, calculado com `memory_bytes()` do código). O limite depende de d **e** s ao mesmo tempo:

| d | sem sazonalidade | maior s com ≤ 1,3 KB |
|---|---|---|
| 1 | 376 B | 78 |
| 2 | 572 B | 62 |
| 3 | 768 B | 46 |
| 4 | 964 B | 29 |
| 5 | 1.160 B | 13 |
| 6 | 1.356 B | nenhum (já excede sem sazonalidade) |

  Com s = 144: 2,1–3,1 KB; com s = 1440: ~18 KB; com s = 10.080: ~122 KB. O valor declarado é uma mediana do held-out, não um limite do envelope.
""")

W("14_QUANTILE_CADENCE_AUDIT.md", f"""
# 14 — Cadência do intervalo (8 passos)

## Implementação real (código)
A cada 8 passos (t ≡ 0 mod 8): q ← max(0, q + 8·γ·σ̂·(1{{|e_t| > q}} − α)). Só o indicador **do passo de atualização** entra, multiplicado por 8 (operador A).
O operador alternativo B soma os 8 indicadores do bloco: q ← q + γ·σ̂·Σ(1{{|e|>q}} − α). O operador C atualiza a cada passo.
Em séries periódicas, **A e B não são equivalentes**: se 8 divide s, A só observa s/gcd(8,s) fases. Por exemplo, 3 de 24 com s = 24 e 18 de 144 com s = 144.

## Resíduos periódicos sintéticos (σ_t periódico, amplitude 0,8)
{md(qc.round(4))}

## Resíduos reais do próprio modelo (held-out; o operador só altera o intervalo, não a previsão)
{md(tel[tel.s.notna()][['src', 'task', 's', 'cov_A', 'cov_B', 'cov_C']].round(3))}

- Com o operador A, a cobertura real varia entre 0,85 e 0,97 conforme a série. Com B ou C, todas ficam em 0,900–0,906.
- O Q1 (0,965, a única série fora da faixa no pré-registro) vai para 0,901 com B.
- A cobertura por fase é ruim em todos os operadores (mínimos de 0,3–0,8), porque a cobertura é marginal, não condicional, como a especificação já declarava.

**Classificação:** `QUANTILE_CADENCE_PHASE_ALIASING = SUPPORTED`. O operador B é o candidato natural de correção, mas **não** foi adotado nesta etapa.
""")

W("15_FORECASTING_CLAIM_RECONCILIATION.md", f"""
# 15 — Reconciliação das afirmações de previsão

Razão = NMSE da LEBRE / NMSE do modelo. Valores < 1 indicam a LEBRE melhor. "Válidas" são as séries em que o modelo concluiu sem falha.

{md(fr.round(3))}

- **Comparadores online pré-registrados** (protocolo comum de 10 séries): a LEBRE é a melhor. Razão 0,84 contra o NLinear, 8/10 vitórias; contra DLinear, Holt-Winters e IPNLMS, vence em 10/10.
- **Clássicos pós-hoc:**
  - **airline por MLE**, 9 séries (falha de memória na implementação de espaço de estados com s = 144): **1,054**; a LEBRE vence 3/9.
  - **Só M:** 0,967.
  - **RLS:** 6 séries válidas, com 4 divergências.
  - Modelos com coberturas diferentes (10, 9, 6 ou 4 séries) não devem entrar num único ranking ordinal.
- **Modelos de fundação:** Chronos-2 é melhor (LEBRE/Chronos-2 = 1,357). O Chronos-2 com covariáveis só cobre 4 séries.

**Frase mais forte defensável:**
"Melhor modelo entre os comparadores online pré-registrados, no protocolo comum de 10 séries (0,84× o NLinear calibrado). Um modelo airline ajustado por máxima verossimilhança, avaliado depois (pós-hoc), é ~5% mais preciso nas 9 séries em que rodou, e o Chronos-2 é ~1,36× mais preciso, com custo 10⁶–10⁷ vezes maior."

**Não é defensável:** "melhor modelo não-fundação", porque existe um clássico pós-hoc mais forte. Também não se deve pôr num único ranking ordinal modelos com coberturas diferentes.

**Terminologia "held-out":**
- O conjunto principal (Q1–Q10) nunca foi usado por nenhuma versão: held-out genuíno.
- O segundo conjunto (N1–N10) já havia sido usado para avaliar a v0.5, e N1/N4 são séries do BENCH-04 em outro período. Deve ser chamado de **semi-held-out**. A §9.6 da especificação o chama de "já visto", mas a §10 o conta como held-out: a inconsistência procede.
""")

W("16_STABILITY_SEMANTICS_AUDIT.md", """
# 16 — O que a "estabilidade" mede

Protocolo: a mesma janela final de teste, com 0, 50, …, 450 passos iniciais descartados.

- **Mede:** sensibilidade do resultado à inicialização e ao período de aquecimento (*burn-in*). Ou seja, se o modelo converge para o mesmo desempenho independentemente de como começou.
- **Não mede:** estabilidade entre trechos diferentes da série (regimes, estações, anos), nem variância entre janelas independentes. Nenhuma janela independente foi avaliada.
- **Nome adequado:** "sensibilidade à inicialização (burn-in)". A frase "estável" na especificação deve ser restrita a esse sentido. Não se pode afirmar robustez temporal.
""")

W("17_REAL_STRUCTURAL_EVIDENCE_AUDIT.md", f"""
# 17 — Evidência estrutural em dados reais

Telemetria do S dentro da v0.51 nos dois conjuntos held-out (código original, harness original):

{md(tel[['src', 'task', 'd', 's', 'mean_wS', 'max_wS', 'frac_wS_gt_0.5', 'S_structural_promotions', 'S_removals', 'S_contribution_rms_rel']].round(3))}

**Classificação por série:**
- **MEMORY_DOMINATED:** 16/20, com w_S ≈ 0. 15 delas não têm nenhuma promoção estrutural; a N6 tem 1 promoção sem peso no combinador. Inclui as 7 séries do ONS com 6 entradas.
- **MIXED:** Q5 e N5 (câmbio): w_S médio de 0,27–0,44, contribuição < 1,2% do desvio do alvo; e N10 (KDD S3): w_S 0,16, contribuição de 4,6%.
- **STRUCTURAL_DOMINATED:** Q9 (qualidade do ar KDD S4): w_S médio de 0,56, contribuição de 21% do desvio do alvo; o ganho sobre M é real (NMSE 0,101 contra 0,138 da M sozinha).
- Nenhuma dessas séries é um sistema guiado por entradas no sentido pretendido. Nas séries com d = 1, as "entradas" são apenas o próprio passado do alvo.

`REAL_STRUCTURAL_DISCOVERY = INSUFFICIENT_EVIDENCE` (status: **OPEN**). A recuperação sintética não autoriza nenhuma inferência sobre dados reais.
""")

W("19_LITERATURE_SCOPE_MAP.md", """
# 19 — Mapa de escopo da literatura

| Tema | Resultado externo estabelecido | Relevância para a LEBRE | Hipóteses que não se transferem | Hipótese específica da LEBRE |
|---|---|---|---|---|
| Martingales de mistura / sempre válidos (Howard et al. 2021; de la Peña 1999; Ville 1939) | supermartingale sob incrementos condicionalmente simétricos; P(sup M ≥ 1/a) ≤ a | promoção | simetria condicional com parâmetros adaptados online; σ̂² estimado | erro tipo I ≤ α/p por episódio no laço adaptativo (verificado só empiricamente) |
| Continuação opcional / *skipping* previsível (Ramdas, Grünwald, Vovk & Shafer 2023) | e-processos válidos sob parada e continuação opcionais | portões de silêncio, quarentena e dormência | validade por teste, não controle de família entre testes | pular por regra previsível preserva a validade de cada teste |
| Seleção sequencial de variáveis (Foster & Stine 2008, alpha-investing; Zhou et al. 2005) | controle de mFDR ao longo de fluxos de hipóteses | retestes e acúmulo de falsas promoções | a LEBRE não gasta nem ganha "riqueza" de α | α/p fixo por episódio basta em fluxos longos (0/17.686 episódios nulos) |
| Filtragem adaptativa / regularização do NLMS (Haykin 2002; Benesty, Paleologu & Ciochină 2011) | o ε ótimo depende da SNR e da escala da entrada; ε fixo quebra a invariância | ε da M e do S | a literatura supõe entrada estacionária | NLMS sem ε na M é seguro, o que o degrau refuta |
| Esparsidade limitada / troca no conjunto ativo (online sparse / sparse LMS, Chen, Gu & Hero 2009) | penalização ℓ1 contínua, sem conjunto discreto | orçamento M_max e troca | a LEBRE usa seleção discreta com testes | a troca por R ≥ h/2 alcança a estrutura verdadeira (refutado no B3 pelo latente único) |
| Detecção de mudança com penalidade de complexidade (Page 1954; Lorden 1971; Rissanen 1978) | ARL ≥ e^h para o CUSUM sem deriva | remoção | o aluguel de parcimônia adiciona deriva, e a garantia se perde | remoções como "perda de utilidade" (taxa empírica de 3·10⁻⁶ por passo ativo) |
| Média dinâmica de modelos (Raftery, Kárný & Ettler 2010) | pesos por verossimilhança preditiva com esquecimento | combinador | 2 especialistas, perdas normalizadas | η = 1/2 derivado; no B3 a combinação custa 2% (limite de 1% da réplica) |
| Quantil online (Gibbs & Candès 2021; Angelopoulos et al. 2023) | cobertura de longo prazo para atualização a cada passo | intervalo | a atualização em lotes com um só indicador não está coberta | a cadência de 8 preserva a taxa (refutado com 8 dividindo s) |
| Identificação de sistemas / ARX em espaço de estados (Ljung 1999; Harvey 1989) | preditor de Kalman estacionário em forma de inovações | estado latente | as ordens e o número de estados são conhecidos na literatura | um único latente com banco de polos basta (limitante no B3) |
""")

W("21_CORRECTIVE_BRANCH_DECISION.md", """
# 21 — Decisão sobre ramos corretivos

| Ramo | Condição de autorização | Evidência | Decisão |
|---|---|---|---|
| A — normalização | S canônico sofre o problema do normalizador | a réplica usou outro normalizador; em B1–B3 nenhum efeito; A8 indisponível | **não autorizado** (evidência insuficiente; exige um teste não estacionário pré-registrado antes) |
| B — troca no conjunto ativo | falha do B3 causada por vagas cheias | orçamento cheio em 3,5% do tempo, 0 bloqueios; a causa é o latente único e a escolha de polo | **não autorizado** na forma proposta; o mecanismo real sugere um ramo diferente (seleção/revisão do polo latente), que não está na lista |
| C — vazão de teste | H7 limitado pela vazão, e não pelo poder | proposta tardia (~1.500–2.900 passos) com teste rápido (~200–300 passos); mecanismo observado, não isolado | **candidato mais forte**, mas o mecanismo é de *busca/triagem* e não de vagas de teste |
| D — poder do martingale | testes observados, com evidência lenta | as amostras até o cruzamento (90–150) são adequadas; só o átomo fraco do B2 sofre futilidade | não autorizado |
| E — atualização do quantil em lote | aliasing de fase reproduzido | **reproduzido** em dado sintético e real (0,85–0,97 → 0,900–0,906) | **autorizável** isoladamente |
| F — contrato numérico do NLMS | ambiguidade do ε afeta resultados ou estabilidade | divergência reproduzida no degrau; nenhum efeito no held-out | **autorizável** isoladamente (baixo risco) |

**Recomendação para revisão humana:**
- Os ramos **E** e **F** atendem às condições e são isoláveis.
- O problema estrutural principal (B3 e H7) aponta para dois mecanismos que não estavam na lista pré-definida: a *seleção do polo com latente único* e a *vazão da triagem*. Eles precisam de um desenho novo antes de qualquer experimento.
- Pelas regras desta etapa, **nenhum reparo foi executado**, e a decisão final cabe à revisão humana (`AUTHORIZED_CORRECTIVE_BRANCH = HUMAN_REVIEW`).
""")
print("ok")
