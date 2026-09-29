# RESOURCE-ACCOUNTING-RECONCILIATION-01: Code-Path Forensics & Architectural Differential Analysis
## Line-by-Line Execution and Accounting Comparison: B7 vs. H0 vs. H3

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Status:** `FROZEN_PRE_EXPERIMENTAL`  
**Governing Context:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. Executive Summary

This document performs a forensic audit comparing the exact Python source code and execution paths of:
- **Variant A (`B7`):** `DynamicLagLifecycleModel` from `scratch/run_dynamic_lag_lifecycle_01.py` (reported at **82.0 FLOPs/step**).
- **Variant B (`H0`):** `HistoryBoundedAdaptiveFilter` with `ExactFP32RingProvider` from `scratch/run_bounded_history_experiments.py` and `scratch/bounded_history_providers.py` (reported at **125.1 FLOPs/step**).
- **Variant C (`H3`):** `HistoryBoundedAdaptiveFilter` with `QuantizedInt8RingProvider` (reported at **176.0 FLOPs/step**).

---

## 2. Answers to the 10 Mandated Architectural Questions

### 1. Are B7 and H0 actually executing the same algorithm?
**YES, with minor numerical refinements.**  
Both B7 and H0 implement the identical core two-timescale structural lag discovery lifecycle:
- Causal linear base filter with normalized LMS.
- Scalar recurrent state $s_t = \tanh(\lambda s_{t-1} + u_t)$.
- Sparse non-contiguous active lag taps.
- Rotating grid candidate probing ($M=2$ pairs/step).
- Counterfactual shadow probation with marginal gain accumulation.
- Two-timescale obsolescence eviction with quiescence protection ($|x| > 0.1$).

The minor algorithmic differences are:
- H0 adds a denominator stabilization term $(x_{\text{delayed}}^2 + 1.0)$ and weight clipping $[-5.0, 5.0]$ to the tap and shadow updates to prevent burst instability.
- H0 increases provisional candidate capacity from 3 to 8.

### 2. Does H0 include operations absent in B7?
**YES.**
1. **Per-Tap Denominator Normalization:** In H0, `tap['w'] += (mu_lag / (val**2 + 1.0)) * e_live * val` adds $1 \text{ multiply} + 1 \text{ add} + 1 \text{ divide} = 3$ operations per active tap and per provisional candidate.
2. **Weight Saturation / Clipping:** H0 calls `np.clip(...)` on active and shadow weights, adding 2 comparisons per active tap and per candidate.
3. **Double Provider Querying:** In H0, `self.provider.query(tap['i'], tap['k'])` is executed once in the forward pass and a second time in the weight adaptation loop, incurring duplicate query accounting.

### 3. Did provider abstraction introduce additional work?
**YES, overwhelmingly in the FLOP counter.**
- In B7: Delayed feature access was an inline helper `get_delayed(i, k)` returning `history[i, (ptr - k) % (L + 1)]` with **0 FLOPs added**.
- In H0: Every call to `self.provider.query(...)` returns `lookup_flops = 2` ("modulo + array index"), which the caller directly adds to `flops`.
- Because queries occur across forward pass ($K$), shadow scoring ($C$), weight adaptation ($K$), and candidate probing ($M$), H0 adds:
  $$\Delta_{\text{query}} = 2 \times (K + C + K + M) = 2 \times (2K + C + M) \text{ "FLOPs"}$$
  For typical values $K=2, C=2, M=2$, this single abstraction artifact adds **16 "FLOPs"/step** that were previously counted as 0.

### 4. Does one report include normalization while another excludes it?
- Both models include **base linear model normalization:**
  $$\text{denom}_{\text{base}} = \mathbf{x}_t^T \mathbf{x}_t + 10^{-4} \implies 2D + 1 \text{ FLOPs}$$
  and $\mathbf{w}_{\text{base}} \leftarrow \mathbf{w}_{\text{base}} + (\mu / \text{denom}) e_t \mathbf{x}_t$ ($D + 1$ FLOPs), totaling $3D$ in B7 and $3D$ in H0.
- However, H0 additionally includes local normalization $(x_{\text{delayed}}^2 + 1.0)$ on active taps and provisional candidates, which B7 omitted.

### 5. Does one include candidate probing while another excludes it?
**NO, both include candidate probing ($M=2$ pairs/step).**
- In B7: Candidate probing added $4 \text{ FLOPs}$ per probe ($0.95 \times \text{corr} + 0.05 \times (e \times x)$) $\implies 4M = 8 \text{ FLOPs}$.
- In H0: Candidate probing added $4 + q_{\text{flops}} = 4 + 2 = 6 \text{ FLOPs}$ per probe $\implies 6M = 12 \text{ FLOPs}$.

### 6. Does one include history writes?
**YES, both include history writes.**
- In B7: `history[:, hist_ptr] = x_t` added `self.D = 5` to `flops`.
- In H0: `provider.write(x_t)` returned `self.D = 5`, which was added to `flops`.
- Both models mislabeled the memory store of $D$ floats as $D$ arithmetic FLOPs.

