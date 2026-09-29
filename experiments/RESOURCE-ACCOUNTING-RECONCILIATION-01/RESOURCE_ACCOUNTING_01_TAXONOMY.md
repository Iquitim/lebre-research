# RESOURCE-ACCOUNTING-RECONCILIATION-01: Operation Taxonomy & Accounting Specification

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Status:** `FROZEN_PRE_EXPERIMENTAL`  
**Governing Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. The Four-Channel Resource Model

To eliminate ambiguous aggregation, all computational work is partitioned into four strictly non-interchangeable resource views:

```text
========================================================================================
CHANNEL 1: FLOATING_POINT_OPS (IEEE 754 Arithmetic Only)
CHANNEL 2: INTEGER_OPS        (Integer Arithmetic, Bitwise, Shifts, Conversions)
CHANNEL 3: MEMORY_TRAFFIC     (Bytes Loaded, Bytes Stored, Memory Footprint)
CHANNEL 4: PLATFORM_COST      (Host Execution Latency, Cycle Counts, Energy Proxy)
========================================================================================
```

> [!IMPORTANT]
> **No Universal Conversion Factor:** Under no circumstances shall integer operations, rounding, or memory access bytes be converted into "FLOP equivalents" (e.g. no "1 INT8 = 0.25 FLOP"). Each channel retains its native dimension.

---

## 2. Granular Operation Taxonomy

Every discrete algorithmic operation executed by LEBRE's base model, recurrent unit, history provider, and dynamic-lag lifecycle is categorized into one of the following exact primitives:

### A. Floating-Point Arithmetic (`FLOATING_POINT_OPS`)
| Opcode | Description | Standardized Cost (FLOPs) | Legacy Undercount Note |
| :--- | :--- | :---: | :--- |
| `FP_ADD` | IEEE-754 32-bit addition | 1 | Standard 1 FLOP |
| `FP_SUB` | IEEE-754 32-bit subtraction | 1 | Standard 1 FLOP |
| `FP_MUL` | IEEE-754 32-bit multiplication | 1 | Standard 1 FLOP |
| `FP_DIV` | IEEE-754 32-bit floating division | 1 | Standard 1 FLOP (often 4–14 cycles on MCU) |
| `FP_SQRT` | IEEE-754 square root | 1 | Standard 1 FLOP |
| `FP_FMA` | Fused Multiply-Accumulate ($a \times b + c$) | 2 | Counted as 1 FLOP in legacy MAC convention |
| `FP_COMPARE` | Floating-point magnitude comparison | 1 | Relational evaluation ($x > y$) |

### B. Integer Arithmetic & Logic (`INTEGER_OPS`)
| Opcode | Description | Classification | Hardware Realization |
| :--- | :--- | :---: | :--- |
| `INT_ADD` | Integer 8/16/32-bit addition | `INTEGER_OP` | Single-cycle integer ALU |
| `INT_SUB` | Integer 8/16/32-bit subtraction | `INTEGER_OP` | Single-cycle integer ALU |
| `INT_MUL` | Integer 8/16/32-bit multiplication | `INTEGER_OP` | Single-cycle integer multiplier / DSP |
| `INT_DIV` | Integer division | `INTEGER_OP` | Multi-cycle hardware divider |
| `INT_SHIFT` | Logical / arithmetic bit shift (`<<`, `>>`) | `INTEGER_OP` | Single-cycle barrel shifter |
| `INT_COMPARE`| Integer equality/inequality comparison | `INTEGER_OP` | Integer comparator / condition flags |
| `BITWISE_OP` | Bitwise AND, OR, XOR, NOT | `INTEGER_OP` | Single-cycle bitwise ALU |

### C. Precision Conversion & Control Operations (`CONVERSION_AND_CONTROL`)
| Opcode | Description | Classification | Notes |
| :--- | :--- | :---: | :--- |
| `ROUND` | Round-to-nearest-integer float $\to$ int | `INTEGER_OP` | FPU conversion instruction |
| `CLIP` | Saturating range clamp $[q_{\min}, q_{\max}]$ | `INTEGER_OP` | 2 comparisons + conditional select |
| `CAST_FP_TO_INT` | Bitcast / conversion float $\to$ integer | `INTEGER_OP` | FPU-to-Core register move |
| `CAST_INT_TO_FP` | Bitcast / conversion integer $\to$ float | `INTEGER_OP` | Core-to-FPU register move |
| `ABS` | Absolute value $|x|$ | `INTEGER_OP` / `FP_OP` | Sign bit masking |
| `MIN_MAX` | Scalar min or max evaluation | `INTEGER_OP` / `FP_OP` | Comparison + conditional assignment |
| `MODULO` | Circular buffer index wrapping ($k \pmod L$) | `INTEGER_OP` | Bitwise AND (if $2^p$) or int rem |
| `BRANCH` | Conditional control-flow branch | `CONTROL_OP` | Pipeline branch / predicate |
| `ARRAY_INDEX` | Base + offset address calculation | `CONTROL_OP` | Address Generation Unit (AGU) |

