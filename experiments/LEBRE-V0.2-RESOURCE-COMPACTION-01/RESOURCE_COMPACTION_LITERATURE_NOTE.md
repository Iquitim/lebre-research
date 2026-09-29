# Literature Review: Precision Compaction in Streaming Adaptive Systems

**Study Identifier:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Focus:** Finite-Precision Correlation Grid Storage, Numerical Stability, and Adaptive State Quantization  
**Auditor / Researcher:** Independent Skeptical Senior Researcher  
**Date:** September 2026  

---

## 1. Executive Summary

This note synthesizes foundational literature across mixed-precision computing, finite-precision adaptive filtering, and statistical equivalence testing to establish the methodological justification and risk boundaries for compacting the persistent correlation-state grid of LEBRE candidate $T_3$ from `float32` (FP32) to IEEE 754 half-precision `float16` (FP16).

The key insight from the literature is double-edged:
1. **Memory Feasibility:** Decoupling storage precision (FP16) from arithmetic/accumulation precision (FP32) can halve persistent state footprint without degrading dynamic range, provided updates and threshold comparisons occur in higher precision (Micikevicius et al., 2018).
2. **Dynamic Risk in Recursive Adaptive State:** Quantizing internal recursive state in an adaptive filter is fundamentally distinct from quantizing weights in a trained static neural network or offline SGD. Finite precision in online recursion introduces coefficient roundoff, update stagnation (when incremental innovations fall below the least significant bit), threshold-crossing jitter, limit cycles, and long-term error drift (Cioffi, 1987; Yousef & Sayed, 2000, 2003).

Therefore, half-precision storage cannot be assumed harmless based on nominal bit-width alone. Equivalence must be rigorously established against pre-frozen equivalence bounds (Lakens, 2017).

---

## 2. Mixed-Precision Computation: Principles & Domain Boundaries

### 2.1 The Master-Copy / Low-Precision Storage Pattern
Micikevicius et al. (*Mixed Precision Training*, ICLR 2018, arXiv:1710.03740) demonstrated that deep neural networks can be trained with FP16 representations if three techniques are applied:
1. Maintaining a full-precision (FP32) master copy of weights for accumulation to prevent small gradient updates from vanishing;
2. Performing numerically sensitive operations (reductions, exponentiations, inner products) in FP32;
3. Scaling loss magnitudes dynamically to avoid underflow in the restricted dynamic range of FP16 ($10^{-5}$ to $6.5 \times 10^4$).

### 2.2 Domain Translation & Critical Limitations for Embedded Streaming
While Micikevicius et al. established the viability of FP16 arithmetic in deep learning, their context exhibits three critical differences from LEBRE:
- **No Master Copy Permitted:** In embedded TinyML ($< 1$ KiB RAM budget), storing a persistent FP32 master copy would defeat the memory compaction objective. In LEBRE, the **persistent state must reside entirely in FP16** ($165 \times 2 = 330$ B). Full-precision FP32 is permitted *only* as a transient scalar workspace (at most 4–8 bytes of register workspace) during the active update cycle, after which the updated value is cast back to FP16.
- **Recursive State Dynamics:** In deep learning, weight updates are driven by external batch gradients sampled across stationary data distributions. In LEBRE, the correlation grid is an online exponential moving average:
  $$C_{i,k}(t) = (1 - \lambda) C_{i,k}(t-1) + \lambda (e_t \cdot x_{i,t-k})$$
  Here, $C_{i,k}(t)$ is an internal recursive state that drives non-linear threshold crossings ($|C_{i,k}| > 0.20$) to trigger candidate birth and subsequent structural promotion. Small quantization errors can alter which candidate crosses the threshold first, inducing macro-level structural divergence.

---

## 3. Finite-Precision Adaptive Filtering: The Analytical Foundation

### 3.1 Roundoff and Update Stagnation (Cioffi, 1987)
In his seminal work (*Limited-Precision Effects in Adaptive Filtering*, IEEE Trans. Circuits and Systems, 1987, DOI: 10.1109/TCS.1987.1086209), John Cioffi analyzed the fundamental failure modes of finite-precision recursive adaptive algorithms:
1. **Update Stagnation (Digital Deadbands):** When the magnitude of the innovation update $\Delta C = \lambda (e_t \cdot x_{i,t-k})$ is smaller than half the spacing between representable floating-point numbers ($\frac{1}{2} \text{ULP}$ of $C_{i,k}$), rounding causes the update to be truncated to zero:
   $$C_{i,k} \oplus \Delta C = C_{i,k}$$
   In this regime, the adaptive filter stops learning entirely, even when prediction errors remain substantial.
2. **Coefficient Drift and Limit Cycles:** In under-excited directions (channels or lags with low variance), finite-precision errors accumulate along unconstrained sub-spaces, causing coefficients to drift until an overflow or spurious threshold crossing occurs.
3. **Threshold Jitter:** Fixed decision thresholds ($\theta = 0.20$) applied to quantized internal state can lead to chatter (rapid oscillation between active and inactive states) if the quantized state hovers near the boundary.

