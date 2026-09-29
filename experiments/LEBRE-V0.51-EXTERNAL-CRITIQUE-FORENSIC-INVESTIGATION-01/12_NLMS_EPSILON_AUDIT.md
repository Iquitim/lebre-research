# 12 — ε do NLMS

1. **O código autoritativo usa ε?**
   - **S:** sim, ε = 10⁻⁶ absoluto no denominador.
   - **M:** não. A atualização só é pulada quando ‖φ‖² = 0 exatamente.
2. **Documentado?** Não.
3. **Invariância de escala.** Com w ← w + μ e φ/(‖φ‖² + ε), um ε absoluto fixo quebra a invariância: o passo efetivo em escala c é μ c² ‖φ‖²/(c² ‖φ‖² + ε), que depende de c. Na M (sem ε), a invariância é **exata**: NMSE idêntico de ×10⁻⁶ a ×10⁶. Em compensação, **não há proteção** quando ‖φ‖ é pequeno e o erro é grande.

| case                             |   season |       nmse |         mse |    max_abs_w | finite   |
|:---------------------------------|---------:|-----------:|------------:|-------------:|:---------|
| scaled x1e-06                    |       24 | 0.020693   | 0           |  0.636394    | True     |
| scaled x1                        |       24 | 0.020693   | 1.40501     |  0.636394    | True     |
| scaled x1e+06                    |       24 | 0.020693   | 1.40501e+12 |  0.636394    | True     |
| constant                         |       24 | 0          | 0           |  0           | True     |
| near-constant (1e-9 noise)       |       24 | 1.07244    | 0           |  1.35057     | True     |
| quantised random walk (plateaus) |      nan | 0.003142   | 0.49708     | 15.5948      | True     |
| quantised seasonal (plateaus)    |       24 | 0.05656    | 3.96554     |  0.741251    | True     |
| flat then step                   |      nan | 8.0804e+20 | 1.51523e+22 |  4.52517e+11 | True     |

- **O caso "plano seguido de degrau" diverge** (NMSE ~8·10²⁰; |w| ~4,5·10¹¹): os incrementos recentes são ~0 enquanto o erro é grande. Esse é o mecanismo que a crítica observou no R1m sem período.
- Séries quantizadas com platôs e alvos quase constantes não divergiram neste teste.
- **Efeito nos resultados reportados:** nenhuma divergência no held-out (0 divergências registradas). O risco é real em séries com platôs longos seguidos de saltos.

**Classificação:** `NLMS_EPSILON_SPEC = CODE_ONLY` para S (ε absoluto não documentado) e **MISSING/UNSTABLE** para M. `NLMS_NUMERIC_CONTRACT = UNSTABLE`.
