# Seed Provenance: LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Governance:** Strict Preregistered Seed Lineage Invariance  
**Date:** September 22, 2026  

---

## 1. Complete Historical Seed Registry

To prevent data contamination, tuning on test data, and subtle statistical leakage, LEBRE enforces strictly partitioned, disjoint seed cohorts across experimental milestones:

| Milestone / Experiment Stage | Purpose | Cohort Scope | Seeds Allocated | Status |
|:---|:---|:---:|:---:|:---:|
| `BENCH-01A` / Canonical Benchmarks | Exploratory & Baselines | $N=5$ | 42, 123, 456, 789, 1024 | FROZEN |
| `RESOURCE-ACCOUNTING-01` | Resource Instrumentation | $N=10$ | 1201..1210 | FROZEN |
| `LEBRE-V0.2-INTEGRATION-DESIGN-01` | DEV Screening | $N=10$ | 1301..1310 | FROZEN |
| `LEBRE-V0.2-INTEGRATION-DESIGN-01` | Confirmatory Evaluation | $N=30$ | 1311..1340 | FROZEN |
| `LEBRE-V0.2-RESOURCE-COMPACTION-01` | DEV Screening | $N=10$ | 1401..1410 | FROZEN |
| `LEBRE-V0.2-RESOURCE-COMPACTION-01` | Confirmatory Evaluation | $N=30$ | 1411..1440 | FROZEN |
| `CORRECTIVE-CONFIRMATION-01` | DEV Screening | $N=10$ | 1501..1510 | FROZEN |
| `CORRECTIVE-CONFIRMATION-01` | Confirmatory Evaluation | $N=30$ | 1511..1540 | FROZEN |
| `SHADOW-RENT-GOVERNANCE-01` | DEV Screening | $N=10$ | 1601..1610 | FROZEN |
| `SHADOW-RENT-GOVERNANCE-01` | Confirmatory Evaluation | $N=30$ | 1611..1640 | FROZEN |
| `SHADOW-MULTIRATE-DECOMPOSITION-01` | DEV Screening | $N=10$ | 1701..1710 | FROZEN |
| `SHADOW-MULTIRATE-DECOMPOSITION-01` | Confirmatory Evaluation | $N=30$ | 1711..1740 | FROZEN |
| `CORRELATION-SEARCH-COMPACTION-01` | DEV Screening | $N=10$ | 1801..1810 | FROZEN |
| `CORRELATION-SEARCH-COMPACTION-01` | Confirmatory Evaluation | $N=30$ | 1811..1840 | FROZEN |
| **`RECURRENT-SHADOW-COST-01` (CURRENT)** | **DEV Screening** | $N=10$ | **1901..1910** | **ACTIVE (FRESH)** |
| **`RECURRENT-SHADOW-COST-01` (CURRENT)** | **Confirmatory Evaluation** | $N=30$ | **1911..1940** | **RESERVED (FRESH)** |

---

## 2. Seed Contamination Audit

- **DEV Seeds 1901..1910 ($N=10$):** Verified completely unused as simulation seeds in all prior stages.
- **FINAL Seeds 1911..1940 ($N=30$):** Verified completely independent, untouched, and unpeeked.
- **Overlap Check:**
  $$\{1901..1910\} \cap \{1911..1940\} = \emptyset$$
  $$\{1901..1940\} \cap \{ 	ext{All Historical Seeds} \} = \emptyset$$
- **Seed Provenance Certification:** `100% PRISTINE / ZERO CONTAMINATION`.
