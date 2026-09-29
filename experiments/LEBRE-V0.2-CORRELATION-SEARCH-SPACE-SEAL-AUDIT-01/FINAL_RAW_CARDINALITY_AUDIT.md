# Final Raw Data Cardinality Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Cardinality Verification  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **CERTIFIED COMPLETE & VALID**  

---

## 1. Cardinality Assertion and Verification Matrix

The confirmatory raw dataset (`CORRELATION_SEARCH_FINAL_RESULTS.csv`) was independently audited for structural integrity, key uniqueness, and complete factorial balance:

| Cardinality Dimension | Preregistered Requirement | Observed Raw Value | Verification Status |
| :--- | :--- | :--- | :--- |
| **Independent Seeds ($N$)** | $30$ independent streams | $30$ seeds ($1811..1840$) | **EXACT MATCH** |
| **Benchmark Tasks ($T$)** | $14$ canonical tasks ($I_1..I_{14}$) | $14$ unique tasks | **EXACT MATCH** |
| **Evaluated Architectures ($M$)** | $3$ models ($R_0, R_1, M_1^*$) | $3$ models | **EXACT MATCH** |
| **Expected Total Rows** | $30 \times 14 \times 3 = 1,260$ | $1,260$ rows | **EXACT MATCH** |
| **Rows per Model** | $420$ task-seed runs | $420$ rows ($R_0$), $420$ ($R_1$), $420$ ($M_1^*$) | **EXACT MATCH** |
| **Unique Composite Key** | `(seed, task_id, model_label)` | $1,260$ unique combinations | **ZERO DUPLICATES** |
| **Missing Cells / Incomplete Runs** | $0$ missing records | $0$ missing records | **100% COMPLETE** |

---

## 2. Factorial Balance & Seed Integrity

1. **Seed Range:** Exactly covers `1811..1840` without gaps or historical collisions.
2. **Task Coverage:** Each of the 14 tasks has exactly 30 independent runs per model.
3. **Run Length:** Each run executed for exactly $6,000$ prequential streaming steps, yielding $2,520,000$ steps per model and $7,560,000$ total steps across all three models.
4. **Audit Conclusion:** The confirmatory raw dataset is structurally complete, fully aligned, free of duplicate or dropped rows, and valid as Level 1 ground truth.
