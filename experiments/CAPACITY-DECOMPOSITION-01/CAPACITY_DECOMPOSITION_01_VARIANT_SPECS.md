# CAPACITY-DECOMPOSITION-01: Formal Model & Variant Specifications

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** Preregistered Algorithmic Specifications

---

## 1. Prequential Causal Execution Interface

All variants implement the strict prequential streaming protocol:
```
for t in 1 .. T:
    x_t, y_t = stream[t]
    x_norm_t = normalizer.transform(x_t)
    
    # 1. Causal Prediction (strictly prior to observing y_t in training)
    y_hat_t, flops_pred = model.predict(x_norm_t)
    
    # 2. Evidence Recording
    loss_t = (y_t - y_hat_t) ** 2
    record_evidence(loss_t)
    
    # 3. Model Parameter Adaptation
    flops_update = model.update(x_norm_t, y_t)
    normalizer.update(x_t)
```

---

## 2. Level 0: Frozen Baseline References

### B0: `LEBRE_v0.1_FROZEN`
- Canonical frozen Track-B architecture with linear NLMS base + provisional/active scalar recurrent state.
- Lifecycle thresholds: $T_{\text{prob}} = 50, \theta_{\text{promote}} = 0.05, \theta_{\text{birth}} = 0.15, \theta_{\text{ret}} = 0.02, N_{\text{pat}} = 30$.
- Parameters: $D + 5 = 25$ params (at $D=20$). Compute: $\approx 90.4$ FLOPs/step. Memory: $\approx 440$ bytes.

### B1: `LEBRE_NO_REC_BIRTH`
- Identical to $B0$ except recurrent candidate birth is permanently inhibited (`_trigger_birth` disabled).
- Operates purely as adaptive linear learner on instantaneous $x_t$.
- Parameters: $D = 20$ params. Compute: $64.0$ FLOPs/step. Memory: $360$ bytes.

### B2: `LEBRE_FIXED_STRICT_DIAGNOSTIC`
- Identical to $B0$ except candidate promotion threshold is tightened to $\theta_{\text{promote}} = 0.15$.
- Parameters: $D + 5 = 25$ params. Compute: $73.7$ FLOPs/step. Memory: $440$ bytes.

---

## 3. Level 1: Estimator Sufficiency Variants (Input: $\mathbf{x}_t \in \mathbb{R}^D$)

### E0: `NLMS_GRADIENT` (Current Frozen Linear Estimator)
- Prediction: $\hat{y}_t = \mathbf{w}_t^T \mathbf{x}_t$
- Update: $e_t = y_t - \hat{y}_t$, $\quad \mathbf{w}_{t+1} = \mathbf{w}_t + \frac{\mu}{\epsilon + \|\mathbf{x}_t\|^2} e_t \mathbf{x}_t$ ($\mu = 0.10, \epsilon = 10^{-4}$).
- FLOPs: $2D$ (dot product) + $2D + 3$ (update) = $4D + 3$ FLOPs/step ($83$ FLOPs at $D=20$).
- Parameters: $D$. Persistent Memory: $8D + 32$ bytes.

### E1: `ONLINE_RLS` (Recursive Least Squares)
- Prediction: $\hat{y}_t = \mathbf{w}_t^T \mathbf{x}_t$
- Gain vector: $\mathbf{k}_t = \frac{\mathbf{P}_{t-1} \mathbf{x}_t}{\lambda + \mathbf{x}_t^T \mathbf{P}_{t-1} \mathbf{x}_t}$ ($\lambda = 0.999$, $\mathbf{P}_0 = 100 \cdot \mathbf{I}$).
- Parameter update: $\mathbf{w}_t = \mathbf{w}_{t-1} + \mathbf{k}_t (y_t - \hat{y}_t)$
- Inverse covariance update: $\mathbf{P}_t = \frac{1}{\lambda} [\mathbf{P}_{t-1} - \mathbf{k}_t \mathbf{x}_t^T \mathbf{P}_{t-1}]$
- FLOPs: $4D^2 + 4D$ FLOPs/step ($1,680$ FLOPs at $D=20$).
- Parameters: $D$. Persistent Memory: $8(D^2 + D) + 64$ bytes ($3,424$ bytes at $D=20$).

