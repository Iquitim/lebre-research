# LEBRE v0.2 Seal Audit Itemized Errata Corrigendum

**Document Identifier:** `LEBRE_V0_2_SEAL_AUDIT_ERRATA_CORRIGENDUM.md`  
**Audit Reference:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Parent Forensic Audit:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  

---

## 1. Itemized Errata Table

| Item ID | Original Claim / Text | Original Value | Recomputed Value | Root Cause | Error Class | Statistical Impact | Architectural Impact | Corrected Wording |
|:---|:---|:---:|:---:|:---|:---|:---|:---|:---|
| **ERR-01** | Cascade order discrepancy on $I_4$ | $0.1654$ ($p < 10^{-6}$) | $0.000772$ ($p = 0.8872$) on $I_4$; $0.165426$ on $I_8$ | Conflation of pasted DEV $I_4$ table with $I_8$ benchmark maximum and $T_3$ vs. $T_1$ p-value | `REPORT_COPY_FORWARD_ERROR`, `STATISTICAL_LINEAGE_ERROR` | $H_7$ inferential significance on $I_4$ is refuted; zero tasks survive Holm multiplicity | Cascade rejection does not rely on $I_4$; $T_3$ evaluation symmetry verified independently | "Sequential cascades exhibit stochastic order sensitivity descriptively (mean absolute difference reaches $0.1654$ on $I_8$ and $0.1586$ on $I_3$), but differences on $I_4$ are negligible ($0.0008, p=0.887$)." |
| **ERR-02** | $T_2$ redundant dual allocation on $I_{10}$ | $48.2\% \pm 0.112$ | $100.0\%$ dual occupancy (`frac_both = 1.000`); $0.15\%$ software redundant rate | Copy-forward from DEV screening logs (DEV $T_2$ NMSE was $0.482682$) | `REPORT_COPY_FORWARD_ERROR`, `METRIC_DEFINITION_ERROR` | Headline figure 48.2% was not a confirmatory measurement | Strengthens rejection of $T_2$: $T_2$ suffers permanent 100% double payment on $I_{10}$ | "$T_2$ suffered permanent 100.0% steady-state dual occupancy on $I_{10}$, incurring +28.6% live FLOP waste with no accuracy improvement over $T_3$." |
| **ERR-03** | Definition of $ho_{	ext{order}}$ in $H_7$ | $\max_i \|NMSE_i(T_1) - NMSE_i(T_{1R})\|$ | $rac{1}{N}\sum \mathbb{I}(	ext{Alloc}_{T1} 
e 	ext{Alloc}_{T1R})$ on $I_{10}$ | Post-hoc metric substitution following result inspection | `METRIC_DEFINITION_ERROR`, `POST_SELECTION_INFERENCE_ERROR` | Preregistered $ho_{	ext{order}} = 0.000$ (both allocate BOTH); falsified under original formal definition | Auxiliary rationale only; $T_3$ selection justified by aggregate accuracy and Pareto dominance | "Under its preregistered structural definition, $H_7$ is not supported; cascades are evaluated by predictive divergence and loss of arbitration." |
| **ERR-04** | Inference on post-selection maximum | Single-task confirmatory claim on maximum task | Family-wise Holm-Bonferroni testing across 14 tasks | Selecting maximum task after observing data without multiplicity adjustment | `POST_SELECTION_INFERENCE_ERROR` | Raw $p$-values do not survive family-wise correction | Scopes order sensitivity to descriptive benchmark characterization | "Across the 14-task benchmark family, cascade order sensitivity is observed as a descriptive sample divergence on specific delay streams." |
