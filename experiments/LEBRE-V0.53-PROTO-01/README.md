# LEBRE v0.53 — protótipo de desenvolvimento

Não é uma versão publicada. Implementa a v0.52-r1 inalterada mais as mudanças da v0.53 à medida que são especificadas.

- `lebre053/_core.py`, `_engine.py`, `_memory.py`, `_model052.py`: cópias byte a byte da biblioteca congelada
  `lebre==0.1.0` (hashes em `SHA256_COPIAS.txt`, conferidos nos testes). Nunca são editadas.
- `lebre053/model053.py`: M2, a porta da referência trivial (especificação:
  `../LEBRE-V0.53-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M2.md`).
- `lebre053/agregacao.py`: M2, rascunho 2 (`../LEBRE-V0.53-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M2_r2.md`): AdaHedge e
  FlipFlop transcritos das Figuras 1 e 2 de de Rooij et al. (2014), parâmetros do Corolário 16. Ativado com
  `saida="adahedge"` ou `saida="flipflop"`; o padrão (`saida="porta"`) mantém o rascunho 1 reproduzível.
- M2, rascunho 3 (`ALGORITHM_SPEC_DRAFT_M2_r3.md`): `saida="fixedshare"`, Fixed Share com α_t = 1/t
  (Adamskiy et al., 2016) sobre previsões gaussianas de R e L; testes conferem o Corolário 6 em todos os intervalos e o
  pior caso do Teorema 4.
- M2, rascunho 4 (`ALGORITHM_SPEC_DRAFT_M2_r4.md`): `saida="adahedge_recortada"`, AdaHedge sobre a perda recortada da
  v0.52.
- M2, rascunho 5 (`ALGORITHM_SPEC_DRAFT_M2_r5.md`): `saida="adahedge_compartilhada"`, Fixed Share com taxas variáveis
  (Cesa-Bianchi et al., 2012, eq. 13) sobre a perda recortada; testes conferem o Teorema 4 em todos os intervalos.
- `tests/`: com a porta desligada, a saída é idêntica bit a bit à da v0.52; comportamento básico da porta; garantias do artigo (Corolários 9 e 16) e
  exemplo da seção 3.1 para a agregação.

Desenvolvimento só com o LEBRE Lab e os dados de desenvolvimento da v0.52; a reserva da v0.53 (`LEBRE-V0.53-DATA-01`)
não é usada.
