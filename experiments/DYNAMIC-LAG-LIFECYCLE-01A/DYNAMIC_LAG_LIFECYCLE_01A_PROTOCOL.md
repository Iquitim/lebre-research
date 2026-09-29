# DYNAMIC-LAG-LIFECYCLE-01A: Audit Protocol Specification
## Corrective Mini-Audit of Ablation Integrity & Statistical Traceability

**Stage ID:** `DYNAMIC-LAG-LIFECYCLE-01A`  
**Parent Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Governing Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Canonical Invariants:** `src/` and `tests/` are 100% bitwise immutable; M3 unopened; zero novelty claims.

---

## 1. Audit Scope & Objectives

This audit evaluates and reconciles two identified internal inconsistencies:
1. **Inconsistency A (B7 vs B7_E0 Equivalence vs H5 Claim):**
   - Trace why `DYNAMIC_LAG_LIFECYCLE_01_FINAL_REPORT.md` displays identical values for B7 and B7_E0.
   - Trace why B7_E0 eviction was largely inactive during silence in D7.
   - Isolate the ablation mechanism, test deterministic micro-trajectories, and verify on original evaluation seeds (`801`–`830`) and 30 fresh confirmation seeds.
2. **Inconsistency B (Statistical Significance $p < 10^{-15}$ vs $p = 1.73 \times 10^{-6}$):**
   - Trace exact computational lineage of both numbers.
   - Establish whether pseudoreplication occurred (pooling 90 task $\times$ seed observations).
   - Recompute exact combinatorial Wilcoxon, asymptotic Wilcoxon, bootstrap 95% CI, and Cohen's $d_z$ strictly at the independent seed level ($N=30$).

---

## 2. Execution Protocol

### Step 1: Evidence Freezing
- Hash all 13 artifacts from `DYNAMIC-LAG-LIFECYCLE-01` and record in `DYNAMIC_LAG_LIFECYCLE_01A_ORIGINAL_ARTIFACT_HASHES.txt`. Never overwrite parent artifacts.

### Step 2: Track A Implementation & Micro-Trace
- Produce `B7_B7E0_CONFIG_DIFF.md` and `B7_B7E0_EXECUTION_TRACE.md`.
- Construct deterministic synthetic stream with silence interval ($T=10,000$, silence $[3000, 7000]$).
- Execute micro-trace and log `B7_B7E0_MICROTRACE.csv`.
- Implement isolated ablation repair strictly under audit path; test original seeds (`801`–`830`) and fresh confirmation seeds (`901`–`930`) on D7, D4, and D9.
- Log `B7_B7E0_SEED_RESULTS.csv` and `B7_B7E0_TAP_EVENTS.csv`.

### Step 3: Track B Statistical Re-Audit
- Populate `STATISTICAL_CLAIM_TRACEABILITY.csv` mapping every inferential claim in the original report.
- Extract `H1_PAIRED_DIFFERENCES.csv`.
- Compute full robustness statistics (paired mean/median delta, 95% bootstrap CI, Cohen's $d_z$, win rate, Wilcoxon exact/asymp, sign test).
- Produce `DYNAMIC_LAG_LIFECYCLE_01A_STATISTICAL_REAUDIT.md`.

### Step 4: Visualizations & Synthesis
- Generate 5 minimal diagnostic figures in `figures/`:
  - `F1_B7_vs_B7E0_survival_D7.png`
  - `F2_B7_vs_B7E0_relevance_trace.png`
  - `F3_post_quiescence_recovery.png`
  - `F4_D4_support_relocation_comparison.png`
  - `F5_H1_paired_seed_differences.png`
- Compile `DYNAMIC_LAG_LIFECYCLE_01A_CORRIGENDUM.md` and `DYNAMIC_LAG_LIFECYCLE_01A_FINAL_REPORT.md`.
- Run post-audit regression suite (124 tests).
- Enforce hard stop.
