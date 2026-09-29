# Arbitration Decision Staleness Analysis

## 1. Maximum Periodic Staleness Formulation (B11, B12)

Let $K_{\text{arb}}$ denote the evaluation period of the supervisory arbitration subsystem.
The **arbitration decision age** $a(t)$ is defined as the number of stream steps elapsed since the last applied arbitration decision:
$$a(t) = t \pmod{K_{\text{arb}}}, \quad a(t) \in [0, K_{\text{arb}} - 1].$$

### Comparative Metrics:
| Metric | Current Schedule ($K_{\text{arb}}=5$) | Proposed Schedule ($K_{\text{arb}}=10$) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **Minimum Decision Age** | $0$ steps | $0$ steps | $0$ steps |
| **Maximum Periodic Staleness** | **$4$ steps** | **$9$ steps** | **$+5$ steps** |
| **Mean Decision Age** | $2.0$ steps | $4.5$ steps | $+2.5$ steps |
| **Median Decision Age** | $2.0$ steps | $4.5$ steps | $+2.5$ steps |
| **P95 Decision Age** | $3.8$ steps | $8.55$ steps | $+4.75$ steps |

---

## 2. Response-Latency Floor (B13)

When an external regime change or structural innovation occurs at stream step $t^*$:
- Under $K=5$, the arbitration filter evaluates at $t_1 = 5 \lceil t^* / 5 \rceil$. The latency floor is:
  $$\Delta \tau_5 = t_1 - t^* \in [0, 4]\text{ steps}.$$
- Under $K=10$, the arbitration filter evaluates at $t_2 = 10 \lceil t^* / 10 \rceil$. The latency floor is:
  $$\Delta \tau_{10} = t_2 - t^* \in [0, 9]\text{ steps}.$$
- **Incremental Response-Latency Floor:** Moving from $K=5 \to 10$ imposes an incremental latency of:
  $$\Delta \tau_{10-5} \in [0, 5]\text{ stream steps}.$$
- **Safety Evaluation against Preregistered Guardrails:**
  The preregistered switching latency margin for directional regime switching tasks ($I_{11}..I_{14}$) is **`+50 stream steps`**.
  An intrinsic delay floor of at most **`+5 steps`** represents exactly $10\%$ of the allowed tolerance, providing a $10\times$ theoretical buffer against catastrophic switching failure.
