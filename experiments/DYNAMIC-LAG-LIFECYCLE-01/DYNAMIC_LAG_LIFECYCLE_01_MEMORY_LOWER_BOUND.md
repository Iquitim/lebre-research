# DYNAMIC-LAG-LIFECYCLE-01: Fundamental Memory Lower Bound & Information Storage Audit
## The "Sparse Weights but Dense History" Dilemma in Micro-Edge Streaming Systems

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Auditor:** Embedded Systems Researcher, Adaptive Signal Processing Specialist, Reproducibility Auditor  
**Date:** September 2026  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Resource Envelope:** R2-FLOP $\le 100$ FLOPs/step, R2-MEM $\le 1024$ Bytes persistent state

---

## 1. Executive Summary & The Core Physical Dilemma

In `CAPACITY-DECOMPOSITION-01`, variant $T5$ demonstrated that an oracle sparse lag set (3 active taps at lags 4, 8, and 30) achieved optimal predictive performance ($\text{NMSE} = 0.363$) while consuming only **420 Bytes** of memory for the 3 active tap buffers.

However, an **unresolved physical dilemma** emerges the moment oracle knowledge is removed:

> [!CAUTION]
> **The Fundamental Information-Storage Axiom:**
> A causal streaming model cannot evaluate, correlate, or adapt a candidate delayed feature $x_{i, t-k}$ at step $t$ unless the information required to reconstruct $x_{i, t-k}$ was physically stored in memory at time $t-k$ and preserved continuously through step $t$.
> 
> Therefore, in an online system with no oracle:
> $$\mathbf{PERSISTENT\_MEMORY = ACTIVE\_TAP\_MEMORY + HISTORY\_STORAGE\_FOR\_DISCOVERY}$$
> An algorithm can possess strictly sparse active weights ($K \ll L_{\max}$) while still requiring a dense history buffer of size $D \times L_{\max}$ scalars.

This document formally derives the theoretical minimum memory bounds, audits history representation alternatives, and calculates the exact capacity boundaries under LEBRE's $\le 1024$ byte micro-edge budget.

---

## 2. Mathematical Derivation of Naive History Preservation

Consider an online system receiving an input vector $\mathbf{x}_t \in \mathbb{R}^D$ at each discrete time step $t$, searching for delayed dependencies over a maximum temporal horizon $L_{\max}$.

### 2.1 Raw History Buffer Sizing
To allow any candidate pair $(i, k)$ with $i \in \{1, \dots, D\}$ and $k \in \{1, \dots, L_{\max}\}$ to be probed at time $t$, a naive implementation must maintain a circular ring buffer:
$$\mathbf{H}_t \in \mathbb{R}^{D \times L_{\max}}$$
The raw storage required is:
$$\text{MEM}_{\text{raw}} = D \cdot L_{\max} \cdot S_{\text{dtype}} \quad \text{bytes}$$
where $S_{\text{dtype}}$ is the scalar storage size:
- Standard Double Precision (float64): $S_{\text{dtype}} = 8$ bytes
- Single Precision (float32): $S_{\text{dtype}} = 4$ bytes
- Half Precision (float16 / bfloat16): $S_{\text{dtype}} = 2$ bytes

### 2.2 Numerical Evaluation Against R2-MEM ($\le 1024$ Bytes)

| Input Dimension ($D$) | Horizon ($L_{\max}$) | float64 (8 B) | float32 (4 B) | float16 (2 B) | R2-MEM Status ($\le 1024$ B) |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **$D = 20$** (A2–A4 benchmark) | $L_{\max} = 32$ | **5,120 B** | **2,560 B** | **1,280 B** | **VIOLATES R2-MEM** (All precisions) |
| **$D = 20$** | $L_{\max} = 16$ | **2,560 B** | **1,280 B** | 640 B | **VIOLATES R2-MEM** (float64/32) |
| **$D = 20$** | $L_{\max} = 8$ | 1,280 B | 640 B | 320 B | PASSES in float32 / float16 |
| **$D = 2$** (A5/A7 control) | $L_{\max} = 32$ | 512 B | 256 B | 128 B | **PASSES** (Fully compliant) |
| **$D = 1$** (SISO control) | $L_{\max} = 64$ | 512 B | 256 B | 128 B | **PASSES** (Fully compliant) |

### 2.3 Key Conclusion on Naive Dense History
> [!IMPORTANT]
> If a benchmark has $D = 20$ input channels and the search horizon extends to $L_{\max} = 32$, preserving a naive dense history buffer costs **2,560 Bytes in float32** and **5,120 Bytes in float64**.  
> This immediately exceeds the entire 1,024-byte persistent state budget **before a single model weight, candidate statistic, or normalizer state is allocated**.
> 
> Therefore, unconstrained multivariate dense delay discovery at $L_{\max} \ge 32$ is physically incompatible with R2-MEM unless:
> 1. History is stored only for active/provisional dimensions;
> 2. Downsampled / hierarchical history structures are used; or
> 3. $L_{\max}$ is bounded according to input dimensionality $D$ ($L_{\max} \le \lfloor 800 / (D \cdot 4) \rfloor$).

