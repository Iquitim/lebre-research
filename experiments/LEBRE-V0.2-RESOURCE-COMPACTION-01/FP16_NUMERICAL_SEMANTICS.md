# IEEE 754 Float16 Numerical Semantics & Architecture

**Document Identifier:** `FP16_NUMERICAL_SEMANTICS.md`  
**Study Identifier:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Auditor / Researcher:** Independent Skeptical Senior Researcher  
**Date:** September 2026  

---

## 1. Mathematical Representation of IEEE 754 Half-Precision

IEEE 754-2008 defines the 16-bit binary floating-point format (`binary16`, commonly known as `half` or `float16`) with the following bit allocation:

| Field | Bit Width | Bit Positions | Description |
|:---|:---:|:---:|:---|
| **Sign ($s$)** | $1$ | $[15]$ | $0 \implies$ positive, $1 \implies$ negative |
| **Exponent ($e$)** | $5$ | $[14:10]$ | Biased exponent, bias $B = 15$ |
| **Fraction / Mantissa ($m$)** | $10$ | $[9:0]$ | Explicit significand bits |

### 1.1 Interpretation by Exponent Field
For an encoded bit-pattern $(s, e, m)$:
1. **Normalized Numbers ($1 \le e \le 30$):**
   $$x = (-1)^s \times 2^{e - 15} \times \left( 1 + \sum_{j=1}^{10} m_{10-j} 2^{-j} \right)$$
   Implicit leading bit is $1$. The effective precision is $p = 11$ bits ($1$ implicit + $10$ explicit).
2. **Subnormal / Denormalized Numbers ($e = 0, m \ne 0$):**
   $$x = (-1)^s \times 2^{-14} \times \left( \sum_{j=1}^{10} m_{10-j} 2^{-j} \right)$$
   Implicit leading bit is $0$. Provides gradual underflow down to $2^{-24}$.
3. **Signed Zero ($e = 0, m = 0$):**
   $$x = (-1)^s \times 0.0 \quad (+0.0 \text{ or } -0.0)$$
4. **Infinities ($e = 31, m = 0$):**
   $$x = (-1)^s \times \infty \quad (+\infty \text{ or } -\infty)$$
5. **Not a Number (NaN) ($e = 31, m \ne 0$):**
   Signaling NaN ($m_9 = 0, m \ne 0$) or Quiet NaN ($m_9 = 1$).

---

## 2. Fundamental Numerical Boundaries & Constants

| Property | Exact Formula | Decimal Value | Significance for LEBRE Correlation State |
|:---|:---:|:---:|:---|
| **Machine Epsilon ($\epsilon_{\text{mach}}$)** | $2^{-10}$ | $9.765625 \times 10^{-4}$ | Relative resolution between consecutive representable numbers |
| **Half-Epsilon (Rounding Bound)** | $2^{-11}$ | $4.8828125 \times 10^{-4}$ | Maximum relative roundoff error under round-to-nearest |
| **Smallest Positive Normalized** | $2^{-14}$ | $6.103515625 \times 10^{-5}$ | Normal precision boundary; below this, subnormal loss occurs |
| **Smallest Positive Subnormal** | $2^{-24}$ | $5.9604644775390625 \times 10^{-8}$ | Absolute numerical floor; values smaller round to $0.0$ |
| **Maximum Representable Finite** | $(2 - 2^{-10}) \times 2^{15}$ | $65,504.0$ | Saturation/overflow ceiling; values $> 65,504$ round to $\infty$ |
| **Dynamic Range** | $\approx 2^{40}$ | $\approx 1.1 \times 10^{12}$ | Ratio of maximum finite to minimum positive subnormal |
| **Decimal Precision** | $\log_{10}(2^{11})$ | $\approx 3.31$ decimal digits | Number of trustworthy decimal digits |

---

## 3. Dissecting the LEBRE Correlation Operating Range

In the LEBRE architecture, the correlation grid cells $C_{i,k}$ track empirical normalized or pseudo-normalized correlation:
$$C_{i,k} \in [-1.0, +1.0]$$

