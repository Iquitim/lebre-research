# Multirate Seal Audit: Exhaustive Root Cause Analysis

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Issue 1: Narrative Reporting of $T_{\text{probation}} = 300$

- **What Happened:** In `FINAL_CANDIDATE_FREEZE.md` (line 49) and `SHADOW_MULTIRATE_FINAL_REPORT.md` (line 49), the text stated that candidate probation required $300$ shadow exposures, while canonical v0.1 used $50$ and parent T3 used $15$.
- **Where Introduced:** During the drafting of `FINAL_CANDIDATE_FREEZE.md` following DEV screening.
- **Why Prior Checks Did Not Catch It:** Automated text linting did not check semantic consistency between narrative prose and Python variable assignments in `run_v02_multirate_experiments.py`.
- **Whether Raw Data Remain Valid:** **YES.** The Python runner strictly executed `obs_count >= 15`. Level 1 raw traces (`FIRST_DIVERGENCE_TRACE.csv`) confirm recurrent promotion at stream step 15.
- **Whether Causal Interpretation Changes:** **NO.** The multirate study tested clock decimation under the identical probation threshold ($15$) inherited from the parent. Causal interpretability is **INTACT**.
- **Whether a New Stochastic Confirmation is Necessary:** **NO.** Corrected via errata.

---

## 2. Issue 2: Conflation of Historical R2 Memory with Peak Working SRAM

- **What Happened:** The parent report labeled `HISTORICAL_R2_PERSISTENT_MEMORY_STATUS = FAIL` because maximum memory reached $1064\text{ B}$.
- **Where Introduced:** In the synthesis stage of `SHADOW_MULTIRATE_FINAL_REPORT.md`.
- **Why Prior Checks Did Not Catch It:** The term "memory $\le 1024\text{ B}$" was used colloquially across milestones without prefixing whether it applied to mean persistent model RAM or peak working SRAM.
- **Whether Raw Data Remain Valid:** **YES.** Raw occupied bytes ($970.34\text{ B}$ mean, $1064\text{ B}$ peak) are verified.
- **Whether Causal Interpretation Changes:** **YES (Governance Reclassification).** Under the binding historical R2 definition (mean persistent model RAM), LEBRE passes ($970.34 \le 1024\text{ B}$). It fails only under the v0.2 Gate 3 peak working SRAM metric.
- **Whether a New Stochastic Confirmation is Necessary:** **NO.**

---

## 3. Issue 3: Overstatement of Recurrent State Continuity ($K=1$ "Required")

- **What Happened:** The parent report claimed $K=1$ recurrent forward tracking was "strictly required" despite DEV ladders showing $K=2$ and $K=5$ had NMSE deltas of only $+0.00137$ and $+0.00286$.
- **Where Introduced:** In `COMPONENT_SENSITIVITY_PROTOCOL.md` and report Section 1.
- **Why Prior Checks Did Not Catch It:** Confirmatory candidate $M_1$ opted for $K=1$ to achieve zero predictive degradation, and the report treated this design choice as an absolute physical necessity.
- **Whether Raw Data Remain Valid:** **YES.** Ladder data in `COMPONENT_RATE_BOUNDARIES.csv` are fully reproducible.
- **Whether Causal Interpretation Changes:** **YES.** Demoted from "strictly required" to "more cadence-sensitive than learning; decimation up to K=5 is tolerated within margin".
- **Whether a New Stochastic Confirmation is Necessary:** **NO.**

---

## 4. Issue 4: Modal Logic Inversion on Residual Serial Correlation ($MR_3$)

- **What Happened:** The parent report claimed residual autocorrelation was "necessary but insufficient" for detecting temporal inadequacy, despite exhibiting $>80\%$ false negatives on delay tasks.
- **Where Introduced:** In the discussion of candidate $MR_3$ in `SHADOW_MULTIRATE_FINAL_REPORT.md`.
- **Why Prior Checks Did Not Catch It:** The colloquial use of "necessary" was conflated with "heuristically informative".
- **Whether Raw Data Remain Valid:** **YES.** DEV task results confirm poor detection across delay tasks.
- **Whether Causal Interpretation Changes:** **YES.** Corrected to "neither necessary nor sufficient; not a reliable standalone router".
- **Whether a New Stochastic Confirmation is Necessary:** **NO.**
