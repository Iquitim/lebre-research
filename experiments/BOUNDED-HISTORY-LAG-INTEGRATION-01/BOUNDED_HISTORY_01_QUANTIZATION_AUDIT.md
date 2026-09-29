# BOUNDED-HISTORY-LAG-INTEGRATION-01: Quantization Audit
## Finite-Word-Length Analysis, Saturation Behavior & Steady-State Excess MSE

**Stage:** `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Theoretical Basis:** Yousef & Sayed (2003); Widrow & Stearns (1985)

---

## 1. Mathematical Formulation of Quantization Noise in History Storage

Let $x_t \in \mathbb{R}$ represent an input signal sample. When written to a quantized buffer of word length $B$ bits with dynamic range $[-V_{\max}, V_{\max}]$, the stored representation is:
$$x_t^{(q)} = \mathcal{Q}(x_t) = x_t + \eta_t$$
where $\eta_t$ is the quantization noise modeled as an uncorrelated white noise sequence with zero mean and variance:
$$\sigma_\eta^2 = \frac{\Delta^2}{12} = \frac{1}{12} \left(\frac{2 V_{\max}}{2^B - 1}\right)^2 \approx \frac{V_{\max}^2}{3 \cdot 2^{2B}}$$

### 1.1 Quantization Noise by Bit-Width ($V_{\max} = 4.0$, standard normalized input)
- **Float32 ($B=24$ mantissa bits):** $\sigma_\eta^2 \approx 1.89 \times 10^{-15} \approx 0$
- **Float16 ($B=11$ mantissa bits):** $\Delta = \frac{8}{2047} \approx 3.9 \times 10^{-3} \implies \sigma_\eta^2 \approx 1.27 \times 10^{-6}$
- **Int16 ($B=16$ signed bits):** $\Delta = \frac{8}{65535} \approx 1.22 \times 10^{-4} \implies \sigma_\eta^2 \approx 1.24 \times 10^{-9}$
- **Int8 ($B=8$ signed bits):** $\Delta = \frac{8}{255} \approx 3.14 \times 10^{-2} \implies \sigma_\eta^2 \approx 8.20 \times 10^{-5}$

---

## 2. Theoretical Excess MSE Induced by Quantized History

In normalized LMS adaptive filtering with active tap weight $w^*$, the prediction using quantized past sample $x_{t-k}^{(q)}$ is:
$$\hat{y}_t = w^* x_{t-k}^{(q)} = w^* (x_{t-k} + \eta_{t-k}) = w^* x_{t-k} + w^* \eta_{t-k}$$
The additional steady-state error variance directly contributed by history quantization is:
$$\text{EMSE}_{\text{quant}} = (w^*)^2 \cdot \sigma_\eta^2$$
For an active tap with coefficient $w^* = 0.8$:
- **FP16:** $\text{EMSE}_{\text{quant}} = (0.8)^2 \times (1.27 \times 10^{-6}) = \mathbf{8.13 \times 10^{-7}}$ (Completely negligible!)
- **INT16:** $\text{EMSE}_{\text{quant}} = (0.8)^2 \times (1.24 \times 10^{-9}) = \mathbf{7.94 \times 10^{-10}}$ (Completely negligible!)
- **INT8:** $\text{EMSE}_{\text{quant}} = (0.8)^2 \times (8.20 \times 10^{-5}) = \mathbf{5.25 \times 10^{-5}}$ (Negligible, $< 10^{-4}$!)

### 2.3 Impact on Candidate Probing (Cross-Correlation Estimation)
When probing candidate pair $(i, k)$ using noisy historical sample $x_{i, t-k} + \eta_{i, t-k}$:
$$\hat{\rho}_{i, k} = \frac{1}{T} \sum_{t=1}^T e_t (x_{i, t-k} + \eta_{i, t-k}) = \rho_{i, k} + \frac{1}{T} \sum_{t=1}^T e_t \eta_{i, t-k}$$
Because $e_t$ and $\eta_{i, t-k}$ are statistically independent, $\mathbb{E}[e_t \eta_{i, t-k}] = 0$.
The estimator remains strictly **unbiased**. The sample variance increases by $\frac{\sigma_e^2 \sigma_\eta^2}{T}$.
For $T \ge 100$ probing steps, this variance is $< 10^{-6}$, proving that **quantization noise does not prevent accurate candidate promotion** down to 8 bits.
