# CAR_01_PRIOR_ART_RECONSTRUCTION.md — Conceptual Prior-Art Composite Reconstruction

**Stage:** CAR-01 (Contribution Assessment Review)  
**Task:** Adversarial Prior-Art Reconstruction & Distinctiveness Boundary Analysis  
**Governing Standard:** Sections 78–80 of CAR-01 Specification  
**Date:** September 19, 2026  
**Status:** COMPLETED & SEALED  

---

## 1. Adversarial Prior-Art Reconstruction Hypothesis

A skeptical prior-art auditor constructs the following challenge:

> *"If a researcher takes the existing literature and composites:  
> (1) Online RTRL forward sensitivity (Williams & Zipser 1989),  
> (2) Cascade Correlation Network / CCN growing (Fahlman & Lebiere 1990; Javed et al. 2023),  
> (3) RSONN / MUSE-RNN structural growth and pruning (Neurocomputing 2017; ICDM 2019),  
> (4) Continual Backpropagation utility and maturity replacement (Dohare et al., Nature 2024),  
> (5) Controllability/Observability gramian truncation (Moore 1981; AIRE / LAST),  
> (6) Variable-Tap LMS filter order adaptation (Zhao et al. 2008), and  
> (7) Adaptive Compression ESN capacity scheduling (Zhang et al. 2026),  
> does anything remain in Track B that is not already described?"*

---

## 2. Qualitative Literature Coverage Assessment

Evaluating Track B's component primitives against this conceptual composite:

| Track B Component | Precedent Literature Source | Qualitative Coverage |
| :--- | :--- | :---: |
| Forward Sensitivity Gradient Computation | Real-Time Recurrent Learning (Williams & Zipser 1989) | **100% COVERED** |
| Unit Maturation & Newborn Protection | Continual Backpropagation (Dohare et al., Nature 2024) | **100% COVERED** |
| Marginal Predictive Contribution / Utility | CCN (Javed et al. 2023) / Continual Backpropagation | **100% COVERED** |
| Dynamic Unit Growth / Allocation on Residual Error | RSONN (2017) / Resource Allocating Network (Platt 1991) | **100% COVERED** |
| Unit Eviction / Pruning on Low Relevance | MUSE-RNN (2019) / RSONN (2017) | **100% COVERED** |
| Controllability & Observability State Metric | Balanced Truncation (Moore 1981) / AIRE / LAST | **100% COVERED** |
| Sparse Feature Selection / Probing | Active Feature Acquisition / Stochastic Feature Selection | **100% COVERED** |
| Adaptive Filter Tapped-Delay Order | Variable-Tap LMS (Zhao et al. 2008) | **100% COVERED** |

**Overall Primitive Coverage Rating:** **HIGH**  
Every individual primitive mathematical operation (sensitivity derivative, running utility estimate, maturity counter, gramian proxy, sparse dot product) exists in the prior literature. **Track B does not introduce a novel primitive mathematical operator.**

---

## 3. What Remains After Literature Reconstruction?

After subtracting all known primitives, what remains is the **interaction architecture and structural governance policy**:

### 3.1 Unification Across Structural Object Types (The Unified Abstraction)
In prior art, the evaluation of feature selection, lag expansion, and recurrent state creation exist in completely isolated literatures:
- Sparse filtering (LMS/LASSO) operates strictly on feedforward inputs $x_t$.
- Adaptive delay filtering (Zhao et al. 2008) operates strictly on contiguous temporal buffers $x_{t-d}$.
- Growing neural networks (RSONN, MUSE-RNN, CCN) operate strictly on hidden neural units.

Track B organizes all three into a single coherent abstraction: **Cost-Bearing Computational Structures**. Observable features, temporal lag probes, and recurrent internal states undergo an identical lifecycle:  
$$\text{DORMANT} \longrightarrow \text{PROVISIONAL (Shadow)} \longrightarrow \text{ACTIVE} \longrightarrow \text{MATURE} \longrightarrow \text{EVICTED (Reclaimed)}$$

### 3.2 Two-Timescale Structural Retention Under Rent-Based Eviction
Prior-art growing/pruning systems (RSONN, MUSE-RNN, Continual Backprop) define utility via instantaneous error gradients or loss reduction:
$$U_t = \beta U_{t-1} + (1-\beta) |e_t|$$
Under quiescent workloads (Tasks A5 & A7), input signals drop to zero for extended intervals ($T_{\text{gap}} \sim \text{Poisson}(150)$). During these gaps, instantaneous predictive utility falls to zero, causing prior-art pruning rules to **annihilate dormant memory latches** (confirmed by Continual Backprop's failure on A5/A7).

Track B resolves this via an empirically derived interaction:
- It decouples structural relevance ($O_{\text{struct}}$, derived from input-to-state and state-to-output coupling) from excitation ($O_{\text{obs}}$, tracking recent state activity).
- It imposes an **asymmetric 300:1 false-eviction weighting**, preserving unexcited structural capacity across event gaps while evicting obsolete states only when persistent alternative evidence is established.

### 3.3 Provisional Non-Interfering Background Probation
In CCN, RSONN, and Continual Backprop, newly allocated units immediately drive the active network output. If a candidate unit receives noisy initial updates, it introduces transient output shock, frequently destabilizing the network on non-stationary streams (confirmed by Continual Backprop's 13.3% divergence rate on B2/B3).

Track B implements **shadow probation**: candidate states compute sensitivity traces and adapt in the background without affecting the primary prediction until their counterfactual rent payment ($\Delta \mathcal{L} > \theta_{\text{promote}}$) is confirmed over a probation window.

### 3.4 Parsimonious Structural Escalation
Track B enforces a hierarchical complexity escalation policy:
$$\text{Sparse Feedforward Linear} \xrightarrow[\Delta \mathcal{L} > 0.15]{\text{Failure}} \text{Linear Recurrent State} \xrightarrow[\text{Linear Fails}]{\Delta \mathcal{L} > 0.15} \text{Gated Recurrent State}$$
Higher-complexity structures (and their attendant FLOP costs) are explored only when lower-complexity models prove empirically insufficient.

---

## 4. Conclusion of Prior-Art Reconstruction

While 100% of Track B's computational primitives are known, **their joint organizational lifecycle—integrating multi-object structural governance, non-interfering shadow probation, two-timescale quiescent retention, and rent-based physical resource reclamation—does not exist as a composite in the prior literature.**
