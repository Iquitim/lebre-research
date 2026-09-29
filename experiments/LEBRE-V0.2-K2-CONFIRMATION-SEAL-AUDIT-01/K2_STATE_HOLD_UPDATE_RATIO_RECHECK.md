# State Trajectory Distortion & Update/Hold Ratio Audit

**Audited Telemetry:** Synchronized latent state traces $h_t(C_0)$ vs $h_t(C_2)$ across all 420 paired runs ($2,520,000$ evaluated steps).

---

## 1. Authoritative State Distortion Metrics
- **Grand Mean MAE:** `0.343444`
- **Grand Mean 95th Percentile Deviation (P95):** `0.981762`
- **Grand Mean Peak Deviation (Max):** `2.457191`
- **Update-Step Mean MAE ($t \equiv 0 \pmod 2$):** `0.383609`
- **Hold-Step Mean MAE ($t \equiv 1 \pmod 2$):** `0.303278`

---

## 2. Lineage of the Reported Ratio `0.761` (F15)
Direct division of grand means yields:

$$R_{\text{grand}} = \frac{\text{Mean}(MAE_{\text{hold}})}{\text{Mean}(MAE_{\text{update}})} = \frac{0.303278}{0.383609} = \mathbf{0.790592} \approx \mathbf{0.791}$$

However, in `generate_k2_confirmation_outputs.py` line 396 and 808, the ratio was computed per-task and then averaged across tasks:

$$R_{\text{task\_avg}} = \frac{1}{14} \sum_{i=1}^{14} \frac{MAE_{\text{hold}, i}}{MAE_{\text{update}, i}} = \mathbf{0.761409} \approx \mathbf{0.761}$$

**Conclusion:** Both numbers are arithmetically valid under their respective definitions. The discrepancy arose from reporting the average of task ratios ($0.761$) without labeling it as distinct from the ratio of pooled grand means ($0.791$).

---

## 3. Zero-Order-Hold Theoretical Match Audit (F16 / F40)
- **Parent Claim:** The report stated that the ratio `0.761` "exactly matches the theoretical profile of a zero-order hold filter."
- **Audit Verification:** An exhaustive search of all parent artifacts, derivations, and historical stages revealed **zero theoretical derivation** predicting an update/hold ratio of $0.761$.
- **Verdict:** `ZERO_ORDER_HOLD_THEORETICAL_RATIO_DERIVED = NO`.
- The claim must be downgraded from "theoretical match" to `DESCRIPTIVE_OBSERVATION`.

---

## 4. State Path vs Behavioral Distortion (F17 / F41)
- State trajectory deviation is clearly present ($MAE = 0.343444$, $P95 = 0.981762$).
- However, all preregistered predictive non-inferiority margins and critical temporal mechanisms passed unconditionally.
- **Verdict:** `STATE_PATH_DIFFERENCE_PRESENT = YES`, `BEHAVIORALLY_UNACCEPTABLE_STATE_DISTORTION = NO`.
