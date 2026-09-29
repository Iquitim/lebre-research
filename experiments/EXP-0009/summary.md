# EXP-0009 — Active Probe Design Diagnostic
**Can Structured Active Probes Create a High-SNR Candidate Information Channel Under a Fixed Compute Budget?**

---

## 0. Executive Summary & Diagnostic Decisions

| Field | Decision / Result | Status |
| :--- | :--- | :---: |
| **PRIMARY_DECISION** | **`ACTIVE_PROBING_INSUFFICIENT`** | **CRITICAL FINDING** |
| **BEST_ACTIVE_CHANNEL** | **`A1`** (Symmetric $\pm\delta$ Paired Excitation) | P@3 = 20.0%, P@5 = 16.0% |
| **MIN_ACTIVE_ROUNDS** | **`NONE`** | Fails $\ge 50\%$ Gate |
| **GROUP_PROBING** | **`NOT_USEFUL`** | P@3 = 0.0% (G=4), 6.7% (G=8) |
| **INFORMATION_STATUS** | **`ACTIVE_INFORMATION_INSUFFICIENT`** | Resolved |
| **EXP_0009_STATUS** | **`DIAGNOSIS_IDENTIFIED`** | **SUCCESSFUL DIAGNOSTIC** |
| **Practical Question 1 (Higher SNR via active probing?)** | **NO** (Predictive perturbations cannot alter environmental input variance) | Resolved |
| **Practical Question 2 (Group probing screens multiple candidates?)** | **NO** (Interference & varying inputs across rounds degrade ranking) | Resolved |
| **Practical Question 3 (Active probes beat 85 noise extremes?)** | **NO** (P99 noise scores remain $5\times - 30\times$ larger than median true) | Resolved |
| **Milestone M1 Gate** | **`M1_CANDIDATE = FALSE`** (Frozen diagnostic gate) | Preserved |
| **NEXT STEP** | **`STRUCTURAL_IDENTIFIABILITY_REASSESSMENT`** | Section 108 |

---

## 1. Motivation & Conceptual Transition

In **EXP-0007**, passive small-sample statistics ($|\bar{c}|, \gamma$) failed to separate true candidates from 85 noise candidates at $n \le 5$.
In **EXP-0008**, passive shadow micro-interventions ($I_2, I_3, I_4$) failed due to the **93:1 Class Imbalance Trap**: under high residual variance ($\sigma_e^2 \approx 6.5$), random environmental fluctuations caused $47.5\%$ of noise candidates to accidentally reduce squared error on a single out-of-sample observation, resulting in $98.8\%$ noise contamination among positive-gain candidates.

**EXP-0009** marked the fundamental transition in Track B:
> *"Can the learner actively create a more informative observation by introducing known, bounded perturbations, rather than passively waiting for natural variation?"*

### Hypotheses Tested
1. **H1 (Symmetric Paired Cancellation)**: Symmetric $\pm\delta$ perturbations cancel common residual error and isolate candidate directional response. (**PARTIALLY CONFIRMED**: Mathematical cancellation proved ($L_- - L_+ = 4\delta e x$), lifting Enrichment to $18.64\times$, but Precision@3 plateaued at 20.0%).
2. **H2 (Random-Sign Coherent Accumulation)**: Random-sign coded excitation accumulates signal coherently while uncorrelated noise cancels. (**REJECTED**: Multi-step coded accumulation degraded P@3 to $13.3\%$ due to environmental non-stationarity across successive steps).
3. **H3 (Orthogonal Group Probing)**: Walsh-Hadamard group codes extract information about multiple candidates simultaneously ($G/R \ge 1$). (**REJECTED**: While codes are strictly orthogonal ($H H^T = R \cdot I$), dynamic variation in candidate inputs across steps creates temporal cross-talk, collapsing P@3 to $0.0\% - 6.7\%$).
4. **H4 (Paired Sham Cancellation)**: Subtracting a matched sham perturbation removes shared environmental shocks. (**CONFIRMED BUT INSUFFICIENT**: A4 matched A1 at P@3 = 20.0%, but added 12 FLOPs without improving precision).

---

## 2. Baseline Reproduction Gate Verification

