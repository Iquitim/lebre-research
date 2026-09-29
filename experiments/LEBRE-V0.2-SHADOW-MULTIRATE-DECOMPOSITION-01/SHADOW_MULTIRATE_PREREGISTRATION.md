# Formal Preregistration: LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01

**Document Status:** FROZEN PRIOR TO CONFIRMATORY SIMULATION  
**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Preregistration Standard:** Level 1 Confirmatory Preregistration (Simmons et al., 2011; Nosek et al., 2018)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Primary Hypotheses & Statistical Decision Rules

All statistical tests are evaluated under independent random seeds as the inferential sampling unit ($N=30$, seeds `1711..1740`), eliminating pseudoreplication bias across the 14 benchmark tasks.

### 1.1 Hypothesis 1: Resource Gate ($H_{\text{RESOURCE}}$)
- **Claim:** The frozen multirate candidate $M_1$ recovers mean total online computational cost strictly beneath the primary ceiling:
  $$\bar{F}_{\text{total}, M1} \le 100.00\text{ FP FLOPs/step}$$
- **Scope:** Computed over all 6,000 timesteps across all 14 benchmark tasks ($84,000$ steps per seed, averaged across $N=30$ seeds). Includes live path, shadow path, router, sentinel, and all bookkeeping overheads.
- **Verdict Rule:** `PASS` if $\bar{F}_{\text{total}} \le 100.00$; `FAIL` otherwise.

### 1.2 Hypothesis 2: Predictive Non-Inferiority ($H_{\text{PREDICTIVE}}$)
- **Claim:** $M_1$ does not degrade aggregate predictive accuracy relative to continuous compacted baseline $M_0$ by more than the preregistered equivalence margin $\Delta_{\text{margin}} = +0.0100$ NMSE:
  $$H_0: \mu_{\Delta} \ge +0.0100 \quad \text{vs.} \quad H_1: \mu_{\Delta} < +0.0100$$
  where $\Delta_s = \bar{\text{NMSE}}_{s, M1} - \bar{\text{NMSE}}_{s, M0}$ for seed $s \in \{1711, \dots, 1740\}$.
- **Standard:** One-sided upper $95\%$ Student-$t$ confidence bound with $29$ degrees of freedom.
  $$\text{Upper } 95\% \text{ CI} = \bar{\Delta} + t_{0.95, 29} \cdot \frac{s_{\Delta}}{\sqrt{30}} < +0.0100$$
- **Verdict Rule:** `SUPPORTED` if Upper $95\%$ CI $< +0.0100$; `NOT_SUPPORTED` otherwise.

### 1.3 Hypothesis 3: Pure-Lag Preservation ($H_{\text{LAG}}$)
- **Claim:** Predictive performance on pure-lag tasks ($I_3, I_4, I_5, I_8$) is preserved within margin $+0.0150$ NMSE, and support recovery $F_1$ is maintained:
  $$\Delta \text{NMSE}_{\text{lag}} = \text{NMSE}_{M1} - \text{NMSE}_{M0} \le +0.0150$$
- **Verdict Rule:** `SUPPORTED` if all 4 pure-lag tasks satisfy margin; `NOT_SUPPORTED` otherwise.

### 1.4 Hypothesis 4: Continuous-Latent & Recurrent Continuity ($H_{\text{REC}}$)
- **Claim 4a:** Recurrent discovery remains functional on continuous-latent tasks ($I_6, I_7$) with successful promotion and non-zero dwell.
- **Claim 4b (Recurrent Continuity Invariant):** Decimating recurrent state propagation ($D_{9F}, K=5$) induces significantly worse NMSE degradation than decimating recurrent parameter learning ($D_{9L}, K=5$):
  $$\text{NMSE}(D_{9F}) - \text{NMSE}(D_{9L}) > 0$$
  confirming that recurrent hidden state continuity is structurally essential.