---

## 3. Granular Component Memory Breakdown

To eliminate any ambiguity in algorithmic state accounting, we decompose the total persistent memory of a dynamic lag lifecycle learner into 6 strictly bounded structural blocks:

### Block 1: Base Linear Model State ($\text{MEM}_{\text{base}}$)
- Weight vector: $D$ floats ($\mathbf{w} \in \mathbb{R}^D$)
- Running normalization statistics: mean ($\mu \in \mathbb{R}^D$), variance ($\sigma^2 \in \mathbb{R}^D$)
- Step counter and learning rate metadata: 16 bytes
$$\text{MEM}_{\text{base}} = (3D \times 8) + 16 = 24D + 16 \quad \text{bytes}$$
For $D=20$: $\text{MEM}_{\text{base}} = 496$ bytes.

### Block 2: Recurrent Unit State ($\text{MEM}_{\text{rec}}$)
- Scalar recurrent weight $w_{\text{rec}}$, feedback parameter $\lambda$, output weight $w_{\text{out}}$: $3 \times 8 = 24$ bytes
- RTRL sensitivity trace $p_t$: 8 bytes
- Internal state $s_t$: 8 bytes
$$\text{MEM}_{\text{rec}} = 40 \quad \text{bytes}$$

### Block 3: Active Lag Taps ($\text{MEM}_{\text{active}}$)
For a hard sparsity cap of $K_{\max}$ active taps:
- Tap coefficients: $K_{\max}$ floats ($w_k$) $\to K_{\max} \times 8$ bytes
- Dimension index $i \in \{1 \dots D\}$ and lag index $k \in \{1 \dots L_{\max}\}$: $K_{\max} \times 4$ bytes
- Fast gradient statistics / momentum: $K_{\max} \times 8$ bytes
- Dedicated circular tap buffer per active tap ($k$ floats): $\sum_{j=1}^{K} k_j \times S_{\text{dtype}}$ bytes
$$\text{MEM}_{\text{active}} = K_{\max} \times 20 + \sum_{j=1}^{K} (k_j \times S_{\text{dtype}}) \quad \text{bytes}$$
For $K_{\max} = 3$ taps at lags 4, 8, 30 with float32:
$$\text{MEM}_{\text{active}} = 60 + (4 + 8 + 30) \times 4 = 60 + 168 = 228 \quad \text{bytes}$$

### Block 4: Provisional Candidates & Shadow Evidence ($\text{MEM}_{\text{cand}}$)
For $M$ simultaneous provisional candidates under probation:
- Shadow weight $w_{\text{cand}}$: $M \times 8$ bytes
- Paired prequential loss accumulator: $M \times 8$ bytes
- Counterfactual evidence score: $M \times 8$ bytes
- Candidate age / timer: $M \times 4$ bytes
- Candidate coordinate identifier $(i, k)$: $M \times 4$ bytes
$$\text{MEM}_{\text{cand}} = M \times (8 + 8 + 8 + 4 + 4) = M \times 32 \quad \text{bytes}$$
For $M = 2$ provisional slots: $\text{MEM}_{\text{cand}} = 64$ bytes.

### Block 5: Two-Timescale Relevance & Eviction State ($\text{MEM}_{\text{life}}$)
- Slow relevance score $R_j$ for each active tap: $K_{\max} \times 8$ bytes
- Quiescence timer / observation counter: $K_{\max} \times 4$ bytes
- Global replacement regret accumulator: 8 bytes
$$\text{MEM}_{\text{life}} = K_{\max} \times 12 + 8 \quad \text{bytes}$$
For $K_{\max} = 3$: $\text{MEM}_{\text{life}} = 44$ bytes.

### Block 6: Candidate Discovery History Buffer ($\text{MEM}_{\text{hist}}$)
This is the central variable governed by the history representation architecture (HIST0 vs HIST1 vs HIST2).

---

## 4. History Representation Architectures Evaluated

