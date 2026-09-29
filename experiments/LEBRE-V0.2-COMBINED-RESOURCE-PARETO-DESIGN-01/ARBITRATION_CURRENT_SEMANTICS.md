# Arbitration Subsystem: Architectural Semantics & Code Audit

## 1. Disentangling "Promotion Check" from "Arbitration" (B6)

Historical documentation conflated two distinct operations under the umbrella label `"arbitration"`:
1. **Recurrent Shadow Promotion Check (R11):**
   Inside the arbitration trigger, the code checks whether the recurrent shadow unit meets promotion criteria (`rec_evidence > 0.02 and rec_obs_count >= 15`). In the recurrent shadow operation ledger, this check was recorded with an operation cost of $0.0\text{ FP}$ and $2\text{ INT}$ ops.
2. **Descendant Counterfactual Gain Arbitration (Stage 10):**
   The mathematical machinery that evaluates conditional errors ($e_{\text{base}}, e_D, e_R, e_{DR}$), computes raw gains, and updates exponential moving averages. This process costs exactly $28.0\text{ FP}$ per event ($5.600000\text{ FP/step}$ at $K=5$).

**Audit Clarification:** The promotion check is merely a boolean condition evaluation ($0\text{ FP}$) executed *downstream* of the counterfactual gain filtering ($28.0\text{ FP}$). They are separated in the operation ledger as `OP_ARB_01..03` (Gain Evaluation, $28.0\text{ FP}$) and `OP_ARB_07..08` (Promotion Decision, $0\text{ FP}$).

---

## 2. Occupancy Independence of Arbitration Cost (B7)

In `run_k2_confirmation.py` lines 179–194:
```python
if self.step_count % self.K_arbitration == 0:
    self.shadow_res.fp_flops += 28.0
    self.candidate_arb_flops += 28.0
    ...
```
- The operation cost is logged **unconditionally** every 5 steps.
- Whether zero, one, two, or three candidate taps are currently under probation, the counterfactual evaluation evaluates the best candidate (or zero if none exist), computing the exact 4-quadruplet error and 4 EMAs.
- Therefore, arbitration compute is **strictly periodic and occupancy-independent**.
$$\text{CURRENT\_ARBITRATION\_FP\_PER\_STEP} = \frac{28.0}{K_{\text{arb}}} = \frac{28.0}{5} = \mathbf{5.600000\text{ FP/step}}.$$
$$\text{PROJECTED\_K10\_ARBITRATION\_FP\_PER\_STEP} = \frac{28.0}{10} = \mathbf{2.800000\text{ FP/step}}.$$

---

## 3. Behavioral Role: Why Arbitration is NOT Mere Bookkeeping (B2)

Arbitration directly controls the dynamical trajectory of the model:
1. **Structural Selection:** Determines when an active delay tap or recurrent unit is promoted to live prediction or evicted.
2. **Dual-Occupancy Regulation:** Governs whether a task operates with dual complementary models (`BOTH`) or collapses to a single representation.
3. **Switching Latency:** Directly bounds the speed at which the model detects a regime transition and replaces stale parameters.