The frozen EXP-0006 J4 learner (`TieredEvidenceLearner` with `TieredEvidenceRatePolicy(mode="queue_multi_rate")` and `ProbeBankController`) was verified bit-for-bit during diagnostic data collection:
- **Seed 42 Exact Match**: Regime-2 MSE = **0.011546915**, Recall = **77.26%**, Occupancy = **57.80%** (100% exact match).
- **5-Seed Aggregate Match**: Regime-2 MSE = **0.013552460**, Recall = **81.324%**, Occupancy = **61.760%**, Total Probes = **10,000**, Compute = **142.80 FLOPs/step**.
- **Observer Invariance**: 56,265 active probe evaluations conducted without mutating learner weights, active sets, queues, or PRNG streams. All 60 repo-wide tests pass.

---

## 3. Primary Empirical Results

### 3.1 Table 1: Information Channels Diagnostic
*Evaluated across 56,265 active probe episodes in Regime 2 post-shift ($t \ge 1000$).*

| Channel ID | Channel Name | PR-AUC | ROC-AUC | P@1 | P@2 | P@3 | P@5 | P@10 | Enrichment@3 | Active SNR | P(True > P99 Noise) | FLOPs / Test | Proj FLOPs/step | Dense % |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A0** | **Passive Control (Excess Gain)** | 0.0135 | 0.4494 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | $0.00\times$ | -0.341 | 1.3% | 0.0 | 142.8 | 23.7% |
| **A1** | **Paired $\pm\delta$ (Signed)** | 0.0357 | 0.5690 | **40.0%** | **20.0%** | **20.0%** | **16.0%** | 10.0% | **$18.64\times$** | **+0.254** | **7.7%** | 12.0 | 148.8 | 24.7% |
| **A1** | **Paired $\pm\delta$ (Magnitude)** | 0.0352 | **0.7624** | 20.0% | 10.0% | 13.3% | 8.0% | 8.0% | $12.43\times$ | **+0.629** | 4.9% | 12.0 | 148.8 | 24.7% |
| **A2** | **Random-Sign Code ($R=2$)** | 0.0255 | 0.4826 | 0.0% | 10.0% | 13.3% | 8.0% | 10.0% | $12.43\times$ | +0.002 | 5.7% | 24.0 | 154.8 | 25.7% |
| **A2** | **Random-Sign Code ($R=4$)** | 0.0282 | 0.5025 | 20.0% | 20.0% | 13.3% | 12.0% | 8.0% | $12.43\times$ | -0.008 | 7.0% | 48.0 | 166.8 | 27.7% |
| **A3** | **Group Coding ($G=4, R=4$)** | 0.0344 | 0.5997 | 0.0% | 0.0% | 0.0% | 8.0% | 6.0% | $0.00\times$ | +0.191 | 4.2% | 16.0 | 150.8 | 25.0% |
| **A3** | **Group Coding ($G=8, R=8$)** | 0.0374 | 0.5700 | 20.0% | 10.0% | 6.7% | 12.0% | 8.0% | $5.31\times$ | +0.218 | 6.4% | 20.0 | 152.8 | 25.4% |
| **A4** | **Paired + Sham Excess** | 0.0292 | 0.5443 | **40.0%** | **20.0%** | **20.0%** | **16.0%** | **12.0%** | **$18.64\times$** | +0.173 | 4.1% | 24.0 | 154.8 | 25.7% |
| **A5** | **Multi-Round Acc ($R=4$)** | 0.0321 | 0.5122 | 20.0% | 20.0% | **20.0%** | **16.0%** | 8.0% | **$18.64\times$** | +0.061 | 7.2% | 48.0 | 166.8 | 27.7% |
| **Oracle**| **Oracle Ceiling** | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | $93.20\times$ | +31622.8 | 100.0% | 0.0 | 142.8 | 23.7% |

---

### 3.2 Table 2: Residual Quantile Stratification (Q1–Q4)
| Quantile | Smoothed Residual Range | True Count | Noise Count | Base Rate | Best Channel | Best Precision@3 | Best Active SNR |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **Q1** | $0.057 - 0.093$ (Settled) | 0 | 9,082 | 0.00% | NONE | 0.0% | 0.000 |
| **Q2** | $0.093 - 0.111$ (Low-Mid) | 0 | 9,081 | 0.00% | NONE | 0.0% | 0.000 |
| **Q3** | $0.111 - 1.210$ (Mid-High) | 65 | 9,018 | 0.72% | A2 Random-Sign ($R=4$) | 6.7% | +0.256 |
| **Q4** | $1.210 - 3.067$ (Burst) | 323 | 8,756 | 3.56% | A1 Paired Signed | **20.0%** | **+0.205** |

