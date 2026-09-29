# Confirmatory Seed Freshness and Provenance Audit

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Registry Comparison Across Project History

To ensure zero seed contamination or data leakage, the seeds used in `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01` were cross-referenced across every prior experimental registry in the repository:

| Experimental Milestone | Cohort Phase | Registered Seed Range | Total Seeds | Overlap with Confirmatory Seeds (1711..1740) |
| :--- | :--- | :--- | :--- | :--- |
| **BENCH-01A** | Discovery | 1..100 | 100 | 0 (ZERO) |
| **BENCH-01B** | Confirmatory | 101..130 | 30 | 0 (ZERO) |
| **INTEGRATION-DESIGN-01** | DEV | 1301..1310 | 10 | 0 (ZERO) |
| **INTEGRATION-DESIGN-01** | FINAL | 1311..1340 | 30 | 0 (ZERO) |
| **RESOURCE-COMPACTION-01** | DEV | 1401..1410 | 10 | 0 (ZERO) |
| **RESOURCE-COMPACTION-01** | FINAL | 1411..1440 | 30 | 0 (ZERO) |
| **SHADOW-RENT-GATE-01** | DEV | 1601..1610 | 10 | 0 (ZERO) |
| **SHADOW-RENT-GATE-01** | FINAL | 1611..1640 | 30 | 0 (ZERO) |
| **MULTIRATE-DECOMPOSITION-01** | DEV | 1701..1710 | 10 | 0 (ZERO) |
| **MULTIRATE-DECOMPOSITION-01** | FINAL | 1711..1740 | 30 | **TARGET COHORT (30)** |

---

## 2. Forensic Overlap Audit Result

Script `scratch/check_seed_column_overlap.py` executed an exhaustive search across all CSV files in `experiments/`.
- DEV seeds ($1701..1710$): Zero collisions with prior studies.
- Confirmatory seeds ($1711..1740$): Zero collisions with prior studies.
- DEV vs. FINAL within Multirate study: Completely disjoint sets.

- **`FINAL_SEEDS_FRESH`:** **`YES`**
