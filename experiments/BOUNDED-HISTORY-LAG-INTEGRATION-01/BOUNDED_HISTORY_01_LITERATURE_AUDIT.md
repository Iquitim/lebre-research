# BOUNDED-HISTORY-LAG-INTEGRATION-01: Literature Audit
## Bounded-History Representations, Multirate DSP, Streaming Synopses & Polynomial Projections

**Stage:** `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Purpose:** Audit seven distinct mathematical and algorithmic families for bounded temporal history representation in streaming systems.  
**Auditor Roles:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Signal Processing Researcher, Streaming Algorithms Auditor.

---

## 1. Deep Dive into the 7 Evaluated Literature Families

### L1. Sliding-Window Streaming Algorithms
- **Primary Citation:** Datar, M., Gionis, A., Indyk, P., & Motwani, R. (2002). *Maintaining stream statistics over sliding windows*. SIAM Journal on Computing, 31(6), 1794–1813.
- **Core Principles:** Maintains approximate aggregate statistics (counts, sum of bits, $L_p$ norms) over a sliding window of length $W$ using $O(\frac{1}{\epsilon} \log^2 W)$ space via exponential histograms.
- **Critical LEBRE Audit Question:** *Can exponential histograms recover arbitrary past real-valued samples $x_{i, t-k}$?*
- **Skeptical Analysis:** **NO.** Exponential histograms cluster past events into geometrically growing buckets where timestamp precision is deliberately lost to achieve logarithmic space. They support window sums and quantile queries, but **cannot** perform point retrieval of an arbitrary historical sample. Confusing sliding-window aggregation with sample history storage is a category error.

### L2. One-Pass Wavelet Synopses
- **Primary Citation:** Gilbert, A. C., Kotidis, Y., Muthukrishnan, S., & Strauss, M. (2001). *Surfing wavelets on streams: One-pass summaries for approximate aggregate queries*. VLDB, 79–88. Follow-up: Matias, Y., Vitter, J. S., & Wang, M. (1998). *Wavelet-based histograms for select estimation*. ACM SIGMOD.
- **Core Principles:** Maintains an online Haar wavelet decomposition of a streaming signal. Small wavelet coefficients are discarded, retaining the top-$B$ most significant coefficients.
- **Critical LEBRE Audit Question:** *Can a wavelet synopsis preserve enough local information to discover an unknown sharp discrete lag?*
- **Skeptical Analysis:** A top-$B$ wavelet synopsis compresses smooth or piecewise constant trends efficiently. However, if the stream is white noise ($x_t \sim \mathcal{N}(0, 1)$), wavelet coefficients are identically independent Gaussian variables with uniform variance across scales. Truncating small coefficients introduces significant reconstruction error ($\text{RMSE} \propto \sqrt{(W - B)/W}$). For isolated discrete delays, wavelet truncation severely attenuates the cross-correlation signal needed by LEBRE's candidate probing.

### L3. Legendre Memory Units (LMU)
- **Primary Citation:** Voelker, A. R., Kajić, I., & Eliasmith, C. (2019). *Legendre Memory Units: Continuous-time representation in recurrent neural networks*. NeurIPS 2019.
- **Core Principles:** Derives a linear time-invariant continuous-time state-space system $\dot{m}(t) = A m(t) + B x(t)$ whose transfer function computes an optimal $d$-order Padé approximation to the ideal delay operator $e^{-\theta s}$ across sliding window $[t - \theta, t]$.
- **Reconstruction:** Historical signal is reconstructed via shifted Legendre polynomials: $x(t - \tau) \approx \sum_{i=0}^{d-1} m_i(t) P_i(\tau / \theta)$.
- **Critical LEBRE Audit Question:** *Can LMU serve as a compressed history provider?*
- **Skeptical Analysis:** For bandlimited, continuous signals, LMU provides exceptional temporal compression ($d \ll W$). However, on discrete white noise, high-degree Legendre approximations suffer from boundary oscillation (Gibbs/Runge-like artifacts), and updating the dense state vector $m \in \mathbb{R}^d$ costs $O(d^2)$ or $O(d)$ FLOPs per step per channel. We include LMU strictly as a diagnostic compressed-history comparator, not as a replacement for LEBRE recurrence.

### L4. HiPPO: High-Order Polynomial Projection Operators
- **Primary Citation:** Gu, A., Dao, T., Ermon, S., Rudra, A., & Ré, C. (2020). *HiPPO: Recurrent memory with optimal polynomial projections*. NeurIPS 2020.
- **Core Principles:** Formalizes online continuous memory as an orthogonal polynomial projection onto a time-varying measure (e.g., sliding window via Legendre measure $\mu(t) = \frac{1}{\theta} \mathbb{I}_{[t-\theta, t]}$).
- **Critical LEBRE Audit Question:** *Does polynomial projection preserve isolated discrete delays?*
- **Skeptical Analysis:** HiPPO proves that sliding-window memory can be maintained with optimal $L_2$ error. However, $L_2$-optimal polynomial projection concentrates its energy on low-frequency modes. In an IID Gaussian stream, an isolated lag at $k=28$ requires high polynomial degrees ($N_p \ge 32$) to localize, which completely eliminates the memory savings ($N_p \ge L_{\max}$).

### L5. Multirate Signal Processing & Decimation
- **Primary Citations:** Crochiere, R. E., & Rabiner, L. R. (1983). *Multirate Digital Signal Processing*. Prentice-Hall. Vaidyanathan, P. P. (1993). *Multirate Systems and Filter Banks*. Prentice Hall.
- **Core Principles:** Decreases sampling rate by factor $M$ (decimation: $\downarrow M$). Nyquist-Shannon sampling theorem mandates that downsampling without an anti-aliasing low-pass filter ($H(e^{j\omega}) = 0$ for $|\omega| > \pi / M$) creates irreversible spectral fold-over (aliasing).
- **Critical LEBRE Audit Question:** *Can history be stored at decreasing temporal resolution?*
- **Skeptical Analysis:** If history is downsampled naively ($x_{t-2k}$ stored, $x_{t-2k-1}$ discarded), odd lags are **completely unavailable** for point lookup. If an anti-alias filter is applied, the stored value is an average, not the true instantaneous sample $x_{t-k}$. Therefore, multirate history can only discover lags on signals with genuine low-frequency temporal correlation.

### L6. Finite-Precision Adaptive Filtering & Fixed-Point Analysis
- **Primary Citations:** Yousef, N. R., & Sayed, A. H. (2003). *Fixed-point steady-state analysis of adaptive filters*. Int. J. Adapt. Control Signal Process., 17(10), 743–761. Widrow, B., & Stearns, S. D. (1985). *Adaptive Signal Processing*. Prentice-Hall.
- **Core Principles:** Analyzes the effect of finite word length in adaptive filters. Uniform quantization of signal samples to $B$ bits introduces quantization noise $q_t \sim \mathcal{U}(-\frac{\Delta}{2}, \frac{\Delta}{2})$ with variance $\sigma_q^2 = \frac{\Delta^2}{12} = \frac{X_{\max}^2 2^{-2B}}{3}$.
- **Implication for History Storage:** Lowering sample precision from float32 to float16 or int8 introduces zero temporal distortion (all timesteps remain individually addressable), but injects quantization noise into the candidate cross-correlation estimator:
  $$\hat{\rho}_{i, k} = \frac{1}{T} \sum e_t (x_{i, t-k} + q_{i, t-k}) = \rho_{i, k} + \frac{1}{T} \sum e_t q_{i, t-k}$$
  Since $e_t$ and $q_{i, t-k}$ are uncorrelated, the estimator remains **unbiased**, but its variance increases.

### L7. Stream Sketches (CountSketch & Related Algorithms)
- **Primary Citations:** Charikar, M., Chen, K., & Farach-Colton, M. (2004). *Finding frequent items in data streams*. Theoretical Computer Science, 312(1), 3–15. Cormode, G., & Muthukrishnan, S. (2005). *An improved data stream summary: the count-min sketch and its applications*. J. Algorithm, 55(1), 58–75.
- **Core Principles:** Estimates point queries over high-dimensional frequency vectors $v \in \mathbb{R}^N$ by hashing items into a small 2D bucket array.
- **Critical LEBRE Audit Question:** *Can sketch algorithms replace the time-series delay buffer?*
- **Skeptical Analysis:** **NO.** In literature, "point query" means: *"Given item $i$, estimate the frequency $f_i$."* It does **not** mean: *"Given lag $k$, recover the real-valued signal sample $x_{t-k}$."* Hashing real continuous signals across time into hash buckets destroys chronological order. Stream sketches are fundamentally inapplicable to time-series history storage.

---

## 2. Section B4: Master Literature Audit Table

| REFERENCE | YEAR | PRIMARY SOURCE VERIFIED | STREAMING | WINDOW BOUNDED | STATE SIZE COMPLEXITY | UPDATE COMPLEXITY | EXACT POINT LOOKUP | APPROX POINT LOOKUP | RECONSTRUCTION AVAILABLE | ERROR BOUND | ASSUMPTIONS ON SIGNAL | PRESERVES ARBITRARY DISCRETE DELAY? | BEHAVIOR ON IID GAUSSIAN HISTORY | BEHAVIOR ON SMOOTH HISTORY | DIRECT APPLICABILITY TO LEBRE | WHY INCLUDED | WHY NOT DIRECTLY IMPORTED |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Datar et al.** | 2002 | YES | YES | YES | $O(\frac{1}{\epsilon} \log^2 W)$ | $O(\frac{1}{\epsilon} \log W)$ | NO | NO | NO | $\epsilon \cdot \text{Sum}$ | Positive integers / bits | **NO** | Discards individual values; clusters timestamps | Discards individual values | Inapplicable | Historical baseline for sliding windows | Only supports aggregate queries, not sample lookup |
| **Gilbert et al.** | 2001 | YES | YES | YES | $O(B)$ | $O(\log W)$ | NO | YES | YES | $\|x - \hat{x}\|_2 \le \text{tail}$ | Piecewise smooth / compressible | **POOR** | Truncates noise; heavy reconstruction error | Excellent compression ($B \ll W$) | High Compute | Representative multiresolution synopsis | High update cost; attenuates sharp discrete delays |
| **Voelker et al. (LMU)** | 2019 | YES | YES | YES | $O(d)$ | $O(d)$ | NO | YES | YES | Padé order $d$ error | Bandlimited continuous signal | **POOR** | Boundary ringing (Runge/Gibbs); loses sharp lags | Exceptional smooth compression | Moderate | State-of-the-art continuous memory model | Matrix update FLOPs violate R2-FLOP; loses IID lags |
| **Gu et al. (HiPPO)** | 2020 | YES | YES | YES | $O(N_p)$ | $O(N_p)$ | NO | YES | YES | $L_2(\mu)$ optimal projection | Square-integrable measure | **POOR** | Requires $N_p \approx W$ for discrete lags | Optimal orthogonal polynomial recovery | Moderate | Foundation of modern state-space models | No memory savings on IID discrete delay streams |
| **Crochiere & Rabiner** | 1983 | YES | YES | YES | $O(W / M)$ | $O(M)$ | NO | YES (if bandlimited) | YES (interpolated) | Aliasing error / Filter ripple | Bandlimited: $\omega_{\max} < \frac{\pi}{M}$ | **CONDITIONAL** | Aliases high frequencies; destroys un-sampled lags | Preserves signal within decimation passband | **HIGH** | Foundational multirate signal processing | Fails completely on IID white noise without correlation |
| **Yousef & Sayed** | 2003 | YES | YES | YES | $O(W \cdot B)$ | $O(1)$ | YES | YES | YES | $\sigma_q^2 = \frac{\Delta^2}{12}$ | Bounded dynamic range | **YES** | Preserves exact coordinates; adds unbiased noise | Preserves coordinates; noise scales with bits | **CRITICAL** | Core analytical basis for reduced word length | Direct basis for H1 (FP16) and H2/H3 (INT8) |
| **Charikar et al.** | 2004 | YES | YES | NO | $O(\frac{1}{\epsilon^2} \log \frac{1}{\delta})$ | $O(\log \frac{1}{\delta})$ | NO | NO | NO | $\|v - \hat{v}\|_\infty \le \epsilon \|v\|_2$ | Discrete item universe | **NO** | Destroys chronological sequence | Destroys chronological sequence | Inapplicable | Frequent item frequency contrast | Categorical mismatch: frequency sketch $\neq$ history ring |
