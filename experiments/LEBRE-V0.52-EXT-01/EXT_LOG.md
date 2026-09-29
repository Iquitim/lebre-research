# LEBRE v0.52 — Extensão pós-congelamento (EXT-01): diário

**Início:** 27/09/2026. **Regra:** a v0.52 está congelada (650 arquivos com hash). Nada congelado é editado; os módulos congelados são só **importados**. Todo trabalho novo fica nesta pasta.

## Plano (fixado antes de qualquer resultado)

1. **Formalizar o achado do desajuste:** proposição com demonstração (condição suficiente para que a melhora preditiva sobre a referência implique estrutura) e verificação empírica **no desenvolvimento** (novas sementes nulas 7201–7260), medindo a quantidade prevista pela teoria (fração projetada do erro de estimação da referência) para μ ∈ {0,1; 0,05; 0,03}.
2. **Comparadores de orçamento e tetos pequenos:** FITS (~10k parâmetros) e SparseTSF (< 1k), ajustados nos primeiros 15% como o SARIMAX-X; TTM (Tiny Time Mixers, ~1M parâmetros) zero-shot e com ajuste fino nos primeiros 15% com as entradas como canais exógenos. **Desenvolvidos e testados só nas séries de desenvolvimento.** Custo por previsão calculado analiticamente (FLOPs).
3. **Custo em microcontrolador por simulador:**
   - porte da configuração canônica para **C em float32**;
   - **teste de equivalência** contra o Python congelado **só em séries de desenvolvimento**;
   - compilação para **Cortex-M4F** (arm-none-eabi-gcc) e execução no simulador **Renode** (STM32F4), com contagem de instruções e ciclos por passo (média, p99,9, máximo), RAM e flash pelo mapa do compilador;
   - ciclos estimados pelos tempos publicados do Cortex-M4 quando o simulador não os modela.
4. **Reserva 3 (dados nunca vistos):** próximas posições das mesmas permutações (CAMELS-BR 80+, BDG2 55+). **Pré-registro antes do acesso**, com os comparadores do passo 2 e a versão em C; execução única.

## Etapa 1 — Formalização do desajuste (concluída)

- Nota formal: `MISADJUSTMENT_NOTE.md`.
  - **Proposição 1:** identidade E[Δ | passado] = (2gη − g²)/B² ≤ η²/B².
  - **Corolário 1:** garantia exata, se o desajuste normalizado for ≤ ε para qualquer desafiante (NLMS: M ≲ 4ε, μ ≲ 0,016).
  - **Proposição 2:** desafiantes de coeficiente fixo; a quantidade relevante é a projeção Dᵤ.
  - **Proposição 3:** critério prático no horizonte, D < σ_d·√(2 log(1/α)/T).
- Verificação (`misadj_verify.py`, `MISADJ_VERIFY*.csv`; 120 execuções nulas de desenvolvimento, sementes 7201–7240):
  - μ = 0,1: oráculo mediano 18,2 contra limiar 5,63 → 10/40 aceitações;
  - μ = 0,05: oráculo máx. 5,2 → 0/40;
  - μ = 0,03: ≈ 0 → 0/40;
  - as aceitações ocorrem sempre na unidade de maior projeção (o próprio passado do alvo).
- **Leitura honesta:** a v0.52 (μ = 0,05) está no regime **prático** (violação pequena demais para ser detectada no horizonte), não no da garantia exata.
- **Incidente:** durante a criação de `heldout2_cfg.py`, uma cópia foi criada e apagada por engano na pasta congelada PROTO-01; nenhum arquivo com hash foi alterado (reconferir no fim da EXT-01).

## Incidente de ambiente (27/09/2026)

- A instalação do pacote do TTM (granite-tsfm 0.3.9) **atualizou o pandas para 3.0.6**. Nessa versão, arrays vindos de `to_numpy()` são somente leitura, e o carregador de dados congelado falhou na primeira rodada dos comparadores. Nenhum resultado foi produzido com essa versão.
- **Correção:** o pandas foi restaurado para **2.2.3** (versão registrada no relatório de reprodutibilidade do projeto). A reprodução **bit a bit** das previsões congeladas da reserva 2 foi reconferida (2 séries) e o TTM continua funcionando.
- **Regra adicionada:** qualquer nova instalação deve fixar `pandas==2.2.3`.

## Etapa 3 — Porte para C e custo em microcontrolador simulado (desenvolvimento)

**Porte:** `lebre_c/lebre052.{h,c}`, C99, só o caminho da configuração canônica, com arrays de capacidade fixa (sinalizador de estouro). As constantes da mistura do e-process foram pré-calculadas por hipótese (mesmos valores; evita potência e logaritmo em precisão dupla a cada revisão).

**Equivalência** (`equiv_test.py`, 29 séries de desenvolvimento, `EQUIV_TEST.csv`):

| Versão | Sequências de mudanças aceitas idênticas ao Python | Diferença relativa do NMSE |
|---|---|---|
| C, precisão dupla (valida a lógica do porte) | **29/29** | mediana 2·10⁻¹⁶ |
| C, precisão simples (versão do microcontrolador) | **28/29** | mediana 8·10⁻⁷; máx. 8·10⁻³ (Silverbox: uma divisão aceita 10 passos depois) |

Nenhum estouro de capacidade.

