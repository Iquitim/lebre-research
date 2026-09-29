# Candidate Subsystem Resource Feasibility & Post-Seal Microcorrection Final Report
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Target Parent Stages: LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01 & LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01
## Lead Auditor: Independent Senior Scientific Software Auditor
## Date of Audit: September 2026
## Authority Level: Level 3 (Sealed Forensic Report & Feasibility Ruling)

---

## Executive Summary

This study executed two strictly separated objectives:
- **Phase A (Post-Seal Deterministic Microcorrection):** Resolved the residual Gate G8 / $R_0$ baseline non-inferiority reporting discrepancy, standardized search memory terminology across dense and sparse architectures, and calibrated the causal phrasing regarding queue traversal speed.
- **Phase B (Candidate Subsystem Resource Feasibility):** Evaluated whether the candidate discovery, probation, and evaluation subsystem contains sufficient theoretically removable computational work to close the resource deficit between current model $M_1^*$ ($111.013591\text{ FP/step}$) and the mandatory $\le 100.0\text{ FP/step}$ ceiling.

### Core Feasibility Ruling:
The mathematical and empirical evaluation proves that **the candidate subsystem cannot close the resource gap**.
- The compute deficit against the $100.0\text{ FP/step}$ target is **$11.013591\text{ FP/step}$**.
- The entire candidate subsystem (direct observation, parameter learning, counterfactual loss, and descendant arbitration) consumes only **$7.444633\text{ FP/step}$**.
- Even under an **impossible oracle where 100% of candidate work is free (0 FLOPs)**, the residual compute of $M_1^*$ is **$103.568958\text{ FP/step} > 100.0\text{ FP/step}$**.
- Failed probation waste accounts for only **$1.769083\text{ FP/step}$** ($16.06\%$ of the deficit), of which at most $\approx 0.8845\text{ FP/step}$ ($8.03\%$) is retrospectively removable via early rejection.
- Consequently, stage `LEBRE-V0.2-CANDIDATE-PROBATION-COST-01` is **DENIED AUTHORIZATION**. The project must pause for human review to address the true computational sinks: base live linear execution ($75.47\text{ FP/step}$) and recurrent shadow work ($20.20\text{ FP/step}$).

---

## Section 1: Phase A Deterministic Microcorrections

### 1.1 Gate G8 / $R_0$ Baseline Non-Inferiority Reconciliation
In the seal audit final report, Gate G8 was tabulated as:
`| G8 | Baseline Preservation | R0 non-inferiority maintained | M1* beats R0 by -0.0982 NMSE | PASSED |`

The forensic audit determined that this was a **`MANUAL_TRANSCRIPTION_ERROR`**:
- The value $+0.0982$ originated from Gate G8's true preregistered identity in `SUCCESS_CRITERIA_RECONCILIATION.md`: **Hybrid Complementarity on $I_9$** ($G_{D|B+R} = +0.0982$, **PASSED**).
- The author conflated this metric with $R_0$ baseline preservation, inverted its sign to $-0.0982$, and labeled it as passing baseline preservation.
- Recomputing from Level 1 confirmatory logs (`CORRELATION_SEARCH_FINAL_RESULTS.csv`) across all 30 seeds yields:
  $$\Delta_{\text{NMSE}}(M_1^* - R_0) = +0.013027, \quad s_{\Delta} = 0.020554, \quad \text{SE}_{\Delta} = 0.003753$$
  $$\text{One-Sided 95% Upper CI} = +0.013027 + 1.699127 \times 0.003753 = \mathbf{+0.019402}$$
- Because $+0.019402 > +0.0100$ (the non-inferiority margin), **$R_0$ Baseline Non-Inferiority is FAILED (NOT_SUPPORTED)** ($t = +0.8065, p = 0.7867$). Continuous dense search $R_0$ achieves faster re-locking on abrupt regime transitions than $M_1^*$.

### 1.2 Search Memory Terminology Disambiguation
Frozen certified memory metrics:
- `DENSE_SEARCH_ACCUMULATOR_BYTES`: $165 \times 2\text{B} = \mathbf{330\text{ B}}$.
- `SPARSE_SEARCH_ACCUMULATOR_BYTES`: $32 \times 6\text{B} = \mathbf{192\text{ B}}$.
- `ACCUMULATOR_MEMORY_REDUCTION_PCT`: $\frac{330 - 192}{330} = \mathbf{41.82\%}$ (Gate G4 Passed).
- `DENSE_TOTAL_SEARCH_STATE_BYTES`: $\mathbf{330\text{ B}}$ (Standard) or $\mathbf{802\text{ B}}$ (`LEGACY_FULL_SEARCH_SUBSYSTEM_STATE_BYTES`).
- `SPARSE_TOTAL_SEARCH_STATE_BYTES`: $\mathbf{260\text{ B}}$ ($192\text{B table} + 68\text{B overhead}$).
- `TOTAL_SEARCH_STATE_REDUCTION_PCT`:
  - Relative to standard table ($330\text{ B}$): $\frac{330 - 260}{330} = \mathbf{21.21\%}$.
  - Relative to legacy full state ($802\text{ B}$): $\frac{802 - 260}{802} = \mathbf{67.58\%}$.
  The legacy $802\text{ B}$ figure included $330\text{B}$ feature energy accumulators, $2\text{B}$ residual energy, and $140\text{B}$ tracking metadata.