In this $[-1.0, +1.0]$ operating envelope:
1. **Representable Spacing ($\text{ULP}$):**
   - At $|C| \in [0.5, 1.0)$: $e = 14 \implies \text{ULP} = 2^{-11} \approx 4.88 \times 10^{-4}$.
   - At $|C| \in [0.25, 0.5)$: $e = 13 \implies \text{ULP} = 2^{-12} \approx 2.44 \times 10^{-4}$.
   - At $|C| \in [0.125, 0.25)$: $e = 12 \implies \text{ULP} = 2^{-13} \approx 1.22 \times 10^{-4}$.
   - At $|C| \in [0.0625, 0.125)$: $e = 11 \implies \text{ULP} = 2^{-14} \approx 6.10 \times 10^{-5}$.
2. **Threshold Sensitivity at $\theta = 0.20$:**
   - The decision threshold for provisional candidate birth is $\theta = 0.20$.
   - The binary16 encoding of $0.20$ is:
     $$0.20 \approx 2^{-3} \times (1 + 0.6) = 0.125 \times 1.6 \implies e = 12, m = 614 \implies 0.199951171875$$
   - The next representable number is $0.2001953125$ ($\text{ULP} = 2.44 \times 10^{-4}$).
   - The boundary interval is $[0.199951, 0.200195]$. Quantization jitter near this boundary is strictly bounded by $\pm 1.22 \times 10^{-4}$.
3. **Stagnation Condition:**
   - The EMA update formula is:
     $$\Delta C = \lambda \cdot (e_{\text{probe}} \cdot x_{i,t-k} - C_{i,k})$$
     with $\lambda = 0.05$.
   - Update stagnation occurs if $|\Delta C| < \frac{1}{2} \text{ULP}$.
   - At $|C| \approx 0.20$, $\frac{1}{2} \text{ULP} \approx 1.22 \times 10^{-4}$.
   - Thus, an innovation step will stagnate only if $|e \cdot x - C| < \frac{1.22 \times 10^{-4}}{0.05} \approx 0.00244$.
   - This represents a deadband of $\pm 0.00244$ around the true target correlation.

---

## 4. Separation of Storage Precision vs. Arithmetic Precision

A fundamental tenet of this resource compaction study is the strict separation of **Persistent Storage Precision** from **Transient Arithmetic Precision**:

```
+-------------------------------------------------------------------------+
| PERSISTENT LEDGER (DRAM / SRAM)                                         |
|   corr_grid: np.float16[5, 33] = 165 elements * 2 Bytes = 330 Bytes     |
+-------------------------------------------------------------------------+
                                 │
                 (1) Read & Cast │ (np.float32)
                                 ▼
+-------------------------------------------------------------------------+
| TRANSIENT WORKSPACE (CPU / MCU Registers)                               |
|   val_fp32 = np.float32(corr_grid[i, k])                                |
|   innov_fp32 = np.float32(e_probe * x_delayed)                          |
|   upd_fp32 = np.float32(0.95) * val_fp32 + np.float32(0.05) * innov     |
|   is_promoted = abs(upd_fp32) > np.float32(0.20)                        |
+-------------------------------------------------------------------------+
                                 │
             (2) Round & Cast-to │ (np.float16, Round-to-Nearest-Even)
                                 ▼
+-------------------------------------------------------------------------+
| PERSISTENT LEDGER (DRAM / SRAM)                                         |
|   corr_grid[i, k] = np.float16(upd_fp32)                                |
+-------------------------------------------------------------------------+
```

### 4.1 Invariants of the Hybrid Protocol
1. **Zero Persistent FP32 Master Grid:** At no point during execution is a 660-byte FP32 matrix maintained alongside the FP16 matrix. Any such implementation would constitute an accounting breach.
2. **Transient Register Overhead:** The temporary scalar variables (`val_fp32`, `innov_fp32`, `upd_fp32`) occupy at most 12 bytes of transient register/stack workspace. On ARM Cortex-M4/M7 (FPU registers `s0..s3`), this uses zero SRAM data allocation.
3. **Rounding Mode:** Round-to-nearest, ties-to-even (IEEE 754 default, matching NumPy `np.float16`).
4. **Cast Operations Counted:** Every read requires $1$ `F16_TO_F32` cast; every write requires $1$ `F32_TO_F16` cast. These are formally tracked in the resource ledger under `CAST_OPS`.
