# Literature Note: Sequential Evidence, Anytime-Valid Testing & Data-Selective Adaptation in Candidate Lifecycle Systems
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Theoretical Precedents & Epistemic Constraints

---

## 1. Executive Summary

This note reviews three foundational literature frameworks relevant to candidate probation and early decision policies in streaming adaptive filtering:
1. **Wald's Sequential Probability Ratio Test (SPRT);**
2. **Anytime-Valid Inference & Confidence Sequences;**
3. **Data-Selective Adaptive Filtering.**

The purpose is to establish principled design boundaries for potential future sequential probation mechanisms while explicitly documenting why naive applications of these theories fail in non-stationary streaming architectures like LEBRE.

---

## 2. Wald's Sequential Probability Ratio Test (SPRT)

### 2.1 Classical Foundations (Wald, 1945)
In classical hypothesis testing, sample size $N$ is fixed a priori. Abraham Wald formulated sequential analysis where data are observed incrementally $x_1, x_2, \dots$ and a likelihood ratio is maintained:
$$\Lambda_n = \prod_{i=1}^n \frac{f(x_i \mid H_1)}{f(x_i \mid H_0)}$$
The test terminates at the stopping time:
$$N = \inf \{n \ge 1 : \Lambda_n \ge A \text{ or } \Lambda_n \le B\}$$
where boundaries $A \approx \frac{1 - \beta}{\alpha}$ and $B \approx \frac{\beta}{1 - \alpha}$ provide exact type-I ($\alpha$) and type-II ($\beta$) error guarantees while minimizing the expected sample size $\mathbb{E}[N]$.

### 2.2 Conceptual Analogy to Candidate Probation
In LEBRE, candidate probation currently enforces a fixed-horizon observation rule ($T_{\text{prob}} = 15$ shadow observations). SPRT demonstrates the theoretical principle that a fixed horizon is mathematically sub-optimal: candidates with overwhelming evidence of utility should be promoted early ($\Lambda_n \ge A$), while candidates with clear futility should be discarded early ($\Lambda_n \le B$), reserving full probation only for ambiguous candidates.

### 2.3 Critical Limitations in LEBRE
Standard SPRT **cannot be directly deployed** on streaming candidate residuals for three fundamental reasons:
1. **Non-I.I.D. Observations:** Streaming innovation errors in LEBRE exhibit strong temporal autocorrelations and non-stationary distribution shifts.
2. **Transient Convergence Dynamics:** During early probation ($n \in [1, 5]$), candidate filter weights are undergoing rapid initial adaptation. Residual variance is non-constant, violating Wald's stationary density assumptions.
3. **Model Selection Coupling:** Candidate errors are conditioned on the live model's current weights, which are simultaneously updating online.

$$\mathbf{Classification: \ INSPIRATIONAL\_MATHEMATICAL\_ANALOGY \ (NOT\_DIRECTLY\_APPLICABLE)}$$

---

## 3. Anytime-Valid Inference & Confidence Sequences

### 3.1 Modern Sequential Inference (Howard et al., 2021; Ramdas et al., 2023)
When an online algorithm repeatedly checks evidence to decide whether to stop or promote, it performs **optional stopping**. In classical statistics, optional stopping inflates false positive rates to $100\%$ as $t \to \infty$.

Modern anytime-valid inference resolves this via **Confidence Sequences (CS)** and **e-processes / e-values**:
$$\mathbb{P}(\exists n \ge 1 : \mu \notin C_n) \le \alpha$$
A confidence sequence $C_n$ shrinks around the true parameter $\mu$ at rate $\sqrt{\frac{\ln \ln n}{n}}$ (law of the iterated logarithm) while maintaining valid coverage at every stopping time $\tau$.

### 3.2 Lessons for LEBRE Architectural Governance
1. **Repeated Peeking Prohibition:** Future probation mechanisms must not repeatedly compute conventional fixed-sample $t$-tests or $p$-values at every stream step and terminate whenever $p < 0.05$. This practice introduces uncontrolled selection bias.
2. **Deterministic Evidence Schedules:** If an empirical heuristic is used (e.g. a two-stage screen), it must be preregistered with fixed checkpoint intervals ($n \in \{5, 15\}$) and calibrated operating characteristics rather than ad-hoc continuous peeking.
3. **Statistical Precedent:** Classified as `STATISTICAL_DESIGN_PRECEDENT`.

---

## 4. Data-Selective Adaptive Filtering

### 4.1 Foundations (Diniz, 2018)
In data-selective adaptive filtering (e.g. Set-Membership Filtering, SM-NLMS; Diniz, 2018, *IEEE Trans. Signal Processing*, 66(16):4239–4252), parameter updates are skipped whenever the instantaneous error falls below an innovation threshold:
$$\text{If } |e(t)| \le \gamma \implies \mathbf{w}(t+1) = \mathbf{w}(t) \quad (\text{Zero FLOPs})$$
This achieves substantial compute reduction in steady-state when the filter is already well-tuned.

### 4.2 LEBRE Historical Precedent & Warning
In experimental stage `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01` and earlier multirate explorations (MR2), data-selective gating was evaluated on candidate probation. The experiment revealed that naive instantaneous error thresholding severely starved candidate learning:
- During early probation, low error often occurs by chance when input energy is temporarily quiescent, leading to missed updates;
- When a sudden delay change occurred, the candidate failed to adapt quickly enough to accumulate promotion utility.

$$\mathbf{Governing \ Lesson: \ DATA\_SELECTIVE\_UPDATE\_SKIPPING \ REQUIRES \ CUMULATIVE \ EVIDENCE, \ NOT \ INSTANTANEOUS \ GATING.}$$

---

## 5. Historical Context: LEBRE Exploratory Finding F-11

In early v0.1 exploratory notes, finding F-11 reported that under the original prototype architecture, many eventual candidate rejects were already separable by exposure $\sim 150$.

### Explicit Scope Governance:
- The historical value $150$ must **never** be cited as an active threshold for v0.2.
- In v0.1, candidates were evaluated continuously ($K=1$) over stream steps ($T_{\text{prob}} = 50\text{ steps}$).
- In v0.2 multirate execution, probation is governed strictly by **$T_{\text{prob}} = 15\text{ shadow observations}$** ($K_{\text{obs}} = 5 \implies 75\text{ stream steps}$).
- Any retrospective early-rejection analysis in this stage must evaluate exposures strictly within the active v0.2 horizon: $n \in [1, 15]$.
