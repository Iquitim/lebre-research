# Literature Note: Theoretical Foundations of Multirate and Data-Selective Shadow Governance

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (v0.2 Experimental Stream)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Status:** PREREGISTERED THEORETICAL BASIS  

---

## 1. Executive Summary & Epistemic Taxonomies

The whole-shadow duty-cycling experiment (`LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`) proved that monolithic downsampling of the entire shadow block fails:
- Periodic scheduling ($S_2, K=5$) cut compute ($89.5\text{ FP}$) but severely degraded predictive non-inferiority ($\Delta \text{NMSE} = +0.0567$) and regime-switching latency ($+763\text{ steps}$).
- Event-triggered scheduling ($S_3$) failed the compute gate ($110.07\text{ FP}$) due to persistent false alarms on static nonlinear tasks ($I_2$) where large approximation error was mistaken for temporal structural change.

To resolve these failure mechanisms, this study decomposes the shadow subsystem into its atomic constituent operations:
$$\text{Sensing} \quad \longleftrightarrow \quad \text{Observation} \quad \longleftrightarrow \quad \text{State Propagation} \quad \longleftrightarrow \quad \text{Parameter Learning} \quad \longleftrightarrow \quad \text{Arbitration}$$

Every literature-derived mechanism utilized in this study is explicitly classified under one of three epistemic categories:
1. `[ESTABLISHED_EXTERNAL_MECHANISM]`: Formally proven mathematical or signal-processing property in the cited literature within its specified domain.
2. `[CONCEPTUAL_ANALOGY]`: Qualitative algorithmic precedent whose mathematical assumptions do not strictly hold in LEBRE's non-stationary, non-convex setting.
3. `[LEBRE_SPECIFIC_HYPOTHESIS]`: An empirical hypothesis unique to the LEBRE runtime architecture that requires direct confirmatory evaluation.

---

## 2. Review of Foundational Literature

