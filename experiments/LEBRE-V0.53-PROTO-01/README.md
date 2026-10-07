# LEBRE v0.53 — protótipo de desenvolvimento

Não é uma versão publicada. Implementa a v0.52-r1 inalterada mais as mudanças da v0.53 à medida que são especificadas.

- `lebre053/_core.py`, `_engine.py`, `_memory.py`, `_model052.py`: cópias byte a byte da biblioteca congelada
  `lebre==0.1.0` (hashes em `SHA256_COPIAS.txt`, conferidos nos testes). Nunca são editadas.
- `lebre053/model053.py`: M2, a porta da referência trivial (especificação:
  `../LEBRE-V0.53-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M2.md`).
- `tests/`: com a porta desligada, a saída é idêntica bit a bit à da v0.52; comportamento básico da porta.

Desenvolvimento só com o LEBRE Lab e os dados de desenvolvimento da v0.52; a reserva da v0.53 (`LEBRE-V0.53-DATA-01`)
não é usada.
