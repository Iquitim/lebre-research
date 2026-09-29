# PRA-01: Architectural Comparison & Novelty Boundaries

**Audit ID:** PRA-01  
**Auditor:** Adversarial Literature Reviewer & Novelty Analyst  
**Date:** September 19, 2026  

---

## 1. Section A: What is Clearly Known in Prior Art

An adversarial review reveals that nearly every individual mathematical operation in the Track-B system has established, mature academic precedent:

1. **Online Recurrent Credit Assignment via Forward Sensitivity**:
   - The forward sensitivity trace $S_t = \lambda S_{t-1} + u_{t-1}$ is the exact mathematical reduction of Williams & Zipser's 1989 **Real-Time Recurrent Learning (RTRL)** algorithm to a single scalar recurrence ($d=1$).
   - The credit assignment mechanism contains **zero algorithmic novelty**. It is computationally light ($O(1)$) solely because the state dimension is restricted to 1.
2. **Online Sparse Parameter Adaptation**:
   - Zero-Attracting LMS (ZA-LMS, Chen et al. 2009), Reweighted ZA-LMS (Gu et al. 2009), and Online Lasso (Angelosante et al. 2010) already established $\ell_1$-regularized online gradient descent for streaming regression.
3. **Autonomous Structural Birth and Pruning in Streaming Data**:
   - The Minimal Resource Allocation Network (MRAN; Kadirkamanathan & Niranjan 1993; Sundararajan et al. 1999) established the online error-triggered birth and moving-window contribution-based eviction lifecycle.
   - Self-evolving recurrent networks (MUSE-RNN, Das et al. 2019; SkipE-RNN, Das et al. 2020) established real-time addition and pruning of recurrent hidden units in non-stationary data streams without task labels or replay.
4. **State Utility via Controllability and Observability**:
   - Evaluating state importance by the product of input controllability and output observability ($C \times O$) is the foundational concept of **Balanced Truncation and Hankel Singular Value Analysis** (Moore 1981).
   - Recent 2025–2026 preprints in state space models (AIRE-Prune, Padhy et al. 2026; LAST, Padhy et al. 2025) directly use asymptotic impulse response energy and subsystem $\mathcal{H}_\infty$ norms for structured state pruning.
5. **Temporal Lag Expansion**:
   - Expanding inputs into delayed features ($x_{j, t-d}$) via a tapped-delay ring buffer is the standard foundation of Time-Delay Neural Networks (TDNN; Waibel 1989), nonlinear autoregressive models (NARX; Billings 2013), and variable-tap adaptive filters (Zhao et al. 2008).

---

## 2. Section B: What is a Recombination of Known Ideas

Track B's architecture combines several independent lines of research to solve a constrained, resource-bounded streaming problem:

1. **Budgeted Probe Bank + Sparse Filtering**:
   - Standard sparse LMS processes all $D$ features every step ($O(D)$ FLOPs). Track B recombines Active Feature Acquisition (AFA) ideas with multi-armed bandit hypothesis testing (Wald SPRT) to maintain a small active set ($K_{\max}$) and evaluate unobserved features using a low-rate probe bank ($Q \ll D$), achieving genuine sub-linear compute ($O(K + Q)$).
2. **Probationary Shadow Window for Structural Growth**:
   - Lillo & Cheney (2026) demonstrated that standard structural growth suffers from the "Newborn Bottleneck" (new units are forward-active but receive weak gradient credit compared to mature units).
   - Track B addresses this by introducing a **20-step Probation Period**: nascent states learn dynamic parameters in shadow without driving live predictions, being promoted only if they demonstrate predictive superiority ($\ge 15\%$) over the feedforward baseline.
3. **Order Escalation Hierarchy**:
   - Moving from feedforward features $\to$ linear recurrence $\to$ gated recurrence follows the classical system identification escalation principle (Ljung 1999) and Recurrent Cascade-Correlation (Fahlman 1991).

---

## 3. Section C: What is Possibly Distinctive

If a novelty claim is to be made in a scientific publication, it must be narrowed strictly to the following integrated mechanisms:

1. **Resolution of the "Silent-Necessary vs Silent-Obsolete" Dilemma**:
   - In autonomous memory architectures, quiescent states (e.g., a SET/RESET latch during long event-free gaps where state $s_t = 0$) produce near-zero instantaneous prediction error delta ($\Delta L_t \approx 0$).
   - Every existing eviction rule in the evolving systems literature (MUSE-RNN's Network Significance, MRAN's output contribution, dead-unit pruning) triggers **premature eviction** during quiescence.
   - Track B uniquely resolves this by decoupling **Structural Observability ($O_{\text{struct}} = w_s^2$)** from instantaneous state amplitude, tracking it over a slow exponential timescale ($\tau_{\text{ret}} \approx 140$ steps).
2. **Positive Obsolescence Accumulation under Asymmetric Loss**:
   - Track B establishes empirically that decision cost is highly asymmetric ($C_{\text{FE}} / C_{\text{FR}} > 300 : 1$).
   - State deletion is governed by an explicit **positive obsolescence confirmation accumulator** ($O_{\text{obs}}$), requiring confirmed zero-excitation ($|x_t| < \epsilon \land |\hat{y}_t| < \epsilon$) across a sustained patience window before physical state reclamation.
3. **Unified Structural Lifecycle Across Observable and Hidden Representations**:
   - While prior works treat either sparse feature selection OR hidden neuron growth in isolation, Track B unifies observable features, temporal lags, and internal recurrent hidden states under an identical resource lifecycle:  
     $$\text{Candidate Probing} \to \text{Incubation/Probation} \to \text{Active Promotion} \to \text{Retention Utility} \to \text{Eviction/Reclaim}$$
   - Internal computational structure is treated strictly as a cost-bearing resource that must "pay rent" through predictive error reduction.

---

## 4. Section D: What Appears Unsupported as a Novelty Claim

The following claims must be **explicitly abandoned or retracted** in any academic paper or technical report:

1. **DO NOT claim novelty for forward sensitivity credit assignment**:
   - It is not a new learning rule; it is 1989 RTRL for $d=1$.
2. **DO NOT claim novelty for online structural growth and pruning**:
   - Evolving recurrent networks (Pratama, Das et al.) and resource-allocating networks (Platt, Kadirkamanathan) established this in 1991–2020.
3. **DO NOT claim novelty for state utility based on controllability/observability**:
   - Balanced truncation (Moore 1981) and state-space pruning (AIRE-Prune 2026) established this mathematically.
4. **DO NOT claim that the system is a "general-purpose foundation model"**:
   - The frozen core is strictly validated as a single-state ($K=1, d=1$) continuous learner.

---

## 5. Section E: What Requires Benchmark Evidence Rather than Novelty Evidence

A paper describing Track B will not be accepted based on theoretical claims of uniqueness alone. It requires empirical benchmark validation:

1. **Head-to-Head Comparison against Evolving Neural Networks**:
   - Does Track B achieve higher active recall and lower state churn than MUSE-RNN or SkipE-RNN on non-stationary streams with long quiescent gaps?
2. **Head-to-Head Comparison against Fixed Recurrent Models**:
   - Does Track B achieve equivalent or superior predictive MSE compared to a fixed GRU, LSTM, or Mamba while consuming $5\times$ to $20\times$ less amortized energy and memory?
3. **Ablation of the Causal Guardrails**:
   - Empirical proof that removing the probation window reopens the "Newborn Bottleneck" (validating Lillo & Cheney 2026).
   - Empirical proof that removing the positive obsolescence accumulator causes premature state forgetting under high cost asymmetry ($> 300:1$).
