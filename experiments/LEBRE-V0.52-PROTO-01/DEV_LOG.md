# LEBRE v0.52 — Diário de desenvolvimento (só dados de desenvolvimento)

Registro de todas as decisões tomadas olhando dados de **desenvolvimento**, antes de qualquer acesso ao held-out. O carregador (`data_v052.py`) recusa tarefas de held-out, e isso foi testado (Jupiá foi recusada).

## 26/09/2026

### Bugs corrigidos (sem efeito sobre a arquitetura)
1. **Parsing da opção:** `kind[-1]` tratava "v052-II" como opção I. Corrigido.
2. **Coeficiente do desafiante:** o NLMS de um único coeficiente era normalizado por φ² instantâneo, que gera passos explosivos quando φ ≈ 0. Passou a ser normalizado pela potência média de φ.
3. **Memória:** a média exponencial não era iniciada quando os primeiros alvos faltavam. Sem média, a reversão agora é 0.
4. **Execução:** resultados sintéticos perdidos por gravação só no fim. Agora a gravação é incremental.

### Regra de validade de dados acrescentada (achado no desenvolvimento)
- **Observação:** a base horária do ONS ("não verificada") contém erros grosseiros, com Furnas registrando até 972 mil m³/s para uma afluência típica de ~1.000. Isso tornava o NMSE sem sentido e fazia qualquer modelo autorregressivo divergir.
- **Regra (causal, igual para todos os modelos):** um valor é inválido se exceder **20 × o percentil 90 da própria série nos 7 dias anteriores**. Janela de 56 blocos de 3 h no ONS, aplicada ao alvo e às entradas; janela de 168 h no BDG2, aplicada ao alvo.
- **Status:** fixada agora, antes do held-out, e passa a integrar `SPLIT_RULES.md` e o pré-registro.

### Correção numérica da memória
- **Observação:** um medidor de água quente do BDG2 fazia a memória divergir. É o caso "trecho constante seguido de salto" da Errata E4/E5 da v0.51: o ε relativo decaía junto com o sinal.
- **Correção:** o denominador do NLMS passou a ser ‖φ‖² + 10⁻³·EMA(‖φ‖²) + 10⁻⁴·EMA_lenta(y²), que é invariante à escala e sobrevive a trechos constantes. Resultado nesse medidor: NMSE ∞ → 0,029 (v0.51: 2,097).

### Decisões de arquitetura
1. **Opção I descartada.** Estrutura somada diretamente à memória, sem combinador: a âncora no último valor prejudica séries sem memória própria (T1: 0,842 contra 0,656; N1: 1,286 contra 1,071).
2. **Opção II → IIb.** Julgar as mudanças na previsão *combinada* gera um impasse. Quando a memória domina, w_S → 0 e nenhum desafiante mostra melhora, então a estrutura nunca cresce (latente B3: 0 átomos). Na **IIb**, as mudanças são julgadas na previsão do **próprio especialista estrutural** S, e o combinador decide o uso. Continua sendo um teste válido de melhora preditiva, agora da previsão de S.
3. **Hipóteses persistentes** (substituem "uma hipótese por experimento"):
   - **Problema:** com ~600 experimentos por fluxo de 20 mil passos, o nível e-LOND caía para ~10⁻⁶, e só 1 de 3 atrasos era encontrado.
   - **Solução:** um e-process por candidato ("in") e por átomo ativo ("out"), que acumula evidência entre episódios. As pausas são uma subsequência previsível (Choe & Ramdas, §F.1).
   - **Nível:** γ = 1/(2P) para as primeiras P = 2p hipóteses, depois 0,5·γ_k (Σγ ≤ 1), multiplicado por α·(R + 1) na criação. A hipótese é consumida na aceitação; uma reentrada cria nova instância.
   - **Efeito (IIb, 3 sementes):** B2 passou de 1/3 para **3/3** atrasos (NMSE 0,763 → 0,576); B3 de 0 para 1,33/3 átomos (0,735 → 0,596); N1 continua com 0 aceitações.
4. **Limiar de triagem `screen_z = 2`.** O limiar 3 reduz os experimentos em 3×, mas quase dobra a latência no T1, e as hipóteses persistentes já tornam o número de experimentos inofensivo para o nível.

### Pendências conhecidas
- **Poder e latência:** a v0.51 ainda prevê melhor nos sintéticos com vários atrasos e com latente (B2 0,488; B3 0,375), porque promove mais cedo. A primeira descoberta da v0.52 leva ~2,8–4 mil passos.
- **Latente (B3):** recuperação parcial, com átomos aproximados aceitos (melhoram a previsão, mas não são a estrutura verdadeira).
- **Custo:** ~200–215 FP/passo no protótipo, acima do alvo de 150. Precisa de otimização (recalcular o log-e a cada k passos, menos filtros).
- **Semi-sintéticos** a partir das entradas do rio Grande: ainda não gerados.
- **Topologia do ONS:** falta conferir com o diagrama oficial.

### Avaliação completa de desenvolvimento com a IIb (26/09/2026; `DEV_SYNTH.csv`, `DEV_REAL.csv`)

**Sintéticos (5 sementes):**
- **Mudanças falsas:** 0 em N1, N2, T1, B1 e B2.
- **Estrutura:** B2 com 2,8/3 atrasos (estrutura exata no fim em 80% das sementes); B3 com 1,4/3 átomos e 1 átomo aproximado aceito.
- **NMSE, IIb × v0.51:** T1 0,657 × 0,653; B1 0,661 × 0,652; N1 1,070 × 1,070; **B2 0,592 × 0,488; B3 0,538 × 0,375** (a v0.51 ainda é melhor com vários atrasos e com latente).

**Reais de desenvolvimento** (média geométrica do NMSE relativo à v0.51; vitórias da IIb):

| Grupo | Tarefas | Só M | IIb | Vitórias |
|---|---|---|---|---|
| ONS (rio Grande) | 11 | 1,896 | **1,020** | 4/11 |
| CAMELS-BR | 10 | 0,790 | **0,630** | 9/10 |
| BDG2 | 5 | 0,431 | **0,418** | 4/5 |
| Silverbox | 1 | 0,941 | 0,941 | 1/1 |
| Cascaded Tanks | 2 | 0,986 | 0,986 | 1/2 |

- A melhora sobre a v0.51 no CAMELS e no BDG2 vem em boa parte da **memória corrigida** (só M já fica em 0,79 e 0,43).
- A **estrutura** aparece em 13 das 29 tarefas reais, com leituras fisicamente plausíveis:
  - ONS: M. Moraes ← Furnas com atraso de 2 blocos (6 h); Igarapava ← Jaguara com 1 bloco (3 h); Volta Grande ← Igarapava com 2 blocos, mais um latente;
  - CAMELS: precipitação filtrada (armazenamento da bacia) em 2 bacias;
  - Cascaded Tanks: entradas filtradas por vários polos (armazenamento dos tanques).
- **Custo:** 164 FP/passo em média, acima do alvo de 150. **Cobertura:** 0,906.

### Custo × poder (26/09/2026; `TUNE_COST.csv`, `TUNE_CLIP.csv`, `TUNE_FRONTIER.csv`)

- **Contagem de FP revisada** para ser mais honesta (cada vaga custa ~25–28 FP por passo).
- **Evidência a cada 2 passos:** corta ~40 FP, mas dobra a latência e piora o B2 (0,63 → 0,74). **Rejeitada:** evidência a cada passo.
- **Coeficiente inicial pela triagem:** sem ganho. **Rejeitado.**
- **Polo 0,5 retirado** dos filtros e latentes: custo menor, com pequena perda no B2/B3. **Mantido** (os atrasos 1–2 cobrem a dinâmica curta).
- **Escala de recorte da perda k = 2** (antes 3): maior razão sinal/limite no e-process (o λ fica limitado por 1/c). É o maior ganho de poder: B2 0,630 → **0,504**, com 3/3 atrasos e latência 4,4 mil → 2,6 mil. **Adotado.**
- **Fronteira custo × latência** (k = 2, d = 5, 5 sementes):

| Vagas | FP | B2 atrasos | B2 NMSE | 1ª descoberta T1 |
|---|---|---|---|---|
| 1 | 171 | 2,2/3 | 0,699 | 3.600 |
| 2 | 201 | 3/3 | 0,526 | 2.678 |
| 3 | 226 | 2,8/3 | 0,531 | 2.034 |
| 4 | 240–254 | 3/3 | 0,504 | 2.514 |

- **Micro-otimizações:** a exponencial do combinador passa a ser recalculada a cada 8 passos; a potência da triagem só é rastreada quando necessária.
- **decide_every = 20 foi testado e revertido para 10:** o B2 piorou de 0,526 para 0,577 com ganho de só ~2 FP.
- **Padrões atuais:** opção IIb, k = 2, 2 vagas, evidência a cada passo, decisão a cada 10 passos, polos {0,8; 0,95}.
- **Custo real de desenvolvimento** (2 vagas, decisão a cada 20): média de 146 FP (d = 1: 132; d = 3: 152; BDG2 com s = 24: 175). Sintéticos com d = 5: ~185–194.
- **O custo fixo com d = 5 já é ~140 FP** (base densa + filtros + memória + controle). Portanto o orçamento de 150 FP com d = 5, herdado da v0.51, **não é atingível** sem retirar capacidades. **Decisão pendente com o responsável pelo projeto.**

### Motor genérico, correção e triagem (26/09/2026)

- **Motor de experimentos separado** (`change_engine.py`): hipóteses persistentes, e-process, níveis LOND e vagas, independentes do tipo de estrutura. É a preparação para governar mudanças multivariadas no futuro (roteiro rumo a um world model). A refatoração foi verificada **bit a bit** contra `REGRESS_BASELINE.json` (previsões, eventos, FP e estrutura em 4 tarefas).
- **Correção:** depois de uma aceitação, os experimentos sobre os átomos alterados passam a ser encerrados de fato (antes a lista filtrada era sobrescrita). A regressão ficou idêntica nas 4 tarefas de referência, pois o caso é raro.
- **Triagem normalizada pela potência de projeto analítica** (`TUNE_SCREENNORM.csv`, 5 sementes):
  - **Problema:** entradas filtradas e latentes têm potência (1−p)/(1+p) ≪ 1; com o escore bruto perdiam o ranking para atrasos sem sinal, e o filtro verdadeiro do B3 nunca chegava ao topo.
  - **Alternativas testadas:** escore bruto; normalização por média móvel de φ² (ruidosa, piorou o B2); **normalização analítica** (exata, sem custo, como na v0.51).
  - **Resultado da analítica:** B2 0,526 (3/3); **B3 0,484** (2,4/3, 0,2 aceitações aproximadas; antes 0,656 e 1,2/3; v0.51: 0,375); T1 com latência 2,7 mil → 3,4 mil. **Adotada.**
- **Referência de regressão regravada** com o novo comportamento.

### Avaliação completa com os padrões atuais (26/09/2026; `DEV_SYNTH.csv`, `DEV_REAL.csv`)

**Padrões:** opção IIb, k = 2, m = 2, evidência a cada passo, decisão a cada 10 passos, polos {0,8; 0,95}, triagem com normalização analítica, encerramento dos experimentos superados.

**Sintéticos (5 sementes):**
- **Mudanças falsas:** 0 em N1, N2, T1, B1 e B2; 0,2 no B3 (termo aproximado).
- **Estrutura exata no fim:** B2 100%; B3 40% (2,4/3 átomos).
- **NMSE, IIb × v0.51:** T1 0,655 × 0,653; B1 0,652 × 0,652; B2 0,526 × 0,488; **B3 0,484 × 0,375**.

**Reais de desenvolvimento** (média geométrica do NMSE relativo à v0.51):
- **Todas as 29 tarefas: 0,755** (só M: 1,013), ou seja, o ganho vem da arquitetura, não só da memória corrigida.
- **Por grupo:** CAMELS 0,656 (9/10 vitórias); BDG2 0,420 (4/5); **ONS 1,046 (3/11): pendência.**
- **Estrutura** em 18 das 29 tarefas. **Custo:** 152,5 FP de média, 196,5 no máximo. **Cobertura:** 0,906.

**Contrato de complexidade:** `COMPLEXITY_CONTRACT.md` (lei FP ≈ 63 + 17,5 d + 26·[s=24] + 20 m; perfis embarcado, padrão e fronteira).

### Investigação do ONS: contrato de entrada P6 restaurado (26/09/2026; `TUNE_CONTRACT.csv`)

- **Diagnóstico:** a diferença para a v0.51 no ONS (1,046) vinha de duas tarefas.
  - **Igarapava** (1,56): a v0.52 só aceitava o atraso verdadeiro de 2 blocos perto do fim do fluxo.
  - **Furnas** (1,16): nenhum dos dois acha estrutura, mas o S da v0.51 recebe mais peso.
- **Causa encontrada:** a v0.52 não tinha trazido o **contrato de entrada P6** da v0.45/v0.51. Depois de um valor recortado (|x| > 8), a parte estrutural não aprende nem testa por L passos, enquanto o valor extremo ainda está nas defasagens.
- **Validade:** a pausa é previsível, e a memória continua aprendendo (não usa as entradas).
- **Efeito:**
  - Igarapava 0,116 → **0,069** (v0.51: 0,075);
  - ONS 1,046 → **1,000**; CAMELS 0,656 → 0,638; BDG2 igual;
  - **todas as 29 tarefas: 0,755 → 0,735** do erro da v0.51;
  - sintéticos idênticos à referência de regressão.
