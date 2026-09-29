# PRA-01: Claim-by-Claim Adversarial Audit (Claims C1–C10)

**Audit ID:** PRA-01  
**Auditor:** Adversarial Literature Reviewer & Novelty Analyst  
**Date:** September 19, 2026  

---

## 1. Overview of Claim Audit Classification Standard

Per Section 45 and 46 of the audit protocol, candidate claims are classified under strict evidence thresholds:
- **`KNOWN`**: The mechanism is already published and established in identical mathematical or algorithmic form.
- **`CLOSE_PRECEDENT`**: The core principle is established in closely related architectures with minor domain differences.
- **`COMBINATION_ONLY`**: The individual components are well-known, but their specific operational combination addresses a distinct constraint.
- **`POSSIBLY_DISTINCT`**: No close precedent was found after exhaustive adversarial search across all 16 literature families. *(Does not imply legal patentability).*
- **`UNRESOLVED`**: Literature evidence is ambiguous or incomplete.

---

## 2. Claim-by-Claim Audit Table

| Claim ID | Claim Summary Description | Audit Status | Closest Discovered Precedent | Concrete Evidence & Overlap | Remaining Distinction | Confidence |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **C1** | Online sparse structural discovery under bounded compute. | **`COMBINATION_ONLY`** | Zero-Attracting LMS (ZA-LMS / RZA-LMS; Chen et al. 2009; Gu et al. 2009); Online Lasso (Angelosante et al. 2010). | Online $\ell_1$-penalized stochastic gradient descent is mathematically standard. ZA-LMS continuously drives inactive weights toward zero in streaming data. | Standard sparse LMS observes all $D$ inputs on every step ($O(D)$ FLOPs). Track B enforces a sub-linear compute budget ($O(K_{\max} + Q) \ll O(D)$) via budgeted probe screening. | **HIGH CONFIDENCE** |
| **C2** | Explicit candidate investigation / resource budgeting (Explore/Confirm probe bank). | **`CLOSE_PRECEDENT`** | Active Feature Acquisition (AFA; Saar-Tsechansky et al. 2009; Guney et al. 2025; Norcliffe et al. 2025); Sequential Probability Ratio Test (Wald 1945). | Gathering features sequentially under an exploration budget and validating them through multi-stage confirmation is well-established in budgeted sensing and statistical hypothesis testing. | AFA targets external sensor measurement costs in test-time inference. Track B applies probe budgeting to internal candidate filter weights under strict streaming FLOP ceilings. | **HIGH CONFIDENCE** |
| **C3** | Temporal candidate expansion into feature-lag structure. | **`KNOWN`** | Time-Delay Neural Networks (TDNN; Waibel et al. 1989); Sparse NARX Identification (Billings 2013); Variable-Tap LMS (Zhao et al. 2008). | Storing inputs in a delay buffer and testing delayed variables ($x_{j, t-d}$) is the foundation of nonlinear autoregressive modeling and variable-delay adaptive filters. | Track B integrates non-contiguous lag exploration into a sparse probe bank with age-normalized victim scoring. | **HIGH CONFIDENCE** |
| **C4** | Compact recurrent state introduced only when explicit history is insufficient. | **`CLOSE_PRECEDENT`** | Recurrent Cascade-Correlation (Fahlman 1991); Model order escalation in system identification (Ljung 1999). | Recurrent Cascade-Correlation starts with feedforward connections and adds self-recurrent hidden units only when feedforward residual error ceases to improve. | Fahlman's method trains in offline batch candidate-freezing phases. Track B discovers state necessity strictly online in a single streaming pass. | **HIGH CONFIDENCE** |
| **C5** | Online learned recurrent state without BPTT. | **`KNOWN`** | Real-Time Recurrent Learning (RTRL; Williams & Zipser 1989); SnAp (Menick et al. 2021). | Track B's forward sensitivity trace ($S_t = \lambda S_{t-1} + u_{t-1}$) is the exact mathematical specialization of Williams & Zipser's 1989 forward sensitivity equation to a 1D scalar recurrent state ($N=1$). | **Zero algorithmic novelty.** It is computationally cheap ($O(1)$) solely because state dimension is $d=1$. | **HIGH CONFIDENCE** |
| **C6** | Autonomous state birth / maturation / eviction. | **`CLOSE_PRECEDENT`** | MUSE-RNN (Das et al. 2019); SkipE-RNN (Das et al. 2020); Minimal Resource Allocation Network (MRAN; Kadirkamanathan & Niranjan 1993). | Dynamic node birth triggered by residual error and node eviction triggered by low contribution/significance over streaming data is fully established in MRAN and MUSE-RNN. | Track B introduces an explicit **probationary shadow window** (where candidate states train parameters in shadow before participating in primary predictions), directly addressing Lillo & Cheney's "Newborn Bottleneck". | **HIGH CONFIDENCE** |
| **C7** | Dynamic choice between cheaper linear state and selective gated state. | **`POSSIBLY_DISTINCT`** | Multi-Model Adaptive Control (MMAC; Narendra & Balakrishnan 1997); Evolving Takagi-Sugeno (eTS; Angelov & Filev 2004). | MMAC runs multiple parallel models and switches based on residuals. eTS combines linear sub-models with non-linear fuzzy antecedent gates. | Track B implements a sequential parsimony order: linear recurrence is evaluated first; gated recurrence is instantiated only if linear probation fails ($15\%$ threshold test). | **HIGH CONFIDENCE** |
| **C8** | Quiescent memory retained using long-horizon structural relevance ($C \times O_{\text{struct}}$). | **`POSSIBLY_DISTINCT`** | Balanced Truncation / Hankel Singular Values (Moore 1981); AIRE-Prune (Padhy et al. 2026); LAST (Padhy et al. 2025). | Evaluating recurrent states by the product of controllability and observability ($C \times O$) is the classical basis of balanced model reduction (Moore 1981) and modern SSM state pruning (AIRE-Prune 2026). | Prior methods apply $C \times O$ for offline post-training pruning. Track B adapts the principle for **online causal retention during silent event gaps** (preventing premature eviction during Poisson quiescence where observable activity $s_t = 0$). | **HIGH CONFIDENCE** |
| **C9** | Positive obsolescence evidence required before state death ($O_{\text{obs}}$). | **`POSSIBLY_DISTINCT`** | Sequential hypothesis testing with indifference zone (Wald 1945); Concept drift warning/detection confirmation (Gama et al. 2004). | Requiring confirmation evidence across a temporal window before triggering structural changes exists in drift detection. | Track B couples an empirical asymmetric loss penalty ($C_{\text{FE}} / C_{\text{FR}} > 300:1$) with an explicit zero-excitation accumulator ($|x_t| < \epsilon \land |\hat{y}| < \epsilon$) and hysteresis thresholding to prevent premature eviction of silent states. | **HIGH CONFIDENCE** |
| **C10** | Same general lifecycle principle applied across observable and internal structure. | **`POSSIBLY_DISTINCT`** | Structural plasticity frameworks (Kong & Sutton 2026; Jia & Zhou 2026; Chen et al. 2009). | Prior methods treat either observable features (sparse filters) OR hidden neurons (MRAN, MUSE-RNN), but do not unify both under a shared resource governance lifecycle. | Track B unifies features, feature-lag pairs, and recurrent states under an identical lifecycle: *Candidate Probing $\to$ Incubation/Probation $\to$ Active Promotion $\to$ Retention Utility $\to$ Eviction/Reclaim*. | **HIGH CONFIDENCE** |

---

## 3. Summary of Claim Vulnerability

- **Clearly Known / No Novelty**:
  - `C5` (Online recurrent credit assignment via forward sensitivity) is **100% KNOWN** as RTRL (1989) specialized to scalar state.
  - `C3` (Temporal lag expansion) is **KNOWN** from TDNN and NARX literature.
- **Close Precedent Found**:
  - `C2` (Candidate probing under budget) is established in Active Feature Acquisition.
  - `C4` (Recurrent state added when feedforward fails) is established in Recurrent Cascade-Correlation.
  - `C6` (Autonomous state birth and eviction) is established in MRAN (1993) and MUSE-RNN (2019).
- **Recombinations / Possibly Distinct Elements**:
  - `C1` (Online sparse learning under sub-linear probe budget).
  - `C7` (Parsimonious linear-first vs gated recurrence hierarchy).
  - `C8` (Two-timescale structural observability protecting quiescent memory).
  - `C9` (Positive obsolescence evidence accumulator under asymmetric loss).
  - `C10` (Unified structural lifecycle across observable and hidden representations).
