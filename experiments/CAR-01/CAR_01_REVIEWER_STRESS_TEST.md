# CAR_01_REVIEWER_STRESS_TEST.md — Adversarial Reviewer Stress Test & Empirical Defense

**Protocol:** CAR-01  
**Milestone:** Contribution Assessment Review  
**Date:** September 19, 2026  
**Status:** Skeptical Peer Review Audit  

---

## 1. The Adversarial Reviewer Attack (<= 200 Words)

> *"This submission is an ad-hoc bag of tricks masquerading as an architecture. Every single component is well-known textbook prior art: Williams & Zipser established 1D RTRL in 1989; Chen et al. solved sparse LMS decades ago; Dohare et al. (Nature 2024) recently formalized utility-based pruning with newborn maturity protection; and balanced truncation Gramians date back to Moore (1981). Sticking an economic rent threshold and a shadow buffer between these existing algorithms is standard engineering duct tape, not a scientific contribution. Furthermore, your architecture does not even achieve the lowest error: RSONN and CCN both beat Track B in aggregate prediction. Without a genuinely new learning rule or mathematical primitive, you have merely assembled off-the-shelf heuristics that happen to fit your hand-picked benchmark tasks."*

---

## 2. The Evidence-Based Author Response (<= 250 Words)

> *"The reviewer is entirely correct that every mathematical primitive in Track B is established prior art—a fact our contribution decomposition explicitly documents. However, dismissing the system as an unprincipled composition overlooks three falsifiable empirical realities demonstrated across 6,750 competitive runs:
>
> 1. **Failure of Naive Composition:** Simply combining these primitives without our derived lifecycle fails catastrophically. Our controlled ablations prove that direct candidate coupling causes gradient shock (4.8× transient error spike; M2-EXP-0001); standard utility decay annihilates dormant memory during quiescent bursts (100% loss; M2-EXP-0003); and symmetric pruning triggers destructive churn cycles (M2-EXP-0005r). The specific interaction mechanisms—shadow probation, two-timescale Gramian retention ($O_{\text{struct}}$ vs $O_{\text{obs}}$), and 300:1 asymmetric obsolescence confirmation—were empirically necessary under the tested ablations to stabilize the coupled dynamics.
> 2. **Reproducibility of Failure in Nearest Neighbors:** Existing systems embodying subsets of these primitives broke under continuous streaming: S2 (LRU) suffered a 21% divergence rate; S5 (Continual Backpropagation) diverged on 13.3% of runs and prematurely evicted dormant units; and S1 (Variable-Tap LMS) diverged on real-world multi-sensor streams. In contrast, Track B achieved a 0.0% divergence rate across all 450 evaluation runs.
> 3. **Distinct Micro-Resource Operating Point:** While higher-capacity models (RSONN, CCN) achieve lower error on unconstrained synthetic tasks, they require 3.5× to 5.5× more compute. Track B occupies a distinct, strictly bounded operating point among evaluated methods: mean 90.44 FLOPs/step, 440 bytes of memory, zero divergence, and strict Pareto-dominance over standard minimal recurrent units (Minimal GRU, MUSE-RNN).
>
> Track B’s contribution is not a new primitive, but the empirically verified, resource-governed structural lifecycle that makes continuous adaptation stable under strict sub-100-FLOP constraints."*

---

## 3. Direct Answers to the Seven Core Human-Readable Questions

### Question 1: What did we actually discover?
**Answer:** We discovered that streaming temporal learners operating under extreme micro-resource constraints ($\le 100$ FLOPs) do not fail from lack of capacity, but from **asymmetric lifecycle instability**. Specifically:
- Adding unvalidated recurrent feedback causes immediate predictive shock;
- Single-timescale utility metrics mistake temporal quiescence for obsolescence, prematurely destroying dormant memory;
- Evicting a necessary recurrent state incurs an error penalty hundreds of times higher than the marginal compute cost of retaining it.
Stabilizing online structural learning requires decoupling observation frequency from structural retention and enforcing asymmetric hysteresis on structural removal.

### Question 2: What part of this system is actually our scientific contribution, as opposed to known components?
**Answer:** The scientific contribution is **the resource-governed structural lifecycle and its empirical interaction constraints**:
- The non-interfering shadow probation buffer for candidate recurrent states;
- The two-timescale structural relevance mechanism ($O_{\text{struct}}$ vs $O_{\text{obs}}$) that preserves dormant state across low-activity intervals;
- The positive obsolescence confirmation protocol operating under a 300:1 asymmetric false-eviction weighting;
- The unified treatment of feature taps, temporal delays, and internal recurrence as cost-bearing adaptive objects under a common lifecycle.

### Question 3: Why is this not merely a bag of known techniques?
**Answer:** A bag of techniques is an arbitrary collection of heuristics whose interactions are unstudied. Track B is an **empirically derived architecture where each interaction mechanism was forced by the concrete mathematical failure of simpler compositions**. Ablating any single lifecycle mechanism destroys benchmark stability:
- Removing shadow probation causes gradient shock on regime changes;
- Removing two-timescale retention destroys memory on Poisson gap workloads;
- Removing asymmetric eviction causes catastrophic structural churn;
- Removing physical deallocation violates the sub-100-FLOP micro-resource budget.
Furthermore, the lifecycle applies symmetrically across heterogeneous structures (features, lags, states), satisfying the definition of a coherent architectural framework.

### Question 4: What does Track B buy that its closest prior-art neighbors do not buy at the same resource level?
**Answer:** Track B buys **zero observed numerical divergences across 450 evaluation runs, adaptive capacity elasticity (A8), and favorable predictive accuracy within an extreme micro-resource envelope ($\le 100$ FLOPs, $\le 1024$ Bytes)**:
- Versus Minimal GRU: 1.24× lower error, 3.12× lower compute, lower memory.
- Versus MUSE-RNN: 1.43× lower error, 1.75× lower compute.
- Versus Variable-Tap LMS & Continual Backprop: Zero divergence on complex real-world streams (Jena Weather, Gas Mixture) where competitors suffered gradient explosions.
- Versus RSONN & CCN: Matches stability and sparse efficiency at 1/5th and 1/3.5th of the computational cost.

### Question 5: Where should this architecture NOT be used?
**Answer:** Track B must **NOT** be used in:
1. **Pure discrete tapped-delay problems** (e.g. A2–A4), where shift-register delay lines (FIR filters) are mathematically required.
2. **Dense high-dimensional chaotic or nonlinear state-space manifolds** (e.g. B4 Silverbox System Identification), where a single 1D scalar recurrent state lacks topological capacity.
3. **Batch, offline, or over-parameterized deep learning domains** (e.g. LLMs, foundation models, offline vision), where compute is unconstrained and backpropagation-through-time (BPTT) is computationally feasible.

### Question 6: Is it now scientifically reasonable to call this an architecture?
**Answer: YES_WITH_SCOPE_LIMITS.**  
Track B possesses persistent structural organization, multi-component interaction, formal information routing, and a unified lifecycle that cannot be reduced to a single algorithmic update equation. However, the scope is strictly limited to single-state scalar recurrence and sparse feature adaptation under streaming micro-resource budgets.

### Question 7: Is it now reasonable to give it a formal name?
**Answer: YES.**  
The empirical evidence, structural boundaries, and scientific contribution are now sufficiently delineated that assigning a formal architecture name in a dedicated naming stage (`ARCH-NAME-01`) is scientifically justified and necessary for publication positioning.
