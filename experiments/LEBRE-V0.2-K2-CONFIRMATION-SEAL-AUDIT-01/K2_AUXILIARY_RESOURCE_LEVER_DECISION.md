# Auxiliary Resource Lever Feasibility & Decision

**Audited Baseline:** $C_2\text{ Mean Total Compute} = \mathbf{101.023283\text{ FP/step}}$  
**Audited Baseline:** $C_2	ext{ Mean Total Compute} = \mathbf{101.023283	ext{ FP/step}}$  
**Strict Deficit to Budget (<= 100.0 FP):** $\mathbf{1.023283	ext{ FP/step}}$

---

## 1. Quantitative Headroom Targets
To ensure that a future intervention does not merely land at $99.99	ext{ FP/step}$ with zero margin against stochastic jitter or overhead, target savings are defined:

- **Strict Closure ($100.00	ext{ FP}$):** Required Net Saving = $\mathbf{1.023283	ext{ FP/step}}$
- **$0.5	ext{ FP}$ Headroom ($99.50	ext{ FP}$):** Required Net Saving = $\mathbf{1.523283	ext{ FP/step}}$
- **$1.0	ext{ FP}$ Headroom ($99.00	ext{ FP}$):** Required Net Saving = $\mathbf{2.023283	ext{ FP/step}}$
- **$2.0	ext{ FP}$ Headroom ($98.00	ext{ FP}$):** Required Net Saving = $\mathbf{3.023283	ext{ FP/step}}$

---

## 2. Re-evaluation of Early Candidate Rejection (F25 / F26 / F27 / F51 / F52)
- **Previous Study:** `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`
- **Reported Retrospective Upper Bound:** $\mathbf{0.884542\text{ FP/step}}$ (zero-false-rejection at checkpoint $n=7$).
- **Naive Additive Balance:**
  $$101.023283 - 0.884542 = \mathbf{100.138741\text{ FP/step}} > 100.000000\text{ FP/step}$$
- **Forensic Adjudication:**
  - Even assuming 100% of the retrospective saving materializes with zero implementation overhead, $C_2 + \text{Early Rejection}$ remains **above budget** by $+0.1387\text{ FP/step}$.
  - Under realistic decision overhead ($pprox 0.05\text{ FP/step}$), the net saving drops to $pprox 0.8345\text{ FP/step}$, leaving a deficit of $+0.1887\text{ FP/step}$.
  - **Verdict:** `EARLY_REJECTION_ALONE_CAN_CLOSE_K2_GAP = NO`.
  - The parent recommendation (Q19) that early rejection is sufficient to close the gap is **arithmetically refuted**.

---

## 3. Alternative Lever: Arbitration Decimation ($K_{\text{arb}} = 5 \to 10$)
- **Mechanism:** Decimating candidate-to-live arbitration from every 5 steps to every 10 steps.
- **Analytical Gross Saving:**
  $$\frac{28.0}{5} - \frac{28.0}{10} = 5.60 - 2.80 = \mathbf{2.800000\text{ FP/step}}$$
- **Net Projected Compute:**
  $$101.023283 - 2.800000 = \mathbf{98.223283\text{ FP/step}}$$
- **Headroom Provided:** Provides $\mathbf{1.776717\text{ FP/step}}$ of clearance below the strict $100.0\text{ FP}$ ceiling!
- **Behavioral Risk:** Decimating arbitration may slightly delay tap promotion; however, switching latency guardrails ($\le +50$ steps) provide substantial margin.

---

## 4. Live Linear Optimization Warning (F30 / F56)
- **Base Live Mass:** $74.483266\text{ FP/step}$ (largest single component).
- **Proven Removable Waste:** $\mathbf{0.000000\text{ FP/step}}$.
- **Verdict:** Base live linear filtering is the primary predictive foundation of the model. Modifying it without empirical proof of waste is strictly forbidden.
