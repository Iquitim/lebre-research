# Recurrent Seal Claim Dependency Graph

```mermaid
graph TD
    K[Recurrent State Cadence K=5] -->|Decimation| H[HOLD_STATE Skip Semantics]
    H -->|Zero-Order Hold| LAG[Severe State Lag & Step Distortion: Path MAE=0.5810]
    LAG -->|Degraded Shadow Prediction| EV[Evidence Collapse on Latent Tasks I6, I7, I9, I10]
    EV -->|Lifecycle Arbitration| EVICT[Loss of Promotion / Premature Eviction of Live Recurrence]
    
    H -->|Direct Shadow Clock| SAV_SH[Direct Recurrent Shadow Saving: 14.41 FP/step]
    EVICT -->|Unoccupied Live Recurrence| SAV_LIVE[Indirect Live Filtering Drop: 10.49 FP/step]
    
    SAV_SH -->|Sum| TOT_SAV[Total Empirical Saving: 24.91 FP/step]
    SAV_LIVE -->|Sum| TOT_SAV
    TOT_SAV -->|Compute Result| COMP_PASS[Total Compute = 85.98 FP/step <= 100.0: PASS]
    
    LAG -->|Predictive Degradation| NMSE_FAIL[Delta NMSE = +0.0321 > +0.0100: BEHAVIORAL FAIL]
    EV -->|Loss of Complementarity| I9_FAIL[I9 G_R|B+D < 0: COMPLEMENTARITY FAIL]
    EVICT -->|Delayed Adaptation| SWITCH_FAIL[I11 Latency +246 steps > +50: SWITCHING FAIL]
```

### Crucial Architectural Insight:
The graph shows that the compute pass ($85.98\text{ FP}$) and the predictive failure ($+0.0321\text{ NMSE}$) are **causally intertwined**: the extra $10.5\text{ FP}$ needed to get well below $100\text{ FP}$ was caused by the system losing its live recurrent filters due to state distortion!
