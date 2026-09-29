# Step Count & Run Cardinality Reconciliation

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Run-Count and Step-Count Reconciliation  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **RECONCILED & RECLASSIFIED**  

---

## 1. Phase 2 DEV Run Count Reconciliation: 840 vs. 980

### The Discrepancy:
In the parent final report (`CORRELATION_SEARCH_FINAL_REPORT.md` Section 1), the text stated:
> "Phase 2 (Candidate Screening & Freeze): Evaluation of 840 DEV runs comparing continuous dense ($R_0$), dense multirate ($R_1$), four rotating sparse frontier configurations ($C_{1a}..C_{1d}$), and hierarchical coarse-to-fine ($C_2$)."

However, evaluating 7 distinct models ($R_0, R_1, C_{1a}, C_{1b}, C_{1c}, C_{1d}, C_2$) across $10\text{ seeds} \times 14\text{ tasks}$ mathematically equals:
$$7 \times 10 \times 14 = \mathbf{980\text{ runs}}$$

### Forensic Root Cause:
In `scratch/run_phase2_dev_screening.py`:
- Lines 33–42 define `CONFIGS` containing exactly 6 models: `R0_CONTINUOUS`, `C1_H16_B2`, `C1_H16_B4`, `C1_H32_B2`, `C1_H32_B4`, and `C2_HIERARCHICAL`.
- Line 50 prints:
  `Total screening simulation runs: 840` ($6 \times 10 \times 14 = 840$).
- Lines 65–72 then execute an additional 140 runs for `R1_DENSE_MULTIRATE` to construct the aligned baseline dataset, combining both into `df_full` ($840 + 140 = 980\text{ rows}$).
- **Audit Finding:** The author transcribed the initial batch printout ($840$) into narrative text without adding the 140 aligned baseline runs.
- **Classification:** `RUN_COUNT_ERROR` / `REPORTING_ERROR`.

---

## 2. Confirmatory Step Count Reconciliation: 2.52M vs. 7.56M

### The Discrepancy:
In `CORRELATION_SEARCH_FINAL_REPORT.md` and `CORRELATION_SEARCH_RESOURCE_REPORT.md`, the text asserted:
> "across $N=30$ independent confirmatory streams ($1811..1840$, 14 benchmark tasks, $2,520,000$ total stream steps)."

Yet $1,260\text{ confirmatory runs} \times 6,000\text{ steps/run} = \mathbf{7,560,000\text{ total stream steps}}$.

### Forensic Root Cause:
- Confirmatory evaluation tested 3 architectures: $R_0, R_1, M_1^*$.
- Each architecture had $30\text{ seeds} \times 14\text{ tasks} = 420\text{ runs}$.
- For a single architecture:
  $$\text{Steps per model cohort} = 420 \times 6,000 = \mathbf{2,520,000\text{ steps}}$$
- Total steps across all three models:
  $$\text{Total steps} = 3 \times 2,520,000 = \mathbf{7,560,000\text{ steps}}$$
- **Audit Finding:** The reported value ($2.52\text{M}$) represents the stream steps evaluated *per model cohort*, not across the complete three-model factorial design.
- **Classification:** `STEP_COUNT_ERROR` / `REPORTING_ERROR`.
