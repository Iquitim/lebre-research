# BENCH-01A: Hyperparameter Tuning Specification & Calibration Protocol

**Document ID:** BENCH-01A-TUNING  
**Auditor:** Statistical Fairness Auditor & Experimental Methodologist  
**Date:** September 19, 2026  
**Status:** PROTOCOL FROZEN — SELECTION BIAS MITIGATED  
**Governing Standard:** Sections 74–93, 202, 203, 212 of BENCH-01A Protocol  

---

## 1. Principles of Algorithmic Fairness in Comparative Evaluation

Per Section 74 of the governing protocol:
> *"A method must not receive materially more optimization effort merely because it is new or familiar."*

In many comparative studies, proposed methods are exhaustively tuned on the evaluation data while baselines are run with sub-optimal default parameters. To eliminate this pervasive form of evaluation bias:
1. **Track B Zero-Tuning Rule (Section 75):** Track B is frozen under `M2_SINGLE_STATE_SPEC.md`. It receives **ZERO hyperparameter tuning, zero structural adjustments, and zero threshold modifications** on any benchmark stream.
2. **Symmetric Baseline Budget (Section 78):** Every competitive baseline is granted an identical maximum search budget of **exactly 16 configurations** (`MAX_CONFIGS = 16`) per task family.
3. **Strict Chronological Data Splitting (Sections 85–90):** Model selection is conducted exclusively on an upfront chronological calibration segment. The final evaluation interval is strictly quarantined and untouched by any hyperparameter selection.

---

## 2. Chronological Stream Partitioning Protocol (Sections 85–93)

To respect non-stationary temporal causality while enabling rigorous hyperparameter selection, every benchmark stream is partitioned into three chronological segments:

```
+-------------------------------------------------------------------------------+
|                       CHRONOLOGICAL STREAM PARTITIONING                       |
|                                                                               |
|  [CALIBRATION PREFIX: 0% - 15%]  -->  Baseline Hyperparameter Grid Screen     |
|  [VALIDATION SEGMENT: 15% - 30%] -->  Configuration Stability Confirmation   |
|  [FINAL TEST SEGMENT: 30% - 100%]->  Frozen Competitive Evaluation (N=30 seeds|
+-------------------------------------------------------------------------------+
```

### 2.1 Segment Definitions & Governance
1. **Calibration Prefix ($t \in [1, 0.15 \cdot T]$):**  
   All 16 hyperparameter candidates per baseline are executed across 3 calibration seeds. The optimal configuration is selected based on prequential MSE on this segment. This segment is discarded from final test scoring.
2. **Validation Segment ($t \in [0.15 \cdot T + 1, 0.30 \cdot T]$):**  
   The single selected configuration per baseline is executed to verify numerical stability, finite gradients, and absence of divergence. No hyperparameter changes may occur in validation.
3. **Final Test Segment ($t \in [0.30 \cdot T + 1, T]$):**  
   The locked baseline configurations and the frozen Track-B model are evaluated across **30 independent random seeds**. All reported predictive, adaptation, resource, and Pareto metrics are computed exclusively over this final $70\%$ segment.
4. **Continuous State Warm-Start (Section 92):**  
   In genuine streaming environments, models maintain continuous online state representations. The internal weights and state buffers accumulated during the calibration and validation segments transfer continuously into the test segment, preventing artificial restart transients.

---

## 3. Explicit 16-Configuration Search Grids by Baseline (Section 79)

Every search grid is defined *a priori* across canonical, mathematically grounded dimensions:

### 3.1 Baseline B1: RZA-LMS Grid (16 Configurations)
- **Step size $\eta$:** $\{10^{-3}, 3 \times 10^{-3}, 10^{-2}, 3 \times 10^{-2}\}$ (4 values).
- **Shrinkage $\rho_{\text{za}}$:** $\{10^{-6}, 10^{-5}, 10^{-4}, 10^{-3}\}$ (4 values).
- **Total Configurations:** $4 \times 4 = 16$.

