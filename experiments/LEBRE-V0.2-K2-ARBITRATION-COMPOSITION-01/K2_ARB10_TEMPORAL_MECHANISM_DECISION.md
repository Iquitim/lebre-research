# Temporal Mechanism Decision: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Temporal Guardrails Overall Status:** **`FAIL`**

| Gate | Target / Threshold | Observed A2 vs A0 | Observed A2 vs A1 | Status |
| :--- | :---: | :---: | :---: | :---: |
| **I6 Continuous Latent** | $\Delta \le +0.010000$ | **`+0.005277`** | `+0.002081` | **PASS** |
| **I7 Quiescent Retention** | $\Delta \le +0.010000$ | **`+0.017118`** | `+0.011218` | **FAIL** |
| **I9 Complementarity** | $G_{D|BR} > 0 \land G_{R|BD} > 0$ | $G_{D} = 0.3647, G_{R} = 0.0352$ | Positive on both | **PASS** |
| **I11 Switching Recovery** | $\Delta \text{latency} \le +50\text{ steps}$ | **`+76.17\text{ steps}`** | `+19.83\text{ steps}` | **PASS** |
| **I12 Switching Recovery** | $\Delta \text{latency} \le +50\text{ steps}$ | **`+213.63\text{ steps}`** | `+167.97\text{ steps}` | **FAIL** |
| **I13 Switching Recovery** | $\Delta \text{latency} \le +50\text{ steps}$ | **`+-1.73\text{ steps}`** | `+0.53\text{ steps}` | **PASS** |
| **I14 Switching Recovery** | $\Delta \text{latency} \le +50\text{ steps}$ | **`+-398.27\text{ steps}`** | `-428.13\text{ steps}` | **PASS** |

## Findings
While continuous latent tracking ($I_6$) and hybrid complementarity ($I_9$) passed, quiescent state retention ($I_7$) and directional regime switching on $I_{12}$ (`Latent_To_Delay`) breached their respective preregistered tolerances.
