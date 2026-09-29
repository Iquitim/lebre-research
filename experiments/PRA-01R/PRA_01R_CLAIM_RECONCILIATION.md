# PRA-01R: Claim-by-Claim Prior-Art Reconciliation (Claims C1–C10)

**Document ID:** PRA-01R-CLAIMS  
**Author:** Skeptical Literature Reconciler & Pre-Publication Novelty Auditor  
**Date:** September 19, 2026  
**Status:** RECONCILIATION COMPLETE — DOWNGRADES APPLIED  
**Governing Rules:** Claim Downgrade Rule (Section 52), No-Novelty Cap (Section 53), CBP Maturation Precedent (Section 15), RCC Birth Precedent (Section 21)  

---

## 1. Governance and Classification Standard

In strict compliance with the PRA-01R governing protocol:
- **No-Novelty Rule (Section 53):** No claim may be classified as `NOVEL`. The strongest permissible status is `POSSIBLY_DISTINCT`.
- **Symmetric Downgrade Rule (Section 52):** If independent prior-art lineages (RSONN, CCN, CBP, ACESN, RCC, MRAN, Variable-Order) provide closer precedents or invalidate novelty premises, the claim MUST be downgraded immediately without defending previous audit labels.
- **Continual Backprop Rule (Section 15):** Unit maturation thresholds and utility-based replacement are classified as **`KNOWN`**.
- **Cascade-Correlation Rule (Section 21):** Recurrent state birth triggered by residual error failure is classified as **`KNOWN`**.

### Standard Classification Levels:
1. **`KNOWN`**: The mathematical or algorithmic mechanism exists in published prior art.
2. **`CLOSE_PRECEDENT`**: Close mathematical or architectural analogues exist; differences are domain-specific or minor parameterizations.
3. **`COMBINATION_ONLY`**: Individual components are known, but their integrated operational combination addresses an unaddressed interaction constraint.
4. **`POSSIBLY_DISTINCT`**: No integrated precedent found in literature for this specific structural mechanism or governance rule. *(Subject to verification via external benchmarking; does not imply legal patentability).*
5. **`UNRESOLVED`**: Evidence remains ambiguous.

---

## 2. Claim-by-Claim Reconciliation Table

