# RESOURCE-ACCOUNTING-RECONCILIATION-01: Legacy R2-FLOP Definition Audit
## Forensic Analysis of Historical Resource Thresholds and Architectural Invariants

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Status:** `FROZEN_PRE_EXPERIMENTAL`  
**Governing Context:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. Executive Summary

This audit establishes the precise historical definition of the **`R2_FLOP <= 100 FLOPs/step`** resource ceiling that has governed the LEBRE project since Milestone M1/M2 and `BENCH-01B`. 

We classify the historical definition against the five formal categories specified in the audit mandate:

```text
========================================================================================
FORMAL CLASSIFICATION:
R2_FLOP_DEFINITION = C. MAC_BASED (with Mixed Transcendental & Inconsistent Memory Pricing)
========================================================================================
```

---

## 2. Historical Genesis & Evolution of R2-FLOP

### A. The Benchmark Protocol Specification (`BENCH-01A` & `bench_01_locked_config.json`)
The origin of the $100$-FLOP rule traces back to `experiments/BENCH-01A/bench_01_locked_config.json` and `BENCH_01B_RESOURCE_ANALYSIS.md` (Section 156 of Protocol BENCH-01B):
- **Addition / Subtraction:** 1 FLOP
- **Multiplication:** 1 FLOP
- **Multiply-Accumulate (MAC):** 2 FLOPs
- **Division / Reciprocal:** 4 FLOPs
- **Square Root:** 4 FLOPs
- **Elementary Transcendental ($\exp, \tanh, \sigma$):** 8 FLOPs
- **R2-FLOP Ceiling:** $\le 100.0\text{ FLOPs/step mean}$ across streaming trajectories.

### B. The Specification Clarification (ADR-006 & Correction A)
As documented in `LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md` (Section 8.2 and ADR-006):
> *"The R2-FLOP requirement ($\le 100$ FLOPs/step) is strictly a **mean benchmark budget** evaluated over complete streaming trajectories. It is not an absolute ceiling on every isolated clock cycle. In Task B5, LEBRE achieves an average throughput of 90.44 FLOPs/step mean. During transient probation intervals where a shadow candidate is evaluated concurrently with live inference, total computational load reaches a temporary peak of $\approx 206$ FLOPs/step for 50 steps."*

### C. Inconsistencies in Implementation Practice
While `BENCH-01B` defined a rigorous weighting model (4 FLOPs for division, 8 FLOPs for tanh), later experimental scripts deviated in two opposite directions:
1. **Under-Counting in `DYNAMIC-LAG-LIFECYCLE-01` (B7):**
   - Division was assigned 1 FLOP or subsumed into $3D$.
   - Ring buffer history writes (`self.history[:, ptr] = x_t`) were counted as $D$ "FLOPs", mislabeling memory stores as arithmetic.
   - Delayed value retrieval (`get_delayed`) was assigned $0$ FLOPs, completely omitting indexing and memory loads.
   - Result: B7 reported **82.0 FLOPs/step**.
2. **Over-Aggregation in `BOUNDED-HISTORY-LAG-INTEGRATION-01` (H0 & H3):**
   - In H0, `provider.query(...)` was assigned $2$ "FLOPs" ("modulo + array index"). Because query was called multiple times per step (forward pass, candidate scoring, tap update, probing), this added $2 \times (K + C + K + M)$ "FLOPs" per step.
   - In H3, `provider.write(...)` added $7D$ "FLOPs" and `provider.query(...)` added $4$ "FLOPs", labeling dynamic scale comparisons, clipping, rounding, and byte indexing directly as "FLOPs".
   - Result: H0 reported **125.1 FLOPs/step** and H3 reported **176.0 FLOPs/step**.

---

## 3. Classification Verdict & Technical Impact

The historical definition is classified as **`MAC_BASED` with mixed-inconsistent implementation**:
- **Why not `STRICT_FP_ONLY`?** Because both B7 and H0/H3 counted integer ring buffer indices, stores, and modulo operations inside the FLOP accumulator.
- **Why not `ALL_ARITHMETIC_MISLABELED_AS_FLOPS`?** Because transcendental weights ($\tanh = 8$) and division weights ($4$) were applied, and memory stores were counted as arithmetic operations.
- **Why not `UNRECOVERABLE`?** The exact lines of code in `run_dynamic_lag_lifecycle_01.py` and `bounded_history_providers.py` are preserved bitwise. Every single added increment is 100% auditable.

---

## 4. Preservation Policy for Legacy Metric & Future Proposal

1. **Preservation of `LEGACY_R2_FLOP`:**
   To maintain continuity with `BENCH-01B`, `CAR-01`, and `LEBRE_SPEC_v0.1`, the historical scalar metric is retained under the explicit designation:
   $$\text{LEGACY\_R2\_FLOP} \le 100.0\text{ FLOPs/step (Historical Proxy)}$$
2. **Adoption of the Heterogeneous Compute Vector:**
   For all future micro-edge evaluations and M3 consideration, the multidimensional vector is proposed:
   $$\mathbf{c}_t = \left\{ \text{FP\_FLOPS}, \text{INT\_OPS}, \text{BYTES\_READ}, \text{BYTES\_WRITTEN}, \text{PEAK\_STATE\_BYTES} \right\}$$
   This prevents reduced-precision schemes (INT8, FP16) from being penalized by mislabeled FLOP counters.
