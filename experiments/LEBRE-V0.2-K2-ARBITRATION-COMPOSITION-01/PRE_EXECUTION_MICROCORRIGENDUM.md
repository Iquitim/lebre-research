# Pre-Execution Microcorrigendum: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Governance Status:** MANDATORY PRE-EXECUTION AUDIT PASS  
**Execution Condition:** P0.1 satisfied (zero stochastic streams executed prior to this corrigendum).

---

## MC-01: Structural No-Change $\ne$ Computational Redundancy (P0.2)

The design report observed that approximately 99.55% of $K_{\text{arb}}=5$ evaluations did not immediately trigger a structural state change (promotion or eviction).
This does **NOT** establish that 99.55% of arbitration computation was redundant.
Each arbitration evaluation computes counterfactual error quadruplets, evaluates conditional gains ($g_d, g_r, g_{d|br}, g_{r|bd}$), and updates the 4 conditional-gain exponential moving averages (EMAs). These continuous state updates accumulate evidence that governs future structural allocations.

**Binding Corrected Wording:**
> *"Approximately 99.55% of observed K_arb=5 arbitration evaluations did not immediately change structural allocation on the audited trajectories. These evaluations are NOT proven computationally redundant because they update gain-estimation state that may influence future decisions."*

---

## MC-02: Scheduler-Latency Clock Bound $\ne$ Behavioral Recovery Latency (P0.3)

The design document referred to an `"incremental latency floor of +5 steps"`.
This must be explicitly recognized as a **deterministic clock wait bound**, NOT an upper bound on empirical behavioral recovery latency.

**Binding Formal Distinctions:**
- `MAX_ADDITIONAL_PERIODIC_SCHEDULER_WAIT_VS_K5` = **5 stream steps** (deterministic clock limit).
- `MAX_SCHEDULER_WAIT_INCREMENT` = **+5 steps**.
- `BEHAVIORAL_RECOVERY_LATENCY_INCREMENT` = **EMPIRICAL / TO BE MEASURED**.
Observed dynamical transitions may exhibit recovery latencies shorter than, equal to, or substantially longer than $+5$ steps depending on parameter convergence and error accumulation.

---

## MC-03: Reference Arm A0 Nomenclature (P0.4)

Arm $A0$ ($K_{\text{rec}}=1, K_{\text{arb}}=5$) must **NOT** be labeled `"canonical v0.1"`.
Canonical LEBRE v0.1 remains a distinct frozen historical architecture with continuous arbitration ($K_{\text{arb}}=1$).

**Binding Label:**
$$\mathbf{A0 = \text{ORIGINAL\_LOCAL\_V0\_2\_K1\_KARB5\_REFERENCE}}.$$

---

## MC-04: Exploratory Status of Churn Filtering (P0.5)

The hypothesis that slower arbitration *"filters high-frequency noise and reduces structural churn"* is formally classified as:
$$\mathbf{\text{CHURN\_REDUCTION} = \text{EXPLORATORY\_MECHANISTIC\_HYPOTHESIS}}.$$
It is NOT an expected benefit, a validated mechanism, or a prerequisite for confirmatory success. A reduction in churn is beneficial if and only if predictive accuracy and switching responsiveness are preserved.

---

## MC-05: Critical EMA-Timescale Consequence (P0.6–P0.10)

The arbitration subsystem updates four conditional-gain EMAs:
$$\text{EMA}_{k} = 0.98 \times \text{EMA}_{k-1} + 0.02 \times \text{gain}_{k}.$$
Because these updates occur strictly upon arbitration events, holding $\alpha = 0.02$ fixed while decimating the arbitration period ($K_{\text{arb}}: 5 \to 10$) **doubles the effective filter memory in stream time**.

### Exact Discrete-Time Mathematical Derivation:
- Discrete-time filter pole: $q = 1 - \alpha = 0.98$.
- Event-time constant:
  $$\tau_{\text{events}} = -\frac{1}{\ln(0.98)} = \mathbf{49.4983\text{ events}}.$$
- Stream-time constant $\tau_{\text{stream}}(K) = K \times \tau_{\text{events}}$:
  $$\tau_{\text{stream}}(K=5) = 5 \times 49.4983 = \mathbf{247.4916\text{ stream steps}}.$$
  $$\tau_{\text{stream}}(K=10) = 10 \times 49.4983 = \mathbf{494.9832\text{ stream steps}}.$$
- Half-life in events:
  $$\text{half\_life}_{\text{events}} = \frac{\ln(0.5)}{\ln(0.98)} = \mathbf{34.3096\text{ events}}.$$
- Stream-time half-life:
  $$\text{half\_life}_{\text{stream}}(K=5) = 5 \times 34.3096 = \mathbf{171.5481\text{ stream steps}}.$$
  $$\text{half\_life}_{\text{stream}}(K=10) = 10 \times 34.3096 = \mathbf{343.0962\text{ stream steps}}.$$

### Mandatory Experimental Rule:
**Do NOT rescale $\alpha_{\text{EMA}}$ in this experiment.**
Holding $\alpha = 0.02$ fixed preserves the strict single-intervention invariant ($K_{\text{arb}}: 5 \to 10$). The future experiment tests the combined causal effect of:
1. Decision scheduling staleness ($+5$ step clock wait); and
2. Slower stream-time evolution of conditional-gain evidence.