| Claim ID | Claim Summary Description | PRA-01 Status | Independent Review Challenge | New Primary Evidence | Reconciled Status | Confidence | Closest Discovered Precedent |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :--- |
| **C1** | Online sparse parameter adaptation under bounded compute budget. | `COMBINATION_ONLY` | Variable-tap LMS (Zhao 2008) and Sparse Online LMS already bound active parameters. | Online $\ell_1$/zero-attracting LMS updates every parameter ($O(D)$) even if weights are zero. | **`COMBINATION_ONLY`** | **HIGH** | RZA-LMS (Chen 2009); Variable-Tap LMS (Zhao 2008). |
| **C2** | Explicit candidate investigation / resource budgeting (probe bank). | `CLOSE_PRECEDENT` | Active Feature Acquisition (AFA) and Multi-Armed Bandits already allocate budgeted probes. | AFA (Norcliffe 2025; Guney 2025) budgets external sensor measurement costs, not internal streaming filter taps. | **`CLOSE_PRECEDENT`** | **HIGH** | Active Feature Acquisition (Saar-Tsechansky 2009; Guney 2025); SPRT (Wald 1945). |
| **C3** | Temporal candidate expansion into feature-lag structure ($x_{j, t-d}$). | `KNOWN` | Variable-tap LMS and sparse NARX models have used delayed taps for decades. | Variable-tap LMS (Zhao 2008; Zhang 2014) dynamically adapts tap length based on MSE gradients. | **`KNOWN`** | **CERTAIN** | Variable-Tap LMS (Zhao 2008); TDNN (Waibel 1989); Sparse NARX (Billings 2013). |
| **C4** | Compact recurrent state introduced when explicit history is insufficient. | `CLOSE_PRECEDENT` | Recurrent Cascade-Correlation (RCC) explicitly allocates recurrent units when feedforward error plateaus. | Fahlman (1991) defines candidate unit creation triggered by residual error plateau. | **`KNOWN`** *(Downgraded)* | **HIGH** | Recurrent Cascade-Correlation (Fahlman 1991); Model-order escalation (Ljung 1999). |
| **C5** | Online learned recurrent state without BPTT via forward sensitivity. | `KNOWN` | Columnar-Constructive Networks (CCN; Javed et al. 2023) use identical scalar forward sensitivity RTRL. | CCN establishes exact $O(1)$ RTRL for scalar units. Identical to Williams & Zipser (1989) for $N=1$. | **`KNOWN`** | **CERTAIN** | RTRL (Williams & Zipser 1989); CCN (Javed, Shah, Sutton, White 2023). |
| **C6** | Autonomous state birth, maturation, and utility eviction. | `CLOSE_PRECEDENT` | Continual Backprop (Dohare 2021, 2024) has unit age, maturity threshold $m$, and utility replacement. MRAN (1999) has birth/pruning/maturity. | CBP explicitly introduces maturity threshold $m$ to protect newborn units before utility eviction. | **`KNOWN`** *(Downgraded)* | **HIGH** | Continual Backpropagation (Dohare et al. 2021, 2024); MRAN (Lu et al. 1999); MUSE-RNN (Das 2019). |
| **C7** | Linear-first vs gated parsimonious state-type hierarchy. | `POSSIBLY_DISTINCT` | Multi-Model Adaptive Control (MMAC) and Evolving Neuro-Fuzzy (eTS) combine linear and nonlinear models. | MMAC runs parallel competitive models; eTS partitions space. Neither evaluates a parsimonious linear candidate in shadow before escalating to gated recurrence. | **`POSSIBLY_DISTINCT`** | **MEDIUM-HIGH** | Multi-Model Adaptive Control (Narendra 1997); Evolving Takagi-Sugeno (Angelov 2004). |
| **C8** | Quiescent memory retention using two-timescale structural relevance ($C \times O_{\text{struct}}$). | `POSSIBLY_DISTINCT` | Balanced truncation (Moore 1981), AIRE-Prune (Padhy 2026), and LAST (Padhy 2025) use controllability $\times$ observability. | Metric ($C \times O$) is KNOWN from control/SSM pruning. But its use for **online streaming quiescent preservation** (protecting silent memory when $s_t=0$) is distinct from offline pruning. | **`POSSIBLY_DISTINCT`** *(Lifecycle combination)* | **HIGH** | Balanced Truncation (Moore 1981); AIRE-Prune (Padhy 2026); LAST (Padhy 2025). |
| **C9** | Positive obsolescence evidence before state death under asymmetric loss. | `POSSIBLY_DISTINCT` | Sequential change detection, CUSUM, Page-Hinkley, and drift detection with confirmation windows (Gama 2004). | Drift detectors confirm distribution shift, but do not integrate an asymmetric loss ratio ($C_{\text{FE}}/C_{\text{FR}} > 300:1$) with confirmed zero-excitation accumulation to govern physical state death. | **`POSSIBLY_DISTINCT`** | **MEDIUM-HIGH** | Concept Drift Confirmation (Gama 2004); CUSUM (Page 1954); SPRT (Wald 1945). |
| **C10** | Unified structural lifecycle across observable inputs, lags, and recurrent states. | `POSSIBLY_DISTINCT` | Structural plasticity (Jia & Zhou 2026; Kong & Sutton 2026); RSONN (Han 2019). | Existing literature adapts *either* input weights *or* hidden neurons. None executes a unified Probe $\to$ Mature $\to$ Promote $\to$ Evict lifecycle jointly governing inputs, lags, and states under a single budget. | **`POSSIBLY_DISTINCT`** | **HIGH** | Structural Plasticity (Kong & Sutton 2026); RSONN (Han 2019); MUSE-RNN (Das 2019). |

---

## 3. In-Depth Technical Analysis of Critical Claims

