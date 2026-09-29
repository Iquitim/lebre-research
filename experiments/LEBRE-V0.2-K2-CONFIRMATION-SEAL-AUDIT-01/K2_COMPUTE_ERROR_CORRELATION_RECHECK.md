# Compute-Error Association & Sign Convention Audit

**Audited Telemetry:** Paired $N=30$ seed averages of compute change and predictive error change.

---

## 1. Sign Convention Analysis

$$\begin{aligned}
\Delta \text{FP}_s &= \text{FP}_{C2, s} - \text{FP}_{C0, s} \quad (\text{negative values represent compute reduction}) \\
\text{Saving}_{\text{FP}, s} &= \text{FP}_{C0, s} - \text{FP}_{C2, s} \quad (\text{positive values represent compute reduction}) \\
\Delta \text{NMSE}_s &= \text{NMSE}_{C2, s} - \text{NMSE}_{C0, s} \quad (\text{positive values represent predictive degradation})
\end{aligned}$$

---

## 2. Correlation Recomputation

| Association Pair | Pearson $r$ | Two-Sided $p$-value | Interpretation |
|:---|:---:|:---:|:---|
| $\text{corr}(\Delta \text{FP}, \Delta \text{NMSE})$ | `-0.5627` | `0.0012` | Inverse correlation between net difference and error change |
| $\text{corr}(\text{Saving}_{\text{FP}}, \Delta \text{NMSE})$ | `0.5627` | `0.0012` | Positive correlation between compute saving and predictive degradation |

---

## 3. Epistemic Audit of Narrative Claims (F11 / F12)
- **Parent Claim:** The parent reported $r = -0.5627$ ($p = 0.0012$) and stated this "confirmed no perverse coupling between compute reduction and degradation."
- **Forensic Correction:**
  - Because $\Delta \text{FP}$ is negative for savings, $r(\Delta \text{FP}, \Delta \text{NMSE}) = -0.5627$ is algebraically identical to $r(\text{Saving}_{\text{FP}}, \Delta \text{NMSE}) = +0.5627$.
  - This demonstrates that seeds that achieved larger compute savings tended to exhibit greater predictive degradation.
  - This is an empirical **resource/accuracy trade-off association**, not an "absence of coupling."
  - Furthermore, this is a descriptive cross-seed association and must not be over-interpreted as a causal mechanism.
