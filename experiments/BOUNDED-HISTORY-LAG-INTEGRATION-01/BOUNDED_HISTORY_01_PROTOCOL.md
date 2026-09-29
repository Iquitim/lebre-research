# Experimental Protocol: Bounded-History Representation, Compression & Lag-Discovery Integration

**Document ID:** `BOUNDED_HISTORY_01_PROTOCOL`  
**Status:** `FROZEN_PRE_REGISTRATION`  
**Governing Standard:** LEBRE Experimental Rigor Specification v0.1  
**Primary Inferential Unit:** `INDEPENDENT_SEED`  
**Milestone Status:** `M3_STATUS = UNOPENED`  
**Canonical Lineage:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. Executive Protocol Summary

This experimental protocol governs the empirical investigation of bounded-history representations and history compression mechanisms for streaming adaptive lag discovery. 

The investigation resolves three foundational questions:
- **Q1 (Precision):** Can history quantization (FP16, INT16, INT8, Age-Aware Mixed Precision) reduce memory footprint without degrading asymptotic tracking error ($\text{EMSE} < 10^{-3}$) or support discovery recovery rate ($F_1 \ge 0.95$)?
- **Q2 (Temporal Resolution):** Does temporal subsampling / multirate decimation preserve discrete lag discovery under High-Entropy IID regimes, or does Shannon-Nyquist aliasing inherently destroy sub-grid delay resolution?
- **Q3 (Continuous Representation):** Under what conditions (specifically compressible Regime B vs. non-compressible Regime A) can continuous polynomial/state-space representations (HiPPO) identify temporal dependencies?

---

## 2. Seed Partitioning & Reproducibility Policy

To guarantee statistical integrity, data splitting and seed isolation are strictly enforced:

1. **Development & Hyperparameter Screening Seeds ($N_{\text{dev}} = 10$):**
   - Seed range: `[951, 952, 953, 954, 955, 956, 957, 958, 959, 960]`
   - Purpose: Code stabilization, step-size tuning verification, memory verification.
   - Rule: Development results must never be pooled with confirmation results.

2. **Final Confirmation Seeds ($N_{\text{final}} = 30$):**
   - Seed range: `[1101, ..., 1130]` (30 contiguous virgin seeds).
   - Screening status: Verified 100% disjoint from all previous LEBRE stages (01, 01A, 0001–0010).
   - Rule: Executed exactly once under frozen hyperparameters. All hypotheses P1–P7 evaluated exclusively on this set.

3. **Paired Statistical Design:**
   - Every candidate provider ($H_1, \dots, H_7$) is evaluated on the exact same pseudo-random stream instances as the baseline provider ($H_0$, Exact FP32) on a per-seed basis.

---

## 3. Benchmark Task Definitions (BH1 – BH12)

The benchmark comprises 12 streaming tasks divided into two distinct information-theoretic regimes:
- **Regime A (High-Entropy IID):** Uncorrelated innovations where history possesses maximum Kolmogorov complexity.
- **Regime B (Compressible / Structured):** Spatio-temporally correlated or bandlimited inputs where Shannon rate-distortion allows sub-linear representation.

All streams are generated for $T = 20{,}000$ steps with noise variance $\sigma_v^2 = 0.01$ (SNR $\approx 20$ dB), input dimensionality $D \in \{5, 10\}$, and maximum lag window $L_{\max} \in \{32, 64\}$.

### Regime A: High-Entropy IID Streams
- **BH1 (Single Discrete Lag):** High-entropy white Gaussian input $x_t \sim \mathcal{N}(0, I_D)$. Single causal tap at lag $\tau^* = 12$ on channel $d=2$ with weight $w^* = 0.85$.
- **BH2 (Multi-Tap Dispersed):** Three active taps at $\tau \in \{4, 11, 25\}$ across distinct channels with weights $\{0.70, -0.60, 0.50\}$.
- **BH3 (Widely Separated Taps):** Two taps at extremes of the buffer: $\tau_1 = 2$ and $\tau_2 = 30$ ($L_{\max}=32$). Tests buffer boundary preservation.
- **BH4 (Relocating Dynamic Lag):** Active tap moves from $\tau_1 = 8$ to $\tau_2 = 22$ at step $t = 10{,}000$. Evaluates tracking agility under bounded history.
- **BH8 (Dynamic Range Stress):** Heavy-tailed Cauchy/Laplace innovations with dynamic scale variations spanning 4 orders of magnitude ($\pm 100\sigma$). Tests dynamic-range clipping and INT8 overflow.
- **BH9 (Memoryless Control):** System with zero temporal lag ($\tau = 0$ only). Tests false discovery rate of history providers.
- **BH10 (Quiescent Delay Stability):** Input enters complete silence ($x_t = 0$) for $t \in [8{,}000, 12{,}000]$ while true tap is at $\tau^* = 15$. Tests retention vs. eviction under zero-gradient quiescence.

