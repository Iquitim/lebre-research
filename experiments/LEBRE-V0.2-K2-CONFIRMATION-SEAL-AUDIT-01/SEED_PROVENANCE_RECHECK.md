# Seed Provenance & Freshness Recheck

**Audited Range:** Seeds $1941..1970$ ($N=30$, contiguous)

---

## 1. Repository-Wide Seed Column Audit
An exhaustive scan of every `.csv` file across all experiment directories in the `experiments/` repository was performed to verify whether any historical stage had used seeds in the range $[1941, 1970]$ in its experimental `seed`, `random_seed`, or `seed_id` column:

- Historical Milestone 2 stages audited:
  - `LEBRE-V0.2-RESOURCE-COMPACTION-01` (DEV: 1401..1410)
  - `LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01` (FINAL: 1511..1540)
  - `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01` (FINAL: 1611..1640)
  - `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01` (FINAL: 1711..1740)
  - `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01` (DEV: 1801..1810, FINAL: 1811..1840)
  - `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01` (DEV: 1901..1910, FINAL: 1911..1940)
- Overlaps with any prior experimental `seed` column: **0 seeds (0.00%)**.

## 2. Investigation of Raw Number Matches
Earlier superficial regex scans matching the raw digits `1944`, `1955`, etc., occurred solely on step counters, timestamp fractions, or row numbers in legacy files (e.g. `DYNAMIC-LAG-LIFECYCLE-01`), never on seed allocation columns.

## 3. Verdict
- **SEED_FRESHNESS = PASS**.
- Confirmatory seed block $1941..1970$ was 100% fresh, unexposed to prior optimization or selection, and guarantees strict inferential validity.
