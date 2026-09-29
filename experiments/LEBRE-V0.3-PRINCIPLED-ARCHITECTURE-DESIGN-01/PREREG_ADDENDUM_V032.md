# Adendo ao pré-registro — v0.3.2 e BENCH-01 com colunas permutadas

**Escrito e com hash registrado antes da execução das Partes IV e V.** Não altera o pré-registro original nem os resultados das Partes I–III.

## Motivação (documentada antes dos resultados)
1. **Bug da v0.3.1** encontrado na Parte II: a inicialização preguiçosa de σ² (F3) pode começar em ~1e-12, o que dá τ ~1e13 nos episódios
   iniciais. v0.3.2 = v0.3.1 + F6 (estimadores por média amostral no aquecimento, sem episódios antes de n_warm = 20).
   SHA-256 em `FREEZE_V032_SHA256.txt`. Nenhum outro parâmetro mudou.
2. **Artefato do BENCH-01:** as dependências verdadeiras de A2, A3, A4 e H1 ficam na coluna 0 (A3 também na coluna 1). Isso favorece
   quem privilegia a coluna 0: C4 e S1 usam só a feature 0; a v0.3 (iter4) testa primeiro (0,1)..(0,4) por ordem do dicionário.

## Parte IV — BENCH-01 sintético com colunas permutadas
- Tarefas A1–A8, H1, H2. Sementes **161..190** (livres).
- Para cada semente s, as colunas de X são permutadas por `np.random.RandomState(s + 1_000_000).permutation(D)`, **a mesma para todos os modelos**.
- Modelos: os 15 do BENCH-01B (configurações calibradas originais), V03, V031, V032, CTRL_ARX_NLMS e CTRL_PERSISTENCE.
- Desfechos: os mesmos da Parte II.

## Parte V — Interno I1–I14 para a v0.3.2
- Sementes **2146..2175** (livres). Braços: V02_A0, V031, V032, CTRL_ARX.
- H1' (V032 − V02_A0 < 0), H2' (FP da V032 ≤ 100), H3' (V032 − CTRL_ARX < 0) e H4' (estrutura exata V032 − V02_A0 > 0), com Holm sobre H1', H3' e H4'.
  Secundário: V032 − V031.

## Parte VI — Dados reais X1–X3 para a v0.3.2 (rotulado como semi-held-out)
A correção F6 veio da A3 sintética, não de X1–X3, mas os resultados da v0.3.1 em X1–X3 já foram vistos. Rodo com as mesmas sementes e reporto como **semi-held-out**.