### 1.3 Queue Traversal Causal Wording Correction
Auditing the simulation logs confirmed that no dedicated parameter ablation isolating queue sweep speed while holding all other factors constant was ever conducted (`QUEUE_SPEED_CAUSAL_ABLATION_EXISTS = NO`).
The binding wording is amended to:
> **"Faster traversal is the primary mechanistically supported explanation under the current evidence."**
- `FASTER_QUEUE_TRAVERSAL = SUPPORTED_MECHANISTIC_EXPLANATION`
- `ISOLATED_CAUSAL_EFFECT = NOT_ESTABLISHED`

---

## Section 2: Phase B Candidate Subsystem Operation Ledger & Global Reconciliation

### 2.1 Operation Ledger Summary
The candidate subsystem encompasses 10 functional operations (certified in `CANDIDATE_SUBSYSTEM_OPERATION_LEDGER.csv`):
- **`DISCOVERY` (OP_01):** Frontier threshold check & slot allocation ($0.0\text{ FP/step}$, $0.0155\text{ events/step}$).
- **`OBSERVATION` (OP_02):** Delay tap fetch & forward counterfactual prediction ($0.246148\text{ FP/step}$).
- **`STATE_PROPAGATION` (OP_03):** Advance age/obs counter ($0.0\text{ FP/step}$, $2\text{ INT ops}$).
- **`PARAMETER_LEARNING` (OP_04):** Normalized LMS gradient step on candidate weight ($1.598486\text{ FP/step}$).
- **`COUNTERFACTUAL_SCORING` (OP_05):** Error power difference calculation (bundled in obs, $0.164126\text{ FP/step}$).
- **`EVIDENCE_ACCUMULATION` (OP_06):** Running utility filter update (bundled in obs, $0.082063\text{ FP/step}$).
- **`PROMOTION_DECISION` (OP_07):** Threshold check vs $\theta_{\text{promote}}$ at $n=15$ ($0.015496\text{ FP/step}$).
- **`DISCARD_DECISION` (OP_08):** Eviction and slot deallocation ($0.0\text{ FP/step}$, $4\text{ INT ops}$).
- **`ARBITRATION` (OP_09):** Candidate descendant arbitration evaluations ($5.600000\text{ FP/step}$).
- **`HOUSEKEEPING` (OP_10):** Active slot table indexing ($0.0\text{ FP/step}$, $4\text{ INT ops}$).

### 2.2 Global Compute Reconciliation
The exact decomposition of model $M_1^*$'s online operational compute ($111.013591\text{ FP/step}$) is:
$$\text{Base Live Execution (Synchronous filter + active taps)} = \mathbf{75.468234\text{ FP/step}} \quad (67.98\%)$$
$$\text{Search Frontier Probing (B=4, K=2)} = \mathbf{7.900724\text{ FP/step}} \quad (7.12\%)$$
$$\text{Base Recurrent Shadow State} = \mathbf{20.200000\text{ FP/step}} \quad (18.20\%)$$
$$\text{Direct Candidate Observation} = \mathbf{0.246148\text{ FP/step}} \quad (0.22\%)$$
$$\text{Direct Candidate Parameter Learning} = \mathbf{1.598486\text{ FP/step}} \quad (1.44\%)$$
$$\text{Candidate Descendant Arbitration} = \mathbf{5.600000\text{ FP/step}} \quad (5.04\%)$$
$$\mathbf{Total \ Instrumented \ Compute} = \mathbf{111.013591\text{ FP/step}} \quad (100.00\%)$$

$$\text{Direct Candidate Work} = 0.246148 + 1.598486 = \mathbf{1.844634\text{ FP/step}}$$
$$\text{Indirect Descendant Arbitration Work} = \mathbf{5.600000\text{ FP/step}}$$
$$\mathbf{Total \ Candidate \ Subsystem \ Footprint} = \mathbf{7.444633\text{ FP/step}} \quad (6.71\%)$$
$$\mathbf{Untouchable \ Core \ Compute} = 75.468234 + 7.900724 + 20.200000 = \mathbf{103.568958\text{ FP/step}} \quad (93.29\%)$$

