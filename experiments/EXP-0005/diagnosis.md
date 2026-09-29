# EXP-0005 — Diagnosis & Component Status

## 1. Primary Diagnosis

**`EVIDENCE_STOPPING_NOT_PRIMARY`**

The hypothesis that $T_{\text{evidence}} \approx 129$ steps was caused by an overly conservative sample requirement ($N_{\min}=8$) was directly refuted:
1. Naively reducing $N$ to 3 (H1) or relying on signal strength alone (H2) caused catastrophic noise-driven failure (MSE $\ge 2.2$, $\sim 40$ displacements, occupancy $< 20\%$).
2. Requiring directional consistency (H3) and sequential Wald bounds (H4) protected against noise, but $T_{\text{evidence}}$ remained between $158$ and $194$ steps.
3. Crucially, **H5 (Oracle Evidence-Stopping Diagnostic)**, with 100% early promotion precision on true candidates, still had $T_{\text{evidence}} = 156.76$ steps.

### Physical Mechanism
Under the Explore/Confirm policy with 40% coverage across 90 inactive candidates ($q \approx 5 \implies 2$ coverage probes/step):
$$\tau_{\text{scan}} = \frac{90 \text{ candidates}}{2 \text{ probes/step}} = 45 \text{ steps per observation}$$
Accumulating even 3 observations takes $3 \times 45 = 135$ steps. Therefore, evidence accumulation latency is bound by **candidate probe arrival rate and probe concentration**, not by sample count stopping rules.

---

## 2. Component Status

| Component | Status | Rationale |
| :--- | :---: | :--- |
| **LOWER_FIXED_N** | **REMOVE** | Naively lowering $N$ to 3 causes 3,430 false promotions, 39.2 displacements, and explodes MSE to 3.27. |
| **STRENGTH_ADAPTIVE_EVIDENCE** | **REMOVE** | Signal magnitude alone fails to distinguish true candidates from transient noise spikes; MSE explodes to 2.24. |
| **CONSISTENCY_ADAPTIVE_EVIDENCE** | **DEFER** | Sign consistency is essential (cuts false promotions by 86%), but cannot overcome low probe arrival rates. |
| **EARLY_STOPPING** | **DEFER** | H4's Wald bound achieves best overall MSE (0.01334) with zero seed collapses, but latency gains are capped by probe arrival rate. |
| **AGE_NORMALIZED_VICTIM** | **KEEP** | Essential baseline from EXP-0004. Preserves 0.0% noise survival @ 50 and shields adapting true features. |
| **EXPLORE_CONFIRM** | **KEEP** | Provides structured confirmation, but candidate entry queue requires higher probe concentration. |
| **FORCED_COVERAGE** | **KEEP** | Strictly required to prevent candidate starvation ($T_{\text{wait}} \approx 46$ steps). |
| **PROBE_BANK** | **KEEP** | Enforces exact 10,000 probe budget with zero drift. |

---

## 3. Experiment Status Verdict

**`EXP_0005_STATUS = PARTIAL_GO`** (NO_GO for early stopping as a standalone latency solution)

- $T_{\text{evidence}} \le 70$ steps: **FAIL** (Best causal: 129.28 in H0, 158.12 in H3)
- Full-Support Occupancy $\ge 75\%$: **FAIL** (Best causal: 65.36% in H0, 54.50% in H4)
- Regime-2 MSE $\le 0.03$: **PASS** (H0: 0.01383, H4: 0.01334)
- Mean Compute $\le 25\%$ Dense: **PASS** (All variants $\approx 20.5\%$ Dense)
- Total Probes = 10,000: **PASS** ($\Delta = 0$)

### Milestone M1 Gate
**`M1_CANDIDATE = FALSE`**  
(Occupancy remains below 75% and $T_{\text{evidence}}$ remains above 70 steps).

---

## 4. Next Step Taxonomy

**`NEXT = EVIDENCE_RATE_DIAGNOSTIC`**

Having proven that stopping rules alone cannot compress evidence latency due to the $\sim 45$-step round-robin scan cycle across 90 inactive candidates:
The next empirical investigation must focus on **accelerating the evidence acquisition rate for promising candidates** (e.g. dynamic coverage reallocation, tiered multi-resolution candidate pooling, or adaptive confirmation probe scaling) under the matched 10,000 budget.
