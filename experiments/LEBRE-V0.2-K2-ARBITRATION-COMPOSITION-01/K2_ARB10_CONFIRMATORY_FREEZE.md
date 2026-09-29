# Confirmatory Parameter Freeze: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

All architectural parameters, seeds, tasks, and thresholds are strictly frozen.
- Arms: $A0$ ($K_{\text{rec}}=1, K_{\text{arb}}=5$), $A1$ ($K_{\text{rec}}=2, K_{\text{arb}}=5$), $A2$ ($K_{\text{rec}}=2, K_{\text{arb}}=10$).
- Gain EMA smoothing coefficient: $\alpha = 0.02$ fixed across all arms.
- Recurrent learning cadence: $K_{\text{rec\_learn}} = 10$, HOLD_STATE semantics.
- Frontier: $H=32, B=4, K_{\text{probe}}=2$.
- Candidate: $T_{\text{prob}}=15, \theta_{\text{promote}}, \theta_{\text{tol}}=0.01$.
