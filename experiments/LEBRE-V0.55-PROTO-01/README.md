# LEBRE v0.55 — protótipo de desenvolvimento (núcleo ancorado)

- `lebre055/`: cópia byte a byte da v0.54 congelada (commit `f9906c4`; hashes em `SHA256_COPIAS.txt`) mais dois
  arquivos novos:
  - `anchored.py`: o núcleo com as alavancas ANCHOR, SLOW e REF_CORE (rascunhos 0 a 2);
  - `model055.py`: as variantes A, A0, B, B1, B2, B4 e B5.
- Nenhum arquivo copiado é editado.
- `tests/test_anchored.py`:
  - identidade bit a bit de A0 (reescrita com as alavancas desligadas) com a v0.54;
  - não vazamento em todas as variantes;
  - alinhamento da referência lenta e assentamento.
- `FUMACA_RESULTADO.md`: teste de fumaça que escolheu as variantes da D1 (A, B4, B5). B, B1 e B2 ficam como resultados
  negativos de desenvolvimento.
- Desenho: `experiments/LEBRE-V0.55-DESIGN-NOTE-01/DESIGN_NOTE.md` (com o adendo 01).

Rodar os testes desta pasta: `python -m pytest -q tests`.
