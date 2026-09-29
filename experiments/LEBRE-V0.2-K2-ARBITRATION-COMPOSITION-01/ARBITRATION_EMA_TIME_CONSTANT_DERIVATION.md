# Analytical Derivation: Arbitration EMA Time Constants

## 1. Filter Formulation

The supervisory arbitration block updates four conditional-gain signals:
- $\text{EMA}\_G\_D\_B$ (discrete delay tap vs base)
- $\text{EMA}\_G\_R\_B$ (recurrent unit vs base)
- $\text{EMA}\_G\_D\_BR$ (discrete tap given base + recurrent)
- $\text{EMA}\_G\_R\_BD$ (recurrent unit given base + discrete)

Each filter follows an exponential smoothing difference equation:
$$y[n] = (1 - \alpha) y[n-1] + \alpha u[n], \quad \alpha = 0.02.$$
Pole location: $q = 1 - \alpha = 0.98$.

---

## 2. Derivation of Event-Time Metrics

The impulse response of the first-order lowpass filter is:
$$h[n] = \alpha q^n = \alpha e^{-n / \tau_{\text{events}}}.$$
Matching the decay rate:
$$e^{-1 / \tau_{\text{events}}} = q \implies \tau_{\text{events}} = -\frac{1}{\ln(q)} = -\frac{1}{\ln(0.98)} = \mathbf{49.498316\text{ events}}.$$

The half-life $n_{1/2}$ (number of events for a step response to reach $50\%$ of asymptote, or impulse to decay to $50\%$):
$$q^{n_{1/2}} = 0.5 \implies n_{1/2} = \frac{\ln(0.5)}{\ln(0.98)} = \frac{-0.693147}{-0.020203} = \mathbf{34.309618\text{ events}}.$$

---

## 3. Mapping to Stream Steps

Under multirate execution with period $K_{\text{arb}}$:
$$t = n \times K_{\text{arb}} \implies \tau_{\text{stream}} = K_{\text{arb}} \times \tau_{\text{events}}.$$

| Quantity | Event Time ($n$) | Stream Steps at $K=5$ | Stream Steps at $K=10$ | Decimation Ratio ($K=10 / K=5$) |
| :--- | :---: | :---: | :---: | :---: |
| **Filter Pole ($q$)** | $0.98$ | $0.98^{1/5} \approx 0.99596$ | $0.98^{1/10} \approx 0.99798$ | N/A |
| **Characteristic Time ($	au$)** | `49.4983` events | `247.4916` steps | `494.9832` steps | **$2.000\times$** |
| **Half-Life ($t_{1/2}$)** | `34.3096` events | `171.5481` steps | `343.0962` steps | **$2.000\times$** |
| **95% Settling Time ($3\tau$)** | `148.4949` events | `742.4747` steps | `1484.9495` steps | **$2.000\times$** |

### Physical Consequence:
Holding $\alpha$ fixed at $0.02$ doubles the effective memory window of structural selection in physical stream time. Structural adaptations to regime changes will observe gains integrated over approximately $\sim 500$ stream steps rather than $\sim 250$ steps.
