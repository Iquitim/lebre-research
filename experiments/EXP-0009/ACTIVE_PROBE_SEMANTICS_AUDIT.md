# EXP-0009: Active Probe Semantics Audit
**Pre-Execution Verification of Active Perturbation Validity in Streaming Regression**

---

## 0. Audit Purpose & Governance

Under Section 44–46 of the EXP-0009 Experimental Protocol, active probing must be rigorously audited before any diagnostic execution to ensure that:
1. Active perturbations do not violate streaming environment semantics.
2. The perturbation target is mathematically well-defined.
3. Causal ordering and temporal consistency are preserved.
4. Ground truth is never accessed or leaked into candidate selection, code assignment, or decoding.

If any check fails, execution must halt immediately with status `ACTIVE_PROBE_SEMANTICS_INVALID`.

---

## 1. Audit Questions & Formal Answers

### Question 1: What exactly is being perturbed?
**Answer**:
The perturbation is applied **exclusively to the learner's shadow prediction hypothesis on out-of-sample observations**.
Specifically, when evaluating an unselected candidate $j$ (or a group of candidates $G$), the baseline prediction on future step $t+r$ is:
$$\hat{y}_{\text{base}, t+r} = \sum_{k \in S_t} w_k(t) \cdot x_{t+r, k}$$
The shadow active probe adds a temporary, diagnostic excitation term $\Delta \hat{y}_{t+r}$:
$$\hat{y}_{t+r}^{(pert)} = \hat{y}_{\text{base}, t+r} + \Delta \hat{y}_{t+r}$$
The underlying data generation mechanism of the environment ($y_{t+r} = \sum_{j \in S^*} \beta_j x_{t+r, j} + \epsilon_{t+r}$) is **NOT mutated**. The candidate feature values $x_{t+r, j}$ are drawn naturally by the environment and are never overwritten.

---

### Question 2: Is the perturbation applied to prediction contribution, candidate coefficient, candidate feature, or another quantity?
**Answer**:
The perturbation is applied to the **candidate's shadow prediction contribution**, parameterized by a bounded virtual coefficient:
- **Individual Candidate Probing (A1, A2, A4)**:
  $$\Delta \hat{y}_{t+r}^{(j)} = \delta \cdot s_r \cdot x_{t+r, j}$$
  where $\delta = 0.10$ is a fixed, small coefficient amplitude ($\approx 7\% - 11\%$ of typical true coefficients $|\beta_j| \in [0.9, 1.6]$), and $s_r \in \{-1, +1\}$ is the probe sign code.
- **Orthogonal Group Probing (A3)**:
  $$\Delta \hat{y}_{t+r}^{(G)} = \sum_{j \in G} \delta \cdot H[j, r] \cdot x_{t+r, j}$$
  where $H[j, r] \in \{-1, +1\}$ is row $j$ of a Walsh-Hadamard orthogonal matrix.

---

### Question 3: Is the resulting response mathematically meaningful in the current synthetic environment?
**Answer**:
**YES**.
In the linear Gaussian stream:
$$y_{t+r} = \sum_{k \in S_t} w_k^* x_{t+r, k} + \sum_{j \in S^* \setminus S_t} \beta_j x_{t+r, j} + \epsilon_{t+r}$$
The baseline residual is:
$$e_{\text{base}, t+r} = y_{t+r} - \hat{y}_{\text{base}, t+r} = \sum_{k \in S_t} (w_k^* - w_k(t)) x_{t+r, k} + \sum_{j \in S^* \setminus S_t} \beta_j x_{t+r, j} + \epsilon_{t+r}$$