### 1.5 Hypothesis 5: Regime-Switching Preservation ($H_{\text{SWITCH}}$)
- **Claim:** On every primary directional regime-switching task ($I_{11}, I_{12}, I_{13}, I_{14}$ evaluated independently), recovery latency under $M_1$ does not exceed $M_0$ latency by more than $50$ stream steps:
  $$\Delta T_{\text{switch}, \tau} = T_{\text{recovery}, M1}(\tau) - T_{\text{recovery}, M0}(\tau) \le +50.0\text{ stream steps} \quad \forall \tau \in \{I_{11}, I_{12}, I_{13}, I_{14}\}$$
- **Verdict Rule:** Must pass independently on all 4 tasks without cross-task averaging.

### 1.6 Hypothesis 6: Hybrid Complementarity ($H_{\text{HYBRID}}$)
- **Claim:** On hybrid task $I_9$, co-adaptation produces positive conditional gains for both discrete delay and continuous recurrence ($G_{D|B+R} > 0$ and $G_{R|B+D} > 0$).

### 1.7 Hypothesis 7: Quiescent Retention ($H_{\text{QUIESCENCE}}$)
- **Claim:** Under extended silence ($I_7, I_8$), shadow execution duty drops while retaining latent memory, and post-quiescence reactivation latency is preserved within $+50$ steps.

---

## 2. Hard Governance Invariants & Scope Safeguards

```
+-----------------------------------------------------------------------------------------------+
| Governance Invariant               | Preregistered Value & Status                            |
+-----------------------------------------------------------------------------------------------+
| CANONICAL_VERSION                  | 0.1 (FROZEN_WITH_SCOPE_LIMITS)                          |
| M3_STATUS                          | UNOPENED                                                |
| NOVELTY_CLAIM_READY                | NO                                                      |
| CANONICAL_SRC_CHANGED              | NO (Strictly verified bitwise immutable)                |
| CANONICAL_TESTS_CHANGED            | NO (Strictly verified bitwise immutable)                |
| PARENT_GATE6_STATUS                | FAIL (Carried forward as legacy failure)                |
| FORMAL_GATE6_RETEST                | NOT_PERFORMED (frac_both changes are observational only)|
| EXACT_LAG_SUPPORT_STATUS           | PARTIAL (Carried forward; not optimized in this stage)  |
| PRIMARY_COMPARATORS                | M0 (Continuous compacted T3) vs. M1 (Selected Multirate)|
| CONFIRMATORY_SEEDS                 | 1711 .. 1740 (N = 30 independent seeds)                 |
+-----------------------------------------------------------------------------------------------+
```

---

## 3. Master Decision Rule

The overarching study outcome `MULTIRATE_SHADOW_GOVERNANCE_SUPPORTED = YES` shall be declared **if and only if ALL 12 conditions are satisfied**:
1. $\bar{F}_{\text{total}} \le 100.00\text{ FP FLOPs/step}$
2. Upper $95\%$ CI of aggregate $\Delta \text{NMSE} < +0.0100$
3. Pure-lag preservation $\Delta \text{NMSE} \le +0.0150$
4. Continuous-latent discovery functional on $I_6, I_7$
5. All switching tasks satisfy $+50$-step tolerance independently
6. $I_9$ hybrid complementarity confirmed
7. Quiescence retention preserved on $I_7, I_8$
8. Zero access to privileged stream information (causal purity)
9. All router, sentinel, and bookkeeping compute counted
10. Zero numerical instability (no NaN, Inf, or divergence)
11. Memory impact fully accounted under Phase A standards
12. Canonical `src/` and `tests/` completely unchanged.

If any mandatory criterion fails, the outcome is classified under the frozen failure taxonomy:
`COMPUTE_RECOVERED_BEHAVIOR_DEGRADED`, `BEHAVIOR_PRESERVED_COMPUTE_NOT_RECOVERED`, `RECURRENT_STATE_CONTINUITY_CONFLICT`, or `TEMPORAL_ROUTER_MISCLASSIFICATION`.
