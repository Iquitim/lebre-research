# Seed Provenance and Freshness Certification

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Registered Cohort Allocations

To ensure zero prequential data leakage, seed contamination, or post-hoc cherry-picking, the random seeds for this study were preregistered and allocated into disjoint sets:

- **DEV Exploration & Policy Screening Cohort:**
  - Seeds: `1801..1810`
  - Sample Size: $N_{\text{DEV}} = 10$
  - Usage: Dense grid utilization audit, lag-score locality characterization, candidate parameter tuning, DEV policy comparisons.
- **FINAL Confirmatory Cohort:**
  - Seeds: `1811..1840`
  - Sample Size: $N_{\text{FINAL}} = 30$
  - Usage: Single-shot confirmatory evaluation of the frozen candidate $M_1^*$ vs. continuous reference $R_0$ and parent causal reference $R_1$.

---

## 2. Exhaustive Historical Registry Overlap Audit

An automated exhaustive scan was conducted across every CSV, JSON, and markdown artifact in the repository (including `experiments/`, `data/`, and `results/`). The certified registry history is summarized below:

| Experimental Milestone | Cohort / Stage | Registered Seed Range | Total Seeds | Overlap with Target Range (1801..1840) | Collision Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BENCH-01A** | Exploration & Discovery | 1..100 | 100 | 0 (ZERO) | **VERIFIED CLEAN** |
| **BENCH-01B** | Confirmatory Benchmark | 101..130 | 30 | 0 (ZERO) | **VERIFIED CLEAN** |
| **INTEGRATION-DESIGN-01** | DEV Screening | 1301..1310 | 10 | 0 (ZERO) | **VERIFIED CLEAN** |
| **INTEGRATION-DESIGN-01** | Confirmatory Evaluation | 1311..1340 | 30 | 0 (ZERO) | **VERIFIED CLEAN** |
| **RESOURCE-COMPACTION-01**| DEV Screening | 1401..1410 | 10 | 0 (ZERO) | **VERIFIED CLEAN** |
| **RESOURCE-COMPACTION-01**| Confirmatory Evaluation | 1411..1440 | 30 | 0 (ZERO) | **VERIFIED CLEAN** |
| **SHADOW-RENT-GATE-01** | DEV Screening | 1601..1610 | 10 | 0 (ZERO) | **VERIFIED CLEAN** |
| **SHADOW-RENT-GATE-01** | Confirmatory Evaluation | 1611..1640 | 30 | 0 (ZERO) | **VERIFIED CLEAN** |
| **MULTIRATE-DECOMPOSITION**| DEV Screening | 1701..1710 | 10 | 0 (ZERO) | **VERIFIED CLEAN** |
| **MULTIRATE-DECOMPOSITION**| Confirmatory Evaluation | 1711..1740 | 30 | 0 (ZERO) | **VERIFIED CLEAN** |
| **CORRELATION-SEARCH** | **DEV Screening** | **1801..1810** | **10** | **TARGET DEV SET** | **FRESH / UNUSED** |
| **CORRELATION-SEARCH** | **Confirmatory Evaluation**| **1811..1840** | **30** | **TARGET FINAL SET**| **FRESH / UNUSED** |

---

## 3. Provenance Certification

1. **`DEV_SEEDS_FRESH = YES`**: Seeds $1801..1810$ have zero prior occurrences as random stream seeds.
2. **`FINAL_SEEDS_FRESH = YES`**: Seeds $1811..1840$ have zero prior occurrences as random stream seeds.
3. **`DEV_FINAL_DISJOINT = YES`**: The DEV and FINAL cohorts share zero common seeds.
4. **`STOCHASTIC_INDEPENDENCE = VERIFIED`**: Each seed independently generates the 14 synthetic prequential benchmark streams ($I_1..I_{14}$, 6,000 steps per stream).
