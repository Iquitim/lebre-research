# Official Corrigendum: LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01

This document records all formal errata and corrected textual wording for the parent confirmation stage.

---

### ERR-01: Total Compute Saving Magnitude
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` lines 15, 63, 812; `K2_RESOURCE_DECOMPOSITION.csv` line 5; `K2_BOUNDARY_DECISION.md` line 32; `K2_FUTURE_COMPOSITION_ELIGIBILITY.md` line 25.
- **Original Text:** "an exact saving of $17.000\text{ FP/step}$"
- **Original Value:** `17.000`
- **Corrected Value:** `10.212835`
- **Error Class:** `STALE_INTERMEDIATE / REPORTING_ERROR`
- **Authoritative Source:** `K2_FINAL_RESULTS.csv` ($111.236118 - 101.023283 = 10.212835\text{ FP/step}$).
- **Corrected Wording:** "an authoritative total compute saving of $10.213\text{ FP/step}$ ($-9.18\%$ vs $C_0$'s $111.236\text{ FP/step}$)."
- **Scientific Impact:** Clarifies physical component accounting.
- **Requires New Simulation:** `NO`.

---

### ERR-02: Engineering Near-Miss Gate Decision
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` lines 15, 820; `K2_RESOURCE_DECISION.md`.
- **Original Text:** "classified as an OVER_BUDGET within the preregistered $\le 101.0\text{ FP}$ engineering tolerance interval... Yes. It falls strictly inside the $[100.0, 101.0]\text{ FP}$ engineering tolerance interval."
- **Original Value:** `PASS / INSIDE_TOLERANCE`
- **Corrected Value:** `FAIL / OUTSIDE_TOLERANCE`
- **Error Class:** `ROUNDING_GOVERNANCE_ERROR`
- **Authoritative Source:** `K2_FINAL_RESULTS.csv` (empirical mean $= 101.023283 > 101.000000$).
- **Corrected Wording:** "Mean total compute load is $101.023\text{ FP/step}$, strictly failing the $\le 100.0\text{ FP}$ ceiling by $+1.023\text{ FP}$ and narrowly exceeding the preregistered $\le 101.0\text{ FP}$ engineering near-miss boundary by $+0.023\text{ FP}$ at full precision."
- **Scientific Impact:** Reclassifies resource status from near-miss to narrow overage.
- **Requires New Simulation:** `NO`.

---

### ERR-03: Non-Inferiority P-Value Typo
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 1.
- **Original Text:** "$p_{{\text{NI}}} \approx 8.58e-14$"
- **Original Value:** `8.58e-14`
- **Corrected Value:** `3.4621e-11`
- **Error Class:** `P_VALUE_TRANSCRIPTION_ERROR`
- **Authoritative Source:** Level-1 paired t-test for non-inferiority ($t = -9.9798$, $df=29$).
- **Corrected Wording:** "One-sided non-inferiority against margin $+0.0100$ is confirmed with $t(29) = -9.9798, p_{{\text{NI}}} = 3.4621 \times 10^{-11}$."
- **Scientific Impact:** Eliminates p-value conflation in report.
- **Requires New Simulation:** `NO`.

---

### ERR-04: Compute/Error Correlation Interpretation
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 4 Q16.
- **Original Text:** "$r = -0.5627$ ($p = 0.0012$), confirming no perverse coupling."
- **Original Value:** `No coupling`
- **Corrected Value:** `Trade-off association`
- **Error Class:** `SIGN_INTERPRETATION_ERROR`
- **Authoritative Source:** Level-1 seed correlation ($r(\text{Saving}, \Delta\text{NMSE}) = +0.5627$).
- **Corrected Wording:** "Pearson correlation indicates that seeds with greater observed compute savings tended to exhibit greater predictive degradation ($r = +0.5627, p = 0.0012$), representing an empirical trade-off association."
- **Scientific Impact:** Accurately states empirical association.
- **Requires New Simulation:** `NO`.

---

### ERR-05: Theoretical Zero-Order Hold Ratio Claim
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 4 Q10.
- **Original Text:** "exactly matching the theoretical profile of a zero-order hold filter."
- **Original Value:** `Theoretical match`
- **Corrected Value:** `Descriptive empirical observation`
- **Error Class:** `UNSUPPORTED_THEORETICAL_MATCH`
- **Authoritative Source:** Lack of derivation in parent artifacts.
- **Corrected Wording:** "Hold steps exhibit a distortion ratio of $0.761$ relative to update steps when averaged across tasks ($0.791$ across pooled grand means), representing a descriptive empirical characteristic of state holding."
- **Scientific Impact:** Removes unproven theoretical assertion.
- **Requires New Simulation:** `NO`.

---

### ERR-06: Generalization of Failure to All $K \ge 3$
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 4 Q17.
- **Original Text:** "As established in the seal audit, $K \ge 3$ creates unrecoverable phase distortion and breaks state tracking."
- **Original Value:** `All K >= 3 fail`
- **Corrected Value:** `K=3, K=4 untested; K=5 failed`
- **Error Class:** `UNSUPPORTED_INTERPOLATION`
- **Authoritative Source:** Cadence evidence boundary table.
- **Corrected Wording:** "Higher decimation at $K=5$ previously failed confirmatory testing under HOLD_STATE. Intermediate cadences ($K=3, K=4$) remain untested."
- **Scientific Impact:** Establishes correct epistemic boundaries.
- **Requires New Simulation:** `NO`.

---

### ERR-07: Early Candidate Rejection Resource Sufficiency
- **Target Artifact:** `K2_CONFIRMATION_FINAL_REPORT.md` Section 4 Q19.
- **Original Text:** "Pair $K_{{\text{rec\_forward}}}=2$ with candidate probation decimation / early rejection in a future formal composition study [to close $\le 100$]."
- **Original Value:** `Sufficient to close gap`
- **Corrected Value:** `Insufficient alone; requires additional or alternative lever`
- **Error Class:** `FUTURE_STAGE_OVERAUTHORIZATION`
- **Authoritative Source:** Retrospective early rejection max saving ($0.8845\text{ FP}$) vs deficit ($1.0233\text{ FP}$).
- **Corrected Wording:** "Early candidate rejection alone ($0.885\text{ FP}$) is arithmetically insufficient to close the $1.023\text{ FP}$ deficit. A future composition study must evaluate an auxiliary lever with sufficient resource mass, such as arbitration decimation ($2.800\text{ FP}$ saving)."
- **Scientific Impact:** Redirects future research to a mathematically viable path.
- **Requires New Simulation:** `NO`.
