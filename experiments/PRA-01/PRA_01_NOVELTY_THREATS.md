# PRA-01: Adversarial Novelty Threat Rankings

**Audit ID:** PRA-01  
**Auditor:** Adversarial Literature Reviewer & Novelty Analyst  
**Date:** September 19, 2026  

---

## 1. Threat Classification Scheme

Per Sections 49–53 of the audit protocol, prior art is categorized by the degree to which it undermines candidate novelty claims:
- **`CRITICAL`**: A paper that appears to implement nearly the exact same core combination or renders a foundational claim completely false.
- **`HIGH`**: A paper that covers most core principles but differs along one meaningful architectural axis (e.g., spatial vs. temporal, or unbudgeted inputs).
- **`MEDIUM`**: A paper that substantially overlaps with one subfamily (e.g., state pruning utility, or online sparse filtering) but lacks the integrated lifecycle.
- **`LOW`**: A paper that provides background context or reinforces known trade-offs without presenting direct architectural overlap.

---

## 2. Ranked Novelty Threats

### Tier 1: CRITICAL THREATS (Direct Invalidation of Specific Claims)

#### 1. Williams & Zipser (1989) — *Real-Time Recurrent Learning (RTRL)*
- **Threat Level**: **`CRITICAL` (for Credit Assignment / Claim C5)**
- **Why It Is Critical**:
  - Any claim that Track B introduces a "novel online gradient learning rule for recurrence without BPTT" is **scientifically false**.
  - The forward sensitivity trace:
    $$S_t = \lambda S_{t-1} + u_{t-1}$$
    is the direct algebraic specialization of Williams & Zipser's 1989 RTRL formula ($\frac{\partial h_t}{\partial \theta} = \frac{\partial f}{\partial h} \frac{\partial h_{t-1}}{\partial \theta} + \frac{\partial f}{\partial \theta}$) applied to a 1D scalar state ($N=1$).
  - Track B achieves $O(1)$ computation not through a new mathematical trick, but strictly because the state dimension is restricted to $d=1$.
- **Action**: Claim C5 must be classified as **`KNOWN`**. Do not claim credit assignment novelty.

---

### Tier 2: HIGH THREATS (Close Architectural Precedents)

#### 2. MUSE-RNN (Das, Pratama, Savitri, & Zhang, ICDM 2019)
- **Threat Level**: **`HIGH` (for Autonomous Recurrent State Lifecycle / Claim C6)**
- **Why It Is a High Threat**:
  - Implements an evolving recurrent neural network in real-time streaming data.
  - Dynamically creates and destroys hidden recurrent nodes and layers without task labels or replay buffers.
  - Demonstrates true resource reclamation (pruned nodes are physically removed from memory and compute graphs).
- **Key Distinctions Protecting Track B**:
  1. *Unbudgeted Inputs*: MUSE-RNN computes all $D$ input connections ($O(D)$); Track B uses a sub-linear probe bank ($O(K + Q) \ll O(D)$).
  2. *No Probation Window*: MUSE-RNN nodes are born directly into live predictions, suffering from newborn instability.
  3. *No Quiescent Protection*: Pruning is based on instantaneous variance (Network Significance). During quiescent memory intervals ($s_t = 0$), MUSE-RNN is prone to premature eviction.
  4. *No Linear vs Gated Hierarchy*: Employs only standard tanh recurrence.

#### 3. SkipE-RNN (Das, Pratama, Zhang, & Ong, AAAI 2020)
- **Threat Level**: **`HIGH` (for Temporal Lags + Recurrent Plasticity / Claims C3 & C6)**
- **Why It Is a High Threat**:
  - Combines evolving recurrent nodes with dynamically created skip-connections across historical time lags.
- **Key Distinctions Protecting Track B**:
  - Skip connections in SkipE-RNN route delayed label feedback under label latency. Track B discovers sparse feature-lag pairs ($x_{j, t-d}$) from unobserved candidate inputs under strict compute budgets.

#### 4. Minimal Resource Allocation Network — MRAN (Kadirkamanathan & Niranjan 1993; Sundararajan 1999)
- **Threat Level**: **`HIGH` (for Foundational Sequential Lifecycle / Claim C6)**
- **Why It Is a High Threat**:
  - First rigorously demonstrated online sequential lifecycle: *Prediction error spike $\to$ Unit birth $\to$ Online parameter learning $\to$ Sliding-window output contribution $\to$ Unit eviction*.
