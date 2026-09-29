# Protocol: Component Sensitivity Screening on DEV

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Cohort:** DEV Seeds `1701..1710` ($N=10$) across 14 Benchmark Streams  

---

## 1. Single-Difference Sensitivity Invariant

To determine which operations require high execution frequency versus which tolerate slow adaptation, we evaluate isolated single-component downsampling interventions against continuous baseline $D_0$:

```
+---------------+------------------------+-------------------------------------------------------------------------------+
| Condition ID  | Target Operation Scope | Operational Cadence Allocation                                                |
+---------------+------------------------+-------------------------------------------------------------------------------+
| D0            | None (Continuous Ref)  | All components continuous (K_probe=1, K_cand=1, K_rec_fwd=1, K_rec_lrn=1, K_arb=1)|
| D7            | Stage 7 (Corr Sensing) | K_probe = 5; all other components continuous (K=1)                             |
| D8            | Stage 8 (Candidates)   | K_cand_obs = 5, K_cand_learn = 5; all other components continuous (K=1)        |
| D9F           | Stage 9A/9B (Rec Prop) | K_rec_forward = 5; all other components continuous (K=1)                       |
| D9L           | Stage 9C/9D/9E (Rec Lrn| K_rec_learn = 5; Recurrent state propagation CONTINUOUS (K_rec_forward = 1)   |
| D10           | Stage 10 (Arbitration) | K_arbitration = 5; all other components continuous (K=1)                       |
+---------------+------------------------+-------------------------------------------------------------------------------+
```

---

## 2. Sensitivity Evaluation Metrics

For each condition, we compute across $N_{\text{DEV}} = 10$ seeds:
1. **Compute Saving ($\Delta \text{FP}$):** $\bar{F}_{\text{total}}(D_0) - \bar{F}_{\text{total}}(D_x)$
2. **Aggregate Predictive Delta ($\Delta \text{NMSE}$):** $\bar{\text{NMSE}}(D_x) - \bar{\text{NMSE}}(D_0)$
3. **Pure-Lag Delta ($\Delta \text{NMSE}_{\text{lag}}$):** Mean delta over $I_3, I_4, I_5, I_8$
4. **Continuous-Latent Delta ($\Delta \text{NMSE}_{\text{rec}}$):** Mean delta over $I_6, I_7$
5. **Hybrid Delta ($\Delta \text{NMSE}_{\text{hyb}}$):** Mean delta over $I_9, I_{13}, I_{14}$
6. **Switching Latency Delta ($\Delta T_{\text{switch}}$):** Mean recovery delay difference over $I_{11}$–$I_{14}$
7. **Lag Discovery Delay ($T_{\text{lag\_disc}}$):** Timestep of first active delay promotion on $I_3$
8. **Recurrent Discovery Delay ($T_{\text{rec\_disc}}$):** Timestep of first active recurrent promotion on $I_6$
9. **Support Recovery $F_1$:** Precision and recall on $I_3$ and $I_4$
10. **Redundancy Mitigation ($I_{10} \text{ frac\_both}$):** Fraction of steady-state dual active steps
11. **Quiescent Retention:** Reactivation latency on $I_7$ and $I_8$
12. **First Divergence Step:** First timestep where structural state diverges from $D_0$.

---

## 3. Behavioral Classification Taxonomy

Following sensitivity screening, each component is formally classified:
- `CADENCE_INSENSITIVE_WITHIN_TESTED_RANGE`: $\Delta \text{NMSE} \le +0.0020$ and latency delta $\le +10$ steps at $K=5$.
- `SLOW_TIMESCALE_TOLERANT`: Tolerates $K \ge 5$ with minor, acceptable delay within preregistered margins.
- `FAST_TIMESCALE_REQUIRED`: Significant performance collapse ($\Delta \text{NMSE} > +0.0100$ or latency $> +50$ steps) if downsampled.
- `STATE_CONTINUITY_REQUIRED`: Asymmetric degradation between state propagation and parameter learning (confirms path-dependence).
- `EVENT_SELECTIVE_CANDIDATE`: Candidate for innovation-gated execution rather than periodic downsampling.
- `UNRESOLVED`: Boundary ambiguous; requires refinement on rate ladder.

---

## 4. Rate Ladder Exploration ($K \in \{1, 2, 5, 10\}$)

Following $K=5$ screening, rates for candidates are refined only within the discrete ladder $K \in \{1, 2, 5, 10\}$ to bracket the exact point of preservation failure.