When symmetric paired perturbations $\pm \Delta \hat{y}$ are evaluated on the **same sample**:
$$L_{-} = (e_{\text{base}, t+r} + \Delta \hat{y})^2 = e_{\text{base}, t+r}^2 + 2 e_{\text{base}, t+r} \Delta \hat{y} + (\Delta \hat{y})^2$$
$$L_{+} = (e_{\text{base}, t+r} - \Delta \hat{y})^2 = e_{\text{base}, t+r}^2 - 2 e_{\text{base}, t+r} \Delta \hat{y} + (\Delta \hat{y})^2$$

Subtracting the two losses yields the **exact linear directional response**:
$$L_{-} - L_{+} = 4 e_{\text{base}, t+r} \Delta \hat{y}$$

Notice two critical mathematical properties:
1. **The common baseline residual squared error $e_{\text{base}}^2$ completely cancels out!**
2. **The quadratic perturbation penalty $(\Delta \hat{y})^2$ completely cancels out!**
3. For an individual candidate $j$, $L_{-} - L_{+} = 4 \delta \cdot (e_{\text{base}, t+r} x_{t+r, j})$.
4. For an orthogonal group $G$, $L_{-} - L_{+} = 4 \delta \sum_{j \in G} H[j, r] (e_{\text{base}, t+r} x_{t+r, j})$.

This establishes an exact, linear code-division multiplexed observation channel without second-order distortion.

---

### Question 4: Does the perturbation preserve causal ordering?
**Answer**:
**YES**.
All shadow evaluations are conducted strictly on **future time steps** $t+r > t$, where $t$ is the time step at which the candidate probe was scheduled.
The observer registers pending active tests at step $t$ and processes their responses sequentially as future streaming samples $(x_{t+r}, y_{t+r})$ arrive in subsequent environment steps.
At no point does the observer inspect future data prematurely.

---

### Question 5: Can paired measurements share the same environmental realization?
**Answer**:
**YES**.
Because the perturbation is applied to the learner's computational prediction hypothesis ($\hat{y}_+ = \hat{y}_{\text{base}} + \Delta \hat{y}$ vs $\hat{y}_- = \hat{y}_{\text{base}} - \Delta \hat{y}$) and NOT to the external environment, both $L_+$ and $L_-$ can be computed on the identical realization $(x_{t+r}, y_{t+r})$ of the data stream.
In accordance with Section 49, this same-sample comparison is counted explicitly as **two shadow predictive evaluations (computational cost)**, not as two separate world samples.

---

### Question 6: Does active probing accidentally reveal ground truth?
**Answer**:
**NO**.
1. Candidate selection for active probing is determined strictly by the baseline probe policy (e.g. queue service order).
2. The sign codes $s_r \in \{-1, +1\}$ and Walsh-Hadamard matrices $H \in \{-1, +1\}^{G \times R}$ are generated via fixed, deterministic pseudo-random or algebraic rules independent of true feature identities, true signs, or weights.
3. Group assignment pools candidates strictly by inactive index or queue position, with zero knowledge of $S^*$.
4. Decoding correlates observed scalar loss responses against the known assigned code, with zero access to true support labels.
5. True support labels are utilized strictly in offline post-processing to compute diagnostic performance metrics (PR-AUC, ROC-AUC, Precision@K, and Oracle upper bounds).

---

## 2. Pre-Audit Verdict

| Criteria | Status | Detail |
| :--- | :---: | :--- |
| **Perturbation Target Valid** | **PASS** | Shadow prediction hypothesis only; environment unmutated. |
| **Mathematical Meaningfulness** | **PASS** | $L_- - L_+ = 4\delta e x$ proves exact cancellation of quadratic & baseline noise. |
| **Causal Ordering Preserved** | **PASS** | Strictly future samples ($t+r > t$). |
| **Same-Sample Pairing Counted** | **PASS** | Computed on same realization; counted as extra shadow FLOPs. |
| **Zero Truth Leakage** | **PASS** | Codes and groups generated algebraically; truth offline only. |
| **AUDIT_STATUS** | **`ACTIVE_PROBE_SEMANTICS_VALID`** | **APPROVED TO EXECUTE** |