---

## Section 3: The Three Savings Ceilings & Feasibility Determination

### 3.1 Ceilings Comparison Table

| Scenario / Ceiling | Removable Work (FP/step) | Residual Compute (FP/step) | Gap to 100 FP Target | Closure Ratio vs Deficit ($11.01\text{ FP}$) | Feasibility Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Current Baseline ($M_1^*$)** | $0.000000$ | $111.013591$ | $+11.013591$ | $0.00\%$ | Deficit Baseline |
| **Plausible Early Rejection** | $0.884542$ | $110.129049$ | $+10.129049$ | $8.03\%$ | **NO_FEASIBILITY** |
| **Semantically Mandatory Floor** | $1.769083$ | $109.244508$ | $+9.244508$ | $16.06\%$ | **NO_FEASIBILITY** |
| **Impossible Oracle Ceiling** | $7.444633$ | $103.568958$ | $+3.568958$ | $67.59\%$ | **MATHEMATICALLY_NO** |
| **Target Ceiling** | $11.013591$ | $100.000000$ | $0.000000$ | $100.00\%$ | Required Gate |

### 3.2 Key Feasibility Inferences
1. **Mathematical Infeasibility:** Even if every candidate operation (including observation, learning, and descendant arbitration) is made 100% free, total compute is $103.57\text{ FP/step}$, failing the $100.0\text{ FP/step}$ requirement by $+3.57\text{ FP/step}$.
2. **Semantic Infeasibility:** Retaining logical candidate evaluation and eliminating failed probation waste yields $109.24\text{ FP/step}$, closing only $16.06\%$ of the deficit.
3. **Engineering Infeasibility:** Retrospective zero-false-negative early rejection recovers at most $\approx 0.88\text{ FP/step}$, closing only $8.03\%$ of the deficit.

---

## Section 4: Systematic Answers to the 25 Final Report Questions

### 1. What exactly constitutes the candidate subsystem?
The candidate subsystem comprises all computational logic, state, and evaluation overhead causally induced by temporary structural hypotheses prior to promotion: discovery birth logic, observation/feature extraction, state propagation, parameter adaptation, counterfactual scoring, evidence accumulation, promotion decision, discard eviction, descendant arbitration, and candidate slot housekeeping.

