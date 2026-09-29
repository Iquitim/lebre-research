# LEBRE-DIAG-01: Eviction Response Latency & Retention Regret Analysis

**Protocol:** LEBRE-DIAG-01  
**Target:** Retention & Eviction Controller ($	heta_{\text{ret}} = 0.02, \theta_{\text{obs}} = 0.80, N_{\text{pat}} = 30, \tau_{\text{mature}} = 100$)  
**Date:** 2026-09-19  

---

## 1. Eviction Latency Mechanics

When a false promotion occurs, the candidate immediately increases prediction error. However, under LEBRE v0.1 architecture rules, a promoted state cannot be evicted until:
1. It reaches full maturity age $\tau_{\text{mature}} = 100$ steps (or 120 in M2 legacy controller).
2. Its utility drops below $\theta_{\text{ret}} = 0.02$.
3. Its obsolescence counter accumulates to $\theta_{\text{obs}} = 0.80$.
4. It sustains both conditions across $N_{\text{pat}} = 30$ consecutive patience steps.

As a result, a harmful state is guaranteed to remain active for at least $\approx 80$ to $160$ steps, continuously degrading active streaming predictions.

| Task | Mean Lifespan of Harmful States | Mean Eviction Latency ($T_{\text{evict\_response}}$) | Mean Regret per Seed ($R_{\text{harm}}$) | Oracle Immediate Eviction Recovery (%) |
| :--- | :---: | :---: | :---: | :---: |
| **A2** (Single Delay) | 91.6 steps | 81.2 steps | 148.6 | **18.6%** |
| **A3** (Multiple Delays) | 95.5 steps | 83.4 steps | 112.4 | **12.7%** |
| **A4** (Long Delay) | 84.6 steps | 76.1 steps | 176.8 | **23.4%** |
| **A5** (Set/Reset) | 455.3 steps | 18.2 steps | 14.2 | N/A (Recurrence Beneficial) |
| **A7** (Poisson Gap) | 222.5 steps | 24.6 steps | 18.5 | N/A (Recurrence Beneficial) |
| **A8** (Tri-Regime) | 103.9 steps | 68.2 steps | 42.1 | 5.2% |

---

## 2. Oracle Eviction Upper Bound (`LEBRE_ORACLE_HARM_STOP`)

The diagnostic variant `LEBRE_ORACLE_HARM_STOP` immediately evicts any active state as soon as it exhibits 20 consecutive steps of counterfactual excess loss.
- On **A2**, Oracle Harm Stop reduces NMSE from **1.1324** to **1.1292**, recovering **18.6%** of the net recurrent harm.
- On **A3**, Oracle Harm Stop reduces NMSE from **1.1279** to **1.1264**, recovering **12.7%** of the net recurrent harm.
- On **A4**, Oracle Harm Stop reduces NMSE from **1.1350** to **1.1302**, recovering **23.4%** of the net recurrent harm.

### Diagnostic Conclusion:
Delayed eviction accounts for roughly **15% to 23%** of the net regret incurred by recurrent units. However, because over 80% of promoted units are defective from inception, immediate eviction cannot prevent the initial shock. More importantly, even if all recurrent units are completely eliminated (`LEBRE_NO_REC_BIRTH`), the system still incurs an NMSE of $pprox 1.115$ on A2–A4. Thus, sluggish eviction is a contributing secondary factor, not the primary bottleneck.