- **Key Distinctions Protecting Track B**:
  - MRAN operates strictly on static spatial RBF kernels in $\mathbb{R}^D$. It has zero temporal memory, zero recurrence, zero decay dynamics, and zero lag discovery.
  - Uses an expensive Extended Kalman Filter ($O(N^2)$), whereas Track B uses Normalized LMS ($O(N)$).

---

### Tier 3: MEDIUM THREATS (Subfamily Overlap)

#### 5. AIRE-Prune (Padhy, Camacho, & Mukhopadhyay, ICLR 2026)
- **Threat Level**: **`MEDIUM` (for State Utility Principle / Claim C8)**
- **Why It Is a Threat**:
  - Establishes that evaluating state utility via long-horizon output influence (Asymptotic Impulse-Response Energy) is the optimal way to prune state space models.
  - Threatens any claim that evaluating recurrent states by $C \times O$ is a new discovery.
- **Key Distinctions Protecting Track B**:
  - AIRE-Prune is strictly an offline, post-training model compression tool. Track B adapts the $C \times O$ principle into a causal, two-timescale online retention signal during live streaming.

#### 6. LAST — Layer-Adaptive State Pruning (Padhy et al., ICLR 2025)
- **Threat Level**: **`MEDIUM` (for Control-Theoretic State Truncation)**
- **Why It Is a Threat**:
  - Uses $\mathcal{H}_\infty$ subsystem norms and modal truncation to prune SSM states under compute budgets.
- **Key Distinctions Protecting Track B**:
  - Static offline pruning tool vs. Track B's dynamic online state creation and destruction.

#### 7. Elastic Neural Networks (Kong & Sutton, arXiv August 2026)
- **Threat Level**: **`MEDIUM` (for Bounded Structural Plasticity / Continual Learning)**
- **Why It Is a Threat**:
  - Demonstrates that growing and pruning units online maintains compact capacity and prevents loss of plasticity.
- **Key Distinctions Protecting Track B**:
  - Requires task boundaries to prune dead units. Restricted to feedforward networks.

#### 8. SMGrNN (Jia & Zhou, Neurocomputing 2026)
- **Threat Level**: **`MEDIUM` (for Local Evidence-Based Neuron Birth/Death)**
- **Why It Is a Threat**:
  - Adds and prunes neurons online in reinforcement learning based on local weight update statistics.
- **Key Distinctions Protecting Track B**:
  - Feedforward MLP; zero temporal recurrence or feature-lag discovery.

#### 9. Sparse LMS / Zero-Attracting LMS (Chen et al. 2009; Gu et al. 2009)
- **Threat Level**: **`MEDIUM` (for Online Sparse Learning / Claim C1)**
- **Why It Is a Threat**:
  - Establishes $\ell_1$-regularized online gradient descent for streaming regression.
- **Key Distinctions Protecting Track B**:
  - Requires observing all $D$ features every step ($O(D)$). Track B uses an active probe bank ($O(K + Q)$).

#### 10. Active Feature Acquisition (Guney et al. 2025; Norcliffe et al. 2025)
- **Threat Level**: **`MEDIUM` (for Budgeted Candidate Investigation / Claim C2)**
- **Why It Is a Threat**:
  - Establishes the principle of acquiring costly features sequentially under a budget.
- **Key Distinctions Protecting Track B**:
  - AFA optimizes external test-time measurement costs using offline-trained decision policies. Track B optimizes internal algorithmic FLOPs during online continuous learning.

---

### Tier 4: LOW THREATS (Background & Confirmatory Context)

#### 11. Stability of Growth in Structural Plasticity (Lillo & Cheney, arXiv May 2026)
- **Threat Level**: **`LOW` (as a threat) / `HIGH` (as theoretical validation)**
- **Role in Audit**: Confirms the severity of the "Newborn Bottleneck" in structural plasticity, providing strong external justification for Track B's 20-step probationary shadow window.

#### 12. Modern State Space Models — Mamba / S4 / LRU (Gu et al., Orvieto et al.)
- **Threat Level**: **`LOW`**
- **Role in Audit**: Fixed-dimension sequence representations; they do not grow, prune, or adapt internal state capacity dynamically during online inference.