### 2. How many FP/step does it consume in total?
It consumes **$7.444633\text{ FP/step}$** ($6.71\%$ of model $M_1^*$'s total compute).

### 3. How much is direct candidate work?
Direct candidate work is **$1.844634\text{ FP/step}$** (Observation: $0.246148\text{ FP/step}$; Learning: $1.598486\text{ FP/step}$).

### 4. How much is descendant arbitration / shadow work?
Candidate descendant arbitration consumes **$5.600000\text{ FP/step}$**.

### 5. How much comes from failed candidates?
Failed candidate probation accounts for **$1.769083\text{ FP/step}$** ($95.9\%$ of direct candidate probation FLOPs).

### 6. How much comes from candidates that eventually promote?
Candidates that eventually promote consume **$0.040050\text{ FP/step}$** ($4.1\%$ of direct candidate probation FLOPs).

### 7. How much is candidate-independent and therefore untouchable?
Untouchable core compute is **$103.568958\text{ FP/step}$** ($93.29\%$ of total compute), consisting of base live filtering ($75.47\text{ FP/step}$), search probing ($7.90\text{ FP/step}$), and base recurrent shadow state ($20.20\text{ FP/step}$).

### 8. Does failed probation alone have enough leverage to close the gap?
**NO.** Failed probation is $1.769083\text{ FP/step}$. Eliminating 100% of failed probation leaves total compute at $109.244508\text{ FP/step}$, closing only $16.06\%$ of the $11.01\text{ FP}$ deficit.

### 9. Does ALL candidate work have enough leverage?
**MATHEMATICALLY NO.** Total candidate subsystem work is $7.444633\text{ FP/step}$. The required saving is $11.013591\text{ FP/step}$. $7.444633 < 11.013591$.

### 10. What is the theoretical M1* compute if the entire candidate subsystem became free?
It would be **$103.568958\text{ FP/step}$** ($+3.57\text{ FP/step}$ above the $100.0\text{ FP/step}$ target).

### 11. What is the minimum compute preserving logically mandatory candidate semantics?
Retaining mandatory observation ($0.246\text{ FP/step}$) and arbitration ($5.600\text{ FP/step}$), the minimum compute is **$109.244508\text{ FP/step}$**.

### 12. How much early failure rejection is retrospectively possible with zero lost promotions?
At exposure checkpoint $n = 7\text{ shadow observations}$, a retrospective filter discarding candidates with running utility $\le 0.0$ rejects **$58.0\%$ of eventual failures** with **$0.0\%$ false rejection of eventual promotions**, saving **$0.884542\text{ FP/step}$**.

### 13. At what exposure do eventual failures become separable?
Failures become separable starting at **$n = 7\text{ shadow observations}$** ($35\text{ stream steps}$). Prior to $n=5$, filter adaptation transients cause true delays to have temporarily negative or near-zero utility, making early separation impossible without false negatives.

### 14. Are eventual successes identifiable earlier?
Yes; $\approx 25\%$ of promoted candidates achieve utility above $\theta_{\text{promote}}$ by $n = 10$, and $\approx 62\%$ by $n = 12$.

### 15. Would earlier promotion actually save compute after counting earlier live execution?
**NO; IT INCREASES TOTAL COMPUTE.** Promoting a candidate earlier saves shadow probation work ($0.033\text{ FP/step}$), but adds live filter execution earlier ($+1$ active linear tap $= +2.0\text{ FP/step}$ over the remaining stream steps), resulting in a net compute penalty of **$+0.152\text{ FP/step}$**.

### 16. Which tasks consume the most probation compute?
Tasks with high structural ambiguity: $I_2$ (static nonlinear control, $2.068\text{ FP/step}$ failed probation), $I_6$ (continuous latent state, $2.029\text{ FP/step}$), and $I_{11}/I_{12}$ (switching tasks, $1.948 / 1.946\text{ FP/step}$).

### 17. Does I2 create substantial useless probation?
**YES.** $I_2$ generates the highest candidate birth rate ($104.87\text{ births/run}$) and the highest failed probation compute ($2.068\text{ FP/step}$), as nonlinear approximation errors trigger false correlation threshold crossings.

### 18. How much of I11/I12 latency is due to probation rather than search?
On $I_{11}$ ($286\text{ steps}$ total latency), search queue traversal accounts for $80\text{ steps}$ ($28.0\%$), candidate probation accounts for $75\text{ steps}$ ($26.2\%$), and arbitration convergence accounts for $131\text{ steps}$ ($45.8\%$). Probation contributes materially to adaptation latency.

### 19. What fraction of the remaining 11-FP deficit is addressable by candidate/probation policy?
At most **$16.06\%$** is theoretically addressable by eliminating failed probation ($1.77\text{ FP/step}$), and only **$8.03\%$** ($0.88\text{ FP/step}$) is plausibly addressable via early rejection.

### 20. Would a future decision rule's own overhead erase the saving?
If a complex sequential test (e.g. SPRT with log-likelihood tracking, costing $\approx 0.25\text{ FP/step}$) is deployed, it would erase $\approx 30\%$ of the $0.88\text{ FP/step}$ saving. A simple deterministic check ($0.002\text{ FP/step}$) preserves virtually all savings.

### 21. Is fixed two-stage probation sufficient in principle?
**YES.** A simple two-stage screen (check $U \le 0.0$ at $n=7$; full evaluation at $n=15$) achieves $95\%$ of the theoretical early-rejection savings without statistical overhead.

### 22. Would sequential/anytime-valid evidence be potentially useful?
Conceptually useful for formal error guarantees, but practically unviable due to non-i.i.d. violation and floating-point computational overhead.

### 23. Is adaptive thresholding actually necessary?
**NO.** Retrospective curves show that eventual failures are separable using the frozen threshold $\theta = 0.0$. Changing $\theta_{\text{promote}}$ distorts model-selection semantics.

### 24. Is CANDIDATE-PROBATION-COST-01 scientifically justified?
**NO.** It is not justified as a resource-restoration stage because it cannot close the compute deficit.

### 25. If not, which subsystem should be investigated next?
The project must investigate the actual resource sinks:
1. **Arbitration Decimation** (`LEBRE-V0.2-ARBITRATION-COST-DECOMPOSITION-01`): Decimating arbitration from $K=2.5$ to $K=10$ saves $\approx 4.2\text{ FP/step}$.
2. **Base Recurrent Gating** (`LEBRE-V0.2-RECURRENT-LIVE-COST-RECONCILIATION-01`): Gating quiescent recurrent shadow execution ($20.20\text{ FP/step}$) offers $>10\text{ FP/step}$ leverage.
3. **Live Filter Compaction**: Reducing active linear filter taps ($75.47\text{ FP/step}$).

---

## Section 5: Epistemic Sign-Off

This report, all associated CSV datasets, and cryptographic manifests are sealed under stage `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`.
