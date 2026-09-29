# Root Cause Analysis: Audited Reporting Discrepancies

---

### RCA-01: Reported "17.000 FP" Total Compute Saving
- **Original Claim:** "an exact saving of $17.000\text{ FP/step}$"
- **First Artifact:** `K2_RESOURCE_DECOMPOSITION.csv` line 5, `K2_CONFIRMATION_FINAL_REPORT.md` line 15.
- **Authoritative Source:** `K2_FINAL_RESULTS.csv` ($111.236118 - 101.023283 = 10.212835\text{ FP/step}$).
- **Root Cause:** `generate_k2_confirmation_outputs.py` hardcoded a stale theoretical number (`34.0 -> 17.0`) from an earlier conceptual draft into the markdown template.
- **Corrected Result:** Authoritative compute saving is exactly $10.212835\text{ FP/step}$ ($-9.18\%$).
- **Scientific Impact:** None on behavioral results; establishes correct physical resource accounting.
- **Governance Impact:** Requires textual erratum. No new stochastic simulation required.

---

### RCA-02: Engineering Near-Miss Gate Declared PASS via Rounding
- **Original Claim:** "Falls strictly inside the $[100.0, 101.0]\text{ FP}$ engineering tolerance interval."
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` line 820, `K2_RESOURCE_DECISION.md`.
- **Authoritative Source:** `K2_FINAL_RESULTS.csv` (mean total FP = $101.023283$).
- **Root Cause:** The author observed $101.023$, rounded to one decimal place ($101.0$), and evaluated the gate against the rounded display string rather than full precision.
- **Corrected Result:** $101.023283 > 101.000000$. The formal near-miss gate fails by $+0.023283\text{ FP/step}$.
- **Scientific Impact:** Reclassifies the resource status from near-miss to narrow overage.
- **Governance Impact:** Primary outcome relabeled to `K2_BEHAVIOR_CONFIRMED_RESOURCE_STATUS_RECLASSIFIED`.

---

### RCA-03: Transcription Typo in Non-Inferiority P-Value (`8.58e-14`)
- **Original Claim:** "$p_{{\text{NI}}} \approx 8.58e-14$"
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 1.
- **Authoritative Source:** `scipy.stats.t.cdf(t_ni, df=29)` where $t_{{\text{NI}}} = -9.9798$, yielding $p = 3.4621 \times 10^{-11}$.
- **Root Cause:** Conflation between the test against zero ($p = 8.58 \times 10^{-4}$) and the non-inferiority test, combined with an exponent transcription typo.
- **Corrected Result:** $p_{{\text{NI}}} = 3.4621 \times 10^{-11}$; $p_{{\text{zero}}} = 8.5794 \times 10^{-4}$.
- **Scientific Impact:** Both tests pass with extreme statistical significance; clarifies distinct inferential questions.
- **Governance Impact:** Textual corrigendum.

---

### RCA-04: Compute/Error Correlation Sign & Interpretation
- **Original Claim:** "$r = -0.5627$, confirming no perverse coupling."
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` line 832.
- **Authoritative Source:** Level-1 seed-level paired correlation between compute change and NMSE change.
- **Root Cause:** Overlooking that compute difference $\Delta\text{FP}$ is negative for savings.
- **Corrected Result:** $\text{corr}(\text{Saving}, \Delta\text{NMSE}) = +0.5627$ ($p = 0.0012$). Higher compute saving was associated with higher predictive degradation.
- **Scientific Impact:** Clarifies the empirical trade-off between decimation and predictive degradation.
- **Governance Impact:** Textual corrigendum.

---

### RCA-05: Theoretical Zero-Order Hold Ratio Claim
- **Original Claim:** "Hold steps exhibit a distortion ratio of 0.761... exactly matching the theoretical profile of a zero-order hold filter."
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` line 808.
- **Authoritative Source:** None. No mathematical derivation was performed.
- **Root Cause:** A heuristic observation was elevated to a "theoretical match" in narrative drafting.
- **Corrected Result:** Downgraded to descriptive empirical observation.
- **Scientific Impact:** Prevents unsubstantiated theoretical claims from entering the literature.
- **Governance Impact:** Textual corrigendum.

---

### RCA-06: Overgeneralized Failure Claim for $K \ge 3$
- **Original Claim:** "$K \ge 3$ creates unrecoverable phase distortion and breaks state tracking."
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` line 836.
- **Authoritative Source:** $K=3$ and $K=4$ were never run in this branch; only $K=5$ failed.
- **Root Cause:** Heuristic interpolation treating failure at $K=5$ as proof that $K=3$ and $K=4$ must fail.
- **Corrected Result:** $K=3$ and $K=4$ are strictly `UNTESTED`.
- **Scientific Impact:** Preserves accurate epistemic boundaries.
- **Governance Impact:** Epistemic corrigendum.

---

### RCA-07: Early Candidate Rejection Insufficiency to Close Resource Gap
- **Original Claim:** "Pair $K_{{\text{rec\_forward}}}=2$ with candidate probation decimation / early rejection in a future formal composition study [to close $\le 100$]."
- **First Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` line 844.
- **Authoritative Source:** Retrospective max saving is $0.8845\text{ FP/step}$; current deficit is $1.0233\text{ FP/step}$.
- **Root Cause:** Recommending early rejection qualitatively without checking additive arithmetic.
- **Corrected Result:** Early candidate rejection alone is arithmetically insufficient to close the gap. An additional lever (e.g. arbitration decimation) is required.
- **Scientific Impact:** Prevents executing an under-resourced composition study doomed to fail the strict budget.
- **Governance Impact:** Recommendation updated.
