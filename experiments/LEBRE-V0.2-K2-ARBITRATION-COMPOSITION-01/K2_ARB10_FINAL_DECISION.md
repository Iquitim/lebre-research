# Final Decision: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Primary Stage Outcome:** **`K2_ARB10_RESOURCE_PASS_END_TO_END_NI_FAIL`**

---

## 1. Executive Adjudication

| Evaluation Gate | Requirement | Observed Outcome | Ruling |
| :--- | :---: | :---: | :---: |
| **Strict Resource Gate** | Total Compute $\le 100.000000\text{ FP/step}$ | `96.957851\text{ FP/step}` | **PASS** |
| **Primary Predictive Gate** | $A2 - A0$ 95% Upper CI $< +0.010000$ | `+0.020204\text{ NMSE}` | **FAIL** |
| **K2 Replication Gate** | $A1 - A0$ 95% Upper CI $< +0.010000$ | `+0.004477\text{ NMSE}` | **PASS** |
| **Directional Switching Gate**| $\Delta \text{latency} \le +50\text{ steps}$ on $I_{11}..I_{14}$ | Max $\Delta = +213.63\text{ steps}$ on $I_{12}$ | **FAIL** |
| **Hybrid Complementarity** | $G_{D|BR} > 0 \land G_{R|BD} > 0$ on $I_9$ | $G_D = 0.3647, G_R = 0.0352$ | **PASS** |
| **Single-Intervention Rule** | Exactly $K_{\text{arb}}: 5 \to 10$ relative to $A1$ | Verified in `A0_A1_A2_CONFIG_DIFF.csv` | **PASS** |

## 2. Verdict
The combined architecture $K_{\text{rec}}=2 + K_{\text{arb}}=10$ (Arm A2) **CANNOT BE CERTIFIED AS A LOCAL RESOURCE-COMPLIANT CANDIDATE**.
While it successfully achieved the strict compute ceiling ($96.96\text{ FP/step}$), it failed the mandatory primary predictive non-inferiority gate and switching latency guardrails.
