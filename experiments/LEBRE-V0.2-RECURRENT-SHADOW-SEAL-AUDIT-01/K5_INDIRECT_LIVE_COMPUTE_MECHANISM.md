# K=5 Indirect Live Compute Mechanism (Pathological Structure Loss)

**Audited Issue:** Flags F07, F08, F09 (Decomposition of the excess $10.51\text{ FP/step}$ saving).

### 1. Empirical Reality
- Direct shadow clock decimation ($18.0 \to 3.6\text{ FP}$): Saved **14.4127 FP/step** (matching projected $14.40\text{ FP}$).
- Total empirical compute drop: **24.9073 FP/step**.
- **Excess Unprojected Saving:** **10.5073 FP/step**.

### 2. Origin of Excess Saving
The entire excess saving occurred in `live_fp_mean`:
$$\text{Live Compute Drop} = 75.337063 - 64.842460 = \mathbf{10.4946\text{ FP/step}}$$

### 3. Causal Attribution
Live recurrent execution costs $34.00\text{ FP/step}$ when promoted and active.
On tasks with latent state ($I_6, I_7, I_9, I_{10}$), recurrent shadow state distortion caused:
1. Failure of candidate recurrent units to accumulate sufficient evidence for promotion.
2. Premature eviction of promoted live recurrent units due to unstable utility.
3. Live recurrent filter occupancy dropped from $30.9\%$ in $C_0$ to $0.0\%$ on $I_6$ and $I_{10}$!

### 4. Epistemic Ruling:
`INDIRECT_LIVE_SAVING_CLASSIFICATION = BEHAVIORALLY_COSTLY_STRUCTURE_LOSS`.
This compute reduction is **pathological undermodeling**, not efficiency.
