# Claim Dependency Graph: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

```mermaid
graph TD
    K_ARB["Intervention: K_arb 5 -> 10 (alpha=0.02 fixed)"]
    
    %% Direct Branch
    K_ARB --> ARB_OPP["Arbitration Cadence Halved (10-step period)"]
    K_ARB --> EMA_UPD["Gain-EMA Updates Halved in Stream Time"]
    
    %% Decision Staleness Path
    ARB_OPP --> SCHED_AGE["Scheduler Decision Age Increases (+5 max steps)"]
    
    %% EMA Timescale Path
    EMA_UPD --> TAU_DOUBLE["Effective Stream Filter Pole Doubles (247 -> 495 steps)"]
    TAU_DOUBLE --> GAIN_TRAJ["Slower Gain-EMA Evidence Trajectory"]
    GAIN_TRAJ --> THRESH_DELAY["Delayed Threshold Crossings (150-250 stream steps)"]
    
    %% Structural & Behavioral Path
    SCHED_AGE --> STRUC_DELAY["Delayed Structural Promotions / Evictions"]
    THRESH_DELAY --> STRUC_DELAY
    STRUC_DELAY --> UNDERMODEL["Task-Conditional Under-Modeling (I12 delay taps, I10 latching)"]
    
    UNDERMODEL --> LIVE_SAVING["Indirect Live Structural Saving (+0.92 FP)"]
    UNDERMODEL --> BEH_FAIL["Prediction NMSE Degradation (+0.0145)"]
    UNDERMODEL --> SW_FAIL["Switching Latency Breach (I11: +76 steps, I12: +214 steps)"]
    
    %% Resource Path
    ARB_OPP --> DIR_SAVING["Direct Arbitration Saving (2.80 FP/step)"]
    DIR_SAVING --> RES_CLOSURE["Total Compute 96.96 FP/step (<= 100.0 PASS)"]
    LIVE_SAVING --> RES_CLOSURE
    
    %% Final Outcomes
    BEH_FAIL --> NI_FAIL["Primary End-to-End NI FAIL (+0.0202 > +0.0100)"]
    SW_FAIL --> GUARD_FAIL["Switching Guardrail FAIL (I11 and I12)"]
    
    style K_ARB fill:#f9f,stroke:#333,stroke-width:2px
    style RES_CLOSURE fill:#dfd,stroke:#333,stroke-width:2px
    style NI_FAIL fill:#fdd,stroke:#333,stroke-width:2px
    style GUARD_FAIL fill:#fdd,stroke:#333,stroke-width:2px
```

### Resource Projection Lineage Comparison
```
Historical Baseline: 101.02 FP ──[-2.80 Direct]──> Projected: 98.22 FP ──> Observed: 96.96 FP (Residual: -1.27 FP)
Concurrent Baseline: 100.67 FP ──[-2.80 Direct]──> Projected: 97.87 FP ──> Observed: 96.96 FP (Indirect: +0.92 FP)
```