- **Adotado como padrão** (`input_contract=True`).
- **Pendência:** Furnas (1,03 × 0,89). Reservatório grande, com muita afluência incremental não observada; a entrada de montante explica pouco. Fica registrado, sem ação.

### Comparação competitiva de desenvolvimento e próprio passado do alvo (26/09/2026; `COMP_DEV.csv`, `TUNE_SELFINPUT.csv`, `EVAL_SYNTH.csv`)

**Protocolo único** (`comp_dev.py`):
- todos os modelos preveem em cada passo com alvo observado;
- NMSE numa máscara comum (teste a partir de 30%);
- comparadores online calibrados na janela inicial, como na v0.51;
- airline SARIMA ajustado por máxima verossimilhança na janela de calibração.

**Antes da mudança** (média geométrica do NMSE relativo ao NLinear calibrado):
- **Todas as tarefas:** v0.52 **0,874**; airline 1,017; DLinear 1,25; Holt-Winters 1,44; AMRules 5,1; v0.51 2,76 (diverge num medidor do BDG2).
- **ONS:** v0.52 **0,587** (entradas causais: a estrutura dá a vantagem).
- **CAMELS:** v0.52 1,242 (perde para NLinear e airline 0,874).
- **BDG2:** v0.52 1,014 (airline 0,984).
- **Custo:** v0.52 148 FP; NLinear 671; DLinear 1.525; Holt-Winters 20.

**Diagnóstico do CAMELS:** falta o passado do próprio alvo. A memória sem sazonalidade só vê o último valor e o último incremento, e o dicionário só tem as entradas externas. A recessão da bacia fica sem representação.

**Mudança adotada: o passado do próprio alvo** (y_{t−1}, preenchido causalmente) vira **uma entrada a mais do dicionário**.
- Padronização causal idêntica à das entradas, implementada dentro do modelo (`self_input=True`) e verificada como idêntica à versão feita no harness (diferença máxima de 0,0).
- **Efeito real** (relativo ao NLinear): ONS 0,587 → **0,576**; CAMELS 1,242 → **0,994**; BDG2 1,014 → **0,930**; **todas 0,874 → 0,791** (airline 1,017). Custo 148 → 156 FP.
- **Efeito sintético** (5 sementes):
  - 0 aceitações falsas de entradas externas e 0 termos do próprio alvo nos nulos;
  - B3 com NMSE 0,484 → **0,423** (v0.51: 0,375), com menos átomos "verdadeiros" (1/3): termos do próprio passado cumprem parte do papel do latente;
  - **B2 pior (0,526 → 0,618)**, ainda com 3/3: o dicionário maior dilui a busca;
  - custo com d = 5 (+1): ~212 FP.
- **Troca aceita** porque o ganho em dados reais é grande e generalizado.

**Lacuna competitiva restante:** CAMELS contra o airline ajustado série a série (0,994 × 0,874).

**Referência de regressão** regravada com o novo padrão.

### Modelos de fundação nos mesmos pontos (26/09/2026; `chronos_dev.py`, `COMP_DEV_1000PTS.csv`)

**Protocolo:** Chronos-Bolt tiny e small e Chronos-2, zero-shot, univariados (sem covariáveis), contexto de 512, previsão mediana a um passo, em 1.000 pontos igualmente espaçados do teste. Todos os modelos são avaliados **nos mesmos pontos**.

**Média geométrica do NMSE relativo ao NLinear:**

| Grupo | v0.52 | Chronos-2 | Bolt small | Bolt tiny | airline |
|---|---|---|---|---|---|
| ONS | **0,646** | 0,885 | 0,921 | 0,958 | 1,055 |
| CAMELS | 0,951 | 0,892 | 0,963 | 1,018 | **0,881** |
| BDG2 | 0,920 | **0,780** | 0,870 | 0,900 | 0,993 |
| **Todas** | **0,813** | 0,926 | 1,051 | 1,138 | 1,060 |

- A v0.52 vence o Chronos-2 em **16 de 29** tarefas. Custo: ~165 FP/passo contra ~10⁹–10¹⁰ estimados do Chronos-2 (120 milhões de parâmetros).
- **Ressalvas:**
  1. São dados de **desenvolvimento**, nos quais a v0.52 foi ajustada; o Chronos não.
  2. O **Chronos-2 com covariáveis não foi avaliado**; é o comparador justo para tarefas guiadas por entradas e **precisa entrar no pré-registro**.
  3. Furnas é uma anomalia nesses pontos (v0.52 1,72 contra ~0,78 dos demais) e precisa de investigação.

### Furnas, comparação justa e semi-sintéticos (26/09/2026)

- **Furnas:**
  - **Causa 1:** o próprio alvo tem erros grosseiros isolados (20–43 mil m³/s numa série de ~1.000) que a regra de validade (20×p90) não pega, porque a série varia muito.
  - **Causa 2:** o efeito específico da v0.52/v0.51 vem depois do pico. O valor contaminava a memória e o próprio passado, e a previsão explodia (±40 mil) nos blocos seguintes.
  - **Correção no modelo** (a avaliação continua com o alvo bruto, igual para todos): **contrato P6 do alvo**. Se |y − ŷ| > 8σ (depois de 200 passos de aquecimento), o valor é armazenado limitado a ŷ ± 8σ e não gera aprendizado nem evidência. Os sintéticos continuam idênticos à referência de regressão.
- **Topologia do ONS:** conferida contra o cadastro oficial (ver `SPLIT_RULES.md` §7). Consistente; a divisão não muda.
- **Comparação justa: comparadores que usam as entradas**, porque os univariados (NLinear, airline) não recebiam a informação exógena que a v0.52 recebe:
  - **SARIMAX-X:** airline com x_t…x_{t−4} como regressores, ajustado por máxima verossimilhança;
  - **ARX denso online:** NLMS sobre todas as defasagens 0–32 das entradas e 1–32 do alvo, com passo calibrado;
  - **Chronos-2 com covariáveis:** covariáveis passadas no mesmo contexto e **a entrada atual x_t como covariável futura conhecida**, a mesma informação dos modelos online.
- **Semi-sintéticos** (`semi_synth.py`, estruturas declaradas antes de rodar): entradas reais do rio Grande (defluentes de 5 usinas) e alvo por estrutura conhecida (nulo, um atraso, vários atrasos, armazenamento com latente, sazonal + atraso), 5 sementes (6101–6105).
- **Contrato do alvo revertido** (`target_contract=False`), `TUNE_KAPPA.csv`:
  - com κ = 8/16/32 ajudava no ONS (0,576 → 0,533), mas **prejudicava o BDG2 para qualquer κ** (0,930 → 1,06): não distingue erro de registro de pico real;
  - a correção foi movida para os **dados**: regra de salto do ONS (`SPLIT_RULES.md` §8), igual para todos os modelos;
  - todos os modelos serão rodados de novo sobre os dados corrigidos.
- **Comparação com comparadores que usam as entradas** (antes da regra de salto; relativo ao NLinear):
  - ONS: v0.52 **0,533**; ARX denso 0,567 (390 FP); SARIMAX-X 0,824;
  - CAMELS: SARIMAX-X **0,808**; v0.52 1,047 (com o contrato do alvo);
  - BDG2: SARIMAX-X **0,965**;
  - **todas:** v0.52 **0,803**; SARIMAX-X 0,971; ARX 1,139.
  - **Leitura honesta:** no ONS, boa parte da vantagem vem de *usar as entradas* (o ARX denso chega perto); a descoberta de estrutura acrescenta precisão e ~2,4× menos custo.

### Dados corrigidos, Chronos-2 com covariáveis e semi-sintéticos (27/09/2026)

**Com a regra de salto** (máscara completa, relativo ao NLinear): todas — v0.52 **0,793**, SARIMAX-X 0,992, ARX denso 1,155; ONS — v0.52 0,579, ARX 0,589, v0.51 0,607.

**1.000 pontos, com o Chronos-2 com covariáveis** (média geométrica relativa ao NLinear):

| Grupo | Chronos-2 + cov. | v0.52 | Chronos-2 |
|---|---|---|---|
| ONS | **0,500** | 0,535 | — |
| CAMELS | **0,838** | 0,951 | — |
| BDG2 | **0,718** | 0,920 | — |
| **Todas** | **0,701** | 0,757 | 0,915 |

- **Leitura honesta:** com a mesma informação, o **Chronos-2 com covariáveis é mais preciso que a v0.52** em todos os grupos. A v0.52 vence em 7/29 tarefas, a um custo ~10⁷× menor. Na fronteira precisão × custo ela não é dominada, mas **em precisão pura não é competitiva com o modelo de fundação**.

**Semi-sintéticos** (5 sementes, NMSE; ARX / NLinear / v0.51 / v0.52): SS0 1,007/1,027/1,060/1,064; SS1 0,601/0,660/0,643/0,649; SS2 0,305/0,342/0,341/0,343; SS3 0,082/0,093/0,099/0,092; SS4 0,419/0,414/0,520/0,519.
- **A v0.52 não aceitou nenhuma estrutura em nenhuma tarefa**, embora ache as estruturas nos sintéticos puros.

**Diagnóstico** (`diag_ss_gain.py`, `diag_ss_trace.py`, `TUNE_NMIN.csv`):
1. **Não é o tamanho do episódio:** n_min de 100, 400 ou 1000 dão resultado idêntico (0 aceitações).
2. **Contrafactual errado sob colinearidade.** As entradas reais a 3 h são suaves (autocorrelação 0,96 no lag 1, 0,89 no lag 3) e colineares. Por OLS offline, o atraso verdadeiro do SS1:
   - vale **10,0%** do MSE da base com reajuste conjunto;
   - vale só **1,8%** ajustado sozinho sobre o resíduo da base congelada, que é o que o desafiante faz.
3. **Estimador ruidoso.** O coeficiente NLMS do desafiante oscila de episódio para episódio (lag(3,12), valor correto ≈ 1: −0,45, +0,65, −0,41, +0,76), porque com regressores autocorrelacionados o gradiente anda aleatoriamente. O erro de estimação come o ganho e o δ médio fica negativo, mesmo para átomos que valeriam 6–8%.
4. **Triagem:** os átomos verdadeiros ficam em posições baixas (26ª a 205ª de 206). Candidatos vizinhos colineares ocupam o topo.

**Correção em teste** (opção, padrão inalterado, `REGRESS` idêntico): desafiante `rls2`, com mínimos quadrados recursivos no episódio sobre [átomo, valor atual da própria fonte]. O atraso passa a ser julgado líquido do que x_t já carrega. Na aceitação, a correção da fonte é transferida para a base. Há também um aquecimento opcional (`chal_warm`) em que as primeiras amostras do episódio só treinam o desafiante (subsequência previsível). Resultado em `TUNE_CHAL.csv`.

**Resultados das correções do desafiante** (`TUNE_CHAL.csv`, `TUNE_CHAL_2.csv`; 3 sementes):
- `rls2`: zero aceitações nos semi-sintéticos. No SS1, o episódio do atraso verdadeiro passou a ter δ médio **positivo** (+0,006 em 3.003 amostras), mas foi encerrado em T_max com log_e 1,68 contra o limiar 9,71; pela variância observada, precisaria de ~17 mil amostras. Nos sintéticos puros melhora o B2 (0,621 → 0,555) sem falsas.
- `rls2` persistente (estado do desafiante guardado na hipótese): zero aceitações em SS0–SS3; aceita defasagens do próprio alvo no SS4; **1 falsa exógena no B3**. Descartado.
- **Triagem é o gargalo de identificação.** A triagem pelo resíduo coloca os átomos verdadeiros em posições baixas (lag(1,3) 105ª; lag(3,12) 42ª–113ª), porque entradas suaves espalham a correlação cruzada pelos atrasos vizinhos.
- **Pré-branqueamento** (Box–Jenkins, `diag_prewhiten.py`): mesmo com AR(1) por entrada, os atrasos verdadeiros vão para 1º, 1º, 2º, 1º e 12º de 160 (AR(8): 1º, 1º, 3º, 4º, 1º). Custo ~11·d FP/passo.
- Implementado como `screen_norm="prewhite"`: a_i é estimado causalmente (EMA da autocorrelação de ordem 1), e o resíduo é filtrado pelo mesmo a_i. `REGRESS` idêntico. Grade em `TUNE_CHAL_3.csv`.
- **Resultado do pré-branqueamento no modelo** (`TUNE_CHAL_3.csv`): zero aceitações exógenas nos semi-sintéticos (0 falsas nos nulos; B2 melhora para 0,576 com `rls2`). O rastreio explica o porquê:
  - **Orçamento de amostras da triagem.** Com 2 sondas por passo sobre 206 candidatos, cada candidato é atualizado a cada ~103 passos, e a EMA com peso 0,2 retém ~5 amostras efetivas. O ruído da pontuação (~0,33 do d.p. do resíduo) enterra correlações verdadeiras de 0,1–0,3. No SS1 o atraso verdadeiro ficou em 145º; defasagens do próprio alvo e filtros de polo 0,95 ocuparam o topo.
  - **Poder do teste.** Quando o átomo verdadeiro é testado, a evidência cresce devagar. No SS3, lag(3,12): 3.000 amostras, δ médio +0,006, log_e 1,13 contra o limiar 9,71 (log(2P/α), com P = 412 hipóteses). Seriam necessárias ~2·10⁴ amostras por descoberta, perto do comprimento da série inteira.
