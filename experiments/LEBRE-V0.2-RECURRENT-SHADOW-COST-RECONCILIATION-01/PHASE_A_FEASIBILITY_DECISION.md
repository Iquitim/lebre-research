# Phase A Feasibility Adjudication & Decision Gate

**Stage ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Layer:** Phase A (Deterministic Subsystem Reconciliation)  
**Adjudicator:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Summary of Reconciled Resource Accounting

1. **Exact 20.20 FP Reconciliation:**
   - Forward State Propagation (Op R1, R2, R3) + Prediction (Op R4, R5): $12.0 + 6.0 = 18.000000\text{ FP/step}$ ($K_{\text{rec\_fwd}} = 1$).
   - RTRL Sensitivities (Op R6) + Parameter Learning (Op R7, R8, R9) + Evidence EMA (Op R10): $(8.0 + 8.0 + 6.0) / 10 = 2.200000\text{ FP/step}$ ($K_{\text{rec\_learn}} = 10$).
   - Sum: $18.000000 + 2.200000 = \mathbf{20.200000\text{ FP/step}}$ (Exact match, tolerance $< 10^{-9}$).
2. **Current Total Online Compute ($M_1^*$):**
   $$\text{Total FP} = 75.468234\text{ (live)} + 7.900724\text{ (probe)} + 7.444633\text{ (candidate)} + 20.200000\text{ (recurrent)} = \mathbf{111.013591\text{ FP/step}}$$
3. **Required Budget Saving:**
   $$\Delta \text{FP} = 111.013591 - 100.000000 = \mathbf{11.013591\text{ FP/step}}$$
4. **Maximum Permissible Recurrent Compute for $\le 100\text{ FP}$ Ceiling:**
   $$\text{Max Recurrent FP} = 20.200000 - 11.013591 = \mathbf{9.186409\text{ FP/step}}$$
   $$\text{Required Recurrent Reduction} = \frac{11.013591}{20.200000} \approx \mathbf{54.5227\%}$$

---

## 2. Cadence Feasibility Adjudication

| Cadence Candidate | Projected Recurrent FP/step | Recurrent Saving (FP/step) | Projected Total Compute (FP/step) | Meets $\le 100\text{ FP}$ Gate? | Historical DEV $\Delta \text{NMSE}$ | Historical Margin ($+0.0100$) Status | Feasibility Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $K=1$ (Current $M_1^*$) | $20.200000$ | $0.000000$ | $111.013591$ | **FAIL** | $0.000000$ | Reference | BASELINE |
| $K=2$ | $11.200000$ | $9.000000$ | $102.013591$ | **FAIL** | $+0.001374$ | PASS | **INSUFFICIENT LEVERAGE** |
| **$K=5$** | **$5.800000$** | **$14.400000$** | **$96.613591$** | **PASS** | **$+0.002858$** | **PASS** | **VIABLE CANDIDATE** |
| $K=10$ | $4.000000$ | $16.200000$ | $94.813591$ | **PASS** | $+0.010144$ | **FAIL** | **MARGIN BREACHED** |

---

## 3. Formal Adjudication Decisions

1. **Can recurrence alone close the 11.013591-FP gap?**
   $$\mathbf{RECURRENCE\_ALONE\_CAN\_MATHEMATICALLY\_CLOSE\_100\_GATE = YES}$$
2. **Is $K=2$ sufficient for compute closure?**
   $$\mathbf{K2\_COMPUTE\_SUFFICIENT = NO} \quad (102.01 > 100.0)$$
3. **Is $K=5$ sufficient for compute closure?**
   $$\mathbf{K5\_COMPUTE\_SUFFICIENT = YES} \quad (96.61 \le 100.0)$$
4. **Does prior mechanistic evidence support $K=5$?**
   $$\mathbf{PRIOR\_EVIDENCE\_SUPPORTS\_K5 = YES} \quad (\Delta \text{NMSE} = +0.002858 < +0.0100)$$
5. **Phase A Classification Outcome:**
   $$\mathbf{PHASE\_A\_OUTCOME = RECURRENT\_SUBSYSTEM\_STRONG\_RESOURCE\_LEVER}$$

---

## 4. Phase B Authorization Gate

Phase A has satisfied all preregistered requirements:
- Ledger reconciles to $20.200000\text{ FP/step}$ exactly.
- Mathematical closure is proven ($K=5$ recovers $14.40\text{ FP/step}$, achieving $96.61\text{ FP/step}$).
- Prior evidence demonstrates behavioral viability within the $+0.0100$ margin.
- Fresh seed provenance is established ($1901..1910$ DEV, $1911..1940$ FINAL).

Therefore:
$$\mathbf{PHASE\_B\_AUTHORIZED = YES}$$

**Authorized Study Arms for Phase B:**
- Primary Candidate: $K_{\text{rec\_state}} = 5$ (Evaluated on DEV $N=10$, then FINAL $N=30$).
- Control Candidate: $K_{\text{rec\_state}} = 2$ (Evaluated on DEV $N=10$ only, as resource negative control).
