# Literature-Grounded Hypothesis Freeze: Arbitration Dynamics

**Stage ID:** `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`  
**Purpose:** Formally ground the arbitration decimation study in external control and learning literature, enforcing strict epistemic discipline (established result vs conceptual analogy vs LEBRE hypothesis).

---

## 1. Epistemic Taxonomy & Guardrails (L1, L8, L9)

Every literature concept cited in this study is classified into one of three tiers:
1. `[ESTABLISHED_EXTERNAL_RESULT]`: Proven mathematical theorem or empirical finding published in peer-reviewed literature for a specific class of dynamical systems.
2. `[CONCEPTUAL_ANALOGY]`: High-level structural similarity that motivates qualitative intuition but confers no mathematical guarantee to LEBRE.
3. `[LEBRE_SPECIFIC_HYPOTHESIS]`: Empirical proposition regarding LEBRE that must be tested and validated by experimental observation.

**Strict Scope Limit:** No external theorem proves that $K_{\text{arb}}=10$ will preserve predictive accuracy, hybrid complementarity, or switching responsiveness in LEBRE. LEBRE requires empirical evidence.

---

## 2. Review of Foundational Literature

### 2.1 Mixture-of-Experts Gating (L2)
- **Reference:** Jacobs, R. A., Jordan, M. I., Nowlan, S. J., & Hinton, G. E. (1991). *"Adaptive Mixtures of Local Experts"*, Neural Computation, 3(1):79–87. DOI: `10.1162/neco.1991.3.1.79`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Modular networks combine specialized local experts via a supervisory gating network that learns to partition the input space.
- **`[CONCEPTUAL_ANALOGY]`:** LEBRE's conditional arbitration operates as a supervisory gating layer deciding whether discrete lag taps, recurrent units, or both govern operational predictions.
- **`[CRITICAL_LIMITATION]`:** Classical MoE evaluates soft gating weights continuously per sample via softmax. LEBRE uses sparse, hard-switched conditional gains with asymmetric lifecycles and unrounded TinyML constraints.

### 2.2 Multiple-Model Adaptive Control (MMAC) & Switching Dynamics (L3)
- **Reference:** Narendra, K. S., & Balakrishnan, J. (1994, 1997). *"Improving Transient Response of Adaptive Control Systems Using Multiple Models and Switching"*, IEEE TAC, 39(9):1861–1866; *"Adaptive Control Using Multiple Models"*, IEEE TAC, 42(2):171–187.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** In adaptive control, switching between multiple identification models based on accumulated performance indices materially alters transient behavior, convergence rates, and stability margins.
- **`[LEBRE_IMPLICATION]`:** Arbitration cadence ($K_{\text{arb}}$) is a dynamical subsystem variable. Changing evaluation frequency directly affects transient response during regime transitions ($I_{11}..I_{14}$).

### 2.3 Filtered Supervisory Performance Evidence (L4)
- **Reference:** Mosca, E., & Agnoloni, T. (2001). *"Inference of Candidate Loop Performance and Data Filtering for Switching Supervisory Control"*, Automatica, 37(4):527–534. DOI: `10.1016/S0005-1098(00)00183-7`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** In supervisory switching control, the choice of lowpass filter applied to performance signals (prediction errors) critically affects supervisory decision reliability and switching stability.
- **`[LEBRE_IMPLICATION]`:** The conditional-gain EMA is part of the evidence state of arbitration. Holding $\alpha = 0.02$ fixed while decimating $K_{\text{arb}}: 5 \to 10$ doubles the effective stream-time filter memory ($\tau_{\text{stream}}: 247.5 \to 495.0$ steps). This constitutes an intentional mechanistic change in evidence accumulation speed.

### 2.4 Hysteresis Switching (L5)
- **Reference:** Morse, A. S., Mayne, D. Q., & Goodwin, G. C. (1992). *"Applications of Hysteresis Switching in Parameter Adaptive Control"*, IEEE TAC, 37(9):1343–1354. DOI: `10.1109/9.159571`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Hysteresis switching logic prevents high-frequency chattering between candidate controllers.
- **`[CRITICAL_LIMITATION]`:** Fixed periodic decimation is NOT hysteresis. Decimation introduces a fixed time delay; hysteresis introduces an error-magnitude threshold.

### 2.5 Average Dwell-Time in Switched Systems (L6)
- **Reference:** Hespanha, J. P., & Morse, A. S. (1999). *"Stability of Switched Systems with Average Dwell-Time"*, Proceedings of the 38th IEEE CDC, pp. 2655–2660. DOI: `10.1109/CDC.1999.831330`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** Switched systems remain stable if switching logic enforces a sufficiently large average dwell-time between switches.
- **`[CRITICAL_LIMITATION]`:** LEBRE does not satisfy linear time-invariant switched system assumptions; no formal stability theorem applies to LEBRE without proof.

### 2.6 Event-Triggered Computation (L7)
- **Reference:** Tabuada, P. (2007). *"Event-Triggered Real-Time Scheduling of Stabilizing Control Tasks"*, IEEE TAC, 52(9):1680–1685. DOI: `10.1109/TAC.2007.904277`.
- **`[ESTABLISHED_EXTERNAL_RESULT]`:** State-dependent event triggering can replace periodic task execution, reducing compute while retaining stability.
- **`[LEBRE_IMPLICATION]`:** If fixed $K=10$ fails in confirmatory testing due to switching lag, event-triggered arbitration is the primary successor architecture. It is NOT implemented in this stage to maintain single-intervention discipline.
