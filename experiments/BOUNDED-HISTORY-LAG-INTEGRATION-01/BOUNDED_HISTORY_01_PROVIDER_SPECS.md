# BOUNDED-HISTORY-LAG-INTEGRATION-01: Provider Specifications
## Mathematical & Bit-Level Architecture of Candidate Temporal History Providers

**Stage:** `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Purpose:** Formalize data layouts, quantization schemes, decimation matrices, and lookup semantics for all history providers.

---

## 1. Provider Comparison Overview

| Provider ID | Implementation Concept | Word Length | Storage per Sample | Total History Bytes ($D=5, L=32$) | Metadata Bytes | Total Persistent RAM | Lookup Type |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **H0: EXACT_FP32_RING** | Exact Circular Buffer | 32-bit float | 4.0 Bytes | 660 Bytes | 20 Bytes | **680 Bytes** | `EXACT_POINT_LOOKUP` |
| **H1: FP16_EXACT_RING** | Half-Precision IEEE 754 | 16-bit float | 2.0 Bytes | 330 Bytes | 20 Bytes | **350 Bytes** | `APPROXIMATE_POINT_LOOKUP` |
| **H2: INT16_QUANTIZED** | Fixed-Point Quantization | 16-bit int | 2.0 Bytes | 330 Bytes | 40 Bytes | **370 Bytes** | `APPROXIMATE_POINT_LOOKUP` |
| **H3: INT8_QUANTIZED** | Uniform Linear Quantization | 8-bit int | 1.0 Byte | 165 Bytes | 40 Bytes | **205 Bytes** | `APPROXIMATE_POINT_LOOKUP` |
| **H4: AGE_AWARE_MIXED** | Split-Horizon Hierarchy | FP16 / INT8 | 2.0 B (k≤8), 1.0 B (k>8) | 215 Bytes | 44 Bytes | **259 Bytes** | `APPROXIMATE_POINT_LOOKUP` |
| **H5: MULTIRATE_DECIM** | Geometric Decimation | 32-bit float | 4.0 B (subsampled) | 380 Bytes | 28 Bytes | **408 Bytes** | `EXACT / APPROX` (Conditional) |
| **H7: HIPPO_POLYNOMIAL**| Shifted Legendre Projection | 32-bit float | Order $N_p = 6$ | 120 Bytes | 208 Bytes | **328 Bytes** | `APPROXIMATE_POINT_LOOKUP` |

---

## 2. Mathematical Detail by Family

### 2.1 Uniform Quantization Scheme (H2 & H3)
- Running scale factor per channel $i$:
  $$S_i(t) = \max\left(1.0, 0.99 \cdot S_i(t-1) + 0.01 \cdot 1.2 \cdot |x_{i, t}|\right)$$
- Quantization operator ($B$ bits, signed integer):
  $$q_{i, t} = \text{clip}\left(\left\lfloor \frac{x_{i, t}}{S_i(t)} \cdot (2^{B-1} - 1) + 0.5 \right\rfloor, -(2^{B-1}-1), 2^{B-1}-1\right)$$
- Dequantization operator for candidate evaluation:
  $$\hat{x}_{i, t-k} = q_{i, \text{idx}} \cdot \frac{S_i(t)}{2^{B-1} - 1}$$

### 2.2 Multirate Decimation Ladder (H5)
- Tier 1 ($k \in [1, 8]$): Every sample stored. Capacity = 9 samples.
- Tier 2 ($k \in [9, 16]$): $2\times$ decimation. Stored every 2nd step. Capacity = 5 samples.
- Tier 3 ($k \in [17, 32]$): $4\times$ decimation. Stored every 4th step. Capacity = 5 samples.
- Odd/decimated queries return interpolated or nearest-neighbor values, explicitly flagged as `APPROXIMATE_POINT_LOOKUP`.

### 2.3 Continuous Shifted Legendre Polynomial Projection (H7)
- Projects history onto Legendre polynomial basis $P_n(u)$ on $u \in [0, 1]$ where $u = \frac{\tau}{L_{\max}}$.
- State vector $m_i(t) \in \mathbb{R}^{N_p}$ updated via discrete state transition:
  $$m_i(t+1) = (I + \Delta t A) m_i(t) + \Delta t B x_{i, t}$$
- Query at lag $k$:
  $$\hat{x}_{i, t-k} = \sum_{n=0}^{N_p - 1} m_{i, n}(t) \cdot \sqrt{2n + 1} \cdot P_n\left(\frac{2k}{L_{\max}} - 1\right)$$
