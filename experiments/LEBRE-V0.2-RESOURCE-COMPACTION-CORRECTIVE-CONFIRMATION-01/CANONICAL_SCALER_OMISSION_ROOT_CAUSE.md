# Forensic Root-Cause Analysis: Omission of Online Scaler Update in Resource Compaction Harness

**Document ID:** `LEBRE-V0.2-CORRECTIVE-ROOT-CAUSE-01`  
**Parent Study:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Forensic Audit:** `LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01`  
**Status:** CONFIRMED & DOCUMENTED  

---

## 1. Executive Summary

During the forensic audit of the resource compaction study (`experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01`), an algorithmic discrepancy was uncovered between the canonical $T_3$ implementation (`IntegratedLEBREModel` in `scratch/run_v02_integration_experiments.py`) and the experimental compaction harness (`CompactedLEBREModel` in `scratch/run_v02_resource_compaction_experiments.py`).

Specifically, line 559 of `scratch/run_v02_integration_experiments.py`:
```python
self.scaler.update(x_raw, self.live_res)
```
was inadvertently omitted from `CompactedLEBREModel.step()` in `scratch/run_v02_resource_compaction_experiments.py`.

As a direct consequence:
1. In both $C_0$ (FP32 baseline) and $C_1$ (FP16 compaction candidate), the causal standard scaler was never updated (`scaler.count` remained 0, `scaler.mean` remained $\mathbf{0}$, and `scaler.var` remained $\mathbf{1}$).
2. The normalized feature vector `x_norm` passed to the base predictor and ring buffer was simply $x_{\text{raw}} / \sqrt{1 + 10^{-4}}$ rather than dynamically standardized data.
3. The computational accounting for online standard deviation updating ($4D = 20.0$ FLOPs/step and $16D = 80$ Bytes memory traffic) was omitted from `live_fp_flops` in both arms.

While $C_0$ and $C_1$ remained strictly symmetric with respect to each other (preserving internal validity for the isolated question of FP16 numerical stability under static scaling), neither arm executed the true canonical $T_3$ pipeline. This corrective study restores canonical causal scaling to both arms, verifies canonical reference parity for $C_0$, and evaluates FP16 compaction inside the true, uncompromised $T_3$ architecture.

---

## 2. Line-by-Line Code Comparison

### 2.1 Canonical Implementation (`IntegratedLEBREModel.step`)
In `scratch/run_v02_integration_experiments.py` (lines 550–570):
```python
550:         # Track dual active occupancy
551:         has_lag = len(self.active_taps) > 0
552:         has_rec = self.active_rec is not None
553:         if has_lag and has_rec:
554:             self.dual_active_steps += 1
555:             if decision == "REDUNDANT" or (self.ema_G_D_BR <= self.theta_tol and self.ema_G_R_BD <= self.theta_tol):
556:                 self.redundant_dual_steps += 1
557:                 
558:         # Scaler update
559:         self.scaler.update(x_raw, self.live_res)
560:         
561:         # Structural state summary
562:         if has_lag and has_rec:
563:             curr_state = "BOTH"
564:         elif has_lag:
565:             curr_state = "LAG"
566:         elif has_rec:
567:             curr_state = "RECURRENT"
568:         else:
569:             curr_state = "NONE"
```

### 2.2 Parent Compaction Harness (`CompactedLEBREModel.step`)
In `scratch/run_v02_resource_compaction_experiments.py` (lines 328–344):
```python
328:         # State tracking
329:         has_lag = len(self.active_taps) > 0
330:         has_rec = self.active_rec is not None
331:         if has_lag and has_rec:
332:             allocated_state = "BOTH"
333:             self.dual_active_steps += 1
334:             if decision == "REDUNDANT":
335:                 self.redundant_dual_steps += 1
336:         elif has_lag:
337:             allocated_state = "LAG"
338:         elif has_rec:
339:             allocated_state = "RECURRENT"
340:         else:
341:             allocated_state = "NONE"
342:             
343:         return {
344:             "loss": ell_live,
...
```
**Finding:** Between lines 335 and 336, `self.scaler.update(x_raw, self.live_res)` was completely absent.

---

## 3. Mathematical & Algorithmic Consequences

### 3.1 Causal Standard Scaler Dynamics
The canonical `CausalStandardScaler` updates online via Welford-like exponential averaging:
$$\mu_{t} = (1 - \alpha_t) \mu_{t-1} + \alpha_t x_t, \quad \alpha_t = \min(0.05, 1/t)$$
$$\sigma^2_{t} = (1 - \alpha_t) \sigma^2_{t-1} + \alpha_t (x_t - \mu_t)^2$$
When `update` is omitted:
$$\mu_t \equiv \mathbf{0}, \quad \sigma^2_t \equiv \mathbf{1}, \quad \forall t \ge 0$$
Consequently, the transformation:
$$\tilde{x}_t = \frac{x_t - \mu_t}{\sqrt{\sigma^2_t + \epsilon}}$$
operated as a fixed scaling $\tilde{x}_t \approx x_t$. On synthetic zero-mean benchmarks with unit variance, inputs were approximately unscaled, which masked the defect during superficial sanity checks. However, on non-zero mean features or non-unit variance regimes, adaptation was suppressed.

### 3.2 Resource Accounting Discrepancy
Each call to `scaler.update` executes:
- Floating-point FLOPs: $4D = 20.0$ FLOPs/step (difference subtraction, mean update, squared difference, variance update).
- Memory Traffic: $2 \times D \times 8 = 80.0$ Bytes written per step.

Because this call was omitted:
- Reported $C_0$ Live FLOPs on memoryless stream $I_1$ was $38.0$ FLOPs/step instead of canonical $58.0$ FLOPs/step ($38.0 + 20.0$).
- Reported aggregate Live FLOPs was undercounted by exactly $20.0$ FLOPs across all tasks.

---

## 4. Symmetry and Equivalence Validity of Prior Results

It is vital to state what the parent study proved and did not prove:
- **Internally Symmetric:** Because both $C_0$ and $C_1$ shared the identical omission, the paired difference $\Delta = C_1 - C_0$ tested FP32 vs FP16 correlation grid maintenance under static feature scaling. That test demonstrated that the quantization noise of FP16 does not destabilize the online correlation estimator when inputs are stationary or mildly unscaled.
- **Ecologically Incomplete:** It did **not** prove that FP16 correlation storage is robust when features undergo continuous online causal rescaling, where feature magnitudes shift dynamically as $\mu_t$ and $\sigma_t$ adapt.

---

## 5. Corrective Action Plan

1. Implement `CorrectedCanonicalLEBREModel` inheriting directly from canonical `IntegratedLEBREModel`.
2. Parameterize `corr_grid_dtype \in {np.float32, np.float16}` as the sole behavioral toggle.
3. Restore `self.scaler.update(x_raw, self.live_res)` inside the canonical `step()` method.
4. Enforce the **Canonical Reference Parity Gate**: prove that `CorrectedCanonicalLEBREModel(corr_grid_dtype=np.float32)` produces bitwise identical predictions, losses, states, and resource counts to `IntegratedLEBREModel(topology="T3")` across all 14 benchmark tasks for 6,000 steps.
5. Execute the full confirmatory protocol with fresh seeds (`DEV`: 1501..1510, `FINAL`: 1511..1540) to reconfirm FP16 equivalence under true canonical conditions.
