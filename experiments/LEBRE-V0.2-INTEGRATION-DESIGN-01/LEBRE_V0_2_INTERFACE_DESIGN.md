# LEBRE-V0.2-INTEGRATION-DESIGN-01: Modular Interface Design
## Formal Component Interfaces, Information Encapsulation & Cross-Module Contracts

**Document ID:** `LEBRE-V0.2-INTF-2026-v1.0`  
**Status:** `EXPERIMENTAL_INTERFACE_DESIGN`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Systems Architect:** Skeptical Senior ML Systems Researcher, Scientific-Software Auditor  

---

## 1. Architectural Encapsulation Principles

To prevent moving-target destabilization and maintain scientific modularity, LEBRE v0.2 enforces strict information encapsulation across components:
1. **Separation of Forward Path and Evidence Path:** Active prediction generation is strictly decoupled from shadow candidate scoring;
2. **Forbidden Cross-Module Leaks:** No module may inspect the internal weights, gradients, or private state trajectories of another module;
3. **Prequential Timing Barriers:** Counterfactual evaluations must execute prior to the revelation of $y_t$.

---

## 2. Component Interface Specifications

### 2.1 Interface: `LinearPredictor`
- **Role:** Instantaneous linear baseline representation ($L_t = w^T x_t$).
- **Inputs:** $x_t \in \mathbb{R}^D$, scalar target $y_t$ (post-prediction).
- **Outputs:** $\hat{y}_{\text{base}} \in \mathbb{R}$, baseline error $e_{\text{base}} \in \mathbb{R}$.
- **Persistent State:** Weights $w \in \mathbb{R}^D$ (40 B for $D=5$), step counter $t$.
- **Update Order:** Step 9 (post-loss evaluation).
- **Allowed Cross-Module Information:** None. Operates directly on raw normalized features.
- **Forbidden Information:** Target $y_t$ during prediction; temporal module predictions or weights.
- **Resource Footprint:** 10 FP FLOPs (forward dot product), 15 FP FLOPs (NLMS update).

---

### 2.2 Interface: `HistoryProvider`
- **Role:** Addressable bounded temporal history buffer (`FP16_EXACT_ADDRESSABLE_RING`).
- **Inputs:** $x_t \in \mathbb{R}^D$, feature index $i \in \{1..D\}$, lag delay $k \in \{1..L_{\max}\}$.
- **Outputs:** Stored sample $x_{i, t-k} \in \mathbb{R}$ (cast back to FP32 on read).
- **Persistent State:** Circular array buffer of size $D \times (L_{\max} + 1)$ in FP16 (330 B for $D=5, L=32$), head pointer `head` (2 B).
- **Update Order:** Step 2 (immediately upon receiving $x_t$).
- **Allowed Cross-Module Information:** Raw input stream $x_t$.
- **Forbidden Information:** Errors, predictions, targets, structural states.
- **Resource Footprint:** 5 FP-to-INT16 casts + 10 write bytes per step. 2 read bytes per query.

---

### 2.3 Interface: `LagMemoryManager`
- **Role:** Lifecycle governance, candidate probing, probation, active tap adaptation, and obsolescence eviction for sparse discrete lags $(i, k)$.
- **Inputs:** $x_t \in \mathbb{R}^D$, query function `get_delayed(i, k)`, error signal $e_t$.
- **Outputs:** Live lag prediction $\hat{y}_{\text{lag}} \in \mathbb{R}$, shadow candidate prediction $\hat{y}_{\text{lag, shadow}} \in \mathbb{R}$, active lag count $K_t$, promotion/eviction requests.
- **Persistent State:** Active tap table ($K_{\max} \le 4$ entries: $(i, k, w, R, \text{age})$), candidate pool ($M \le 3$ entries), correlation grid ($D \times L_{\max}$ floats), probe pointer.
- **Update Order:** Step 9 (tap weights) and Step 10 (lifecycle relevance and eviction).
- **Allowed Cross-Module Information:** Input history, baseline residual error $e_{\text{base}}$.
- **Forbidden Information:** Recurrent state internal sensitivities or activation states.
- **Lifecycle Events:** `PROBE`, `CANDIDATE_BIRTH`, `PROMOTE_TO_ACTIVE`, `EVICT_OBSOLETE`.