### 3.1 Reconciliation of Claim C7: Parsimonious State-Type Hierarchy
- **Claim Formulation:** Evaluating candidate temporal structure through a sequential parsimony order: evaluate cheap linear recurrence first ($s_t = \lambda s_{t-1} + u_{t-1}$); escalate to selective gated recurrence ($s_t = f s_{t-1} + i \tilde{s}_t$) only if the linear candidate fails probationary error reduction by an empirical margin ($\ge 15\%$).
- **Literature Scrutiny:**
  - *Multi-Model Adaptive Control (MMAC; Narendra & Balakrishnan 1997):* Instantiates a bank of pre-existing linear and nonlinear controllers in parallel, weighting outputs via Bayesian likelihood. MMAC runs all models simultaneously; it does not follow a constructive, parsimonious escalation hierarchy.
  - *Evolving Takagi-Sugeno (eTS; Angelov & Filev 2004):* Combines linear consequent polynomials with nonlinear fuzzy antecedent membership functions. The structure is fixed in its hybrid nature, not parsimoniously escalated from linear to non-linear.
  - *Neural Architecture Search (NAS / DARTS; Liu et al. 2018):* Evaluates mixed candidate operations in supernets, but requires heavy offline bi-level optimization over static datasets.
- **Reconciled Decision:** **`POSSIBLY_DISTINCT`**.
- **Critical Assessment:** While the heuristic principle "try linear first, escalate to nonlinear" is an established engineering maxim in system identification, its formal operationalization as an autonomous, single-pass probationary escalation test between scalar linear and scalar gated states is not found in published streaming recurrent learners.

### 3.2 Reconciliation of Claim C8: Quiescent Memory Retention via Two-Timescale Relevance
- **Claim Formulation:** Preserving dormant recurrent states during extended silent gaps (where instantaneous state activation $s_t \approx 0$ and instantaneous prediction contribution $\hat{y}_{rec} \approx 0$) by evaluating structural relevance via decoupled two-timescale observability:
  $$O_{\text{struct}, t} = \beta_{slow} O_{\text{struct}, t-1} + (1 - \beta_{slow}) |w_{out, t}| \cdot \mathcal{E}_{\text{impulse}}$$
  where $\mathcal{E}_{\text{impulse}}$ captures the dynamic transfer capability rather than instantaneous magnitude.
- **Literature Scrutiny:**
  - *Balanced Truncation & Hankel Singular Values (Moore 1981):* Classical linear systems theory defines state importance by the product of controllability and observability Gramians ($W_c W_o$).
  - *SSM State Pruning (AIRE-Prune; Padhy et al. 2026; LAST; Padhy et al. 2025):* AIRE-Prune explicitly computes controllability and observability metrics to prune state dimensions in pre-trained state-space models. However, AIRE-Prune is an **offline, post-training, non-causal** batch algorithm.
  - *Continual Backprop & MUSE-RNN:* CBP defines utility as $|w_{out}| \cdot \mathbb{E}[|h|]$; MUSE-RNN uses $|h_t| \cdot |w_{out}|$. Both metrics collapse to zero when $h_t \approx 0$. In event-driven Poisson tasks, both CBP and MUSE-RNN evict the state during the silent gap, causing catastrophic forgetting of the stored event.
- **Reconciled Decision:** **`POSSIBLY_DISTINCT`** (at the online lifecycle combination level).
- **Critical Distinction:** The importance metric ($C \times O$) is **`KNOWN`**. The distinctiveness lies strictly in its causal, two-timescale application to prevent premature eviction during quiescent event gaps in online streams.

### 3.3 Reconciliation of Claim C9: Positive Obsolescence Evidence Under Asymmetric Cost
- **Claim Formulation:** Requiring positive statistical evidence of obsolescence ($O_{\text{obs}, t} \ge \theta_{\text{obs}}$) before state death, rather than evicting immediately upon utility dropping below an instantaneous threshold:
  $$O_{\text{obs}, t} = \begin{cases} O_{\text{obs}, t-1} + 1, & \text{if } |x_{obs, t}| < \epsilon_x \land |\hat{y}_t - y_t| < \epsilon_e \land U_t < \theta_{\text{evict}} \\ 0, & \text{otherwise} \end{cases}$$
  coupled with a confirmation hysteresis window calibrated against the empirical asymmetric loss ratio ($C_{\text{Premature\_Eviction}} / C_{\text{Stale\_Retention}} > 300:1$).
- **Literature Scrutiny:**
  - *Concept Drift Detection (DDM, EDDM; Gama et al. 2004):* Introduces a "warning level" and "drift level" based on binomial confidence intervals before resetting models.
  - *Online Pruning Literature (MRAN, RSONN, Continual Backprop):* All existing online pruning methods evict units whenever instantaneous utility or a short sliding-window average falls below a threshold. None requires positive evidence that the input channel has permanently ceased excitation while predictions remain accurate.
