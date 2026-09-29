# Forensic Audit: Transferability of Prior D9F / D9L Multirate Evidence

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Prior Stages Audited:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01` & `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Date:** September 22, 2026  

---

## 1. Prior Evidence Summary

In stage `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01` and its forensic seal audit `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`, single-component downsampling was evaluated on DEV seeds `1701..1710` ($N=10$):

| Condition ID | Evaluated Cadence | Delta NMSE vs Continuous | I6 NMSE (Latent) | I7 NMSE (Quiescent) | Practical Margin (+0.0100) Status | Certified Finding |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `REC_FWD_K1` | $K=1$ (Ref) | $0.000000$ | $0.140742$ | $0.146495$ | REFERENCE | Base |
| `REC_FWD_K2` | $K=2$ | $+0.001374$ | $0.141870$ | $0.150055$ | **PASS** | Minor degradation |
| `REC_FWD_K5` | $K=5$ | $+0.002858$ | $0.144224$ | $0.158662$ | **PASS** | Sub-margin degradation |
| `REC_FWD_K10`| $K=10$ | $+0.010144$ | $0.155712$ | $0.192111$ | **FAIL** | Exceeds +0.0100 margin |
| `REC_LRN_K10`| $K=10$ | $-0.000203$ | $0.141991$ | $0.151320$ | **PASS** | Cadence-insensitive |

---

## 2. Refutation of Historical Overclaim

In `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`, Claim C05 (*"Recurrent forward state propagation K=1 is strictly required"*) was formally audited and classified as **CAUSAL_ATTRIBUTION_OVERREACH**. The seal audit certified:
$$\mathbf{RECURRENT\_STATE\_K1\_STRICTLY\_REQUIRED = NO}$$
$$\mathbf{RECURRENT\_STATE\_PROPAGATION\_MORE\_CADENCE\_SENSITIVE = YES}$$

Decimating state forward propagation to $K=2$ or $K=5$ produces small, bounded degradations ($+0.00137$ and $+0.00286$) that remain safely within the project's practical margin of $+0.0100$.

---

## 3. Transferability Comparison to Current M1*

| Subsystem Dimension | Historical Multirate Stage (`SHADOW-MULTIRATE-01`) | Current $M_1^*$ Stage (`RECURRENT-SHADOW-01`) | Match Status |
|:---|:---|:---|:---:|
| Recurrent State Equation | Scalar tanh RTRL: $h_t = a h_{t-1} + b x_t$ | Scalar tanh RTRL: $h_t = a h_{t-1} + b x_t$ | **IDENTICAL** |
| Parameter Learning Rule | Normalized LMS with gradient clipping | Normalized LMS with gradient clipping | **IDENTICAL** |
| Floating Point Precision | FP32 | FP32 | **IDENTICAL** |
| Recurrent Evidence / EMA | $lpha = 0.02, 	ext{gain} = (y - \hat{y}_{	ext{base}})^2 - e_{	ext{rec}}^2$ | $lpha = 0.02, 	ext{gain} = (y - \hat{y}_{	ext{base}})^2 - e_{	ext{rec}}^2$ | **IDENTICAL** |
| Promotion Criteria | Evidence $> 0.02$, Obs count $\ge 15$ | Evidence $> 0.02$, Obs count $\ge 15$ | **IDENTICAL** |
| Upstream Search Policy | Dense 160-cell grid probing ($R_1$) | Rotating Sparse Frontier ($M_1^*, H=32, B=4$) | **DIFFERENT** |
| Candidate Arrival Rate | Higher spurious arrival on dense grid | Lower candidate birth rate on sparse frontier | **DIFFERENT** |

---

## 4. Formal Transferability Classification

Because the upstream temporal discovery frontier was changed from dense search ($R_1$) to sparse search ($M_1^*$), residual dynamics and candidate arrival trajectories are not identical.

Therefore, prior D9F/D9L behavioral values are classified as:
$$\mathbf{PRIOR\_D9F\_D9L\_TRANSFERABILITY = MECHANISTICALLY\_RELEVANT\_NOT\_CONFIRMATORY}$$

The prior numbers provide strong mechanistic plausibility that $K=5$ will remain within the $+0.0100$ margin, but confirmatory revalidation on the current $M_1^*$ branch is required.
