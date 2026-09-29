# HOLD_STATE Semantics & Scope Audit

**Audited Issue:** Flag F15 & F17 (Whether HOLD_STATE is the 'only valid' semantic).

### Audit Finding:
The parent report asserted that `HOLD_STATE` was standardized as the "only valid skip semantics".

### Epistemic Calibration:
1. `HOLD_STATE` is **a specific design choice** (zero-order hold), frozen in Milestone 2 to maintain causal isolation against earlier multirate baselines (D9F).
2. It is **NOT** mathematically the only valid semantic. Other legitimate candidates include:
   - Analytical decay during quiescence ($h_t = a^\Delta h_{t-\Delta}$).
   - Event-triggered state propagation.
   - Dual-rate Kalman/observer updates.
   - Linear interpolation between sparse update points.
3. Therefore, the refutation of $K=5$ under `HOLD_STATE` refutes **the fixed zero-order hold decimation strategy on the $M_1^*$ branch**, but does not prove that all sparse recurrent computation is impossible.
