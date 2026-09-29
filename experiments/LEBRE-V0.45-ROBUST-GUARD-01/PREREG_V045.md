# Pré-registro — LEBRE v0.4.5 (guarda de contrato de entrada, C5′)

**Escrito e com hash registrado antes de qualquer execução abaixo.** Objeto: `lebre_v045.py`
(SHA-256 `97af0482f44e28bd00116c084aed2f37671e8c6506b8e4844aed17fe6ad1feec`), congelado.
LEBRE v0.1 continua canônica; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## 1. Motivação e diagnóstico

- **BENCH-04** (pré-registrado): a v0.4 (`lebre_v042.py`) ficou 1,18× pior que a v0.3.2.
- **Pós-hoc no BENCH-04:** a ablação apontou o recorte C5 (±8) como causa (sem ele, 0,99×). Com 10 pontos de partida, a regressão foi de 1,21×, e a v0.4 era muito instável.
- **DEV** (`dev_guard.py`, só dados já usados: BENCH-02, séries 1 do BENCH-03, external_v03). O mecanismo foi confirmado na AusElectricity (0,115 contra 0,014):
  - o recorte age só no aquecimento do escalonador causal do ambiente (~150–400 passos, com |z| até ~10⁴);
  - **sem recorte**, essas entradas inflam p_in e o gate de excitação mantém o modelo em silêncio;
  - **com recorte**, o modelo se julga excitado e promove estrutura espúria enquanto o viés ainda está longe do nível;
  - recortar só depois de 200 passos dá o mesmo resultado que nunca recortar.
- **Correção C5′:** a violação do contrato de entrada do P6 (|x| > 8) não é evidência. Enquanto um valor recortado puder ser lido por
  alguma defasagem (L passos), o passo é tratado como não excitado: sem atualização de σ², sem evidência, sem testes.
  Os pesos também não são atualizados, porque uma entrada recortada não é um regressor válido (rejeição forte de pontos de alavancagem, no espírito dos estimadores GM de Mallows).
  - A previsão continua usando a entrada recortada.
  - A decisão de pular depende só de x_t, conhecido antes de y_t (é previsível); pular preserva as propriedades de supermartingale das estatísticas de evidência (optional skipping; aprendizagem data-selective).
  - Quando nada é recortado, a v0.4.5 é idêntica à v0.4.2.
- **Resultado no DEV** (10 offsets, razão geométrica pareada contra a v0.3.2):
  | Variante | Razão contra v0.3.2 | Pior tarefa |
  |---|---|---|
  | v0.4.2 | 0,82 | 9,4× |
  | v0.4.2 sem recorte | 0,85 | 1,28× (X3 sem proteção: 1,38 contra 0,27) |
  | **v0.4.5** | **0,75** | 2,05× (AusElectricity; limite conhecido, declarado) |
  O X3 fica protegido (0,262). Alternativas testadas e descartadas: normalização do passo pela energia bruta (não corrige);
  quarentena só da evidência (pior caso 2,5×); pular o aprendizado só no passo recortado (instável).

## 2. Partes e critérios

**Parte 1 — confirmação interna** (I1–I14; N = 30; sementes **2401..2430**, verificadas livres; braços V02_A0, V032, V042, V045 e CTRL_ARX).
- G1–G6 idênticos ao pré-registro da v0.4, com V045 como objeto.
- Salvaguardas vinculantes contra a v0.3.2: latência I11–I14 ≤ +50; ΔNMSE por tarefa ≤ +0,010; reativação I7 ≤ +25; atraso de detecção ≤ 1,25×.
- **Nova, vinculante:** não degradar contra a v0.4.2, com NMSE médio V045 − V042 ≤ +0,005 (limite superior de 95%).

**Parte 2 — propriedades:** T1–T8 (`verify_properties.py`, LEBRE_MODEL=v045) e T9–T10 (`verify_v045_observability.py`).
- **Vinculantes:** T3 sem promoções falsas acima de α; T9 com fidelidade exata (diferença ≤ 1e−9); T10 com cobertura média ∈ [0,88; 0,92].

**Parte 3 — BENCH-04 refeito (semi-held-out:** esses dados foram usados no diagnóstico pós-hoc).
- Mesmo harness, tarefas, sementes 7611..7613 e comparadores (tirados de `BENCH04_RESULTS.csv` e `BENCH04_CHRONOS_RESULTS.csv`).
- Reportamos K-a a K-e (com K-d contra a v0.3.2), o rank e a comparação com a v0.4.2. Sem limiar próprio; entra na regra de promoção (§3).

**Parte 4 — HELD-OUT brasileiro** (nunca usado): ONS carga Sul e Nordeste (univariadas), eólica Sul e solar SE/CO (multivariadas, balanço 2023–2024).
Braços V032, V042, V045 e persistência, com 10 pontos de partida (0..450). Também reportado nas tarefas do BENCH-04.
- **H1 (vinculante):** razão geométrica pareada V045/V042 ≤ 1,00 no held-out.
- **H2 (vinculante):** razão geométrica pareada V045/V032 ≤ 1,10 no held-out.
- **H3 (reportada):** instabilidade (mediana entre tarefas de p90/p10 entre offsets) V045 ≤ V042.

**Parte 5 — salvaguarda X3** (Metro, outliers de entrada), com 10 offsets. **Vinculante:** mediana V045 ≤ 1,10 × mediana V042.

## 3. Regra de promoção

A LEBRE é promovida a **v0.4.5 (versão de pesquisa)**, substituindo a v0.4.2 como referência, se passar em:
Parte 1 (G1–G6 e todas as salvaguardas), Parte 2 (critérios vinculantes), H1, H2 e Parte 5; e se o rótulo do BENCH-04 refeito
não for pior que o da v0.4.2 (`PARTIALLY_COMPETITIVE`). Caso contrário, a v0.4.2 permanece, e o resultado é reportado.

## 4. Limites declarados antes da execução

A lacuna residual na AusElectricity (DEV, 2× contra "sem recorte") não é resolvida pela C5′.
A C5′ também não corrige a falta de memória sazonal longa nem a representação do nível. A lacuna para NLinear e Chronos no BENCH-04 deve persistir.
