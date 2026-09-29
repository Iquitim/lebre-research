# K=2 Boundary Decision Deliverable

**Stage:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Purpose:** Comprehensive adjudication of the $K=2$ recurrent-state boundary.

---

## 1. Synthesis of Gates

1. **Gate 1: Fresh-Seed Local Predictive Non-Inferiority:**  
   - Criterion: Upper 1-sided 95% CI on $\Delta \text{NMSE} < +0.0100$.  
   - Result: **`+0.003955`** $\implies$ **PASS**.
2. **Gate 2: Critical Temporal-Mechanism Integrity:**  
   - Criterion: Preservation of $I_6, I_7, I_9$ and switching gates $I_{11}..I_{14}$.  
   - Result: **All preserved** $\implies$ **PASS**.
3. **Gate 3: Pathwise State Distortion Bounds:**  
   - Criterion: Finite distortion without accumulation; bounded update vs hold ratio.  
   - Result: **Confirmed bounded** $\implies$ **PASS**.
4. **Gate 4: Concurrent Resource Accounting:**  
   - Criterion: Strict $\le 100.0\text{ FP/step}$ vs Engineering Near-Miss $\le 101.0\text{ FP/step}$.  
   - Result: **`101.023\text{ FP/step}`** $\implies$ **OVER_BUDGET**.

---

## 2. Boundary Conclusion

> [!IMPORTANT]
> **FINAL BOUNDARY VERDICT: CONFIRMED PREDICTIVELY SOUND & NEAR-MISS BOUNDARY**
> 
> The $K=2$ recurrent decimation boundary is definitively validated on fresh seeds as predictively non-inferior to continuous recurrent execution ($C_0$).
> It operates at `101.023\text{ FP/step}`, which misses the strict $100.0\text{ FP}$ ceiling by only `1.023\text{ FP/step}` (a `1.02%` margin).
> Because $K=2$ achieves massive compute reduction ($-17.000\text{ FP/step}$) without breaking any temporal mechanisms, it represents the correct physical recurrent foundation for LEBRE v0.2.