- **Conclusão:** em entradas reais (suaves, colineares, efeito de ~10% do MSE), a v0.52 atual **não tem poder** para descobrir estrutura dentro do comprimento das séries. O controle de erro está correto (0 falsas), mas o mecanismo não entrega a descoberta, que é o seu propósito. Os ajustes locais (n_min, RLS, persistência, pré-branqueamento da triagem) não resolvem. O problema é de **unidade de hipótese e de orçamento**: 412 hipóteses atômicas, cada uma com uma fração pequena do ganho.

### Reformulação: hipótese por entrada (27/09/2026) — critérios fixados ANTES de implementar

**Desenho:** a unidade de hipótese passa de "um atraso de uma entrada" (412 hipóteses) para "**uma entrada inteira**" (d+1 unidades: cada entrada, incluindo o próprio passado do alvo, mais o estado latente do resíduo).
- O desafiante de uma entrada é um **bloco de resposta** com médias de atrasos em faixas diádicas ([1], [2–3], [4–7], [8–15], [16–32]) mais a correção do valor atual, ajustado em conjunto por mínimos quadrados recursivos.
- A triagem é uma estatística de grupo por entrada, com pré-branqueamento AR(1), atualizada **a cada passo**.
- A versão atômica fica congelada neste protótipo como ablação.

**Critérios de sucesso** (dados de desenvolvimento; medidos uma vez, sem ajuste depois de ver):
1. Semi-sintéticos: encontrar as entradas verdadeiras em pelo menos **2 de 3** tarefas com estrutura exógena (SS1–SS3), na maioria das sementes.
2. **Zero** descobertas exógenas falsas nos nulos (N1, N2, SS0) e nenhuma entrada falsa nas demais tarefas.
3. Nos dados reais (ONS, CAMELS, BDG2), média geométrica do NMSE relativo **não pior** que a v0.52 atômica (tolerância de 1%).
4. Custo dentro do contrato (~200–250 FP/passo com d = 5+1).

**Se falhar:** registrar o resultado negativo e reposicionar a contribuição (preditor barato, com controle de erro, que só muda diante de efeitos grandes).

**Primeira medição da versão por entrada** (`lebre_v052u.py`; `EVAL_UNIT.csv`, `REAL_UNIT.csv`, `COMP_DEV_1000PTS_UNIT.csv`). Sem ajuste de hiperparâmetros: faixas, limiares e aquecimento foram fixados antes de rodar.

| Critério | Resultado | Situação |
|---|---|---|
| 1. Entradas verdadeiras (SS1–SS3, maioria das sementes) | SS1 2/3 sementes; SS2 1 de 3 entradas em 1/3 sementes; SS3 0/3 | **Falhou** (1 de 3 tarefas) |
| 2. Zero falsas exógenas | 0 em todos os nulos e tarefas | Passou |
| 3. Dados reais não piores (média geométrica vs NLinear) | Todas: **0,694** vs 0,793 (atômica); ONS 0,521 vs 0,579; CAMELS 0,929 vs 0,994; BDG2 **0,957 vs 0,930** | Passou no total; **falhou no BDG2** (−3%) |
| 4. Custo ~200–250 FP | ~340 FP nos reais; ~430–590 nos sintéticos | **Falhou** (sem compressão ainda) |

- **Regressão nos sintéticos puros** (não era critério, mas é defeito): T1 0,652 → 0,863; B1 0,647 → 1,060; B2 0,621 → 0,902. A causa é o bloco de **médias por faixa**: com entradas brancas, um atraso exato fica diluído (lag 12 numa faixa de 8 valores retém ~1/8 do efeito). Com entradas suaves, a média por faixa perde pouco.
- **1.000 pontos, mesmo protocolo do Chronos** (máscara reconstruída; checagem exata contra a v0.52 armazenada, diferença 8e-17, n idêntico):

| Grupo | v0.52 por entrada | Chronos-2 + cov. | v0.52 atômica | ARX denso | SARIMAX-X |
|---|---|---|---|---|---|
| ONS | **0,478** | 0,500 | 0,535 | 0,529 | 0,847 |
| CAMELS | 0,895 | 0,838 | 0,951 | 1,208 | **0,825** |
| BDG2 | 0,982 | **0,718** | 0,920 | 2,008 | 0,970 |
| **Todas** | **0,663** | 0,701 | 0,757 | 1,109 | 0,988 |

- A versão por entrada vence o Chronos-2 com covariáveis em **14 de 29** tarefas, a ~340 FP/passo.
- **Ressalvas:**
  1. Dados de desenvolvimento. A reformulação foi motivada por diagnósticos em dados de desenvolvimento (semi-sintéticos, não as séries reais).
  2. O ganho no total vem do ONS e do Silverbox (0,937 → 0,107). O BDG2 piora e continua longe do Chronos-2.
  3. Pelos critérios fixados, a reformulação **não passou** (critérios 1 e 4). A melhora nos dados reais é real, mas não substitui os critérios.
- **Próxima iteração proposta:** refinamento hierárquico (faixa → metades, estilo Haar, cada divisão uma hipótese; Meinshausen 2008, Yekutieli 2008) e compressão de custo. Deve ser medida em **sementes novas** (6104, 6105) e em **estruturas semi-sintéticas novas declaradas antes**, para não ajustar até passar nas mesmas tarefas.

### Iteração hierárquica — conjunto de avaliação declarado ANTES de implementar (27/09/2026)

- **Desenvolvimento/ajuste** permitido apenas em: semi-sintéticos SS0–SS4 (sementes 6101–6103) e sintéticos puros (sementes 9101–9103).
- **Medição dos critérios** (uma vez, com a configuração congelada antes):
  - semi-sintéticos **novos** SN0–SN4 (`semi_synth2.py`: nulo; resposta distribuída; duas entradas; armazenamento + atraso; **nulo com alvo autocorrelacionado**), sementes **6201–6203**;
  - sintéticos puros com sementes **novas 9201–9203**;
  - dados reais de desenvolvimento, que não são "novos". Não há alternativa sem tocar o held-out, o que continua proibido.
- **Critérios** (os mesmos, adaptados):
  1. entradas verdadeiras em pelo menos 2 de 3 tarefas estruturadas SN1–SN3, na maioria das sementes;
  2. zero entradas exógenas falsas (SN0, SN4, N1, N2 e todas as demais);
  3. dados reais não piores que a v0.52 atômica, no total e por grupo, com tolerância de 1%;
  4. custo médio nos reais ≤ 250 FP/passo;
  5. (novo) sintéticos puros não piores que a atômica em mais de 5% em nenhuma tarefa.

**Desenvolvimento da versão hierárquica** (`lebre_v052h.py`; conjuntos antigos; `TUNE_HIER*.csv`):
- **Só faixas + divisões** (sem pico):
  - T1 é refinado até o atraso exato (lag 3, peso 0,79; NMSE 0,650);
  - B1 fica em 1,06: a entrada é aceita tarde ou nunca.
  - Diagnóstico: a triagem acerta (x1 no topo), mas o **teste** não tem poder, porque o desafiante com médias de faixa expressa só 1/8 do atraso 12 (5.000 amostras, δ +0,0038, log_e 1,27 contra 6,33).
- **Atraso de pico no desafiante.** O e-process é válido para qualquer desafiante previsível. O desafiante de uma entrada passa a carregar também o seu atraso mais forte, escolhido por ele mesmo pela correlação pré-branqueada na primeira metade do aquecimento, antes de qualquer evidência. Resultado (3 sementes; atômica entre parênteses):
  - sintéticos: B1 0,646 (0,647); B2 **0,467** (0,621); B3 **0,398** (0,429); T1 0,650 (0,652); nulos iguais;
  - semi-sintéticos: SS2 0,325 (0,344); SS3 0,085 (0,092); SS4 0,494 (0,518); SS1 0,649 (0,650);
  - **zero exógenas falsas.**
- **Custo** (antes da compressão): 330–640 FP. Estrutura ~120 fixos; triagem ~100–140; experimentos 90–300 (mínimos quadrados com 7 parâmetros). Em teste: triagem a cada 8 passos e desafiante atualizado em passos alternados (`TUNE_HIER_3.csv`).
- Cortes de custo (`TUNE_HIER_3.csv`): triagem a cada 8 passos e/ou mínimos quadrados em passos alternados baixam para 230–460 FP, mas perdem descobertas (SS2 1,33 → 0–0,33) e **todas** as variantes baratas aceitam 1 entrada exógena fora da verdade no SS2. Descartados.

**CONGELAMENTO para a medição** (antes de rodar o conjunto novo): `lebre_v052h.py` com os padrões do construtor (peak=True, screen_w=0,02, screen_every=4, m_slots=2, rls_every=1). SHA-256 (16 primeiros): lebre_v052h.py `1a30054bc5aa714a`; change_engine.py `6da8ccc70fc7376b`; lebre_v052.py (Memory/POLES) `212872117d795203`. Configuração escolhida só com dados de desenvolvimento, por ser a melhor em precisão e descoberta, com zero falsas. **Espera-se que falhe no critério 4 (custo)**, o que será reportado sem alterar o critério.

**MEDIÇÃO FINAL da versão hierárquica** (código congelado, hash `1a30054bc5aa714a` conferido antes da execução; `FINAL_HIER_SYNTH.csv`, `REAL_HIER.csv`, `COMP_DEV_1000PTS_HIER.csv`).
- *Incidente de script:* na primeira execução, a substituição de texto que criava o modo `--final` não foi aplicada, e a parte sintética rodou de novo os conjuntos antigos. Os dados reais rodaram corretamente. O erro foi percebido pela saída (sementes 9101…), o script foi corrigido e o conjunto declarado rodou uma única vez. Nenhuma decisão foi tomada com base na execução errada.

| Critério | Resultado (hierárquica vs atômica) | Situação |
|---|---|---|
| 1. Entradas verdadeiras em ≥ 2 de 3 tarefas SN1–SN3 (maioria das sementes) | SN1 0/3 sementes; SN2 x3 em 3/3 sementes (x1 nunca); SN3 x4 em 1/3 | **Falhou** |
| 2. Zero exógenas falsas | 0 em tudo, inclusive o nulo com alvo autocorrelacionado (SN4) | Passou |
| 3. Reais não piores, total e por grupo (±1%) | Total **0,693** vs 0,793; ONS 0,519 vs 0,579; CAMELS 0,924 vs 0,994; BDG2 **0,956 vs 0,930** | **Falhou no BDG2** (−2,8%); passou nos demais |
| 4. Custo ≤ 250 FP nos reais | 357 FP | **Falhou** |
| 5. Sintéticos puros não piores >5% | B2 **0,495** vs 0,747; B3 0,390 vs 0,404; B1, T1 e nulos iguais | Passou |

- **Semi-sintéticos novos (NMSE):** SN2 **0,493** vs 0,593; SN3 0,425 vs 0,428; SN1 0,517 = 0,517; nulos iguais. No SN1 (resposta distribuída numa entrada suave) nenhuma versão descobre a entrada, e as duas preveem igual: o valor atual x2(t) já carrega quase toda a informação.
- **1.000 pontos, protocolo do Chronos** (relativo ao NLinear):

| Grupo | Hierárquica | Chronos-2 + cov. | Atômica |
|---|---|---|---|
| ONS | **0,475** | 0,500 | 0,535 |
| CAMELS | 0,872 | **0,838** | 0,951 |
| BDG2 | 0,994 | **0,718** | 0,920 |
| Todas | **0,660** | 0,701 | 0,757 |

  Vence o Chronos-2 com covariáveis em 13/29 tarefas.
- **Leitura:** pelos critérios fixados, a iteração **não passou** (critérios 1, 3-BDG2 e 4). Ela é, porém, a melhor versão em precisão até agora em todos os conjuntos, exceto o BDG2, e preserva o controle de erro. As lacunas remanescentes são claras:
  1. descoberta lenta em entradas suaves e colineares (primeira aceitação entre 12 e 26 mil passos);
  2. BDG2, onde as entradas (clima) parecem atrapalhar;
  3. custo cerca de 1,4× acima do contrato.

### Diagnóstico da lentidão da descoberta — passo 1: tempo de teste (27/09/2026; `diag_duty.py`; SS3, semente 6101, desenvolvimento; modelo congelado, sem alteração)

**Critério definido antes:** se a fração de tempo em teste fosse < 20% e explicasse o atraso, o escalonamento seria a causa. **Resultado: não é.** A entrada verdadeira x3 esteve em teste **61%** do tempo (51% em amostras de evidência).

