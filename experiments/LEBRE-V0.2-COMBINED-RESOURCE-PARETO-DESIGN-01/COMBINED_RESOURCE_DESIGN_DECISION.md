# Combined Resource Design Decision

**Decision:** `K2_ARB10_COMPOSITION_DESIGN_AUTHORIZED`

---

## 1. Justification

1. **Analytical Leverage Verified:**
   Decimating arbitration from $K_{\text{arb}}=5 \to 10$ yields a net direct saving of **`2.800000 FP/step`**.
   This is substantially greater than the strict deficit of **`1.023283 FP/step`** ($2.74\times$ coverage).
2. **Projected Static Clearance:**
   Under static projection, combined compute lands at **`98.223283 FP/step`**, providing **`1.776717 FP/step`** of headroom below the strict $100.0\text{ FP/step}$ ceiling.
3. **Single-Intervention Governance:**
   The future study alters exactly one parameter relative to confirmed K2 ($K_{\text{arb}}: 5 \to 10$). All other subsystems (search, recurrent, candidate lifecycle, live linear) remain frozen.
4. **Epistemic Discipline:**
   No novelty claims, no global v0.2 validation claim, Gate 6 remains permanently failed, and M3 remains unopened.