**Microcontrolador simulado:**
- Renode 1.17, STM32F4 (Cortex-M4F) + modelo DWT; `PerformanceInMips = 168` e DWT a 168 MHz, de modo que o contador conta **instruções executadas**;
- firmware com arm-none-eabi-gcc 15.2 (`-O2 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -ffp-contract=off`), float32;
- padronizador causal das entradas também no dispositivo, com custo medido à parte;
- **ciclos** estimados de um rastreio de execução (janela de ~300 passos no meio da série) com os tempos do manual do Cortex-M4 (`cycles_estimate.py`): **CPI 1,62** (ONS) e **1,57** (BDG2). Suposição: sem esperas efetivas de flash (acelerador ART).

| Série (desenvolvimento) | Entradas | Instruções/passo: média | mediana | p99 | p99,9 | pico | Ciclos/passo (média ×1,6) | Tempo a 168 MHz |
|---|---|---|---|---|---|---|---|---|
| ONS Volta Grande | 1 | 3.701 | 3.363 | 11.635 | 12.327 | 42.021 | ~5.900 | ~35 µs |
| CAMELS 71350001 | 3 | 4.560 | 4.599 | 12.979 | 14.387 | 48.447 | ~7.300 | ~43 µs |
| BDG2 Bull_education_Hayley | 2 | 5.964 | 5.607 | 13.695 | 16.843 | 45.654 | ~9.500 | ~57 µs |

- **Conferência no dispositivo:** mudanças aceitas (4, 3, 2) e NMSE (0,282602; 0,022912; 0,030527) **iguais** ao Python e ao C float32 do PC.
- **Picos:** todos os passos acima de 20 mil instruções são passos de decisão (a cada 10 passos), em 10–14 ocorrências por série (criação de hipótese, aceitação com recálculo de somas).
- **Padronizador das entradas:** 7–110 instruções por passo.
- **Memória:**
  - estado do modelo 74.988 B de RAM (dominado pela tabela de hipóteses dimensionada para 160; cabe nos 128 KB de um STM32F407);
  - código do modelo 14,6 KB de flash + ~10 KB de libm/libc.
- **Relação com a contagem analítica:** ~400 FP/passo analíticos correspondem a ~3,7–6,0 mil instruções (~9–15 instruções por FLOP), por causa de acessos à memória, laços, índices e divisões (5–7% dos ciclos em VDIV).
- **Energia (estimativa, não medida):** com ~40 mA a 168 MHz e 3,3 V (ordem de grandeza típica de folha de dados de um Cortex-M4 da classe STM32F4), ~5–7 µJ por passo.

## Pré-registro da reserva 3 (27/09/2026)

- `LEBRE-V0.52-HELDOUT-03/PREREG_V052_RESERVA3.md`, SHA-256 (16) **48edcc3590498e78**, antes de qualquer acesso aos valores das séries.
- 30 CAMELS-BR + 30 BDG2; V052 congelada (Python e C float32); FITS, SparseTSF, TTM (zero-shot e ajustado com exógenas), Chronos-2 com covariáveis; custo no Cortex-M4F simulado em 4 séries.

- **Reconferência dos congelamentos** (27/09/2026, depois do incidente da cópia na pasta congelada e da troca de versão do pandas): v0.52 **650/650** e v0.51 **52/52** arquivos conferem; nenhum arquivo estranho na pasta congelada.

- **Incidente de infraestrutura (reserva 3):** `heldout3_mcu.sh` passou ao Python um caminho no formato do shell e falhou antes de rodar qualquer firmware. Corrigido só o caminho (`cygpath -w`); a etapa do microcontrolador foi repetida, como o pré-registro permite. O hash de `heldout3_mcu.sh` passa a diferir do pré-registrado por essa linha.
- Segunda falha de infraestrutura na mesma etapa: o `build_run.sh` consumia a entrada padrão e só a 1ª série rodou; corrigido com `< /dev/null` e a etapa foi repetida.
- Terceira falha de infraestrutura: no laço do script, as duas séries do BDG2 não geraram relatório (provável instância anterior do Renode ainda ativa). As duas foram rodadas **manualmente**, com o mesmo `build_run.sh ... final`, e os relatórios foram gravados em `mcu/r3_3.txt` e `mcu/r3_4.txt` no mesmo formato.

## Etapa 4 — Reserva 3 (concluída)

Relatório: `LEBRE-V0.52-HELDOUT-03/RESERVA3_REPORT.md`. 60 séries nunca vistas (30 CAMELS-BR + 30 BDG2).
- **Q1:** 0 catastróficas.
- **Q2:** 1º na classe de orçamento (0,812 [0,752; 0,866]; NLinear 1,000; DLinear 1,009; FITS 1,244; SparseTSF 2,933).
- **Q3:**
  - melhor que o TTM sem treino (0,747) e ajustado (0,771);
  - empate com o SARIMAX-X (1,002);
  - melhor que o ARX por mínimos quadrados no total (0,582);
  - **Chronos-2 com covariáveis 25% melhor** (1,250; vence 51/60).
- **Q4:** pior grupo 0,858; 0% > 1,5.
- **Q5:** porte em C float32 com sequências idênticas em 54/60 (90%, no limite do critério); mediana 1,1·10⁻⁶.
- **Q6:**
  - FP 415 médio e 1.020 máximo (~4% e ~2% acima do contrato);
  - microcontrolador simulado: 3,2–5,8 mil instruções/passo (~31–55 µs a 168 MHz), 75 KB de RAM, decisões e NMSE iguais aos do Python nas 4 séries.
