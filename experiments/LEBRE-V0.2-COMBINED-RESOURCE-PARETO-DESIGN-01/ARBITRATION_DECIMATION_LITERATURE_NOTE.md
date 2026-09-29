# Arbitration Decimation: Literature-Grounded Interpretation

**Study:** `LEBRE-V0.2-COMBINED-RESOURCE-PARETO-DESIGN-01`  
**Purpose:** Situate arbitration cadence decimation within established external control and machine learning literature, enforcing strict distinctions between external theorems, conceptual analogies, and LEBRE-specific empirical hypotheses.

---

## 1. Epistemic Classification Framework (B26)

Every scientific claim in this note is strictly categorized:
1. `[ESTABLISHED_EXTERNAL_RESULT]`: Proven mathematical theorem or empirical finding published in peer-reviewed literature for a specific class of dynamical systems.
2. `[CONCEPTUAL_ANALOGY]`: High-level structural or philosophical similarity that guides architectural intuition but confers no mathematical guarantee to LEBRE.
3. `[LEBRE_SPECIFIC_HYPOTHESIS]`: Empirical proposition regarding LEBRE that must be tested and validated by experimental observation.

---

## 2. Review of Foundational Literature

### 2.1 Mixture of Experts & Gating Cadence (B27)
- **Reference:** Jacobs, R. A., Jordan, M. I., Nowlan, S. J., & Hinton, G. E. (1991). *"Adaptive Mixtures of Local Experts"*, Neural Computation, 3(1):79–87. DOI: `10.1162/neco.1991.3.1.79`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Modular neural networks combining specialized local experts via a supervisory gating network can partition input spaces and decouple representation learning.
- **`[CONCEPTUAL_ANALOGY]`:** LEBRE's conditional arbitration layer acts as a supervisory gating mechanism deciding whether discrete lag taps, recurrent units, or both govern operational predictions.
- **`[CRITICAL_LIMITATION]`:** In classical MoE, gating weights are evaluated continuously per sample via soft softmax blending. LEBRE uses sparse, hard-switched conditional gains with asymmetric lifecycles and unrounded TinyML constraints. Classical MoE provides no guarantees for periodic decimation.

### 2.2 Multiple-Model Adaptive Control (MMAC) & Switching Dynamics (B28)
- **Reference:** Narendra, K. S., & Balakrishnan, J. (1994, 1997). *"Improving Transient Response of Adaptive Control Systems Using Multiple Models and Switching"*, IEEE TAC, 39(9):1861–1866; *"Adaptive Control Using Multiple Models"*, IEEE TAC, 42(2):171–187.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** In adaptive control, switching between multiple identification models based on accumulated performance indices materially alters transient behavior, convergence rates, and stability margins.
- **`[LEBRE_IMPLICATION]`:** Arbitration cadence ($K_{\text{arb}}$) cannot be treated as an inert computational scheduler. Because it changes the timing of model selection, it is a dynamical subsystem variable that directly affects transient response during regime transitions ($I_{11}..I_{14}$).

### 2.3 Hysteresis Switching (B29)
- **Reference:** Morse, A. S., Mayne, D. Q., & Goodwin, G. C. (1992). *"Applications of Hysteresis Switching in Parameter Adaptive Control"*, IEEE TAC, 37(9):1343–1354. DOI: `10.1109/9.159571`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Introducing a hysteresis margin between candidate model performance indices prevents high-frequency chattering and guarantees a finite number of switches over compact intervals.
- **`[CONCEPTUAL_ANALOGY]`:** Slowing arbitration cadence ($K=5 \to 10$) acts as an implicit temporal low-pass filter, preventing rapid oscillatory switching between structures in noisy environments.
- **`[CRITICAL_LIMITATION]`:** Periodic decimation is mathematically distinct from state-dependent hysteresis. Periodic decimation introduces a fixed time delay, whereas hysteresis introduces an error-magnitude threshold. Do not claim that $K=10$ implements hysteresis switching.

### 2.4 Average Dwell-Time in Switched Systems (B30)
- **Reference:** Hespanha, J. P., & Morse, A. S. (1999). *"Stability of Switched Systems with Average Dwell-Time"*, Proceedings of the 38th IEEE Conference on Decision and Control (CDC), Phoenix, AZ. DOI: `10.1109/CDC.1999.831330`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** A switched linear system remains exponentially stable if the switching logic enforces a sufficiently large average dwell-time $\tau_a$ between switch events, allowing transient energy to dissipate.
- **`[CONCEPTUAL_ANALOGY]`:** Increasing $K_{\text{arb}}$ naturally increases the minimum dwell-time between structural reallocations to at least 10 stream steps.
- **`[CRITICAL_LIMITATION]`:** LEBRE's combined linear/recurrent architecture with online learning does not satisfy the linear time-invariant assumptions of the Hespanha-Morse theorem. The theorem provides qualitative intuition, not a formal stability proof.

### 2.5 Event-Triggered Control Task Scheduling (B31)
- **Reference:** Tabuada, P. (2007). *"Event-Triggered Real-Time Scheduling of Stabilizing Control Tasks"*, IEEE TAC, 52(9):1680–1685. DOI: `10.1109/TAC.2007.904277`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Periodic task execution can be replaced by state-dependent event triggering (executing control updates only when Lyapunov function decay or state error exceeds a threshold), dramatically reducing computational utilization while guaranteeing asymptotic stability.
- **`[LEBRE_IMPLICATION]`:** The bursty nature of LEBRE's meaningful arbitration decisions (Section B24) suggests that an event-triggered arbitration scheduler is theoretically sound. If fixed $K=10$ fails due to latency, event-triggered arbitration is the primary successor candidate.

---

## 3. Literature Claim Discipline (B32)

External literature justifies investigating whether supervisory decision frequency can be reduced to save computational resources.
However, **no external theorem proves that $K_{\text{arb}}=10$ will preserve predictive accuracy or temporal mechanism integrity in LEBRE**.
Non-inferiority, switching latency preservation ($\le +50$ steps), and hybrid complementarity ($G_{D|B+R} > 0, G_{R|BD} > 0$) remain **unproven LEBRE-specific empirical hypotheses** that must be rigorously validated through paired confirmatory experimentation.
