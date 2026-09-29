# Probation Unit Governance Audit: Stream Steps vs. Shadow Observations

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Context and Problem Formulation

A critical question raised in Audit Question J (Section 45–46) is whether measuring candidate probation in **actual shadow exposures** rather than **stream time** was:
- An inherited semantic rule;
- A newly introduced experimental rule; or
- Merely a bookkeeping reinterpretation.

Because decimating shadow execution ($K > 1$) decouples stream time ($t$) from candidate evaluation cycles, counting stream steps versus counting actual shadow observations produces radically different candidate lifetimes.

---

## 2. Forensic Reconstruction Across Historical Stages

1. **Canonical v0.1 (`LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`):**
   - Candidate probation was specified as $T_{\text{prob}} = 50\text{ steps}$.
   - In v0.1, shadow evaluation was strictly continuous ($K=1$), so stream steps and shadow exposures were numerically identical ($1\text{ stream step} \equiv 1\text{ shadow exposure}$).
2. **T3 Integration Design (`LEBRE-V0.2-INTEGRATION-DESIGN-01`):**
   - Continuous shadow evaluation was maintained ($K=1$). Candidates were evaluated every step.
3. **Resource Compaction (`LEBRE-V0.2-RESOURCE-COMPACTION-01`):**
   - Continuous shadow evaluation ($K=1$) was maintained. Threshold was adjusted to 15 steps to minimize transient state footprint.
4. **Shadow-Rent Governance (`LEBRE-V0.2-SHADOW-RENT-GATE-01`):**
   - **Crucial Inflection Point:** This study introduced periodic ($S_2$) and event-triggered ($S_3$) shadow gating, where the shadow subsystem was turned OFF during quiescent intervals.
   - To prevent candidate structures from maturing during periods when the shadow subsystem was completely inactive, the code explicitly incremented `cand['age']` **only when shadow evaluation executed**:
     ```python
     # scratch/run_v02_shadow_rent_governance.py:270, 326
     if shadow_active:
         self.rec_age += 1
         best_cand['age'] += 1
     ```
   - Thus, the transition from *stream-step age* to *active-shadow-exposure age* was formally introduced and sealed in `LEBRE-V0.2-SHADOW-RENT-GATE-01`.
5. **Multirate Decomposition (`LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`):**
   - `SHADOW_MULTIRATE_PROTOCOL.md` Section 87 explicitly preserved this rule:
     > *"Probation maturity ($T_{\text{prob}} = 15$ steps) must be evaluated based strictly on actual shadow exposures."*
   - Variable name was clarified in `MultirateLEBRECandidate` from generic `age` to `obs_count`.

---

## 3. Governance Verdict

- **`PARENT_PROBATION_UNIT`:** `SHADOW_OBSERVATIONS` (inherited from `LEBRE-V0.2-SHADOW-RENT-GATE-01`).
- **`MULTIRATE_PROBATION_UNIT`:** `SHADOW_OBSERVATIONS`.
- **`PROBATION_UNIT_CHANGED`:** `NO`.
- **`PROBATION_UNIT_CHANGE_AUTHORIZED`:** `YES` (Inherited from sealed Level 4 parent).
- **`SINGLE_INTERVENTION_INVARIANT`:** `PASS`.

Multirate execution did not introduce an unauthorized reinterpretation of candidate probation. The multirate study tested the decimation of shadow clocks under the exact structural lifecycle semantics established in its direct parent.
