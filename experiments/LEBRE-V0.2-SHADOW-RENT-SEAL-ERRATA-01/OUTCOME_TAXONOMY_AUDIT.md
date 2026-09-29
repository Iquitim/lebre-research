# Primary Outcome Taxonomy Audit & Semantic Drift Reconciliation

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus Inquiry:** Issue D — Audit of the Primary Outcome Categorization Drift  

---

## 1. Executive Summary

In `SHADOW_RENT_FINAL_REPORT.md` (Section 8, Line 207) and `MANIFEST.json`, the parent study recorded the following terminal machine-readable outcome:
> `PRIMARY_OUTCOME = COMPUTE_RECOVERED_PREDICTIVE_DEGRADED`

This forensic audit cross-references this label against the authorized outcome taxonomy preregistered in the study design charter and prompt Section 59. 

The audit reveals a **formal taxonomy label mismatch**:
- The authorized preregistered label was **`COMPUTE_RECOVERED_BEHAVIOR_DEGRADED`**.
- The author substituted the term **`PREDICTIVE`** for **`BEHAVIOR`**, producing an unregistered category name (`COMPUTE_RECOVERED_PREDICTIVE_DEGRADED`).
- While the semantic intent of the author is fully consistent with the actual experimental findings (total compute was recovered under $100$ FP by $S_2$, but predictive fidelity and switching latency were degraded), strict confirmatory governance prohibits ad-hoc label mutations.
- This errata audit formally restores the binding preregistered label: **`COMPUTE_RECOVERED_BEHAVIOR_DEGRADED`**.

---

## 2. Preregistered Taxonomy Specification (Section 59)

The governing protocol defined an exhaustive, mutually exclusive set of 6 terminal outcomes for the shadow-rent study:

```
+-------------------------------------------------------------------------------------------------------------------+
| Taxonomy Identifier                              | Formal Criteria & Behavioral Meaning                           |
+-------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_ELIMINATED_BEHAVIOR_PRESERVED        | Total FP <= 100.0, Delta NMSE <= 0.0100, Switch Latency <= +50 |
|                                                  | All gates pass; duty cycling achieves ideal zero-cost savings. |
+-------------------------------------------------------------------------------------------------------------------+
| COMPUTE_RECOVERED_BEHAVIOR_PRESERVED             | Total FP <= 100.0, Predictive non-inferiority PASSES, but minor|
|                                                  | benign shifts in secondary metrics occur (all gates pass).     |
+-------------------------------------------------------------------------------------------------------------------+
| COMPUTE_RECOVERED_BEHAVIOR_DEGRADED              | Total FP <= 100.0 achieved by candidate, but predictive         |
|                                                  | non-inferiority FAILS or switching latency FAILS.              |
+-------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_UNAFFECTED                           | None of the tested duty-cycling mechanisms succeed in reducing  |
|                                                  | compute below the 100-FLOP ceiling.                            |
+-------------------------------------------------------------------------------------------------------------------+
| EXPLORATION_EXTINGUISHED_COLLAPSE                | Reducing shadow exploration leads to catastrophic failure of    |
|                                                  | temporal discovery (resembles S1 control).                     |
+-------------------------------------------------------------------------------------------------------------------+
| INCONCLUSIVE_INSUFFICIENT_POWER                  | High variance prevents statistically resolving non-inferiority.|
+-------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Analysis of the Observed Empirical State

Let us evaluate the empirical findings of the parent study against the criteria of the 6 authorized classes:

1. **Did any candidate achieve compute $\le 100.0$ FLOPs?**  
   **YES.** Configuration $S_2$ (Periodic $K=5$) achieved a mean total online compute of **$89.53\text{ FLOPs/step}$**, satisfying Gate 1.
2. **Was behavior preserved?**  
   **NO.**  
   - On Gate 2 (Predictive Non-inferiority), $S_2$ exhibited a mean degradation of $\Delta \text{NMSE} = +0.0567$ ($p_{\text{adj}} = 1.000$, failing the $+0.0100$ margin).
   - On Gate 4 (Switching Latency), $S_2$ exhibited massive structural recovery delays on regime transitions: $+582.5\text{ steps}$ on $I_{11}$ and $+763.0\text{ steps}$ on $I_{12}$, failing the $\le +50.0\text{ steps}$ requirement.
3. **Did catastrophic collapse occur?**  
   **NO.** $S_2$ significantly outperformed the blind control $S_1$ ($\Delta \text{NMSE}_{S_1 - S_2} = +0.0541$, $p < 10^{-10}$); structural discovery was delayed, not extinguished.
4. **Was statistical power sufficient?**  
   **YES.** With $N = 30$ independent pairs, the standard error of $\Delta \text{NMSE}$ was $0.0049$, providing statistical power $> 99\%$ to resolve the non-inferiority boundary.

### Mapping Determination
Under the preregistered taxonomy, this profile maps uniquely and unambiguously to:
$$\mathbf{COMPUTE\_RECOVERED\_BEHAVIOR\_DEGRADED}$$

---

## 4. Lineage of the Semantic Substitution

- **Author's Motivation:** The author observed that the primary operational degradation was in prequential mean squared error (NMSE), and colloquially wrote `PREDICTIVE_DEGRADED` instead of the system-level term `BEHAVIOR_DEGRADED`.
- **Governing Rule:** Confirmatory science requires that categorical labels in machine-readable blocks match the preregistered schema exactly to allow automated downstream aggregation.
- **Corrigendum Mandate:** In the final machine-readable block of `SHADOW_RENT_SEAL_ERRATA_FINAL_REPORT.md`, the outcome will be recorded strictly as `COMPUTE_RECOVERED_BEHAVIOR_DEGRADED`.