- **Reconciled Decision:** **`POSSIBLY_DISTINCT`**.
- **Critical Assessment:** The concept of confirmation patience is established in drift detection, but its specific structural formulation as an explicit zero-excitation counter protecting high-replacement-cost recurrent memory against asymmetric eviction failure is distinct.

### 3.4 Reconciliation of Claim C10: Unified Structural Lifecycle Across Representational Tiers
- **Claim Formulation:** Executing a single unified lifecycle (*Probe $\to$ Mature/Probation $\to$ Active Promotion $\to$ Retention Utility $\to$ Obsolescence Confirmation $\to$ Eviction $\to$ Resource Reclamation*) across three distinct representational tiers:
  1. Observable spatial input features ($x_j$);
  2. Temporal lag features ($x_{j, t-d}$);
  3. Internal recurrent hidden states ($s_t$);
  under an overarching rigid sub-linear FLOP budget ($O(K_{\max} + Q) \ll O(D)$).
- **Literature Scrutiny:**
  - *RSONN & MUSE-RNN:* Adapt recurrent hidden nodes, but assume static, dense input connectivity.
  - *Sparse LMS & Online Lasso:* Adapt input feature sparsity, but possess no concept of temporal lag discovery or internal recurrent state generation.
  - *Variable-Tap LMS:* Adapts FIR tap length, but does not discover sparse spatial inputs or generate recurrent states.
  - *Continual Backprop:* Replaces feedforward neurons under fixed capacity, without input screening or temporal lag adaptation.
- **Reconciled Decision:** **`POSSIBLY_DISTINCT`**.
- **Critical Assessment:** No single published system unites sparse input selection, temporal lag discovery, and recurrent state birth/death under an integrated resource-budgeted lifecycle.

---

## 4. Reconciled Claim Vulnerability Summary

### 4.1 Claims Permanently Invalidate / Classified as KNOWN:
- **`C3` (Temporal Lag Expansion):** **`KNOWN`** (TDNN, Waibel 1989; Variable-Tap LMS, Zhao 2008).
- **`C4` (Recurrent State Birth from Residual Failure):** **`KNOWN`** (Recurrent Cascade-Correlation, Fahlman 1991).
- **`C5` (Online Recurrent Forward Sensitivity / Credit Assignment):** **`KNOWN`** (RTRL, Williams & Zipser 1989; CCN, Javed et al. 2023).
- **`C6` (Maturation Windows and Utility-Based Replacement):** **`KNOWN`** (Continual Backpropagation, Dohare et al. 2021, 2024; MRAN, Lu et al. 1999).

> [!WARNING]
> **MANDATORY GOVERNANCE RESTRICTION:**  
> Claims C3, C4, C5, and C6 must **NEVER** be described as novel, unique, or proprietary in any future paper, report, or specification. They are established foundational techniques in the literature.

### 4.2 Claims Surviving as POSSIBLY_DISTINCT:
- **`C7` (Parsimonious Linear-First vs Gated Recurrence Hierarchy):** Survives as possibly distinct in its autonomous single-pass shadow escalation test.
- **`C8` (Two-Timescale Structural Relevance for Quiescent Preservation):** Survives at the lifecycle integration level (protecting silent memory during Poisson event gaps).
- **`C9` (Positive Obsolescence Evidence Under Asymmetric Loss):** Survives in its specific confirmation accumulator preventing high-cost premature eviction.
- **`C10` (Unified Resource Lifecycle Across Features, Lags, and States):** Survives as the primary architectural claim.

---

## 5. Conclusion of Claim Reconciliation

The independent literature review has successfully clarified the boundary between established prior art and potential architectural distinctiveness. By formally downgrading C4 and C6 to **`KNOWN`**, Track B's intellectual scope is sharpened: it does not claim to have invented state birth, state eviction, maturation, or scalar RTRL. 

Its potential contribution rests strictly on Claims **C7–C10**: the unified, resource-governed integration that solves the joint problem of sparse input selection, temporal lag promotion, and quiescent-protected recurrent memory under hard compute ceilings.
