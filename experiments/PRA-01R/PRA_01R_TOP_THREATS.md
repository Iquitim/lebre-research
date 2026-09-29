# PRA-01R: Prior-Art Top Threats & Threat Matrix Re-Ranking

**Document ID:** PRA-01R-THREATS  
**Author:** Skeptical Literature Reconciler & Adversarial Novelty Auditor  
**Date:** September 19, 2026  
**Status:** RECONCILIATION COMPLETE — THREATS RE-RANKED  
**Governing Standard:** Multi-Dimensional Threat Assessment (Sections 47, 48, 54)  

---

## 1. Executive Summary of Threat Landscape

Following the integration of eight independent prior-art lineages into the PRA-01 baseline, the overall threat landscape has shifted from general skepticism toward specific, highly focused technical precedents. 

The audit reveals that **no single paper implements the full Track-B architecture**, but several papers dominate individual sub-problems. In particular, credit assignment (RTRL) and maturation/utility-based replacement are completely preempted by **CCN (Javed et al. 2023)** and **Continual Backprop (Dohare et al. 2021, 2024)**, respectively.

---

## 2. Category-by-Category Threat Champions (Section 54)

Per Section 54 of the governing protocol, the primary threat champions across key architectural dimensions are formally identified:

### 2.1 Biggest Overall Architectural Threat: **MUSE-RNN (Das et al. 2019)**
- **Why:** MUSE-RNN remains the closest single published system to Track B’s recurrent core. It operates in a strictly online, single-pass streaming regime without task labels, dynamically allocating recurrent hidden nodes based on residual error spikes and evicting under-performing nodes based on magnitude heuristics.
- **Vulnerability of Track B:** If an adversarial reviewer ignores input sparsity and quiescent memory preservation, they will classify Track B as an incremental modification of MUSE-RNN.
- **Track B Defense Boundary:** MUSE-RNN relies on dense input connections ($O(D \cdot N)$), lacks probationary shadow validation (causing newborn instability), collapses in quiescent Poisson regimes (annihilating silent state memory), and has no concept of input feature/lag discovery.

### 2.2 Biggest Online-Credit Threat: **Columnar-Constructive Networks (CCN; Javed et al. 2023)**
- **Why:** CCN proves that restricting recurrent units to 1D scalar self-connections renders exact Real-Time Recurrent Learning (RTRL) computationally tractable at $O(1)$ per unit, with zero gradient approximations or truncation artifacts.
- **Impact:** Completely invalidates any attempt to claim mathematical novelty for Track B's forward sensitivity trace ($S_t = \lambda S_{t-1} + u_{t-1}$). Track B’s credit assignment is mathematically identical to CCN and Williams & Zipser (1989).

### 2.3 Biggest Maturation and Utility Threat: **Continual Backpropagation (CBP; Dohare et al. 2021, 2024)**
- **Why:** Continual Backprop explicitly formalizes the twin concepts of (1) **unit utility** ("structure must pay rent or be evicted/re-initialized") and (2) **unit age and maturity threshold** ($m$), protecting newly initialized units from premature eviction while their weights adapt.
- **Impact:** Eliminates the possibility of claiming novelty for probationary maturation or utility-driven unit replacement. These principles are now canonical in continual learning.

### 2.4 Biggest State-Pruning Threat: **MRAN (Lu, Sundararajan et al. 1999) & AIRE-Prune (Padhy et al. 2026)**
- **Why:** MRAN pioneered sliding-window contribution pruning with explicit variance thresholds in online streaming data. AIRE-Prune formalized controllability $\times$ observability ($C \times O$) metrics for pruning state dimensions.
- **Impact:** Proves that both empirical contribution pruning (MRAN) and balanced-truncation state importance (AIRE-Prune) have extensive historical and modern precedents.

### 2.5 Biggest Recurrence and Growth Threat: **Recurrent Cascade-Correlation (RCC; Fahlman 1991) & RSONN (Han & Qiao 2013, 2019)**
- **Why:** Fahlman established in 1991 that recurrent units should be added precisely when feedforward residual error stops improving. RSONN demonstrated online recurrent node creation and sensitivity-based pruning in dynamic system identification.
- **Impact:** Eradicates any claim that error-triggered recurrent allocation is novel.

### 2.6 Biggest Adaptive-Capacity Threat: **Adaptive-Capacity ESN (ACESN; 2026)**
- **Why:** ACESN dynamically scales effective recurrent capacity in response to streaming error demand.
- **Impact:** Preempts high-level marketing language claiming that "dynamically matching recurrent capacity to task demand" is a new concept.

---

## 3. Qualitative Scoring Across 12 Threat Dimensions (Sections 47 & 48)

Candidates are evaluated across twelve dimensions:
- **T1:** Structural Growth (dynamic allocation of parameters/nodes)
- **T2:** Structural Pruning (dynamic removal/eviction of parameters/nodes)
- **T3:** Recurrence (internal feedback states / temporal memory)
- **T4:** Strictly-Online Learning (continuous streaming, no mini-batches, no epochs)
- **T5:** Online Parameter Learning (adapting weights online simultaneously)
- **T6:** State Birth (spawning recurrent state from temporal error failure)
- **T7:** State Death (permanent eviction and physical memory deallocation)
- **T8:** Maturation / Probation (protecting new units during initialization)
- **T9:** Quiescent Retention (protecting silent states during zero-excitation gaps)
- **T10:** Resource Budgeting (rigid sub-linear operational ceilings)
- **T11:** Sparse Observable Structure (probing and discovering sparse inputs $x_j$)
- **T12:** Unified Lifecycle (governing inputs, lags, and states identically)

