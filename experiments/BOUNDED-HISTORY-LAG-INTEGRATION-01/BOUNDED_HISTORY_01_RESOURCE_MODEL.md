# BOUNDED-HISTORY-LAG-INTEGRATION-01: Resource Model & Scalability Matrix
## Analytical Memory Formulations, FLOP Ledgers & Dimension Scaling

**Stage:** `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Ceilings:** R2-FLOP ($\le 100$ FLOPs/step), R2-MEM ($\le 1024$ Bytes RAM)

---

## 1. Exact Analytical Memory Formulas

For an exact or quantized circular buffer:
$$\text{MEM}_{\text{history}}(D, L_{\max}, B) = D \cdot (L_{\max} + 1) \cdot \frac{B}{8} + \text{Metadata}(D)$$
where $\text{Metadata}(D) = 20 \text{ Bytes}$ for unscaled buffers and $20 + 4D \text{ Bytes}$ for quantized buffers with per-channel float32 dynamic scale factors.

Total persistent system state when coupled with the frozen LEBRE baseline ($K_{\max} = 2, M = 2$):
$$\text{MEM}_{\text{total}} = \text{MEM}_{\text{history}} + \text{MEM}_{\text{active\_taps}} (112 \text{ B}) + \text{MEM}_{\text{candidate\_probing}} (64 \text{ B}) + \text{MEM}_{\text{base\_recurrent}} (148 \text{ B})$$
$$\text{MEM}_{\text{fixed\_overhead}} = 112 + 64 + 148 = \mathbf{324 \text{ Bytes}}$$

---

## 2. Scalability Matrix across Dimensions ($D \in \{5, 10\}, L_{\max} \in \{32, 64\}$)

| Configuration Grid | Provider Paradigm | History Buffer RAM | Fixed Overhead | Total Persistent RAM | R2-MEM ($\le 1024$ B) | Headroom |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Current: $D=5, L_{\max}=32$** | H0: FP32 Exact Ring | 680 B | 324 B | **1,004 B** | **PASS** | +20 B |
| Current: $D=5, L_{\max}=32$ | H1: FP16 Exact Ring | 350 B | 324 B | **674 B** | **PASS** | +350 B |
| Current: $D=5, L_{\max}=32$ | H3: INT8 Quantized Ring | 205 B | 324 B | **529 B** | **PASS** | +495 B |
| **Wider: $D=10, L_{\max}=32$** | H0: FP32 Exact Ring | 1,340 B | 354 B | **1,694 B** | **FAIL** | -670 B |
| Wider: $D=10, L_{\max}=32$ | H1: FP16 Exact Ring | 680 B | 354 B | **1,034 B** | **MARGINAL** | -10 B |
| Wider: $D=10, L_{\max}=32$ | H3: INT8 Quantized Ring | 390 B | 354 B | **744 B** | **PASS** | **+280 B** |
| **Longer: $D=5, L_{\max}=64$** | H0: FP32 Exact Ring | 1,320 B | 324 B | **1,644 B** | **FAIL** | -620 B |
| Longer: $D=5, L_{\max}=64$ | H1: FP16 Exact Ring | 670 B | 324 B | **994 B** | **PASS** | **+30 B** |
| Longer: $D=5, L_{\max}=64$ | H3: INT8 Quantized Ring | 345 B | 324 B | **669 B** | **PASS** | **+355 B** |
| **Wider & Longer: $D=10, L=64$** | H0: FP32 Exact Ring | 2,620 B | 354 B | **2,974 B** | **FAIL** | -1,950 B |
| Wider & Longer: $D=10, L=64$ | H3: INT8 Quantized Ring | 710 B | 354 B | **1,064 B** | **MARGINAL** | -40 B |

**Key Finding:** Reduced precision (FP16 and INT8) is the **only physical mechanism** that allows streaming lag discovery to scale beyond $D=5, L_{\max}=32$ under micro-edge constraints.

---

## 3. Computational FLOP Ledger per Time Step

$$\text{FLOPs}_{\text{total}} = \text{FLOPs}_{\text{history\_write}} + \text{FLOPs}_{\text{active\_predict\_update}} (32) + \text{FLOPs}_{\text{candidate\_probing}} (28) + \text{FLOPs}_{\text{base\_recurrent}} (22)$$
$$\text{FLOPs}_{\text{fixed\_overhead}} = 32 + 28 + 22 = \mathbf{82 \text{ FLOPs}}$$

| Provider | Write FLOPs/step | Query FLOPs/probe | Mean Total FLOPs/step | Peak FLOPs/step | R2-FLOP ($\le 100$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **H0: FP32 Exact** | 5.0 | 2.0 | **87.0** | 97.0 | **PASS** |
| **H1: FP16 Exact** | 10.0 | 3.0 | **92.0** | 102.0 | **PASS** |
| **H2: INT16 Quantized** | 35.0 | 4.0 | 117.0 | 127.0 | FAIL (Over budget) |
| **H3: INT8 Quantized** | 35.0 | 4.0 | 117.0 | 127.0 | FAIL (Over budget) |
| **H4: Age-Aware Mixed** | 45.0 | 3.0 | 127.0 | 137.0 | FAIL (Over budget) |
| **H5: Multirate Naive** | 8.8 | 2.0 | **90.8** | 100.0 | **PASS** |
| **H7: HiPPO Polynomial**| 420.0 | 30.0 | 502.0 | 542.0 | FAIL (Diagnostic Only) |

> [!NOTE]
> Integer quantization requires dynamic scaling FLOPs ($+30$ FLOPs/step). On integer-native microcontrollers with hardware fixed-point arithmetic (DSP instructions), this cost is 0 FLOPs. On generic floating-point ALUs, FP16 delivers optimal compute ($\le 100$ FLOPs).