### Regime B: Temporally Compressible Streams
- **BH5 (Smooth AR(1) Low-Pass):** Spatially independent AR(1) process with pole $\alpha = 0.92$: $x_t = \alpha x_{t-1} + \sqrt{1-\alpha^2}\epsilon_t$. Active tap at $\tau^* = 14$.
- **BH6 (Bandlimited Multi-Tap):** Input filtered through Butterworth 4th-order low-pass filter ($f_c = 0.15 f_s$). Active taps at $\tau \in \{5, 12, 19\}$.
- **BH7 (Correlated Long Delay):** Strongly correlated Gaussian process ($r(k) = \exp(-k^2/50)$) with long delay $\tau^* = 28$.
- **BH11 (Continuous-State Recurrence):** Output governed by continuous linear state-space system $\dot{h}(t) = A h(t) + B x(t)$ sampled at $\Delta t = 0.05$. Tests polynomial projection capacity.
- **BH12 (Hybrid Discrete + Continuous):** Linear combination of discrete sparse tap ($\tau^* = 7$) and continuous AR(2) resonant tail ($f_0 = 0.05 f_s, Q = 5$).

---

## 4. History Provider Candidate Suite

| Provider ID | Provider Name | Buffer Precision | Decimation / Basis | Nominal Memory (B) [$D=5, L=32$] | Read Complexity |
|:---|:---|:---:|:---:|:---:|:---:|
| **H0** | Exact FP32 Ring Buffer (Baseline) | IEEE FP32 (32-bit) | None ($R=1$) | 680 B | $O(1)$ direct |
| **H1** | FP16 Exact Ring Buffer | IEEE FP16 (16-bit) | None ($R=1$) | 350 B | $O(1)$ cast |
| **H2** | Symmetric INT16 Quantized Ring | INT16 (16-bit) | Per-channel dynamic scale | 370 B | $O(1)$ dequant |
| **H3** | Symmetric INT8 Quantized Ring | INT8 (8-bit) | Per-channel dynamic scale | 205 B | $O(1)$ dequant |
| **H4** | Age-Aware Mixed Precision | FP16 (lags $\le 8$), INT8 (lags $>8$) | Dual-precision ring | 259 B | $O(1)$ piecewise |
| **H5-Naive** | Multirate Ring Buffer (Naive) | FP32 | Subsampled $R=2$ for $\tau > 8$ | 408 B | Interpolated |
| **H5-AA** | Multirate Ring Buffer (Anti-Alias) | FP32 | 3-tap FIR filter + $R=2$ | 408 B | Filtered |
| **H7** | HiPPO Polynomial History (Diagnostic) | FP32 state vector | Legendre polynomials ($N=6$) | 328 B | Recurrence step |

---

## 5. Mathematical Metrics & Evaluation Criteria

1. **Prediction Error Metrics:**
   - Mean Squared Error: $\text{MSE} = \frac{1}{T - T_{\text{warm}}} \sum_{t=T_{\text{warm}}+1}^T (y_t - \hat{y}_t)^2$.
   - Excess MSE (EMSE): $\text{EMSE} = \max(0, \text{MSE} - \sigma_v^2)$.
   - Tracking Degradation Factor: $\rho_{\text{EMSE}} = \frac{\text{EMSE}_{\text{candidate}}}{\text{EMSE}_{H0}}$.

2. **Lag Discovery & Support Recovery Metrics:**
   - Active Tap Precision: $P = \frac{|\hat{\mathcal{S}} \cap \mathcal{S}^*|}{|\hat{\mathcal{S}}|}$ (defined as 1.0 if $\hat{\mathcal{S}} = \mathcal{S}^* = \emptyset$).
   - Active Tap Recall: $R = \frac{|\hat{\mathcal{S}} \cap \mathcal{S}^*|}{|\mathcal{S}^*|}$.
   - Support F1 Score: $F_1 = \frac{2 P R}{P + R}$.
   - Discovery Win Rate: Proportion of seeds where $\hat{\mathcal{S}}_{\text{final}} = \mathcal{S}^*$.

3. **History Reconstruction Fidelity:**
   - Root Mean Squared Reconstruction Error:
     $$\text{RMSE}_{\text{recon}} = \sqrt{\frac{1}{D \cdot L_{\max}} \sum_{d=1}^D \sum_{\ell=1}^{L_{\max}} (X_{d, \ell}^{\text{true}} - \hat{X}_{d, \ell})^2}$$

