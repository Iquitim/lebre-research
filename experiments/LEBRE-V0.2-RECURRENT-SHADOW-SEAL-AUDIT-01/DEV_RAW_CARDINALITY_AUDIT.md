# DEV Raw Cardinality Audit

**Dataset:** `RECURRENT_DEV_RESULTS.csv`  
**Expected Structure:** 10 Seeds ($1901..1910$) $\times$ 14 Tasks ($I_1..I_{14}$) $\times$ 3 Models (`C0_M1_PARENT`, `C1_K5`, `C2_K2`) = **420 rows**.

### Cardinality Findings:
- Total Rows Expected: **420**
- Total Rows Observed: **420**
- Unique Seeds: **10** (`1901` to `1910`)
- Unique Tasks: **14** (`I1_Memoryless_Linear` to `I14_Intermittent_Hybrid`)
- Unique Models: **3** (`C0_M1_PARENT`, `C1_K5`, `C2_K2`)
- Exact Duplicate Keys (`task_id, seed, model_label`): **0**
- Missing Values / NaNs: **0**

### Conclusion:
The DEV screening Level-1 dataset exhibits **perfect structural cardinality and zero data corruption**.
