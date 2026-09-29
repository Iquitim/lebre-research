# LEBRE-V0.2-INTEGRATION-DESIGN-01: Unified Resource Model
## 4-Channel Disaggregated Cost Ledger, Live vs. Shadow Accounting & Hybrid Capacity Budgets

**Document ID:** `LEBRE-V0.2-RES-2026-v1.0`  
**Status:** `FROZEN_RESOURCE_MODEL`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Hardware Analyst:** Skeptical Senior ML Systems Researcher, Computer-Architecture Performance Analyst  

---

## 1. Unified 4-Channel Vector Resource Formulation

In accordance with the post-reconciliation audit (`RESOURCE-ACCOUNTING-RECONCILIATION-01`), resource consumption is modeled strictly as a 4-channel physical cost vector:

$$\mathbf{R} = \begin{bmatrix} \text{FP\_FLOPS} \\ \text{INTEGER\_OPS} \\ \text{MEMORY\_TRAFFIC\_BYTES} \\ \text{PERSISTENT\_BYTES} \end{bmatrix}$$

Arbitrary scalarization is prohibited. Candidate architectures are compared via Pareto partial dominance:
$$\mathbf{R}_A \prec \mathbf{R}_B \iff (\forall k, R_{A, k} \le R_{B, k}) \land (\exists k, R_{A, k} < R_{B, k})$$

---

## 2. Component-by-Component Analytical Cost Breakdown

The table below details the exact primitive operation costs for each architectural sub-system under `FP16_EXACT_ADDRESSABLE_RING` ($D=5, L_{\max}=32$):

| Sub-system Component | FP FLOPs (IEEE-754) | Integer ALU / Shift / Cast | Memory Traffic (Bytes / step) | Persistent State (Bytes) | Category |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Feature Normalization (Causal)** | 10.0 (5 mul, 5 sub) | 0.0 | 40 B (read/write mean, var) | 40 B | Baseline |
| **Linear Base Forward** | 10.0 (5 mul, 5 add) | 0.0 | 40 B (load $x$, load $w$) | 40 B | Baseline |
| **Linear Base Update (NLMS)** | 15.0 (5 mul, 5 add, 5 scale) | 0.0 | 20 B (store updated $w$) | — | Baseline |
| **FP16 History Write** | 0.0 | 7.0 (5 casts, 1 mod, 1 add) | 10 B (store 5 FP16 words) | 330 B (Buffer) + 2 B (ptr) | History Buffer |
| **FP16 History Query (per tap)**| 0.0 | 4.0 (2 sub, 1 mod, 1 cast) | 2 B (load 1 FP16 word) | — | Query Primitive |
| **Active Discrete Tap Forward** | 2.0 per tap | Query overhead (4 ops) | 2 B load | 12 B per tap | Live Temporal |
| **Active Discrete Tap Update** | 4.0 per tap | Query overhead (4 ops) | 6 B (2 B read, 4 B store) | — | Live Temporal |
| **Active Tap Relevance & Evict**| 3.0 per tap | 1.0 (comparison/branch) | — | — | Live Lifecycle |
| **Active Recurrent Unit Forward**| 8.0 (tanh, mul, add) | 0.0 | 8 B (load state, load weights) | 48 B | Live Temporal |
| **Active Recurrent Forward Trace**| 10.0 (sensitivity updates) | 0.0 | 16 B (trace updates) | — | Live Temporal |
| **Active Recurrent Parameter Upd**| 8.0 (gradient, norm step) | 0.0 | 12 B (store updated $a, b, c$) | — | Live Temporal |
| **Shadow Candidate Probing (M=2)**| 4.0 (2 candidate correlations)| 8.0 (2 queries $\times$ 4 ops) | 4 B (load probed samples) | 80 B (Grid) | Shadow Rent |
| **Shadow Candidate Scoring (C cands)**| 4.0 per cand | 4.0 query ops per cand | 2 B load per cand | 16 B per cand | Shadow Rent |
| **Shadow Recurrent Training** | 18.0 (trace + update) | 0.0 | 20 B | 48 B (Shadow State)| Shadow Rent |
| **Capacity Arbitrator Logic** | 8.0 (loss diffs, EMAs) | 5.0 (comparisons/hysteresis) | 0.0 (register cached) | 32 B | Governor |

