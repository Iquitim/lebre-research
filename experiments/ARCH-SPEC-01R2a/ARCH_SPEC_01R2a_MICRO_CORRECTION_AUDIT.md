# ARCH-SPEC-01R2a: Micro-Correction Audit & Editorial Consistency Log

**Stage:** ARCH-SPEC-01R2a — Micro Editorial Consistency Fix Before Final Freeze  
**Date:** 2026-09-19  
**Role:** Scientific Documentation Auditor and Technical Editor  
**Status:** COMPLETE  

---

## 1. Executive Summary

This audit documents every textual and editorial consistency correction executed under stage `ARCH-SPEC-01R2a`. The corrections eliminate remaining wording inconsistencies across authoritative Markdown source files, HTML templates, and derived publication PDFs, enforcing:
1. Canonical **Five-State Structural Lifecycle** (*Ciclo de Vida Estrutural de Cinco Estados*: DORMANT, PROVISIONAL, ACTIVE, MATURE, EVICTED).
2. Empirically bounded **Linear-First** phrasing (eliminating universal claims of *garante*, *jamais*, *nunca*, or *sempre*).
3. Bounded **Memory Semantics** (observed mean persistent model-state footprint of 440.0 bytes under the benchmark $R_2\text{-MEM} \le 1024$ bytes ceiling, explicitly excluding total device RAM in hardware implementations).
4. Exact **FLOP Semantics** (measured mean algorithmic throughput $\le 100$ FLOPs/step under the frozen benchmark protocol, distinguishing mean benchmark budget from transient shadow probation peaks).
5. Hardware Boundary preservation (software simulation boundary affirmed; no micro-controller bare-metal deployment, battery efficiency, or hard real-time latency claims).

No source code was modified (`src/` and `tests/` remain 100% frozen; 124/124 tests pass). No benchmark results or constants were changed.

---

## 2. Micro-Correction Log

