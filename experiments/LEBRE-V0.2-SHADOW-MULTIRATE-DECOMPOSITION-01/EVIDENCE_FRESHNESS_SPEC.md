# Specification: Evidence Freshness & Counterfactual Synchronization

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Freshness Metadata Standard

Every evidence variable, candidate prediction, and loss accumulator in the shadow subsystem maintains two mandatory integer metadata tags:
1. `last_update_step`: The absolute stream timestep $t$ on which the variable was most recently evaluated.
2. `age_steps`: The elapsed stream steps since the last update:
   $$\text{age\_steps}(t) = t - \text{last\_update\_step}$$

---

## 2. Binding Counterfactual Synchronization Rule

The $T_3$ Capacity Arbitrator evaluates the four counterfactual losses:
$$\ell_B(t) = (y_t - P_{\text{BASE}})^2, \quad \ell_{BD}(t) = (y_t - P_{\text{BASE\_D}})^2, \quad \ell_{BR}(t) = (y_t - P_{\text{BASE\_R}})^2, \quad \ell_{BDR}(t) = (y_t - P_{\text{BASE\_D\_R}})^2$$

Where:
- $P_{\text{BASE}} = \hat{y}_{\text{base}}(t)$ (always fresh, $t$)
- $P_{\text{BASE\_D}} = \hat{y}_{\text{base}}(t) + \hat{y}_{\text{lag\_eval}}(t)$
- $P_{\text{BASE\_R}} = \hat{y}_{\text{base}}(t) + \hat{y}_{\text{rec\_eval}}(t)$
- $P_{\text{BASE\_D\_R}} = \hat{y}_{\text{base}}(t) + \hat{y}_{\text{lag\_eval}}(t) + \hat{y}_{\text{rec\_eval}}(t)$

### 2.1 The Freshness Precondition
Let $\tau_{\text{lag}} = t - t_{\text{last\_lag\_eval}}$ and $\tau_{\text{rec}} = t - t_{\text{last\_rec\_eval}}$.
Arbitration loss construction (`10A`) and gain filtering (`10C`) may execute **if and only if both candidate signals meet the freshness ceiling**:
$$\tau_{\text{lag}} \le \tau_{\text{tol}} \quad \text{AND} \quad \tau_{\text{rec}} \le \tau_{\text{tol}}$$
where the preregistered maximum allowable staleness is:
$$\mathbf{\tau_{\text{tol}} = 2 \text{ stream steps}}$$

### 2.2 Rejection Behavior (`NO_ARBITRATION_UPDATE`)
If either $\tau_{\text{lag}} > \tau_{\text{tol}}$ or $\tau_{\text{rec}} > \tau_{\text{tol}}$:
1. Operations `10A`, `10B`, and `10C` are aborted.
2. Gain EMA filters are frozen (`NO_NEW_EVIDENCE`).
3. Structural state is held (`HOLD_STATE`).
4. A diagnostic counter `stale_arbitration_skips` is incremented.

**Violation Penalty:** Any implementation that evaluates conditional gains by mixing a fresh live residual with a stale candidate prediction older than $\tau_{\text{tol}}$ is invalid.
