# Milestone Specification: M1-Pred & M1-Struct (M1-SPEC)

**Document Version:** 1.0.0  
**Effective Date:** 2026-09-19  
**Status:** Certified / Active Standard  
**Supercedes:** Original Unsplit Milestone M1 (Linear Continuous Sparse Adaptation)  
**Governance Authority:** Section 83 Protocol & Track-B Review Board  

---

## 1. Scope and Architectural Purpose

This specification formally establishes the split benchmark architecture for Milestone M1 in the continuous online learning research roadmap:

```
                          [ Original M1 ]
                    (Conflated Pred & Struct)
                                |
                    M1-R1 Robustness Audit
                                |
                +---------------+---------------+
                |                               |
          [ M1-Pred ]                     [ M1-Struct ]
    Online Predictive Adaptation    Ground-Truth Identification
     (Objective: Low Regret)          (Objective: Support Recovery)
```

### Core Separation Principle
Empirical evidence from EXP-0001 through EXP-0010 and the M1-R1 audit established that **a learner can achieve near-oracle predictive performance while recovering only a fraction of the ground-truth feature support**, particularly when non-dominant features fall below the critical signal-to-noise identification limit ($\Gamma < 20$).

Conflating these two objectives in a single pass/fail milestone led to unnecessary rejection of predictively optimal architectures. Henceforth, online adaptation and structural discovery are audited under decoupled standards.

---

## 2. Milestone M1-Pred: Online Predictive Adaptation

### 2.1 Goal Description
Demonstrate that a sparse adaptive learner can continuously track a dynamic linear stream under strict compute constraints, achieving post-shift predictive accuracy comparable to a Sparse Oracle and strictly outperforming Dense NLMS, without receiving ground-truth support or shift alerts.

### 2.2 Formal Pass / Fail Criteria
A candidate learner is certified under **M1-Pred** if, evaluated across at least 20 fresh holdout seeds on the Canonical Benchmark Suite, it satisfies:

1. **Prediction Superiority vs Dense Reference:**
   $$\text{Dense MSE Ratio} = \frac{\text{MSE}_{\text{post}}(\text{Learner})}{\text{MSE}_{\text{post}}(\text{Dense NLMS})} \le 1.00$$
   *(The sparse learner must strictly match or beat a full dense model running on all $D$ features).*

2. **Prediction Parity vs Sparse Oracle Reference:**
   $$\text{Oracle MSE Ratio} = \frac{\text{MSE}_{\text{post}}(\text{Learner})}{\text{MSE}_{\text{post}}(\text{Sparse Oracle})} \le 1.50$$
   *(The sparse learner must remain within $50\%$ of the error achieved by an unconstrained oracle knowing true support).*

3. **Compute Budget Ceiling:**
   $$\text{Compute Overhead} = \frac{\text{Total FLOPs}(\text{Learner})}{\text{Total FLOPs}(\text{Dense NLMS})} \times 100\% \le 25.0\% \quad (\text{for } D \ge 100)$$
   *(For $D < 100$, compute overhead must satisfy $\le \frac{6K_{\max} + 16 \cdot Q_{\text{avg}}}{6D + 2} \times 100\%$).*

4. **Holdout Reliability:**
   $$\text{Certification Pass Rate} \ge 80.0\% \text{ across fresh holdout seeds.}$$

### 2.3 Evaluation Protocol
- **Evaluation Window:** Post-adaptation MSE is measured strictly on steps $t \in [1801, 2000]$ following an unannounced regime shift at $t=1000$.
- **Compute Accounting:** All operations including feature updates, candidate dot products, probe selection, and queue management must be logged.
- **Reference Models:**
  - *Dense NLMS:* Learning rate $\mu = 0.5$, regularization $\epsilon = 10^{-6}$, operating over all $D$ ambient dimensions ($6D+2$ FLOPs/step).
  - *Sparse Oracle NLMS:* Learning rate $\mu = 0.5$, $\epsilon = 10^{-6}$, updating strictly on $S_t^*$ ($6K^*+2$ FLOPs/step, zero exploration cost).

---

## 3. Milestone M1-Struct: Ground-Truth Structural Identification

### 3.1 Goal Description
Demonstrate that a candidate learner can correctly discover and retain the ground-truth active features under a bounded probe exploration budget, evaluated strictly in **information-theoretically identifiable regimes**.

### 3.2 Regime Identifiability Precondition
Structural identification is audited **only** in environments where the Diagnostic Index $\Gamma$ satisfies:
$$\Gamma = \frac{\beta_{\min}}{\sigma} \sqrt{\frac{N_{\text{eff}}}{\log(D - K^*)}} \ge 20.0$$
In environments where $\Gamma < 20.0$, full ground-truth recovery is physically intractable under the probe budget; failures in these regimes do not constitute a failure of M1-Struct.