### 2.1 Partial-Update Adaptive Filtering
- **Citation:** Godavarti, M., & Hero, A. O. III. (2005). *Partial Update LMS Algorithms*. IEEE Transactions on Signal Processing, 53(7), 2382–2399. DOI: [10.1109/TSP.2005.849167](https://doi.org/10.1109/TSP.2005.849167).
- **Core Findings:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: In linear adaptive filtering, updating only a subset of coefficients at each iteration (either via periodic block decimation or sequential coordinate selection) reduces per-iteration arithmetic operations from $\mathcal{O}(N)$ to $\mathcal{O}(M)$ ($M < N$).
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: Arbitrary coefficient decimation alters the effective convergence rate, steady-state excess mean-squared error (EMSE), and stability bounds. The stability margin is compressed, requiring smaller step sizes or strict orthogonality between update subsets.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: In LEBRE, candidate parameter adaptation and correlation probing can be decimated without destabilizing live predictions because candidates operate in counterfactual shadow isolation. However, candidate convergence latency will degrade if decimation is too severe ($K > 5$).

### 2.2 Data-Selective Adaptive Filtering
- **Citation:** Diniz, P. S. R. (2018). *On Data-Selective Adaptive Filtering*. IEEE Transactions on Signal Processing, 66(16), 4239–4252. DOI: [10.1109/TSP.2018.2847657](https://doi.org/10.1109/TSP.2018.2847657).
- **Core Findings:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: In set-membership and data-selective filtering, updates are skipped when the innovation error $|e(t)|$ falls within a predefined error bound $\gamma$. This reduces average updates by $70\%–90\%$ in stationary and sparse-innovation regimes while preserving tracking capability during sudden perturbations.
  - `[CONCEPTUAL_ANALOGY]`: Skipping redundant shadow parameter updates when innovation is negligible can conserve computational resources without compromising structural discovery.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: A data-selective criterion based on pre-filter residual magnitude and candidate error reduction can eliminate idle parameter updates in the shadow candidate pool during stationary tracking.

### 2.3 Two-Timescale Stochastic Approximation
- **Citation:** Borkar, V. S. (1997). *Stochastic Approximation with Two Time Scales*. Systems & Control Letters, 29(5), 291–294. DOI: [10.1016/S0167-6911(97)90015-3](https://doi.org/10.1016/S0167-6911(97)90015-3).
- **Core Findings:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: Coupled recursions $\theta_{n+1} = \theta_n + a_n f(\theta_n, \phi_n)$ and $\phi_{n+1} = \phi_n + b_n g(\theta_n, \phi_n)$ converge almost surely to their respective equilibria if step-size schedules satisfy $\sum a_n = \infty, \sum b_n = \infty$ and $a_n / b_n \to 0$, effectively decoupling fast dynamics from slow dynamics.
  - `[CONCEPTUAL_ANALOGY]`: Structural sensing (correlation grid, fast timescales) can be decoupled from structural arbitration and capacity allocation (slow timescales) without theoretical divergence.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: Because recurrent hidden states are path-dependent, recurrent state propagation must operate at a faster rate than recurrent parameter weight updates ($K_{\text{rec\_prop}} < K_{\text{rec\_learn}}$). Decimating parameter learning is well-tolerated, whereas decimating state propagation destroys the latent dynamical trajectory.

### 2.4 Model Structure Validation via Residual Correlation
- **Citation:** Douma, S. G., Bombois, X., & Van den Hof, P. M. J. (2008). *Validity of the standard cross-correlation test for model structure validation*. Automatica, 44(5), 1285–1294. DOI: [10.1016/j.automatica.2007.09.027](https://doi.org/10.1016/j.automatica.2007.09.027).
- **Core Findings:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: The classical residual-input cross-correlation test ($R_{\varepsilon u}(\tau) = 0$) and residual autocorrelation test ($R_{\varepsilon \varepsilon}(\tau) = 0$) rely on linear system assumptions and undermodelling bounds. In the presence of undermodelling (e.g. unmodelled nonlinearities or feedback), these tests can either fail to detect structural inadequacy or spuriously declare correlation.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: A large prediction residual alone ($e^2$) is NOT evidence of missing temporal memory. On Task $I_2$ (static nonlinear control), large residual error arises from instantaneous function approximation limits. Residual temporal correlation $R_{e e}(1)$ and lagged input-residual correlation $R_{x e}(\tau)$ must be monitored before concluding that temporal structure is needed.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: Residual correlation tests may authorize temporal shadow exploration, but they must NEVER directly promote a lag or recurrent unit. Direct promotion must remain governed by symmetric counterfactual arbitration.

### 2.5 Event-Triggered Online Learning
- **Citation:** Umlauft, J., & Hirche, S. (2020). *Feedback Linearization Based on Gaussian Processes With Event-Triggered Online Learning*. IEEE Transactions on Automatic Control, 65(10), 4154–4169. DOI: [10.1109/TAC.2019.2958840](https://doi.org/10.1109/TAC.2019.2958840).
- **Core Findings:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: Online Gaussian process updates can be gated by an information-theoretic criterion (predictive variance exceedance), guaranteeing tracking error bounds while reducing kernel maintenance compute by orders of magnitude.
  - `[CONCEPTUAL_ANALOGY]`: An expensive online learning update (e.g., RTRL recurrent parameter learning, counterfactual loss grid) can be conditionally gated by cheaper $\mathcal{O}(1)$ statistics.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: The cost of evaluating the triggering condition itself ($\mathcal{O}(1)$ operations) must be strictly counted against the compute budget. Any router that incurs high overhead defeats the purpose of duty-cycling.

### 2.6 Sequential Inspection Schemes (Page-Hinkley Baseline)
- **Citation:** Page, E. S. (1954). *Continuous Inspection Schemes*. Biometrika, 41(1/2), 100–115.
- **Role in LEBRE:**
  - `[ESTABLISHED_EXTERNAL_MECHANISM]`: The cumulative sum (CUSUM) / Page-Hinkley test detects abrupt mean-shifts in a scalar process with minimal detection delay.
  - `[CONCEPTUAL_ANALOGY]`: Used in study $S_3$ as an event-triggered sentinel on the squared loss $\ell_{\text{live}}$.
  - `[LEBRE_SPECIFIC_HYPOTHESIS]`: Page-Hinkley on raw loss $\ell_{\text{live}}$ is inherently flawed for temporal structure routing because it cannot distinguish between high static nonlinear approximation error ($I_2$) and genuine temporal regime shifts ($I_{11}$–$I_{14}$). It is retained strictly as an audited baseline comparator, not as the primary solution.

---

## 3. Synthesis of Design Implications for Multirate Architecture

1. **Decouple Fast Sensing from Slow Adaptation:**  
   $K_{\text{probe}} \in \{1, 2\}$, $K_{\text{cand\_learn}} \in \{2, 5\}$, $K_{\text{rec\_learn}} \in \{5, 10\}$.
2. **Preserve Recurrent State Continuity:**  
   Never decimate the recurrent forward pass ($K_{\text{rec\_prop}} = 1$) even when recurrent parameter learning is decimated ($K_{\text{rec\_learn}} \ge 5$).
3. **Guard Negative Controls ($I_2$):**  
   Router sentinels must incorporate temporal correlation indicators ($e_t \cdot e_{t-1}$ or $e_t \cdot x_{t-k}$), preventing static error from waking temporal shadow discovery.
4. **Count All Overheads:**  
   Router compute and memory are non-zero and must be audited down to individual FLOPs, integer casts, and persistent registers.
