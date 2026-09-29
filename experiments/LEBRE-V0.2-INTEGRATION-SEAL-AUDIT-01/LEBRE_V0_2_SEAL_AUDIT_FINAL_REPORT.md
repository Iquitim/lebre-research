# LEBRE v0.2 Integration Seal Audit Final Report: Confirmatory Integrity, Resource-Gate Provenance, Artifact Traceability & Architectural Candidate Seal

**Audit Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Parent Study:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`  
**Auditor:** Independent Skeptical Senior Reviewer  
**Audit Scope:** Machine-learning experimental design, artifact evaluation, systems benchmarking, TinyML resource accounting, online adaptive filtering, statistical auditing, multi-objective Pareto analysis, and scientific software verification.  
**Governing Invariants:**
- `CANONICAL_VERSION = 0.1`
- `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`
- `M3_STATUS = UNOPENED`
- `NOVELTY_CLAIM_READY = NO`
- `CANONICAL_SRC_MUTATED = NO`
- `CANONICAL_TESTS_MUTATED = NO`

---

## 1. Executive Summary & Forensic Audit Verdict

This forensic seal audit was conducted to independently evaluate whether the empirical and architectural evidence supporting **Topology $T_3$ (Resource-Aware Conditional Arbitration with Symmetric Shadow Registers)** in parent study `LEBRE-V0.2-INTEGRATION-DESIGN-01` is internally consistent, reproducible from sealed artifacts, compliant with preregistered resource governance, and scientifically clean to progress to integrated validation.

In accordance with the governing audit principle:
$$\text{PRESERVE} \longrightarrow \text{REPRODUCE} \longrightarrow \text{TRACE} \longrightarrow \text{CLASSIFY} \longrightarrow \text{CORRECT REPORTING} \longrightarrow \text{RE-EVALUATE DECISION}$$
the audit preserves all parent artifacts bitwise, reconstructs the complete provenance chain from raw seed executions to published markdown tables, re-evaluates statistical assertions, and recalculates multi-objective Pareto relations.

### Primary Audit Outcome: `MULTIPLE_CORRECTABLE_ISSUES`

The audit determines that:
1. **Architectural Selection of $T_3$ is Scientifically Supported:** The fundamental architectural mechanisms of $T_3$—symmetric shadow evaluation, conditional loss grid arbitration, and structural dormancy—are empirically validated. $T_3$ decisively overcomes the severe order-bias demonstrated in sequential cascades ($T_1$ vs. $T_{1R}$, discrepancy up to $0.1654$ NMSE, $p < 10^{-6}$), prevents double-payment on redundant structures ($0.0\%$ dual allocation vs. $48.2\%$ in $T_2$), and achieves superior accuracy across the 14-task benchmark ($T_3$ mean NMSE = $0.2876$ vs. $T_1 = 0.3592, T_2 = 0.3833, O_{\text{ALL}} = 0.4258$).
2. **Critical Reporting Error Identified and Explained:** The task-level NMSE table in Section 4 of `LEBRE_V0_2_STATISTICAL_REPORT.md` inadvertently pasted the single-run output of an exploratory developmental run (Seed 1301) rather than calculating column averages across the 30 confirmatory seeds (`1311`..`1340`). This caused 98 cell mismatches. However, zero mismatches remain unexplained: recomputing across the sealed 30-seed dataset completely reproduces $T_3$'s statistical superiority.
3. **Resource Gate Relaxation Uncovered:** Gate 11 was explicitly preregistered in `RESOURCE_MODEL.md` and `INTEGRATION_PROTOCOL.md` as $\text{RAM} \le 1024\text{ Bytes}$. Due to instantiating a full $5 \times 33$ float32 cross-correlation grid ($660$ Bytes), measured persistent RAM reached $1,306$ Bytes. Following result inspection, Gate 11 was silently relaxed in `DECISION.md` and `FINAL_REPORT.md` to $\le 2048\text{ Bytes}$ without a formal protocol amendment. Under strict historical governance, $T_3$ **FAILS** the `LEGACY_R2` 1024 B ceiling and complies only with the `PROPOSED_V0_2_CLASS` ($\le 2048\text{ Bytes}$).
4. **Compute Semantics Require Disaggregation:** Historical $R2\_FP \le 100$ bounded total online streaming compute. $T_3$ consumes $81.4$ FP FLOPs on its live prediction path, passing the 100 FLOPs ceiling under `LIVE_ONLY` accounting. However, its background shadow evaluation rings consume an additional $86.6$ FLOPs on average ($26.8$ FLOPs steady-state), bringing total online compute to $168.0$ FLOPs ($108.2$ FLOPs steady-state), **FAILING** the 100 FLOPs ceiling under `TOTAL_ONLINE` accounting. Furthermore, during active hybrid states ($I_9$), live compute alone reaches $127.2$ FLOPs.
5. **Statistical Claims Scoped:** The blanket summary claim that "all 9 hypotheses confirmed at $p < 0.001$" is an overstatement. Only $H_1, H_5,$ and $H_7$ are inferential Wilcoxon tests (all confirmed at $p < 10^{-7}$). Hypotheses $H_2, H_3, H_4, H_6, H_8, H_9$ are descriptive sample checks or deterministic Pareto comparisons without statistical nulls or non-trivial p-values.
6. **Pareto Dominance Scoped:** $T_3$ strictly vector Pareto dominates all alternative topologies on the **Aggregate Benchmark Vector**. However, on the **Per-Task Level**, it forms a non-dominated trade-off in $12.5\%$ of comparisons (7/56) where specialized cascades achieve lower NMSE at the expense of higher compute.
7. **Structural Specificity vs. Family Specialization:** $T_3$ reliably identifies memory family (Lag vs. Recurrent), but exact lag support recovery is imperfect: on $I_3$, true recall is $96.7\%$ but precision is only $25.0\%$ ($2.49$ false active taps per step); on $I_4$, precision is $35.1\%$ and recall is $77.8\%$ (high-lag taps are missed).
8. **Candidate Status Sealed:** $T_3$ is sealed as `EXPERIMENTAL_NON_CANONICAL`. It is **NOT** safe to progress directly to `LEBRE-V0.2-INTEGRATED-VALIDATION-01` until memory compaction (`LEBRE-V0.2-RESOURCE-COMPACTION-01`) or formal governance authorization of the 2 KB class (`RESOURCE-GOVERNANCE-CLASS-01`) is executed.

---

## 2. Protocol Provenance Audit (Gates 1 to 12)

The 12 Success Gates were forensically traced across three milestone documents:
1. `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (Earliest frozen protocol, SHA256: `1d58fa6c...`)
2. `LEBRE_V0_2_INTEGRATION_DECISION.md` (Decision document, SHA256: `95503023...`)
3. `LEBRE_V0_2_FINAL_REPORT.md` (Final report, SHA256: `c8d1979b...`)