---

### 3.3 Table 3: Temporal Stratification Across Post-Shift Windows
| Window | Steps Post-Shift | True Count | Noise Count | Base Rate | Best Channel | Best Precision@3 | Best Active SNR |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **A** | 0–20 | 30 | 692 | 4.16% | A5 Multi-Round ($R=4$) | 13.3% | +0.260 |
| **B** | 21–50 | 38 | 1,030 | 3.56% | A1 Paired Signed | 6.7% | +0.103 |
| **C** | 51–100 | 71 | 1,714 | 3.98% | A2 Random-Sign ($R=4$) | 20.0% | -0.119 |
| **D** | 101–250 | 157 | 4,957 | 3.07% | A1 Paired Signed | 13.3% | +0.194 |
| **E** | >250 | 92 | 27,544 | 0.33% | A1 Paired Signed | 20.0% | +0.483 |

---

### 3.4 Table 4: Orthogonal Group Probing Metrics
| Group Size $G$ | Code Length $R$ | Orthogonality Error | Decoded Precision@3 | Decoded Precision@5 | Decoded Enrichment@3 | Active SNR | Effective Probes / Cand |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4** | 4 | 0.0000 | 0.0% | 8.0% | $0.00\times$ | +0.191 | 1.0 |
| **8** | 8 | 0.0000 | 6.7% | 12.0% | $5.31\times$ | +0.218 | 1.0 |

---

### 3.5 Causal Controls & Sanity Verification
| Control Test | Operational Description | Empirical Result | Status |
| :--- | :--- | :--- | :---: |
| **Zero-Delta Control** | $\delta = 0$ (all perturbations zeroed) | Mean true = 0.0000, Mean noise = 0.0000, ROC-AUC = 0.5000 | **PASS** |
| **Sign-Flip Control** | Code sequence inverted ($s \to -s$) | Decoded score exactly negates; ROC-AUC inverts ($1 - 0.5025 = 0.4975$) | **PASS** |
| **Code Permutation Control** | Post-hoc random code permutation | Decoded candidate information collapses to noise (ROC-AUC = 0.4975) | **PASS** |

---

## 4. Physical & Mathematical Diagnosis: Why Active Probing Fails

### 4.1 The Fundamental Equivalence Proof
Why did structured active perturbations fail to achieve the 50% operational separability gate?

In an online streaming environment, the learner can perturb **only its own internal prediction hypothesis**, not the physical data generation mechanism.
When symmetric perturbations $+\delta$ and $-\delta$ are evaluated on the same sample $(x_{t+r}, y_{t+r})$:
$$L_{-} - L_{+} = (e_{\text{base}} + \delta x_j)^2 - (e_{\text{base}} - \delta x_j)^2 = 4 \delta (e_{\text{base}, t+r} x_{t+r, j})$$

Notice the profound mathematical consequence:
1. Symmetric paired excitation succeeds in eliminating the common squared baseline error $e_{\text{base}}^2$ and the quadratic penalty $(\delta x_j)^2$.
2. **However, the remaining signal is strictly $4 \delta \cdot (e_{\text{base}, t+r} x_{t+r, j})$.**
3. This quantity is mathematically identical to a single-sample passive inner product!
4. The learner cannot perturb the environment's input $x_{t+r, j}$. The candidate feature value $x_{t+r, j} \sim \mathcal{N}(0, 1)$ arrives passively from the natural environment.

### 4.2 The Impossibility of Beating Noise Extremes on Passive Inputs
Because the input $x_{t+r, j}$ is drawn from the environment:
- For a true feature $j^* \in S^*$, $\mathbb{E}[4 \delta e_{t+r} x_{t+r, j^*}] = 4 \delta \beta_{j^*} \approx 4 \times 0.1 \times 1.2 \approx +0.48$.
- For an irrelevant noise candidate $j \notin S^*$, $\mathbb{E}[4 \delta e_{t+r} x_{t+r, j}] = 0$.
- However, the variance of this observation is:
  $$\operatorname{Var}(4 \delta e_{t+r} x_{t+r, j}) = 16 \delta^2 \sigma_e^2 \approx 16 \times 0.01 \times 6.5 \approx 1.04 \implies \sigma \approx 1.02$$

