# Future Success Criteria: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Formal Decision Protocol:** The future study can declare `COMBINED_K2_ARB10_SUPPORTED = YES` if and only if **ALL 10 of the following criteria pass simultaneously**:

| Gate # | Category | Metric / Condition | Target / Threshold | Criticality |
| :---: | :--- | :--- | :---: | :---: |
| **G1** | Strict Resource Gate | Arm A2 Grand Mean Total Online Compute | $\le \mathbf{100.000000\text{ FP/step}}$ | **MANDATORY** |
| **G2** | Primary Behavioral Gate | End-to-End Paired $\Delta \text{NMSE}(A2 - A0)$ 95% Upper CI | $< \mathbf{+0.010000}$ | **MANDATORY** |
| **G3** | Continuous Latent Gate | Task $I_6$ End-to-End Paired $\Delta \text{NMSE}(A2 - A0)$ | $\le \mathbf{+0.010000}$ | **MANDATORY** |
| **G4** | Quiescence Retention Gate| Task $I_7$ End-to-End Paired $\Delta \text{NMSE}(A2 - A0)$ | $\le \mathbf{+0.010000}$ | **MANDATORY** |
| **G5** | Hybrid Complementarity | Task $I_9$ A2 Active Conditional Gains | $G_{D|B+R} > 0 \land G_{R|BD} > 0$ | **MANDATORY** |
| **G6** | Directional Switching | Tasks $I_{11}..I_{14}$ Paired $\Delta \text{Latency}(A2 - A0)$ | $\le \mathbf{+50\text{ steps}}$ | **MANDATORY** |
| **G7** | Structural Integrity | No Pathological Structural Occupancy Collapse | Stable duty cycles | **MANDATORY** |
| **G8** | Resource Completeness | All Scheduler & Decimation Overhead Accounted | Zero unmodeled FP | **MANDATORY** |
| **G9** | Single-Intervention | Strict Invariant ($A2$ differs from $A1$ only by $K_{\text{arb}}$) | Preserved | **MANDATORY** |
| **G10**| Canonical Immutability | Canonical `src/` and `tests/` remain untouched | 124/124 Pytest Pass | **MANDATORY** |

---

## Outcome Taxonomy (C39)

The future study must classify its final result into exactly one outcome:
- **`COMBINED_RESOURCE_AND_BEHAVIOR_PASS`**: All 10 gates pass.
- **`RESOURCE_PASS_END_TO_END_NI_FAIL`**: Compute $\le 100\text{ FP}$, but aggregate $\Delta \text{NMSE} \ge +0.0100$.
- **`RESOURCE_PASS_SWITCHING_FAIL`**: Compute $\le 100\text{ FP}$, but switching latency exceeds $+50$ steps.
- **`RESOURCE_PASS_COMPLEMENTARITY_FAIL`**: Compute $\le 100\text{ FP}$, but $I_9$ collapses representation.
- **`BEHAVIOR_PASS_RESOURCE_FAIL`**: Behavior passes, but total compute exceeds $100.0\text{ FP/step}$.
- **`STRUCTURAL_UNDERMODELING`**: Severe structural collapse or failure of tap retention.
- **`IMPLEMENTATION_OR_ACCOUNTING_FAILURE`**: Code execution or accounting inconsistency.