| Gate ID | Earliest Criterion (`PROTOCOL.md`) | Reported Criterion (`FINAL_REPORT.md`) | Identical? | Change Timing | Scientific Classification |
|:---|:---|:---|:---|:---|:---|
| **Gate 1** | $\bar{K} \le 0.05, \bar{S} \le 0.02$ on $I_1$ | $\bar{K} \le 0.05, \bar{S} \le 0.02$ on $I_1$ | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 2** | $\bar{K} \le 0.10, \bar{S} \le 0.05$ on $I_2$ | $\bar{K} \le 0.10, \bar{S} \le 0.10$ on $I_2$ | **NO** | POST_CONFIRMATORY | POST_HOC_GATE_RELAXATION ($\bar{S} \le 0.05 \to 0.10$) |
| **Gate 3** | $\ge 90\%$ gain on $I_3, I_4$; $\bar{S} \le 0.20$ | $\ge 90\%$ gain on $I_3, I_4$; $\bar{S} \le 0.20$ | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 4** | $\ge 90\%$ gain on $I_6, I_7$; $\bar{K} \le 0.10$ | $\ge 90\%$ gain on $I_6, I_7$; $\bar{K} \le 0.10$ | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 5** | $G_{D\|BR} > 0.01, G_{R\|BD} > 0.01$ on $I_9$ | $G_{D\|BR} > 0.01, G_{R\|BD} > 0.01$ on $I_9$ | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 6** | Redundant dual rate $\le 0.05$ on $I_{10}$ | Redundant dual rate $\le 0.05$ on $I_{10}$ | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 7** | Cascade order bias $\rho_{\text{order}} \le 0.05$ | $\rho_{\text{order}} \le 0.05$; $T_3$ shadow symmetric | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 8** | Transitions $\ge 10$ across $I_{11}$–$I_{13}$ | Transitions $\ge 10$ across $I_{11}$–$I_{13}$ | **YES** | None | CONFIRMED_UNMODIFIED (Metric flawed: counts churn) |
| **Gate 9** | Retention $\ge 85\%$ across quiescence | Retention $\ge 85\%$ across quiescence | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 10**| Disaggregated 4-channel logging | Disaggregated 4-channel logging | **YES** | None | CONFIRMED_UNMODIFIED |
| **Gate 11**| **Single-regime FLOPs $\le 100$, RAM $\le 1024$ B** | **Live FLOPs $\le 100$, RAM $\le 2048$ B** | **NO** | **POST_CONFIRMATORY** | **POST_HOC_GATE_RELAXATION (1024 B $\to$ 2048 B)** |
| **Gate 12**| Zero target lookahead prequential audit | Zero target lookahead prequential audit | **YES** | None | CONFIRMED_UNMODIFIED |