---

### 2.4 Interface: `RecurrentMemoryManager`
- **Role:** Continuous latent memory governance, candidate training, probation, and real-time forward sensitivity tracking.
- **Inputs:** Driving input $x_{1, t} \in \mathbb{R}$, error signal $e_t$.
- **Outputs:** Live recurrent prediction $\hat{y}_{\text{rec}} \in \mathbb{R}$, shadow candidate prediction $\hat{y}_{\text{rec, shadow}} \in \mathbb{R}$, internal state $s_t$, promotion/eviction requests.
- **Persistent State:** Candidate/Active unit ($s, \alpha, b, c, p_\alpha, p_b$) (48 B), state readout weight $w_{\text{state}}$, probation counter, utility EMA.
- **Update Order:** Step 4 (forward sensitivity) and Step 9 (parameter update via forward gradients).
- **Allowed Cross-Module Information:** Baseline residual error $e_{\text{base}}$.
- **Forbidden Information:** Discrete tap locations, tap weights, or circular history pointers.
- **Lifecycle Events:** `INIT_CANDIDATE`, `PROMOTE_ACTIVE`, `DEMOTE_EVICT`.

---

### 2.5 Interface: `CapacityArbitrator`
- **Role:** Resource-aware multi-capacity structural governor (Topology T3).
- **Inputs:** Counterfactual losses ($\ell_{\text{BASE}}, \ell_{\text{BASE}+D}, \ell_{\text{BASE}+R}, \ell_{\text{BASE}+D+R}$), candidate probation statuses, resource budgets.
- **Outputs:** Structural Allocation Action $\in \{\text{NONE}, \text{LAG\_ONLY}, \text{RECURRENT\_ONLY}, \text{BOTH}\}$.
- **Persistent State:** Filtered gain EMAs ($\bar{G}_{D|B}, \bar{G}_{R|B}, \bar{G}_{D|B+R}, \bar{G}_{R|B+D}$), hysteresis counter, structural state register.
- **Update Order:** Step 10 (after loss recording, prior to next step).
- **Allowed Cross-Module Information:** Counterfactual scalar predictions and scalar losses.
- **Forbidden Information:** Private weight vectors or internal feature representations.
- **Mathematical Complexity:** Fixed scalar arithmetic ($4$ subtractions, $4$ EMA updates, $5$ comparison checks). Zero neural network or learned parameters.

---

### 2.6 Interface: `ResourceLedger`
- **Role:** Non-intrusive 4-channel physical resource accounting.
- **Inputs:** Operation counters from all components.
- **Outputs:** Real-time resource vector $\mathbf{R} = [\text{FP\_FLOPS}, \text{INT\_OPS}, \text{MEM\_TRAFFIC\_BYTES}, \text{PERSISTENT\_BYTES}]$.
- **Persistent State:** Cumulative counters, peak registers, per-step buffers.
- **Update Order:** Continuous instrumentation across all steps.
- **Allowed Cross-Module Information:** All hardware operation events.
- **Forbidden Information:** Modifying algorithm state or execution logic.

---

## 3. Sequence & Dataflow Diagram

```
Time Step t:
  1. Receive x_t
  2. HistoryProvider.write(x_t)
  3. LinearPredictor.predict(x_t)                ──► y_base
  4. RecurrentMemoryManager.forward(x_t)         ──► y_rec (active & shadow)
  5. LagMemoryManager.forward(get_delayed)       ──► y_lag (active & shadow)
  6. CapacityArbitrator.form_counterfactuals()   ──► [P_B, P_B+D, P_B+R, P_B+D+R]
  7. Form Live Prediction                        ──► y_hat_live
  8. Reveal y_t
  9. Record losses & compute gains               ──► [ell_live, G_D|B, G_R|B, G_D|B+R, G_R|B+D]
 10. Update LinearPredictor(e_live)
 11. Update LagMemoryManager(e_live)
 12. Update RecurrentMemoryManager(e_live)
 13. CapacityArbitrator.arbitrate(gains)         ──► [Promote / Evict / Maintain]
 14. ResourceLedger.record_step()
```