| Episódio | Início–fim | Pico escolhido | Amostras de evidência | Soma | log_e | Fim |
|---|---|---|---|---|---|---|
| 1 | 390–900 | lag 28 (errado) | 103 | −0,18 | −0,05 | varredura |
| 2 | 2.720–3.280 | lag 31 (errado) | 275 | −0,12 | −0,09 | varredura |
| 3 | 4.860–10.100 | lag 12 (certo) | **5.008** | +39,2 | **5,05** | T_max |
| 4 | 10.730–11.290 | lag 12 | 360 | — | 6,33 | aceito |

- Incrementos de evidência: média +0,0080, d.p. 0,094. Pela deriva, n* ≈ 2·6,33·σ²/μ² ≈ **1.800** amostras. O e-process precisou de **~5.400**.
- **Causa principal: conservadorismo do e-process nesta escala.** O incremento é limitado a [−1, 1], e o código usa c = 2(1+ε), a amplitude total, o que limita λ < 0,9/c ≈ 0,45. O λ ótimo seria S/V ≈ 0,81, acima do teto. No teto, a penalidade ψ_E cresce muito (cλ = 0,9 → ψ ≈ 0,35 contra λ²/2 ≈ 0,10). Com a grade grossa (fator 2) e a penalidade da mistura (log 8 ≈ 2,1 nats, um terço do limiar), o melhor termo fica em ~7,0 e a mistura em **5,0**, exatamente o valor observado. Os incrementos têm d.p. ~0,1, mas o teste os trata como se pudessem chegar a ±2.
- **Causas secundárias:**
  1. Nas duas primeiras tentativas, o pico escolhido em 100 amostras de aquecimento foi errado (lags 28 e 31), porque em entrada suave 100 amostras são poucas. Isso somou ~4.900 passos antes do episódio útil, incluindo a espera de 2.000.
  2. O encerramento por T_max (5.000) custou ~630 passos. A evidência é persistente, então não se perdeu.
  3. As vagas ficaram **vazias 37%** do tempo.
- **Hipótese para o passo 2** (verificar na teoria antes de codar): no Teorema 3 de Choe & Ramdas, a constante c do ψ_E pode ser o limite **inferior** dos incrementos centrados (~1), não a amplitude total (~2). Se for, o teto de λ e a penalidade caem e a evidência cresce ~2× mais rápido, sem perder validade. Alternativa conhecida: λ previsível adaptado à variância observada (plug-in de Waudby-Smith & Ramdas 2023) no lugar da grade fixa.

### Diagnóstico — passo 2: conferência teórica da constante c (27/09/2026; só leitura, nenhum código alterado)

**Fontes conferidas** (arXiv; citações obtidas por ferramenta de leitura e conferidas pela dedução abaixo):
- Choe & Ramdas, *Comparing Sequential Forecasters* (arXiv 2110.00115v6): assumem |δ̂_i| ≤ c/2 e γ_i predizível em [−c/2, c/2]; daí |δ̂_i − γ_i| ≤ c. É uma condição **suficiente**, de dois lados.
- Howard, Ramdas, McAuliffe & Sekhon, *Time-uniform, nonparametric, nonasymptotic confidence sequences* (arXiv 1810.08240v9): o Teorema 4 também é enunciado com X ∈ [a, b] e c = b − a. Mas a demonstração (§A.8) usa apenas o lema de Fan, Grama & Liu (2015), **exp{λξ − ψ_E(λ)ξ²} ≤ 1 + λξ para todo ξ ≥ −1 e λ ∈ [0, 1)**, com ξ = (X_i − X̂_i)/c. Só o limite **inferior** X_i − X̂_i ≥ −c é usado.

**Dedução para o nosso caso** (teste unilateral, λ ≥ 0, nula fraca E_{i−1}[d_i] = μ_i ≤ 0):
1. Se d_i − γ_i ≥ −c, então exp{λ(d_i − γ_i) − ψ_{E,c}(λ)(d_i − γ_i)²} ≤ 1 + λ(d_i − γ_i).
2. Multiplicando por exp{λ(γ_i − μ_i)} e tomando a esperança condicional: ≤ (1 + λ(μ_i − γ_i))·e^{λ(γ_i − μ_i)} ≤ 1, porque 1 + x ≤ eˣ.
3. Como λ ≥ 0 e μ_i ≤ 0, exp{λ Σd_i − ψ_{E,c}(λ) V_t} é limitado por uma supermartingala não negativa, com V_t = Σ(d_i − γ_i)².
4. **Nenhuma condição sobre γ_i além de ser predizível**, e nenhuma cota superior de d_i.

**Consequência:** d_i = lf − lg − ε ≥ −(1 + ε) sempre. Com γ_i = min(média passada, 0), vale d_i − γ_i ≥ −(1 + max(ε, 0)), e **c = 1 + max(ε, 0) ≈ 1,002** é válido, contra os 2,004 atuais. A mistura continua válida, pois é média de e-processes, e as pausas continuam sendo subsequência predizível.

**Ganho esperado** (recalculado com os números do SS3, passo 1: μ = 0,0072 por amostra, σ² = 0,0089):
- c = 2,004 (atual): taxa ≈ 0,0013/amostra → ~6.500 amostras até o limiar com a penalidade da mistura (observado ~5.400).
- c = 1,002: melhor termo λ = 0,449 → taxa ≈ 0,0019/amostra → **~4.400 amostras** (~1,5× mais rápido; se tivesse sido usado, o log_e no fim do episódio 3 seria ~8,4 contra o limiar 6,33, e a aceitação teria vindo antes do T_max).
- O limite teórico (λ ótimo 0,81, sem penalidade de mistura) é ~2.200–2.900. A distância restante vem do ψ_E, que protege contra incrementos de até −c, enquanto o d.p. real é ~0,1. Isso só se reduz trocando a grade fixa por um **λ predizível adaptado à variância observada** (apostas, Waudby-Smith & Ramdas 2023), com ganho estimado ~2–2,5×. É outro passo, a verificar separadamente.

**Implicação para o documento:** a garantia da v0.52 passa a se apoiar na forma unilateral (lema de Fan et al., via a demonstração de Howard et al.), não no enunciado de dois lados de Choe & Ramdas. Isso deve estar explícito na especificação e no pré-registro.

### Iteração "evidência e pico" — conjunto de avaliação #3 declarado ANTES de implementar (27/09/2026)

- **Mudanças planejadas** (ajustadas só nos conjuntos antigos: SS0–SS4 sementes 6101–6103, sintéticos 9101–9103, dados reais de desenvolvimento):
  1. constante c unilateral (passo 2);
  2. opção de evidência por apostas com λ predizível;
  3. estatística do pico persistente entre episódios;
  4. investigação do BDG2 e do custo.
- **Conjunto de medição #3:** `semi_synth3.py` (SP0–SP4, sementes 6301–6303) + sintéticos puros com sementes 9301–9303 + dados reais de desenvolvimento. Medido **uma vez**, com código congelado e hash registrado antes.
- **Critérios** (redação precisa, fixada agora):
  1. **Descoberta:** em SP1–SP3, pelo menos 2 das 3 tarefas com (a) alguma entrada verdadeira na estrutura final em ≥ 2 de 3 sementes **e** (b) cobertura média das entradas verdadeiras ≥ 0,5.
  2. **Zero** entradas exógenas fora da verdade aceitas, em qualquer tarefa (SP0, SP4, N1, N2 e demais).
  3. **Dados reais:** média geométrica do NMSE relativo ao NLinear não pior que a v0.52 atômica em mais de 1%, no total **e** em cada grupo (ONS, CAMELS, BDG2).
  4. **Custo** médio nos dados reais ≤ 250 FP/passo.
  5. **Sintéticos puros:** nenhuma tarefa pior que a atômica em mais de 5%.
  6. **(novo) Controle de erro do teste**, por simulação: sob a nula no limite (média 0), a fração de trajetórias com evidência cruzando log(1/α) = log 20 em 5.000 passos deve ser ≤ α = 0,05, com incrementos com a forma dos observados.

**Evidência — implementação e validação** (`change_engine.py`, opção `evidence`; padrão "psiE2" inalterado, `REGRESS` idêntico).
- Variantes: "psiE1" (c unilateral), "bet" (apostas com λ plug-in aGRAPA, λ ∈ [0; 0,5/(1+ε)]), "mix" (média de psiE1 e bet).
- **Simulação** (`sim_evidence.py`; 400 trajetórias × 5.000 passos; nula no limite, média 0; cruzamento de log 20 em qualquer ponto):

| Evidência | Tipo I: recortada / dois pontos / pesada | Poder (+0,0072) | Tempo mediano |
|---|---|---|---|
| psiE2 (atual) | 0,000 / 0,005 / 0,013 | 0,66 | 3.720 |
| psiE1 | 0,003 / 0,025 / 0,003 | 0,77 | 2.910 |
| bet | 0,020 / 0,033 / 0,035 | **0,91** | **1.520** |
| mix | 0,018 / 0,025 / 0,018 | 0,86 | 1.910 |

  **Critério 6 satisfeito** por todas as variantes (erro-padrão de Monte Carlo ≈ 0,011 em 0,05).

**BDG2 — causa da perda** (`diag_bdg2.py`, hotwater Moose, versão medida): o aquecimento fica desligado ~3.000 passos (y ≡ 0). Nesse trecho, a escala da perda (σ do resíduo) vai a ~0, qualquer ganho absoluto minúsculo vira evidência grande, e **3 estruturas foram aceitas no trecho plano** (t = 13.200; 14.580; 14.820). Quando o aquecimento volta, a estrutura erra (MSE do bloco 13.990 contra 5.775 da atômica).
- **Correção:** `scale_floor`. A escala da perda dos experimentos nunca fica abaixo de 10% da escala lenta de y (EMA 1e-4, média simples no início), o mesmo princípio do piso da memória.
- Com o piso: nenhuma aceitação no trecho plano, e o bloco pós-retomada fica em 5.690 (atômica 5.775).

**Grade de desenvolvimento 1** (`TUNE_DEV1_*.csv`; conjuntos antigos + reais de desenvolvimento). Média geométrica relativa ao NLinear (atômica: todas 0,793 / ONS 0,579 / CAMELS 0,994 / BDG2 0,930):

| Config. | Todas | ONS | CAMELS | BDG2 | Exógenas fora da verdade |
|---|---|---|---|---|---|
| medida (meas2) | 0,693 | 0,519 | 0,924 | 0,956 | 0 |
| + piso de escala | 0,690 | 0,519 | 0,924 | **0,927** | 0 |
| + piso + pico persistente + psiE1 | **0,683** | 0,515 | 0,923 | 0,927 | **0** |
| + piso + pico persistente + bet | 0,682 | 0,514 | 0,912 | 0,934 | **2** (SS1, SS3) |
| + piso + pico persistente + mix | 0,683 | 0,514 | 0,913 | 0,927 | **1** (SS3) |

- As aceitações fora da verdade com bet/mix são **substitutas quase idênticas**: x0 e x1 (Camargos e Itutinga) têm correlação 0,98. Nenhum teste preditivo as distingue com dados finitos (limite de identificabilidade, não erro do controle).
- Como o critério 2 conta qualquer entrada fora da verdade, a escolha é **psiE1**: zero aceitações fora da verdade e precisão praticamente igual.
- **Nota para o desenho futuro:** o critério certo para "descoberta" deveria tratar como equivalentes as entradas quase colineares, ou o modelo deveria reportar o grupo, "x0 ou x1". Não se muda o critério #3 declarado.

**Grades de custo** (`TUNE_DEV2/3_*.csv`; evidência psiE1, piso e pico persistente em todas). Colunas: todas / ONS / CAMELS / BDG2 · FP médio nos reais · exógenas fora da verdade:

| Config. | Precisão | FP | Fora da verdade |
|---|---|---|---|
| base | 0,683 / 0,515 / 0,923 / 0,927 | 361 | 0 |
| + metades sob demanda (lazy) | idêntica | 359 | 0 |
| lazy + triagem a cada 8 | 0,675 / 0,521 / 0,919 / 0,927 | 305 | **1** (SS2) |
| lazy + triagem 8 + RLS a cada 2 | 0,685 / 0,528 / 0,912 / 0,925 | 254 | **1** |
| lazy + triagem 8 + RLS 2 + 1 vaga | 0,690 / 0,526 / 0,935 / 0,932 | 241 | **1** |
| lazy + RLS a cada 2 | 0,693 / 0,521 / 0,926 / 0,926 | 298 | 0 |
| lazy + RLS 2 + 1 vaga | 0,708 / 0,528 / 0,954 / 0,929 | 272 | 0 |
| lazy + RLS 3 + 1 vaga | 0,690 / 0,525 / 0,927 / 0,929 | 255 | 0 |

- A triagem espaçada (a cada 8) produz a aceitação de substituta no SS2 em todas as variantes. Os cortes no desafiante (RLS espaçado, 1 vaga) não produzem.
- O custo tem um piso estrutural alto: memória 23–49, controle ~25, estrutura ~110 com uma unidade ativa (~40 FP por unidade ativa, entre predição e NLMS dos pesos do bloco), triagem ~50–70.
- **lazy + RLS 4 + 1 vaga** (TUNE_DEV4): **249 FP** (dentro do contrato); todas 0,688 / ONS 0,528 / CAMELS 0,897 / BDG2 0,930; zero fora da verdade; mas **zero descobertas nos semi-sintéticos**. Com entradas suaves há um compromisso real entre custo e descoberta: no orçamento de ~250 FP o desafiante não acumula evidência a tempo.

