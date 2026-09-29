# Analytical Derivation: Timebase-Preserving Arbitration EMA

## 1. Mathematical Derivation
At $K_{\text{arb}}=5$, the discrete pole per arbitration event is $q_5 = 1 - \alpha_5 = 0.98$.  
Its equivalent decay per stream step is:
$$q_{\text{stream}} = q_5^{1/5} = 0.98^{0.2} \approx 0.995960.$$

To preserve the exact same stream-step decay rate at $K_{\text{arb}}=10$:
$$q_{10}^{1/10} = q_5^{1/5} \implies q_{10} = q_5^{10/5} = q_5^2 = (0.98)^2 = \mathbf{0.960400}.$$

Therefore, the required per-event smoothing factor is:
$$\alpha_{10} = 1 - q_{10} = 1 - 0.960400 = \mathbf{0.039600}.$$

## 2. Theoretical Equivalence
- Event characteristic time: $\tau_{\text{events, K10}} = -1 / \ln(0.9604) = \mathbf{24.749158\text{ events}}$.
- Physical stream characteristic time:
  $$\tau_{\text{stream, K10}} = 10 \times 24.749158 = \mathbf{247.491582\text{ stream steps}} \equiv \tau_{\text{stream, K5}}.$$

## 3. Governance Classification
- Status: **`ANALYTICALLY_DERIVED_FUTURE_HYPOTHESIS`**.
- Execution: **`NO`** (Unexecuted in this stage).
- Preregistration Requirement: Implementing $\alpha_{10}=0.039600$ requires a dedicated confirmatory preregistration on fresh seeds.
- Scope Limitation: Matching the EMA pole restores stream-time evidence decay, but does NOT restore lost arbitration decision opportunities (cadence remains 10 steps).