### 3.1 12-Dimensional Threat Evaluation Matrix

| Candidate System | Threat Level | T1 Growth | T2 Prune | T3 Recur | T4 Online | T5 Param | T6 Birth | T7 Death | T8 Mature | T9 Quiescent | T10 Budget | T11 Sparse | T12 Unified |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track B (Target)** | **REF** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** |
| **MUSE-RNN** (Das 2019) | **CRITICAL** | YES | YES | YES | YES | PARTIAL | YES | YES | NO | NO | NO | NO | NO |
| **CCN** (Javed 2023) | **CRITICAL** | YES | NO | YES | YES | YES | YES | NO | NO | NO | PARTIAL | NO | NO |
| **Continual Backprop** (Dohare 2024) | **HIGH** | PARTIAL | PARTIAL | NO | YES | YES | NO | NO | YES | NO | NO | PARTIAL | NO |
| **RSONN** (Han & Qiao 2019) | **HIGH** | YES | YES | YES | YES | YES | YES | YES | NO | NO | NO | NO | NO |
| **SkipE-RNN** (Das 2020) | **HIGH** | NO | NO | YES | YES | PARTIAL | NO | NO | NO | NO | NO | NO | NO |
| **MRAN** (Lu 1999) | **HIGH** | YES | YES | NO | YES | YES | YES | YES | YES | NO | NO | NO | NO |
| **Recurrent Cascade-Correlation** | **MEDIUM** | YES | NO | YES | NO | NO | YES | NO | NO | NO | NO | NO | NO |
| **ACESN** (2026) | **MEDIUM** | PARTIAL | PARTIAL | YES | YES | NO | NO | NO | NO | NO | NO | NO | NO |
| **AIRE-Prune / LAST** (Padhy 2026) | **MEDIUM** | NO | YES | YES | NO | NO | NO | YES | NO | PARTIAL | NO | NO | NO |
| **SOFNN / eTS** (Angelov 2004) | **MEDIUM** | YES | YES | PARTIAL | YES | YES | YES | YES | NO | NO | NO | NO | NO |
| **Variable-Order LMS** (Zhao 2008) | **MEDIUM** | YES | YES | NO | YES | YES | NO | NO | NO | NO | NO | PARTIAL | NO |

---

## 4. Re-Ranked Prior-Art Threat Hierarchy

Based on comprehensive technical reconciliation, the candidate systems are stratified into four rigorous threat tiers:

```
+-------------------------------------------------------------------------+
| TIER 1: CRITICAL THREATS (Must be benchmarked or explicitly cited)     |
| 1. MUSE-RNN (Das et al. 2019)       -- Nearest online recurrent growth  |
| 2. CCN (Javed et al. JMLR 2023)     -- Exact scalar RTRL credit baseline|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| TIER 2: HIGH THREATS (Direct algorithmic precursors to key mechanisms)  |
| 3. Continual Backprop (Nature 2024) -- Preempts maturation & utility    |
| 4. RSONN (IEEE TNNLS 2019)          -- Sensitivity-based birth & death  |
| 5. SkipE-RNN (Das et al. 2020)      -- Dynamic temporal state gating    |
| 6. MRAN (Lu et al. 1999)            -- Established birth/prune/mature   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| TIER 3: MEDIUM THREATS (Conceptual overlap or domain-specific variants) |
| 7. Recurrent Cascade-Correlation    -- Residual-triggered recurrent add |
| 8. ACESN (2026)                     -- Adaptive capacity in reservoirs  |
| 9. AIRE-Prune / LAST (2025/2026)    -- Controllability x Observability  |
| 10. SOFNN / eTS (2004/2006)         -- Evolving recurrent neuro-fuzzy   |
| 11. Variable-Order LMS (2008)       -- Dynamic temporal tap allocation  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| TIER 4: LOW / DISTANT THREATS (Static architectures / unbudgeted SGD)   |
| 12. Standard LSTM / GRU (RTRL)      -- Static capacity, no lifecycle    |
| 13. Zero-Attracting LMS (2009)      -- Unbudgeted sparse descent O(D)   |
+-------------------------------------------------------------------------+
```

---

## 5. Strategic Pre-Publication Guidance

To withstand aggressive peer review by authors or proponents of these lineages:

1. **Acknowledge CCN and RTRL Immediately:**  
   State up front: *"Credit assignment for scalar recurrent states follows Williams & Zipser (1989) and Javed et al. (2023), computing exact O(1) forward sensitivities without approximation."*
2. **Acknowledge Continual Backprop for Maturation:**  
   State up front: *"The principle of protecting newly generated units during a maturation window is derived from generate-and-test continual learning (Dohare et al. 2021, 2024). Track B extends this principle to non-intrusive shadow evaluation of recurrent state dynamics."*
3. **Acknowledge Fahlman and MRAN for Error-Triggered Allocation:**  
   State up front: *"Generating new structural capacity in response to residual prediction failure has a long lineage beginning with Cascade-Correlation (Fahlman 1991) and MRAN (Lu et al. 1999)."*
4. **Sharpen the Distinctive Boundary:**  
   Focus empirical validation strictly where prior art fails:
   - Simultaneous governance of sparse inputs, lags, and recurrent states under rigid $O(K_{\max}+Q)$ ceilings;
   - Parsimonious escalation from linear to gated recurrence;
   - Quiescent retention protecting event memory against zero-excitation eviction;
   - Evidence-confirmed positive obsolescence under asymmetric loss ratios.
