# Compute Field Dictionary & Metrics Lexicon

**LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01**

---

## 1. Overview & Forensic Objective

A primary motivation for this seal audit is resolving apparently conflicting compute numbers appearing across parent artifacts in `LEBRE-V0.2-RESOURCE-COMPACTION-01` and `LEBRE-V0.2-INTEGRATION-DESIGN-01`:
- Why does the machine-readable block report **56.5 FLOPs/step**?
- Why does Table 6 in the resource report state **81.36 FLOPs/step** (Live) and **108.19 FLOPs/step** (Total Online)?
- Why do raw CSV simulation files record **88.65 FLOPs/step** for shadow compute?
- Why does the integration seal report state **167.99 FLOPs/step** (~168.0)?

This dictionary provides the authoritative definition, mathematical formula, code origin, and reconciliation for every compute field.

---

## 2. Field Specifications

### 2.1 `LIVE_FP_FLOPS_RAW_COMPACTED` (56.52 FP FLOPs/step)
- **Reported Value:** $56.52$ FLOPs (reported as $56.5$ in `RESOURCE_COMPACTION_FINAL_REPORT.md` Section 43 block).
- **Mathematical Definition:**
  $$\text{FLOPs}_{\text{live,compacted}}(t) = \text{FLOPs}_{\text{base}}(t) + \text{FLOPs}_{\text{scaler\_transform}}(t) + \sum_{k \in \mathcal{A}_{\text{taps}}} \text{FLOPs}_{\text{tap}, k}(t) + \mathbb{I}_{\text{rec}}(t) \cdot \text{FLOPs}_{\text{rec\_live}}(t)$$
- **Code Origin:** `scratch/run_v02_resource_compaction_experiments.py`, lines 548–567 in `CompactedLEBREModel.step()`.
- **Included Components:**
  - Base Linear Predictor: `transform` ($2D = 10$) + `update` ($3D + 3 = 18$) = $28.0$ FLOPs.
  - Causal Scaler: `transform` only ($2D = 10.0$ FLOPs).
  - Active Tap Predictors: $10.0$ FLOPs per active tap ($2$ forward $+ 8$ LMS update).
  - Active Recurrent Unit (when state is RECURRENT or BOTH): $34.0$ FLOPs ($18$ forward $+ 16$ update).
- **Excluded Components:**
  - `scaler.update`: In `CompactedLEBREModel.step()`, line 559 of the integration model (`self.scaler.update(x_raw, self.live_res)`) was inadvertently not invoked. This omitted $4D = 20.0$ FLOPs/step.
- **Execution Scope:** Mean over all 6,000 steps across 420 confirmatory runs ($N=30$ seeds $\times$ 14 tasks).
- **Reconciliation Status:** Understood. $56.52$ FLOPs represents the exact instrumented counter in the compaction script.

---

### 2.2 `LIVE_FP_FLOPS_CANONICAL_T3` (81.37 FP FLOPs/step)
- **Reported Value:** $81.3687$ FLOPs (reported as $81.36$ in `RESOURCE_COMPACTION_RESOURCE_REPORT.md` Table 6 and $81.4$ in `LEBRE_V0_2_SEAL_AUDIT_FINAL_REPORT.md`).
- **Mathematical Definition:**
  $$\text{FLOPs}_{\text{live,canonical}}(t) = \text{FLOPs}_{\text{live,compacted}}(t) + \text{FLOPs}_{\text{scaler\_update}}(t)$$
  where $\text{FLOPs}_{\text{scaler\_update}} = 4D = 20.0$ FLOPs.
- **Code Origin:** `scratch/run_v02_integration_experiments.py`, lines 538–572 in `IntegratedLEBREModel.step()`.
- **Included Components:**
  - Base Linear Predictor ($28.0$ FLOPs)
  - Causal Scaler Transform ($10.0$ FLOPs) + Causal Scaler Update ($20.0$ FLOPs) = $30.0$ FLOPs
  - Active Tap Predictors ($10.0$ FLOPs/tap)
  - Active Recurrent Unit ($34.0$ FLOPs when active)
- **Execution Scope:** Confirmatory 30-seed parent integration cohort ($N=30$ seeds $\times$ 14 tasks).
  - Memoryless tasks ($I_1, I_2$): $58.0$ FLOPs
  - Single delay tasks ($I_3, I_4, I_5$): $86.8$–$88.9$ FLOPs
  - Hybrid tasks ($I_9, I_{14}$): $97.0$–$127.2$ FLOPs
  - Mean across all tasks: **$81.37$ FLOPs/step**.
- **Reconciliation Status:** Authoritative canonical live compute baseline for $T_3$. Fully complies with Legacy R2 ($\le 100$ FP FLOPs/step).

---