### E2: `REGULARIZED_RLS`
- Identical to $E1$ with regularized shrinkage $\delta = 1.0$: $\mathbf{P}_0 = \frac{1}{\delta} \mathbf{I}$.

### E3: `OFFLINE_OLS_ORACLE` (Diagnostic Ceiling, Non-Causal)
- Fit on entire test segment via SVD: $\mathbf{w}_* = (\mathbf{X}_{\text{test}}^T \mathbf{X}_{\text{test}} + 10^{-6} \mathbf{I})^{-1} \mathbf{X}_{\text{test}}^T \mathbf{y}_{\text{test}}$.
- Measures the absolute empirical linear representation limit of $\mathbf{x}_t$ under zero estimator variance.

### E4: `OFFLINE_RIDGE_ORACLE` (Diagnostic Ceiling, Non-Causal)
- Fit with Ridge penalty $\alpha = 1.0$: $\mathbf{w}_* = (\mathbf{X}_{\text{test}}^T \mathbf{X}_{\text{test}} + \alpha \mathbf{I})^{-1} \mathbf{X}_{\text{test}}^T \mathbf{y}_{\text{test}}$.

---

## 4. Level 2: Finite Temporal Representation (Delay Coordinates)

All delay variants maintain a circular delay line $\mathbf{B}_t = [\mathbf{x}_t, \mathbf{x}_{t-1}, \dots, \mathbf{x}_{t-L}]$ and learn linear readout weights via NLMS:

### T0: `LAG_0` ($\mathbf{x}_t$ only)
- Dimension: $D = 20$. Parameters: $20$. Compute: $64$ FLOPs.

### T1: `LAG_1` ($[\mathbf{x}_t, \mathbf{x}_{t-1}]$)
- Dimension: $2D = 40$. Parameters: $40$. Compute: $128$ FLOPs. Memory: $480$ bytes.

### T2: `LAG_2` ($[\mathbf{x}_t, \mathbf{x}_{t-1}, \mathbf{x}_{t-2}]$)
- Dimension: $3D = 60$. Parameters: $60$. Compute: $192$ FLOPs. Memory: $640$ bytes.

### T3: `LAG_4` ($[\mathbf{x}_t, \dots, \mathbf{x}_{t-4}]$)
- Directly covers target delay for Task A2 ($x_{1, t-4}$) and partial delay for Task A3 ($x_{1, t-2}$).
- Dimension: $5D = 100$. Parameters: $100$. Compute: $320$ FLOPs. Memory: $960$ bytes.

### T4: `LAG_8` ($[\mathbf{x}_t, \dots, \mathbf{x}_{t-8}]$)
- Directly covers both target delays for Task A3 ($x_{1, t-2}$ and $x_{2, t-8}$).
- Dimension: $9D = 180$. Parameters: $180$. Compute: $576$ FLOPs. Memory: $1,600$ bytes.

### T5: `SPARSE_LAG_BANK` ($[\mathbf{x}_t, x_{1, t-4}, x_{1, t-8}, x_{1, t-30}]$)
- Targeted sparse delay line covering A2, A3, and long delay A4 ($t-30$).
- Dimension: $D + 3 = 23$. Parameters: $23$. Compute: $74$ FLOPs. Memory: $420$ bytes.

---

## 5. Level 3: Static Nonlinearity Controls (No Memory)

### NL1: `POLYNOMIAL_DEG2`
- Quadratic basis expansion on top $k=5$ PCA features of $\mathbf{x}_t$: $z = [x_i, x_i x_j]$.
- Dimension: $5 + 15 = 20$. Parameters: $20$. Compute: $\approx 95$ FLOPs.

### NL2: `RANDOM_FOURIER_FEATURES` (RFF)
- Mapping: $\phi(\mathbf{x}_t) = \sqrt{\frac{2}{K}} \cos(\mathbf{\Omega} \mathbf{x}_t + \mathbf{b})$, where $\mathbf{\Omega}_{ij} \sim \mathcal{N}(0, \sigma^2)$, $\mathbf{b}_j \sim \mathcal{U}(0, 2\pi)$.
- Dimension: $K = 50$. Linear readout on $\phi(\mathbf{x}_t)$ via NLMS.
- Parameters: $50$ linear weights (plus fixed frozen projection). Compute: $\approx 160$ FLOPs.

