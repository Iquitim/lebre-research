# Correlation Search Claim Dependency Graph
## Stage: LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01
## Target Parent: LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01

This document maps the epistemic and causal dependencies between the thirty-four (34) claims formulated in the parent stage `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`. It traces how root analytical errors, mistaken hypothesis test references, and unverified narrative extrapolations propagated through intermediate claims into final architectural conclusions.

---

## 1. High-Level Dependency Clusters

```mermaid
graph TD
    subgraph Cluster_Stat [Statistical Inference Cluster]
        Root_Stat["Root Error 1:<br/>Non-Inferiority Test cited as Superiority Test<br/>(margin +0.0100 yielded t=-4.57, p=4.2e-5)"]
        C1["C1: M1* achieves lower NMSE than R1 (t=-4.57, p=4.2e-5)"]
        C2["C2: M1* statistically significantly outperforms R1"]
        C3["C3: M1* achieves lower NMSE than R0 (t=-15.35)"]
        C11["C11: Large effect size d > 0.8 vs R1"]
        C26["C26: M1* Pareto dominates R1 across all dimensions"]
        Root_Stat --> C1
        C1 --> C2
        C1 --> C11
        C1 --> C26
        C3 --> C26
    end

    subgraph Cluster_Compute [Resource & Compute Accounting Cluster]
        Root_Compute["Root Error 2:<br/>Table Summation of Rounded Components<br/>(110.82 FP/step vs 111.01 empirical mean)"]
        C4["C4: M1* requires 110.82 FP/step online compute"]
        C12["C12: Compute savings over R1 is negligible or positive"]
        C17["C17: Constant compute floor is 88.45 FP/step"]
        C26_2["C26: Pareto Dominance Claim"]
        Root_Compute --> C4
        C4 --> C12
        C4 --> C26_2
        C17 --> C4
    end

    subgraph Cluster_Churn [Mechanistic Churn & Epistemic Filter Cluster]
        Root_Churn["Root Error 3:<br/>Narrative Extrapolation of Design Intent<br/>(Hypothesized Birth/Probation reduction never verified)"]
        C5["C5: Candidate births reduced by ~57%"]
        C6["C6: Failed probation waste reduced by ~70%"]
        C7["C7: Compact frontier functions as an epistemic filter"]
        C13["C13: Churn reduction explains superior tracking"]
        C14["C14: Higher signal-to-noise ratio in probation candidates"]
        Root_Churn --> C5
        Root_Churn --> C6
        C5 --> C7
        C6 --> C7
        C7 --> C13
        C7 --> C14
    end

    subgraph Cluster_Geometry [Memory & Queue Geometry Cluster]
        Root_Geom["Root Error 4:<br/>Spec-to-Implementation Divergence<br/>(Hypothetical 272-step spec vs 80-step circular buffer)"]
        C8["C8: Memory footprint reduced to 192B (330B -> 192B)"]
        C9["C9: Frontier queue guarantees revisit within 272 steps"]
        C10["C10: Dense correlation arrays permanently eliminated"]
        C21["C21: Circular pointer achieves deterministic coverage"]
        Root_Geom --> C9
        C8 --> C26
        C10 --> C26
        C21 --> C9
    end

    subgraph Cluster_Gov [Governance & Deprecation Cluster]
        C27["C27: Dense search is permanently deprecated"]
        C28["C28: Correlation Search Space Compaction is Supported"]
        C29["C29: M1* replaces R0 and R1 as canonical baseline"]
        C2 --> C28
        C26 --> C28
        C26 --> C27
        C28 --> C29
        C27 --> C29
    end
```

---

## 2. Root Cause Propagation Paths

### Propagation Path A: The Non-Inferiority Conflation (Statistical Lineage)
1. **Origin:** Script `scratch/postprocess_confirmatory_results.py` executed `scipy.stats.ttest_1samp(deltas_r1, 0.0100)` to test non-inferiority margin $+0.0100$. It returned $t = -4.56822, p = 4.20 \times 10^{-5}$.
2. **First-Hop Error (C1):** The author copied these exact values into Section 5 of the parent report and described them as a paired $t$-test against null hypothesis $H_0: \mu_{\Delta} = 0$.
3. **Second-Hop Propagation (C2, C11):** C2 asserted "overwhelming statistical significance ($p < 10^{-4}$)" and C11 asserted an exaggerated large effect size ($d > 0.8$) directly derived from the inflated $t$-statistic.
4. **Final-Hop Distortion (C26, C28):** Contributed to the false conclusion that $M_1^*$ was strictly superior and unequivocally passed the statistical gate, obscuring that the true effect size against zero is modest ($dz = -0.445, t = -2.435, p = 0.0213$) and failed on 11 of 30 seeds.

