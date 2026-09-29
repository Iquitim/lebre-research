# Inferential Unit Audit: Independent Seeds vs Pooled Observations

**LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01**

---

## 1. Problem Statement: Pseudoreplication in Inferential Testing

In `RESOURCE_COMPACTION_FINAL_REPORT.md` Section 3 and `RESOURCE_COMPACTION_EQUIVALENCE_REPORT.md`, the statistical equivalence test between $C_0$ and $C_1$ was reported with sample size:
$$N = 420 \text{ paired simulations}$$
arising from $30 \text{ seeds} \times 14 \text{ benchmark tasks} = 420 \text{ observations}$.

As an independent skeptical reviewer, this audit must evaluate whether pooling these 420 pairs constitutes **pseudoreplication** under experimental design standards (Hurlbert, 1984; Lakens, 2017).

---

## 2. Theoretical Analysis

### 2.1 The Sampling Unit in Online Learning Benchmarks
In benchmark evaluation of online adaptive algorithms:
1. An experimental run is defined by drawing an independent pseudo-random seed $s \sim \text{Uniform}(\mathbb{N})$, which initializes the data generator, noise sequences, regime switch timings, and parameter priors.
2. Evaluating 14 different benchmark tasks ($I_1$ to $I_{14}$) under the **same** seed $s$ yields 14 performance measurements that share the identical underlying random number generator state.
3. Therefore, observations within seed $s$ are **mutually dependent**. Treating them as 420 independent degrees of freedom inflates the effective sample size by a factor of 14, artificially compressing standard errors by $\sqrt{14} \approx 3.74$.

### 2.2 Established LEBRE Governance Standard
LEBRE Experimental Governance (`AGENTS.md`, `LEBRE_V0_2_SEAL_AUDIT_PROTOCOL.md`) defines the **INDEPENDENT INFERENTIAL UNIT** strictly as:
$$\text{Inferential Unit} \equiv \text{SEED} \quad (N = 30)$$
All confirmatory hypothesis testing must be conducted at the seed level by aggregating task performances per seed prior to inferential testing.

---

## 3. Seed-Level Recomputation Methodology

For each independent seed $s \in \{1411, 1412, \dots, 1440\}$ ($N = 30$):
1. Compute the aggregate mean NMSE across all 14 benchmark tasks for baseline $C_0$:
   $$\overline{\text{NMSE}}_{C0, s} = \frac{1}{14} \sum_{k=1}^{14} \text{NMSE}_{C0}(s, I_k)$$
2. Compute the aggregate mean NMSE across all 14 benchmark tasks for compacted candidate $C_1$:
   $$\overline{\text{NMSE}}_{C1, s} = \frac{1}{14} \sum_{k=1}^{14} \text{NMSE}_{C1}(s, I_k)$$
3. Compute the paired aggregate difference:
   $$d_s = \overline{\text{NMSE}}_{C1, s} - \overline{\text{NMSE}}_{C0, s}$$
4. Evaluate the Two One-Sided Tests (TOST) against the preregistered equivalence margin $\Delta_{\text{eq}} = \pm 0.010$ (1% NMSE) with $df = N - 1 = 29$:
   $$t_1 = \frac{\bar{d} - (-\Delta_{\text{eq}})}{\text{SE}_d}, \quad t_2 = \frac{\bar{d} - (+\Delta_{\text{eq}})}{\text{SE}_d}$$
   $$p_{\text{TOST}} = \max(p(t_1), p(t_2))$$

---

## 4. Empirical Recomputation Results

```
+-----------------------------------------------------------------------------+
| Inferential Statistic              | Pooled Report (N=420) | Certified Seed (N=30) |
+-----------------------------------------------------------------------------+
| Sample Size (Degrees of Freedom)   | N = 420 (df = 419)   | N = 30 (df = 29)     |
| Mean C0 Aggregate NMSE             | 0.328196             | 0.328196             |
| Mean C1 Aggregate NMSE             | 0.328205             | 0.328205             |
| Paired Mean Delta (d_bar)          | +0.00000862          | +0.00000862          |
| Paired Standard Deviation (s_d)    | 0.00015701           | 0.00004159           |
| Paired Standard Error (SE_d)       | 0.00000766           | 0.00000759           |
| 90% Two-Sided Confidence Interval  | [-0.0000040, +0.0000212] | [-0.0000043, +0.0000215] |
| Equivalence Margin (Delta_eq)      | +/- 0.0100           | +/- 0.0100           |
| TOST t_1 Statistic (Lower Bound)   | t = 1306.4           | t = 1318.2           |
| TOST t_2 Statistic (Upper Bound)   | t = -1304.2          | t = -1315.9          |
| TOST p-value                       | p < 1e-100           | p = 4.10e-71         |
| Behavioral Equivalence Certified   | YES                  | YES                  |
+-----------------------------------------------------------------------------+
```

### Forensic Observations:
1. **Variance Aggregation Effect:** When averaging across the 14 tasks per seed, cross-task variance cancels out, reducing the standard deviation of seed-level differences from $1.57 \times 10^{-4}$ to $4.16 \times 10^{-5}$.
2. **Equivalent Standard Error:** Because the standard deviation decreases in proportion to the smaller sample size, the standard error at the seed level ($\text{SE}_d = 7.59 \times 10^{-6}$) is virtually identical to the pooled standard error ($\text{SE}_d = 7.66 \times 10^{-6}$).
3. **Decisive Rejection of Non-Equivalence:** The certified TOST $p$-value at $N=30$ is:
   $$p_{\text{TOST}} = 4.10 \times 10^{-71} \ll 0.05$$
   The 90% confidence interval for aggregate performance difference is $[-0.0000043, +0.0000215]$, which is tightly nested inside the $\pm 0.0100$ equivalence bounds by over two orders of magnitude.

---

## 5. Corrigendum & Audit Verdict

1. **Reporting Overstatement Acknowledged:** The parent report's claim of $N=420$ paired simulations represents a formal reporting error (pseudoreplication across tasks).
2. **Scientific Invariance:** Recomputing the test under the rigorous, certified independent sampling unit ($N=30$ seeds) **fully preserves and certifies the substantive scientific conclusion**.
3. **Certified Status:** The equivalence between $C_0$ and $C_1$ is certified under the proper independent inferential unit ($N=30$).
