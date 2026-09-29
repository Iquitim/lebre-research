# Candidate Subsystem Boundary & Operational Scope
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Subsystem Boundary Definition & Cost Attribution Rules

---

## 1. Subsystem Definition & Inclusions

The **Candidate Subsystem** comprises all computational logic, memory state, and evaluation overhead causally induced by the creation, maintenance, evaluation, and disposition of temporary structural hypotheses prior to full structural promotion.

### Formal Functional Roles (10 Operations):
1. **`DISCOVERY` (Birth Logic):** Evaluating correlation threshold crossings in the search frontier and instantiating candidate tracking descriptors.
2. **`OBSERVATION` (Feature Extraction):** Extracting historical delay taps from the circular buffer and computing candidate forward output:
   $$\hat{y}_{\text{cand}}(t) = w_{\text{cand}}(t) \cdot x(t - \tau_{\text{cand}})$$
3. **`STATE_PROPAGATION`:** Advancing candidate internal lag counters and circular index offsets.
4. **`PARAMETER_LEARNING`:** Performing normalized gradient updates on candidate filter weights:
   $$w_{\text{cand}}(t+1) = w_{\text{cand}}(t) + \mu \frac{e_{\text{cand}}(t) x(t - \tau_{\text{cand}})}{\epsilon + \|x(t - \tau_{\text{cand}})\|^2}$$
5. **`COUNTERFACTUAL_SCORING`:** Evaluating counterfactual error relative to the live base model:
   $$e_{\text{cand}}(t) = y(t) - (\hat{y}_{\text{base}}(t) + \hat{y}_{\text{cand}}(t))$$
6. **`EVIDENCE_ACCUMULATION`:** Updating running utility and tracking cumulative variance reduction:
   $$U_{\text{cand}}(t) = (1 - \lambda) U_{\text{cand}}(t-1) + \lambda (e_{\text{base}}^2(t) - e_{\text{cand}}^2(t))$$
7. **`PROMOTION_DECISION`:** Checking fixed-horizon maturity ($n = T_{\text{prob}} = 15$ shadow observations) against promotion threshold $\theta_{\text{promote}}$.
8. **`DISCARD_DECISION`:** Evicting candidates that fail the promotion criterion upon reaching full probation maturity.
9. **`ARBITRATION` (Descendant Comparisons):** Computing dual candidate evaluations and competitive counterfactual gain calculations when a candidate competes with incumbent live structures.
10. **`HOUSEKEEPING`:** Managing slot pointers, metadata timestamps, and volatile table indexing.

---

## 2. Direct vs. Indirect Cost Partitioning

### 2.1 Direct Candidate Work
Direct operations are those executed exclusively by the candidate object itself during its probation lifetime:
- `candidate_obs_fp` = **$0.246148\text{ FP/step}$** (Observation, forward prediction, counterfactual error).
- `candidate_learn_fp` = **$1.598486\text{ FP/step}$** (Weight adaptation, norm calculation, step scaling).
$$\mathbf{DIRECT\_CANDIDATE\_FP} = 0.246148 + 1.598486 = \mathbf{1.844634\text{ FP/step}}$$

### 2.2 Indirect Descendant Work
Indirect operations are external system evaluations causally triggered by the existence of an active candidate:
- `candidate_arb_fp` = **$5.600000\text{ FP/step}$** (Descendant arbitration evaluations, gain margin comparisons, structure collision checks).
$$\mathbf{INDIRECT\_CANDIDATE\_DESCENDANT\_FP} = \mathbf{5.600000\text{ FP/step}}$$

### 2.3 Total Candidate Subsystem Footprint
$$\mathbf{TOTAL\_CANDIDATE\_SUBSYSTEM\_FP} = 1.844634 + 5.600000 = \mathbf{7.444633\text{ FP/step}}$$

---

## 3. Candidate-Independent Untouchable Subsystems

The remaining computational mass in model $M_1^*$ is causally independent of candidate probation and cannot be reduced by any probation policy:
1. **Base Live Linear Execution:** Fixed $5$-tap synchronous filter and mature active taps:
   $$\text{Live FP Mean} = \mathbf{75.468234\text{ FP/step}}$$
2. **Search Frontier Probing:** Evaluating $B=4$ correlation hypotheses every $K_{\text{probe}}=2$ steps:
   $$\text{Search Probe FP} = \mathbf{7.900724\text{ FP/step}}$$
3. **Base Recurrent / Shadow State:** Constant recurrent latent state stepping and background shadow tracking:
   $$\text{Base Shadow FP} = \mathbf{20.200000\text{ FP/step}}$$

### Untouchable Core Compute:
$$\text{Untouchable Base Compute} = 75.468234 + 7.900724 + 20.200000 = \mathbf{103.568958\text{ FP/step}}$$

$$\mathbf{Critical \ Identity: \ 103.568958 \ (Untouchable) + 7.444633 \ (Candidate) = 111.013591\text{ FP/step} \ (Total)}$$

Even if the entire candidate subsystem is completely eliminated, the untouchable core compute ($103.57\text{ FP/step}$) exceeds the $100.0\text{ FP/step}$ target by $+3.57\text{ FP/step}$.