---

## 3. Disaggregation of Live vs. Shadow Rent

A core metric mandated by this stage is **Shadow Rent**: the computational and memory budget expended evaluating non-promoted candidates.

$$\mathbf{R}_{\text{total}} = \mathbf{R}_{\text{live}} + \mathbf{R}_{\text{shadow}}$$

### 3.1 Steady-State Live Regimes (Converged Execution)
- **Memoryless Regime (Linear Base Only):**
  $$\mathbf{R}_{\text{live, Base}} = [35.0 \text{ FP FLOPs}, 7.0 \text{ INT ops}, 110.0 \text{ B Traffic}, 412 \text{ B RAM}]$$
- **Pure Discrete Delay Regime (Base + $K=2$ Taps):**
  $$\mathbf{R}_{\text{live, Base+Lag}} = [53.0 \text{ FP FLOPs}, 25.0 \text{ INT ops}, 130.0 \text{ B Traffic}, 436 \text{ B RAM}]$$
- **Pure Continuous State Regime (Base + $N=1$ Recurrent):**
  $$\mathbf{R}_{\text{live, Base+Rec}} = [61.0 \text{ FP FLOPs}, 7.0 \text{ INT ops}, 146.0 \text{ B Traffic}, 460 \text{ B RAM}]$$
- **Hybrid Regime (Base + $K=2$ Taps + $N=1$ Recurrent):**
  $$\mathbf{R}_{\text{live, Hybrid}} = [79.0 \text{ FP FLOPs}, 25.0 \text{ INT ops}, 166.0 \text{ B Traffic}, 484 \text{ B RAM}]$$

### 3.2 Shadow Exploration Overhead (Active Search)
When structural search is fully engaged:
- Shadow Discrete Probing & Scoring ($M=2, C=3$): $+16.0$ FP FLOPs, $+20.0$ INT ops, $+10.0$ B Traffic, $+128$ B RAM.
- Shadow Recurrent Unit Training ($N=1$ candidate): $+18.0$ FP FLOPs, $0.0$ INT ops, $+20.0$ B Traffic, $+48$ B RAM.
- Capacity Arbitrator: $+8.0$ FP FLOPs, $+5.0$ INT ops.
- **Maximum Peak Shadow Search Burden:**
  $$\mathbf{R}_{\text{shadow, peak}} = [42.0 \text{ FP FLOPs}, 25.0 \text{ INT ops}, 30.0 \text{ B Traffic}, 176 \text{ B RAM}]$$

---

## 4. Hybrid Resource Stress & Feasibility Ceilings

Under maximum structural expansion (Hybrid Task I9, where BOTH Discrete Lags $K=4$ and Recurrence $N=1$ are active alongside active search):

$$\text{Peak Live Compute} = 35.0 \text{ (base)} + 36.0 \text{ (4 taps)} + 26.0 \text{ (rec)} = \mathbf{97.0 \text{ FP FLOPs/step}}$$
$$\text{Peak Persistent RAM} = 412 \text{ B (base+buf)} + 48 \text{ B (4 taps)} + 48 \text{ B (rec)} + 32 \text{ B (arbitrator)} = \mathbf{540 \text{ Bytes}}$$

### Compliance Verdict

1. **Legacy R2-FLOP Ceiling (100 FP FLOPs):**  
   Steady-state live hybrid compute is **97.0 FP FLOPs/step**, which is strictly **COMPLIANT** with the 100-FLOP ceiling.  
   However, during active parallel shadow search ($97.0 + 42.0 = 139.0$ FLOPs), total execution transiently exceeds 100 FLOPs. The report will explicitly disaggregate live from shadow compute to document this transient search overhead.
2. **R2-MEM Ceiling (1024 Bytes):**  
   Total persistent RAM footprint is **540 Bytes** (live) and **716 Bytes** (including full shadow candidate buffers), strictly **COMPLIANT** with the 1024-byte ceiling.
