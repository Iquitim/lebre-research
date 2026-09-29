# Experimental Protocol: Correlation Search Space Compaction

**Study Identifier:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2, Non-Canonical T3)  
**Author:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** FROZEN EXPERIMENTAL PROTOCOL  

---

## 1. Scientific Context and Governance

### 1.1 Objective
To determine whether LEBRE's discrete temporal delay search space can be compacted from its ambient dense $165$-cell grid ($5\text{ features} \times 33\text{ lags}$) into a bounded, resource-governed search frontier while preserving true-delay discovery, non-contiguous support identification, moving-support tracking, quiescent retention, and predictive non-inferiority.

### 1.2 Governance Invariants
- **`CANONICAL_VERSION`:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`).
- **`CANONICAL_SRC_MUTATION`:** `FORBIDDEN`.
- **`CANONICAL_TEST_MUTATION`:** `FORBIDDEN`.
- **`M3_STATUS`:** `UNOPENED`.
- **`NOVELTY_CLAIM_READY`:** `NO`.
- **`T3_CANDIDATE_STATUS`:** `EXPERIMENTAL_NON_CANONICAL`.
- **`SAFE_FOR_INTEGRATED_VALIDATION`:** `NO`.
- **`FP16_CORR_GRID_PRECISION`:** Frozen FP16 correlation storage ($2\text{ bytes per active cell}$). Precision changes are forbidden in this stage.
- **`CAUSAL_NORMALIZATION_IMMUTABILITY`:** Causal standard scaler parameters, input dimensions ($D=5$), and normalization structures remain immutable.

---

## 2. Frozen Multirate Parent Clock Invariants

To guarantee causal interpretability, all multirate scheduling clocks are strictly inherited from parent candidate $M_1$ (`MR1_C`) and held constant across all evaluations:
- **$K_{\text{probe}} = 2$** (Probe every 2 stream steps, evaluating $2$ hypotheses per probe step).
- **$K_{\text{candidate\_obs}} = 5$** (Evaluate candidate loss every 5 stream steps).
- **$K_{\text{candidate\_learn}} = 10$** (Execute candidate parameter LMS update every 10 stream steps).
- **$K_{\text{rec\_forward}} = 1$** (Continuous recurrent state tracking every step).
- **$K_{\text{rec\_learn}} = 10$** (Recurrent RTRL parameter sensitivity update every 10 stream steps).
- **$K_{\text{arbitration}} = 5$** (Capacity arbitration update every 5 stream steps).

Retuning clocks while altering search-space representation is strictly forbidden.

---

## 3. Baseline References and Privileged Diagnostic Oracle

### 3.1 Reference Baselines
1. **$R_0$ (Canonical Behavioral Reference):**
   - Compacted continuous-shadow T3 baseline.
   - Dense $5 \times 33$ correlation grid, continuous shadow execution ($K=1$).
   - Used to judge predictive non-inferiority, pure-lag preservation, and switching latency.
2. **$R_1$ (Causal Parent Multirate Reference):**
   - Multirate candidate $M_1$ ($MR_{1C}$) with dense $165$-cell correlation grid and frozen clocks.
   - Used to isolate the causal effect of the search-space intervention.

### 3.2 Privileged Diagnostic Oracle ($O_{\text{TRUE\_SUPPORT}}$)
- Evaluated **strictly offline** on synthetic streams where generating ground-truth delays are known.
- Off-policy, non-interfering, and completely excluded from candidate runtime memory and compute.
- Used to compute search regret:
  $$\text{SEARCH\_REGRET}(t) = \max_{(i, k) \in \text{Dense}} |\rho_{i, k}(t)| - \max_{(i, k) \in \text{Frontier}} |\rho_{i, k}(t)|$$

---

## 4. Search-Space Candidate Architectures

### 4.1 Primary Candidate Family: $C_1$ (Rotating Sparse Frontier)
- **State Representation:**
  - Hot Frontier: Stores explicit FP16 correlation state and metadata for $H \in \{16, 32\}$ cells.
  - Persistent memory: $H \times (2\text{ B correlation} + 1\text{ B feature index} + 1\text{ B lag index} + 2\text{ B age}) = H \times 6\text{ Bytes}$.
  - Dense correlation array is **excised completely** from RAM.
- **Exploration Mechanism:**
  - Round-robin exploration queue visiting $B \in \{2, 4\}$ inactive cells per probe step.
  - Bounded silence invariant:
    $$\text{MAX\_UNOBSERVED\_INTERVAL} \le \lceil (165 - H) / B \rceil \times K_{\text{probe}} \quad \text{stream steps}$$
- **Admission & Eviction:**
  - If a probed inactive cell exhibits correlation magnitude exceeding the minimum frontier cell by a margin $\delta_{\text{admit}} = 0.02$, it is admitted into the frontier, and the lowest-magnitude cell is evicted back to the exploration queue.
  - Candidates entering provisional status ($|\rho| > 0.20$) are promoted from the frontier into the active provisional candidate list.

### 4.2 Secondary Candidate Family: $C_2$ (Hierarchical Coarse-to-Fine Search)
- **Prerequisite:** Evaluated on DEV only if the empirical Lag-Score Locality Audit confirms neighbor correlation ($r \ge 0.60$ and recall $\ge 70\%$).
- **Structure:** Coarse lag anchors ($k \in \{2, 4, 8, 16, 32\}$) evaluated initially; fine refinement activated within a radius $\Delta k = \pm 1$ around coarse peaks.
- **Anti-Miss Exploration Rule:** Inactive coarse regions must be periodically revisited via a secondary queue to prevent permanent pruning of isolated delays.

---

## 5. Experimental Phases and Cohort Allocations

### 5.1 Phase 0: Dense Grid Utilization Audit
- Evaluated on DEV seeds $1801..1810$ ($N=10$, 14 tasks) under dense baseline $R_1$.
- Quantifies cell visit frequency, threshold crossings, candidate births, and promotion ancestry to measure search-space concentration.

### 5.2 Phase 1: Lag-Score Locality Audit
- Evaluated on DEV seeds $1801..1810$.
- Measures cross-lag correlation decay and peak width around true delays.
- Decides `COARSE_TO_FINE_ELIGIBLE` (`YES` / `NO`).

### 5.3 Phase 2: DEV Screening and Candidate Selection
- Evaluates deployable candidates ($H \in \{16, 32\}$, $B \in \{2, 4\}$, max 6 configurations).
- Freezes exactly **ONE** candidate in `FINAL_SEARCH_CANDIDATE_FREEZE.md`.

### 5.4 Phase 3: Confirmatory Evaluation ($N=30$)
- Fresh independent seeds $1811..1840$ on the full 14-task benchmark suite ($84,000$ steps per seed; $2,520,000$ total steps).

---

## 6. Mandatory Confirmatory Gates

1. **Compute Gate:** Mean total online compute $\le 100.00\text{ FP/step}$.
2. **Predictive Non-Inferiority:** Aggregate $\Delta\text{NMSE} \le +0.0100$ vs. $R_0$ ($95\%$ one-sided upper CI bound).
3. **Pure-Lag Preservation:** $\Delta\text{NMSE} \le +0.0150$ on $I_3, I_4, I_5, I_8$.
4. **Switching Preservation:** Delay-to-latent and latent-to-delay structural recovery within $+50\text{ steps}$ of $R_0$.
5. **Hybrid Complementarity:** $G_{D|B+R} > 0$ and $G_{R|B+D} > 0$ on $I_9$.
6. **No Hidden State:** Zero dense 165-cell correlation arrays retained in RAM.