| File | Section | Original Text | Corrected Text | Reason | Scientific Meaning Changed? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md) | Section 8 (Título) | `## 8. Ciclo de Vida Estrutural de Quatro Fases` | `## 8. Máquina de Estados do Ciclo de Vida de Cinco Estados` | Alinhamento com a terminologia canônica de cinco estados do ciclo de vida | **NO** |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md) | Section 8 (Texto) | `limiar de promoção (> 15% por 120 passos)` | `limiar de promoção (\(\theta_{\text{promote}} = 0,05\), > 5% por \(T_{\text{prob}} = 50\) passos; maturação em \(\tau_{\text{mature}} = 100\) passos)` | Reconciliação numérica com constantes canônicas e separação entre ACTIVE e MATURE | **NO** |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md) | Section 41.2 | `quatro fases ambientais consecutivas` | `quatro regimes ambientais consecutivos` | Evitar ambiguidade entre estados de ciclo de vida e fases do experimento sintético | **NO** |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md) | Section 8 (Heading) | `## 8. Four-Phase Structural Lifecycle` | `## 8. Five-State Lifecycle State Machine` | Terminology alignment with canonical five-state lifecycle | **NO** |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md) | Section 8 (Text) | `promotion threshold (> 15% for 120 steps)` | `promotion threshold (\(\theta_{\text{promote}} = 0.05\), > 5% for \(T_{\text{prob}} = 50\) steps; maturation at \(\tau_{\text{mature}} = 100\) steps)` | Numerical reconciliation with frozen parameters and distinct mature transition | **NO** |
| [`LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md) | Section 41.2 | `four distinct environmental phases` | `four distinct environmental regimes` | Eliminate ambiguity between structural lifecycle states and synthetic task phases | **NO** |
| [`LEBRE_OVERVIEW_EN.md`](<lebre-research>/docs/architecture/LEBRE_OVERVIEW_EN.md) | Section 1 (Summary) | `strictly bounded to ~440 bytes of state RAM and <= 100 FLOPs/step` | `observed mean persistent model-state footprint of 440.0 bytes of RAM (compliant with the R2-MEM $\le 1024$ bytes ceiling; excluding execution stack and runtime buffers) and a measured mean algorithmic compute within the R2-FLOP limit of 100 FLOPs/step` | Canonical distinction between observed persistent state vs device RAM ceiling | **NO** |
| [`LEBRE_OVERVIEW_PTBR.md`](<lebre-research>/docs/architecture/LEBRE_OVERVIEW_PTBR.md) | Section 1 (Sumário) | `estritamente limitada a ~440 bytes de RAM de estado e <= 100 FLOPs/passo` | `pegada média observada de 440,0 bytes de estado persistente do modelo (em conformidade com o teto R2-MEM $\le 1024$ bytes; excluindo stack e runtime de hardware) e custo computacional médio observado dentro do limiar R2-FLOP de 100 FLOPs/passo` | Semântica canônica de memória de modelo e distinção de hardware | **NO** |
| [`LEBRE_ARCHITECTURAL_DECISIONS.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md) | ADR-006 (Heading) | `Strictly Bounded at $N \le 1$` | `Constrained to Scalar Recurrence ($N \le 1$)` | Neutral architectural phrasing regarding recurrent topology scope | **NO** |
| [`LEBRE_ARCHITECTURE_DIAGRAMS.md`](<lebre-research>/docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md) | Section D3 (Line 165) | `ensuring strictly bounded per-step execution latency` | `ensuring bounded per-step execution latency` | Avoid unqualified hard real-time latency claim | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 2 (Princípio 1) | `A LEBRE garante que dependências lineares triviais jamais disparem alocações de estado computacionalmente dispendiosas.` | `Nos regimes lineares avaliados, a alocação de estado recorrente não foi acionada quando a linha de base linear se mostrou suficiente.` | Enforce canonical bounded Linear-First wording; eliminate universal "garante" and "jamais" | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 2 (Princípio 2) | `Unidades estruturais provisionais jamais têm permissão para corromper as predições ativas do modelo durante sua fase de treinamento inicial.` | `Unidades estruturais provisionais são desacopladas das predições ativas do modelo durante sua fase de treinamento inicial.` | Remove absolute word "jamais" | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 2 (Princípio 3) | `garantindo a retenção através de longos intervalos quiescentes de Poisson.` | `preservando a retenção através de longos intervalos quiescentes de Poisson observados nos benchmarks.` | Remove absolute claim "garantindo" | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 2 (Princípio 4) | `A LEBRE impõe restrições operacionais rígidas em tempo real. A pegada de memória de estado é estritamente limitada a \approx 440 bytes de RAM de estado persistente do modelo...` | `Nos benchmarks avaliados, a LEBRE apresentou pegada média observada de 440,0 bytes de estado persistente do modelo, sob o teto R2-MEM de 1024 bytes (esse valor não representa o consumo total de RAM de uma implementação em hardware). O custo computacional médio observado permaneceu dentro do limiar R2-FLOP de 100 FLOPs/passo...` | Enforce canonical memory and FLOP semantics, hardware boundary, and mean budget specification | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 4 (Intro) | `Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em quatro estados: DORMANT (Dormente), PROVISIONAL (Provisional), ACTIVE / MATURE (Ativo / Maduro) e EVICTED (Desalojado).` | `Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em cinco estados: DORMANT, PROVISIONAL, ACTIVE, MATURE e EVICTED.` | Fix contradictory PT-BR lifecycle state count; enforce canonical five states | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 4.2 | `sem jamais terem perturbado a inferência ativa.` | `sem terem perturbado a inferência ativa.` | Remove unhedged word "jamais" | **NO** |
| [`build_ptbr_html.py`](<lebre-research>/scratch/build_ptbr_html.py) / [`LEBRE_CONDENSED_PTBR.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html) | Section 9 (Tabela) | `Máquina discreta de quatro estados` | `Máquina discreta de cinco estados (Dormant-Prov-Act-Mature-Evict)` | Reconcile architectural scope comparison table with five-state lifecycle | **NO** |
| [`build_en_html.py`](<lebre-research>/scratch/build_en_html.py) / [`LEBRE_CONDENSED_EN.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html) | Section 2 (Principle 2) | `Provisional structural units are never allowed to corrupt live model predictions during their initial training phase.` | `Provisional structural units are decoupled from live model predictions during their initial training phase.` | Tone down absolute expression "never allowed to corrupt" | **NO** |
| [`build_en_html.py`](<lebre-research>/scratch/build_en_html.py) / [`LEBRE_CONDENSED_EN.html`](<lebre-research>/docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html) | Section 2 (Principle 4) | `LEBRE continuously enforces hard resource bounds. Observed mean persistent model-state footprint is 440.0 bytes of RAM (excluding stack, code, runtime, and I/O buffers; benchmark limit \(R_2\text{-MEM} \le 1024\) bytes)...` | `Across evaluated benchmarks, LEBRE exhibited an observed mean persistent model-state footprint of 440.0 bytes of RAM (under the R2-MEM ceiling of 1024 bytes; this figure does not represent total device RAM in a hardware implementation). Measured mean computational throughput remained within the R2-FLOP limit of 100 FLOPs/step...` | Enforce canonical English bounded memory and FLOP semantics and hardware boundary qualification | **NO** |

---

## 3. Regression & Integrity Status

- **Source Code Changed:** `NO` (`src/` is strictly untouched).
- **Test Suite Execution:** `pytest tests/` ran 124 tests.
- **Pass Rate:** `124 passed in 2.87s` (100%).
- **Benchmark Data Changed:** `NO` (BENCH-01B CSVs, M1/M2 logs, and CAR-01 results remain frozen).
- **Scientific Results Changed:** `NO` (all numerical values and empirical conclusions preserved).
