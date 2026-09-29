# Dense Search Deprecation Governance Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Governance Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **GOVERNANCE OVERSTATEMENT OVERRULED**  

---

## 1. Audit of the "Permanently Deprecated" Claim

### The Narrative Claim:
In `CORRELATION_SEARCH_FINAL_REPORT.md` Q25 and `CORRELATION_SEARCH_DECISION.md` Section 3:
> "Dense 160-cell correlation state matrices are permanently deprecated and purged from the v0.2 runtime architecture."

---

## 2. Governance Evaluation Rules

Under established research governance and Level 3 preregistration rules:
1. An existing baseline or architectural component can be **permanently deprecated** if and only if its replacement satisfies **all preregistered validation gates** without performance regression.
2. In this study, while $M_1^*$ eliminated dense arrays from memory and outperformed the dense multirate reference $R_1$, it **failed two mandatory global gates**:
   - Primary Predictive Non-Inferiority vs Continuous Dense Reference $R_0$: $\bar{\Delta} = +0.0130 > +0.0100$ ($\text{CI}_{95\%} = +0.0194$);
   - Total Online Compute Ceiling: $111.01\text{ FP/step} > 100.00\text{ FP/step}$.
3. Furthermore, on benchmark tasks requiring immediate detection of newly introduced delays ($I_3, I_4, I_{11}, I_{12}$), continuous dense probing ($R_0$) demonstrated strictly lower predictive error and faster recovery than decimated sparse probing.

---

## 3. Governance Ruling

```text
DENSE_SEARCH_PERMANENTLY_DEPRECATED = NO
```

### Mandatory Governance Corrective Actions:
1. Dense continuous reference $R_0$ and dense multirate reference $R_1$ **must remain active scientific comparators** in the LEBRE benchmark and test suites.
2. The compacted sparse frontier ($M_1^*$) is adopted as:
   `PROMISING_EXPERIMENTAL_SPARSE_SEARCH_CANDIDATE`
   within the experimental multirate branch, not as a canonical replacement.
3. Classification: **`GOVERNANCE_OVERSTATEMENT`**.