4. **Computational & Hardware Complexity:**
   - Total SRAM Footprint: $\mathcal{S}_{\text{RAM}} = \text{DataBytes} + \text{StateBytes} + \text{MetadataBytes}$.
   - Memory Reduction Ratio: $\rho_{\text{MEM}} = \frac{\mathcal{S}_{\text{RAM}}(H0)}{\mathcal{S}_{\text{RAM}}(H_k)}$.
   - Compute Overhead: Incremental FLOPs per incoming sample per channel.

---

## 6. Pre-Registered Hypotheses & Falsification Thresholds

| ID | Formal Hypothesis Statement | Confirmation Criteria | Falsification Condition |
|:---|:---|:---|:---|
| **P1** | **FP16 Lossless Discovery:** Half-precision storage preserves exact lag discovery and asymptotic EMSE under both regimes. | Paired Wilcoxon $p \ge 0.05$ on EMSE vs H0; $F_1 \ge 0.98$; Win rate $\ge 96.7\%$. | Any seed fails discovery or $\text{EMSE}_{\text{excess}} > 10^{-4}$. |
| **P2** | **INT8 Bounded Degradation:** 8-bit quantization with dynamic scale tracking incurs negligible EMSE increase ($\Delta \text{EMSE} < 10^{-3}$) while cutting RAM $>65\%$. | Mean $\Delta \text{EMSE} < 10^{-3}$; $F_1 \ge 0.95$; Memory $\le 210$ B ($D=5, L=32$). | $F_1 < 0.90$ or Divergence on BH8 stress stream. |
| **P3** | **Multirate Aliasing Breakdown (Regime A):** Under IID white noise, temporal decimation ($R \ge 2$) fails to discover odd/intermediate discrete lags due to Nyquist violation. | Odd-lag discovery rate $< 10\%$ for H5 on BH1/BH2; Falsification of discrete lag discovery. | H5 reliably discovers odd discrete lags without phase ambiguity ($F_1 > 0.90$). |
| **P4** | **Multirate Viability (Regime B):** Under bandlimited signals, multirate decimation preserves tracking without aliasing penalty. | $F_1 \ge 0.90$ on BH5/BH6/BH7; $\rho_{\text{EMSE}} < 1.15$. | $F_1 < 0.75$ on BH5/BH6. |
| **P5** | **Continuous-Representation Domain Failure (HiPPO on Regime A):** Fixed-order polynomial projection cannot resolve high-entropy localized discrete delays. | HiPPO $F_1 < 0.20$ on BH1/BH2/BH3; Reconstruction error $> 0.50 \sigma_x$. | HiPPO matches discrete ring discovery ($F_1 > 0.85$). |
| **P6** | **Continuous-Representation Efficiency (HiPPO on Regime B):** Polynomial compression tracks continuous/smooth dynamics (BH11/BH12) with sublinear memory scaling. | HiPPO EMSE $\le 1.10 \times \text{EMSE}_{H0}$ on BH11; memory savings $> 50\%$. | HiPPO fails to stabilize or diverges on continuous streams. |
| **P7** | **Pareto Superiority of Mixed Precision (H4):** Age-aware mixed precision achieves Pareto-optimal trade-off between memory footprint ($\rho_{\text{MEM}} \approx 2.6\times$) and transient tracking error. | Non-dominated in (Memory, EMSE, $F_1$) front across all 12 tasks. | Dominated by INT8 (H3) or FP16 (H1) on all axes. |

---

## 7. Statistical Test Procedures & Multiple Comparison Controls

1. **Paired Non-Parametric Inference:**
   - Two-sided and one-sided Wilcoxon signed-rank tests applied to paired differences $\Delta_i = M_i(H_k) - M_i(H_0)$ for each seed $i \in \{1, \dots, 30\}$.
2. **Family-Wise Error Rate Control:**
   - Primary hypotheses evaluated under Holm-Bonferroni step-down procedure at family-wise significance level $\alpha = 0.01$.
3. **Effect Size Reporting:**
   - All comparisons report matched-pairs rank biserial correlation $r_{\text{rb}}$ and paired Cohen's $d_z = \frac{\bar{\Delta}}{s_{\Delta}}$.

---

## 8. Protocol Freezing & Cryptographic Seal

Before launching confirmation runs, this document is hashed. Any discrepancy between the pre-registered protocol and the post-run audit invalidates Phase B conclusions.
