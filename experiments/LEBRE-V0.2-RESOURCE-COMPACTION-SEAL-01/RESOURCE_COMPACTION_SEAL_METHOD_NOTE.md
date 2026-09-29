# Methodological Note: Scientific Foundations of Resource-Compaction Seal Auditing

**LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01**

---

## 1. Introduction & Epistemic Framework

When evaluating edge machine learning models designed for extreme resource-constrained environments (e.g. sub-1KB SRAM microcontrollers), empirical claims of "memory reduction without accuracy loss" are prone to subtle methodological errors:
1. **Representational vs Accumulation Precision Confusion:** Storing weights in lower precision while accumulating in full precision alters numerical dynamics (Micikevicius et al., 2018).
2. **Pseudo-Replication in Inferential Testing:** Treating multiple tasks evaluated under the same seed as independent statistical draws inflates degrees of freedom and creates spurious significance (Hurlbert, 1984; Lakens, 2017).
3. **Capacity vs Allocation Accounting:** Conflating worst-case allocated structural capacity with mean operational occupancy obscures true hardware feasibility (Banbury et al., 2021).
4. **Selective Stagnation Reporting:** Failing to distinguish mathematical boundary conditions (Cioffi, 1987) from streaming empirical stability.

This note documents the scientific literature and rigorous standards applied during this seal audit.

---

## 2. Theoretical Literature & Foundational Citations

### 2.1 Mixed-Precision Representation & Accumulation Dynamics
- **Micikevicius, P., et al. (2018). "Mixed Precision Training." *ICLR 2018*.**
  Demonstrates that half-precision floating point (IEEE 754-2008 binary16, 1 sign, 5 exponent, 10 mantissa bits) provides sufficient dynamic range ($\approx 6.1 \times 10^{-5}$ to $6.55 \times 10^4$) for intermediate activation and state storage, provided that:
  - Updates are computed and accumulated in single precision (FP32).
  - The minimum representable increment (machine epsilon $\epsilon_{\text{FP16}} = 2^{-11} \approx 4.88 \times 10^{-4}$ for normalized numbers, $2^{-24} \approx 5.96 \times 10^{-8}$ for subnormals) does not exceed the steady-state innovation gradient.
- **Cioffi, J. M. (1987). "Limited-precision effects in adaptive filtering." *IEEE Transactions on Circuits and Systems*, 34(7), 821–833.**
  Proves that in recursive stochastic gradient and LMS filtering, parameter updating halts (stagnation) when:
  $$|\mu \cdot e(t) \cdot x(t-\tau)| < \frac{1}{2} \text{LSB}(w)$$
  In $T_3$, updates to the correlation grid occur via exponential moving averages:
  $$R_{ik}(t) = (1 - \beta) R_{ik}(t-1) + \beta \cdot [x_i(t) \cdot x_i(t-k)]$$
  When $|x_i(t) \cdot x_i(t-k) - R_{ik}(t-1)| \cdot \beta < 2^{-11}$, arithmetic rounding in pure FP16 truncates the update to zero. The hybrid strategy implemented in $C_1$ (`FP32_UPDATE_FP16_STORAGE`) computes the differential in FP32 before casting to FP16, mitigating gradient vanishing down to FP16 subnormal representation ($5.96 \times 10^{-8}$).
- **Yousef, N. R., & Sayed, A. H. (2000; 2003). "A unified approach to the error analysis of adaptive filters." *IEEE Transactions on Signal Processing*, 49(2), 314–324.**
  Establishes energy conservation relations showing that steady-state excess mean-square error (EMSE) under finite-precision arithmetic decomposes into tracking lag error plus gradient quantization noise:
  $$\text{EMSE}_{\text{quant}} = \text{EMSE}_{\text{exact}} + \frac{\sigma_{\text{quant}}^2}{2 \mu}$$
  For correlation grid values bounded in $[-1.0, 1.0]$, FP16 quantization noise variance is bounded by $\sigma_{\text{quant}}^2 = \frac{\Delta^2}{12} \le \frac{(2^{-11})^2}{12} \approx 1.98 \times 10^{-8}$, which is orders of magnitude smaller than structural discovery thresholds ($\Gamma_{\text{delay}} = 0.15$).

### 2.2 Equivalence Testing & Inferential Units
- **Lakens, D. (2017). "Equivalence testing for psychological research: A tutorial on NHST, $p$-values, and Two One-Sided Tests (TOST)." *Social Psychological and Personality Science*, 8(4), 355–362.**
  Establishes that absence of evidence is not evidence of equivalence. Equivalence between $C_0$ and $C_1$ requires formally rejecting the composite null hypotheses:
  $$H_{01}: \mu_{C1} - \mu_{C0} \le -\Delta_{\text{eq}} \quad \text{or} \quad H_{02}: \mu_{C1} - \mu_{C0} \ge +\Delta_{\text{eq}}$$
  with $\Delta_{\text{eq}} = 0.010$ (1% NMSE).
- **Hurlbert, S. H. (1984). "Pseudoreplication and the design of ecological field experiments." *Ecological Monographs*, 54(2), 187–211.**
  Prohibits treating non-independent observations as independent sampling units. In LEBRE benchmarking, the independent randomizing unit is the **SEED**. Running 14 tasks under the same seed creates 14 correlated responses; pooling them into $N=420$ observations constitutes technical pseudoreplication. Valid confirmatory inference must be conducted at the aggregate seed level ($N=30$).
- **Nosek, B. A., et al. (2018, 2019). "The preregistration revolution." *PNAS*, 115(11), 2600–2606.**
  Enforces clear separation between exploratory cohorts (Seeds 1401..1410) and confirmatory cohorts (Seeds 1411..1440). Confirmatory conclusions must not incorporate data from exploratory runs.

### 2.3 Embedded Resource Accounting Standards
- **Banbury, C., et al. (2021). "MLPerf Tiny Benchmark." *NeurIPS Datasets and Benchmarks Track*.**
  Specifies rules for embedded TinyML benchmarking:
  1. Memory accounting must report both static persistent state (SRAM retained across inference steps) and transient scratchpad memory (reused across operations).
  2. Memory buffers must be evaluated at maximum simultaneous allocation, not arbitrary downsampled averages, unless dynamic pool eviction is formally guaranteed by the runtime.
  3. FLOP counting must separate floating-point arithmetic from integer indexing and type-conversion overheads.

---

## 3. Methodological Audit Standards Applied

1. **Arithmetic Integrity:** Any table summarizing memory components must strictly satisfy $\sum \text{components} = \text{total}$. No manual overrides or unallocated slack terms are permitted.
2. **Deterministic Certification:** In cases where empirical paired delta is exactly zero across all seeds, parametric Student's $t$ division by zero standard error is replaced with a formal deterministic proof of exact sample equality.
3. **Cross-Cohort Boundary Enforcement:** Observations from un-preregistered cohorts (e.g. exploratory seed groups) cannot be used to post-hoc alter gate outcomes of preceding confirmatory studies.