**CONGELAMENTO da medição #3** (antes de rodar; perfis declarados, os dois reportados, sem seleção posterior):
- **PADRÃO** (principal; todos os critérios se aplicam): scale_floor=0,1; peak_persist; evidence=psiE1; lazy_halves; m_slots=2. **Espera-se falha no critério 4.**
- **ENXUTO** (perfil de custo, informativo): o mesmo com rls_every=4 e m_slots=1.
- SHA-256 (16): lebre_v052h.py d803128bbb436c78; change_engine.py 11bb13022e408776; lebre_v052.py 212872117d795203; final3.py 2638ac0d7b686b0e; semi_synth3.py 1c895092027098f1.

**MEDIÇÃO #3** (única; hashes conferidos antes da execução: lebre_v052h `d803128bbb436c78`, change_engine `11bb13022e408776`, final3 `2638ac0d7b686b0e`; `FINAL3_*.csv`, `FINAL3.log`). Critérios para o perfil **PADRÃO**:

| Critério | Resultado | Situação |
|---|---|---|
| 1. Descoberta (≥ 2 de 3 tarefas SP1–SP3) | SP1: x4 em 3/3 sementes (cobertura 1,0); SP2: x3 em 3/3 (cobertura 0,5; x0 nunca); SP3: 0/3 | **Passou** (2 de 3) |
| 2. Zero exógenas fora da verdade | 0 em todas as tarefas e sementes | **Passou** |
| 3. Reais não piores, total e por grupo | Todas **0,683** vs 0,793; ONS 0,515 vs 0,579; CAMELS 0,923 vs 0,994; BDG2 0,927 vs 0,930 | **Passou** |
| 4. Custo ≤ 250 FP | 359 FP | **Falhou** |
| 5. Sintéticos puros não piores > 5% | B2 0,478 vs 0,612; B3 0,384 vs 0,413; B1 0,656 vs 0,658; T1 0,651 vs 0,652; nulos iguais | **Passou** |
| 6. Controle de erro (simulação) | tipo I ≤ 0,025 nas três formas (psiE1) | **Passou** |

- **Perfil ENXUTO** (informativo): 249 FP (passa no 4), mas descobre só SP1 (3/3, tarde: 5 mil a 30 mil passos) e nada em SP2/SP3 (falha no 1). B3 0,453 vs 0,413 (falha no 5). Reais: todas 0,688.
- **Latência de descoberta** (PADRÃO): SP1 entre 4,4 e 6,2 mil passos; SP2 entre 5,4 e 17 mil. Na medição #2 eram 12 a 26 mil passos. Sintéticos puros: 500–2.200 passos.
- **Observação honesta — alvo ruído branco:** no SP0 (y = ruído branco), semente 6302, o PADRÃO aceitou a unidade do **próprio passado do alvo** (x5) em t = 5.270. Não é entrada exógena (não conta no critério 2), mas é uma mudança sem melhora real: um falso positivo em 3 × 5 tarefas nulas-alvo. É compatível com o controle de taxa de mudanças falsas em α = 0,05 (controle de FDR, não garantia de zero), mas é registrado. No SP4 (alvo AR) aceitar o próprio passado é correto.
- **1.000 pontos, protocolo do Chronos** (relativo ao NLinear):

| Grupo | PADRÃO | ENXUTO | Chronos-2 + cov. | Atômica | ARX denso | SARIMAX-X |
|---|---|---|---|---|---|---|
| ONS | **0,472** | 0,491 | 0,500 | 0,535 | 0,529 | 0,847 |
| CAMELS | 0,870 | 0,895 | 0,838 | 0,951 | 1,208 | **0,825** |
| BDG2 | 0,916 | 0,918 | **0,718** | 0,920 | 2,008 | 0,970 |
| **Todas** | **0,645** | 0,666 | 0,701 | 0,757 | 1,109 | 0,988 |

  PADRÃO e ENXUTO vencem o Chronos-2 com covariáveis em 13/29 tarefas cada.
- **Conclusão da iteração:** a versão hierárquica com evidência unilateral, piso de escala e pico persistente cumpre os critérios de descoberta, segurança, precisão e sintéticos. **Não cumpre o contrato de custo** (359 contra 250). O perfil que cumpre o custo perde a descoberta em entradas suaves. **Esse compromisso custo × descoberta é o principal resultado aberto da v0.52.**

### Iteração "custo, grupos e ciclo semanal" — conjunto #4 declarado ANTES de implementar (27/09/2026)

- **Mudanças planejadas** (parcimoniosas; ajuste só nos conjuntos antigos e nos reais de desenvolvimento):
  1. **custo:** cortar partes fixas sem mudar a lógica (pesos vivos atualizados em passos alternados; triagem sem as unidades já ativas; mínimos quadrados do desafiante em passos alternados só depois do aquecimento);
  2. **grupos de entradas equivalentes:** o modelo passa a reportar, junto de cada entrada aceita, as entradas quase idênticas a ela (correlação causal ≥ 0,95); a decisão não muda;
  3. **ciclo semanal na memória**, para séries horárias de prédios (período 168 declarado como metadado do conjunto, como já é o diário de 24).
