# Arbitration Cadence & Resource Value Lineage

## 1. Chronology of Arbitration Cadence Configurations

1. **`v0.1 Canonical` ($K_{\text{arb}} = 1$):**
   In the frozen v0.1 baseline, structural selection and capacity evaluations executed continuously at every stream step ($1.0\text{ event/step}$).
2. **`v0.2 Multirate Screening` ($D_{10}$, $K_{\text{arb}} = 5$):**
   In `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`, isolated component screening identified arbitration as a slow-timescale supervisory process. Running arbitration every 5 steps ($0.2\text{ events/step}$) eliminated $22.40\text{ FP/step}$ of continuous compute ($28.0 \to 5.6\text{ FP/step}$) without predictive degradation.
3. **`Historical Notation Artifact` ($K_{\text{arb}} = 2.5$):**
   In `RESOURCE_ACCOUNTING_01_FINAL_REPORT.md` (line 97), the narrative discussed:
   `"Mean query frequency = 5.5 queries/step (2.5 active taps + 1.0 candidate probe + 2.0 provisional shadow queries)"`.
   Subsequent summary notes misquoted `"2.5 active taps"` as a fractional modulo clock `"K_arb = 2.5"`.
   **Resolution:** In executable Python code, modulo clocks have always operated strictly on integers (`step_count % K == 0`). Fractional clocks do not exist in the codebase. The reference to $2.5$ was strictly an average occupancy statistic.
4. **`Confirmed K2 Parent Branch` ($K_{\text{arb}} = 5$):**
   In `run_k2_confirmation.py`, arbitration is strictly governed by `if self.step_count % self.K_arbitration == 0:`, with `self.K_arbitration = 5`.
5. **`Current Proposed Composition` ($K_{\text{arb}} = 10$):**
   Proposed decimation to `self.K_arbitration = 10`, cutting the evaluation rate from $0.20$ to $0.10\text{ events/step}$.

---

## 2. Reconciliation of Historical Saving Figures ($\sim 4.2$ vs $\sim 2.8\text{ FP/step}$)

- **`~4.2 FP/step` Lineage:** Derived from a theoretical model in `CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01` that assumed arbitration cost scaled linearly with active candidate count ($3\text{ candidates} \times 14\text{ FP} = 42\text{ FP/event} \implies 4.2\text{ FP/step}$ saving).
- **`~2.8 FP/step` Lineage:** Derived from the **actual executable code** of the K2 branch, where arbitration logs a fixed $28.0\text{ FP}$ unconditionally per execution.
  $$\Delta \text{FP}_{\text{direct}} = \frac{28.0}{5} - \frac{28.0}{10} = 5.600000 - 2.800000 = \mathbf{2.800000\text{ FP/step}}.$$
- **Authoritative Determination:** Only the exact executable code of the K2 branch governs the composition study. The valid direct projected saving is **`2.800000 FP/step`**.