### Propagation Path B: The "Epistemic Filter" Fabrication (Mechanistic Lineage)
1. **Origin:** In the conceptual design phase, the author hypothesized that searching only top-variance coordinates would reduce false positive promotions, leading to lower candidate churn.
2. **First-Hop Error (C5, C6):** Without querying `candidate_births` or `failed_probation_flushes` in the raw CSV, the narrative asserted that candidate births dropped from $90.22$ to $38.8$ ($-57\%$) and probation waste dropped by $-70\%$.
3. **Second-Hop Propagation (C7, C13, C14):** C7 coined the term "epistemic noise filter" to explain why $M_1^*$ achieved lower NMSE. C13 and C14 argued that probation efficiency was the causal driver of improved tracking.
4. **Forensic Refutation:** The audit verified that candidate births actually *increased* ($90.22 \to 92.97$) and probation waste was unchanged ($1.711 \to 1.769\text{ FP/step}$). The actual causal mechanism was faster sweep frequency ($80\text{ steps}$ revisit period) boosting true delay discovery recall ($76.31\%$ vs $66.55\%$).

### Propagation Path C: The Queue Spec Desynchronization (Geometry Lineage)
1. **Origin:** An early design draft proposed an asymmetric partitioned queue ($H_{\text{track}} = 24$ slots polled every $4$ steps, $B_{\text{explore}} = 1$ slot polled every $34$ steps), which produced a theoretical revisit latency of $272\text{ steps}$.
2. **Implementation Change:** The implementation committed to code (`src/lebre/search/compact_frontier.py` / `m1_star`) was a simple uniform circular buffer: $160$ searchable coordinates, $B = 4$ coordinates per probe, $K_{\text{probe}} = 2$ steps.
3. **First-Hop Error (C9):** The report narrative uncritically retained the $272\text{ steps}$ figure from the preliminary spec.
4. **Forensic Reconciliation:** Actual revisit latency is $(160 / 4) \times 2 = 80\text{ stream steps}$.

### Propagation Path D: The Component Rounding Sum (Compute Accounting Lineage)
1. **Origin:** The resource breakdown table was assembled by summing analytical expectations of individual modules: Baseline ($88.45$) + Correlation Probing ($12.00$) + Frontier Maintenance ($5.37$) + Probation Overhead ($5.00$) = $110.82\text{ FP/step}$.
2. **First-Hop Error (C4):** Reported as the empirical mean total compute of $M_1^*$.
3. **True Empirical Value:** The exact mean of `total_fp_mean` in `CORRELATION_SEARCH_FINAL_RESULTS.csv` across all 420 runs is $111.013591\text{ FP/step}$.
4. **Governance Impact (C12, C26):** Obscured that $M_1^*$ consumes $+4.28\text{ FP/step}$ *more* compute than $R_1$ ($106.74\text{ FP/step}$), invalidating any claim of strict Pareto dominance.

---

## 3. Claim Adjudication Status Summary

| Status Category | Count | Associated Claims |
|:---|:---:|:---|
| **CONFIRMED / VERIFIED** | 16 | C3, C8, C10, C16, C18, C19, C20, C21, C22, C23, C24, C25, C30, C31, C32, C33 |
| **QUALIFIED / RECONCILED** | 9 | C1, C2, C4, C9, C11, C15, C17, C34, G5-G8 |
| **REFUTED / RETRACTED** | 9 | C5, C6, C7, C12, C13, C14, C26, C27, C28, C29 |

---

## 4. Architectural Impact on Subsequent Stages

```mermaid
graph LR
    subgraph Erroneous_Parent_Claims
        EP1["Claimed 70% probation savings"]
        EP2["Claimed strict Pareto dominance"]
        EP3["Claimed Dense Search permanently deprecated"]
    end
    subgraph Forensic_Audit_Corrections
        FC1["Probation waste unchanged (1.77 FP/step)"]
        FC2["Tradeoff: -0.0114 NMSE for +4.28 FP/step"]
        FC3["Dense Search retained as reference baseline"]
    end
    subgraph Next_Stage_Directives
        NS1["Next Stage: LEBRE-V0.2-CANDIDATE-PROBATION-COST-01<br/>Must target actual probation bottleneck"]
        NS2["M1* designated PROMISING_EXPERIMENTAL_CANDIDATE"]
        NS3["R0/R1 retained for benchmarking"]
    end
    EP1 -.->|Refuted by| FC1
    EP2 -.->|Refuted by| FC2
    EP3 -.->|Refuted by| FC3
    FC1 ==> NS1
    FC2 ==> NS2
    FC3 ==> NS3
```

By decoupling these erroneous claims, downstream stages will avoid attempting to optimize non-existent probation gains and will instead focus on the true bottleneck: optimizing candidate probation validation mechanisms and eliminating the $+4.28\text{ FP/step}$ compute penalty of the compact frontier.