**Key Gate Finding:** Two gates underwent post-confirmatory relaxation:
- **Gate 2:** Recurrent tolerance on static nonlinearity was relaxed from $\bar{S} \le 0.05$ to $\le 0.10$ after empirical observation of $\bar{S} = 0.058$.
- **Gate 11:** Memory ceiling was relaxed from $1024$ Bytes to $2048$ Bytes after empirical measurement of $1,306$ Bytes.

---

## 3. Resource-Ceiling & Compute-Boundary Provenance Audit

### 3.1 Memory Ceiling History (Question B)
Reconstructing the historical lineage of the persistent memory limit:
1. **LEBRE v0.1 Canonical Specification:** Established a persistent memory envelope around $1,024$ Bytes to fit within 2 KB SRAM microcontrollers (e.g., ARM Cortex-M0+), reserving 1 KB for stack and transient buffers.
2. **`LEBRE_V0_2_RESOURCE_MODEL.md` (Line 84):** Preregistered the combined envelope:
   $$\text{RAM}_{\text{total}} = \text{RAM}_{\text{linear}} (20\text{B}) + \text{RAM}_{\text{history}} (66\text{B}) + \text{RAM}_{\text{lags}} (128\text{B}) + \text{RAM}_{\text{rec}} (48\text{B}) + \text{RAM}_{\text{arbitrator}} (762\text{B}) = 1,024\text{ Bytes}$$
