# K=5 Path Distortion Mechanism

**Audited Issue:** Empirical proof of recurrent state pathwise distortion.

### Quantitative Distortion Evidence:
- Mean Absolute Hidden State Deviation: **0.5810**
- 95th Percentile Deviation: **1.6186**
- Maximum Instantaneous Deviation: **4.5112** (on Task $I_7$)

### Mechanistic Impact by Task:
1. **Continuous Latent Integrator ($I_6$):**
   - True underlying dynamics require continuous phase integration. Holding state constant for 5 consecutive timesteps introduces a discrete staircase approximation with 5-step phase lag.
   - Result: $\Delta \text{NMSE} = +0.1013$.
2. **Quiescent Continuous State ($I_7$):**
   - In quiescent decay and reactivation, holding state frozen prevents natural exponential decay during silence, injecting spurious residual energy.
   - Result: $\Delta \text{NMSE} = +0.0982$.
3. **Hybrid Dual Complementarity ($I_9$):**
   - Recurrent unit provides phase-shifted orthogonal information to discrete delay taps. Decimating the recurrent state destroys this orthogonality, causing $G_{R|B+D} < 0$.
