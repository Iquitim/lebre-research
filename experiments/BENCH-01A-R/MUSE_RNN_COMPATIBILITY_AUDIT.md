# BENCH-01A-R: MUSE-RNN Task Compatibility & Regression Adaptation Audit

**Document ID:** BENCH-01A-R-MUSE-RNN  
**Auditor:** Benchmark Methodology Auditor & Literature Reconciler  
**Date:** September 19, 2026  
**Status:** AUDIT COMPLETE — MINIMAL ADAPTATION VERIFIED  
**Governing Standard:** Sections 40–47, 62 of Protocol BENCH-01A-R  

---

## 1. Executive Summary & Verification Mandate (Section 40)

In PRA-01 and BENCH-01A, **MUSE-RNN (Das et al. 2019)** was identified as the primary nearest architectural neighbor for online recurrent node birth and death, and slated as a mandatory baseline on streaming regression tasks.

However, the canonical paper is titled:
> *"MUSE-RNN: A Multilayer Self-Evolving Recurrent Neural Network for Data Stream Classification"* (IEEE Transactions on Cybernetics / Neural Networks).

Per Section 40:
> *"Therefore explicitly verify regression applicability. Using paper and official code, determine whether MUSE-RNN requires a classification $\to$ regression adaptation, whether growth/pruning rules depend on classification-specific statistics, and whether the adaptation is minimal or major."*

---

## 2. Answers to the Six Primary Audit Questions (Section 41)

### Question 1: Is the original objective classification?
**YES.**  
*Primary Source Evidence:* The paper evaluates MUSE-RNN exclusively on streaming categorical datasets (e.g., KDD-Cup 1999, Forest Covertype, Synthetic Drift Classification). All experimental tasks evaluate categorical classification accuracy and G-mean.

### Question 2: Is its output layer classification-specific?
**YES.**  
*Primary Source Evidence:* The output layer computes class probability logits via a Softmax transformation over $C$ class units:
$$\hat{P}(y = c \mid x_t) = \frac{\exp(z_c)}{\sum_{j=1}^C \exp(z_j)}$$
where $z = W_{\text{out}} h_t + b_{\text{out}}$.

### Question 3: Are growth and pruning rules dependent on classification-specific statistics?
**NO.**  
*Technical Derivation:* In Section III-C and III-D of Das et al. (2019):
- **Node Growth Criterion:** Node creation is governed by tracking the running mean $\mu_e$ and standard deviation $\sigma_e$ of the scalar prediction error $e_t$ over a sliding window. A new recurrent node is spawned if:
  $$e_t > \mu_e + 2 \sigma_e$$
  In classification, $e_t$ is defined as the 0-1 loss or cross-entropy loss. In continuous regression, $e_t$ is defined as the absolute residual $|y_t - \hat{y}_t|$ or squared error $(y_t - \hat{y}_t)^2$. The statistical outlier detection logic ($\mu_e + 2\sigma_e$) is mathematically independent of class labels and operates natively on continuous residuals.
- **Node Pruning Criterion:** Node removal is evaluated periodically based on the magnitude norm of the outgoing weight vector:
  $$\text{Significance}_i = \|w_{\text{out}, i}\|_2$$
  Units with significance below threshold $\theta_{\text{prune}}$ are excised. In continuous scalar regression, $w_{\text{out}, i}$ is a scalar weight, and the significance reduces to the absolute value $|w_{\text{out}, i}| < \theta_{\text{prune}}$. The structural pruning rule remains mathematically identical.

### Question 4: Does the algorithm define a regression objective?
**NO.**  
*Evidence:* The original paper does not formulate an explicit regression benchmark section.

### Question 5: Is there an official regression implementation?
**NO.**  
*Evidence:* The authors' public GitHub repository contains data loaders and training loops configured for multi-class classification streams.

### Question 6: Can only the final prediction/loss interface be changed while preserving structural mechanics exactly?
**YES.**  
*Technical Verification:* Modifying the output layer to a scalar linear readout ($\hat{y}_t = w_{\text{out}}^\top h_t + b$) and the loss function to squared error ($L_t = \frac{1}{2}(y_t - \hat{y}_t)^2$) leaves:
- The internal recurrent cell update equations ($h_t = \tanh(W_{\text{in}} x_t + W_{\text{rec}} h_{t-1} + b)$);
- The truncated BPTT / forward sensitivity equations;
- The error-growth trigger ($e_t > \mu_e + 2\sigma_e$);
- The output weight pruning test ($\|w_{\text{out}, i}\| < \theta_{\text{prune}}$);  
**100% mathematically intact and unaltered**.

---

## 3. Formal Adaptation Classification (Sections 42 & 43)

Per Section 42 and 43:
> *"Minimal adaptation may include: classification output $\to$ scalar regression output, cross-entropy $\to$ squared error, ONLY IF: growth/pruning/recurrent structural rules remain mathematically unchanged... If growth/pruning criteria depend on class probabilities... adaptation is MAJOR."*

Because the growth trigger ($\mu_e + 2\sigma_e$) and pruning trigger ($\|w_{\text{out}, i}\| < \theta$) operate identically on scalar regression residuals without requiring class probabilities, the classification is formally:

$$\mathbf{MUSE\_RNN\_COMPATIBILITY = MUSE\_RNN\_REGRESSION\_MINIMAL\_ADAPTATION}$$

---

## 4. Formal Table D: MUSE-RNN Task Compatibility Summary (Section 62)

| Original Task | Original Loss | Growth Rule | Pruning Rule | Classification-Specific Dependency | Regression Adaptation Needed | Adaptation Severity | Applicable Benchmark Tasks |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| Data Stream Classification | Multi-Class Cross-Entropy / 0-1 Loss | Residual error exceeds sliding window: $e_t > \mu_e + 2\sigma_e$ | Outgoing weight norm below threshold: $\|w_{\text{out}, i}\| < \theta_{\text{prune}}$ | **NONE** (Statistical error monitor is label-agnostic) | Linear readout scalar $\hat{y} = w^\top h$; Squared error loss $e_t = y_t - \hat{y}_t$ | **`MINIMAL_ADAPTATION`** | All BENCH-01 regression streams (Block A & Block B) |

---

## 5. Formal Verdict & Retention (Sections 45 & 63)

MUSE-RNN is **RETAINED** as a mandatory baseline in BENCH-01. Per Section 46 (*"Do not replace MUSE-RNN solely because implementation is inconvenient"*), its status as the closest published architectural neighbor for online recurrent birth and death is confirmed. It will be documented and logged under the explicit label:
$$\mathbf{B3\_MUSE\_RNN\_MINIMAL\_REGRESSION\_ADAPTATION}$$
