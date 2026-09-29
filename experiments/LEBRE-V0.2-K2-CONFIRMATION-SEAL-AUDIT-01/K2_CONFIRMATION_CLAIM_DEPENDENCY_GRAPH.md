# Claim Dependency Graph & Scientific Robustness

```mermaid
graph TD
    RawData["Level-1 Raw Results (840 runs, 30 fresh seeds)"] --> SeedStats["Seed-Level NMSE (Delta = +0.002714, Upper95 = +0.003955)"]
    RawData --> TemporalMechanisms["Temporal Mechanisms (I6, I7, I9, I11..I14)"]
    RawData --> RawCompute["Raw Compute Telemetry (C0 = 111.24 FP, C2 = 101.02 FP)"]
    
    SeedStats --> BehBoundary["K2 Confirmed Behavioral Boundary (VALID)"]
    TemporalMechanisms --> BehBoundary
    
    RawCompute --> StrictGate["Strict Gate <= 100.0 FP (FAIL, +1.02 FP)"]
    RawCompute --> NearMissGate["Near-Miss Gate <= 101.0 FP (FAIL at full precision, +0.02 FP)"]
    RawCompute --> TrueSaving["True Saving = 10.21 FP (-9.18%)"]
    
    TrueSaving -.-> NarrativeError["Reported 17.000 FP (STALE TEMPLATE ERROR)"]
    NearMissGate -.-> RoundingError["Reported Near-Miss PASS (DISPLAY ROUNDING ERROR)"]
    
    BehBoundary --> MinimalComp["Future Minimal Composition Eligibility"]
    StrictGate --> AuxiliaryNeeded["Auxiliary Lever Required (Net Saving >= 1.023 FP)"]
    
    AuxiliaryNeeded --> EarlyRej["Early Rejection Alone (Net 0.83 FP < 1.02 FP -> INSUFFICIENT)"]
    AuxiliaryNeeded --> ArbDecim["Arbitration Decimation (Net 2.80 FP > 1.02 FP -> SUFFICIENT)"]
```

### Explanatory Note on Evidentiary Independence
The dependency graph confirms that narrative reporting errors (the 17-FP template string, display rounding of the near-miss gate, and the correlation wording) are terminal leaf artifacts. They do not feed into the Level-1 raw data or the statistical lineage proving predictive non-inferiority and temporal mechanism preservation. Correcting these reporting defects leaves the core scientific behavioral boundary 100% intact.