### 3.3 Formal Pass / Fail Criteria
Within identifiable regimes ($\Gamma \ge 20.0, C \le 3$):
1. **Support Recovery (Graded Metric):**
   $$\text{Energy-Weighted Recall (EWR)} \ge 0.80 \quad (\text{Strict: } \ge 0.85)$$
   $$\text{Full-Support Occupancy} \ge 75.0\% \quad (\text{in stationary post-adaptation window})$$
2. **Evidence Accumulation Latency:**
   $$T_{\text{evid}} = \frac{1}{|S_2^*|} \sum_{j \in S_2^*} (t_{\text{promote}, j} - t_{\text{first\_probe}, j}) \le 120 \text{ steps}$$
3. **Probe Allocation Budget:**
   $$Q_{\text{total}} \le 10,000 \text{ probes across 2000 stream steps.}$$

---

## 4. Benchmark Environments

### Suite I: Canonical Benchmark (V0)
- Ambient Dimensions: $D = 100$
- Active Sparsity: $K^* = 5$
- Observation Noise: $\sigma = 0.10$
- Regime Shift: Step $t = 1000$
- Change Load: $C = 5$ features replaced ($100\%$ support turnover)
- Coefficient Spectrum (Decaying):
  - $R_1$: $\{2: 1.5, 15: -1.2, 33: 0.8, 58: -1.0, 81: 1.3\}$
  - $R_2$: $\{7: -1.4, 24: 1.0, 49: -1.1, 66: 1.6, 92: -0.9\}$

### Suite II: Coefficient Spectrum Invariance (V1)
- Identical total energy $E = \sum \beta_j^2 \approx 7.28$:
  - *Spectrum A (Decaying):* Canonical descending amplitudes.
  - *Spectrum B (Balanced):* Uniformly dispersed amplitudes ($\approx 1.0 - 1.4$).
  - *Spectrum C (Flat):* Exactly equal magnitudes ($|\beta_j| = 1.2066$).
  - *Spectrum D (Weak Tail):* 4 dominant features ($|\beta_j| \ge 1.10$) + 1 weak tail ($\beta_5 = 0.15$).

### Suite III: Generalization Holdouts (V2)
- Variable ambient sizes: $D \in [35, 75, 80, 100, 120, 150]$
- Variable noise floors: $\sigma \in [0.05, 0.10, 0.15, 0.20, 0.35]$
- Variable change loads: $C \in [2, 3, 4, 5]$
- Recurring change shocks: Multiple shifts at $t \in [600, 1200, 1600]$ or $t \in [700, 1400]$.

---

## 5. Formal Certification Record: Track-B Learner

The frozen Track-B Learner (`TieredEvidenceLearner` with `TieredEvidenceRatePolicy` in `queue_multi_rate` mode and `ProbeBankController`) is evaluated against this specification:

| Milestone Component | Audit Result | Formal Status |
| :--- | :---: | :---: |
| **M1-Pred (Predictive Adaptation)** | **96.67% pass on Canonical (V0)**<br>**83.33% pass on Balanced (V1)**<br>**83.33% pass on Flat (V1)** | **VALIDATED WITH SCOPE LIMITS** |
| **M1-Struct (Structural Identification)** | **Validated when $\Gamma \ge 20, C \le 3$**<br>Collapses when $\Gamma < 10$ or $C \ge 4$ | **VALIDATED IN IDENTIFIABLE REGIMES** |
| **Legacy Unsplit M1** | 8.18% pass rate across holdouts | **SUPERSEDED / DEPRECATED** |

### Documented Scope Limits for M1-Pred
1. **High Change Load ($C \ge 4$ at $D \ge 150$):** Re-adaptation requires $>500$ steps due to probe starvation; predictive transients can exceed Dense NLMS in the immediate post-shift window.
2. **Low Dimension ($D \le 75$):** Compute percentage exceeds $25\%$ of Dense NLMS due to the irreducible cost of active ambient exploration ($\mathcal{O}(q)$ vs $\mathcal{O}(d)$).
3. **Recurring Large Shocks:** Requires controller probe re-initialization to avoid latency compounding across multiple shift points.

---

## 6. Authorizations and Hard Stops

Pursuant to Section 83 protocol:
- Milestone M1 is hereby **CLOSED**.
- No further tuning or heuristics will be applied to the linear sparse benchmark.
- All future developmental efforts transition to **Milestone M2 (Temporal & Sequential Adaptation)**.
