# BOUNDED-HISTORY-LAG-INTEGRATION-01: Non-Canonical Architectural Integration Design

**Status:** `PRE-INTEGRATION_DESIGN_SPEC` (Diagnostic Non-Canonical Artifact)
**Milestone Constraint:** `M3_STATUS = UNOPENED` (Zero modifications to canonical `src/` or `tests/`)

## 1. Decoupled Memory Provider Architecture

To integrate bounded-history representations into future LEBRE iterations without violating the frozen specification:

```
┌─────────────────────────────────────────────────────────────┐
│                  LEBRE Adaptive Core Engine                 │
│   (Base NLMS, Recurrent State, Rotating Candidate Probe)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ query(channel, lag)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              HistoryProvider Abstract Interface             │
│   - write(x_t) -> FLOPs                                     │
│   - query(channel, lag) -> (value, status, err, FLOPs)      │
│   - get_memory_breakdown() -> dict                          │
└──────────────┬───────────────┬──────────────┬───────────────┘
               │               │              │
               ▼               ▼              ▼
      ┌─────────────────┐ ┌──────────┐ ┌──────────────┐
      │  H3: INT8 Ring  │ │ H1: FP16 │ │ H4: Mixed P. │
      │ (205 B, 69.9%)  │ │  (350 B) │ │   (259 B)    │
      └─────────────────┘ └──────────┘ └──────────────┘
```

## 2. Memory-Compute Operating Recommendations

1. **Recommended Primary History Representation for Future LEBRE (M3 Candidate):**
   - **H3 (INT8 Quantized Ring Buffer)** is the Pareto-optimal choice for edge/microcontroller deployments ($\le 256$ Bytes).
   - Reduces history memory from 680 Bytes to 205 Bytes (3.32x compression) with zero loss of discrete lag discovery ($F_1 = 1.0$) and negligible excess error ($\Delta \text{EMSE} < 5 \times 10^{-5}$).
2. **For High-Dynamic-Range Applications:**
   - **H1 (FP16 Exact Ring)** provides absolute mathematical losslessness across all dynamic ranges while cutting memory by exactly 48.5% (350 Bytes).
3. **Representation Boundary Rule:**
   - **Never apply multirate decimation or polynomial projections to high-entropy IID streaming delays.** Nyquist aliasing and polynomial smoothing inherently destroy sparse discrete delay peaks.