- **Conjunto de medição #4:** `semi_synth4.py` (SQ0–SQ4, sementes 6401–6403; SQ4 é nulo na média com variância dependente de x0) + sintéticos puros com sementes 9401–9403 + reais de desenvolvimento. Medido **uma vez**, com código congelado e hash registrado antes.
- **Critérios** (os de #3, com o tratamento de grupos fixado agora):
  1. **Descoberta:** em SQ1–SQ3, pelo menos 2 das 3 tarefas com alguma entrada verdadeira, **ou uma do seu grupo de equivalência** (|corr| ≥ 0,95 na amostra inteira), aceita em ≥ 2 de 3 sementes, e cobertura média ≥ 0,5 (grupos contam como a entrada verdadeira).
  2. **Zero** entradas exógenas aceitas fora da verdade **e fora dos grupos** das entradas verdadeiras, em qualquer tarefa (inclui SQ0 e SQ4).
  3. Reais: não pior que a v0.52 atômica em mais de 1%, no total e por grupo.
  4. Custo médio nos reais ≤ 250 FP/passo.
  5. Sintéticos puros: nenhuma tarefa pior que a atômica em mais de 5%.
  6. Controle de erro (simulação), já verificado para psiE1.

**Grade de desenvolvimento 5** (`TUNE_DEV5_*.csv`; base = perfil PADRÃO da medição #3):

| Config. | Todas | ONS | CAMELS | BDG2 | FP | Fora da verdade |
|---|---|---|---|---|---|---|
| base | 0,683 | 0,515 | 0,923 | 0,927 | 359 | 0 |
| custo (pesos vivos a cada 2 + RLS a cada 2 após aquecimento + triagem sem ativas + grupos) | 0,707 | 0,529 | 0,925 | 0,923 | 315 | 0 |
| custo + ciclo semanal | 0,705 | 0,529 | 0,925 | **0,905** | 315 | 0 |

- A perda do pacote de custo vem dos **pesos vivos em passos alternados**: Silverbox 0,095 → 0,198, e as séries do ONS com unidades ativas pioram 1–10%. A estrutura aceita precisa acompanhar a cada passo. Esse corte foi retirado.
- O **ciclo semanal** melhora o BDG2 (0,923 → 0,905; chilledwater 0,812 → 0,774) sem afetar os outros grupos. Só vale onde o período é declarado.
- Com a reprodução exata verificada (código novo com opções desligadas = versão medida em #3, bit a bit).

**Grades 6–7** (TUNE_DEV6/7): sem os pesos vivos alternados, o RLS a cada 2 após o aquecimento ainda custa precisão no Silverbox (0,095 → 0,143; total 0,691; 322 FP). Retirado também. Configuração final (triagem sem ativas + grupos + ciclo semanal): todas **0,680** / ONS 0,515 / CAMELS 0,923 / BDG2 **0,910**; 353 FP; sintéticos idênticos à base; zero fora da verdade. **Os cortes de custo fixo que não mexem na lógica economizam pouco (~2–10%) ou custam precisão; o contrato de 250 FP não é alcançável de forma parcimoniosa nesta arquitetura.**

**CONGELAMENTO da medição #4** (antes de rodar): PADRÃO = #3 + screen_skip_active + track_groups + season2 = 168 nos prédios horários. SHA-256 (16): lebre_v052h.py cc830e6039d520f9; change_engine.py 11bb13022e408776; lebre_v052.py 212872117d795203; final4.py 5452788b17314c03; semi_synth4.py 993c106b71e5fbd8.

**MEDIÇÃO #4** (única; lebre_v052h `cc830e6039d520f9`, final4 `5452788b17314c03`; `FINAL4_*.csv`, `FINAL4.log`):

| Critério | Resultado | Situação |
|---|---|---|
| 1. Descoberta (≥ 2 de 3 tarefas SQ1–SQ3) | SQ1: x1 em 2/3 sementes (grupo reportado {x0, x1}); SQ2: x4 em 3/3 (cobertura 0,5; x2 nunca); SQ3: x3 em 3/3 | **Passou (3 de 3)** |
| 2. Zero exógenas fora da verdade e dos grupos | 0; nada aceito nos nulos SQ0 e SQ4 (variância dependente de x0) | **Passou** |
| 3. Reais não piores, total e por grupo | Todas **0,680** vs 0,793; ONS 0,515 vs 0,579; CAMELS 0,923 vs 0,994; BDG2 **0,910** vs 0,930 | **Passou** |
| 4. Custo ≤ 250 FP | 353 FP | **Falhou** |
| 5. Sintéticos puros não piores > 5% | B2 0,474 vs 0,674; B3 0,391 vs 0,471; T1 0,643 vs 0,656; B1 0,645 vs 0,648; nulos iguais | **Passou** |
| 6. Controle de erro (simulação) | psiE1 ≤ 0,025 | **Passou** |

- **Semi-sintéticos (NMSE, v0.52 vs atômica):** SQ3 **0,280** vs 0,359; SQ2 0,598 vs 0,647; SQ1 0,704 vs 0,711; nulos iguais. Latência de 5 mil a 25 mil passos (SQ1, entrada do grupo quase idêntico, é a mais lenta).
- **1.000 pontos** (relativo ao NLinear): todas **0,641** (Chronos-2 + cov. 0,701; atômica 0,757); ONS **0,472** (0,500); CAMELS 0,870 (0,838); BDG2 0,887 (Chronos-2 + cov. 0,718). Vence o Chronos-2 com covariáveis em 13/29 tarefas.
- **Conclusão:** melhor resultado da v0.52 até aqui, em todos os critérios exceto o custo. Os cortes parcimoniosos de custo fixo não chegam ao contrato. O compromisso custo × descoberta (medição #3, perfil ENXUTO) continua o problema aberto principal.

### Revisão POSTERIOR do contrato de custo (27/09/2026, decisão do usuário)

- **Registro:** a medição #4 **falhou** no contrato declarado (≤ 250 FP). Isso não muda. Por decisão do usuário, o contrato do perfil padrão passa a ser **≤ 400 FP/passo em média nas séries reais**, a valer só a partir da próxima medição, declarada antes.
- **Justificativa** (independente do resultado): o limite de 250 veio do desenho anterior (estrutura atômica, v0.51), não de uma exigência de hardware ou de aplicação. A âncora externa é o comparador linear mais simples com as mesmas entradas: o ARX denso online custa 144 + 132·d FP/passo (390 em média nestas séries) e é bem menos preciso (1,109 contra 0,641 nos 1.000 pontos).
- **Perfil de custo nos dados de desenvolvimento** (`cost_profile.py`, `COST_PROFILE_DEV.csv`; código da medição #4):
  - média entre séries 353 FP (ARX 390);
  - série a série, **acima do ARX em 14 de 29**: todas as de d = 1 (ARX 276; v0.52 261–450). O custo da v0.52 é quase fixo (~300–450), porque memória, vagas e triagem dominam; o do ARX cresce com d. A âncora vale **na média**, não série a série;
  - séries com média > 400: tanks:val 450; camels 61510000 472; BDG2 chilledwater 428; silverbox 408;
  - **picos:** p99,9 de 715 a 1.304 FP e máximo de 828 a 1.414 FP (2,1 a 3,9 vezes o ARX), com duas vagas em aquecimento simultâneo (mínimos quadrados de 7 parâmetros + estatística do pico em 31 atrasos).
- **O pico não recebe limite agora:** fixá-lo depois de vê-lo nos mesmos dados seria circular. Ele passa a ser **reportado**, e o limite de pico fica como item de desenho (por exemplo, escalonar o aquecimento para não coincidir nas duas vagas).

### Medição #5 — replicação sob o contrato revisado, declarada ANTES (27/09/2026)

- **Modelo:** código congelado da medição #4 (lebre_v052h `cc830e6039d520f9`), sem nenhuma alteração.
- **Conjunto:** `semi_synth5.py` (SR0–SR4, sementes 6501–6503; SR4 é nulo com caudas pesadas) + sintéticos puros com sementes 9501–9503. As séries reais são as mesmas de desenvolvimento, e o modelo é determinístico: a parte real **repete** a #4 e não é evidência nova (serve de verificação de integridade: previsões idênticas às da #4).
- **Critérios:** 1, 2, 3, 5 e 6 como na #4 (com grupos de equivalência). **4 revisado: média nas séries reais ≤ 400 FP/passo.** Reportados sem aprovação ou reprovação: média, p99,9 e pico por série, contra 144 + 132·d.
- **Congelamento #5:** lebre_v052h.py cc830e6039d520f9 (deve ser igual ao da #4: cc830e6039d520f9); final5.py 5d6fcf4451942c3c; semi_synth5.py af5a2fefcc8a5991.

**MEDIÇÃO #5** (única; lebre_v052h `cc830e6039d520f9`, igual ao da #4; `FINAL5_SYNTH.csv`, `FINAL5.log`):

| Critério | Resultado | Situação |
|---|---|---|
| 1. Descoberta (≥ 2 de 3 tarefas SR1–SR3) | SR1: 0/3 (x2 com atraso 9; mesmo NMSE da atômica, 0,770); SR2: x3 em 3/3 (cobertura 0,5; o grupo {x0, x1} nunca); SR3: x4 em 3/3 | **Passou** (2 de 3) |
| 2. Zero exógenas fora da verdade e dos grupos | 0 | **Passou** |
| 3. Reais | previsões **idênticas às da #4 nas 29 séries** (verificação de integridade; não é evidência nova): todas 0,680, ONS 0,515, CAMELS 0,923, BDG2 0,910 | **Passou** |
| 4. Custo médio ≤ 400 FP (revisado) | 353 | **Passou** |
| 5. Sintéticos puros | todas ≤ atômica (B2 0,487 vs 0,562) | **Passou** |
| 6. Controle de erro (simulação) | psiE1 | **Passou** |

- **Semi-sintéticos:** SR3 **0,468** vs 0,573 (atômica); SR2 0,646 vs 0,732; SR1 e nulos iguais.
- **Custo reportado** (mesmo código e dados, `COST_PROFILE_DEV.csv`): média por série 261–472; p99,9 715–1.304; máximo 1.414; acima do ARX denso em 14/29 séries (todas de d = 1).
- **Sinal de alerta — próprio passado em alvo ruído branco:** no SR4 (caudas pesadas), semente 6502, a unidade do **próprio passado do alvo** foi aceita (t = 16.930). É a 2ª ocorrência (1ª: SP0, medição #3). Somando as medições #3–#5, houve aceitação do próprio passado em **2 de 15** execuções com alvo sem estrutura (SP0, SQ0, SQ4, SR0, SR4 × 3 sementes); 13%, IC 95% ≈ [2%, 40%]. Com α = 0,05, num nulo global a chance de qualquer aceitação deveria ser ≤ 5%. A amostra é pequena e inconclusiva, mas o sinal é consistente.
  - **Hipótese de causa** (a verificar): o desafiante re-ajusta, por mínimos quadrados, o coeficiente do valor atual da entrada **junto** com o bloco. Contra uma base densa em NLMS, que num alvo ruído branco tem pesos ruidosos, esse re-ajuste melhora a previsão de fato. A nula testada ("sem melhora preditiva") é então falsa, mas a melhora vem de **estimar melhor um coeficiente existente**, não da estrutura nova. O teste está correto para a pergunta que faz; a interpretação estrutural ("o passado importa") é que fica errada.
  - **Correção a desenhar** (próxima iteração): comparar o desafiante com um **controle pareado**, a mesma base com o mesmo re-ajuste de x(t) mas sem o bloco. Assim a evidência mede só o efeito da estrutura.

### Iteração "controle pareado" — conjunto #6 declarado ANTES de implementar (27/09/2026)

- **Mudança planejada:** a evidência de uma unidade de entrada passa a comparar o desafiante (bloco + re-ajuste de x_i(t)) com um **controle pareado** (só o re-ajuste de x_i(t), mínimos quadrados de 1 parâmetro, mesmo aquecimento), e não com a base S. A diferença de perda mede só o efeito do bloco. A validade não muda: são dois previsores previsíveis. Ajuste só em conjuntos antigos, reais de desenvolvimento e um lote nulo de desenvolvimento (sementes 7001–7040).
- **Conjunto #6:** `semi_synth6.py` (SU0–SU4, sementes 6601–6603; em SU4 o próprio passado é estrutura real) + sintéticos puros com sementes 9601–9603 + **lote nulo** (30 execuções com alvo sem estrutura e entradas reais: 15 ruído gaussiano, sementes 6701–6715; 15 caudas pesadas t3, sementes 6716–6730) + reais de desenvolvimento.
- **Critérios:** 1–6 como na #5 (4 = média ≤ 400 FP). **Novo 7:** no lote nulo, número de execuções com **qualquer** mudança aceita (entrada, próprio passado ou estado latente) **≤ 3 de 30**. Se a taxa real fosse 5%, P(≥ 4 de 30) ≈ 0,06; com 13% (a estimativa atual), P(≤ 3) ≈ 0,45.

**Desenvolvimento — lote nulo** (`null_batch.py`; 20 ruído gaussiano + 20 t3, sementes 7001–7040, entradas reais):

| Configuração | Execuções com mudança aceita |
|---|---|
| código da #4/#5 (mu = 0,1) | **8 de 40** (20%), todas a unidade do próprio passado |
| + controle pareado | **12 de 40**: a hipótese do re-ajuste de x(t) estava **errada** |
| mu = 0,03 (com ou sem controle pareado) | **0 de 40** |

- **Causa real:** o **ruído de adaptação da base S**. A base aprende por NLMS com passo 0,1; o desajuste teórico (~μ/2, ~5–7% do ruído) bate com o NMSE ≈ 1,066 observado nos nulos. A oscilação dos pesos depende dos valores passados (o gradiente de t−1 usa y_{t−1} e as entradas de t−1), então o erro de S contém uma parte **previsível pelo passado do alvo**. Um bloco do próprio passado cancela parte desse ruído: há melhora preditiva real sobre S, mas ela vem da imperfeição do aprendiz, não de estrutura.
- **Leitura metodológica:** o teste está correto para a nula que testa ("sem melhora sobre S"); ela é falsa quando S é um estimador ruidoso. Para a leitura estrutural valer, a referência precisa ter **desajuste pequeno**. É uma condição de uso do método, que precisa ficar explícita na especificação.
- O **controle pareado** foi implementado como opção (`paired`), mas não resolve e fica **desligado** (parcimônia). Em teste: mu = 0,05 e 0,03 na grade de desenvolvimento (`TUNE_DEV8`).

**Grade de passo da base** (TUNE_DEV8; mesmos conjuntos antigos e reais):

| mu | Todas | ONS | CAMELS | BDG2 | FP | Nulos (40) | Semi-sintéticos: aceitações fora da verdade |
|---|---|---|---|---|---|---|---|
| 0,10 | 0,680 | 0,515 | 0,923 | 0,910 | 353 | 8 | 0 |
| 0,05 | 0,694 | 0,519 | 0,913 | 0,931 | 360 | **0** | 4, todas x0 ↔ x1 (grupo, corr. 0,98) |
| 0,03 | 0,718 | 0,515 | 0,934 | 0,966 | 376 | **0** | 4, todas x0 ↔ x1 |

- A base mais lenta tira o ruído de adaptação (nulos NMSE 1,066 → 1,034; sintéticos melhoram), mas acompanha menos rápido (BDG2 piora). **Escolhido mu = 0,05:** zero nos nulos, BDG2 dentro da tolerância da atômica (0,931 vs 0,930) e custo 360.

**CONGELAMENTO da medição #6** (antes de rodar): configuração da #4/#5 + mu = 0,05; controle pareado desligado. SHA-256 (16): lebre_v052h.py ab74ae3193264046; change_engine.py 11bb13022e408776; final6.py 344453f4cac58ac3; final4.py 5452788b17314c03; semi_synth6.py 8902b0b1828d173e; null_batch.py 1755a4de30abe30d.

**MEDIÇÃO #6** (única; lebre_v052h `ab74ae3193264046`, final6 `344453f4cac58ac3`; `FINAL6_*.csv`, `FINAL6.log`):

| Critério | Resultado | Situação |
|---|---|---|
| 1. Descoberta (≥ 2 de 3 tarefas SU1–SU3) | SU1: x3 em 3/3; SU2: 0/3 (x1 com atraso 2 e x2 com atraso 16, entradas suaves); SU3: x4 em 3/3 | **Passou** (2 de 3) |
| 2. Zero exógenas fora da verdade e dos grupos | 0 (o próprio passado aceito em SU3 e SU4 é estrutura real: ruído AR 0,9) | **Passou** |
| 3. Reais não piores (±1%), total e por grupo | Todas **0,694** vs 0,793; ONS 0,519 vs 0,579; CAMELS 0,913 vs 0,994; BDG2 0,931 vs 0,930 (+0,1%) | **Passou** |
| 4. Custo médio ≤ 400 FP | 360 (BDG2 401) | **Passou** |
| 5. Sintéticos puros | todos melhores que a atômica (T1 0,632 vs 0,754; B2 0,462 vs 0,576) | **Passou** |
| 6. Controle de erro (simulação) | psiE1, inalterado | **Passou** |
| 7. Lote nulo ≤ 3 de 30 | **0 de 30** (15 gaussianos + 15 t3) | **Passou** |

- **Semi-sintéticos (NMSE vs atômica):** SU1 **0,666** vs 0,855; SU3 0,109 vs 0,130; SU2 0,540 vs 0,552; SU4 0,194 vs 0,199; SU0 1,032 vs 1,063 (a base mais lenta também erra menos nos nulos).
- **1.000 pontos:** todas **0,653** (Chronos-2 + cov. 0,701; atômica 0,757); ONS **0,473** (0,500); CAMELS 0,878 (0,838); BDG2 0,889 (0,718). Vence em 13/29.
- **Custo da correção:** a base mais lenta perde um pouco de precisão real em relação à #4 (0,680 → 0,694; BDG2 0,910 → 0,931). É o preço de uma referência com desajuste pequeno, que torna a leitura estrutural válida.
- **Conclusão:** primeira configuração da v0.52 que passa em todos os critérios declarados, inclusive o controle empírico de mudanças falsas em alvos sem estrutura. Ressalvas:
  1. o contrato de custo foi revisado depois da #4;
  2. os dados reais são de desenvolvimento;
  3. a descoberta falha em respostas de entradas suaves com atraso médio/longo (SU2, SR1);
  4. os picos de custo (até ~1.400 FP) não têm limite.

### Iteração "entradas suaves e picos" — diagnóstico e conjunto #7 declarado ANTES de implementar (27/09/2026)

**Identificabilidade** (`diag_smooth_gain.py`, OLS offline, semente de desenvolvimento 7101): y = 0,6·x_i(t−k) + e sobre a base (valor atual de todas as entradas + y_{t−1}):
- x2 (a mais suave; autocorrelação 0,92–0,96): ganho de 2,8% (k = 2) a 8,1% (k = 25), da ordem de 300–2.600 amostras de evidência;
- x1: 4,7–10,1%; x3 e x4: 12–20%.

**Os casos que falharam (SR1, SU2) são identificáveis dentro das séries (~32 mil passos). A falha é do mecanismo.**

**Rastreio** (`diag_trace2.py`, x2 com atraso 9, semente 7102, configuração da #6):
1. **Triagem cega à entrada suave:** a estatística de x2 ficou entre 0,3 e 10 quase o tempo todo, contra o limiar 15,1, e só 4 episódios foram abertos em 32 mil passos. Com a ≈ 0,98, o pré-branqueamento AR(1) reduz a entrada à sua inovação (d.p. ~0,2) e amplifica o ruído do alvo por (1 + a²): a correlação some. O pré-branqueamento serve para **localizar** o atraso; para **detectar** a unidade (estatística de grupo), a média de faixa bruta basta.
2. **Desafiante realiza pouco do ganho:** no único episódio longo (5.003 amostras), a média de d foi +0,0017, cerca de 1/3 do ganho offline, e log_e ficou em 0,3. Os mínimos quadrados de 7 parâmetros recomeçam do zero a cada episódio, com regressores suaves e colineares.

**Picos de custo:** até ~1.400 FP, quando duas vagas estão em aquecimento ao mesmo tempo (mínimos quadrados de 7 parâmetros + estatística do pico em 31 atrasos, por vaga).

**Mudanças planejadas** (ajuste só no desenvolvimento: conjuntos antigos, réplicas com sementes 7101–7199, lote nulo 7001–7040, reais):
1. triagem de unidade com a estatística bruta de faixa além da pré-branqueada;
2. estado do desafiante (mínimos quadrados) persistente entre episódios, com esquecimento;
3. aquecimentos escalonados: no máximo um experimento em aquecimento por vez.

**Conjunto #7:** `semi_synth7.py` (SW0–SW4, sementes 6801–6803, focado em entradas suaves com atraso médio/longo) + sintéticos puros 9701–9703 + lote nulo 6901–6930 + reais de desenvolvimento.

**Critérios:**
- 1–7 como na #6 (1 sobre SW1–SW3: ≥ 2 de 3 tarefas; 4: média ≤ 400 FP; 7: ≤ 3 de 30).
- **Novo 8 (pico):** custo máximo por passo ≤ 1.000 FP em todas as séries reais de desenvolvimento (d ≤ 3). As séries reais não são novas, e o custo é determinístico dado o código: o critério 8 verifica o **mecanismo** de limitação, não é evidência independente.

**Desenvolvimento — descoberta em entradas suaves** (`dev_smooth.py`; réplicas y = 0,6·x_i(t−k) + e, 6 casos × 2 sementes 7101+; fração de descobertas da entrada verdadeira ou do seu grupo; zero falsas em todas as variantes):

| Variante | x1-12 | x1-25 | x2-5 | x2-9 | x2-16 | x4-20 | Média |
|---|---|---|---|---|---|---|---|
| #6 (base) | 1,0 | 0 | 0 | 0 | 0 | 0,5 | 0,25 |
| + triagem bruta | 0,5 | 0 | 0 | 0 | 0 | 1,0 | 0,25 |
| + desafiante persistente (esq. 0,9995) | 1,0 | 0,5 | 0 | 0 | 0 | 0,5 | 0,33 |
| + escalonamento | 1,0 | 0,5 | 0 | 0 | 0 | 0,5 | 0,33 |
| persistente sem esquecimento | 1,0 | 0,5 | 0 | 0 | 0 | 0,5 | 0,33 |
| idem + T_max 20.000 | 1,0 | 0,5 | 0 | 0,5 | 0 | 0,5 | **0,42** |

- **Rastreio x2-9** com as opções: a evidência passa a acumular entre episódios (log_e 2,8 → 5,1, contra 6,3), mas os episódios longos são encerrados em T_max. O pico escolhido no primeiro episódio (28, errado) fica preso com a persistência. Pesa pouco em entrada suave, porque as faixas cobrem o efeito, mas fica registrado.
- **Limite de informação — oráculo online** (`oracle_online.py`): desafiante que conhece o atraso verdadeiro, mínimos quadrados desde t = 0, sem esquecimento, nunca encerrado, julgado pelo mesmo psiE1:

| Caso | Cruzamento do limiar (3 sementes) |
|---|---|
| x2-9 | 18.124; 12.280; 27.342 |
| x2-16 | 9.429; 14.759; 20.301 |
| x2-5 | **nunca** em 32 mil passos |
| x1-12 | ~8.100 |
| x4-20 | ~4.000–4.300 |

  **Conclusão:** para a entrada mais suave (x2, autocorrelação ~0,99 no passo), mesmo o melhor teste online com garantia leva 9–27 mil passos ou não chega. SR1 (x2-9) e SU2 (x2-16) estão **perto do limite de informação** dentro do comprimento das séries; a v0.52 fica próxima do oráculo ali. Nos casos com mais informação (x4-20: oráculo ~4 mil), ainda há lacuna do mecanismo.

**Desenvolvimento — picos de custo** (`cost_profile.py` com configurações; séries reais de desenvolvimento):
- **Decomposição do passo de pico** (camels 17350000, configuração da #6): experimentos 420–630 (duas vagas: mínimos quadrados de 7 parâmetros + estatística do pico em 31 atrasos durante o aquecimento), **triagem ~320 num único passo** (todas as entradas a cada 4 passos), decisão ~50 (a cada 10 passos).

| Variante | Média | p99,9 máx./ARX | Pico máximo |
|---|---|---|---|
| #6 | 360 | 3,94 | 1.409 |
| + aquecimento escalonado | 364 | 3,47 | 1.306 |
| + triagem espalhada (cada parte na sua fase, mesma frequência) | 368 | 3,10 | 1.039 |
| + estatística do pico em meia janela alternada (aquecimento 250, escolha em 200) | **380** | 2,78 | **904** |
| idem + opções de entrada suave | 371 | 2,91 | **963** |

- As três mudanças de pico **não mudam a estatística**: a mesma frequência de triagem, o mesmo número de amostras por atraso na escolha do pico. Só redistribuem o custo no tempo (e o escalonamento adia aberturas).

**Verificação das candidatas** (TUNE_DEV14, DEV_SMOOTH14, NULL_DEV14):

| Candidata | Todas / ONS / CAMELS / BDG2 | Média / pico FP | Nulos | Réplicas suaves | Fora da verdade (conj. antigos) |
|---|---|---|---|---|---|
| A: correções de pico | 0,709 / 0,508 / 0,937 / 0,932 | 380 / 904 | 0/40 | 0,17 | 3, todas x0 ↔ x1 (grupo) |
| B: A + opções de entrada suave | 0,711 / 0,510 / 0,953 / 0,932 | 371 / 963 | 0/40 | 0,25 | 3, **uma fora de grupo** (x4 por x3, corr. 0,77) |
| sem escalonamento (A sem stagger) | — | 394 / 1.001 | — | — | — |

- O escalonamento é necessário para o pico ≤ 1.000. Ele custa ~2% de precisão (0,694 → 0,709) e um pouco de descoberta, porque adia aberturas.
- As opções de entrada suave dão ganho pequeno (dentro do ruído: 3 contra 2 descobertas em 12) e trazem uma aceitação falsa fora de grupo. Com o oráculo mostrando o limite de informação em x2, **não se justificam**: ficam implementadas, desligadas.
- **Escolhida A.** Espera-se que a #7, focada em entradas suaves, **falhe no critério 1**.

**CONGELAMENTO da medição #7** (antes de rodar): final6.PADRAO + stagger + screen_spread + peak_split (peak_until 200, chal_warm 250). SHA-256 (16): lebre_v052h.py e6bb3a89276c6c3e; change_engine.py 11bb13022e408776; final7.py ccce251c8b46e0ff; final4.py 5452788b17314c03; semi_synth7.py 0f325a8537516210; null_batch.py 1755a4de30abe30d.

**MEDIÇÃO #7** (única; lebre_v052h `e6bb3a89276c6c3e`, final7 `ccce251c8b46e0ff`; `FINAL7_*.csv`, `FINAL7.log`):

| Critério | Resultado | Situação |
|---|---|---|
| 1. Descoberta em SW1–SW3 (entradas suaves, atraso médio/longo) | SW1 (x2-12): 0/3; SW2 (x1-20): 0/3; SW3: x4 em 1/3 (t = 24.200), x2 nunca | **Falhou** (esperado) |
| 2. Zero exógenas fora da verdade e dos grupos | 0 | **Passou** |
| 3. Reais (±1%) | Todas **0,709** vs 0,793; ONS 0,508; CAMELS 0,937; BDG2 0,932 vs 0,930 (+0,2%) | **Passou** |
| 4. Custo médio ≤ 400 FP | 380 | **Passou** |
| 5. Sintéticos ≤ atômica + 5% | B3 0,424 vs 0,407 (+4,2%); demais melhores | **Passou** |
| 6. Controle de erro (simulação) | psiE1 | **Passou** |
| 7. Lote nulo ≤ 3 de 30 | **0 de 30** | **Passou** |
| 8. Pico ≤ 1.000 FP | máximo **904**; p99,9 ≤ 889 (antes: 1.409) | **Passou** |

- **Descoberta onde há informação:** SW4 (x3, atraso 10, entrada menos suave) em 3/3 sementes.
- **Previsão nas tarefas suaves:** mesmo sem descobrir a estrutura, a v0.52 prevê melhor que a atômica (SW1 0,761 vs 0,781; SW3 0,689 vs 0,710), porque a base já carrega o valor atual das entradas.
- **1.000 pontos:** todas **0,669** (Chronos-2 + cov. 0,701); ONS **0,460** (0,500); CAMELS 0,907 (0,838); BDG2 0,896 (0,718). Vence em **14/29**.
- **Conclusão:**
  1. **Pico de custo resolvido** sem alterar a estatística (escalonamento, triagem espalhada, estatística do pico em meia janela). Custa ~2% de precisão.
  2. **Descoberta em entradas muito suaves com atraso médio/longo continua falhando**, e o oráculo online de desenvolvimento mostra que isso está, em boa parte, **perto do limite de informação** de um teste online com garantia no comprimento destas séries: para x2, mesmo o oráculo leva 9–27 mil passos ou não chega. Não é um defeito isolado do mecanismo; é um limite do problema, que precisa ser declarado como escopo.

### Ablações e comparadores fortes — plano e regras de decisão ANTES de rodar (27/09/2026)

**Objetivo:** decidir o que a arquitetura pode afirmar. Só dados de desenvolvimento (séries reais; mesma máscara e mesmos 1.000 pontos), configuração congelada da medição #7 ("COMPLETA").

**Ablações** (mesmo código, uma peça por vez):
- **TUDO_LIGADO:** todas as unidades ativas desde o início (blocos de faixa de todas as entradas + estado latente), sem testes, mesmo aprendiz (NLMS);
- **TUDO_LIGADO_RLS:** idem, com base e blocos aprendidos juntos por mínimos quadrados recursivos (esquecimento 0,9995). É o teto de um modelo denso com a mesma representação;
- **SEM_DIVISOES:** sem refinamento hierárquico;
- **SÓ_MEMÓRIA:** só o especialista de memória (com o ciclo semanal nos prédios);
- **ATÔMICA:** v0.52 atômica (já medida).

**Comparadores fortes com as mesmas entradas:**
- **ARX_RLS_PLS:** seis ARX por mínimos quadrados recursivos (atrasos do alvo p ∈ {2, 8} × atrasos das entradas q ∈ {2, 8, 24}), com escolha online pelo menor erro preditivo acumulado descontado (mínimos quadrados preditivos, Rissanen 1986; Wei 1992);
- **LASSO_ONLINE:** regressão esparsa online (gradiente proximal com limiar suave) sobre todos os atrasos 0–32 das entradas e 1–32 do alvo, passo e penalidade calibrados nos primeiros 15%;
- já existentes: SARIMAX-X, ARX denso NLMS, NLinear, Chronos-2 (com e sem covariáveis).

**Regras de decisão** (média geométrica relativa ao NLinear; "empate" = diferença ≤ 1%):
1. Se TUDO_LIGADO ou TUDO_LIGADO_RLS for **melhor ou empatar** com a COMPLETA, a afirmação de precisão cai: o mecanismo de testes contribui com **estrutura certificada, explicação e custo**, e esses passam a ser os argumentos centrais (o custo de cada variante é reportado).
2. Se algum comparador forte (ARX_RLS_PLS, LASSO_ONLINE) for **melhor** que a COMPLETA no total, a v0.52 **não é competitiva na sua classe** em precisão, e isso é declarado.
3. Se SEM_DIVISOES empatar, as divisões só se justificam por explicação ou pelos sintéticos puros (ver medições anteriores).
4. SÓ_MEMÓRIA mede quanto da precisão vem das entradas.

**RESULTADO — ablações e comparadores fortes** (`abl_analysis.py`, `ABL_FULLMASK.csv`, `ABL_1000PTS.csv`; máscara verificada, n idêntico nos 1.000 pontos):

| Modelo | ONS | CAMELS | BDG2 | **Todas** | FP/passo |
|---|---|---|---|---|---|
| COMPLETA (config. #7) | 0,508 | 0,937 | 0,932 | **0,709** | 380 |
| TUDO_LIGADO (sem testes, NLMS) | 0,505 | 1,033 | 0,982 | 0,731 | 334 |
| TUDO_LIGADO_RLS (sem testes, RLS) | 0,595 | 0,889 | 0,982 | 0,732 | 1.855 |
| SEM_DIVISOES | 0,507 | 0,939 | 0,932 | **0,699** | 357 |
| SÓ_MEMÓRIA | 1,032 | 1,551 | 0,991 | 1,164 | 39 |
| ATÔMICA | 0,579 | 0,994 | 0,930 | 0,793 | 165 |
| **ARX_RLS_PLS** | **0,503** | **0,668** | 2,732 | **0,654** | **33.578** |
| LASSO_ONLINE | 0,643 | 1,211 | 1,964 | 1,322 | 579 |
| ARX_NLMS | 0,589 | 1,219 | 1,929 | 1,155 | 390 |
| SARIMAX-X | 0,873 | 0,808 | 0,965 | 0,992 | n/d |

(máscara completa; nos 1.000 pontos: COMPLETA 0,669, ARX_RLS_PLS **0,630**, Chronos-2 + cov. 0,701, TUDO_LIGADO 0,688, SEM_DIVISOES 0,658.)

**Aplicação das regras declaradas:**
1. **Tudo ligado:** a COMPLETA é melhor no total (0,709 contra 0,731 e 0,732; vence 17/29 e 14/29 séries). O mecanismo de testes **contribui para a precisão** no total. Por grupo: empata no ONS com o NLMS; perde no CAMELS para o RLS denso.
2. **Comparador forte: a regra é acionada.** O ARX_RLS_PLS é **melhor no total** (0,654 contra 0,709; 1.000 pontos: 0,630 contra 0,669). **A v0.52 não é a mais precisa da sua classe.** Nuances:
   - ele custa **~88× mais** (33,6 mil FP);
   - é **catastrófico nos prédios** (2,73, quase 3× pior que o NLinear), enquanto a v0.52 nunca passa de 0,94 em nenhum grupo;
   - a vantagem dele vem do **CAMELS** (0,668 contra 0,937), justamente onde o RLS também ajuda na ablação: o aprendiz NLMS da v0.52 é o gargalo nas bacias.
   - **Achado colateral:** o ARX clássico bem ajustado supera o Chronos-2 com covariáveis nestes dados (0,630 contra 0,701). **"Vencer o Chronos-2" não é um argumento forte neste domínio.**
3. **Divisões:** SEM_DIVISOES é **melhor** nos reais (0,699 contra 0,709) e mais barata (357). As divisões só se justificam pelos sintéticos com atrasos exatos e pela explicação.
4. **Memória:** sozinha, 1,164. A precisão vem essencialmente das **entradas**.

**Afirmação que sobrevive:** a v0.52 **não domina em precisão**. O que ela oferece:
- (a) um ponto da fronteira precisão × custo que nenhum comparador domina (0,709 a 380 FP; o único mais preciso custa 88× mais e falha num grupo inteiro);
- (b) **robustez entre domínios**: pior grupo 0,937, contra 2,73 do ARX RLS e 1,96–1,93 dos lineares online;
- (c) estrutura **certificada e explicada**, com controle empírico de mudanças falsas.

A precisão pura não é argumento central.

### PRÉ-REGISTRO da avaliação em dados reservados (27/09/2026)

- `LEBRE-V0.52-HELDOUT-01/PREREG_V052_HELDOUT.md`, SHA-256 (16) **9d1f304bcd994760**, registrado antes de qualquer acesso aos dados reservados.
- 125 séries: 45 ONS de outros 10 rios, 50 CAMELS-BR e 30 BDG2. Modelo congelado (configuração #7), ablações e comparadores, com os protocolos do desenvolvimento. Execução única.

### RESULTADO da avaliação em dados reservados — parte principal (27/09/2026)

**Execução:** 125/125 séries, sem erros de infraestrutura (`LEBRE-V0.52-HELDOUT-01/RUN.log`). Análise pré-registrada: `HELDOUT_TABLE_FULLMASK.csv`, `HELDOUT_FULLMASK.csv`.

**Pré-registrado (máscara completa, média geométrica relativa ao NLinear):**

| Modelo | ONS | CAMELS | BDG2 | Todas [IC 95%] | Séries > 1,5 | FP |
|---|---|---|---|---|---|---|
| **v0.52 COMPLETA** | 1,180 | **55,1** | 0,940 | **5,20** [0,81; 137] | 4,8% | 365 |
| TUDO_LIGADO | 7,30 | 67,1 | 0,947 | 10,9 | 4,8% | 347 |
| ATÔMICA | 8,42 | 73,0 | 0,919 | 11,7 | 5,6% | 165 |
| v0.51 | 0,706 | 1,864 | 0,959 | 1,120 [1,00; 1,27] | 23,2% | 111 |
| ARX_RLS_PLS | **0,574** | **0,610** | 3,856 | 0,929 [0,75; 1,20] | 10,4% | 38.944 |
| **SARIMAX-X** | 0,866 | 0,766 | **0,872** | **0,826** [0,78; 0,87] | **0,0%** | — |
| airline | 0,973 | 0,897 | 0,881 | 0,919 | 0,8% | — |
| LASSO_ONLINE | 1,077 | 0,938 | 5,091 | 1,479 | 26,4% | 622 |
| SÓ_MEMÓRIA | 537 | 1,7·10⁷ | 1,044 | 7.555 | 33,6% | 41 |

- **Falha grave revelada pela reserva:** em 6 de 125 séries a v0.52 **explode** (até 10⁷⁹), o que domina a média geométrica. **Causa** (diagnóstico exploratório, posterior): quando o alvo falta por vários passos seguidos, a memória da v0.52 preenche o próprio histórico com as próprias previsões (malha aberta). Com os pesos aprendidos (por exemplo, reversão à média com sinal negativo), essa recursão é instável e a previsão cresce exponencialmente durante a lacuna (camels 84551000: −1,5·10⁴² após uma lacuna). A v0.51 pulava os passos sem alvo e não tem o defeito. No desenvolvimento as lacunas eram curtas, e ele não apareceu.
- **Custo:** média 365 FP; p99,9 até 944; máximo **974** (≤ 1.000, dentro do contrato, inclusive com até 5 entradas).
- **Estrutura:** 79 de 125 séries aceitaram ≥ 1 entrada; primeira aceitação mediana em t = 3.515; cobertura do intervalo 0,904 (nominal 0,90).

**Vistas exploratórias (posteriores, NÃO pré-registradas), para localizar o "limiar" fora do defeito:**

| Modelo | Todas, erro limitado a 10 | Todas, sem as 6 catastróficas | Pior grupo (sem as 6) |
|---|---|---|---|
| v0.52 COMPLETA | 0,802 | **0,706** | **0,810** |
| TUDO_LIGADO | 0,810 | 0,713 | 0,817 |
| ARX_RLS_PLS | 0,784 | 0,950 | 4,051 (BDG2) |
| SARIMAX-X | 0,826 | 0,823 | 0,866 |
| v0.51 | 1,090 | 1,132 | 1,911 |

- Sem as 6 séries, COMPLETA / ARX_RLS_PLS = 0,743 (mas o ARX vence 74 de 119 séries; ele é muito melhor no ONS e no CAMELS e catastrófico nos prédios); COMPLETA / SARIMAX-X = 0,858 (vence 74/119); **COMPLETA / TUDO_LIGADO = 0,99 (vence 55/119)**.
- Medianas: COMPLETA 0,804; ARX_RLS_PLS 0,669; SARIMAX-X 0,852; v0.51 1,027.

### Avaliação em dados reservados — CONCLUÍDA (27/09/2026)

Relatório completo: `LEBRE-V0.52-HELDOUT-01/HELDOUT_REPORT.md`. Chronos 375/375, sem erro (relançado uma vez por falha de infraestrutura antes de produzir previsões). Respostas pré-registradas:
- **Q1** mecanismo de testes contra tudo ligado: sem evidência de ganho (0,479, IC [0,10; 1,20]; sem as catastróficas, 0,99);
- **Q2** ARX por mínimos quadrados: melhor no ONS e no CAMELS, muito pior no BDG2; vence 80/125; custo ~100×;
- **Q3** Chronos-2 com covariáveis **melhor**: 0,675 contra 0,911 nos 1.000 pontos; sem as catastróficas, 0,674 contra 0,712. **A vantagem do desenvolvimento se inverte;**
- **Q4** robustez **não** mantida: 6 explosões pelo defeito das lacunas; o SARIMAX-X é o mais robusto;
- **Q5** divisões: sem efeito (0,996);
- **Q6** custo mantido (365 de média; máximo 974).

**Conclusão:** como congelada, a v0.52 tem um **defeito desqualificante** (memória em malha aberta durante lacunas do alvo). Fora dele, 0,706, igual ao desenvolvimento, atrás do Chronos-2 com covariáveis e à frente do SARIMAX-X. A contribuição defensável é o mecanismo com garantia, não a precisão.

### Correção das lacunas do alvo (27/09/2026, depois da avaliação em dados reservados)

- **Princípio do projeto registrado** (usuário): *"a LEBRE não tem que ser o melhor, tem que entregar bem em um orçamento mega reduzido"*. A avaliação passa a ser **qualidade dentro da classe de orçamento** (centenas de FP/passo), com os modelos grandes como teto de referência. Sob esse critério, **nunca falhar catastroficamente** é parte de "entregar bem".
- **Correção** (opções em `lebre_v052h.py`, padrão desligado; o código congelado da avaliação está preservado em `lebre_v052h_heldout.py`):
  1. **`gap_hold`:** durante a lacuna do alvo, o histórico da memória recebe o **último valor observado** (retenção), nunca a própria previsão. Sem malha fechada pelos pesos aprendidos, não há recursão que possa divergir. O alinhamento dos ciclos é mantido;
  2. **`out_contract`:** a previsão é limitada ao envelope dos alvos observados (máximo e mínimo correntes que relaxam devagar para a média lenta, taxa 10⁻³), alargado em 0,5× a sua largura. Uma previsão não finita cai no último valor observado. Custo ~15 FP/passo.
- **Verificação:** com as opções desligadas, o código reproduz bit a bit a versão avaliada. Num sintético sem lacunas, a correção ligada também é idêntica (0 cortes).
- **Teste de estresse** (`stress_gaps.py`, desenvolvimento): 4 lacunas artificiais no alvo (24, 100, 400 e 1.500 passos) nas 29 séries de desenvolvimento, com as entradas mantidas; configurações CONGELADA, RETENÇÃO e RETENÇÃO + CONTRATO; também sem lacunas injetadas, para medir o custo da correção.
- **Resultado do estresse** (`STRESS_GAPS.csv`; explosão = desvio > 10× a amplitude observada, erro > 1,5× o da mesma configuração sem lacunas injetadas, ou previsão não finita):

| Configuração | Com lacunas: explosões | Desvio máx. / amplitude | Erro, média geom. (com / sem lacunas injetadas) | Cortes do contrato | FP |
|---|---|---|---|---|---|
| CONGELADA | **10** (5 CAMELS de 10¹²–10⁷⁶, Furnas, 2 BDG2, 2 Tanks) | **1,1·10³⁹** | 5.727 / 0,0588 | 0 | 380 |
| RETENÇÃO | 2 (só Tanks, ver abaixo) | 1,72 | 0,0726 / 0,0581 | 0 | 380 |
| RETENÇÃO + CONTRATO | 2 (só Tanks) | 1,45 | 0,0721 / **0,0578** | 31 / 33 | 395 |

  - O estresse **reproduz no desenvolvimento o defeito visto na reserva** (bacias do CAMELS explodem na versão congelada) e a retenção **o elimina**.
  - As duas marcações restantes (Cascaded Tanks) **não são explosões:** a série tem 1.024 passos, as lacunas de 400 e 1.500 cobrem quase toda a região de teste, e o erro fica em 0,02 com desvio máximo de 0,39 da amplitude. O critério "> 1,5× sem lacunas" é estrito demais para séries curtas.
  - **Sem lacunas injetadas, a correção melhora** a precisão (média geométrica 0,9825; até −17% em camels 64477600 e −11% em BDG2 Luvenia; pior caso +0,17%). As lacunas **naturais** do desenvolvimento já causavam pequenas instabilidades silenciosas.
  - O contrato de saída age raramente (33 passos no total) e custa ~15 FP (média 395, dentro de 400). Fica como rede de segurança barata.
- **Próximo:** verificar que os sintéticos e os nulos não mudam (não têm lacunas: idênticos por construção; conferido em B3). A confirmação em dados reais exige **nova avaliação pré-registrada em séries nunca vistas**; a reserva anterior foi consumida.

### PRÉ-REGISTRO — reserva 2 (27/09/2026)

- `LEBRE-V0.52-HELDOUT-02/PREREG_V052_RESERVA2.md`, SHA-256 (16) **5a60c67b512a60a1**, antes de qualquer acesso.
- 20 CAMELS-BR + 20 BDG2: as próximas posições das mesmas permutações. Candidata: v0.52 corrigida (retenção + contrato de saída). Classe de orçamento + referências.

### RESULTADO — reserva 2 (27/09/2026)

Relatório: `LEBRE-V0.52-HELDOUT-02/RESERVA2_REPORT.md`. 40/40 séries, sem erros.
- **Q1** zero catastróficas com a correção (congelada: 2).
- **Q2** corrigida / congelada 0,693 [0,425; 0,989].
- **Q3** 1º lugar na classe de orçamento (0,767 [0,657; 0,858]; DLinear 0,957; NLinear 1,0).
- **Q4** Chronos-2 com covariáveis 16% melhor (1,161; vence 28/40); empate com SARIMAX-X (0,999); melhor que ARX por mínimos quadrados (0,540).
- **Q5** pior grupo 0,836 e 0% das séries > 1,5.
- **Q6** média de 407 FP e máximo de 1.015: **~2% acima dos dois limites**, como já previsto para os prédios.

### PRA-04 e congelamento (27/09/2026)

- **PRA-04** (`experiments/PRA-04-V052/`): 25 consultas.
  - **O mecanismo central já existe** em árvores online: Amoukou, Mishra & Veloso, arXiv 2605.31239, maio/2026 — e-process de diferença de perda prequencial, controle global no fluxo. A PRA-03 não o havia encontrado, e a conclusão dela foi **corrigida**.
  - A v0.52 contribui com extensão/integração (séries com entradas, unidades por entrada, hierarquia, remoção e troca, FDR, orçamento), com o achado da condição de uso (desajuste da referência; vizinhos: Giacomini & White 2006, Han & Qu 2026) e com a evidência empírica sob orçamento.
  - O limite de informação e as salvaguardas são conhecidos.
- **Verificação para o congelamento:** o código atual reproduz **bit a bit** as previsões da v0.52 corrigida salvas na reserva 2 (3 séries conferidas, incluindo uma que explodia sem a correção).
- **Congelamento:** `docs/architecture/LEBRE_v0.52_FREEZE_RECORD.md` + MANIFEST + SHA256SUMS. Status: versão de pesquisa congelada, **não promovida**. Configuração canônica: `heldout2_run.V052["V052_CORRIGIDA"]`.
