# Minimal-Composition Future Eligibility Deliverable

**Stage:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Purpose:** Formal recommendation regarding eligibility for future multi-subsystem composition.

---

## 1. Evidence Synthesis

The $K=2$ recurrent boundary has satisfied:
1. Replicability across independent DEV ($N=30$) and CONFIRMATORY ($N=30$) cohorts.
2. Upper 95% CI bound on $\Delta \text{NMSE} = +0.003955 < +0.0100$.
3. 100% preservation of all temporal tracking and switching mechanisms.
4. Total floating-point load of `101.023\text{ FP/step}` (within $0.7\text{ FP}$ of strict closure).

---

## 2. Minimal Composition Recommendation

> [!IMPORTANT]
> **RECOMMENDATION: ELIGIBLE FOR FORMAL MINIMAL-COMPOSITION STUDY**
> 
> $K=2$ is certified as the **sole authorized recurrent-state decimation rate** for future composition.
> To close the remaining `1.023\text{ FP/step}` deficit to achieve strict $\le 100.0\text{ FP/step}$ compliance, a future preregistered experiment (`LEBRE-V0.2-MINIMAL-COMPOSITION-01`) is authorized to combine:
> 1. $K_{\text{rec\_forward}}=2$ (recurrent decimation, saves $17.0\text{ FP}$).
> 2. Candidate probation early rejection / observation decimation ($K_{\text{cand\_obs}}=5 \to 10$ or similar minimal intervention, saving $\sim 0.8\text{ to } 1.2\text{ FP}$).
> 
> Under no circumstances should $K=3$ or $K=4$ be used to close this deficit, as they violate state continuity.
