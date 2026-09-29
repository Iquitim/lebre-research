# Resource Component Decomposition & Mathematical Closure

**Audited Study:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`

---

## 1. Level-1 Empirical Resource Balances

$$\begin{aligned}
\text{Mean Total Compute }(C_0) &= 111.236118\text{ FP/step} \\
\text{Mean Total Compute }(C_2) &= 101.023283\text{ FP/step} \\
\mathbf{\Delta \text{ Total Compute}} &= -10.212835\text{ FP/step} \\
\mathbf{\text{Total Compute Saving}} &= \mathbf{10.212835\text{ FP/step}} \quad (-9.1812\%)
\end{aligned}$$

---

## 2. Component-by-Component Savings Audit

| Subsystem Component | $C_0$ Compute | $C_2$ Compute | Component Saving (FP) | Mechanism |
|:---|:---:|:---:|:---:|:---|
| **Recurrent Shadow Forward & Learn** | `20.200000` | `11.200000` | `+9.000000` | Direct decimation ($K_{\text{rec\_forward}}=1 \to 2$, $18.0 \to 9.0\text{ FP}$) |
| **Live Linear Base & Active Taps** | `75.684417` | `74.483266` | `+1.201151` | Stochastic tap occupancy variation ($-0.0433$ rec duty) |
| **Search Probe & Management** | `7.902070` | `7.901044` | `+0.001025` | Invariant search policy ($K_{\text{probe}}=2, B=4$) |
| **Candidate Direct Observation** | `1.849632` | `1.838973` | `+0.010659` | Candidate observation under $K=5$ |
| **Candidate Arbitration** | `5.600000` | `5.600000` | `+0.000000` | Candidate-to-live arbitration under $K_{\text{arb}}=5$ |
| **SUM OF COMPONENT SAVINGS** | | | `+10.212835` | |

---

## 3. Reconciliation Residual & Closure Verdict

$$\text{Residual} = \text{Authoritative Saving} - \sum \text{Component Savings} = 10.212835 - 10.212835 = \mathbf{0.000000e+00\text{ FP/step}}$$

- **Residual Magnitude:** $0.000000\text{ FP/step}$ (within $10^-14$ machine epsilon).
- **Verdict:** `RESOURCE_COMPONENT_ACCOUNTING = PASS`.
- The resource balances close with zero unexplained residual.

---

## 4. Root Cause of Reported "17.000 FP" Saving (F01 / F24)
- **Lineage:** In `generate_k2_confirmation_outputs.py` line 252, the generator script hardcoded:
  `'c0_fp_mean': 34.0, 'c2_fp_mean': 17.0, 'delta_fp': -17.0`
  representing a stale theoretical assumption of $34.0\text{ FP/forward}$ from an un-decimated analytical prototype.
- **Physical Reality:** In the executable architecture (`RecurrentScalarUnit.forward`), forward execution logs exactly $18.0\text{ FP/step}$, which decimates to $9.0\text{ FP/step}$.
- **Consistency:** The parent report stated the percentage $-9.18\%$, which matches $10.212835 / 111.236118 = 9.1812\%$. The percentage was computed from the true Level-1 saving, while the literal text "17.000" was a stale template string.
