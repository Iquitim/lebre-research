# EXP-0006 — Diagnosis & Component Status

## 1. Primary Diagnosis

**`TIER_ENTRY_STATISTICS_INSUFFICIENT`**

EXP-0006 decisively established that **evidence-rate reallocation is the true physical mechanism to eliminate structural acquisition latency**:
- When elevated probe rates are delivered to true candidates (J5 Oracle), $T_{\text{evidence}}$ collapses from **$129.28$ steps down to $14.92$ steps** (an 88.5% reduction), and full-support occupancy surges to **$95.00\%$** under the exact same 10,000 probe budget.
- In causal learners (J2, J4), evidence arrival velocity was successfully increased: median true inter-probe gap fell from **$16.6$ steps down to $2.4$ steps**, and $T_{\text{first\_probe}}$ fell from **$46.4$ to $11.8$ steps**.
- However, causal learners did not achieve J5's full collapse because **tier entry precision is only $2.8\% - 4.5\%$**.
- *Physical Cause*: Under small sample counts ($n=2$), transient noise correlations easily exceed $\theta_{\text{hint}} = 0.15$ during error surges. Consequently, over $96\%$ of candidates entering elevated tiers are spurious noise features, which absorb $>2,600$ elevated probes and dilute the probe concentration on true features.

---

## 2. Component Status Decisions

| Component | Status | Rationale |
| :--- | :---: | :--- |
| **`TWO_TIER_ALLOCATION`** | **REMOVE** | Without decay (J1), noise lock-in collapses occupancy to 13.7% and MSE to 0.71. |
| **`TIER_DECAY`** | **KEEP** | Essential to prevent noise lock-in; reduces false elevated probes by 42% and restores MSE to 0.01389. |
| **`THREE_TIER_ALLOCATION`** | **DEFER** | Adds parameter complexity without outperforming queue-based multi-rate scheduling; suffered displacement on seed 456. |
| **`QUEUE_MULTI_RATE`** | **KEEP** | **Winning causal allocation mechanism**. Achieved lowest MSE in repository (0.01355), lowest FLOPs (142.8), reduced $T_{\text{total}}$ by 32.7 steps, and had lowest starvation (1.0). |
| **`FORCED_COVERAGE`** | **KEEP** | Strictly preserves global background coverage; guaranteed zero candidate blind spots. |
| **`AGE_NORMALIZED_VICTIM`** | **KEEP** | Essential baseline from EXP-0004. Preserves 0.0% noise survival @ 50 and shields newly promoted features. |
| **`PROBE_BANK`** | **KEEP** | Enforces exact 10,000 probe budget with zero drift. |

---

## 3. Experiment Status Verdict

**`EXP_0006_STATUS = PARTIAL_GO`**

- Median true inter-probe gap $\le 20$: **PASS** (J4 achieved **2.4 steps**, J2 achieved **1.8 steps**, J5 achieved **1.0 step**).
- Regime-2 MSE $\le 0.03$: **PASS** (J4: **0.01355**, J2: **0.01389**, J0: **0.01383**).
- Mean Compute $\le 25\%$ Dense: **PASS** (All variants **$\approx 23.7\%$ Dense**, $< 143.5$ FLOPs/step).
- Total Probes = 10,000: **PASS** ($\Delta = 0$).
- No Catastrophic Starvation: **PASS** (J4 true starvations = 1.0, J0 = 1.8).
- $T_{\text{evidence}} \le 70$: **FAIL** for causal (J4: 133.08; J5 Oracle achieved 14.92).
- Full-Support Occupancy $\ge 75\%$: **FAIL** for causal (J0: 65.36%, J4: 61.76%; J5 Oracle achieved 95.00%).

### Milestone M1 Gate Decision
**`M1_CANDIDATE = FALSE`**  
(Full-support occupancy for causal variants remains below 75%, and $T_{\text{evidence}}$ remains above 70 steps due to low tier entry precision).

---

## 4. Next Step Taxonomy

**`NEXT = TIER_ENTRY_SIGNAL_DIAGNOSTIC`**

Now that EXP-0006 has proven that probe-rate allocation physically solves the structural latency bottleneck (J5 $T_{\text{evidence}} = 14.9$ steps, Occupancy = 95%), the exact remaining challenge is:
**How to causally distinguish true candidates from noise features on small sample sizes ($n \in [1, 3]$) so that elevated queue slots are occupied exclusively by true features.**
Investigating higher-order entry filters, residual variance reduction, or cross-sample consistency will enable causal rate allocators to unlock J5's full performance.