### 7. Does one include lifecycle updates?
**YES, both include identical lifecycle updates:**
- Evidence accumulation: $0.95 E + 0.05 \times \text{gain}$ (4 FLOPs).
- Relevance update: $0.999 R + 0.001 \times \text{gain}$ (4 FLOPs).
- Counterfactual error calculation: $(e_{\text{live}}^2) - (e_{\text{cand}}^2)$ (3 FLOPs).

### 8. Does one include control/indexing arithmetic?
**YES — this is the central accounting discrepancy:**
- In B7: Buffer indexing (`hist_ptr`, `idx = (ptr - k) % (L + 1)`) was treated as zero-cost hardware address calculation / control logic.
- In H0: Buffer indexing was priced as $2 \text{ FLOPs}$ per access.
- In H3: Modulo, byte shifting, dynamic scale comparison, rounding, clipping, and casting were all lumped into the FLOP counter ($7D = 35$ FLOPs on write, $4$ FLOPs per query).

### 9. Does one use different $D, L_{\max}, M$ or $K_{\max}$?
| Parameter | B7 (`DYNAMIC-LAG-01`) | H0 / H3 (`BOUNDED-HISTORY-01`) | Match? |
| :--- | :---: | :---: | :---: |
| Input Dimension $D$ | 5 | 5 | **Identical** |
| Horizon $L_{\max}$ | 32 | 32 | **Identical** |
| Probing Rate $M$ | 2 | 2 | **Identical** |
| Max Active Taps $K_{\max}$ | 4 | 4 | **Identical** |
| Max Provisional Candidates $C_{\max}$ | 3 | 8 | **Different** |

The higher candidate capacity in H0 allows up to 8 shadow candidates during exploratory phases, whereas B7 capped them at 3.

### 10. Are the benchmark tasks causing different dynamic operation counts?
**YES.**
- In B7: Evaluated across tasks D1–D10. The average number of simultaneously active taps was $\bar{K} = 2.10$, and provisional candidates was $\bar{C} = 0.85$.
- In H0: Evaluated across tasks BH1–BH12. In BH8 (complex multi-lag stress), up to 4 taps are active concurrently, and the looser promotion threshold ($\theta_{\text{corr}} = 0.08$ vs $0.22$) generated an average of $\bar{C} \approx 1.82$ provisional candidates.
- Because each candidate and tap incurs per-step compute, the workload distribution contributes to the higher observed mean in H0.

---

## 3. Detailed Component Code-Path Comparison Table

| Execution Phase | B7 Code Path | H0 FP32 Code Path | H3 INT8 Code Path | Accounting Difference |
| :--- | :--- | :--- | :--- | :--- |
| **History Write** | `history[:, ptr] = x_t`<br>Adds $D = 5$ | `write(x_t)`<br>Adds $D = 5$ | `write(x_t)`<br>Scale update + quantize<br>Adds $7D = 35$ | H3 counts integer scaling, clipping, rounding, and casts as FLOPs |
| **Base Linear Forward** | `np.dot(w_base, x_t)`<br>Adds $2D = 10$ | `np.dot(w_base, x_t)`<br>Adds $2D = 10$ | `np.dot(w_base, x_t)`<br>Adds $2D = 10$ | Identical |
| **Active Tap Forward** | `y_lag += tap['w'] * val`<br>Adds $2K$ | `query(...)` + `w * val`<br>Adds $(2 + 2)K = 4K$ | `query(...)` + `w * val`<br>Adds $(4 + 2)K = 6K$ | H0 adds 2 query FLOPs; H3 adds 4 dequantization FLOPs |
| **Recurrent Forward** | Linear drive + tanh + mul<br>Adds 8 | Linear drive + tanh + mul<br>Adds 8 | Linear drive + tanh + mul<br>Adds 8 | Identical |
| **Candidate Scoring** | `query` (0) + scoring (8)<br>Adds $8C$ | `query` (2) + scoring + norm (8)<br>Adds $(8 + 2)C = 10C$ | `query` (4) + scoring + norm (8)<br>Adds $(8 + 4)C = 12C$ | H0 adds query; H3 adds dequantization |
| **Base Weight Update** | Dot product + scale + update<br>Adds $3D = 15$ | Dot product + scale + update<br>Adds $3D = 15$ | Dot product + scale + update<br>Adds $3D = 15$ | Identical |
| **Tap Weight Update** | Gradient + relevance<br>Adds $8K$ | Query (2) + norm + grad + rel<br>Adds $(8 + 2)K = 10K$ | Query (4) + norm + grad + rel<br>Adds $(8 + 4)K = 12K$ | H0 queries again (duplicate!); H3 dequantizes again |
| **Candidate Probing** | Probe update ($0.95 \text{corr} + \dots$)<br>Adds $4M = 8$ | Query (2) + probe update (4)<br>Adds $(4 + 2)M = 12$ | Query (4) + probe update (4)<br>Adds $(4 + 4)M = 16$ | H0 adds 2/probe; H3 adds 4/probe |
