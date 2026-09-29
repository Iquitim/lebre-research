# Search Memory Terminology Corrigendum & Denominator Audit
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Authority Level: Level 3 (Sealed Forensic Corrigendum)

---

## 1. Executive Summary & Certified Frozen Terminology

To eliminate persistent ambiguity across LEBRE v0.2 documentation, this corrigendum establishes unambiguous definitions, formulas, and denominators for memory accounting across dense and sparse correlation search architectures.

### Frozen Certified Terminology:
1. **`DENSE_SEARCH_ACCUMULATOR_BYTES` = $330\text{ bytes}$**  
   Physical buffer: $5\text{ channels} \times 33\text{ taps} = 165\text{ cells} \times 2\text{ bytes (FP16)} = 330\text{ bytes}$.
2. **`SPARSE_SEARCH_ACCUMULATOR_BYTES` = $192\text{ bytes}$**  
   Frontier slots: $32\text{ active candidates} \times 6\text{ bytes (struct slot)} = 192\text{ bytes}$.
3. **`ACCUMULATOR_MEMORY_REDUCTION_PCT` = $41.82\%$**  
   $$\text{Reduction} = \frac{330 - 192}{330} = \frac{138}{330} = 41.8182\% \approx 41.82\%$$
4. **`DENSE_TOTAL_SEARCH_STATE_BYTES` = $330\text{ bytes}$** (Standard) / **$802\text{ bytes}$** (`LEGACY_FULL_SEARCH_SUBSYSTEM_STATE_BYTES`).
5. **`SPARSE_TOTAL_SEARCH_STATE_BYTES` = $260\text{ bytes}$**  
   $192\text{ bytes (table)} + 2\text{ bytes (queue pointer)} + 64\text{ bytes (active slot map)} + 2\text{ bytes (shared residual energy)} = 260\text{ bytes}$.
6. **`TOTAL_SEARCH_STATE_REDUCTION_PCT`:**
   - **Relative to Standard Table ($330\text{ B}$):**
     $$\text{Reduction} = \frac{330 - 260}{330} = \frac{70}{330} = \mathbf{21.21\%}$$
   - **Relative to Legacy Full Volatile State ($802\text{ B}$):**
     $$\text{Reduction} = \frac{802 - 260}{802} = \frac{542}{802} = \mathbf{67.58\%}$$

---

## 2. Forensic Reconstruction of the Legacy 802-Byte Metric

The value $802\text{ bytes}$ appeared in earlier experimental reports (e.g. `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_SPACE_MEMORY_MODEL.md` and `scratch/generate_search_compaction_figures.py`).

The forensic component decomposition (`experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/SEARCH_MEMORY_RECONCILIATION.csv`) confirms that $802\text{ bytes}$ is composed of:
1. `physical_correlation_accumulators`: $165 \times 2\text{ bytes} = 330\text{ bytes}$
2. `feature_energy_accumulators`: $165 \times 2\text{ bytes} = 330\text{ bytes}$
3. `residual_energy_accumulator`: $1 \times 2\text{ bytes} = 2\text{ bytes}$
4. `cell_tracking_metadata` (visit counts and ages): $140 \times 1\text{ byte} = 140\text{ bytes}$
$$\text{Sum} = 330 + 330 + 2 + 140 = \mathbf{802\text{ bytes}}$$

### Formal Metric Designation:
$$\mathbf{LEGACY\_FULL\_SEARCH\_SUBSYSTEM\_STATE\_BYTES} = 802\text{ B}$$
It represents the complete volatile state of the exploratory dense search module (including independent feature normalization and cell diagnostic telemetry). It must **never** be cited as "dense correlation-grid RAM" without explicitly listing its auxiliary energy and metadata components.

---

## 3. Repository Occurrence Audit & Denominator Mapping

| Occurrence String | Context / File | Measured Object | Denominator | Certified Interpretation |
|:---|:---|:---|:---:|:---|
| **`330 B`** | `CORRELATION_SEARCH_FINAL_RESULTS.csv` (`search_persistent_bytes`), `SEARCH_SPACE_MEMORY_MODEL.md` | Primary dense correlation grid ($165 \times \text{FP16}$). | $330\text{ B}$ | Ground truth dense accumulator table size. |
| **`192 B`** | `SEARCH_SPACE_MEMORY_MODEL.md`, `CORRELATION_SEARCH_FINAL_REPORT.md` | Active sparse candidate frontier table ($32 \times 6\text{B}$). | $330\text{ B}$ | Ground truth compact frontier table size ($-41.82\%$). |
| **`260 B`** | `SEARCH_SPACE_MEMORY_MODEL.md`, `walkthrough.md` | Total active sparse search state ($192\text{B table} + 68\text{B overhead}$). | $330\text{ B}$ or $802\text{ B}$ | Ground truth total compact search state. |
| **`802 B`** | `scratch/generate_search_compaction_figures.py`, `SEARCH_MEMORY_RECONCILIATION.csv` | Full legacy volatile search state (accumulators + energy + metadata). | $802\text{ B}$ | Valid historical object: `LEGACY_FULL_SEARCH_SUBSYSTEM_STATE_BYTES`. |
| **`41.82%`** | `CORRELATION_SEARCH_FINAL_REPORT.md`, `SUCCESS_CRITERIA_RECONCILIATION.md` | Reduction in accumulator table memory ($(330 - 192) / 330$). | $330\text{ B}$ | Certified: Gate G4 Passed. |
| **`21.21%`** | `CORRELATION_SEARCH_SEAL_AUDIT_FINAL_REPORT.md` | Reduction in total search state relative to standard table ($(330 - 260) / 330$). | $330\text{ B}$ | Certified standard total state reduction. |
| **`67.58%`** | `walkthrough.md`, `CORRELATION_SEARCH_FINAL_REPORT.md` | Reduction in volatile state relative to full legacy subsystem ($(802 - 260) / 802$). | $802\text{ B}$ | Valid only when explicitly qualified against legacy 802B state. |

---

## 4. Governance Rule on Future Reporting

Any statement claiming search RAM reduction must explicitly name the metric:
- For accumulator table compaction: report **$41.82\%$ ($330\text{ B} \to 192\text{ B}$)**.
- For total state compaction vs dense grid: report **$21.21\%$ ($330\text{ B} \to 260\text{ B}$)**.
- For total state compaction vs legacy full volatile state: report **$67.58\%$ ($802\text{ B} \to 260\text{ B}$)** with explicit citation of auxiliary energy/metadata inclusion.