### 3.2 Baseline B2: CCN Grid (16 Configurations)
- **Readout learning rate $\eta_{\text{out}}$:** $\{10^{-3}, 3 \times 10^{-3}, 10^{-2}, 3 \times 10^{-2}\}$ (4 values).
- **Recurrent learning rate $\eta_{\text{rec}}$:** $\{10^{-4}, 10^{-3}\}$ (2 values).
- **Column capacity $C_{\max}$:** $\{1, 2\}$ (2 values).
- **Total Configurations:** $4 \times 2 \times 2 = 16$.

### 3.3 Baseline B3: MUSE-RNN Grid (16 Configurations)
- **Learning rate $\eta$:** $\{10^{-3}, 3 \times 10^{-3}, 10^{-2}, 3 \times 10^{-2}\}$ (4 values).
- **Growth multiplier $\gamma_{\text{grow}}$:** $\{1.5, 2.5\}$ (2 values).
- **Pruning threshold $\theta_{\text{prune}}$:** $\{10^{-3}, 10^{-2}\}$ (2 values).
- **Total Configurations:** $4 \times 2 \times 2 = 16$.

### 3.4 Baseline B4: Minimal GRU Grid (16 Configurations)
- **Learning rate $\eta$:** $\{10^{-4}, 10^{-3}, 3 \times 10^{-3}, 10^{-2}\}$ (4 values).
- **Weight decay / damping $\lambda$:** $\{0.90, 0.95, 0.99, 0.999\}$ (4 values).
- **Total Configurations:** $4 \times 4 = 16$.

### 3.5 Baseline B5: Online ESN Grid (16 Configurations)
- **Reservoir size $N_{\text{res}}$:** $\{10, 20\}$ (2 values).
- **Spectral radius $\rho(W_{\text{res}})$:** $\{0.85, 0.95\}$ (2 values).
- **Leak rate $\alpha$:** $\{0.3, 0.7\}$ (2 values).
- **Readout learning rate $\eta_{\text{out}}$:** $\{10^{-3}, 10^{-2}\}$ (2 values).
- **Total Configurations:** $2 \times 2 \times 2 \times 2 = 16$.

### 3.6 Baseline B6: Variable-Tap LMS Grid (16 Configurations)
- **Step size $\eta$:** $\{10^{-3}, 3 \times 10^{-3}, 10^{-2}, 3 \times 10^{-2}\}$ (4 values).
- **Tap leakage $\gamma_{\text{tap}}$:** $\{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$ (4 values).
- **Total Configurations:** $4 \times 4 = 16$.

### 3.7 Baseline B7: LRU Streaming Grid (16 Configurations)
- **State learning rate $\eta_s$:** $\{10^{-3}, 10^{-2}\}$ (2 values).
- **Readout learning rate $\eta_w$:** $\{10^{-3}, 3 \times 10^{-3}, 10^{-2}, 3 \times 10^{-2}\}$ (4 values).
- **State decay $\lambda$:** $\{0.90, 0.98\}$ (2 values).
- **Total Configurations:** $2 \times 4 \times 2 = 16$.

---

## 4. Hyperparameter Selection Objective (Sections 81–84)

Per Section 84, hyperparameter selection follows **Prediction Quality Subject to Declared Resource Ceilings**:
$$\theta^* = \arg\min_{\theta \in \Theta_{16}} \text{MSE}_{\text{cal}}(\theta) \quad \text{subject to} \quad \text{Mean\_FLOPs}(\theta) \le \text{FLOP\_Limit}_{\text{regime}}$$

In Regime R1 (Natural), the constraint is unbounded; in Regime R2 (Resource-Matched), configurations that exceed the resource ceiling are disqualified.

---

## 5. Formal Certification of Questions 10 & 11 (Sections 202 & 203)

- **Audit Question 10:** *Is hyperparameter tuning effort comparable across methods?*  
  **Audit Verdict:** **`YES`**. Every competitive baseline receives an identical search budget of 16 structured configurations over identical calibration intervals. Track B receives zero tuning effort, guaranteeing zero tuning advantage.
- **Audit Question 11:** *Are test intervals untouched by all model selection?*  
  **Audit Verdict:** **`YES`**. Final evaluation occurs exclusively on the final 70% test segment, which is completely quarantined during calibration.
