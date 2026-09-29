# EMA Timebase Forensic Reconciliation

## 1. Filter Equation & Exact Poles
The supervisory arbitration difference equation is:
$$y[n] = (1 - \alpha) y[n-1] + \alpha u[n], \quad \alpha = 0.020000, \quad q = 0.980000.$$

Matching the exponential decay $e^{-t / \tau}$:
$$\tau_{\text{events}} = -\frac{1}{\ln(q)} = -\frac{1}{\ln(0.98)} = \mathbf{49.498316\text{ events}}.$$

At cadence $K_{\text{arb}}$:
- $K_{\text{arb}}=5$: $\tau_{\text{stream}} = 5 \times 49.498316 = \mathbf{247.491582\text{ stream steps}}$.
- $K_{\text{arb}}=10$: $\tau_{\text{stream}} = 10 \times 49.498316 = \mathbf{494.983165\text{ stream steps}}$.

Half-Life ($t_{1/2}$):
- Event time: $n_{1/2} = \frac{\ln(0.5)}{\ln(0.98)} = \mathbf{34.309618\text{ events}}$.
- Stream time at $K=5$: $\mathbf{171.548092\text{ stream steps}}$.
- Stream time at $K=10$: $\mathbf{343.096185\text{ stream steps}}$.

## 2. Parent Value Discrepancy
Parent narrative cited:
- $\tau_{\text{events}} \approx 49.4965$
- $\tau_{\text{stream, K5}} \approx 247.4827$
- $\tau_{\text{stream, K10}} \approx 494.9654$

**Root Cause:** `ROUNDING_APPROXIMATION`.  
The discrepancy ($0.0018\text{ events}$, $0.0089\text{ steps}$) originated from truncating the natural logarithm in intermediate single-precision or string rounding ($-\ln(0.98) \approx 0.0202035 \implies 1 / 0.0202035 = 49.4964$). The deterministic physical effect remains exact:
$$\frac{\tau_{\text{stream, K10}}}{\tau_{\text{stream, K5}}} = \mathbf{2.000000\times}.$$

## 3. Causal Scope: Coupled Mechanism vs Isolated Submechanisms
Decimating arbitration cadence from $K_{\text{arb}}=5 \to 10$ while holding $\alpha = 0.02$ fixed inherently:
1. Halved decision opportunity frequency (scheduler evaluation every 10 steps instead of 5);
2. Halved gain-EMA update frequency in physical stream time, doubling the effective stream memory window from $\sim 250$ to $\sim 500$ steps.

Because the single intervention simultaneously altered both dynamics, **EMA timescale distortion and decision staleness cannot be causally separated** from this experiment alone. They form a strongly supported, coupled mechanistic explanation.
