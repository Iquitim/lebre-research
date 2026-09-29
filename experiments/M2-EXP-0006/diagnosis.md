# M2-EXP-0006 — Diagnostic Report & Answers to Core Questions

## 1. Context & Diagnostic Mandate

Experiment **M2-EXP-0006** was executed to answer the fundamental question:
> *Can the learner distinguish a silent-but-necessary memory from a truly obsolete memory, without using oracle regime labels?*

This experiment directly addresses the dominant failure mode isolated in M2-EXP-0005R: **premature state eviction during quiescent latch periods** ($s_t = 0$), which previously caused a 205-step rebirth penalty and degraded active recall to $35.8\%$ in Phase 4.

---

## 2. Answers to the 5 Core Questions

### Question 1 (Section 121): Can the learner distinguish quiet-but-needed from quiet-and-obsolete?
> **Answer: YES.**

**Empirical Proof**:
- In Table A, instantaneous and short-window delta loss ($\Delta L_t$) failed completely, achieving an ROC-AUC of 0.514 and a 100% false eviction rate because $s_t = 0 \implies \Delta L_t \approx 0$ regardless of regime necessity.
- In contrast, **Temporal $C \times O_{\text{struct}}$** (Channel D2) achieved an **ROC-AUC of 0.913** and **PR-AUC of 0.999** across 2,542 matched intervals.
- The key mechanistic distinction is **Structural Observability ($O_{\text{struct}} = w_{\text{state}}^2$)**:
  - In a quiescent SET/RESET regime (Q2), the state readout weight remains coupled to the output ($w_{\text{state}} \approx 1.0$), signaling that the state is structurally integrated into the predictor even when its numeric value is temporarily zero.
  - In a state-free obsolete regime (Q3), the base linear model absorbs prediction and $w_{\text{state}}$ decays toward zero.

---

### Question 2 (Section 122): Is future retention value recoverable from cheap past statistics?
> **Answer: CAUSALLY_ESTIMABLE.**

**Empirical Proof**:
- Counterfactual future horizon analysis (Table C) demonstrates that the true retention value $V_H$ over $H \ge 50$ steps is between $12.7$ and $123.6$ loss units during silent intervals, even while instant $\Delta L \approx 0$.
- This future value does **not** require sequence replay, multi-step rollouts, or BPTT.
- It is causally estimable in $O(1)$ time and $O(1)$ memory by tracking two cheap past statistics:
  1. **Temporal Controllability ($C$)**: A slow exponential moving average of driving input energy ($\alpha = 0.005$, half-life $\approx 140$ steps).
  2. **Structural Observability ($O_{\text{struct}}$)**: The squared readout weight $w_{\text{state}}^2$.
- Together, $U_{\text{ret}} = \sqrt{C \times O_{\text{struct}}}$ survives silence up to $>500$ steps (Table B) and predicts future retention value with $0.993$ recall.

---

### Question 3 (Section 123): Does state eviction require positive evidence of obsolescence?
> **Answer: YES.**

**Empirical Proof**:
- The decision cost model (Table E) reveals an extreme asymmetry:
  - **False Eviction Cost**: $C_{\text{FE}} = 9.225$ prediction regret $+ 4,920$ FLOPs $+ 205$ rebirth steps.
  - **False Retention Cost**: $C_{\text{FR}} = 0.001$ prediction regret $+ 34$ FLOPs $+ 52$ bytes.
  - **Cost Ratio**: $C_{\text{FE}} / C_{\text{FR}} \approx 9,225:1$.
- Because deleting a necessary state is over $9,000\times$ more punitive than holding a stale state, absence of utility ($\Delta L = 0$) cannot be treated as evidence of obsolescence.
- Causal Policy C2 demonstrates that eviction must be gated by **Positive Evidence of Obsolescence ($O_{\text{obs}}$)**: requiring sustained steps where the state-free base model explains the data ($e_{\text{base}}^2 \le \sigma_{\text{noise}}^2$) while input driving channels are inactive.

---

### Question 4 (Section 124): Is a two-timescale utility model necessary?
> **Answer: YES.**

**Empirical Proof**:
- A single-timescale utility rule faces an irreconcilable tradeoff:
  - If fast ($\alpha = 0.05$), it rapidly drops below the eviction threshold during quiescence (reaching $10^{-6}$ within 100 steps; Table B), triggering premature eviction.
  - If slow ($\alpha = 0.005$), it fails to detect true obsolescence when transitioning into a state-free regime, causing indefinite retention.
- A **two-timescale architecture** solves this dilemma:
  - **Fast timescale ($U_{\text{fast}}$)** governs event-driven active utility and immediate error correction.
  - **Slow timescale ($U_{\text{slow}}$ / Temporal $C \times O$)** bridges silent retention gaps.
  - **Obsolescence accumulator ($O_{\text{obs}}$)** drives timely structural eviction once the regime permanently terminates.

---

### Question 5 (Section 125): After correcting eviction, is one state still sufficient?
> **Answer: YES.**

**Empirical Proof**:
- Under Policy C2 with strictly $\text{MAX\_ACTIVE\_STATES} = 1$ and $\text{STATE\_DIM} = 1$:
  - Global MSE: **0.2815** (virtually identical to Oracle Eviction MSE of 0.2815; regret $= 0.000053$).
  - Active Recall: **90.66%** (exceeding the $90.0\%$ target and Oracle Recall of $85.75\%$).
  - Premature Evictions: **0.10 per seed** (down from $2.33$ in C0, a $95.7\%$ reduction).
  - Compute Overhead: **50.4 FLOPs/step** (well below the $60$ FLOPs budget).
- The prior apparent "capacity deficit" in M2-EXP-0005 was entirely an eviction artifact caused by premature deletion during quiescence. Once retention is protected by structural observability, a single scalar state is completely sufficient for the test benchmarks.

---

## 3. Preregistered Primary Decisions

```json
{
  "EXPERIMENT": "M2-EXP-0006",
  "TWO_TIMESCALE_RETENTION_REQUIRED": "YES",
  "POSITIVE_OBSOLESCENCE_EVIDENCE_REQUIRED": "YES",
  "STATE_EVICTION": "VALIDATED",
  "QUIESCENT_RETENTION": "SOLVED",
  "MULTI_STATE_CAPACITY_JUSTIFIED": "NOT_YET",
  "REGRET_VS_ORACLE": 0.000053,
  "PREMATURE_EVICTION_RATE_REDUCTION": "95.7%",
  "ACTIVE_RECALL": 0.9066,
  "STATUS": "SUCCESS_SECTION_133_HARD_STOP",
  "NEXT": "M2_LIFECYCLE_FREEZE_REVIEW"
}
```

---

## 4. Section 133 Hard Stop

All requirements of M2-EXP-0006 have been satisfied:
1. Two-stage evaluation completed across 30 fresh seeds `[8001..8030]`.
2. Tables A, B, C, D, E generated and verified.
3. 15-panel diagnostic figure and matched-pair figure produced.
4. Unit test suite expanded (52/52 passing).
5. All 5 core questions explicitly answered.
6. Execution halted in accordance with Section 133 Hard Stop.