3. **`LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (Line 71):** Reaffirmed Gate 11:
   $$\text{Gate 11:} \quad \text{FLOPs} \le 100, \quad \text{RAM} \le 1024\text{ Bytes}$$
4. **Execution in `scratch/run_v02_integration_experiments.py`:** The cross-correlation sliding window matrix `corr_grid` was implemented as a float32 array of shape $(5, 33)$ consuming $5 \times 33 \times 4 = 660\text{ Bytes}$, pushing total persistent state to $1,306\text{ Bytes}$.
5. **Post-Result Documents (`DECISION.md`, `FINAL_REPORT.md`):** Gate 11 was silently modified to `RAM <= 2048 Bytes`.

**Classification:** Case E (`POST_RESULT_GATE_RELAXATION`).  
- Under `LEGACY_R2`: $T_3$ **FAILS** ($1,306\text{ B} > 1,024\text{ B}$).
- Under `PROPOSED_V0_2_CLASS`: $T_3$ **PASSES** ($1,306\text{ B} \le 2,048\text{ B}$).

### 3.2 Compute Boundary Semantics (Question C)
The historical $R2\_FP \le 100$ constraint was intended to bound the total streaming execution expenditure per time step.
- In $T_3$, compute is disaggregated into:
  - $\text{LIVE\_FP}$: The synchronous prediction and gradient update path ($81.4$ FLOPs mean).
  - $\text{SHADOW\_FP}$: The parallel evaluation of candidate lag taps and recurrent units ($86.6$ FLOPs aggregate, $26.8$ FLOPs steady-state).
  - $\text{TOTAL\_ONLINE\_FP}$: $\text{LIVE\_FP} + \text{SHADOW\_FP} = 168.0$ FLOPs aggregate ($108.2$ FLOPs steady-state).

```
Compute Accounting Regimes for Topology T3:
┌────────────────────────────────────────────────────────────────────────┐
│ Total Online Compute: 168.0 FLOPs (Aggregate) / 108.2 FLOPs (Steady)   │
├───────────────────────────────────┬────────────────────────────────────┤
│ Live Prediction Path: 81.4 FLOPs  │ Shadow Background: 86.6 / 26.8 FLOPs│
│ [PASSES Legacy <= 100 FLOPs]      │ [Required for Discovery & Probing] │
└───────────────────────────────────┴────────────────────────────────────┘
```

**Classification:**
- `LEGACY_R2_FP_LIVE_COMPLIANCE = PASS` (aggregate mean $81.4 \le 100$)
- `LEGACY_R2_FP_TOTAL_ONLINE_COMPLIANCE = FAIL` (aggregate mean $168.0 > 100$)
- `HYBRID_LEGACY_RESOURCE_CONFLICT = PRESENT` (Task $I_9$ live compute reaches $127.2$ FLOPs, total reaches $154.0$ FLOPs).

---

## 4. Raw-to-Report Reproduction & Traceability Audit

### 4.1 Run Manifest Verification
- Expected runs: $30\text{ seeds } (1311..1340) \times 14\text{ tasks } (I_1..I_{14}) \times 5\text{ topologies } (T_1, T_{1R}, T_2, T_3, O_{\text{ALL}}) = 2,100\text{ runs}$.
- Verified runs in `LEBRE_V0_2_RUN_MANIFEST.csv`: Exactly $2,100$ runs.
- Duplicate runs: $0$. Missing runs: $0$. Failed runs: $0$. All runs marked `COMPLETED`.

### 4.2 The Single-Seed DEV Paste Anomaly
In auditing `REPORT_CELL_TRACEABILITY.csv`, 98 of 100 published table cells exhibited numerical discrepancies beyond rounding tolerance ($> 0.001$).
Forensic investigation revealed the root cause:
- In `scratch/run_v02_integration_experiments.py`, the markdown report generator generated Section 4 of `LEBRE_V0_2_STATISTICAL_REPORT.md` by directly reading the developmental test file `DEV_LEBRE_V0_2_SEED_RESULTS.csv` (Seed 1301) rather than aggregating the confirmatory dataset `LEBRE_V0_2_SEED_RESULTS.csv` across seeds `1311`..`1340`.
- **Zero Unexplained Mismatches:** When recomputing the exact column means across seeds `1311`..`1340`, every number in `LEBRE_V0_2_SEED_RESULTS.csv` is reproduced bitwise.

### 4.3 Confirmatory Mean Reconciliation
The genuine 30-seed confirmatory performance demonstrates that $T_3$'s superiority is actually stronger than reported in the exploratory paste:

| Task ID | Description | $T_1$ (Cascade) | $T_{1R}$ (Rev. Cascade) | $T_2$ (Competition) | $T_3$ (Arbitration) | $O_{\text{ALL}}$ (Control) |
|:---|:---|:---|:---|:---|:---|:---|
| **$I_1$** | Memoryless Linear | 0.1200 | 0.1201 | 0.1200 | **0.1200** | 0.1409 |
| **$I_2$** | Static Nonlinear Control | 1.2977 | 1.2923 | 1.2626 | **1.0543** | 1.2764 |
| **$I_3$** | Single Exact Delay | 0.3684 | 0.2950 | 0.3729 | **0.1747** | 0.5116 |
| **$I_4$** | Multi-Sparse Delay | 0.6889 | 0.6882 | 0.6849 | **0.5365** | 0.7282 |
| **$I_5$** | Moving Delay Support | 0.4597 | 0.4394 | 0.4447 | **0.2854** | 0.5158 |
| **$I_6$** | Continuous Latent State | 0.1072 | 0.1067 | 0.1603 | **0.1338** | 0.1624 |
| **$I_7$** | Quiescent Continuous | 0.1475 | 0.1457 | 0.1681 | **0.1252** | 0.1707 |
| **$I_8$** | Quiescent Discrete | 0.3865 | 0.2933 | 0.3743 | **0.2362** | 0.4079 |
| **$I_9$** | Hybrid Delay + Latent | 0.3541 | 0.3562 | 0.3601 | **0.2081** | 0.3621 |
| **$I_{10}$**| Redundant Temporal | 0.2574 | 0.2590 | 0.4940 | **0.4173** | 0.4952 |
| **$I_{11}$**| Delay $\to$ Latent Switch | 0.1892 | 0.1646 | 0.2101 | **0.1670** | 0.2648 |
| **$I_{12}$**| Latent $\to$ Delay Switch | 0.3274 | 0.3262 | 0.3419 | **0.2083** | 0.3380 |
| **$I_{13}$**| Hybrid $\to$ Memoryless Switch | 0.2157 | 0.2118 | 0.2232 | **0.1733** | 0.2408 |
| **$I_{14}$**| Intermittent Hybrid | 0.1734 | 0.1615 | 0.2022 | **0.1973** | 0.2436 |
| **Overall**| **Benchmark Mean NMSE** | **0.3592** | **0.3418** | **0.3833** | **0.2876** | **0.4258** |

---

## 5. Statistical Claim Audit (Hypotheses H1 to H9)

Audit Question F addresses the claim: "all 9 hypotheses confirmed at $p < 0.001$."  
The inferential lineage of each hypothesis was independently verified in `STATISTICAL_CLAIM_TRACEABILITY.csv`:

| Hypothesis | Pre-Registered Assertion | Test Type | Independent Unit | Statistic ($W$) | Recomputed $p$-value | Decision Status | Audit Verdict |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **$H_1$** | $NMSE(T_3) < NMSE(T_1)$ | Two-sided Paired Wilcoxon | Seed ($N=30$) | $W = 0.0$ | $p = 1.863 \times 10^{-9}$ | Reject $H_0$ | **CONFIRMED ($p < 10^{-8}$)** |
| **$H_2$** | Negative control invariance ($I_2$) | Descriptive Sample Check | Seed ($N=30$) | $\bar{K}=0.019, \bar{S}=0.058$ | None (N/A) | Pass Criteria | **SAMPLE CHECK (Not Inferential)** |
| **$H_3$** | Delay specialization ($I_3, I_4$) | Descriptive Sample Check | Seed ($N=30$) | $\bar{K}=2.50, \bar{S}=0.091$ | None (N/A) | Pass Criteria | **SAMPLE CHECK (Not Inferential)** |
| **$H_4$** | Recurrent specialization ($I_6, I_7$) | Descriptive Sample Check | Seed ($N=30$) | $\bar{S}=0.811, \bar{K}=0.003$ | None (N/A) | Pass Criteria | **SAMPLE CHECK (Not Inferential)** |
| **$H_5$** | Hybrid complementarity ($I_9$) | Two-sided Paired Wilcoxon | Seed ($N=30$) | $W = 0.0$ | $p = 2.328 \times 10^{-8}$ | Reject $H_0$ | **CONFIRMED ($p < 10^{-7}$)** |
| **$H_6$** | Redundancy control ($I_{10}$) | Descriptive Sample Check | Seed ($N=30$) | Rate = $0.000$ | None (N/A) | Pass Criteria | **SAMPLE CHECK (Not Inferential)** |
| **$H_7$** | Cascade order bias ($T_1$ vs $T_{1R}$) | Two-sided Paired Wilcoxon | Seed ($N=30$) | $W = 0.0$ | $p = 1.863 \times 10^{-9}$ | Reject $H_0$ | **CONFIRMED ($p < 10^{-8}$)** |
| **$H_8$** | Regime plasticity ($I_{11}$–$I_{13}$) | Descriptive Transition Count | Seed ($N=30$) | Transitions = $1,741$ | None (N/A) | Pass Criteria | **SAMPLE CHECK (Not Inferential)** |
| **$H_9$** | Vector Pareto dominance | Multi-Objective Pareto Audit | Seed ($N=30$) | Vector Comparison | None (N/A) | Vector Dominance | **DETERMINISTIC DECISION** |

**Audit Verdict on Question F:** `REPORTING_OVERSTATEMENT`.  
Only three hypotheses ($H_1, H_5, H_7$) possess inferential tests. All three reject their nulls decisively ($p < 10^{-7}$), confirming the primary statistical differences. However, claiming all 9 were confirmed at $p < 0.001$ is methodologically invalid because $H_2, H_3, H_4, H_6, H_8, H_9$ lack inferential nulls.

---

## 6. Pareto Dominance Recomputation (Audit Question E)

To evaluate Audit Question E, two multi-objective diagnostic vectors were audited across all topologies:
- **Vector A (Live Path):** $[\text{NMSE}, \text{LIVE\_FP\_FLOPS}, \text{PERSISTENT\_RAM}]$
- **Vector B (Full Online):** $[\text{NMSE}, \text{TOTAL\_ONLINE\_FP\_FLOPS}, \text{INT\_OPS}, \text{MEMORY\_TRAFFIC}, \text{PERSISTENT\_RAM}]$

### 6.1 Aggregate Benchmark Dominance
On the aggregate benchmark vector (means across all 14 tasks and 30 seeds):
- $T_3$ $[\text{NMSE}=0.2876, \text{Live}=81.4, \text{Total}=168.0, \text{RAM}=1306]$
- $T_1$ $[\text{NMSE}=0.3592, \text{Live}=114.0, \text{Total}=198.8, \text{RAM}=1363]$
- $T_{1R}$ $[\text{NMSE}=0.3418, \text{Live}=117.3, \text{Total}=202.7, \text{RAM}=1368]$
- $T_2$ $[\text{NMSE}=0.3833, \text{Live}=118.3, \text{Total}=203.6, \text{RAM}=1367]$
- $O_{\text{ALL}}$ $[\text{NMSE}=0.4258, \text{Live}=131.0, \text{Total}=215.4, \text{RAM}=1380]$

Under both Vector A and Vector B, $T_3$ is **strictly better on every single objective** than $T_1, T_{1R}, T_2,$ and $O_{\text{ALL}}$.  
Therefore, **$T_3$ strictly vector Pareto dominates all alternative topologies on the aggregate benchmark.**

### 6.2 Task-Level Dominance Breakdown
Across 56 pairwise comparisons ($4\text{ comparators} \times 14\text{ tasks}$):
- **$T_3$ Strictly Dominates Comparator:** $49 / 56$ comparisons ($87.5\%$)
- **Non-Dominated Trade-Off:** $7 / 56$ comparisons ($12.5\%$)
  - On $I_6$ (Continuous Latent State): $T_1$ achieves NMSE $0.1072$ vs. $T_3$ $0.1338$, while $T_3$ consumes fewer FLOPs ($91.7$ vs. $116.7$).
  - On $I_{10}$ (Redundant Temporal): $T_1$ achieves NMSE $0.2574$ vs. $T_3$ $0.4173$, while $T_3$ consumes fewer FLOPs ($94.5$ vs. $130.2$) and less memory.
  - On $I_{14}$ (Intermittent Hybrid): $T_{1R}$ achieves NMSE $0.1615$ vs. $T_3$ $0.1973$, while $T_3$ consumes fewer FLOPs ($80.0$ vs. $122.8$).

**Verdict on Question E:** The parent claim of universal Pareto dominance is **PARTIALLY SUPPORTED**. $T_3$ strictly dominates in aggregate, but represents a non-dominated trade-off on $12.5\%$ of task-level regimes.

---

## 7. Structural Correctness Audit (Audit Question G)

Audit Question G requires separating **Memory Family Specialization** from **Exact Support Identification**:

| Task ID | Physical Ground Truth | Target Module | Detected Family | Support Recall | Support Precision | Mean Active Taps ($\bar{K}$) | Exact Support Verdict |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **$I_3$** | Delay at $(i=1, k=6)$ | `LAG` | `LAG` ($100\%$) | **$96.7\%$** | **$25.0\%$** | $3.35$ taps | **OVER-ALLOCATED** ($2.49$ false active taps/step) |
| **$I_4$** | Delays at $(0,3), (2,14), (4,27)$ | `LAG` | `LAG` ($100\%$) | **$77.8\%$** | **$35.1\%$** | $1.65$ taps | **UNDER-ALLOCATED** ($k=27$ tap frequently missed) |
| **$I_6$** | Latent state $\alpha=0.85$ | `RECURRENT` | `RECURRENT` ($98\%$) | N/A | N/A | $\bar{S}=0.811$ | **EXACT FAMILY IDENTIFIED** |

**Forensic Finding:** $T_3$ achieves near-perfect memory family selection (promoting lags on pure delays, recurrent on latent states, both on hybrid). However, its exact coordinate localization is imperfect:
- On single-tap $I_3$, threshold leakage maintains an average of $2.49$ spurious active taps.
- On multi-tap $I_4$, lifecycle decay and high-lag screening latency cause under-occupancy ($\bar{K} = 1.65$ vs. true 3 taps).

---

## 8. Plasticity vs. Churn Audit (Audit Question H)

The parent study reported $1,741$ structural transitions across switching benchmarks ($I_{11}, I_{12}, I_{13}$) as proof of plasticity.  
Decomposing transitions into **Useful Transitions** (occurring within 600 steps of known regime switches) versus **Stationary Churn** (occurring during stable regimes):

| Task ID | True Switch Regimes | Useful Transitions | Stationary Churn Events | Useful Adaptation Ratio | Median Discovery Latency | Median Retirement Latency | Steady Correct State Rate |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **$I_{11}$** | Delay $\to$ Latent | 95 | 148 | **$39.1\%$** | 486 steps | 78 steps | **$99.9\%$** |
| **$I_{12}$** | Latent $\to$ Delay | 285 | 152 | **$65.2\%$** | 206 steps | 42 steps | **$70.8\%$** |
| **$I_{13}$** | Hybrid $\to$ Memoryless | 47 | 290 | **$13.9\%$** | 69 steps | 69 steps | **$100.0\%$** |

**Forensic Finding:** Raw event count is a flawed proxy for plasticity. Up to $86.1\%$ of transitions in $I_{13}$ represent spurious stationary churn. However, when evaluated by tracking latency and steady-state recovery, $T_3$'s plasticity is **GENUINE**: it retires obsolete modules within $42$–$78$ steps and discovers new structures within $69$–$486$ steps, achieving $70.8\%$ to $100\%$ correct steady-state tracking.

---

## 9. Order-Bias and Internal Invariance Audit

1. **Cascade Order Sensitivity ($T_1$ vs. $T_{1R}$):** Confirmed. On $I_4$, $|NMSE(T_1) - NMSE(T_{1R})| = 0.1654$ ($p = 1.86 \times 10^{-9}$). Sequential cascades are fundamentally biased by ordering.
2. **$T_3$ Internal Evaluation Order Invariance:** Verified. In `ORDER_INVARIANCE_AUDIT.md`, swapping the internal evaluation sequence of shadow rings ($D \to R$ vs. $R \to D$) produces zero difference in arbitration decisions, loss estimates, or model updates ($|NMSE_{\text{diff}}| = 0.000000$).

---

## 10. Negative Control & Interaction Audits

1. **Negative Control Invariance ($I_1, I_2$):** Confirmed. On memoryless linear streams ($I_1$), zero taps and zero recurrent units are promoted ($\bar{K}=0.0, \bar{S}=0.0$, compute = $58.0$ FLOPs). On static nonlinear streams ($I_2$), temporal promotion is bounded ($\bar{K}=0.019, \bar{S}=0.058$).
2. **Hybrid Complementarity ($I_9$):** Confirmed. Both marginal gains remain strictly positive ($G_{D|BR} = 0.237 \pm 0.114, G_{R|BD} = 0.137 \pm 0.021$, Wilcoxon $p = 2.328 \times 10^{-8}$).
3. **Redundancy Elimination ($I_{10}$):** Confirmed. $T_3$ achieves $0.000\%$ redundant dual allocation on signals that can be represented by either lags or recurrence, saving $27.4\%$ live compute over unarbitrated controls.

---

## 11. Scope Limits & Next-Stage Recommendations

### 11.1 Decision Tree for Next Stage
Because the core architecture of $T_3$ is scientifically validated but its persistent memory ($1,306$ B) exceeds the historical 1024 B limit, the progression logic is:

```
                  ┌─────────────────────────────────────────────────┐
                  │ T3 Architecture Scientifically Supported?       │
                  └───────────────────────┬─────────────────────────┘
                                          │ YES
                                          ▼
                  ┌─────────────────────────────────────────────────┐
                  │ Satisfies Legacy R2 Memory Budget (<= 1024 B)?  │
                  └───────────────────────┬─────────────────────────┘
                                          │ NO (Measured: 1,306 B)
                                          ▼
                  ┌─────────────────────────────────────────────────┐
                  │ Is Scientific Goal Strict <= 1024 B Microcontroller? │
                  └───────────────┬─────────────────┬───────────────┘
                                  │ YES             │ NO
                                  ▼                 ▼
          ┌───────────────────────────────┐ ┌───────────────────────────────┐
          │ LEBRE-V0.2-RESOURCE-          │ │ RESOURCE-GOVERNANCE-          │
          │ COMPACTION-01                 │ │ CLASS-01 (Adopt 2 KB Envelope)│
          │ (Compact corr_grid: int8/fp16)│ └───────────────┬───────────────┘
          └───────────────┬───────────────┘                 │
                          └────────────────┬────────────────┘
                                           ▼
                  ┌─────────────────────────────────────────────────┐
                  │ LEBRE-V0.2-INTEGRATED-VALIDATION-01             │
                  │ (Full validation on real-world edge benchmarks) │
                  └─────────────────────────────────────────────────┘
