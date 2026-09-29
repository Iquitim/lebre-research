# Forensic Runtime Trace: Probation Semantics and Execution

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Target:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Executive Forensic Summary

This audit definitively resolves the apparent discrepancy between historical LEBRE documentation ($T_{\text{prob}} = 50$), the parent multirate report narrative ($T_{\text{probation}} = 300$), and the executable code.

### Definitive Findings:
1. **Executed Runtime Value:** The actual condition executed in the Python simulation runner during both DEV and FINAL confirmatory phases was strictly:
   $$\text{candidate\_obs\_count} \ge 15$$
2. **Origin of the Number 300:** In `scratch/run_v02_multirate_experiments.py`, line 412 and line 415 implement structural eviction protection (stream step warmup):
   ```python
   if len(self.active_taps) > 0 and self.step_count > 300 and self.ema_G_D_B < 0.005:
   if self.active_rec is not None and self.step_count > 300 and self.ema_G_R_B < 0.008:
   ```
   During the compilation of `FINAL_CANDIDATE_FREEZE.md` (Section 3, Line 49) and `SHADOW_MULTIRATE_FINAL_REPORT.md` (Line 49), narrative text erroneously transcribed this stream warmup step count ($300$) into the candidate probation exposure requirement, stating:
   *"candidate shadow exposures (`candidate_shadow_exposures`) were tracked and required to reach $T_{\text{probation}} = 300$ actual shadow exposures"*.
3. **Empirical Event Trace Proof (Level 1 Authority):** In `FIRST_DIVERGENCE_TRACE.csv`, at stream step $t=15$, model $M_0$ (continuous shadow cadence, $K_{\text{obs}}=1$) promoted its recurrent unit (`active_rec_m0 = 1`). Because each stream step under $M_0$ executed exactly one shadow observation, the candidate accumulated exactly 15 exposures at $t=15$. Had the runtime threshold been 300, promotion at step 15 would have been mathematically impossible.
4. **Governance Verdict:** The root cause is classified as **`TPROB_REPORTING_ERROR_ONLY`**. The executed runtime code strictly inherited the binding parent T3 threshold ($15$ shadow observations) from `LEBRE-V0.2-SHADOW-RENT-GATE-01`. Therefore, the single-intervention invariant was **NOT violated** at runtime, and the causal validity of the multirate experiment is **INTACT**.

---

## 2. Static Code Trace in Executable Runner

**Target File:** `scratch/run_v02_multirate_experiments.py`  
**Execution Context:** Function `run_multirate_step(...)` in candidate class `MultirateLEBRECandidate`

### 2.1 Counter Initialization and Increment
- Candidate birth: Candidate structure dictionary is instantiated with:
  ```python
  'obs_count': 0, 'stream_age': 0, 'evidence': 0.05
  ```
- Recurrent candidate initialization (Line 96):
  ```python
  self.rec_obs_count = 0
  ```
- Incrementation rule (Lines 284, 326): Counter increments **strictly when shadow observation occurs** (governed by $K_{\text{obs}}$):
  ```python
  self.rec_obs_count += 1
  best_cand['obs_count'] += 1
  ```
  Candidate age is thus expressed in `SHADOW_OBSERVATIONS`, not stream steps.

### 2.2 Exact Runtime Promotion Condition
The candidate promotion logic is executed at lines 424 and 435:
```python
# Line 424 (Dynamic Delay Tap Promotion):
if b_cand['evidence'] > 0.02 and b_cand['obs_count'] >= 15:
    self.active_taps[b_cand['tap_idx']] = ...

# Line 435 (Recurrent State Promotion):
if self.active_rec is None and self.rec_evidence > 0.02 and self.rec_obs_count >= 15:
    self.active_rec = {'w_rec': self.w_rec_cand.copy(), ...}
    self.rec_obs_count = 0
```
Identical checks are duplicated across candidate branches at lines 446, 453, 465, 476, 490, 501. In all instances, the numerical constant is `15`.

### 2.3 Counter Reset Rule
Upon promotion or eviction:
```python
self.rec_obs_count = 0
```
For dynamic delay taps, the candidate is excised from `self.provisional_cands` and instantiated into `self.active_taps`.

---

## 3. Physical & Algorithmic Implications

Because candidate observation cadence is decimated ($K_{\text{obs}} = 5$ for candidate evaluations in $M_1$):
- In $M_0$ ($K_{\text{obs}} = 1$): 15 shadow observations require $15 \times 1 = 15$ stream steps.
- In $M_1$ ($K_{\text{obs}} = 5$): 15 shadow observations require $15 \times 5 = 75$ stream steps.

This decimation naturally stretches stream-time probation, which was explicitly anticipated in Section 88 of `SHADOW_MULTIRATE_PROTOCOL.md`:
> *"Decimating candidate observation inherently stretches stream probation time, protecting young candidates from premature promotion while reducing evaluation compute."*

The observed delay in promotion under $M_1$ (e.g. $+79.7$ steps on $I_{11}$ and $+633.7$ steps on $I_{12}$) was caused directly by the clock decimation ($K_{\text{obs}} = 5, K_{\text{probe}} = 2$), not by a threshold change to 300.

---

## 4. Conclusion

The reporting error in `FINAL_CANDIDATE_FREEZE.md` and `SHADOW_MULTIRATE_FINAL_REPORT.md` is corrected via formal erratum. No corrective simulation is required because the executed code performed the correct, authorized, parent-inherited intervention.
