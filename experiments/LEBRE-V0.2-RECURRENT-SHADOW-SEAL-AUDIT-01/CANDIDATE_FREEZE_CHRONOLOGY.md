# Candidate Freeze Chronology & Integrity Audit

**Audit Target:** Execution sequence leading to candidate selection and final confirmatory run.

```mermaid
sequenceDiagram
    participant Protocol as Preregistration & Protocol
    participant PhaseA as Phase A Feasibility
    participant DEV as DEV Screening (N=10)
    participant Freeze as Candidate Freeze Doc
    participant FINAL as FINAL Execution (N=30)
    
    Protocol->>PhaseA: Define K=5 Primary, K=2 Control
    PhaseA->>DEV: Authorize DEV execution (Seeds 1901..1910)
    DEV->>Freeze: Generate metrics (K=5: 86.02 FP, +0.0312 NMSE; K=2: 100.70 FP, +0.0042 NMSE)
    Note over Freeze: TEMPLATE ERROR: Writes 'PASS' for +0.0312 based on historical D9F expectation
    Freeze->>FINAL: Freezes C1 (K=5) for confirmatory N=30 run
    FINAL->>FINAL: Confirmatory evaluation (Seeds 1911..1940) produces robust negative finding
```

### Chronological Verification:
1. **Preregistration Locked:** `RECURRENT_SHADOW_PREREGISTRATION.md` locked prior to DEV execution.
2. **Phase A Ruling:** `PHASE_A_FEASIBILITY_DECISION.md` authorized $C_1$ ($K=5$) as Primary Candidate and $C_2$ ($K=2$) as DEV negative control.
3. **DEV Execution:** Seeds $1901..1910$ executed cleanly.
4. **Candidate Freeze Document Created:** `FINAL_RECURRENT_CANDIDATE_FREEZE.md` authored by automated runner script.
5. **FINAL Execution:** Confirmatory evaluation executed across seeds $1911..1940$.