### D. Memory Traffic (`MEMORY_TRAFFIC`)
| Opcode | Description | Unit | Scope |
| :--- | :--- | :---: | :--- |
| `LOAD_BYTES` | Bytes read from SRAM/RAM | Bytes | Explicit input, buffer, or state read |
| `STORE_BYTES`| Bytes written to SRAM/RAM | Bytes | Explicit input, buffer, or state write |
| `TOTAL_BYTES_MOVED` | Sum of `LOAD_BYTES` + `STORE_BYTES` | Bytes | Total memory bus traffic per step |
| `PERSISTENT_BYTES` | Static RAM footprint of parameters/state | Bytes | Retained across time steps |
| `TRANSIENT_BYTES` | Working scratchpad / stack buffer | Bytes | Allocated and reclaimed within step |

---

## 3. Standardized Multiply-Accumulate (MAC) Convention

Earlier benchmarks within the project exhibited divergent MAC counting conventions:
- **Legacy Convention (M1/M2/DYNAMIC-LAG-01):** Counted $1 \text{ MAC} = 1 \text{ FLOP}$ in dot products and LMS updates.
- **Standardized Convention (IEEE / Modern Benchmark Standard):**
  $$\text{FLOP}_{\text{STANDARDIZED}} = 1 \text{ Multiply} + 1 \text{ Addition} = 2 \text{ FLOPs per MAC}$$

Both metrics shall be computed and reported:
$$\text{MAC\_COUNT} = \sum \text{Multiply-Accumulates}$$
$$\text{FLOP\_COUNT\_STANDARDIZED} = \text{Pure Add/Sub} + \text{Pure Mul/Div} + 2 \times \text{MAC\_COUNT}$$

---

## 4. Multi-Dimensional Compute Vector Definition

To replace the oversimplified scalar FLOP metric, this stage formally defines the **Heterogeneous Micro-Edge Compute Vector**:

$$\mathbf{c}_t = \begin{bmatrix} \text{FP\_FLOPS}_t \\ \text{INT\_OPS}_t \\ \text{BYTES\_READ}_t \\ \text{BYTES\_WRITTEN}_t \\ \text{PEAK\_STATE\_BYTES} \end{bmatrix}$$

This vector provides a hardware-independent specification. On any specific processor (e.g. ARM Cortex-M4 @ 64 MHz), cycles and energy are derived by applying the platform's specific execution matrix:

$$\text{Cycles} \approx \alpha_{\text{FP}} \cdot \text{FP\_FLOPS} + \alpha_{\text{INT}} \cdot \text{INT\_OPS} + \alpha_{\text{MEM}} \cdot \text{BYTES\_MOVED}$$

---

## 5. Memory Subsystem Partitioning

Per-step memory traffic is explicitly partitioned across six functional components:
1. **History Buffer Traffic:** Writing $x_t \in \mathbb{R}^D$ to history; querying delayed inputs $x_{i, t-k}$.
2. **Linear Model Traffic:** Reading $w_{\text{base}}$, writing updated weights.
3. **Active Tap Traffic:** Reading tap weights $w_j$, updating $w_j$, reading/writing relevance $R_j$.
4. **Candidate State Traffic:** Reading/updating shadow weights $w_{\text{shadow}}$, evidence $E_m$, age.
5. **Normalization Traffic:** Reading input vector for causal scaling statistics.
6. **Quantizer State Traffic:** Reading/updating dynamic scale $S_i$, reading/writing quantized words.

---

## 6. Operational Intensity Diagnostic

For each representation, operational intensity is formally defined as:
$$\text{FP\_OPS\_PER\_BYTE} = \frac{\text{FP\_FLOPS}}{\text{TOTAL\_BYTES\_MOVED}}$$
$$\text{ARITHMETIC\_OPS\_PER\_BYTE} = \frac{\text{FP\_FLOPS} + \text{INT\_OPS}}{\text{TOTAL\_BYTES\_MOVED}}$$

These diagnostic metrics illustrate whether a quantization scheme increases arithmetic density or remains memory-bound.
