# Confirmatory Candidate Freeze Decision

**Study ID:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Date:** September 2026  

---

## 1. Frozen Candidate Specification

$$\mathbf{CONFIRMATORY\_CANDIDATE = C2\_K2}$$
- **Recurrent State Propagation Cadence:** $K_{\text{rec\_forward}} = 2$
- **Recurrent Learning Cadence:** $K_{\text{rec\_learn}} = 10$ (Strictly Frozen)
- **Skip Semantics:** `HOLD_STATE` (Zero-order hold on odd steps)
- **Search Frontier:** $H=32, B=4, K_{\text{probe}}=2$ (Strictly Frozen)
- **Candidate Probation:** $T_{\text{prob}}=15, \theta_{\text{promote}}=0.02, \theta_{\text{tol}}=0.015$ (Strictly Frozen)
- **Arbitration Cadence:** $K_{\text{arb}}=5$ (Strictly Frozen)

---

## 2. Confirmatory Evaluation Plan

- **Cohort Size:** $N = 30$ independent seeds ($1941..1970$).
- **Benchmark Tasks:** All 14 benchmark tasks ($I_1..I_{14}$).
- **Total Execution Runs:** 840 runs (420 runs for $C_0$, 420 runs for $C_2$).
- **Synchronized State Telemetry:** State register $h_t$ logged every timestep for all 840 runs to calculate exact pathwise distortion.
- **Strict Invariant:** Zero modification of candidate probation, search frontier, learning rates, or canonical repository files.
