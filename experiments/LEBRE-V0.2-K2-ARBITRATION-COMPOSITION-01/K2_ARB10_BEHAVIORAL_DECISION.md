# Behavioral Decision: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Primary Behavioral Non-Inferiority Gate:** **`FAIL`**  
**Primary Contrast:** Arm $A2$ vs Arm $A0$ paired seed-level aggregate across all 14 tasks ($N=30$)  
**Mean Degradation ($\Delta$):** **`+0.014548 NMSE`**  
**One-Sided 95% Upper Confidence Bound:** **`+0.020204 NMSE`**  
**Preregistered Non-Inferiority Margin:** **`+0.010000 NMSE`**  
**Test Statistic:** $t_{\text{NI}} = 1.3660, \quad p_{\text{NI}} = 0.9088$

---

## 1. Analysis of Behavioral Findings
1. **$A1$ vs $A0$ (K2 Replication Check):** **PASS**
   - Mean $\Delta = +0.003196$, One-sided 95% upper bound = **`+0.004477 < +0.010000`** ($p_{\text{NI}} = 3.21 \times 10^{-10}$).
   - Confirms that the $K=2$ recurrent boundary reproduced its non-inferior behavior on fresh seeds `1971..2000`.
2. **$A2$ vs $A0$ (Combined End-to-End Primary Gate):** **FAIL**
   - Mean $\Delta = +0.014548$, One-sided 95% upper bound = **`+0.020204 > +0.010000`**.
   - The combined architecture violates the preregistered practical degradation margin.
3. **$A2$ vs $A1$ (Incremental Causal Effect of Arbitration Decimation):**
   - Mean $\Delta = +0.011352$, One-sided 95% upper bound = **`+0.016960`**.
   - Decimating arbitration from $K=5 \to 10$ accounts for the vast majority ($78.0\%$) of the total end-to-end degradation.

## 2. Decision
The primary predictive non-inferiority gate is **FAILED**.
