# 13 — Escala de memória

**Estado persistente pela fórmula do código** (contabilidade em float32; Python guarda float64, ou seja, o dobro):
- **S:** 4(L+1)d + 8 + 28|A| + 4|polos| + 4|q| + 2·dL + 12|hot| + 24 bytes. Com d = 5 dá ≈ 1,08 KB, **independente de s**.
- **M:** buffer de **2s+2** valores + perfil de **s** valores + pesos, o que dá 4·(3s + k + 8) bytes ≈ **12s bytes**. A crítica estimou ~2s floats; o código guarda ~3s, porque o buffer tem o dobro do necessário para as defasagens usadas (s e s−1).

|   d | s     |   S_bytes |   M_bytes |   total_bytes_code_formula |   python_float64_equivalent_bytes |
|----:|:------|----------:|----------:|---------------------------:|----------------------------------:|
|   1 | none  |       292 |        44 |                        376 |                               752 |
|   1 | 24    |       292 |       340 |                        672 |                              1344 |
|   1 | 48    |       292 |       628 |                        960 |                              1920 |
|   1 | 144   |       292 |      1780 |                       2112 |                              4224 |
|   1 | 1440  |       292 |     17332 |                      17664 |                             35328 |
|   1 | 10080 |       292 |    121012 |                     121344 |                            242688 |
|   5 | none  |      1076 |        44 |                       1160 |                              2320 |
|   5 | 24    |      1076 |       340 |                       1456 |                              2912 |
|   5 | 48    |      1076 |       628 |                       1744 |                              3488 |
|   5 | 144   |      1076 |      1780 |                       2896 |                              5792 |
|   5 | 1440  |      1076 |     17332 |                      18448 |                             36896 |
|   5 | 10080 |      1076 |    121012 |                     122128 |                            244256 |
|   6 | none  |      1272 |        44 |                       1356 |                              2712 |
|   6 | 24    |      1272 |       340 |                       1652 |                              3304 |
|   6 | 48    |      1272 |       628 |                       1940 |                              3880 |
|   6 | 144   |      1272 |      1780 |                       3092 |                              6184 |
|   6 | 1440  |      1272 |     17332 |                      18644 |                             37288 |
|   6 | 10080 |      1272 |    121012 |                     122324 |                            244648 |

- Separação: parâmetros do modelo (pesos de S e M: < 100 floats), buffer de fluxo (histórico de defasagens de S: (L+1)·d; buffer de M: 2s+2), estado sazonal (s) e memória de trabalho (vetores temporários O(d + k)).
- **MEMORY_COMPLEXITY** = 4·[(L+1)d + 2dL/4 + 3s + O(|A| + |hot| + k)] bytes ≈ **196d + 12s + ~190 bytes** (float32; conferido contra `memory_bytes()` para d = 1–6 e s ∈ (24, 144)). Sem sazonalidade: ≈ 196d + 180.
- **Envelope do "~1,3 KB"** (≤ 1.331 B, calculado com `memory_bytes()` do código). O limite depende de d **e** s ao mesmo tempo:

| d | sem sazonalidade | maior s com ≤ 1,3 KB |
|---|---|---|
| 1 | 376 B | 78 |
| 2 | 572 B | 62 |
| 3 | 768 B | 46 |
| 4 | 964 B | 29 |
| 5 | 1.160 B | 13 |
| 6 | 1.356 B | nenhum (já excede sem sazonalidade) |

  Com s = 144: 2,1–3,1 KB; com s = 1440: ~18 KB; com s = 10.080: ~122 KB. O valor declarado é uma mediana do held-out, não um limite do envelope.