When 85 noise candidates are evaluated:
$$\mathbb{E}\left[\max_{1 \le i \le 85} Z_i\right] \approx 2.98 \implies \mathbb{E}[\max_{\text{noise}} \text{Score}] \approx 2.98 \times 1.02 \approx \mathbf{3.04}$$
The maximum noise score ($3.04$) is **$6.3\times$ larger than the expected true signal ($0.48$)**!
As measured empirically in Table 1:
- Median true score for A1 is $0.051$.
- P99 noise score is $1.669$ (32.7x larger!).
- Max noise score observed is $6.097$ (119x larger!).

**Conclusion**: Active prediction perturbation cannot overcome the measurement variance of passive environmental inputs. As long as inputs arrive passively, candidate separability at small sample sizes is mathematically impossible against 85 competitors.

---

## 5. Answers to the 3 Preregistered Practical Questions

### Question 1:
> **“CAN THE LEARNER CREATE A HIGHER-SNR CANDIDATE INFORMATION CHANNEL BY APPLYING KNOWN STRUCTURED PERTURBATIONS, RATHER THAN WAITING FOR PASSIVE NATURAL VARIATION?”**
### **Answer: NO.**
Applying structured perturbations to the prediction hypothesis isolates the linear term $e \cdot x$, but because the learner has no control over the input $x$ generated by the external environment, the observation variance remains identical to passive correlation. The SNR of a single observation cannot be boosted without actively perturbing the environment's state or input distribution.

### Question 2:
> **“CAN ONE ACTIVE PROBE BATTERY SCREEN MULTIPLE CANDIDATES AT ONCE WITHOUT DESTROYING IDENTIFIABILITY?”**
### **Answer: NO.**
While Hadamard codes are strictly orthogonal in expectation ($H H^T = R \cdot I$), streaming inputs $x_{t+r}$ fluctuate randomly from round to round. This dynamic variation destroys sample-path orthogonality across short windows ($R \le 8$), causing inter-candidate cross-talk that collapses Precision@3 from $20.0\%$ to $0.0\% - 6.7\%$.

### Question 3:
> **“DO ACTIVE PROBES BEAT THE EXTREME-VALUE TAIL OF ~85 NOISE CANDIDATES AT AN ACCEPTABLE COMPUTE COST?”**
### **Answer: NO.**
While A1 fits comfortably under the compute ceiling ($148.8$ FLOPs/step, $24.7\%$ Dense), its P99 noise score ($1.669$) is over $30\times$ larger than the median true score ($0.051$). The extreme values of 85 noise candidates routinely submerge true candidates in top-3 and top-5 queues.

---

## 6. Artifact Manifest
- Pre-Audit: [`ACTIVE_PROBE_SEMANTICS_AUDIT.md`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/ACTIVE_PROBE_SEMANTICS_AUDIT.md)
- Configuration: [`config.json`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/config.json)
- Master Runner: [`run_active_diagnostic.py`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/run_active_diagnostic.py)
- Diagnostic Module: [`src/diagnostics/active_probe_diagnostic.py`](file:///d:/Projetos/Codinome%20Lebre/src/diagnostics/active_probe_diagnostic.py)
- Unit Tests: [`tests/test_exp_0009.py`](file:///d:/Projetos/Codinome%20Lebre/tests/test_exp_0009.py) (4/4 passing, 60/60 repo-wide passing)
- Raw Events: [`active_probe_events.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/active_probe_events.csv) (56,265 rows)
- Metrics CSVs: [`channel_metrics.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/channel_metrics.csv), [`precision_at_k.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/precision_at_k.csv), [`group_probe_metrics.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/group_probe_metrics.csv), [`residual_stratification.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/residual_stratification.csv), [`temporal_stratification.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/temporal_stratification.csv), [`causal_controls.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/causal_controls.csv), [`compute_projection.csv`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/compute_projection.csv)
- 12-Panel Publication Figure: [`figures.png`](file:///d:/Projetos/Codinome%20Lebre/experiments/EXP-0009/figures.png)