### NL3: `DIAGNOSTIC_MLP` (Online Shallow Neural Network)
- Architecture: $D \to 16 \to 1$ (ReLU activation, online SGD backprop).
- Parameters: $20 \times 16 + 16 + 16 + 1 = 353$ params. Compute: $\approx 720$ FLOPs.

---

## 6. Level 4: Temporal + Nonlinear Control

### TNL1: `LAG4_PLUS_RFF`
- Input: Delay coordinate $\mathbf{z}_t = [\mathbf{x}_t, \dots, \mathbf{x}_{t-4}] \in \mathbb{R}^{100}$.
- Projected through Random Fourier Features ($K=50$) with linear NLMS readout.
- Parameters: $50$ trainable weights. Compute: $\approx 350$ FLOPs.

---

## 7. Level 5 & 6: Recurrent State Dimension Scaling ($N \in \{1, 2, 4\}$)

### REC_N1: `SCALAR_RECURRENCE` ($N=1$)
- Recurrent state: $s_t = \sigma(\lambda s_{t-1} + \mathbf{u}^T \mathbf{x}_t)$ ($\sigma = \tanh$, $\lambda \in (-1, 1)$).
- Readout: $\hat{y}_t = \mathbf{w}_{\text{base}}^T \mathbf{x}_t + w_s s_t$.
- Real-time sensitivity: $p_t = \frac{\partial s_t}{\partial \lambda} = \sigma'(a_t) [s_{t-1} + \lambda p_{t-1}]$.
- Parameters: $D$ (base) $+ 1$ ($w_s$) $+ 1$ ($\lambda$) $+ D$ ($\mathbf{u}$) $= 2D + 2 = 42$ params (at $D=20$).
- Compute: $\approx 92$ FLOPs/step. Persistent Memory: $\approx 440$ bytes.

### REC_N2: `TWO_STATE_RECURRENCE` ($N=2$)
- Recurrent state vector $\mathbf{s}_t \in \mathbb{R}^2$: $\mathbf{s}_t = \tanh(\mathbf{\Lambda} \mathbf{s}_{t-1} + \mathbf{U} \mathbf{x}_t)$, where $\mathbf{\Lambda} = \begin{pmatrix} \lambda_{11} & \lambda_{12} \\ \lambda_{21} & \lambda_{22} \end{pmatrix}$.
- Supports complex conjugate eigenvalues, allowing damped oscillatory impulse response $h[k] = r^k \cos(\omega k + \phi)$.
- Parameters: $D + 2 + 4 + 2D = 3D + 6 = 66$ params.
- Compute: $\approx 145$ FLOPs/step. Persistent Memory: $\approx 620$ bytes.

### REC_N4: `FOUR_STATE_RECURRENCE` ($N=4$)
- State vector $\mathbf{s}_t \in \mathbb{R}^4$: $\mathbf{s}_t = \tanh(\mathbf{\Lambda} \mathbf{s}_{t-1} + \mathbf{U} \mathbf{x}_t)$.
- Parameters: $D + 4 + 16 + 4D = 5D + 20 = 120$ params.
- Compute: $\approx 290$ FLOPs/step. Persistent Memory: $\approx 1,120$ bytes.

---

## 8. Auxiliary Diagnostic Variants

### Normalization Audit (Section 8)
- `NORM0`: Frozen causal online standardization (`CausalStandardScaler`: running mean and variance updated causal-prequentially).
- `NORM1`: Normalization frozen after warm-up phase ($t=500$).
- `NORM2`: Development statistics normalization (mean/var fixed to development seed empirical values).
- `NORM3`: Full-stream oracle normalization (non-causal diagnostic ceiling computed on test set).

### Interference Audit (Section 9)
- `I0`: Standard live baseline comparator (baseline continues updating).
- `I1`: Snapshot comparator (baseline weights frozen at candidate birth for candidate scoring).
- `I2`: Frozen baseline window (both baseline and candidate evaluate against frozen reference).