### 3.2 Steady-State Excess MSE in Quantized Filters (Yousef & Sayed, 2000, 2003)
Yousef & Sayed (*A Unified Approach to the Steady-State Analysis of Quantized Adaptive Filtering Algorithms*, 2000; *Fixed-point steady-state analysis of adaptive filters*, Int. J. Adapt. Control Signal Process. 2003, DOI: 10.1002/acs.738) unified the mathematical treatment of quantization in recursive filters. They proved that internal quantization introduces an additive excess mean-square error (EMSE):
$$\text{EMSE}_{\text{quant}} = \text{EMSE}_{\text{infinite}} + \mathcal{O}(2^{-2B}) \cdot \frac{1}{\mu}$$
where $B$ is the effective mantissa bit-width and $\mu$ is the learning rate.
Because the correlation grid uses an effective adaptation rate of $\lambda = 0.05$, the ratio $\frac{\sigma_{\text{quant}}^2}{\lambda}$ is non-zero. The 10-bit mantissa of IEEE 754 FP16 provides a machine epsilon of:
$$\epsilon_{\text{mach}} = 2^{-11} \approx 4.88 \times 10^{-4}$$
with representable precision of approximately 3 to 4 significant decimal digits. For correlation values in the range $[-1.0, 1.0]$, the spacing between consecutive representable numbers is at coarsest $2^{-10} \approx 9.77 \times 10^{-4}$ (near $|C| = 1.0$) and $2^{-14} \approx 6.10 \times 10^{-5}$ (near $|C| = 0.1$). Because typical innovation increments $\Delta C = 0.05 \cdot (e \cdot x)$ are on the order of $10^{-2}$ to $10^{-3}$, they comfortably exceed $1 \text{ ULP}$ for active signals, but may approach the stagnation boundary during quiescent or low-amplitude periods.

---

## 4. Statistical Equivalence Testing: The Lakens Framework

### 4.1 Fallacy of the Null Hypothesis Significance Test
Daniël Lakens (*Equivalence Tests: A Practical Primer for t-Tests, Correlations, and Meta-Analyses*, Social Psychological and Personality Science, 2017, DOI: 10.1177/1948550617697177) established the methodological necessity of equivalence testing in behavioral and computer science:
> *"A non-significant result ($p > 0.05$) in an ordinary difference test means only that the data are not sufficiently inconsistent with the null hypothesis of zero difference. It does NOT demonstrate that the two conditions are equivalent."*

In systems engineering, asserting that "FP16 does not degrade accuracy" based on an ordinary $t$-test failing to reach $p < 0.05$ is a severe statistical fallacy (Type II error masking degradation).

### 4.2 Two One-Sided Tests (TOST) and Equivalence Bounds
To validate behavior preservation, one must formulate equivalence hypotheses:
$$H_{0}^{-}: \mu_{C1} - \mu_{C0} \le -\Delta_{\text{equiv}} \quad \text{or} \quad \mu_{C1} - \mu_{C0} \ge +\Delta_{\text{equiv}}$$
$$H_{1}: -\Delta_{\text{equiv}} < \mu_{C1} - \mu_{C0} < +\Delta_{\text{equiv}}$$
Equivalence is declared at significance level $\alpha = 0.05$ if and only if the two-sided $(1 - 2\alpha) = 90\%$ confidence interval for the paired difference $\Delta = C_1 - C_0$ lies **entirely within** $[-\Delta_{\text{equiv}}, +\Delta_{\text{equiv}}]$.

### 4.3 Preregistration Requirement
As emphasized by Simmons, Nelson, & Simonsohn (2011) and Nosek et al. (2018), equivalence margins $\Delta_{\text{equiv}}$ must be derived objectively from parent study empirical distributions **prior to inspecting confirmatory C1 experimental data**. Setting $\Delta_{\text{equiv}}$ post-hoc to encompass an observed deviation destroys the inferential validity of the test.

---

## 5. Methodological Synthesis for LEBRE

The literature directly dictates the experimental architecture of `LEBRE-V0.2-RESOURCE-COMPACTION-01`:
1. **Isolated Intervention:** Only `corr_grid` is cast to FP16; all arithmetic occurs in FP32; no persistent FP32 shadow master copy is maintained.
2. **Numerical Microtrace & Stress Suite:** Must empirically test for stagnation, underflow, overflow, and threshold crossings at the exact boundary of IEEE 754 FP16 representation before full-scale benchmarking.
3. **Rigorous Equivalence Testing:** Predictive NMSE, structural F1, and arbitration stability must be evaluated via paired TOST against pre-frozen bounds derived from sealed parent study variance.
4. **Decoupling Gate 6 & Structural Limitations:** Quantization must not be exploited as an unprincipled vehicle to "tune" or "fix" known open governance issues.
