# Literature Note — EMA Timescale Preservation under Arbitration Decimation (Phase E)

**Purpose.** This note motivates hypotheses, fixes terminology and names risks. It does **not** show that LEBRE is stable,
optimal or correct.

**Evidence labels.** `ESTABLISHED_EXTERNAL_RESULT` (holds in the cited work, under that work's assumptions) ·
`CONCEPTUAL_ANALOGY` (shared structure, no transfer of guarantees) · `LEBRE_SPECIFIC_HYPOTHESIS` (a claim about LEBRE that is untested or only partly tested).

**Verification status of citations.** The bibliographic metadata below (authors, venue, volume, pages, DOI) was
supplied by the stage protocol and agrees with the author's knowledge of these works. The full texts were **not**
retrieved and re-read online during this stage. Each summary is kept at the level of each paper's
well-known central contribution, and it should be checked against the source before any external publication.

---

### 1. Johnstone, Johnson, Bitmead & Anderson (1982)
*Exponential convergence of recursive least squares with exponential forgetting factor.* Systems & Control Letters 2(2):77–82. DOI 10.1016/S0167-6911(82)80014-5.

- **Established (`ESTABLISHED_EXTERNAL_RESULT`).** Under persistent excitation, RLS with forgetting factor λ < 1 converges
  exponentially. The forgetting factor weights past data geometrically (λ^k).
- **Relevance.** This is the canonical statement that a forgetting pole fixes the effective data-memory length. LEBRE's gain EMA also weights
  past evidence geometrically (q^n).
- **Not transferable.** LEBRE's EMA is a scalar first-order smoother of noisy gain samples, not an RLS estimator. None of
  the paper's convergence or excitation results apply to LEBRE's gain EMAs or to its structural decisions.

### 2. Brüggemann & Bitmead (2021)
*Exponential convergence of recursive least squares with forgetting factor for multiple-output systems.* Automatica 124:109389. DOI 10.1016/j.automatica.2020.109389.

- **Established.** Extends exponential-convergence results for RLS with forgetting to the multiple-output case.
- **Relevance.** Context only. Forgetting remains a standard, analyzable design parameter in recursive estimation.
- **Not transferable.** Any convergence guarantee. LEBRE's supervisor is a switched, threshold-driven system.

### 3. Wright (1986)
*Forecasting data published at irregular time intervals using an extension of Holt's method.* Management Science 32(4):499–510. DOI 10.1287/mnsc.32.4.499.

- **Established.** Wright extends exponential smoothing (Holt's method) to irregularly spaced observations. The
  smoothing weight is adjusted according to the elapsed time since the previous observation, rather than held as a
  fixed per-observation constant.
- **Relevance (`CONCEPTUAL_ANALOGY`).** This is the closest external precedent for the B3 manipulation. It interprets the smoothing
  parameter relative to elapsed time, which is what pole matching does for a uniform gap of K_arb stream steps.
- **Not transferable.** Forecast-accuracy properties, and trend handling (LEBRE's gain EMA has no trend component).

### 4. Cipra (2006)
*Exponential smoothing for irregular data.* Applications of Mathematics 51(6):597–604.

- **Established.** Formulates exponential smoothing for irregularly spaced time series, with time-gap-dependent smoothing
  constants, building on Wright's approach.
- **Relevance (`CONCEPTUAL_ANALOGY`).** Supports the design principle that, once the sampling gap changes, a per-sample
  smoothing constant has to be reinterpreted in elapsed time. That is exactly the E3 correction.
- **Not transferable.** Optimality or estimator-variance results, which rest on statistical models LEBRE's gain
  process has not been shown to satisfy. Note also that elapsed-time rescaling fixes the memory **length** but cannot recover
  the **observations skipped** inside the gap. That limitation is the E2 residual identified in Phase C.

### 5. Mosca & Agnoloni (2001)
*Inference of candidate loop performance and data filtering for switching supervisory control.* Automatica 37(4):527–534. DOI 10.1016/S0005-1098(00)00183-7.

- **Established.** In switching supervisory control, the supervisor chooses among candidate controllers using
  inferred performance indices computed from **filtered** data, and the choice of filtering affects which candidate is selected.
- **Relevance (`CONCEPTUAL_ANALOGY`).** LEBRE's four conditional-gain EMAs are the performance-filter state of its
  arbitration supervisor. Changing either the filter's pole (E3) or its input sampling (E2) changes supervisory selection.
- **Not transferable.** Algorithmic identity, stability or performance guarantees.

### 6. Narendra & Balakrishnan (1994)
*Improving transient response of adaptive control systems using multiple models and switching.* IEEE TAC 39(9):1861–1866. DOI 10.1109/9.317113.

### 7. Narendra & Balakrishnan (1997)
*Adaptive control using multiple models.* IEEE TAC 42(2):171–187. DOI 10.1109/9.554398.

- **Established.** Multiple-model switching schemes select a model or controller by a performance index that
  combines instantaneous and exponentially discounted past errors. The weighting and switching rules
  materially affect transient response after parameter changes.
- **Relevance (`CONCEPTUAL_ANALOGY`).** Transient behavior after a regime change depends jointly on how quickly the
  performance index forgets (E3) and on when a switch is permitted (E1).
- **LEBRE implication (`LEBRE_SPECIFIC_HYPOTHESIS`).** Restoring the forgetting timescale may not be enough if decision
  opportunities stay too sparse or the index stays too noisy. I11/I12 are the tasks most exposed.
- **Not transferable.** Stability proofs and transient bounds.

### 8. Jacobs, Jordan, Nowlan & Hinton (1991)
*Adaptive mixtures of local experts.* Neural Computation 3(1):79–87. DOI 10.1162/neco.1991.3.1.79.

- **Established.** A gating network learns to allocate responsibility among specialized expert networks.
- **Relevance (`CONCEPTUAL_ANALOGY`).** This is the conceptual precedent for a gate that assigns predictive responsibility among specialized
  representations (lag taps and the recurrent unit).
- **Not transferable.** LEBRE's arbitration is a thresholded, periodically executed, evidence-EMA rule. It is not a jointly
  trained soft gate, and no MoE result applies to it.

### 9. Multirate signal processing (standard references)
Crochiere & Rabiner (1983), *Multirate Digital Signal Processing*, Prentice-Hall. Vaidyanathan (1993), *Multirate Systems and Filter Banks*, Prentice-Hall.

- **Established.** Down-sampling by M discards M−1 of every M samples. Without appropriate prior filtering and band-limitation
  assumptions, information in the discarded samples is not recoverable. Decimation is formally the combination of filtering and down-sampling.
- **Relevance: `SUBSAMPLING ANALOGY ONLY`.** K_arb = 10 observes the gain signal at half the K5 rate. The midpoint gain g5 is
  discarded, and no change to α can recover it.
- **Not transferable / prohibited claims.** It is **not** asserted that LEBRE gain signals are band-limited, and it is **not**
  asserted that the ARB10 failure is aliasing. No spectral analysis of the gain process has been done.

### 10. Tabuada (2007)
*Event-triggered real-time scheduling of stabilizing control tasks.* IEEE TAC 52(9):1680–1685. DOI 10.1109/TAC.2007.904277.

- **Established.** Under stated conditions (input-to-state stability of the closed loop, with a state-dependent triggering rule),
  event-triggered execution preserves stability while executing the control task less often than periodic implementations, with a
  guaranteed positive minimum inter-execution time.
- **Relevance.** This is the direction for a future E1 repair: arbitrate when the evidence warrants it, rather than on a clock.
- **LEBRE status:** `FUTURE_HYPOTHESIS_ONLY`. Not part of this design.
- **Not transferable.** Stability and minimum-inter-event guarantees. LEBRE has no ISS closed-loop model.

### 11. Morse, Mayne & Goodwin (1992)
*Applications of hysteresis switching in parameter adaptive control.* IEEE TAC 37(9):1343–1354. DOI 10.1109/9.159571.

- **Established.** Hysteresis switching logic prevents chattering in adaptive supervisory control and allows convergence
  results for the switched adaptive system.
- **Relevance.** Relevant to the noise-churn risk that B3 introduces (a noisier EMA against a hard threshold).
- **Explicit non-equivalence.** Periodic K10 execution is **not** hysteresis. B3 adds no hysteresis band, and none is
  proposed here, since that would be a second intervention.

### 12. Hespanha & Morse (1999)
*Stability of switched systems with average dwell-time.* Proc. 38th IEEE CDC. DOI 10.1109/CDC.1999.831330.

- **Established.** A switched system whose subsystems are all stable stays stable if the average dwell time between switches is large
  enough.
- **Relevance.** Vocabulary for the dwell-time and churn telemetry. It motivates reporting switching rates and dwell distributions per arm.
- **Not transferable.** The stability theorem. LEBRE's structural modes are not shown to be individually stable systems in
  this sense.

---

## Synthesis (`LEBRE_SPECIFIC_HYPOTHESIS` unless stated)

1. The irregular-data smoothing literature (Wright, Cipra; `CONCEPTUAL_ANALOGY`) justifies interpreting α in elapsed time.
   B3 is the principled elapsed-time correction for a fixed gap of 10 stream steps.
2. The same logic, together with the multirate analogy, predicts that the correction **cannot** restore skipped observations.
   B3 inherits both E2 effects: the endpoint mismatch α q (g10 − g5) and about twice the stationary EMA variance.
3. The supervisory-switching literature (Mosca & Agnoloni, Narendra & Balakrishnan, Morse et al.) predicts that behavior depends
   jointly on filter memory, filter noise and when switching is allowed. Rescue on the transition tasks (I11, I12) is therefore
   the most uncertain part of the design.
