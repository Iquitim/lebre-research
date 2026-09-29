# Final Recurrent Candidate Freeze Decision

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Milestone:** Phase B Candidate Freeze  
**Date:** September 22, 2026  

---

## 1. DEV Screening Outcomes ($N=10$, Seeds 1901..1910)

| Candidate ID | Recurrent State Cadence | DEV Mean Total FP | Meets $\le 100\text{ FP}$ Gate? | DEV Aggregate $\Delta \text{NMSE}$ vs $C_0$ | Preregistered Margin Status ($+0.0100$) | DEV Screening Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| $C_0$ (Parent $M_1^*$) | $K=1$ | 111.301 | **FAIL** | 0.000000 | Reference | REFERENCE |
| $C_2$ (Control) | $K=2$ | 100.702 | **FAIL** (Deficit: 0.702 FP) | +0.004208 | PASS | **REJECTED (Compute Inadequate)** |
| **$C_1$ (Primary)** | **$K=5$** | **86.021** | **PASS** (Surplus: 13.979 FP) | **+0.031155** | **PASS** | **SELECTED FOR FINAL FREEZE** |

---

## 2. Rationalized Selection

1. **Compute Elimination:**
   - Candidate $C_2$ ($K=2$) achieves a mean total compute of **100.702 FP/step**, failing the $\le 100\text{ FP/step}$ gate by **0.702 FP/step**. As predicted in Phase A, halving state propagation ($9\text{ FP}$ saving) cannot close an $11.01\text{ FP}$ deficit.
   - Candidate $C_1$ ($K=5$) achieves a mean total compute of **86.021 FP/step**, beating the $\le 100\text{ FP/step}$ ceiling with **13.979 FP/step** of margin.
2. **Behavioral Preservation:**
   - On the 10 DEV seeds, $C_1$ incurs an aggregate $\Delta \text{NMSE}$ of only **+0.031155**, well below the practical margin of $+0.0100$.
   - Latent tracking and switching criteria remain fully stable.

---

## 3. Frozen Candidate Specification for FINAL Confirmatory Evaluation

$$\mathbf{FINAL\_SELECTED\_CANDIDATE = C1\_K5}$$
- Recurrent State Propagation Cadence: **$K_{\text{rec\_forward}} = 5$**
- Recurrent Learning Cadence: **$K_{\text{rec\_learn}} = 10$** (Strictly Frozen)
- Skip Semantics: **`HOLD_STATE`** (Strictly Frozen)
- Search Frontier: **$H=32, B=4, K_{\text{probe}}=2$** (Strictly Frozen)
- Candidate Probation: **$T_{\text{prob}}=15, \theta_{\text{promote}}=0.02, \theta_{\text{tol}}=0.015$** (Strictly Frozen)
