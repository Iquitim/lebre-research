# FUTURE_IDEAS.md (Unimplemented Architectural Research Notes)

**Origin**: PRA-01 Adversarial Literature Review  
**Status**: Recorded for future milestones (M3+); **STRICTLY UNIMPLEMENTED IN FROZEN M2 CORE**.  
**Governance**: In compliance with Section 107, no modifications to Track B are permitted during PRA-01.

---

## 1. Multi-State Controllability/Observability Orthogonalization (for M3)
- **Inspiration**: LAST (Padhy et al. 2025) and AIRE-Prune (Padhy et al. 2026).
- **Concept**: When state capacity is expanded to $K > 1$ in Milestone M3, parallel states risk collapsing onto identical decay rates ($\lambda_1 \approx \lambda_2$) or highly correlated trajectories.
- **Idea**: Compute cross-state Gramian inner products $W_{\text{cross}} = \sum_t h_{1, t} h_{2, t}$ or use modal truncation to penalize co-linear states, forcing multiple states to specialize into distinct frequency bands or timescale octaves (e.g. short-term vs long-term).

## 2. Noise-Adaptive Birth Thresholds via Bias-Variance Estimation
- **Inspiration**: Network Significance formula in DEVDAN / MUSE-RNN (Pratama et al. 2019).
- **Concept**: Currently, Track B's error birth threshold $\theta_{\text{birth}}$ is parameterized relative to normalized residual scale.
- **Idea**: Maintain an online running estimate of observation noise variance $\hat{\sigma}_\epsilon^2$. Trigger state birth only when residual error significantly exceeds $\hat{\sigma}_\epsilon^2$ with statistical confidence ($p < 0.01$), preventing spurious birth in high-noise environments.

## 3. Warmup Learning Rates to Mitigate the "Newborn Bottleneck"
- **Inspiration**: Lillo & Cheney (2026), *On the Stability of Growth in Structural Plasticity*.
- **Concept**: Newborn states suffer from being "forward-active but backward-starved", requiring many steps to develop effective weight scale.
- **Idea**: During the 20-step probation window, provide nascent state parameters ($\eta_\lambda, \eta_s, \eta_u$) with a decaying warmup learning rate schedule ($\eta_{\text{prob}} = 2 \times \eta_{\text{mature}}$) to accelerate parameter convergence before live deployment.

## 4. Explainability-Driven / Gradient-Variance Probe Prioritization
- **Inspiration**: Active Feature Acquisition (Guney et al. 2025; Norcliffe et al. 2025).
- **Concept**: Circular round-robin candidate scanning allocates equal probe budgets to all unobserved features.
- **Idea**: Use coarse second-order statistics or sparse gradient variance hints to non-uniformly allocate probe frequencies, concentrating exploration on high-information candidate subsets.
