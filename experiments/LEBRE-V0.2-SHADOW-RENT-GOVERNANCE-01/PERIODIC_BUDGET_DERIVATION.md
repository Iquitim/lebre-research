# Analytical Derivation: Periodic Budgeted Shadow Schedule ($S_2$)

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Analytical Derivation of Minimum Feasible Period $K_{\min}$ for Full-Block Shadow Duty Cycling  
**Author:** Independent Skeptical Senior Researcher  
**Status:** FROZEN ANALYTICAL SPECIFICATION  

---

## 1. Resource Governing Equation

Under the periodic scheduling paradigm ($S_2$), the removable counterfactual shadow block executes exactly once every $K$ streaming timesteps:

$$\mathbb{I}_{\text{shadow}}(t) = \begin{cases} 1, & \text{if } t \equiv 0 \pmod K \\ 0, & \text{otherwise} \end{cases}$$

The duty cycle is strictly constant:
$$\delta_{\text{periodic}} = \frac{1}{K}$$

The expected per-step total online floating-point operational cost is given by:
$$\mathbb{E}[\text{Total Online FP}] = F_{\text{live}} + F_{\text{periodic\_sched}} + \left(\frac{1}{K}\right) F_{\text{shadow\_removable}}$$

where:
- $F_{\text{live}}$ is the mandatory mean live execution cost (including base prediction, active tap/recurrent prediction, active model LMS updates, and causal standard scaler updates).
- $F_{\text{periodic\_sched}}$ is the floating-point overhead of evaluating the periodic schedule condition. Since $t \equiv 0 \pmod K$ requires only integer arithmetic (1 integer modulo operation and 1 integer comparison), $F_{\text{periodic\_sched}} \equiv 0.0 \text{ FLOPs/step}$.
- $F_{\text{shadow\_removable}}$ is the unoptimized mean operational cost of the full counterfactual shadow exploration block.

---

## 2. Derivation of Period $K_{\min}$

The legacy $R2$ compute ceiling requires:
$$\mathbb{E}[\text{Total Online FP}] \le 100.0 \text{ FLOPs/step}$$

Substituting the governing equation:
$$F_{\text{live}} + \left(\frac{1}{K}\right) F_{\text{shadow\_removable}} \le 100.0$$

Rearranging for the available shadow budget:
$$\text{AVAILABLE\_SHADOW\_FP} = 100.0 - F_{\text{live}} - F_{\text{periodic\_sched}}$$

$$\frac{1}{K} \le \frac{\text{AVAILABLE\_SHADOW\_FP}}{F_{\text{shadow\_removable}}} \implies K \ge \frac{F_{\text{shadow\_removable}}}{\text{AVAILABLE\_SHADOW\_FP}}$$

Because $K$ must be an integer:
$$K_{\min} = \left\lceil \frac{F_{\text{shadow\_removable}}}{100.0 - F_{\text{live}}} \right\rceil$$

---

## 3. Numerical Evaluation from Sealed Baseline

Using exact values from `CORRECTED_SHADOW_RENT_BASELINE.json`:
- $F_{\text{live}} = 81.165018 \text{ FLOPs/step}$
- $F_{\text{shadow\_removable}} = 86.533248 \text{ FLOPs/step}$

Calculate available shadow budget:
$$\text{AVAILABLE\_SHADOW\_FP} = 100.0 - 81.165018 = 18.834982 \text{ FLOPs/step}$$

Calculate unconstrained ratio:
$$\kappa^* = \frac{86.533248}{18.834982} \approx 4.5945$$

Evaluating the ceiling function:
$$K_{\min} = \lceil 4.5945 \rceil = \mathbf{5}$$

---

## 4. Resource Verification for $K = 5$

Evaluating the exact theoretical expectation for $K = 5$:
- **Duty Cycle:** $\delta = 1/5 = 0.2000 \quad (20.0\%)$
- **Mean Shadow FP:** $86.533248 \times 0.2000 = 17.306650 \text{ FLOPs/step}$
- **Expected Total Online FP:**
  $$\mathbb{E}[\text{Total Online FP}] = 81.165018 + 17.306650 = \mathbf{98.471668 \text{ FLOPs/step}}$$

### Margin to Ceiling:
$$\text{Compute Margin} = 100.0 - 98.471668 = +1.528332 \text{ FLOPs/step} \quad (\mathbf{PASS})$$

---

## 5. Frozen Specification for Scheduler $S_2$

- **Primary Integer Period:** $K = 5$
- **Sampling Cadence:** Exactly 1 full shadow execution every 5 stream steps
- **Fixed Shadow Duty Fraction:** $0.2000$ (200 shadow exposures per 1,000 steps)
- **Analytical Total Online FP:** $98.47 \text{ FLOPs/step}$
- **Scheduler State Footprint:** $4 \text{ Bytes}$ (`uint16 step_counter`, `uint16 period_K`)