### 2.3 `SHADOW_FP_FLOPS_INSTRUMENTED` (88.65 FP FLOPs/step)
- **Reported Value:** $88.65$ FLOPs in `RESOURCE_COMPACTION_FINAL_RESULTS.csv` (and $86.63$ FLOPs in parent integration study).
- **Mathematical Definition:**
  $$\text{FLOPs}_{\text{shadow}}(t) = \text{FLOPs}_{\text{probing}}(t) + \sum_{c \in \mathcal{C}_{\text{pool}}} \text{FLOPs}_{\text{cand}, c}(t) + \text{FLOPs}_{\text{shadow\_rec}}(t) + \text{FLOPs}_{\text{arbitrator}}(t)$$
- **Code Origin:** Accumulated across background routines:
  - Correlation grid probing: $M=2$ pairs probed per step $\times 4.0$ FLOPs = $8.0$ FLOPs.
  - Provisional candidate scoring: $C \in [0, 3]$ candidates $\times 8.0$ FLOPs (forward + counterfactual loss + EMA + LMS) $\approx 12.0$ FLOPs.
  - Shadow recurrent tracking: $18$ forward $+ 16$ update $+ 6$ EMA = $40.0$ FLOPs.
  - Counterfactual grid evaluation & Arbitrator: $8$ losses $+ 4$ gains $+ 16$ EMA filters = $28.0$ FLOPs.
  - Total per-step nominal shadow execution: $8.0 + 12.0 + 40.0 + 28.0 = 88.0$ FLOPs.
- **Execution Scope:** Executed continuously at every streaming step ($t=1..6000$).
- **Reconciliation Status:** Accurately reflects full continuous background exploration without duty cycling.

---

### 2.4 `ANALYTICAL_MARGINAL_SHADOW_FP` (26.83 FP FLOPs/step)
- **Reported Value:** $26.83$ FLOPs in `RESOURCE_COMPACTION_RESOURCE_REPORT.md` Section 3.
- **Mathematical Definition:**
  $$\text{FLOPs}_{\text{shadow,marginal}} = \text{FLOPs}_{\text{probing}} + \mathbb{E}[\text{FLOPs}_{\text{cand\_eval}}]$$
- **Origin & Purpose:** Derived from `LEBRE_V0_2_RESOURCE_MODEL.md` as the *removable exploratory search burden* (probing $8.0$ FLOPs + candidate maintenance $\approx 18.8$ FLOPs). It represents the exact compute overhead that can be turned off or duty-cycled during quiescent regimes.
- **Reconciliation Status:** Valid analytical quantity representing marginal exploratory compute.

---

### 2.5 `SINGLE_REGIME_TOTAL_ONLINE_FP` (108.19 FP FLOPs/step)
- **Reported Value:** $108.19$ FLOPs ($81.36 + 26.83$) in `RESOURCE_COMPACTION_RESOURCE_REPORT.md` Table 6.
- **Scope:** Combines canonical live compute ($81.36$) with marginal exploratory probing ($26.83$) under single-regime tracking.
- **Reconciliation Status:** Reconciles Table 6 arithmetic.

---

### 2.6 `FULL_STREAM_TOTAL_ONLINE_FP` (167.99 FP FLOPs/step)
- **Reported Value:** $167.998$ FLOPs in parent integration seal audit (`T3_TOTAL_ONLINE_FP_MEAN = 168.0`).
- **Mathematical Definition:**
  $$\text{FLOPs}_{\text{total}} = \text{FLOPs}_{\text{live,canonical}} (81.37) + \text{FLOPs}_{\text{shadow,instrumented}} (86.63) = 167.998 \text{ FLOPs}$$
- **Scope:** Full continuous operation across all 14 benchmark tasks including hybrid regimes.
- **Reconciliation Status:** Authoritative un-gated total online compute of $T_3$. Exceeds legacy R2 ($100$ FLOPs), establishing the exact technical justification for Stage 2.3 (`SHADOW-RENT-GOVERNANCE-01`).

---

### 2.7 `INTEGER_OPS_MEAN` (33.26 vs 37.18 Ops/step)
- **Reported Values:**
  - $C_0$: $33.26$ ops/step (reported as $33.3$)
  - $C_1$: $37.18$ ops/step (reported as $37.2$)
- **Origin:** Ring buffer modulo pointer arithmetic, tap lag indexing, candidate age decrement, plus FP16 half-precision casting:
  - In $C_1$, each step performs $4$ cast/quantization ops (converting probed inputs and correlation updates between FP32 and FP16), resulting in $+3.92$ ops/step over $C_0$.
- **Reconciliation Status:** Exact quantitative agreement.

---

### 2.8 `MEMORY_TRAFFIC_BYTES_MEAN` (291.15 Bytes/step)
- **Reported Value:** $291.15$ B/step (reported as $291.1$).
- **Origin:** Sum of bytes read and bytes written to persistent state during step execution.
  (If scaler update memory traffic of $80$ B is included, canonical traffic is $371.15$ B/step, well within the $512$ B/step ceiling).
- **Reconciliation Status:** Exact quantitative agreement.
