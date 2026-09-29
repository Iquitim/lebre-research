# Mechanism Attribution: Why Arbitration Decimation Failed

**Attributed Mechanism:** **`EMA_TIMESCALE_DISTORTION combined with DECISION_STALENESS`**  
**Excluded Mechanism:** `RESOURCE_BACKFILL` (Resource headroom remained ample at $+3.04\text{ FP}$).

---

## 1. Physical Anatomy of the Failure

1. **The Disproven Hypothesis:**
   It was hypothesized that because $99.55\%$ of evaluations in steady state produced no structural change, $50\%$ of evaluations could be safely skipped by moving from $K=5 \to 10$.
2. **The Mechanism Revealed by Phase 0 & Telemetry:**
   Holding the per-event smoothing factor $\alpha = 0.02$ fixed doubled the effective memory time constant in physical stream steps:
   $$\tau_{\text{stream}}: 247.48 \to \mathbf{494.97\text{ stream steps}}.$$
3. **The Behavioral Cascade:**
   - On tasks requiring dynamic discovery or switching of discrete delay taps ($I_3, I_4, I_5, I_8, I_{10}, I_{12}$), the conditional gain filter $\text{EMA}\_G\_D\_B$ accumulated evidence at half the stream-time rate.
   - On $I_{12}$ (`Latent_To_Delay`), after the changepoint at $t=3000$, the discrete gain took an additional $\approx 168\text{ steps}$ to exceed $\theta_{\text{tol}} = 0.01$.
   - This delayed tap promotion resulted in an extended error transient, causing switching recovery latency to jump by $+182.43\text{ steps}$ and NMSE to degrade.
   - Slower evaluation reduced tap promotions across all tasks from $2.205$ to $1.776$ per run, creating **behaviorally costly under-modeling**.
