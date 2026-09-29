# Scientific Literature Note: Sparse and Multirate Recurrent State Execution

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Reviewed External Architectures

### 1.1 Clockwork RNN (Koutník et al., 2014)
- **Reference:** Koutník, J., Greff, K., Gomez, F., & Schmidhuber, J. (2014). "A Clockwork RNN." *International Conference on Machine Learning (ICML)*, PMLR 32:1851-1859.
- **External Mechanism:** Modules of recurrent hidden units are partitioned into discrete temporal clocks ($T_1, T_2, \dots, T_k$), where slower modules execute only at fixed harmonic intervals, holding their state between updates. Information flows from slow to fast modules.
- **LEBRE Relevance:** Provides strong external precedent for multirate recurrent execution without continuous stepping.
- **Critical Architectural Limit:** Clockwork RNN operates on wide hidden layers partitioned into modular clusters. LEBRE utilizes a single scalar latent unit ($N=1$) with online RTRL sensitivity propagation. Modular hierarchical coupling is not applicable.
- **Formal Classification:**
  - Multirate recurrent state decimation: `ESTABLISHED_EXTERNAL_MECHANISM`
  - Modular clockwork partitioning: `CONCEPTUAL_ANALOGY`

---

### 1.2 Skip RNN (Campos et al., 2018)
- **Reference:** Campos, V., Jou, B., Giró-i-Nieto, X., Torres, J., & Giro-i-Nieto, X. (2018). "Skip RNN: Learning to Skip State Updates in Recurrent Neural Networks." *International Conference on Learning Representations (ICLR)*.
- **External Mechanism:** A learned gating unit emits a binary decision $u_t \in \{0, 1\}$ conditioned on input and current hidden state. When $u_t = 0$, state propagation is completely skipped ($h_t = h_{t-1}$), directly optimizing a resource-penalized loss function.
- **LEBRE Relevance:** Validates the exact `HOLD_STATE` skip semantics ($h_t = h_{t-1}$) as a standard technique for reducing streaming compute.
- **Critical Architectural Limit:** Skip RNN requires offline reinforcement learning or surrogate gradient training with backpropagation-through-time (BPTT) to train the skip controller. LEBRE operates in a strictly online, streaming, single-pass regime with zero BPTT. A learned skip controller introduces meta-optimization overhead that exceeds the compute savings.
- **Formal Classification:**
  - State update skipping via `HOLD_STATE`: `ESTABLISHED_EXTERNAL_MECHANISM`
  - Learned budget-constrained controller: `CONCEPTUAL_ANALOGY`
  - Fixed-cadence decimation under online RTRL: `LEBRE_SPECIFIC_HYPOTHESIS`

---

### 1.3 Phased LSTM (Neil, Pfeiffer & Liu, 2016)
- **Reference:** Neil, D., Pfeiffer, M., & Liu, S. C. (2016). "Phased LSTM: Accelerating Recurrent Network Training for Long or Event-based Sequences." *Advances in Neural Information Processing Systems (NeurIPS)*, 29:3882-3890.
- **External Mechanism:** Extends LSTM cells with a rhythmic time gate governed by an oscillating phase function with three parameters (period $	au$, phase shift $s$, and duty cycle ratio $r$). State updates are executed only during an active phase window ($k_t \in (0, 1]$), remaining frozen elsewhere.
- **LEBRE Relevance:** Demonstrates that temporal decimation preserves long-term dependencies on event-driven sequences and continuous signals with sparse information arrival.
- **Critical Architectural Limit:** Phased LSTM relies on multi-gate LSTM cell dynamics. LEBRE utilizes a single-unit scalar RTRL state where sensitivity gradients ($p_lpha, p_b$) must track state trajectories without full BPTT.
- **Formal Classification:**
  - Periodic temporal gating of recurrent cells: `ESTABLISHED_EXTERNAL_MECHANISM`
  - Oscillating phase gates for RTRL scalar filters: `LEBRE_SPECIFIC_HYPOTHESIS`

---

## 2. Synthesis & Governance Guardrails

1. **Avoidance of Controller Overhead:** We reject learned gating controllers (e.g. Skip RNN controllers) because the arithmetic cost of evaluating an auxiliary gating filter on every step consumes 4–10 FLOPs, erasing the 14.40-FP saving achieved by cadence decimation.
2. **Periodic vs Event-Triggered:** Prior stage MR3 established that residual autocorrelation sentinels failed to detect temporal switching reliably. Therefore, fixed periodic decimation ($K=5$) is the sole admissible primary mechanism.
