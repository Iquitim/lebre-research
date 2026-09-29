# Queue Causal Wording Corrigendum & Epistemic Calibration
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Authority Level: Level 3 (Sealed Forensic Corrigendum)

---

## 1. Epistemic Problem Formulation

In `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01` (Section 4.2 of the Final Report), the causal attribution of model $M_1^*$'s superior NMSE over reference $R_1$ was formulated as:
> *"The true causal driver of $M_1^*$'s accuracy gain was its $2\times$ faster queue sweep speed ($80\text{ steps}$ vs $160\text{ steps}$ in $R_1$), boosting true delay discovery recall from $66.55\%$ to $76.31\%$."*

Under strict scientific causal inference standards, declaring an empirical relationship as an established "causal driver" requires either:
1. A randomized controlled trial / isolated parameter ablation holding all other algorithmic factors strictly invariant; or
2. A formal causal graph with verified unconfoundedness.

---

## 2. Audit of Existing Ablations

An audit of all parent simulation runs across `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/` and `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/` was conducted to determine whether an isolated queue-speed ablation was ever executed.

### Findings:
- In Phase 2 DEV, model candidates differed across multiple simultaneous architectural dimensions:
  - Table capacity ($H \in \{16, 32, 64\}$)
  - Probe batch size ($B \in \{2, 4, 8\}$)
  - Probing cadence ($K_{\text{probe}} \in \{1, 2, 4\}$)
  - Eviction and replacement heuristics
- Reference model $R_1$ operated as a dense multirate grid with $B=2, K=2$ across $160$ cells ($160\text{ steps}$ per cycle).
- Model $M_1^*$ operated as a compact frontier with $B=4, K=2$ across $160$ cells ($80\text{ steps}$ per cycle), but also utilized an active candidate table of size $H=32$ with structural pointer indexing.
- At no point was a dedicated ablation performed where table structure, memory footprint, and candidate tracking were held 100% constant while *only* queue sweep speed was varied.

### Certified Finding:
$$\mathbf{QUEUE\_SPEED\_CAUSAL\_ABLATION\_EXISTS = NO}$$

---

## 3. Binding Epistemic Wording Correction

In accordance with LEBRE Scientific Governance, all reports, summaries, and downstream references must amend the causal assertion as follows:

### Superseded Formulation:
> ❌ *"The true causal driver was faster traversal."*

### Certified Binding Formulation:
> ✅ **"Faster traversal is the primary mechanistically supported explanation under the current evidence."**

### Epistemic Status Categorization:
- **`FASTER_QUEUE_TRAVERSAL`:** `SUPPORTED_MECHANISTIC_EXPLANATION`
- **`ISOLATED_CAUSAL_EFFECT`:** `NOT_ESTABLISHED`

While the mathematical fact that $M_1^*$ visits coordinates twice as frequently as $R_1$ ($80$ vs $160$ steps) strongly correlates with the observed increase in delay promotion recall ($76.31\%$ vs $66.55\%$), isolating this effect from other compact frontier mechanisms requires a future controlled ablation.
