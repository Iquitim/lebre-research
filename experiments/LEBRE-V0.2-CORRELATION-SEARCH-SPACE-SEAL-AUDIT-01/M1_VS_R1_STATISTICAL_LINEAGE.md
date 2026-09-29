# Statistical Lineage Reconciliation: M1* vs. R1

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Statistical-Lineage Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **RECONCILED & CORRECTED**  

---

## 1. The Discrepancy

In the parent study (`LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`), the final reports (`CORRELATION_SEARCH_FINAL_REPORT.md` and `CORRELATION_SEARCH_DECISION.md`) repeatedly asserted that Candidate $M_1^*$ was statistically superior to the dense multirate reference $R_1$, citing the following test statistic:
$$\Delta\text{NMSE} = -0.011417, \quad t = -4.57, \quad p = 4.20 \times 10^{-5}$$

However, an independent paired $t$-test conducted on the $N=30$ independent seed-level paired aggregates ($\text{NMSE}_{M1^*} - \text{NMSE}_{R1}$) testing the standard null hypothesis of no difference ($H_0: \mu_{\Delta} = 0$) yields:
$$\bar{\Delta} = -0.01141697, \quad s_{\Delta} = 0.02567862, \quad \text{SE} = 0.00468825$$
$$t(29) = \frac{-0.01141697 - 0}{0.00468825} = -2.43523, \quad p = 0.021265 \quad (\text{two-sided})$$
$$\text{One-sided } p = 0.010632, \quad \text{Wilcoxon } W = 121.0 \ (p = 0.020850), \quad \text{Cohen's } dz = -0.44461$$
$$\text{Seed Scorecard: } 19 \text{ wins}, \ 11 \text{ losses}, \ 0 \text{ ties}$$

---

## 2. Forensic Reconstruction of the Origin of $t = -4.57$

We traced the execution path in `scratch/postprocess_confirmatory_results.py` lines 99–108:
```python
        'comparison': "M1_STAR_vs_R1_DENSE_MULTIRATE",
        'n_seeds': len(FINAL_SEEDS),
        'mean_delta_nmse': mean_d_r1,
        'std_delta_nmse': std_d_r1,
        'se_delta_nmse': se_d_r1,
        'ci95_upper_onesided': ci95_upper_r1,
        'noninferiority_margin': 0.0100,
        'noninferiority_supported': "YES" if ci95_upper_r1 < 0.0100 else "NO",
        't_stat_vs_margin': float(stats.ttest_1samp(deltas_r1, 0.0100)[0]),
        'p_value_onesided': float(stats.ttest_1samp(deltas_r1, 0.0100)[1] / 2.0)
```

### Forensic Root Cause:
1. **The Code Tested Non-Inferiority Against Margin $+0.0100$:**
   In line 107, `scipy.stats.ttest_1samp(deltas_r1, 0.0100)` was executed. This computes:
   $$t_{\text{margin}} = \frac{\bar{\Delta} - 0.0100}{\text{SE}} = \frac{-0.01141697 - 0.01000000}{0.00468825} = \frac{-0.02141697}{0.00468825} = -4.56822$$
   The associated one-sided $p$-value for $H_0: \mu_{\Delta} \ge +0.0100$ evaluates to:
   $$p_{\text{one-sided}} = 4.203897 \times 10^{-5}$$
2. **Narrative Conflation of Test Types:**
   When compiling the narrative report, the author copied the values $t = -4.57$ and $p = 4.20 \times 10^{-5}$ from the `t_stat_vs_margin` and `p_value_onesided` columns of `PREDICTIVE_NONINFERIORITY.csv`, and presented them as the test of superiority over $R_1$ ($H_0: \mu_{\Delta} = 0$).
3. **Classification:** `STATISTICAL_AGGREGATION_ERROR` / `REPORTING_ERROR`.

---

## 3. Scientific Impact Assessment

- **Does the Effect Survive?** **YES.** $M_1^*$ remains statistically significantly better in predictive performance than $R_1$ under the correct seed-level test against zero ($p = 0.02126 < 0.05$).
- **Effect Size Adjustment:** The effect size is moderate (Cohen's $dz = -0.445$, 19 wins vs 11 losses), not overwhelming ($t = -4.57, p = 4.2 \times 10^{-5}$).
- **Governance Requirement:** All narrative claims citing $t = -4.57$ and $p = 4.20 \times 10^{-5}$ must be formally corrected to $t(29) = -2.44, p = 0.0213$.
