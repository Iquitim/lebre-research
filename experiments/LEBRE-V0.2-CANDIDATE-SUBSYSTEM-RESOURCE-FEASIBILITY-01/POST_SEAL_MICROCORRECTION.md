# Post-Seal Deterministic Microcorrection: Gate G8 & R0 Reconciliation
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Authority Level: Level 3 (Sealed Forensic Corrigendum)

---

## 1. Executive Summary & Root Cause Adjudication

During the forensic review of `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`, a discrepancy was identified in Section 6, Table "Gate Evaluation & Preregistered Success Criteria Re-adjudication":
> `| **G8** | Baseline Preservation | $R_0$ non-inferiority maintained | $M_1^*$ beats $R_0$ by $-0.0982$ NMSE | **PASSED** |`

This entry directly contradicted the confirmatory statistical artifact `PREDICTIVE_NONINFERIORITY.csv`, which reported:
$$\Delta_{\text{NMSE}}(M_1^* - R_0) = +0.013027, \quad \text{Upper 95% CI} = +0.019402, \quad \text{Margin} = +0.0100 \implies \mathbf{NOT\_SUPPORTED}$$

### Forensic Root Cause Determination:
The forensic investigation determined that this discrepancy was caused by a:
$$\mathbf{MANUAL\_TRANSCRIPTION\_ERROR \ / \ WRONG\_GATE \ / \ WRONG\_COLUMN}$$

In the parent study's preregistered criteria (`SUCCESS_CRITERIA_RECONCILIATION.md`, line 22), Gate G8 was defined as:
$$\mathbf{G8: \ Hybrid \ Complementarity \ on \ I_9} \quad (G_{D|B+R} > 0 \land G_{R|B+D} > 0)$$
The empirical values logged for task $I_9$ were $G_{D|B+R} = +0.0982$ and $G_{R|B+D} = +0.1341$ (**PASS**).

When compiling the final summary table in `CORRELATION_SEARCH_SEAL_AUDIT_FINAL_REPORT.md`, the author mistakenly substituted "Baseline Preservation ($R_0$ non-inferiority)" for Gate G8's title, copied the numerical value $+0.0982$ from the hybrid complementarity column, inverted its sign to $-0.0982$, and asserted that $M_1^*$ beat $R_0$ by $-0.0982$ NMSE.

---

## 2. Certified Level-1 Ground Truth: $M_1^*$ vs $R_0$

A complete, certified recomputation was executed on `CORRELATION_SEARCH_FINAL_RESULTS.csv` across all $N=30$ independent seeds ($s \in \{1811..1840\}$) and all 14 benchmark tasks:

$$\Delta_s = \overline{\text{NMSE}}(M_1^*, s) - \overline{\text{NMSE}}(R_0, s)$$

The exact empirical parameters (archived in `R0_G8_RECONCILIATION.csv`) are:
- **Number of Seeds ($N$):** $30$
- **Mean Difference ($\overline{\Delta}$):** $+0.0130265$ (Parent reported $+0.0130$)
- **Sample Standard Deviation ($s_{\Delta}$):** $0.0205543$
- **Standard Error ($\text{SE}_{\Delta}$):** $0.0037527$
- **One-Sided 95% Student-$t$ Critical Value ($t_{0.95, 29}$):** $1.699127$
- **One-Sided 95% Upper Confidence Bound:**
  $$\text{Upper 95% CI} = \overline{\Delta} + t_{0.95, 29} \times \text{SE}_{\Delta} = +0.0130265 + 1.699127 \times 0.0037527 = \mathbf{+0.0194023}$$
- **Preregistered Non-Inferiority Margin ($\epsilon$):** $+0.0100$
- **Non-Inferiority Hypothesis:** $H_0: \mu_{\Delta} \ge +0.0100$ vs $H_1: \mu_{\Delta} < +0.0100$.
- **Test Statistic vs Margin:**
  $$t = \frac{\overline{\Delta} - 0.0100}{\text{SE}_{\Delta}} = \frac{+0.0130265 - 0.0100}{0.0037527} = +0.806504, \quad p = 0.786741 \text{ (one-sided)}$$
- **Two-Sided Test vs Zero:**
  $$t(29) = \frac{+0.0130265}{0.0037527} = +3.47125, \quad p = 0.001642 \text{ (two-sided)}$$
- **Seed Win / Loss Scorecard:**
  - $M_1^* < R_0$ ($M_1^*$ better): $9\text{ seeds } (30.0\%)$
  - $M_1^* > R_0$ ($R_0$ better): $21\text{ seeds } (70.0\%)$

### Scientific Adjudication:
1. **$R_0$ Non-Inferiority Status:** **NOT_SUPPORTED (FAIL)**. Because the upper 95% bound ($+0.0194$) exceeds $+0.0100$, non-inferiority to continuous search $R_0$ is statistically refuted.
2. **Physical Explanation:** Continuous search $R_0$ probes every coordinate every step, providing faster re-locking on abrupt regime transitions ($I_{11}, I_{12}, I_{13}$) than $M_1^*$, whose circular queue requires 80 stream steps per sweep.
3. **Corrected Gate Status:**
   - **True Gate G8 (Hybrid Complementarity on $I_9$):** **PASSED** ($G_{D|B+R} = +0.0982, G_{R|B+D} = +0.1341$).
   - **Secondary Operational Criterion ($R_0$ Non-Inferiority):** **FAILED**.