```
+-----------------------------------------------------------------------------+
| HIST0: Full Dense Ring Buffer                                              |
| Stores all D channels for all L_max steps.                                  |
| Exact tap recovery: YES | Memory: D * L_max * 4 bytes                      |
+-----------------------------------------------------------------------------+
                                      |
+-------------------------------------+---------------------------------------+
|                                     |                                       |
v                                     v                                       v
+-----------------------------+ +-----------------------------+ +-----------------------------+
| HIST1: Dimension-Selective  | | HIST2: Active + Probe Window| | HIST3: Compressed Sketch   |
| Stores only top-d channels  | | Stores active taps + short  | | Count-min sketch / random   |
| based on instantaneous loss | | rotating probe window (M).  | | projections of past delays. |
| Exact: YES (for selected d) | | Exact: ACTIVE ONLY          | | Exact: NO (Screening only)  |
| Memory: d * L_max * 4 bytes | | Memory: K*k_max + M*L_probe | | Memory: O(w * d) bytes      |
+-----------------------------+ +-----------------------------+ +-----------------------------+
```

### 4.1 HIST0: Full Raw Ring Buffer
- **Structure:** Array of shape $(D, L_{\max})$ in float32.
- **Capabilities:** Allows any candidate $(i, k)$ to be probed instantly. Once promoted, the active tap inherits the exact past value $x_{i, t-k}$ with zero latency.
- **Cost for $D=20, L_{\max}=32$:** $20 \times 32 \times 4 = 2,560$ bytes (exceeds R2-MEM).
- **Cost for $D=5, L_{\max}=32$:** $5 \times 32 \times 4 = 640$ bytes (fits R2-MEM).

### 4.2 HIST1: Dimension-Selective Ring Buffer
- **Structure:** Keeps full depth $L_{\max}$ only for active input channels ($D_{\text{active}} \le 4$) determined by instantaneous regression magnitude.
- **Capabilities:** Exact tap recovery for active channels; inactive channels cannot be delayed beyond a shallow screening depth $L_{\text{screen}} = 4$.
- **Cost for $D_{\text{active}}=4, L_{\max}=32$:** $4 \times 32 \times 4 + 16 \times 4 \times 4 = 512 + 256 = 768$ bytes (compliant).

### 4.3 HIST2: Decoupled Active Delay Lines + Rotating Probe Buffer
- **Structure:** 
  1. Active taps maintain only their specific delay line ($k_j$ floats per active tap $j$).
  2. A small rotating probe buffer of depth $L_{\max}$ is maintained for only $P=1$ or $P=2$ probing dimensions at any given time, rotating round-robin across input dimensions.
- **Capabilities:** 
  - Exact recovery for promoted taps.
  - Probe candidates are tested sequentially as the probe window rotates through dimensions $i \in \{1 \dots D\}$.
- **Trade-off:** Slower discovery latency in exchange for strict memory compliance ($2 \times 32 \times 4 = 256$ bytes).

---

## 5. Total Algorithmic Budget Table

Under float32 history and float64 parameters for $D=5$ (or $D=20$ with HIST2 rotating probe), $L_{\max}=32$, $K_{\max}=3$, $M=2$:

| Component | Storage Type | Variables | Bytes |
| :--- | :--- | :--- | :---: |
| Base Linear Model | float64 | $\mathbf{w}$, $\mathbf{\mu}$, $\mathbf{\sigma}^2$ ($3 \times 5 \times 8 + 16$) | 136 B |
| Recurrent Unit | float64 | $w_{\text{rec}}, \lambda, w_{\text{out}}, p_t, s_t$ | 40 B |
| Active Lag Taps | float64 + float32 | 3 weights + 3 delay buffers (lags 4, 8, 30) | 228 B |
| Provisional Shadow State | float64 + int32 | 2 candidates ($M=2 \times 32$) | 64 B |
| Two-Timescale Relevance | float64 + int32 | Relevance $R_j$, timers, regret | 44 B |
| Candidate Probe Buffer (HIST2) | float32 | $2 \text{ channels} \times 32 \text{ lags} \times 4$ | 256 B |
| **TOTAL PERSISTENT ALGORITHMIC MEMORY** | — | — | **768 Bytes** |
| **R2-MEM Micro-Edge Envelope Limit** | — | — | **$\le 1024$ Bytes** |
| **Margin Below R2-MEM Ceiling** | — | — | **+256 Bytes (25.0% Headroom)** |

---

## 6. Formal Statement on Interpreter vs Algorithmic Memory

Consistent with previous LEBRE resource audit reports (`LEBRE_DIAG_01_RESOURCE_REPORT.md` and `CAPACITY_DECOMPOSITION_01_RESOURCE_REPORT.md`):
- All reported memory figures refer strictly to **algorithmic persistent state**: coefficients, circular ring buffers, normalization accumulators, and candidate metadata.
- Python interpreter overhead (PyObject headers, hash-table dict allocations, garbage collector tracking metadata) is excluded from the algorithmic ledger, as it reflects the host runtime rather than the mathematical architecture.
- For embedded C / micro-controller implementation, the exact flat C struct corresponding to the table above requires **768 bytes of contiguous static RAM**.
