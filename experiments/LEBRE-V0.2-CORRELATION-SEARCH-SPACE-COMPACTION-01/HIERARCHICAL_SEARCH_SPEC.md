# Hierarchical Coarse-to-Fine Search Specification

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Comparative Architecture Specification & Negative Control  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Architectural Motivation and Hypothesis

Hierarchical multi-scale delay search is widely utilized in radar time-delay estimation and image pyramid matching (Knapp & Carter 1976). 

The underlying premise is that a search space can be evaluated initially on a coarse sub-sampled grid:
$$\mathcal{K}_{\text{coarse}} = \{2, 4, 8, 12, 16, 20, 24, 28, 32\}$$
If an evidence peak is detected at a coarse anchor $k_{\text{coarse}}$, a local refinement window of fine taps $\{k_{\text{coarse}} - 1, k_{\text{coarse}} + 1\}$ is activated.

### Theoretical Precondition (Lag-Score Locality):
Coarse-to-fine search is valid if and only if true physical delays induce a smooth, smeared correlation response across neighboring lags, ensuring that a coarse tap captures a significant fraction of the peak evidence.

---

## 2. Mathematical Definition

### 2.1 Coarse Grid Structure
- Evaluates $N_{\text{feat}} \times |\mathcal{K}_{\text{coarse}}| = 5 \times 6 = 30$ cells.
- Coarse lag anchors: $k \in \{2, 4, 8, 12, 16, 24\}$.
- Probed at parent clock $K_{\text{probe}} = 2$ steps, 1 cell per probe tick ($2.00\text{ FP/step}$).

### 2.2 Refinement Activation Policy
When a coarse anchor $(i, k_c)$ exhibits $|\hat{\rho}_{i, k_c}| \ge \tau_{\text{refine}} = 0.20$:
- Fine taps $(i, k_c - 1)$ and $(i, k_c + 1)$ are instantiated into a dynamic refinement buffer.
- Refinement taps are probed for $W_{\text{refine}} = 50$ steps.
- If a fine tap crosses $\tau_{\text{birth}} = 0.25$, a candidate is escalated to probation.

---

## 3. Disqualification and Status as Negative Control

In Phase 1 diagnostic auditing (`LAG_SCORE_LOCALITY_REPORT.md` and `HIERARCHICAL_SEARCH_ELIGIBILITY.md`), empirical evaluation across 4,915 active delay instances demonstrated:
1. **Neighbor Rank Correlation:** $r = 0.2176$ (Threshold: $\ge 0.60$ — **REJECTED**).
2. **Neighbor Recall Ratio:** $26.50\%$ (Threshold: $\ge 70.0\%$ — **REJECTED**).
3. **Capture Rate $\ge 70\%$ of Peak:** $3.64\%$ (Threshold: $\ge 70.0\%$ — **REJECTED**).

### Epistemic Role in Experiment:
As mandated by the preregistration, $C_2$ is **formally disqualified** from proceeding to the confirmatory evaluation stage. However, it will be executed during Phase 2 DEV screening alongside $C_1$ to rigorously quantify the predictive failure modes of hierarchical search on discrete white-noise benchmarks ($I_3, I_4, I_5$), providing conclusive empirical documentation of why coarse-to-fine search is physically inappropriate for discrete streaming lag identification.