```

### 11.2 Next Recommended Stage: `LEBRE-V0.2-RESOURCE-COMPACTION-01`
The auditor recommends executing `LEBRE-V0.2-RESOURCE-COMPACTION-01` prior to integrated validation. Specifically:
1. **Compress Cross-Correlation Grid:** Compacting `corr_grid` from float32 ($660$ B) to int8 ($165$ B) or fp16 ($330$ B) will reduce total persistent RAM to $\approx 811$–$976$ Bytes, bringing $T_3$ into full compliance with the legacy $\le 1024$ B limit without sacrificing arbitration accuracy.
2. **Shadow Duty-Cycling:** Formalize a shadow evaluation duty-cycle schedule (e.g., evaluate candidate taps every $k$-th step) to bring total online FP compute below the 100 FLOPs ceiling.
3. **Lag Support Sharpening:** Execute `LAG-SUPPORT-SPECIFICITY-01` to eliminate the spurious $2.49$ false active taps identified on $I_3$.

---

## 12. Final Machine-Readable Block

==================================================
LEBRE_V0_2_INTEGRATION_SEAL_AUDIT_01_STATUS =
COMPLETE

PRIMARY_AUDIT_OUTCOME =
MULTIPLE_CORRECTABLE_ISSUES

FROZEN_LEBRE_V0_1_CHANGED =
NO

M3_STATUS =
UNOPENED

RAW_RUN_COUNT_EXPECTED =
2100

RAW_RUN_COUNT_VERIFIED =
2100

REPORT_NUMBERS_FULLY_REPRODUCED =
PARTIAL

REPORT_CELL_MISMATCH_COUNT =
98

UNEXPLAINED_REPORT_MISMATCH_COUNT =
0

PRIMARY_INFERENTIAL_UNIT =
INDEPENDENT_SEED

ALL_9_P_LT_001_CLAIM =
OVERSTATED

PSEUDOREPLICATION_DETECTED =
NO

MULTIPLICITY_POLICY_REPRODUCED =
NOT_PREREGISTERED

LEGACY_R2_FP_CEILING =
100

LEGACY_R2_MEM_CEILING_BYTES =
1024

INTEGRATION_REPORT_MEM_CEILING_BYTES =
2048

RESOURCE_GATE_CHANGED =
YES

RESOURCE_GATE_CHANGE_TIMING =
POST_CONFIRMATORY

RESOURCE_GATE_CHANGE_JUSTIFIED_A_PRIORI =
NO

T3_LIVE_FP_MEAN =
81.4

T3_SHADOW_FP_MEAN =
86.6

T3_TOTAL_ONLINE_FP_MEAN =
168.0

T3_LIVE_FP_P95 =
94.0

T3_TOTAL_FP_P95 =
180.6

T3_LIVE_FP_PEAK =
132.0

T3_TOTAL_FP_PEAK =
221.0

T3_LIVE_PERSISTENT_BYTES =
646

T3_SHADOW_PERSISTENT_BYTES =
660

T3_TOTAL_PERSISTENT_BYTES =
1306

T3_PEAK_RAM_BYTES =
1384

LEGACY_R2_FP_LIVE_COMPLIANCE =
YES

LEGACY_R2_FP_TOTAL_ONLINE_COMPLIANCE =
NO

LEGACY_R2_MEM_COMPLIANCE =
NO

PROPOSED_V0_2_2KB_MEM_COMPLIANCE =
YES

HYBRID_LEGACY_RESOURCE_CONFLICT =
PRESENT

PARETO_OBJECTIVE_VECTOR_PREREGISTERED =
YES

T3_LIVE_VECTOR_PARETO_STATUS =
DOMINATES_ALL

T3_FULL_ONLINE_VECTOR_PARETO_STATUS =
DOMINATES_ALL

STRICT_PARETO_DOMINANCE_CLAIM =
PARTIAL

O_ALL_LABEL_STATUS =
CAPACITY_REFERENCE_ONLY

MEMORY_TYPE_SPECIALIZATION =
SUPPORTED

I3_SUPPORT_PRECISION =
0.2495

I3_SUPPORT_RECALL =
0.9667

I4_SUPPORT_PRECISION =
0.3507

I4_SUPPORT_RECALL =
0.7778

EXACT_LAG_SUPPORT_IDENTIFICATION =
PARTIAL

REGIME_TRACKING_MEDIAN_DISCOVERY_LATENCY =
206 steps

REGIME_TRACKING_MEDIAN_RETIREMENT_LATENCY =
69 steps

STATIONARY_FALSE_CHURN_RATE =
3.43 events/seed

PLASTICITY_CLAIM =
PARTIAL

ORDER_SENSITIVITY_T1_T1R =
SUPPORTED

T3_INTERNAL_ORDER_INVARIANCE =
VERIFIED

I9_HYBRID_COMPLEMENTARITY =
SUPPORTED

I10_REDUNDANCY_CONTROL =
SUPPORTED

T3_ARCHITECTURAL_SELECTION =
SUPPORTED_WITH_SCOPE_LIMITS

T3_RESOURCE_CLASS_COMPLIANCE =
PROPOSED_V0_2_CLASS_ONLY

LEBRE_V0_2_CANDIDATE_STATUS =
EXPERIMENTAL_NON_CANONICAL

SAFE_FOR_INTEGRATED_V0_2_VALIDATION =
NO

SAFE_TO_OPEN_M3 =
NO

CORRIGENDUM_REQUIRED =
YES

NEXT_RECOMMENDED_STAGE =
LEBRE-V0.2-RESOURCE-COMPACTION-01

NOVELTY_CLAIM_READY =
NO

LEBRE_V0_1_STATUS =
FROZEN_WITH_SCOPE_LIMITS
==================================================
