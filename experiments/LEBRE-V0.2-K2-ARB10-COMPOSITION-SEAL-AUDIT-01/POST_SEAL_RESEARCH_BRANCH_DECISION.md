# Post-Seal Research Branch Decision

## 1. Comparison of Next Research Directions

| Research Branch | Scientific Motivation | Complexity | Causal Cleanliness | Recommendation |
| :--- | :--- | :---: | :---: | :---: |
| **Branch A: EMA Timescale Preservation** (`K_arb=10, alpha=0.0396`) | Directly tests if restoring stream memory window (247 steps) recovers switching agility while retaining 2.8 FP saving | Low (Parameter only) | **High** (Isolates EMA timescale effect under fixed K10) | **`RECOMMENDED_NEXT_STAGE`** |
| **Branch B: Event-Triggered Arbitration** | Asynchronously triggers arbitration on innovation spikes | High (New state routing logic) | Moderate (Coupled with trigger threshold tuning) | Future Hypothesis Only |
| **Branch C: Abandon Arbitration Decimation** | Assume scheduler staleness inherently breaks switching | N/A | N/A | Not Justified (Branch A untested) |

## 2. Recommended Next Stage
**`LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01`**  
A dedicated design stage to specify a 3-arm confirmatory trial ($B0, B1, B2$) isolating the stream-time pole restoration. No code execution without human review.
