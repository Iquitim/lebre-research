# Raw Cardinality & Data Integrity Audit

**Audit Target:** `experiments/LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01/K2_FINAL_RESULTS.csv`

---

## 1. Cardinality Verification
- **Expected Rows:** 840 (30 seeds $\times$ 14 benchmark tasks $\times$ 2 models)
- **Observed Rows:** 840
- **Unique Composite Key:** `(seed, task_id, model_label)`
- **Duplicate Keys:** 0
- **Missing Seeds:** 0
- **Missing Tasks:** 0
- **Unexpected Models:** 0 (Only `C0_M1_PARENT` and `C2_K2`)

## 2. Prequential Step Audit
- **Stream Steps per Run:** 6,000 steps
- **Evaluation Window:** Steps 3,001..6,000 (3,000 prequential test steps)
- **Total Executed Stream Steps:** $840 \times 6,000 = 5,040,000\text{ steps}$
- **Essential Telemetry NaNs:** 0

## 3. Synchronized State Trajectory Cardinality
- **Target:** `K2_STATE_TRAJECTORY_ANALYSIS.csv`
- **Observed Rows:** 420 (30 seeds $\times$ 14 tasks paired trajectories)
- **Duplicate Paired Keys:** 0
- **Verdict:** CARDINALITY_AUDIT = PASS.
