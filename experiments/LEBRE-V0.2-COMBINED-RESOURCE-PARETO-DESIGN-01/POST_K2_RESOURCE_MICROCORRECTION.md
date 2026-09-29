# Post-K2 Resource Microcorrection & Lineage Reconciliation

**Audited Baseline:**
- $C_0$ Grand Mean Total Online Compute: **`111.236118 FP/step`**
- $C_2$ Grand Mean Total Online Compute: **`101.023283 FP/step`**
- Authoritative Compute Saving: **`10.212835 FP/step`** ($-9.1812\%$)
- Strict Budget Ceiling: **`100.000000 FP/step`**
- Strict Resource Deficit: **`1.023283 FP/step`**

---

## 1. Resolution of the Candidate-Saving Discrepancy ($0.010659$ vs $0.011259$)

A forensic audit of inherited documentation revealed a narrative discrepancy between two values:
- Narrative text in the seal audit final report (Q25) stated: `"candidate saving = 0.011259 FP/step"`.
- Machine-readable tables (`K2_RESOURCE_SEAL_RECONCILIATION.csv`) recorded: `"CANDIDATE_DIRECT_FP saving = 0.010659 FP/step"`.

### Forensic Reconstruction
1. **Level-1 Empirical Truth:**
   - $C_0$ Candidate Direct Compute: `1.849632 FP/step`
   - $C_2$ Candidate Direct Compute: `1.838973 FP/step`
   - True Delta: `1.849632 - 1.838973 = \mathbf{0.010659	ext{ FP/step}}`.
2. **Component Closure Proof:**
   $$egin{aligned}
   	ext{Recurrent Saving} &= 9.000000	ext{ FP/step} \
   	ext{Live Saving} &= 1.201151	ext{ FP/step} \
   	ext{Search Saving} &= 0.001025	ext{ FP/step} \
   	ext{Candidate Direct Saving} &= \mathbf{0.010659	ext{ FP/step}} \
   	ext{Arbitration Saving} &= 0.000000	ext{ FP/step} \
   \hline
   \mathbf{\sum 	ext{Orthogonal Components}} &= \mathbf{10.212835	ext{ FP/step}} \
   \mathbf{	ext{Authoritative Saving}} &= \mathbf{10.212835	ext{ FP/step}} \
   \mathbf{	ext{Machine Residual}} &= \mathbf{0.0000000000000000e+00	ext{ FP/step}}
   \end{aligned}$$
3. **Origin of the $0.011259$ Value:**
   In an early drafting iteration, search residuals and candidate differences were tentatively aggregated before exact orthogonal decomposition ($0.021317 - 0.010058 = 0.011259$). Inserting $0.011259$ into the narrative created an unclosed arithmetic residual of $+0.000600	ext{ FP/step}$ ($10.213435 
e 10.212835$).
4. **Authoritative Ruling:**
   The true, verified candidate direct saving is **`0.010659 FP/step`** (`0.01065873015873`).
   The narrative value $0.011259$ is formally retired as a drafting relic.
   The mathematical residual closes to **`0.000000 FP/step`**.

---

## 2. Decomposition of Candidate Subsystem Operations

The candidate subsystem is decomposed into orthogonal constituents:
- **`CANDIDATE_DIRECT_OBSERVATION_FP`**: Evaluated every $K_{	ext{cand\_obs}}=5$ steps for provisional candidates ($2.0	ext{ FP}$ per query).
- **`CANDIDATE_LEARNING_FP`**: Evaluated every $K_{	ext{cand\_learn}}=10$ steps for provisional candidates ($6.0	ext{ FP}$ LMS update per candidate).
- **`CANDIDATE_PROMOTION_CHECK_FP`**: Logical evaluation inside arbitration check (`evidence > 0.02, obs_count >= 15`), costing $0	ext{ FP}$.
- **`CANDIDATE_DESCENDANT_ARBITRATION_FP`**: Counterfactual gain evaluation and EMA filtering, costing $28.0	ext{ FP}$ every $K_{	ext{arb}}=5$ steps ($5.600000	ext{ FP/step}$).
- **`CANDIDATE_DESCENDANT_TOTAL_FP`**: Direct ($1.838973$) + Arbitration ($5.600000$) = $7.438973	ext{ FP/step}$.

Because arbitration frequency and parameters were identical between $C_0$ and $C_2$ ($K_{	ext{arb}}=5$), arbitration saving was identically $0.000000	ext{ FP/step}$. Consequently:
$$\Delta 	ext{CANDIDATE\_DESCENDANT\_FP} \equiv \Delta 	ext{CANDIDATE\_DIRECT\_FP} = \mathbf{0.010659	ext{ FP/step}}.$$

---

## 3. Epistemic Correction of "Robust Headroom" Terminology

Historical audit notes informally stated: `"K_arb=10 provides 1.776717 FP robust headroom"`.
Under strict scientific software governance, this statement is epistemically imprecise.

**Mandatory Formal Wording:**
> `"Under static direct-cost projection, K_arb=10 would provide approximately 1.776717 FP/step of headroom before behavioral and downstream occupancy effects."`

Until the combined candidate is simulated concurrently against paired references on a fresh cohort, true empirical headroom cannot be claimed.
$$\mathbf{	ext{ROBUST\_HEADROOM} = 	ext{NOT\_ESTABLISHED}}.$$
